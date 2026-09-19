# `backend/` — FastAPI

One job: take an upload, run `ml.pipeline.run_pipeline`, add a Gemini summary, save to Mongo, return `AnalysisResult`.

```powershell
# from repo root
uvicorn backend.app.main:app --reload      # http://localhost:8000/docs
pytest backend/tests
```

## Endpoints

| Method | Path | Returns |
|---|---|---|
| `POST` | `/analyze` (multipart `file`: PNG/JPG) | `AnalysisResult` |
| `GET` | `/cases` | `CaseSummary[]` |
| `GET` | `/cases/{id}` | `AnalysisResult` |
| `GET` | `/validation` | `ValidationReport` (from `ml/results/validation.json`) |
| `GET` | `/health` | which integrations are configured |

## The contract

`app/schemas.py` is the source of truth. `frontend/src/api/types.ts` mirrors it and `app/fixtures/mock_analysis.json` is an instance of it. **Change all three in one PR.**

## Inference resolution order (`services/inference.py`)

1. `USE_MOCK_INFERENCE=1` → return `fixtures/mock_analysis.json` (frontend dev before the model exists)
2. else → `ml.pipeline.run_pipeline` (Roboflow hosted API)
3. API failed → `fixtures/demo_cache/<sha256-of-upload>.json` if present (rehearsed demo scans)
4. nothing → `503`

## Graceful degradation

- No `GEMINI_API_KEY` → template summary (still honest, still shows counts)
- No `MONGODB_URI` → in-memory case store (History works, just doesn't persist)
- No Roboflow keys → use mock mode

## Layout

```
app/
├── main.py            app + CORS + routers
├── config.py          Settings from .env; path constants
├── schemas.py         THE CONTRACT
├── routes/            analyze, cases, validation
├── services/
│   ├── inference.py   mock / pipeline / demo-cache resolution
│   ├── gemini.py      summary prompt (hard-codes the honesty rule)
│   └── db.py          motor + in-memory fallback
└── fixtures/          mock_analysis.json, demo_cache/
```
