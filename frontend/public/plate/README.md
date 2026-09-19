# Hero slice

Place the landing-page sample slice here as `hero-slice.png` (PNG or JPG, preprocessed the same way
the model sees it — `python -m data.scripts.preprocess`). The landing renders a labeled slot until it exists.

The detections drawn over it come from `src/mocks/analysis.json`; swap that for the real `AnalysisResult`
of this slice (save it via the demo cache) so boxes line up with the image.
