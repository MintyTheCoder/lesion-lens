"""
raw/ NIfTI volumes -> processed/<dataset>/{train,val}/images/*.png + annotations.json (COCO).

Usage:
    python -m data.scripts.export_coco --dataset ms3seg   --val-frac 0.15
    python -m data.scripts.export_coco --dataset mslesseg --val-frac 1.0     # ALL of MSLesSeg is validation

Split by PATIENT, never by slice - adjacent slices from the same scan are nearly
identical and would leak train into val.

Owner: teammate 3. See data/README.md for raw/ layout.
"""

import argparse
import json
import random
from pathlib import Path

import cv2
from tqdm import tqdm

from data.scripts.load_nifti import iter_axial_slices, load_volume
from data.scripts.masks_to_boxes import mask_to_boxes
from data.scripts.preprocess import preprocess_slice, transform_mask

RAW = Path(__file__).resolve().parents[1] / "raw"
PROCESSED = Path(__file__).resolve().parents[1] / "processed"

CATEGORIES = [{"id": 1, "name": "lesion"}]


def find_cases(dataset: str) -> list[tuple[str, Path, Path]]:
    """
    Return [(case_id, flair_path, mask_path), ...] for a dataset.

    TODO(teammate 3): implement per dataset once you see the real folder layout.
    Document the layout you settled on in data/README.md.
    """
    raise NotImplementedError


def export_split(cases: list[tuple[str, Path, Path]], out_dir: Path) -> None:
    images_dir = out_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    images, annotations = [], []
    img_id = ann_id = 0

    for case_id, flair_path, mask_path in tqdm(cases, desc=out_dir.name):
        flair, mask = load_volume(flair_path), load_volume(mask_path)
        for z, f, m in iter_axial_slices(flair, mask):
            img = preprocess_slice(f)
            boxes = mask_to_boxes(transform_mask(m))
            if not boxes:
                continue
            fname = f"{case_id}_z{z:03d}.png"
            cv2.imwrite(str(images_dir / fname), img)
            images.append({"id": img_id, "file_name": fname, "width": img.shape[1], "height": img.shape[0]})
            for x, y, w, h in boxes:
                annotations.append(
                    {"id": ann_id, "image_id": img_id, "category_id": 1, "bbox": [x, y, w, h], "area": w * h, "iscrowd": 0}
                )
                ann_id += 1
            img_id += 1

    (out_dir / "annotations.json").write_text(
        json.dumps({"images": images, "annotations": annotations, "categories": CATEGORIES})
    )
    print(f"{out_dir}: {len(images)} images, {len(annotations)} boxes")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", choices=["ms3seg", "mslesseg"], required=True)
    ap.add_argument("--val-frac", type=float, default=0.15)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    cases = find_cases(args.dataset)
    random.Random(args.seed).shuffle(cases)
    n_val = round(len(cases) * args.val_frac)
    val, train = cases[:n_val], cases[n_val:]

    if train:
        export_split(train, PROCESSED / args.dataset / "train")
    if val:
        export_split(val, PROCESSED / args.dataset / "val")


if __name__ == "__main__":
    main()
