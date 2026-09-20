# LesionLens — MS Lesion Specificity

**VTHacks 14.** A clinician-facing tool: upload a FLAIR MRI slice → every white-matter lesion is boxed, each is flagged **MS-typical** or **atypical/nonspecific** using established radiological criteria, and a lesion-burden score + plain-language summary come back. Cross-hospital validation shows whether it holds up on data the model never saw.

MS is misdiagnosed ~18% of the time, and the most common mimic is migraine. The root cause is over-calling nonspecific white-matter lesions as MS. This is decision support for a doctor's second look — never shown to a patient, never a standalone diagnosis.

## Status

End-to-end and working: a trained RF-DETR-B model is live on Roboflow, the heuristic pattern layer is implemented, cross-dataset validation has run for real (see numbers below, not placeholders), and the backend + frontend (landing page, upload flow, history, validation panel) all work together. Remaining before judging: the Phase 7 checklist in `CLAUDE.md` §6 — spot-checking the pattern layer against real (not synthetic) detections, and confirming `GEMINI_API_KEY`/`MONGODB_URI` are live for the actual demo rather than running on mock/fallback.

## Team

| Person | Owns | Branch |
|---|---|---|
| Montgomery Brown | `data/` — datasets → COCO in Roboflow | `data` |
| Samuel Sleshi | `ml/` — Roboflow training, inference, heuristics, validation | `ml` |
| Nolawi Melese | `backend/` + `frontend/` | `app` |

Work on your branch, PR into `main` whenever something runs. Each directory has its own README that is your briefing — read it first.

## The honesty rule (everyone rehearses this)

There is **no migraine-patient data** in MS3SEG or MSLesSeg. The pattern flag applies established radiological heuristics to detected lesions. It is not a model trained or tested on confirmed migraine cases.

- ✅ "We encode established diagnostic criteria used to distinguish MS-typical lesions from nonspecific ones."
- ❌ "We trained this to detect migraine" / "our model distinguishes MS from migraine."

## How it fits together

```
 data/                          ml/                                backend/              frontend/
 ─────                          ───                                ────────              ─────────
 MS3SEG NIfTI ──► slices ──►  Roboflow project ──► RF-DETR-B     POST /analyze ──────► PlateFigure
 masks ──► boxes ──► COCO      (hosted train)      (hosted API)   ├─ ml.pipeline         (box overlay)
                                     │                  │         ├─ Gemini summary      CaseView
 MSLesSeg (sealed) ─► mslesseg_ ─► validate.py ◄───────────┘         ├─ MongoDB save        ├─ FindingsNote
                       eval_prep       │                            GET /validation ─────► └─ ValidationTable
                                       └──► results/validation.json
```

Preprocessing (normalize → CLAHE → resize/pad) lives in `data/pipeline/pipeline_ms3seg.py` — that's the pipeline actually deployed to Roboflow, and `ml/pipeline.py` (live inference) and `data/pipeline/mslesseg_eval_prep.py` (MSLesSeg conversion) both import it. `data/scripts/` is a separate, unfinished attempt at the same thing — nothing has been exported or uploaded through it, so don't treat it as canonical.

The frontend also has a `Landing.tsx` page (now `/`, not in the original plan) and a "load a sample" path (`frontend/public/samples/` + `frontend/src/samples.ts`) that shows the 3 rehearsed demo cases without needing an upload — paired with `backend/app/fixtures/demo_cache/`, which has those same 3 scans precomputed for offline/Wi-Fi-down fallback.

**The one integration point:** `ml/pipeline.py:run_pipeline(image_bytes) -> AnalysisResult`. The shape of `AnalysisResult` is defined once in `backend/app/schemas.py` and mirrored in `frontend/src/api/types.ts`. If you change the schema, change both files + `backend/app/fixtures/mock_analysis.json` in the same PR.

## Run it

`ValUnited/.venv` already exists at the repo root, built from `requirements.txt` — activate it instead of creating a new one unless you're on a fresh clone.

```powershell
# Python (one shared env for data/, ml/, backend/) — Python 3.11+
python -m venv .venv            # skip if .venv already exists
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env          # fill in keys you have; everything degrades gracefully without them

# Backend (from repo root) — http://localhost:8000/docs
uvicorn backend.app.main:app --reload

# Frontend — http://localhost:5173
cd frontend
npm install
npm run dev

# Tests
pytest backend/tests
```

With `USE_MOCK_INFERENCE=1` in `.env` (the default), `/analyze` returns a canned result so the frontend works before the model exists.

## Validate the model

`ml/validate.py` scores the trained model against held-out MS3SEG and against MSLesSeg (never trained on) using greedy IoU box matching (0.3), and writes precision / recall / false-positives-per-scan to `ml/results/validation.json` — served at `GET /validation`, shown in the frontend's validation panel.

```powershell
# One-time: convert raw MSLesSeg NIfTI into the COCO eval format validate.py needs
python -m data.pipeline.mslesseg_eval_prep

# Score the model — needs ROBOFLOW_API_KEY + ROBOFLOW_MODEL_ID in .env (a real trained model)
python -m ml.validate
```

`data.pipeline.mslesseg_eval_prep` reuses the same preprocessing/box-extraction as MS3SEG (`data/pipeline/pipeline_ms3seg.py`, the pipeline actually deployed to Roboflow) so predictions and ground truth land in the same coordinate space. It only needs to be run once (or again if `data/raw/MSLesSeg Dataset/` changes) — its output, `data/processed/mslesseg_dataset/test/`, is what `ml/validate.py` reads.

Current snapshot in `ml/results/validation.json` (re-run after any retrain or heuristics change — this will drift):

| Dataset | Scans | Precision | Recall | FP/scan | Flagged atypical |
|---|---|---|---|---|---|
| MS3SEG (held-out test) | 45 | 0.770 | 0.728 | 1.42 | 43% |
| MSLesSeg (never trained on) | 100 | 0.446 | 0.485 | 2.14 | 65% |

## Env vars

| Var | Who sets it | What |
|---|---|---|
| `ROBOFLOW_API_KEY` | ml | Roboflow account key |
| `ROBOFLOW_MODEL_ID` | ml | `workspace/project/version` from the Deploy tab |
| `ROBOFLOW_API_URL` | ml | default `https://serverless.roboflow.com` |
| `GEMINI_API_KEY` | app | plain-language summaries (template fallback without it) |
| `MONGODB_URI` | app | Atlas connection string (in-memory fallback without it) |
| `USE_MOCK_INFERENCE` | anyone | `1` = skip Roboflow, return the fixture |

## Stack

FastAPI · React + Vite + Tailwind · RF-DETR-B fine-tuned via Roboflow Train (free plan → inference over the hosted API) · OpenCV · scikit-image · Gemini · MongoDB Atlas

## Data

Trained on [MS3SEG](https://www.google.com/search?q=MS3SEG+dataset) and cross-dataset validated on [MSLesSeg](https://www.google.com/search?q=MSLesSeg+dataset) — both public MRI lesion-segmentation datasets. MSLesSeg was never used in training.

- **MS3SEG** — training. ~2,000 annotated FLAIR slices; abnormal-WMH class converted to boxes.
- **MSLesSeg** — validation only. 115 scans, multi-hospital, never uploaded to the training project.

Both public. Do not scrape MRI images from anywhere else.

## Fallback order

1. Cut the heuristic pattern layer → detection + burden only (fully defensible)
2. Cut UI polish before model reliability
3. Cut MongoDB before Gemini

See `PLAN.md` for the full brief, pitch timing, and metrics.
