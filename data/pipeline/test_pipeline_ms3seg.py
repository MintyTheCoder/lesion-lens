import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage
import cv2

patient = "001"

flair_path = rf"MS_100_patient_nifti.part1/MS_100_patient_nifti/{patient}/{patient}_FLAIR.nii.gz"
mask_path = rf"MS_100_patient_masks/MS_100_patient_masks/abWMH_Masks/{patient}/{patient}_abWMH_Mask.nii.gz"

flair_img = nib.load(flair_path)
flair_data = flair_img.get_fdata()
print("FLAIR shape:", flair_data.shape)
print("FLAIR affine:\n", flair_img.affine)

mask_img = nib.load(mask_path)
mask_data = mask_img.get_fdata()
print("MASK shape:", mask_data.shape)
print("MASK unique values:", np.unique(mask_data))

assert flair_data.shape == mask_data.shape

lesion_slices = [i for i in range(mask_data.shape[2]) if mask_data[:, :, i].sum() > 0]
mid_slice = lesion_slices[len(lesion_slices) // 2] if lesion_slices else flair_data.shape[2] // 2
print("Using slice:", mid_slice, "| lesion voxels in mask:", int(mask_data[:, :, mid_slice].sum()))

fig, axes = plt.subplots(1, 2, figsize=(10, 5))
axes[0].imshow(flair_data[:, :, mid_slice], cmap="gray")
axes[0].set_title("FLAIR")
axes[0].axis("off")

axes[1].imshow(flair_data[:, :, mid_slice], cmap="gray")
axes[1].imshow(mask_data[:, :, mid_slice], cmap="Reds", alpha=0.4)
axes[1].set_title("FLAIR + abWMH mask overlay")
axes[1].axis("off")

plt.tight_layout()
plt.savefig("test_slice.png", dpi=150)
print("Saved test_slice.png")

slice_mask = mask_data[:, :, mid_slice]
labeled, num_lesions = ndimage.label(slice_mask)
print("Lesions found:", num_lesions)

min_lesion_area = 3
filtered_boxes = []
for lesion_id in range(1, num_lesions + 1):
    ys, xs = np.where(labeled == lesion_id)
    if len(ys) < min_lesion_area:
        continue
    filtered_boxes.append((xs.min(), ys.min(), xs.max(), ys.max()))

print("Filtered lesions:", len(filtered_boxes))
print(filtered_boxes)

fig, ax = plt.subplots(figsize=(6, 6))
ax.imshow(flair_data[:, :, mid_slice], cmap="gray")
for x_min, y_min, x_max, y_max in filtered_boxes:
    rect = plt.Rectangle((x_min, y_min), x_max - x_min, y_max - y_min,
                          edgecolor="red", facecolor="none", linewidth=1.5)
    ax.add_patch(rect)
ax.axis("off")
plt.savefig("test_bboxes.png", dpi=150)
print("Saved test_bboxes.png")

all_patient_boxes = {}
for z in range(mask_data.shape[2]):
    slice_mask_z = mask_data[:, :, z]
    if slice_mask_z.sum() == 0:
        continue
    labeled_z, num_z = ndimage.label(slice_mask_z)
    boxes_z = []
    for lesion_id in range(1, num_z + 1):
        ys, xs = np.where(labeled_z == lesion_id)
        if len(ys) < min_lesion_area:
            continue
        boxes_z.append((xs.min(), ys.min(), xs.max(), ys.max()))
    if boxes_z:
        all_patient_boxes[z] = boxes_z

print("Slices with lesions:", len(all_patient_boxes))
print("Total lesion boxes:", sum(len(v) for v in all_patient_boxes.values()))

lesion_slice_ids = sorted(all_patient_boxes.keys())
sample_slices = lesion_slice_ids[::max(1, len(lesion_slice_ids) // 9)][:9]

fig, axes = plt.subplots(3, 3, figsize=(12, 12))
for ax, z in zip(axes.flat, sample_slices):
    ax.imshow(flair_data[:, :, z], cmap="gray")
    for x_min, y_min, x_max, y_max in all_patient_boxes[z]:
        rect = plt.Rectangle((x_min, y_min), x_max - x_min, y_max - y_min,
                              edgecolor="red", facecolor="none", linewidth=1.2)
        ax.add_patch(rect)
    ax.set_title(f"slice {z}", fontsize=9)
    ax.axis("off")

for ax in axes.flat[len(sample_slices):]:
    ax.axis("off")

plt.tight_layout()
plt.savefig("test_multislice.png", dpi=150)
print("Saved test_multislice.png")

def preprocess_slice(slice_2d, target_size=(256, 256)):
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

    return padded

test_slice_processed = preprocess_slice(flair_data[:, :, mid_slice])

fig, axes = plt.subplots(1, 2, figsize=(10, 5))
axes[0].imshow(flair_data[:, :, mid_slice], cmap="gray")
axes[0].set_title("Original")
axes[0].axis("off")
axes[1].imshow(test_slice_processed, cmap="gray")
axes[1].set_title("Normalized + CLAHE + resized/padded")
axes[1].axis("off")
plt.tight_layout()
plt.savefig("test_preprocessed.png", dpi=150)
print("Saved test_preprocessed.png")