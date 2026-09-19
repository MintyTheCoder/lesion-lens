import nibabel as nib
import numpy as np
import cv2
from scipy import ndimage

MIN_LESION_AREA = 3
TARGET_SIZE = (256, 256)

def load_patient(patient):
    flair_path = f"MS_100_patient_nifti/MS_100_patient_nifti/{patient}/{patient}_FLAIR.nii.gz"
    mask_path = f"MS_100_patient_masks/MS_100_patient_masks/abWMH_Masks/{patient}/{patient}_abWMH_Mask.nii.gz"

    flair_data = nib.load(flair_path).get_fdata()
    mask_data = nib.load(mask_path).get_fdata()

    if flair_data.shape != mask_data.shape:
        return None, None

    return flair_data, mask_data

def extract_boxes(slice_mask):
    labeled, num = ndimage.label(slice_mask)
    boxes = []
    for lesion_id in range(1, num + 1):
        ys, xs = np.where(labeled == lesion_id)
        if len(ys) < MIN_LESION_AREA:
            continue
        boxes.append((int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())))
    return boxes

def preprocess_slice(slice_2d, target_size=TARGET_SIZE):
    norm = cv2.normalize(slice_2d, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(norm)

    h, w = enhanced.shape
    scale = min(target_size[0] / h, target_size[1] / w)
    new_h, new_w = int(h * scale), int(w * scale)
    resized = cv2.resize(enhanced, (new_w, new_h))

    pad_h = target_size[0] - new_h
    pad_w = target_size[1] - new_w
    top, bottom = pad_h // 2, pad_h - pad_h // 2
    left, right = pad_w // 2, pad_w - pad_w // 2
    padded = cv2.copyMakeBorder(resized, top, bottom, left, right, cv2.BORDER_CONSTANT, value=0)

    return padded, scale, (left, top)

def scale_boxes(boxes, scale, offset):
    left, top = offset
    scaled = []
    for x_min, y_min, x_max, y_max in boxes:
        scaled.append((
            int(x_min * scale) + left,
            int(y_min * scale) + top,
            int(x_max * scale) + left,
            int(y_max * scale) + top,
        ))
    return scaled

def process_patient(patient):
    flair_data, mask_data = load_patient(patient)
    if flair_data is None:
        return []

    results = []
    for z in range(mask_data.shape[2]):
        slice_mask = mask_data[:, :, z]
        if slice_mask.sum() == 0:
            continue

        boxes = extract_boxes(slice_mask)
        if not boxes:
            continue

        raw_slice = flair_data[:, :, z]
        processed_slice, scale, offset = preprocess_slice(raw_slice)
        scaled_boxes = scale_boxes(boxes, scale, offset)

        results.append({
            "patient": patient,
            "slice": z,
            "image": processed_slice,
            "boxes": scaled_boxes,
        })

    return results

if __name__ == "__main__":
    sample = process_patient("001")
    print("Lesion-containing slices for patient 001:", len(sample))
    if sample:
        print("First entry boxes:", sample[0]["boxes"])
        print("Image shape:", sample[0]["image"].shape)