# Frontend Flow

**Audience:** radiologists reading FLAIR MRI slices, advising hospital staff.
**Framing (every screen):** decision support for a second look — never a standalone diagnosis, never shown to the patient.

## 1. Landing page (`/`)

Minimal. Three jobs, in order:

1. **Highlight the app** — one line on what it does: boxes white-matter lesions on a FLAIR slice and flags each as MS-typical vs atypical/nonspecific.
2. **The numbers behind misdiagnosis** — why this matters:
   - ~18% of MS diagnoses are wrong (Kaisey et al.)
   - 72% of misdiagnosed patients are put on MS medication they don't need (Solomon et al. 2016)
   - ~33% stay misdiagnosed for 10+ years (Solomon et al. 2016)
   - Root cause: nonspecific white-matter lesions over-called as MS-typical. Migraine is the most common mimic, disproportionately affecting women.
3. **Go to the app** — single CTA → Analyze page.

## 2. Analyze page (`/analyze`)

| Step | What the radiologist sees | What happens |
|---|---|---|
| Upload | `UploadDropzone` — drag/drop or click, PNG/JPG FLAIR slice | `POST /analyze` |
| Processing | Loading state on the viewer (a few seconds) | Model tuned to find white-matter lesions; heuristic layer flags each lesion typical vs atypical |
| Results | `ScanViewer` annotated slice (orange = MS-typical, sky = atypical), `BurdenCard` count/area, `LesionTable` per-lesion flags | `AnalysisResult` rendered |
| Summary | `SummaryCard` — plain-language review of findings + the fixed "decision support, not a diagnosis" line | Gemini summary (template fallback without a key) |
| Validation | `ValidationPanel` — precision / FP rate, including on MSLesSeg (never trained on) | `GET /validation` |

The summary is the hand-off artifact: written so the radiologist can use it directly when advising staff or charting.

## 3. History page (`/history`)

Saved cases from Mongo; click to reopen a past result.

## Honesty rule (copy for any UI text)

✅ "We encode established diagnostic criteria used to distinguish MS-typical lesions from nonspecific ones."
❌ Never "trained to detect migraine" / "distinguishes MS from migraine."
