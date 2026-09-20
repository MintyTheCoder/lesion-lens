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

**Phase 1 — Data pipeline · DONE**
Acquire both datasets → load NIfTI volumes with `nibabel` → masks to boxes via connected components → OpenCV preprocessing → export COCO, upload to Roboflow → split train/val, keep MSLesSeg sealed. Ran through `data/pipeline/` (not the originally-planned `data/scripts/`, which never got finished — see section 13). MS3SEG exported to `data/processed/ms3seg_dataset/{train,valid,test}`; MSLesSeg converted separately by `data/pipeline/mslesseg_eval_prep.py` into `data/processed/mslesseg_dataset/test/`, pooling its raw `train/`+`test/` folders since 100% of it is validation here regardless of MSLesSeg's own internal split. Uploaded to Roboflow via `ml/finetune.py` (misleadingly named — it's the upload script, not local training).

**Phase 2 — Model training · DONE**
Fine-tune RF-DETR-B from pretrained checkpoint; confirm the pipeline runs on a small subset first. Checkpoint by **validation precision, not accuracy**. Wrap in an inference function (scan → boxes + confidence + count/area). Confirm latency is demo-fast. A trained model is live on Roboflow (`ROBOFLOW_MODEL_ID` set); `ml/inference.py::detect()` calls it.

**Phase 3 — Heuristic pattern layer · DONE**
Extract geometric features per detected lesion (orientation/elongation vs. ventricles, periventricular vs. subcortical, shape). Build the rule-based MS-typical/atypical classifier — feature-engineered, not separately trained, since there's no labeled migraine data. Integrate flags into inference output. `ml/heuristics.py::score_lesion`/`classify_pattern` implemented; thresholds tunable at the top of the file. Per the Phase 7 checklist below, still needs a by-eye spot-check against real (not synthetic) detections.

**Phase 4 — Cross-dataset validation · DONE**
One batch script: trained model + heuristic layer over MSLesSeg. Compute precision and per-scan false-positive rate on both held-out MS3SEG and MSLesSeg. Log to a table — this is the validation panel and the strongest demo moment. `python -m ml.validate` runs for real against the live model; `ml/results/validation.json` holds real numbers, not placeholders (see section 13 for the current snapshot). Raw detections are cached to disk (`ml/results/detection_cache/`) so re-scoring after a heuristics change doesn't re-hit Roboflow's free-tier API.

**Phase 5 — Backend + Gemini · DONE**
One FastAPI/Flask endpoint: upload → inference → JSON (detections + flags + burden). Feed into Gemini for plain-language explanation using Section 4 phrasing exactly. MongoDB Atlas for case metadata, results, flags, explanation. `POST /analyze`, `GET /cases`/`GET /cases/{id}`, `GET /validation` all implemented; Gemini summary hard-codes the section 4 honesty line in its system prompt with a template fallback; Mongo save has an in-memory fallback. Per the Phase 7 checklist, confirm real keys are live before the actual demo — `USE_MOCK_INFERENCE`/fallbacks are dev conveniences.

**Phase 6 — Frontend · DONE (polish ongoing)**
Upload flow → annotated image color-coded by pattern flag, count/area summary, Gemini explanation → validation panel front and center. Polish last. Landing page, Analyze flow, and History page all exist; results UI was restructured into `case/` (CaseView, BurdenKey, FindingsNote, ValidationTable) and `plate/` (PlateFrame/PlateFigure/PlateAction/PlateIntake) component groups — see section 13 for the current tree, since it no longer matches the original ScanViewer/BurdenCard component names this brief originally sketched.

**Phase 7 — Integration + rehearsal**
End-to-end test on several real scans. Pick 2–3 demo cases: one clean detection, one clear pattern-flag contrast, one cross-dataset. Rehearse the 4-minute pitch timed, with the Section 4 answer verbatim. The 3 demo cases are already picked and wired up (`frontend/public/samples/` + `backend/app/fixtures/demo_cache/`: `clean-detection`, `pattern-contrast`, `cross-dataset`) — what's left is the checklist below and the timed rehearsal itself.

Checklist before calling this phase done:

