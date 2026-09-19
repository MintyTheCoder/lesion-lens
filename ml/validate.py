"""
Cross-dataset validation - the strongest demo moment.

Runs the detector (+ heuristic pattern layer, once implemented) over held-out MS3SEG
slices AND over MSLesSeg (never trained on), compares predicted boxes to ground-truth
boxes, and writes ml/results/validation.json, which the backend serves at GET /validation.

Usage:
    python -m ml.validate
    python -m ml.validate --ms3seg data/processed/ms3seg_dataset/test --mslesseg data/processed/mslesseg_dataset/test

Expected input layout - either is accepted:
    <dir>/_annotations.coco.json + images alongside      (Roboflow export; what's on disk today)
    <dir>/annotations.json + <dir>/images/*.png           (data/scripts/export_coco.py layout)

Metrics (PLAN.md section 9): precision, recall, false positives per scan at IoU >= 0.3
(lesions are small; 0.5 is too strict for boxes derived from blobs), and % of
detections flagged atypical (descriptive only - no ground truth for that; reported as
0.0 until ml/heuristics.py is implemented, since NotImplementedError is caught per-lesion).

Predictions run directly through ml.inference.detect() on the already-preprocessed
dataset images (NOT through ml.pipeline.run_pipeline, which would re-run preprocessing
a second time on images that are already normalized/CLAHE'd/resized).

Raw detections are cached to disk (results/detection_cache/<sha256 of image bytes>.json)
so re-tuning ml/heuristics.py and re-scoring doesn't re-hit Roboflow's free-tier API for
images already seen. Pass --no-cache to force a fresh run (e.g. after retraining the model).

Owner: teammate 2.
"""

import argparse
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np

from backend.app.schemas import DatasetValidation, ValidationReport
from ml.heuristics import classify_pattern, score_lesion
from ml.inference import RawDetection, detect

RESULTS_PATH = Path(__file__).parent / "results" / "validation.json"
DETECTION_CACHE_DIR = Path(__file__).parent / "results" / "detection_cache"
REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MS3SEG = REPO_ROOT / "data" / "processed" / "ms3seg_dataset" / "test"
DEFAULT_MSLESSEG = REPO_ROOT / "data" / "processed" / "mslesseg_dataset" / "test"


def _cached_detect(image_bytes: bytes, rgb: np.ndarray, use_cache: bool = True) -> list[RawDetection]:
    """detect(rgb), transparently cached on disk by sha256 of the raw image bytes."""
    if not use_cache:
        return detect(rgb)

    digest = hashlib.sha256(image_bytes).hexdigest()
    cache_path = DETECTION_CACHE_DIR / f"{digest}.json"
    if cache_path.exists():
        cached = json.loads(cache_path.read_text())
        return [RawDetection(bbox=d["bbox"], confidence=d["confidence"]) for d in cached]

    dets = detect(rgb)
    DETECTION_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps([{"bbox": d.bbox, "confidence": d.confidence} for d in dets]))
    return dets


def _load_coco_dir(dataset_dir: Path) -> tuple[dict[int, Path], dict[int, list[list[int]]]]:
    """image_id -> image path, image_id -> GT boxes ([x, y, w, h]), for either on-disk layout."""
    flat_coco = dataset_dir / "_annotations.coco.json"
    if flat_coco.exists():
        coco_path, images_dir = flat_coco, dataset_dir
    else:
        coco_path, images_dir = dataset_dir / "annotations.json", dataset_dir / "images"

    coco = json.loads(coco_path.read_text())
    id_to_path = {img["id"]: images_dir / img["file_name"] for img in coco["images"]}
    gt_by_image: dict[int, list[list[int]]] = {}
    for ann in coco["annotations"]:
        gt_by_image.setdefault(ann["image_id"], []).append(ann["bbox"])
    return id_to_path, gt_by_image


def _iou(box_a: list[int], box_b: list[int]) -> float:
    """IoU of two [x, y, w, h] boxes."""
    ax, ay, aw, ah = box_a
    bx, by, bw, bh = box_b
    ix1, iy1 = max(ax, bx), max(ay, by)
    ix2, iy2 = min(ax + aw, bx + bw), min(ay + ah, by + bh)
    inter = max(0, ix2 - ix1) * max(0, iy2 - iy1)
    union = aw * ah + bw * bh - inter
    return inter / union if union > 0 else 0.0


