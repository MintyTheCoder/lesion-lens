# Hero slice

`hero-slice.png` is the landing-page sample: a 256×256 axial FLAIR slice, preprocessed the way the
deployed model sees it (`python -m data.pipeline.pipeline_ms3seg`, min-max → CLAHE → resize/pad 256).

The boxes drawn over it come from `src/mocks/analysis.json` (identical to
`backend/app/fixtures/mock_analysis.json`). They were placed by hand on this slice's visible
hyperintensities — three periventricular lesions and one small deep-white-matter focus — with
features measured from the pixels and reasons phrased exactly as `ml/heuristics.py` emits them.
They are **not model output** and the plate caption says so.

Once the hosted model runs on this slice, save its real `AnalysisResult` via `save_to_demo_cache()`
and copy it into both fixtures so the caption can drop the disclaimer.

`test_boxes.png` is a reference only (a different, skull-stripped slice with ground-truth boxes);
nothing in the app loads it.
