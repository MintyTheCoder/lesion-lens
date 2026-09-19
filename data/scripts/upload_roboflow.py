"""
Upload processed/ms3seg/{train,val} to the Roboflow project so teammate 2 can train.

Usage:
    python -m data.scripts.upload_roboflow --workspace <ws> --project <proj>

Uploads ONLY ms3seg. MSLesSeg must never go into the training project - it is the
"model has never seen this hospital" validation set.

Owner: teammate 3.
"""

import argparse
import json
from pathlib import Path

from roboflow import Roboflow
from tqdm import tqdm

from backend.app.config import settings

PROCESSED = Path(__file__).resolve().parents[1] / "processed"


def upload_split(project, split_dir: Path, split: str) -> None:
    """
    Roboflow's single-image upload accepts an annotation file per image. The
    simplest path is: write a per-image COCO json next to each PNG, then
    project.upload(image_path, annotation_path, split=split).

    TODO(teammate 3): implement. Test with 5 images first - the free plan has an
    image cap, so don't blow it on a bad export.
    """
    raise NotImplementedError


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", required=True)
    ap.add_argument("--project", required=True)
    args = ap.parse_args()

    rf = Roboflow(api_key=settings.roboflow_api_key)
    project = rf.workspace(args.workspace).project(args.project)
    upload_split(project, PROCESSED / "ms3seg" / "train", "train")
    upload_split(project, PROCESSED / "ms3seg" / "val", "valid")


if __name__ == "__main__":
    main()
