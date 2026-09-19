"""
Heuristic pattern layer: per-lesion geometric features -> "ms_typical" / "atypical".

This is NOT a trained classifier. It encodes established radiological criteria
(lesion morphology and location from the McDonald criteria) applied to detector
output. There is no migraine-patient data anywhere in our training set — say
this in Q&A exactly as PLAN.md section 4 phrases it.

Owner: teammate 2. See ml/README.md for the feature definitions and how to tune.
"""

from math import degrees

import cv2
import numpy as np
from skimage import measure

from backend.app.schemas import LesionFeatures, Location, Pattern

# --- Tunable thresholds. Start here, then adjust by eye on real detections. ---
ELONGATION_MS_TYPICAL = 1.8      # major/minor axis ratio above which a lesion counts as "elongated"
OVOID_MS_TYPICAL = 0.6           # solidity above which a lesion counts as "ovoid"
PERIVENTRICULAR_FRAC = 0.22      # normalized distance from image center inside which = periventricular
JUXTACORTICAL_FRAC = 0.80        # normalized distance beyond which = juxtacortical (near the cortex)
PERPENDICULAR_TOL_DEG = 30       # tolerance for "lesion axis points radially away from the ventricles"


def _largest_component_props(crop: np.ndarray):
    if crop is None or crop.size == 0:
        return None
    _, binary = cv2.threshold(crop, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    labeled = measure.label(binary > 0)
    props = measure.regionprops(labeled)
    if not props:
        return None
    return max(props, key=lambda p: p.area)


def score_lesion(crop: np.ndarray, bbox: list[int], image_shape: tuple[int, int]) -> LesionFeatures:
    """
    Compute geometric features for one detected lesion.

    1. Threshold `crop` (Otsu) -> binary blob; keep the largest connected component.
    2. skimage.measure.regionprops -> major_axis_length, minor_axis_length,
       orientation, solidity.
    3. elongation  = major / max(minor, 1)
    4. ovoid_score = solidity
    5. location    = _location_from_bbox(...) — ventricles sit near the center of an
       axial FLAIR slice, so radial distance is our proxy; say so in README.
    6. orientation_deg = degrees(regionprops.orientation), converted from skimage's
       from-vertical convention to LesionFeatures' documented from-horizontal one
       (0 = horizontal) — see _is_radial for the follow-up on verifying this by eye.
    """
    props = _largest_component_props(crop)

    if props is None:
        # degenerate crop (e.g. empty or single-pixel) - fall back to bbox aspect ratio
        w, h = bbox[2], bbox[3]
        major, minor = float(max(w, h, 1)), float(max(min(w, h), 1))
        orientation_from_horizontal = 0.0
        solidity = 1.0
    else:
        major = float(props.axis_major_length) or 1.0
        minor = float(props.axis_minor_length) or 1.0
        # skimage orientation is measured from the vertical (row) axis, 0 = vertical;
        # LesionFeatures.orientation_deg is documented as 0 = horizontal, so convert
        # here rather than storing skimage's raw convention under a mismatched name.
        orientation_from_horizontal = 90.0 - degrees(props.orientation)
        solidity = float(props.solidity)

    elongation = major / max(minor, 1.0)
    location = _location_from_bbox(bbox, image_shape)

    return LesionFeatures(
        elongation=round(elongation, 3),
        ovoid_score=round(solidity, 3),
        orientation_deg=round(orientation_from_horizontal, 1),
        location=location,
    )


def _is_radial(bbox: list[int], image_shape: tuple[int, int], orientation_deg: float) -> bool:
    """
    True if the lesion's major axis roughly points toward/away from image center
    (proxy for the ventricles) - i.e. a Dawson's finger. `orientation_deg` follows
    LesionFeatures' convention (0 = horizontal, already converted from skimage's
    from-vertical convention in score_lesion).

    FOLLOW-UP: this angle-convention math is a reasoned approximation, not yet
    visually verified against real detections. Sanity-check it by eye once the
    model produces real boxes before trusting the "Dawson's finger" reason text.
    """
    h, w = image_shape
    cx, cy = bbox[0] + bbox[2] / 2, bbox[1] + bbox[3] / 2
    radial_deg = degrees(np.arctan2(h / 2 - cy, w / 2 - cx))

    diff = abs((radial_deg - orientation_deg + 90) % 180 - 90)  # smallest angle between two undirected lines
    return diff <= PERPENDICULAR_TOL_DEG


def classify_pattern(features: LesionFeatures, bbox: list[int], image_shape: tuple[int, int]) -> tuple[Pattern, list[str]]:
    """
    Rule-based flag. Returns (pattern, reasons).

      - periventricular AND elongated AND axis roughly radial from image center  -> ms_typical ("Dawson's finger")
      - juxtacortical AND ovoid                                                  -> ms_typical
      - periventricular AND ovoid                                                -> ms_typical
      - otherwise (deep WM, punctate/round, no ventricular orientation)          -> atypical

    `reasons` are short human phrases; the frontend shows them on hover and
    Gemini uses them to write the summary.
    """
    location = features.location
    elongated = features.elongation >= ELONGATION_MS_TYPICAL
    ovoid = features.ovoid_score >= OVOID_MS_TYPICAL
    radial = _is_radial(bbox, image_shape, features.orientation_deg)

    reasons: list[str] = []

    if location == "periventricular" and elongated and radial:
        reasons.append("elongated, periventricular, oriented radially from the ventricles (Dawson's finger)")
        return "ms_typical", reasons

    if location == "juxtacortical" and ovoid:
        reasons.append("ovoid lesion abutting the cortex")
        return "ms_typical", reasons

    if location == "periventricular" and ovoid:
        reasons.append("ovoid periventricular lesion")
        return "ms_typical", reasons

    if location == "deep_wm":
        reasons.append("deep white matter, no periventricular or juxtacortical pattern")
    elif not elongated:
        reasons.append("round/punctate rather than elongated")
    if not radial:
        reasons.append("not radially oriented toward the ventricles")

    return "atypical", reasons


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
