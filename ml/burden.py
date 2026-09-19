"""
Lesion burden: count + area. A real clinical monitoring metric (tracked over time).

Owner: teammate 2.
"""

import numpy as np

from backend.app.schemas import Burden, Lesion


def brain_area_px(image: np.ndarray) -> int:
    """
    Number of pixels inside the brain (not background). Denominator for
    total_area_pct so the % is comparable across slices.

    Suggested: threshold the preprocessed grayscale slice at a low value (e.g. > 10),
    scipy.ndimage.binary_fill_holes, keep the largest component, count pixels.

    TODO(teammate 2): implement.
    """
    raise NotImplementedError


def compute_burden(lesions: list[Lesion], image: np.ndarray) -> Burden:
    """Aggregate per-lesion output into the scan-level burden score."""
    total = sum(lesion.area_px for lesion in lesions)
    brain = max(brain_area_px(image), 1)
    return Burden(
        lesion_count=len(lesions),
        total_area_px=total,
        total_area_pct=round(100 * total / brain, 2),
        ms_typical_count=sum(lesion.pattern == "ms_typical" for lesion in lesions),
        atypical_count=sum(lesion.pattern == "atypical" for lesion in lesions),
    )
