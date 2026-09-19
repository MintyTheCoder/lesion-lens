import nibabel as nib

flair_path = r"MS_100_patient_nifti.part1/MS_100_patient_nifti/001/001_FLAIR.nii.gz"
mask_path = r"MS_100_patient_masks/MS_100_patient_masks/abWMH_Masks/001/001_abWMH_Mask.nii.gz"

flair_img = nib.load(flair_path)
flair_data = flair_img.get_fdata()
print("FLAIR shape:", flair_data.shape)
print("FLAIR affine:\n", flair_img.affine)

mask_img = nib.load(mask_path)
mask_data = mask_img.get_fdata()
print("MASK shape:", mask_data.shape)