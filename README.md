# Val United — MS Lesion Specificity

**VTHacks 14.** A clinician-facing tool: upload a FLAIR MRI slice → every white-matter lesion is boxed, each is flagged **MS-typical** or **atypical/nonspecific** using established radiological criteria, and a lesion-burden score + plain-language summary come back. Cross-hospital validation shows whether it holds up on data the model never saw.

MS is misdiagnosed ~18% of the time, and the most common mimic is migraine. The root cause is over-calling nonspecific white-matter lesions as MS. This is decision support for a doctor's second look — never shown to a patient, never a standalone diagnosis.

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
 MS3SEG NIfTI ──► slices ──►  Roboflow project ──► RF-DETR-B     POST /analyze ──────► ScanViewer
 masks ──► boxes ──► COCO      (hosted train)      (hosted API)   ├─ ml.pipeline         BurdenCard
                                     │                  │         ├─ Gemini summary      LesionTable
 MSLesSeg (sealed) ───────────► validate.py ◄───────────┘         ├─ MongoDB save        SummaryCard
                                     │                            GET /validation ─────► ValidationPanel
                                     └──► results/validation.json
```

**The one integration point:** `ml/pipeline.py:run_pipeline(image_bytes) -> AnalysisResult`. The shape of `AnalysisResult` is defined once in `backend/app/schemas.py` and mirrored in `frontend/src/api/types.ts`. If you change the schema, change both files + `backend/app/fixtures/mock_analysis.json` in the same PR.

## Run it

```powershell
# Python (one shared env for data/, ml/, backend/) — Python 3.11+
python -m venv .venv
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

- **MS3SEG** — training. ~2,000 annotated FLAIR slices; abnormal-WMH class converted to boxes.
- **MSLesSeg** — validation only. 115 scans, multi-hospital, never uploaded to the training project.

Both public. Do not scrape MRI images from anywhere else.

## Fallback order

1. Cut the heuristic pattern layer → detection + burden only (fully defensible)
2. Cut UI polish before model reliability
3. Cut MongoDB before Gemini

See `PLAN.md` for the full brief, pitch timing, and metrics.
