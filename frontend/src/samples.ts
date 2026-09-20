/**
 * Rehearsed sample slices offered on the intake plate. Files live in `frontend/public/samples/`
 * (see the README there). Each is fetched and submitted through POST /analyze like any upload,
 * so a sample's bytes are stable and hit `backend/app/fixtures/demo_cache/` when the hosted
 * model is unreachable. Entries whose file is missing are hidden at runtime.
 */
export interface SampleSlice {
  file: string;
  name: string;
  description: string;
}

export const SAMPLES: SampleSlice[] = [
  {
  file: "/samples/clean-detection.png",
  name: "Clean detection",
  description: "Every lesion in this slice is periventricular and MS-typical, including a classic Dawson's finger.",
  },
  {
    file: "/samples/pattern-contrast.png",
    name: "Pattern contrast",
    description: "MS-typical and nonspecific lesions on one slice, so the flag and its reasons can be read side by side.",
  },
  {
    file: "/samples/cross-dataset.png",
    name: "Cross-dataset",
    description: "An MSLesSeg slice the model never trained on.",
  },
];
