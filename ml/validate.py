"""
Cross-dataset validation - the strongest demo moment.

Runs the full pipeline over held-out MS3SEG slices AND over MSLesSeg (never trained on),
compares predicted boxes to ground-truth boxes, and writes ml/results/validation.json,
which the backend serves at GET /validation.

Usage:
    python -m ml.validate --ms3seg data/processed/ms3seg/val --mslesseg data/processed/mslesseg

Expected input layout (produced by data/scripts/export_coco.py):
    <dir>/images/*.png
    <dir>/annotations.json     (COCO)

Metrics (PLAN.md section 9): precision, recall, false positives per scan at IoU >= 0.3
(lesions are small; 0.5 is too strict for boxes derived from blobs), and % of
detections flagged atypical (descriptive only - no ground truth for that).

Owner: teammate 2.
"""

import argparse
import json
from pathlib import Path

from backend.app.schemas import DatasetValidation, ValidationReport

RESULTS_PATH = Path(__file__).parent / "results" / "validation.json"


def evaluate_dataset(name: str, dataset_dir: Path, iou_threshold: float = 0.3) -> DatasetValidation:
    """
    For each image: run_pipeline -> predicted boxes; load GT boxes from COCO;
    greedy-match by IoU; accumulate TP/FP/FN. Return one DatasetValidation row.

    Note: every image is one Roboflow API call - run on a sample (e.g. 100 slices)
    first to check the numbers make sense, then the full set.

    TODO(teammate 2): implement.
    """
    raise NotImplementedError


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ms3seg", type=Path, required=True, help="held-out MS3SEG val dir")
    ap.add_argument("--mslesseg", type=Path, required=True, help="MSLesSeg dir (never trained on)")
    args = ap.parse_args()

    report = ValidationReport(
        datasets=[
            evaluate_dataset("MS3SEG (held-out val)", args.ms3seg),
            evaluate_dataset("MSLesSeg (never trained on)", args.mslesseg),
        ],
        note="IoU >= 0.3. Pattern % is descriptive - no migraine ground truth exists.",
    )
    RESULTS_PATH.write_text(json.dumps(report.model_dump(), indent=2))
    print(f"wrote {RESULTS_PATH}")


if __name__ == "__main__":
    main()
