# Sample slices

Rehearsed slices offered on the Analyze intake plate. The manifest is `src/samples.ts`; a sample
whose file is missing is hidden at runtime, and when none exist the list is replaced by a one-line note.

Expected files (PNG or JPG, preprocessed the same way the model sees it — `python -m data.scripts.preprocess`):

- `clean-detection.png` — every lesion MS-typical
- `pattern-contrast.png` — MS-typical and nonspecific lesions on one slice
- `cross-dataset.png` — an MSLesSeg slice, never trained on

Before judging, run each through `save_to_demo_cache()` (see `ml/README.md` step 4) so the sample's
exact bytes resolve from `backend/app/fixtures/demo_cache/` if Wi-Fi drops.
