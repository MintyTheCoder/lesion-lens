# `frontend/` — React + Vite + Tailwind

```powershell
cd frontend
npm install
npm run dev        # http://localhost:5173  (proxies /api -> http://localhost:8000)
```

Works without a model: run the backend with `USE_MOCK_INFERENCE=1` (default), or click "Load mock result" on the Analyze page to render `src/mocks/analysis.json` with no backend at all.

## Pages

- **Landing** (`/`) — the pitch backdrop: Plate 1 (sample slice + numbered lesion legend), the misdiagnosis numbers, what the pattern flag encodes, honesty line, CTA → Analyze. Drop the real sample slice at `public/plate/hero-slice.png` (see `public/plate/README.md`); a labeled slot renders until then.
- **Analyze** (`/analyze`) — upload → annotated slice + burden + lesion table + summary + validation panel
- **History** (`/history`) — saved cases from Mongo; click to reopen

## Visual system

`DESIGN.md` at the repo root records the world (MRI atlas plate: black plate, bone hairlines, Archivo across its width axis, orange = MS-typical / sky = atypical as the only chroma). Tokens live in `tailwind.config.ts`; the font is self-hosted in `public/fonts/` so the demo does not depend on Wi-Fi. Product copy that must not drift (name, honesty rule, not-a-diagnosis line) lives in `src/brand.ts`. Analyze and History have not been moved into this world yet.

## Components

| Component | Shows |
|---|---|
| `plate/PlateFigure` | The atlas plate: square hairline frame, lesion boxes in image px, numbered callouts, DOM-measured leaders into the margin legend; hover/click a legend row ↔ its box. |
| `plate/PlateAction` | The plate's one action (ruled box, fills on hover). |
| `UploadDropzone` | drag/drop or click; PNG/JPG only |
| `ScanViewer` | `<img>` + `<svg>` overlay. Boxes are drawn in image pixel coords via `viewBox`, so they scale with the image. Orange = MS-typical, sky = atypical. Hover/click → tooltip with features + reasons. |
| `LesionTable` | one row per lesion, click selects (syncs with viewer) |
| `BurdenCard` | count, % burden, typical/atypical counts |
| `SummaryCard` | Gemini text + the fixed "decision support, not a diagnosis" line |
| `ValidationPanel` | `GET /validation` table — the cross-hospital moment |

## Contract

`src/api/types.ts` mirrors `backend/app/schemas.py`. If it changes, change both + `mock_analysis.json` in one PR. `src/mocks/analysis.json` is a copy of the backend fixture — keep them identical.

## Demo polish TODOs (do last, after the model works)

- Legend for box colors
- Loading state on the viewer while Roboflow responds (a few seconds)
- Hide `ValidationPanel` until `validation.json` has real numbers
- Toggle to show only atypical lesions
