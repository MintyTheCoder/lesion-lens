"""
Raw MSLesSeg NIfTI -> COCO-format eval set for ml/validate.py.

MSLesSeg is never trained on (CLAUDE.md section 5/8) - this only prepares it as an
external, cross-hospital validation set. Reuses the SAME preprocessing and box
extraction as data/pipeline/pipeline_ms3seg.py, i.e. the pipeline actually deployed
to Roboflow (not data/scripts/, which is unfinished/unused), so predicted boxes and
ground-truth boxes are in the same coordinate space the trained model expects.

MSLesSeg's raw train/ and test/ folders use different layouts:
    train/<patient>/<timepoint>/<patient>_<timepoint>_FLAIR.nii.gz (+ _MASK.nii.gz)
    test/<patient>/<patient>_FLAIR.nii.gz (+ _MASK.nii.gz)
Since none of MSLesSeg is used for training here, both splits are pooled into one
external validation set (93 train-layout scans + 22 test-layout scans = 115 total,
matching the dataset's documented size).

Usage:
    python -m data.pipeline.mslesseg_eval_prep

Output: data/processed/mslesseg_dataset/test/*.png + _annotations.coco.json
(same flat Roboflow-export layout as data/processed/ms3seg_dataset/test/, so
ml/validate.py reads both the same way).
"""

import json
from pathlib import Path

import cv2
import nibabel as nib

from data.pipeline.pipeline_ms3seg import extract_boxes, preprocess_slice, scale_boxes

RAW_ROOT = Path(__file__).resolve().parents[1] / "raw" / "MSLesSeg Dataset" / "MSLesSeg Dataset"
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "processed" / "mslesseg_dataset" / "test"


def find_cases() -> list[tuple[str, Path, Path]]:
    """[(case_id, flair_path, mask_path), ...] for every MSLesSeg scan, both raw layouts."""
    cases: list[tuple[str, Path, Path]] = []

    train_root = RAW_ROOT / "train"
    for patient_dir in sorted(p for p in train_root.iterdir() if p.is_dir()):
        patient = patient_dir.name
        for tp_dir in sorted(p for p in patient_dir.iterdir() if p.is_dir()):
            tp = tp_dir.name
            flair = tp_dir / f"{patient}_{tp}_FLAIR.nii.gz"
            mask = tp_dir / f"{patient}_{tp}_MASK.nii.gz"
            if flair.exists() and mask.exists():
                cases.append((f"{patient}_{tp}", flair, mask))

    test_root = RAW_ROOT / "test"
    for patient_dir in sorted(p for p in test_root.iterdir() if p.is_dir()):
        patient = patient_dir.name
        flair = patient_dir / f"{patient}_FLAIR.nii.gz"
        mask = patient_dir / f"{patient}_MASK.nii.gz"
        if flair.exists() and mask.exists():
            cases.append((patient, flair, mask))

    return cases


def process_case(case_id: str, flair_path: Path, mask_path: Path) -> list[dict]:
    """Lesion-containing slices for one scan: preprocessed image + [x, y, w, h] GT boxes."""
    flair_data = nib.load(str(flair_path)).get_fdata()
    mask_data = nib.load(str(mask_path)).get_fdata()
    if flair_data.shape != mask_data.shape:
        return []

    entries = []
    for z in range(mask_data.shape[2]):
        slice_mask = mask_data[:, :, z]
        if slice_mask.sum() == 0:
            continue
        boxes_xyxy = extract_boxes(slice_mask)
        if not boxes_xyxy:
            continue

        processed_slice, scale, offset = preprocess_slice(flair_data[:, :, z])
        scaled_xyxy = scale_boxes(boxes_xyxy, scale, offset)
        # extract_boxes/scale_boxes return (xmin, ymin, xmax, ymax); COCO/schemas.Lesion.bbox
        # use [x, y, w, h] - convert at this boundary, same convention export_coco.py uses.
        boxes_xywh = [[x0, y0, x1 - x0, y1 - y0] for x0, y0, x1, y1 in scaled_xyxy]

        entries.append({"case_id": case_id, "slice": z, "image": processed_slice, "boxes": boxes_xywh})
    return entries


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    cases = find_cases()
    print(f"Found {len(cases)} MSLesSeg scans (train-layout + test-layout, pooled - all held out)")

    images, annotations = [], []
    img_id = ann_id = 1
    skipped = []

    for case_id, flair_path, mask_path in cases:
        entries = process_case(case_id, flair_path, mask_path)
        if not entries:
            skipped.append(case_id)
            continue
        for entry in entries:
            filename = f"{entry['case_id']}_slice{entry['slice']}.png"
            cv2.imwrite(str(OUTPUT_DIR / filename), entry["image"])
            h, w = entry["image"].shape
            images.append({"id": img_id, "file_name": filename, "width": w, "height": h})
            for x, y, bw, bh in entry["boxes"]:
                annotations.append(
                    {"id": ann_id, "image_id": img_id, "category_id": 1, "bbox": [x, y, bw, bh], "area": bw * bh, "iscrowd": 0}
                )
                ann_id += 1
            img_id += 1

    coco = {"images": images, "annotations": annotations, "categories": [{"id": 1, "name": "lesion"}]}
    (OUTPUT_DIR / "_annotations.coco.json").write_text(json.dumps(coco))

    print(f"Wrote {len(images)} images, {len(annotations)} boxes to {OUTPUT_DIR}")
    print(f"Scans with no lesion-containing slices (skipped entirely): {len(skipped)} -> {skipped}")


if __name__ == "__main__":
    main()
