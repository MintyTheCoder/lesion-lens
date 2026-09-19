# VTHacks 14 — MS Lesion Specificity: Project Brief

**Updated:** 2026-09-19
**Locked:** RF-DETR-B + Roboflow architecture · Option B (heuristic lesion-pattern layer)

---

## 1. The Build

**Problem.** MS misdiagnosis runs ~18% (Kaisey et al.) and persists: 72% of misdiagnosed patients are put on MS medication they don't need, ~33% stay misdiagnosed 10+ years (Solomon et al. 2016). Root cause is over-calling nonspecific white matter lesions as MS-typical. Migraine is the most common mimic pattern, and disproportionately affects women.

**Product.** Web app for clinicians. Upload a FLAIR MRI slice → get back:

- Annotated image, every white-matter lesion boxed
- Per-lesion flag: **MS-typical pattern** vs **atypical/nonspecific pattern**
- Lesion count + total area (burden score)
- Plain-language summary of findings
- Precision / false-positive readout, including performance on a dataset the model never trained on

**Flow.** Upload → RF-DETR inference (boxes + confidence) → heuristic pattern scoring per lesion → burden metrics → Gemini plain-language summary → save case to MongoDB → UI renders annotated image, burden score, explanation, validation panel.

**Framing (keep prominent):** decision support for a doctor's second look. Never shown to the patient, never a standalone diagnosis. This preempts most safety questions in Q&A.

---

## 2. Value to the Clinician

Judging whether a lesion pattern looks "MS-typical" is currently a subjective visual call with no quantified baseline — which is exactly where the 18% comes from.

| What changes                     | Why it matters                                                                   |
| -------------------------------- | -------------------------------------------------------------------------------- |
| Subjective read → quantified one | Exact count, area, per-lesion flag; repeatable and documentable                  |
| Second opinion at decision point | Atypical flag = concrete prompt to consider migraine, small-vessel disease       |
| Burden tracked over time         | Rising vs. stable count/area becomes a number, not an eyeball comparison         |
| Review time saved                | Counting, sizing, pattern-judging returned in inference time                     |
| Plain-language output            | Usable directly for referral notes or charting                                   |
| Cross-hospital trust             | MSLesSeg validation answers "does this hold outside the site it was trained on?" |
| Fits existing workflow           | Sits alongside McDonald criteria, doesn't replace judgment                       |

---

## 3. Architecture

Not replicating MS3SEG's 4-class dense tri-mask segmentation. Instead:

