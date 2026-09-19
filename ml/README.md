# `ml/` — Model, heuristics, validation

**Your goal:** give the backend one working function — `run_pipeline(image_bytes) -> AnalysisResult` — and produce the cross-dataset validation numbers for the demo.

You're done when:

1. `ROBOFLOW_MODEL_ID` + `ROBOFLOW_API_KEY` in `.env` point at a trained RF-DETR-B and `python -c "from ml.pipeline import run_pipeline; ..."` returns lesions on a real slice in a few seconds.
2. Every detected lesion carries a `pattern` flag (`ms_typical` / `atypical`) with human-readable `reasons`.
3. `ml/results/validation.json` has **real** precision / recall / FP-per-scan for held-out MS3SEG *and* MSLesSeg.
4. `backend/app/fixtures/demo_cache/` holds precomputed results for the 2–3 rehearsed demo scans (Wi-Fi insurance).

## Setup

```powershell
python -m venv .venv ; .venv\Scripts\activate ; pip install -r requirements.txt
copy .env.example .env      # set USE_MOCK_INFERENCE=0 once your model exists
```

Run everything from the repo root.

## Step 1 — Train in Roboflow (hosted)

We're on the **free plan**: train in the Roboflow UI, and **weights cannot be downloaded**, so inference is always an HTTP call to Roboflow's hosted API. That's already wired up in `inference.py`.

1. The `data` owner uploads MS3SEG to the project. Once a version exists, look at ~20 images in the Roboflow UI. Do the boxes sit on lesions? Are images oriented sanely? If not, fix the data pipeline first — training on garbage wastes free credits.
2. Generate a version. Augmentation: horizontal flip is fine (brains are roughly symmetric), rotation ±10° is fine. **No** vertical flip, no color jitter that would wash out CLAHE.
3. Train → pick **RF-DETR-B**, start from the pretrained checkpoint (never from scratch).
4. Judge the trained version by **precision** at a sane confidence, not mAP alone (PLAN.md §9). We'd rather miss a faint lesion than box noise — false positives are exactly the failure mode the whole project is about.
5. Deploy tab → copy the model id (`workspace/project/version`) into `.env`. Note whether the endpoint shown is `serverless.roboflow.com` or `detect.roboflow.com` and set `ROBOFLOW_API_URL` to match.

Sanity check: `python -c "import cv2; from ml.inference import detect; print(detect(cv2.imread('data/processed/ms3seg/val/images/<any>.png')))"`

## Step 2 — Implement the stubs

| File | Function | Status | What it must do |
|---|---|---|---|
| `inference.py` | `detect(image) -> list[RawDetection]` | **works** | POST to Roboflow, convert center-xywh → top-left `[x,y,w,h]`. Tune `confidence_threshold`. |
| `heuristics.py` | `score_lesion(crop, bbox, image_shape) -> LesionFeatures` | TODO | geometric features per lesion (below) |
| `heuristics.py` | `classify_pattern(features, bbox, image_shape) -> (Pattern, reasons)` | TODO | the rule set (below) |
| `burden.py` | `brain_area_px(image) -> int` | TODO | count non-background pixels (threshold > 10, fill holes, largest component) |
| `pipeline.py` | `run_pipeline(image_bytes) -> AnalysisResult` | **works once the above do** | glue; also swap `area_px` from box area to blob area |
| `validate.py` | `evaluate_dataset(name, dir) -> DatasetValidation` | TODO | IoU-match predictions vs COCO GT, write `results/validation.json` |

## The heuristic pattern layer — what it is and isn't

**It is:** a rule-based encoding of the morphology criteria radiologists already use to call a lesion "MS-typical" (the shape/location parts of the McDonald criteria and the "Dawson's fingers" sign).

**It is not:** a classifier trained on migraine data. We have none. In Q&A say exactly: *"We encode established diagnostic criteria used to distinguish MS-typical lesions from nonspecific ones."* Never *"we trained it to detect migraine."*

### Features (per lesion, from `skimage.measure.regionprops` on an Otsu-thresholded crop)

| Feature | How | MS-typical direction |
|---|---|---|
| `elongation` | `major_axis_length / minor_axis_length` | > ~1.8 (ovoid/elongated, not round) |
| `orientation_deg` | regionprops `orientation` → degrees | axis points *radially outward from the ventricles* (perpendicular to the ventricle wall) |
| `location` | normalized distance of box center from image center (`_location_from_bbox`) | periventricular or juxtacortical — *not* deep subcortical WM |
| `ovoid_score` | `solidity` (blob area / convex hull area) | high = smooth ovoid; low = irregular/punctate |

Why image center ≈ ventricles: on an axial FLAIR slice the lateral ventricles sit near the middle. It's a proxy, not a segmentation — say so if asked. If you have time, a real ventricle mask (dark CSF region near center on FLAIR) makes "perpendicular to ventricle" much more defensible.

### Starting rule set (`classify_pattern`)

```
periventricular AND elongated AND axis roughly radial     → ms_typical   "Dawson's finger pattern"
juxtacortical  AND ovoid                                  → ms_typical
periventricular AND ovoid                                 → ms_typical
otherwise (deep WM, punctate/round, no radial orientation) → atypical     "nonspecific — also seen in migraine / small-vessel disease"
```

Thresholds live at the top of `heuristics.py`. **Tune them by eye** on 20–30 real detections — you're aiming for flags a radiologist would nod at, not a metric (there's no ground truth for this). `reasons` must be short human phrases; the UI shows them on hover and Gemini writes the summary from them.

## Step 3 — Validation (the demo's strongest moment)

```powershell
python -m ml.validate --ms3seg data/processed/ms3seg/val --mslesseg data/processed/mslesseg/val
```

- Match predicted boxes to GT boxes greedily by IoU ≥ **0.3** (lesions are tiny; 0.5 is too strict for blob-derived boxes).
- Report per dataset: `precision`, `recall`, `fp_per_scan`, `atypical_pct` (descriptive only).
- Every image is one API call — run on ~100 slices first, then the full sets.
- The result is served at `GET /validation` and shown in the UI's validation panel. Placeholder zeros are there now; **replace them or hide the panel** before demo.

## Step 4 — Demo cache (do this before judging)

The demo depends on venue Wi-Fi reaching Roboflow. For each of the 2–3 rehearsed demo slices:

```python
from pathlib import Path
from ml.pipeline import run_pipeline
from backend.app.services.inference import save_to_demo_cache
b = Path("demo/slice1.png").read_bytes()
save_to_demo_cache(b, run_pipeline(b))
```

The backend serves the cached result automatically (keyed by file hash) if the API call fails. Commit the JSON files.

## Checkpoint rule

If the detector isn't producing sensible boxes by ~1/3 of build time, **skip the heuristics** and ship detection + burden only. `classify_pattern` can return `("ms_typical", [])` for everything; the UI still works. A working detector beats a broken two-layer system.
