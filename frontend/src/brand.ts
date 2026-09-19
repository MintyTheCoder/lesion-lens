// Product copy that must read identically everywhere. Do not paraphrase the honesty rule.

// Decided 2026-09-19 (see PRODUCT.md → Brand Commitments). This constant is the single source
// of the name in the UI; the <title> in index.html and the FastAPI title mirror it by hand.
export const PRODUCT_NAME = "LesionLens";
export const DESCRIPTOR = "Decision support for a clinician's second look";

export const HONESTY_LINE =
  "We encode established diagnostic criteria used to distinguish MS-typical lesions from nonspecific ones.";
export const NOT_A_DIAGNOSIS =
  "Decision support for clinician review — not a diagnosis. Never shown to the patient.";

export const PATTERN_LABEL = {
  ms_typical: "MS-typical pattern",
  atypical: "Atypical or nonspecific pattern",
} as const;

export const LOCATION_LABEL = {
  periventricular: "periventricular",
  juxtacortical: "juxtacortical",
  deep_wm: "deep white matter",
} as const;