1. Source lesion masks — MS3SEG (abnormal WMH class) and/or MSLesSeg (binary masks)
2. Masks → bounding boxes via connected-component extraction (one blob = one box)
3. OpenCV preprocessing — slice normalization, CLAHE contrast, consistent resize/pad
4. Export to COCO via Roboflow, fine-tune RF-DETR-B for lesion instance detection
5. **Heuristic pattern layer (locked):** per-lesion geometric features known to separate MS-typical from vascular/nonspecific WMH — elongation and orientation relative to ventricles (Dawson's fingers), periventricular vs. subcortical location, ovoid shape
6. Burden signal — lesion count + total box area per scan
7. Cross-dataset check — train on MS3SEG, infer on MSLesSeg

Chosen over U-Net segmentation because RF-DETR + Roboflow is what the team already knows — protects timeline given the added heuristic scope.

---

## 4. Honesty Rule — Non-Negotiable

There is **no migraine-patient data** in MS3SEG or MSLesSeg. The pattern flag applies established radiological heuristics to detected lesions. It is not a model trained or tested on confirmed migraine-mimic cases.

> ✅ **Say:** "We encode established diagnostic criteria used to distinguish MS-typical lesions from nonspecific ones."
>
> ❌ **Never say:** "We trained this to detect migraine" / "our model distinguishes MS from migraine."

Every team member rehearses this verbatim. It is the single most likely judge question — it's the gap between the misdiagnosis-stat pitch and what the system technically does.

---

## 5. Data

| Dataset  | Role            | Detail                                                                                  |
| -------- | --------------- | --------------------------------------------------------------------------------------- |
| MS3SEG   | Training        | ~2,000 annotated FLAIR slices, tri-mask labels (abnormal WMH class), converted to boxes |
| MSLesSeg | Validation only | 115 scans, multi-hospital, binary lesion masks — untouched during training              |

Both public, no access request. Do not scrape MRI images from any other source. Cite both in the README and in deck fine print — costs nothing, avoids an awkward pause.

---

## 6. Build Steps

**Phase 1 — Data pipeline**
Acquire both datasets → load NIfTI volumes with `nibabel` → masks to boxes via connected components → OpenCV preprocessing → export COCO, upload to Roboflow → split train/val, keep MSLesSeg sealed.

**Phase 2 — Model training**
Fine-tune RF-DETR-B from pretrained checkpoint; confirm the pipeline runs on a small subset first. Checkpoint by **validation precision, not accuracy**. Wrap in an inference function (scan → boxes + confidence + count/area). Confirm latency is demo-fast.

**Phase 3 — Heuristic pattern layer**
Extract geometric features per detected lesion (orientation/elongation vs. ventricles, periventricular vs. subcortical, shape). Build the rule-based MS-typical/atypical classifier — feature-engineered, not separately trained, since there's no labeled migraine data. Integrate flags into inference output.

**Phase 4 — Cross-dataset validation**
One batch script: trained model + heuristic layer over MSLesSeg. Compute precision and per-scan false-positive rate on both held-out MS3SEG and MSLesSeg. Log to a table — this is the validation panel and the strongest demo moment.

**Phase 5 — Backend + Gemini**
One FastAPI/Flask endpoint: upload → inference → JSON (detections + flags + burden). Feed into Gemini for plain-language explanation using Section 4 phrasing exactly. MongoDB Atlas for case metadata, results, flags, explanation.

**Phase 6 — Frontend**
Upload flow → annotated image color-coded by pattern flag, count/area summary, Gemini explanation → validation panel front and center. Polish last.

**Phase 7 — Integration + rehearsal**
End-to-end test on several real scans. Pick 2–3 demo cases: one clean detection, one clear pattern-flag contrast, one cross-dataset. Rehearse the 4-minute pitch timed, with the Section 4 answer verbatim.

> **Checkpoint discipline:** if the core detector isn't training reliably by ~1/3 through build time, cut Phase 3 and ship detection + burden tracking only. A working detector beats a broken two-layer system.

---

## 7. Efficiency Rules

- Fine-tune from RF-DETR-B's checkpoint, never train from scratch
- Test on a reduced subset before any full training run
- Verify inference speed before judging, not during
- Lean backend: one endpoint
- Batch the validation run — one script over all of MSLesSeg
- Build Phase 3 only after the detector is confirmed working; it depends on detection output

---

## 8. Tech Stack

**Decided 2026-09-19.** Stack A: FastAPI + React/Vite. Roboflow **free plan** — RF-DETR-B is fine-tuned with Roboflow Train (hosted); weights cannot be downloaded, so all inference is an HTTP call to the Roboflow hosted API. The demo therefore depends on Wi-Fi; the backend falls back to a precomputed `demo_cache/` for rehearsed scans.

| Tool                              | Job                                                              |
| --------------------------------- | ---------------------------------------------------------------- |
| MS3SEG                            | Training data                                                    |
| MSLesSeg                          | Cross-dataset validation (sealed, never uploaded to Roboflow)    |
| nibabel + scipy                   | NIfTI loading, connected components → boxes                      |
| OpenCV                            | Normalization, CLAHE, resize/pad (shared train + inference)      |
| Roboflow (free) + RF-DETR-B       | Annotation hosting, hosted training, hosted inference via httpx  |
| scikit-image                      | Per-lesion geometric features for the heuristic layer            |
| FastAPI + Pydantic v2             | Backend API, the `AnalysisResult` contract                       |
| Gemini API (`google-genai`)       | Plain-language explanation                                       |
| MongoDB Atlas (`motor`)           | Case storage (in-memory fallback without a URI)                  |
| React 18 + Vite + TS + Tailwind   | Frontend, SVG box overlay                                        |
| Python 3.11+ venv, `requirements.txt` | One shared env for `data/`, `ml/`, `backend/`                |

---

## 9. Metrics

**Headline:** precision and per-scan false-positive rate — not accuracy.

- Precision = true lesions detected / all lesions detected
- FP rate per scan = nonspecific lesions wrongly flagged, averaged per scan

**Secondary:** lesion count + total area per scan (burden).

**Pattern layer:** reported descriptively ("X% of detected lesions flagged atypical"). Not an accuracy metric — no ground truth to validate against.

---

## 10. Tracks

- **Sponsor:** none
- **MLH:** Best Use of Gemini API, Best Use of MongoDB Atlas
- **General:** Best Ut Prosim, Best DEI Hack, Overall

---

## 11. Pitch (4 min)

| Time      | Beat                                                                                                                                                              |
| --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0:00–0:45 | Patient gets an MRI, misdiagnosed with MS — it was migraine. Cite Kaisey/Solomon.                                                                                 |
| 0:45–1:15 | Detectors already work. We built the two missing pieces: a pattern layer using established criteria, and cross-hospital validation nobody's done on this dataset. |
| 1:15–3:00 | Live demo — upload, detections with flags, precision/FP rate, holding up on MSLesSeg.                                                                             |
| 3:00–3:30 | Workflow fit (Section 2) + the Section 4 honesty line, stated exactly.                                                                                            |
| 3:30–4:00 | Close on the patient from the opener.                                                                                                                             |

---

## 12. Fallback Order

1. Cut the heuristic pattern layer → detection + burden tracking only (fully defensible on its own)
2. Cut UI polish before model reliability
3. Cut MongoDB before Gemini

Never claim the model was trained to detect migraine — that distinction holds regardless of which layer ships.

---

## 13. Repo Structure

Three workstreams, three directories, three branches. Each directory's `README.md` is its owner's briefing — read it before touching anything in there.

| Directory     | Owner              | Branch | Deliverable                                                   |
| ------------- | ------------------ | ------ | ------------------------------------------------------------- |
| `data/`       | data teammate      | `data` | COCO dataset in Roboflow; local `processed/` for validation   |
| `ml/`         | Roboflow teammate  | `ml`   | `run_pipeline(bytes) -> AnalysisResult`; `validation.json`    |
| `backend/` + `frontend/` | Nolawi  | `app`  | API + UI                                                      |

**The one integration point:** `ml/pipeline.py:run_pipeline`. Its return type `AnalysisResult` is defined in `backend/app/schemas.py`, mirrored in `frontend/src/api/types.ts`, and instantiated in `backend/app/fixtures/mock_analysis.json`. **Change all three in the same PR.**

```
ValUnited/
├── CLAUDE.md                     this brief
├── PLAN.md                       same content, human-facing copy
├── README.md                     team map, honesty rule, architecture diagram, run instructions
├── requirements.txt              one shared Python env (no torch — inference is HTTP)
├── .env.example                  ROBOFLOW_API_KEY, ROBOFLOW_MODEL_ID, ROBOFLOW_API_URL,
│                                 GEMINI_API_KEY, MONGODB_URI, USE_MOCK_INFERENCE
├── .gitignore                    data/raw, data/processed, .env, .venv, node_modules
│
├── data/                         ── DATA PIPELINE ──────────────────────────────────────
│   ├── README.md                 briefing: dataset download, raw/ layout, steps, gotchas
│   ├── raw/          (gitignored) NIfTI volumes as downloaded
│   ├── processed/    (gitignored) <dataset>/{train,val}/images/*.png + annotations.json (COCO)
│   └── scripts/                  run as `python -m data.scripts.<name>` from repo root
│       ├── preprocess.py         WORKS. normalize → CLAHE → resize/pad 560. Also used at
│       │                         inference time by ml/pipeline.py — never fork it.
│       ├── masks_to_boxes.py     WORKS. connected components (8-conn) → [x,y,w,h]; drops <6px
│       ├── load_nifti.py         NIfTI → axial slices. Verify orientation on one volume.
│       ├── export_coco.py        TODO find_cases(). Splits by PATIENT. --val-frac 1.0 for MSLesSeg
│       └── upload_roboflow.py    TODO upload_split(). Uploads ms3seg ONLY.
│
├── ml/                           ── MODEL + HEURISTICS + VALIDATION ─────────────────────
│   ├── README.md                 briefing: Roboflow training, feature defs, rule set, demo cache
│   ├── inference.py              WORKS. httpx POST to Roboflow hosted API → RawDetection list
│   ├── heuristics.py             TODO score_lesion(), classify_pattern(). Thresholds at top.
│   ├── burden.py                 TODO brain_area_px(). compute_burden() done.
│   ├── pipeline.py               run_pipeline(bytes) -> AnalysisResult   ← THE INTEGRATION POINT
│   ├── validate.py               TODO evaluate_dataset(). Writes results/validation.json
│   └── results/validation.json   placeholder zeros; served by GET /validation
│
├── backend/                      ── FASTAPI ────────────────────────────────────────────
│   ├── README.md                 endpoints, inference resolution order, degradation
│   ├── app/
│   │   ├── main.py               app + CORS + routers. `uvicorn backend.app.main:app --reload`
│   │   ├── config.py             Settings from .env; REPO_ROOT / FIXTURES_DIR / VALIDATION_PATH
│   │   ├── schemas.py            THE CONTRACT: AnalysisResult, Lesion, Burden, ValidationReport…
│   │   ├── routes/
│   │   │   ├── analyze.py        POST /analyze (multipart PNG/JPG)
│   │   │   ├── cases.py          GET /cases, GET /cases/{id}
│   │   │   └── validation.py     GET /validation
│   │   ├── services/
│   │   │   ├── inference.py      mock → run_pipeline → demo_cache → 503
│   │   │   ├── gemini.py         summary prompt; hard-codes the §4 honesty rule; template fallback
│   │   │   └── db.py             motor (Atlas) with in-memory fallback
│   │   └── fixtures/
│   │       ├── mock_analysis.json     what /analyze returns when USE_MOCK_INFERENCE=1
│   │       └── demo_cache/<sha256>.json  precomputed results for rehearsed demo scans
│   └── tests/test_analyze.py     5 smoke tests in mock mode. `pytest backend/tests`
│
└── frontend/                     ── REACT + VITE + TAILWIND ────────────────────────────
    ├── README.md                 pages, components, polish TODOs
    ├── package.json  vite.config.ts (proxies /api → :8000)  tailwind.config.ts  tsconfig.json
    ├── index.html
    └── src/
        ├── main.tsx  App.tsx     router + header with the "decision support" line
        ├── api/
        │   ├── types.ts          mirrors schemas.py
        │   └── client.ts         analyze(file), getCases(), getCase(id), getValidation()
        ├── mocks/analysis.json   copy of the backend fixture; "Load mock result" button uses it
        ├── components/
        │   ├── UploadDropzone.tsx
        │   ├── ScanViewer.tsx    <img> + <svg viewBox> overlay; orange = MS-typical, sky = atypical
        │   ├── LesionTable.tsx   click row ↔ viewer selection
        │   ├── BurdenCard.tsx    count / % burden / typical / atypical
        │   ├── SummaryCard.tsx   Gemini text + fixed "not a diagnosis" line
        │   └── ValidationPanel.tsx  GET /validation table
        └── pages/
            ├── Analyze.tsx       upload → results layout
            └── History.tsx       saved cases from Mongo
```

### Conventions

- Run all Python from the repo root as modules (`python -m ml.validate`, `uvicorn backend.app.main:app`). Imports are absolute (`from backend.app.schemas import ...`).
- `USE_MOCK_INFERENCE=1` (the default) makes the whole app work with no keys and no model. Every integration degrades gracefully: no Gemini key → template summary; no Mongo URI → in-memory store.
- `data/scripts/preprocess.py` is shared between training-set export and inference. If train and inference preprocessing drift, the model silently degrades.
- Before judging: populate `backend/app/fixtures/demo_cache/` via `save_to_demo_cache()` for each rehearsed slice (see `ml/README.md` step 4).
