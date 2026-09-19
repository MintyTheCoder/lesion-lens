import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from roboflow import Roboflow

# 1. Target .env located directly inside the ml/ directory
ML_DIR = Path(__file__).resolve().parent
ENV_PATH = ML_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH, override=True)

ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")
if not ROBOFLOW_API_KEY:
    raise ValueError(f"ROBOFLOW_API_KEY is missing from {ENV_PATH}")

rf = Roboflow(api_key=ROBOFLOW_API_KEY)
project = rf.workspace("samuel-sleshi").project("ms-lesion-detection")

# 2. Resolve dataset path relative to project root (ValUnited/)
REPO_ROOT = ML_DIR.parent
DATASET_ROOT = REPO_ROOT / "data" / "processed" / "ms3seg_dataset"

splits = ("train", "valid", "test")

for split in splits:
    split_path = DATASET_ROOT / split
    annotation_file = split_path / "_annotations.coco.json"
    
    if not split_path.is_dir():
        print(f"Skipping {split}: Directory not found at {split_path}")
        continue

    images = list(split_path.glob("*.png")) + list(split_path.glob("*.jpg"))
    print(f"Uploading {len(images)} images to split: '{split}'...")

    for img_path in images:
        project.upload(
            image_path=str(img_path),
            annotation_path=str(annotation_file) if annotation_file.exists() else None,
            split=split,
            num_retry=3
        )

print("Upload complete!")