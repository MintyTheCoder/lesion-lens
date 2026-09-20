"""
Lesion burden: count + area. A real clinical monitoring metric (tracked over time).

Owner: teammate 2.
"""

import numpy as np
from scipy import ndimage
from skimage import measure

from backend.app.schemas import Burden, Lesion


def brain_area_px(image: np.ndarray) -> int:
    """
    Number of pixels inside the brain (not background). Denominator for
    total_area_pct so the % is comparable across slices.

    Threshold the preprocessed grayscale slice at a low value (> 10), fill
    holes so ventricles/CSF don't get excluded, keep only the largest
    connected component (drops any small non-brain noise blobs), count pixels.
    """
    binary = image > 10
    filled = ndimage.binary_fill_holes(binary)
    labeled = measure.label(filled)
    props = measure.regionprops(labeled)
    if not props:
        return 0
    largest = max(props, key=lambda p: p.area)
    return int(largest.area)


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