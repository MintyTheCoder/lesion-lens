# `data/` — Dataset pipeline

**Your goal:** turn MS3SEG into a bounding-box dataset in Roboflow that the `ml` owner can train on, and export MSLesSeg the same way *without* uploading it — it's the "model has never seen this hospital" validation set.

You're done when:

1. The Roboflow project has a train/valid split of MS3SEG slices with one `lesion` box per blob.
2. `data/processed/ms3seg/val/` and `data/processed/mslesseg/` exist locally (images + COCO json) for `ml/validate.py`.
3. Someone else can reproduce it by running the two commands in "Steps" below.

## Setup

```powershell
python -m venv .venv ; .venv\Scripts\activate ; pip install -r requirements.txt
```

Run every script **from the repo root** as a module: `python -m data.scripts.<name>`.

## Get the datasets

Both are public, no access request needed. Do not scrape MRI images from anywhere else.

| Dataset | What it is | Where |
|---|---|---|
| **MS3SEG** | ~2,000 annotated FLAIR slices, tri-mask labels — we use the *abnormal WMH* class | Search "MS3SEG dataset" — comes with the paper. Note the exact download URL here once you have it. |
| **MSLesSeg** | 115 scans, multiple hospitals, binary lesion masks | Search "MSLesSeg dataset" (2024 challenge). Note the URL here. |

Put them under `data/raw/` (gitignored). Suggested layout — **adjust `find_cases()` in `export_coco.py` to whatever the real layout is, then document it here**:

```
data/raw/
├── ms3seg/
│   └── <case_id>/
│       ├── flair.nii.gz
│       └── mask.nii.gz        # abnormal-WMH label only (may need to threshold a multi-class mask)
└── mslesseg/
    └── <case_id>/
        ├── flair.nii.gz
        └── mask.nii.gz
```

## Steps

```powershell
# 1. MS3SEG -> processed/ms3seg/{train,val}   (split by patient, 15% val)
python -m data.scripts.export_coco --dataset ms3seg --val-frac 0.15

# 2. MSLesSeg -> processed/mslesseg/val       (100% val - it is never trained on)
python -m data.scripts.export_coco --dataset mslesseg --val-frac 1.0

# 3. Upload ONLY ms3seg to Roboflow
python -m data.scripts.upload_roboflow --workspace <ws> --project <proj>
```

## What each script does (and what's left for you)

| File | Status | Job |
|---|---|---|
| `preprocess.py` | **works** | normalize → CLAHE → resize/pad to 560×560. Also used by the backend at inference time, so **don't fork it** — tune the constants if needed. `transform_mask()` applies the same geometry to a mask. |
| `masks_to_boxes.py` | **works** | connected components (8-connected) → `[x, y, w, h]`. Drops blobs < 6 px, pads boxes to ≥ 4 px. |
| `load_nifti.py` | works, **verify orientation** | NIfTI → axial slices. Check one volume visually: is the last axis really axial? Are slices "face up" as PNGs? |
| `export_coco.py` | **`find_cases()` is a TODO** | walks raw/, writes PNGs + `annotations.json`. Splits by *patient*, never by slice. |
| `upload_roboflow.py` | **`upload_split()` is a TODO** | pushes processed/ms3seg to the Roboflow project. |

## Why each preprocessing step

- **Percentile normalization** — raw NIfTI intensities are arbitrary floats that differ per scanner. 1st–99th percentile clip → 0–255 makes slices comparable.
- **CLAHE** — local contrast enhancement; small WMH lesions are low-contrast against surrounding white matter. This makes them pop for the detector.
- **Resize/pad to 560** — RF-DETR-B's input size (must be divisible by 56). Padding (not stretching) keeps lesion shapes intact, which the heuristic layer depends on.

## Gotchas

- **Empty slices**: `iter_axial_slices` skips slices with no lesion pixels by default. That's right for training a detector on a free plan with an image cap. If the model over-detects later, add back ~10% empty slices.
- **Tri-mask in MS3SEG**: the mask may be multi-class. Only the abnormal-WMH class becomes boxes — check the label values.
- **Free plan image cap**: upload 5 images first and look at them in the Roboflow UI before uploading everything. A bad orientation bug across 2,000 uploads is hard to undo.
- **MSLesSeg stays sealed**: never upload it to the training project. The whole "cross-hospital validation" demo moment depends on this.
- **Split leakage**: adjacent slices from one scan look nearly identical. `export_coco.py` splits by case_id — keep it that way.

## Hand-off

Tell the `ml` owner: the Roboflow project name, the version number you generated, and the paths to `processed/ms3seg/val` and `processed/mslesseg/val`.
