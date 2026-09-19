// Product copy that must read identically everywhere. Do not paraphrase the honesty rule.

// UNDECIDED (see PRODUCT.md → Brand Commitments): "Val United" vs "MS Lesion Specificity".
// The header currently ships the descriptive name; flip this one constant when the team decides.
export const PRODUCT_NAME = "MS Lesion Specificity";
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
