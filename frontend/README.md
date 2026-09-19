# `frontend/` — React + Vite + Tailwind

```powershell
cd frontend
npm install
npm run dev        # http://localhost:5173  (proxies /api -> http://localhost:8000)
```

Works without a model: run the backend with `USE_MOCK_INFERENCE=1` (default); mock mode echoes the uploaded slice back under the fixture's boxes. With no backend at all, the Analyze error state offers "Load development fixture" (dev builds only) to render `src/mocks/analysis.json`.

## Pages

- **Landing** (`/`) — the pitch backdrop: Plate 1 (sample slice + numbered lesion legend), the misdiagnosis numbers, what the pattern flag encodes, honesty line, CTA → Analyze. Drop the real sample slice at `public/plate/hero-slice.png` (see `public/plate/README.md`); a labeled slot renders until then.
- **Analyze** (`/analyze`) — one plate, four states: intake (empty frame is the drop target + rehearsed sample slices from `public/samples/`) → processing (slice in the frame, elapsed counter) → result (`CaseView`: plate + burden key + legend, findings note with Copy, cross-dataset validation) → error (slice stays in frame, problem named in the margin, Try again / Choose another).
- **History** (`/history`) — saved cases from Mongo; click to reopen

## Visual system

`DESIGN.md` at the repo root records the world (MRI atlas plate: black plate, bone hairlines, Archivo across its width axis, orange = MS-typical / sky = atypical as the only chroma). Tokens live in `tailwind.config.ts`; the font is self-hosted in `public/fonts/` so the demo does not depend on Wi-Fi. Product copy that must not drift (name, honesty rule, not-a-diagnosis line) lives in `src/brand.ts`. History has not been moved into this world yet.

## Components

| Component | Shows |
|---|---|
| `plate/PlateFigure` | The atlas plate: square hairline frame, lesion boxes in image px, numbered callouts, DOM-measured leaders into the margin legend; hover/click a legend row ↔ its box. |
| `plate/PlateAction` | The plate's one action (ruled box, fills on hover). `to` renders a link, `onClick` a button. |
| `plate/PlateFrame` | Shared frame furniture: `FRAME_CLASS`, `PLATE_GRID`, corner ticks + orientation letters, `PlateCaption`. |
| `plate/PlateIntake` | The empty frame as the drop target; brightens on drag-over/focus, holds the slice preview while processing. |
| `case/CaseView` | A finished plate: `PlateFigure` + `BurdenKey` + `FindingsNote` + `ValidationTable`. Reuse for reopened cases. |
| `case/BurdenKey` | count, % burden, typical/atypical counts as the plate's key (figure-scale numerals). |
| `case/FindingsNote` | the summary as a note + "Copy note" + the fixed "decision support, not a diagnosis" line |
| `case/ValidationTable` | `GET /validation` table — the cross-hospital moment. Shows a labelled "pending" row while `n_scans` is 0. |
| `ScanViewer` `LesionTable` `BurdenCard` `SummaryCard` `ValidationPanel` `UploadDropzone` | pre-world components; only History still uses `ScanViewer`/`BurdenCard`. Retire when History moves. |

## Contract

`src/api/types.ts` mirrors `backend/app/schemas.py`. If it changes, change both + `mock_analysis.json` in one PR. `src/mocks/analysis.json` is a copy of the backend fixture — keep them identical.

## Demo polish TODOs (do last, after the model works)

- Move History into the plate world (`/history` ruled list, `/history/:id` → `CaseView`)
- Place the three rehearsed slices in `public/samples/` and cache them via `save_to_demo_cache()`
- Toggle to show only atypical lesions
