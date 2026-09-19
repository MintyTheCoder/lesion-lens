"""
Heuristic pattern layer: per-lesion geometric features -> "ms_typical" / "atypical".

This is NOT a trained classifier. It encodes established radiological criteria
(lesion morphology and location from the McDonald criteria) applied to detector
output. There is no migraine-patient data anywhere in our training set — say
this in Q&A exactly as PLAN.md section 4 phrases it.

Owner: teammate 2. See ml/README.md for the feature definitions and how to tune.
"""

import numpy as np

from backend.app.schemas import LesionFeatures, Location, Pattern

# --- Tunable thresholds. Start here, then adjust by eye on real detections. ---
ELONGATION_MS_TYPICAL = 1.8      # major/minor axis ratio above which a lesion counts as "elongated"
OVOID_MS_TYPICAL = 0.6           # solidity above which a lesion counts as "ovoid"
PERIVENTRICULAR_FRAC = 0.22      # normalized distance from image center inside which = periventricular
JUXTACORTICAL_FRAC = 0.80        # normalized distance beyond which = juxtacortical (near the cortex)
PERPENDICULAR_TOL_DEG = 30       # tolerance for "lesion axis points radially away from the ventricles"


def score_lesion(crop: np.ndarray, bbox: list[int], image_shape: tuple[int, int]) -> LesionFeatures:
    """
    Compute geometric features for one detected lesion.

    Args:
        crop:        grayscale crop of the preprocessed slice inside `bbox` (H x W, uint8)
        bbox:        [x, y, w, h] in full-image pixels
        image_shape: (H, W) of the full preprocessed slice

    Suggested implementation:
      1. Threshold `crop` (Otsu) -> binary blob; keep the largest connected component.
      2. skimage.measure.regionprops -> major_axis_length, minor_axis_length,
         orientation, solidity.
      3. elongation      = major / max(minor, 1)
      4. ovoid_score     = solidity  (document whichever you pick)
      5. location        = _location_from_bbox(...)  — ventricles sit near the center of an
                           axial FLAIR slice, so radial distance is our proxy; say so in README.
      6. orientation_deg = degrees(regionprops.orientation), 0 = horizontal.

    TODO(teammate 2): implement.
    """
    raise NotImplementedError


def classify_pattern(features: LesionFeatures, bbox: list[int], image_shape: tuple[int, int]) -> tuple[Pattern, list[str]]:
    """
    Rule-based flag. Returns (pattern, reasons).

    Starting rule set (tune the constants above, not the structure):
      - periventricular AND elongated AND axis roughly radial from image center  -> ms_typical ("Dawson's finger")
      - juxtacortical AND ovoid                                                  -> ms_typical
      - periventricular AND ovoid                                                -> ms_typical
      - otherwise (deep WM, punctate/round, no ventricular orientation)          -> atypical

    `reasons` are short human phrases; the frontend shows them on hover and
    Gemini uses them to write the summary.

    TODO(teammate 2): implement.
    """
    raise NotImplementedError


def _location_from_bbox(bbox: list[int], image_shape: tuple[int, int]) -> Location:
    """Normalized radial distance of the box center from image center -> Location bucket."""
    h, w = image_shape
    cx, cy = bbox[0] + bbox[2] / 2, bbox[1] + bbox[3] / 2
    r = float(np.hypot((cx - w / 2) / (w / 2), (cy - h / 2) / (h / 2)))
    if r < PERIVENTRICULAR_FRAC:
        return "periventricular"
    if r > JUXTACORTICAL_FRAC:
        return "juxtacortical"
    return "deep_wm"