def _match_boxes(predicted: list[list[int]], ground_truth: list[list[int]], iou_threshold: float) -> tuple[int, int, int]:
    """Greedy IoU matching. Returns (true_positives, false_positives, false_negatives)."""
    matched_gt: set[int] = set()
    tp = fp = 0

    for pred_box in predicted:
        best_iou, best_idx = 0.0, None
        for i, gt_box in enumerate(ground_truth):
            if i in matched_gt:
                continue
            score = _iou(pred_box, gt_box)
            if score > best_iou:
                best_iou, best_idx = score, i

        if best_iou >= iou_threshold and best_idx is not None:
            tp += 1
            matched_gt.add(best_idx)
        else:
            fp += 1

    fn = len(ground_truth) - len(matched_gt)
    return tp, fp, fn


def evaluate_dataset(name: str, dataset_dir: Path, iou_threshold: float = 0.3, use_cache: bool = True) -> DatasetValidation:
    """
    For each image: detect() -> predicted boxes; load GT boxes from COCO; greedy-match
    by IoU; accumulate TP/FP/FN across the whole dataset. Every image is one Roboflow
    API call unless it's already cached - point --ms3seg/--mslesseg at a small subset
    dir first to sanity check, or pass use_cache=False / --no-cache for a fresh run.
    """
    id_to_path, gt_by_image = _load_coco_dir(dataset_dir)

    total_tp = total_fp = total_fn = 0
    total_lesions = total_atypical = 0
    n_scans = 0

    for image_id, image_path in id_to_path.items():
        image_bytes = image_path.read_bytes()
        gray = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
        if gray is None:
            continue
        n_scans += 1

        rgb = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
        # detect() doesn't guarantee confidence order - sort so the greedy IoU match below
        # gives higher-confidence boxes first pick of a GT match, not whatever order the API returned.
        dets = sorted(_cached_detect(image_bytes, rgb, use_cache), key=lambda d: d.confidence, reverse=True)
        predicted = [d.bbox for d in dets]
        ground_truth = gt_by_image.get(image_id, [])

        tp, fp, fn = _match_boxes(predicted, ground_truth, iou_threshold)
        total_tp += tp
        total_fp += fp
        total_fn += fn

        for det in dets:
            total_lesions += 1
            x, y, bw, bh = det.bbox
            crop = gray[max(y, 0) : y + bh, max(x, 0) : x + bw]
            try:
                feats = score_lesion(crop, det.bbox, gray.shape)
                pattern, _ = classify_pattern(feats, det.bbox, gray.shape)
                if pattern == "atypical":
                    total_atypical += 1
            except NotImplementedError:
                pass  # heuristics.py not implemented yet - atypical_pct stays 0.0 until it is

    precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) else 0.0
    recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) else 0.0
    fp_per_scan = total_fp / n_scans if n_scans else 0.0
    atypical_pct = round(100 * total_atypical / total_lesions, 2) if total_lesions else 0.0

    return DatasetValidation(
        name=name,
        n_scans=n_scans,
        precision=round(precision, 4),
        recall=round(recall, 4),
        fp_per_scan=round(fp_per_scan, 4),
        atypical_pct=atypical_pct,
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ms3seg", type=Path, default=DEFAULT_MS3SEG, help="held-out MS3SEG test dir")
    ap.add_argument("--mslesseg", type=Path, default=DEFAULT_MSLESSEG, help="MSLesSeg dir (never trained on)")
    ap.add_argument(
        "--no-cache", action="store_true", help="bypass results/detection_cache/ and re-hit Roboflow for every image"
    )
    args = ap.parse_args()
    use_cache = not args.no_cache

    report = ValidationReport(
        datasets=[
            evaluate_dataset("MS3SEG (held-out test)", args.ms3seg, use_cache=use_cache),
            evaluate_dataset("MSLesSeg (never trained on)", args.mslesseg, use_cache=use_cache),
        ],
        note="IoU >= 0.3. Pattern % is descriptive - no migraine ground truth exists.",
    )
    RESULTS_PATH.write_text(json.dumps(report.model_dump(), indent=2))
    print(f"wrote {RESULTS_PATH}")


if __name__ == "__main__":
    main()
