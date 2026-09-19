import os
from pipeline_ms3seg import process_patient

NIFTI_ROOT = "MS_100_patient_nifti"

available_patients = sorted(
    p for p in os.listdir(NIFTI_ROOT)
    if os.path.isdir(os.path.join(NIFTI_ROOT, p))
)
print("Available patients:", len(available_patients))
print(available_patients[:10])

all_results = []
skipped = []

for patient in available_patients:
    result = process_patient(patient)
    if not result:
        skipped.append(patient)
        continue
    all_results.extend(result)

print("Patients processed:", len(available_patients) - len(skipped))
print("Patients skipped (missing mask or shape mismatch):", skipped)
print("Total lesion-containing image entries:", len(all_results))