import os
import json
import random
import cv2
from run_ms3seg_pipeline import run_pipeline

OUTPUT_DIR = "../processed/coco_export"
IMAGES_DIR = os.path.join(OUTPUT_DIR, "images")
os.makedirs(IMAGES_DIR, exist_ok=True)

TARGET_COUNT = 650

all_results, skipped, available_patients = run_pipeline()

random.seed(42)
if len(all_results) > TARGET_COUNT:
    all_results = random.sample(all_results, TARGET_COUNT)

print("Using", len(all_results), "of the available lesion-containing slices")

coco = {
    "images": [],
    "annotations": [],
    "categories": [{"id": 1, "name": "lesion"}],
}

annotation_id = 1

for image_id, entry in enumerate(all_results, start=1):
    filename = f"{entry['patient']}_slice{entry['slice']}.png"
    filepath = os.path.join(IMAGES_DIR, filename)
    cv2.imwrite(filepath, entry["image"])

    h, w = entry["image"].shape
    coco["images"].append({
        "id": image_id,
        "file_name": filename,
        "width": w,
        "height": h,
    })

    for x_min, y_min, x_max, y_max in entry["boxes"]:
        box_w = x_max - x_min
        box_h = y_max - y_min
        coco["annotations"].append({
            "id": annotation_id,
            "image_id": image_id,
            "category_id": 1,
            "bbox": [x_min, y_min, box_w, box_h],
            "area": box_w * box_h,
            "iscrowd": 0,
        })
        annotation_id += 1

with open(os.path.join(OUTPUT_DIR, "annotations.json"), "w") as f:
    json.dump(coco, f)

print("Images written:", len(coco["images"]))
print("Annotations written:", len(coco["annotations"]))
print("Saved to:", OUTPUT_DIR)