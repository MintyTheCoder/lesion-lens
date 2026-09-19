import os
import json
import random
import cv2
from pipeline_ms3seg import process_patient

NIFTI_ROOT = "../raw/MS_100_patient_nifti"
OUTPUT_ROOT = "../processed/ms3seg_dataset"

TOTAL_TARGET = 650
TRAIN_FRAC = 0.78
VALID_FRAC = 0.15
TEST_FRAC = 0.07

random.seed(42)

all_patients = sorted(
    p for p in os.listdir(NIFTI_ROOT)
    if os.path.isdir(os.path.join(NIFTI_ROOT, p))
)
random.shuffle(all_patients)

n = len(all_patients)
n_train = int(n * TRAIN_FRAC)
n_valid = int(n * VALID_FRAC)

train_patients = all_patients[:n_train]
valid_patients = all_patients[n_train:n_train + n_valid]
test_patients = all_patients[n_train + n_valid:]

overlap = (set(train_patients) & set(valid_patients)) | (set(train_patients) & set(test_patients)) | (set(valid_patients) & set(test_patients))
assert not overlap, f"Patient overlap across splits: {overlap}"

print("Patients — train:", len(train_patients), "valid:", len(valid_patients), "test:", len(test_patients))
print("Overlap check passed: no patient appears in more than one split")

def collect_entries(patients):
    entries = []
    skipped = []
    for patient in patients:
        result = process_patient(patient)
        if not result:
            skipped.append(patient)
            continue
        entries.extend(result)
    return entries, skipped

def export_split(split_name, entries, target_count):
    if len(entries) > target_count:
        entries = random.sample(entries, target_count)

    split_dir = os.path.join(OUTPUT_ROOT, split_name)
    os.makedirs(split_dir, exist_ok=True)

    coco = {
        "images": [],
        "annotations": [],
        "categories": [{"id": 1, "name": "lesion"}],
    }

    annotation_id = 1
    for image_id, entry in enumerate(entries, start=1):
        filename = f"{entry['patient']}_slice{entry['slice']}.png"
        filepath = os.path.join(split_dir, filename)
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

    with open(os.path.join(split_dir, "_annotations.coco.json"), "w") as f:
        json.dump(coco, f)

    print(f"{split_name}: {len(coco['images'])} images, {len(coco['annotations'])} annotations")

train_entries, train_skipped = collect_entries(train_patients)
valid_entries, valid_skipped = collect_entries(valid_patients)
test_entries, test_skipped = collect_entries(test_patients)

print("Skipped patients — train:", train_skipped, "valid:", valid_skipped, "test:", test_skipped)

export_split("train", train_entries, int(TOTAL_TARGET * TRAIN_FRAC))
export_split("valid", valid_entries, int(TOTAL_TARGET * VALID_FRAC))
export_split("test", test_entries, int(TOTAL_TARGET * TEST_FRAC))

print("Done. Output in:", OUTPUT_ROOT)