- Spot-check `classify_pattern()` output against real trained-model detections (not just synthetic/smoke-test boxes) before trusting `atypical_pct` in the validation panel — heuristic thresholds were tuned before the detector finished training.
- Confirm `GEMINI_API_KEY` and `MONGODB_URI` are live and exercised for the actual demo/submission — `USE_MOCK_INFERENCE` and the template/in-memory fallbacks are dev conveniences, not what should be running when judging Best Use of Gemini API / Best Use of MongoDB Atlas.
- Cite MS3SEG and MSLesSeg in the README and deck fine print (Section 5) — confirm this actually got done, not just planned.

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
├── requirements.txt              one shared Python env (no torch — inference is HTTP);
│                                 already installed into ValUnited/.venv — activate that,
│                                 don't create a second one, unless this is a fresh clone
├── .env.example                  ROBOFLOW_API_KEY, ROBOFLOW_MODEL_ID, ROBOFLOW_API_URL,
│                                 GEMINI_API_KEY, MONGODB_URI, USE_MOCK_INFERENCE
├── .gitignore                    data/raw, data/processed, .env, .venv, node_modules
│
├── data/                         ── DATA PIPELINE ──────────────────────────────────────
│   ├── README.md                 briefing: dataset download, raw/ layout, steps, gotchas
│   ├── raw/          (gitignored) NIfTI volumes as downloaded
│   ├── processed/    (gitignored) <dataset>_dataset/{train,valid,test}/*.png +
│   │                              _annotations.coco.json (COCO, Roboflow-export layout)
│   ├── pipeline/                 THE DEPLOYED PIPELINE. What's actually on Roboflow was
│   │   │                         exported through this, not scripts/ below. Run as
│   │   │                         `python -m data.pipeline.<name>` from repo root.
│   │   ├── pipeline_ms3seg.py    WORKS. normalize (min-max) → CLAHE → resize/pad 256.
│   │   │                         `preprocess_slice`/`extract_boxes`/`scale_boxes` are also
│   │   │                         imported by ml/pipeline.py (inference) and
│   │   │                         mslesseg_eval_prep.py below — never fork it.
│   │   ├── export_coco.py        WORKS, already ran — produced processed/ms3seg_dataset/
│   │   │                         {train,valid,test}. Patient-level split.
│   │   └── mslesseg_eval_prep.py WORKS. `python -m data.pipeline.mslesseg_eval_prep`.
│   │                             Raw MSLesSeg NIfTI (its train/ and test/ raw folders use
│   │                             different layouts — handles both) → COCO at
│   │                             processed/mslesseg_dataset/test/. Run once before
│   │                             `python -m ml.validate` can score against MSLesSeg.
│   └── scripts/                  UNFINISHED, NOT USED. `export_coco.py::find_cases()` here
│                                  was never implemented, so nothing has actually been
│                                  exported or uploaded through this path — don't treat it as
│                                  canonical (it isn't what ml/pipeline.py or ml/validate.py
│                                  use) until someone finishes it. Run as
│                                  `python -m data.scripts.<name>` from repo root.
│       ├── preprocess.py         normalize (percentile) → CLAHE → resize/pad 560 — NOT the
│       │                         preprocessing actually used at inference; see data/pipeline/
│       ├── masks_to_boxes.py     works standalone. connected components (8-conn) →
│       │                         [x,y,w,h]; drops <6px
│       ├── load_nifti.py         NIfTI → axial slices, canonical orientation — unused so far
│       ├── export_coco.py        TODO find_cases(). Splits by PATIENT. --val-frac 1.0 for MSLesSeg
│       └── upload_roboflow.py    TODO upload_split(). Uploads ms3seg ONLY.
│
├── ml/                           ── MODEL + HEURISTICS + VALIDATION ─────────────────────
│   ├── README.md                 briefing: Roboflow training, feature defs, rule set, demo cache
│   ├── inference.py              WORKS. httpx POST to Roboflow hosted API → RawDetection list.
│   │                             A trained model is live (ROBOFLOW_MODEL_ID set) — this is a
│   │                             real network call now, not a stub.
│   ├── heuristics.py             DONE. score_lesion() (skimage regionprops -> elongation/
│   │                             ovoid_score/orientation_deg/location) + classify_pattern()
│   │                             (the rule set below). Thresholds tunable at top of file.
│   │                             Still open: _is_radial()'s angle math is a reasoned
│   │                             approximation, not yet visually verified against real
│   │                             detections — see the Phase 7 checklist.
│   ├── burden.py                 DONE. brain_area_px() (threshold, fill holes, largest
│   │                             component) + compute_burden().
│   ├── finetune.py               Misleadingly named — this is the Roboflow UPLOAD script
│   │                             (rf.workspace("samuel-sleshi").project("ms-lesion-detection")
│   │                             .upload(...) over processed/ms3seg_dataset/{train,valid,test}),
│   │                             not local model training. Loads its OWN ml/.env (via
│   │                             python-dotenv), separate from the repo-root .env everything
│   │                             else reads — easy to miss when rotating keys.
│   ├── pipeline.py               run_pipeline(bytes) -> AnalysisResult   ← THE INTEGRATION POINT
│   │                             Preprocesses via data/pipeline/pipeline_ms3seg.py (256×256,
│   │                             min-max norm) to match what's actually deployed on Roboflow.
│   ├── validate.py               DONE. `python -m ml.validate` — scores the trained model
│   │                             against MS3SEG test + MSLesSeg via greedy IoU box matching
│   │                             (0.3), confidence-sorted. Needs ROBOFLOW_API_KEY +
│   │                             ROBOFLOW_MODEL_ID in .env; MSLesSeg needs
│   │                             data/pipeline/mslesseg_eval_prep.py run once first. Caches
│   │                             raw detections to results/detection_cache/<sha256>.json so
│   │                             re-scoring after a heuristics tune doesn't re-hit Roboflow's
│   │                             free tier (--no-cache to force a fresh run). Writes
│   │                             results/validation.json.
│   └── results/
│       ├── validation.json       REAL numbers now, not placeholders (snapshot from the last
│       │                         run — re-run after any retrain/heuristics change; served by
│       │                         GET /validation): MS3SEG held-out test, 45 scans, precision
│       │                         0.770, recall 0.728, 1.42 FP/scan, 43% flagged atypical;
│       │                         MSLesSeg (never trained on), 100 scans, precision 0.446,
│       │                         recall 0.485, 2.14 FP/scan, 65% flagged atypical.
│       └── detection_cache/      (gitignored) cached raw Roboflow predictions, see validate.py
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
│   │       └── demo_cache/            POPULATED — 3 real rehearsed scans cached (README.md
│   │                                  inside explains the convention), keyed by <sha256>.json
│   └── tests/test_analyze.py     5 smoke tests in mock mode. `pytest backend/tests`
│
└── frontend/                     ── REACT + VITE + TAILWIND ──────────────────────────── DONE
    ├── README.md  FLOW.md        pages/components briefing; FLOW.md is newer UX-flow notes
    ├── package.json  vite.config.ts (proxies /api → :8000)  tailwind.config.ts  tsconfig.json
    ├── index.html
    ├── public/
    │   ├── plate/                 hero-slice.png + README - the landing page's hero image
    │   └── samples/                clean-detection.png, pattern-contrast.png, cross-dataset.png
    │                               — the 3 rehearsed demo cases from Phase 7, viewable with no
    │                               upload needed; paired with backend's demo_cache above
    └── src/
        ├── main.tsx  App.tsx     router (`/`, `/analyze`, `/history`) + header
        ├── brand.ts              PRODUCT_NAME / DESCRIPTOR constants used in the header
        ├── samples.ts            wires public/samples/* into the "Load sample" UI
        ├── api/
        │   ├── types.ts          mirrors schemas.py
        │   └── client.ts         analyze(file), getCases(), getCase(id), getValidation()
        ├── mocks/                analysis.json (backend fixture copy) + hero.json (landing page)
        ├── components/            NOTE: original names (ScanViewer/BurdenCard) were replaced
        │   │                      by the case/ and plate/ groups below during Phase 6.
        │   ├── UploadDropzone.tsx
        │   ├── LesionTable.tsx   click row ↔ viewer selection
        │   ├── SummaryCard.tsx   Gemini text + fixed "not a diagnosis" line
        │   ├── ValidationPanel.tsx  GET /validation table
        │   ├── case/              results-display components (the old ScanViewer/BurdenCard role)
        │   │   ├── CaseView.tsx       top-level results layout for one AnalysisResult
        │   │   ├── BurdenKey.tsx      legend for the pattern-flag color coding
        │   │   ├── FindingsNote.tsx   renders the Gemini summary
        │   │   └── ValidationTable.tsx
        │   └── plate/              shared "scan on a plate" visual frame, used by Landing + Analyze
        │       ├── PlateFrame.tsx
        │       ├── PlateFigure.tsx    <img> + <svg viewBox> box overlay; orange = MS-typical, sky = atypical
        │       ├── PlateAction.tsx
        │       └── PlateIntake.tsx    upload/sample-select entry point
        └── pages/
            ├── Landing.tsx       NEW (not in the original plan) - marketing/hero page, now `/`
            ├── Analyze.tsx       upload → results layout
            └── History.tsx       saved cases from Mongo
```

### Conventions

- Run all Python from the repo root as modules (`python -m ml.validate`, `uvicorn backend.app.main:app`). Imports are absolute (`from backend.app.schemas import ...`).
- `ValUnited/.venv` already exists at the repo root, built from `requirements.txt` — activate it rather than creating a new one, unless you're on a fresh clone.
- `USE_MOCK_INFERENCE=1` (the default) makes the whole app work with no keys and no model. Every integration degrades gracefully: no Gemini key → template summary; no Mongo URI → in-memory store.
- `data/pipeline/pipeline_ms3seg.py` — not `data/scripts/preprocess.py`, which is unfinished and unused — is the preprocessing actually shared between the exported training set and inference (`ml/pipeline.py`), and also used by `data/pipeline/mslesseg_eval_prep.py`. If train and inference preprocessing drift, the model silently degrades.
- `ml/finetune.py` (the Roboflow upload script) reads its own `ml/.env`, separate from the repo-root `.env` every other script and the backend read via `backend/app/config.py`. Both are gitignored; keep `ROBOFLOW_API_KEY` in sync between them if you rotate it.
- Demo cache: `backend/app/fixtures/demo_cache/` already has 3 rehearsed scans committed (paired with `frontend/public/samples/`). Re-populate via `save_to_demo_cache()` (see `ml/README.md` step 4) if the demo cases change or the model gets retrained.
