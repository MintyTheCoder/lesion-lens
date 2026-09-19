"""
Binary lesion mask -> one bounding box per connected blob.

Owner: teammate 3.
"""

import numpy as np
from scipy import ndimage

MIN_BLOB_PIXELS = 6      # drop specks smaller than this (annotation noise / partial volume)
MIN_BOX_SIDE = 4         # pad tiny boxes up to this many px so the detector has something to look at


def mask_to_boxes(mask_2d: np.ndarray, min_pixels: int = MIN_BLOB_PIXELS) -> list[list[int]]:
    """
    Returns [[x, y, w, h], ...] in pixel coords (top-left origin) for each
    connected component of the mask with >= min_pixels pixels.

    Uses 8-connectivity so diagonally-touching pixels count as one lesion.
    """
    labeled, n = ndimage.label(mask_2d > 0, structure=np.ones((3, 3)))
    boxes: list[list[int]] = []
    for sl in ndimage.find_objects(labeled):
        if sl is None:
            continue
        ys, xs = sl
        blob = labeled[ys, xs]
        if (blob > 0).sum() < min_pixels:
            continue
        x, y = xs.start, ys.start
        w, h = xs.stop - xs.start, ys.stop - ys.start
        # pad tiny boxes symmetrically
        if w < MIN_BOX_SIDE:
            x -= (MIN_BOX_SIDE - w) // 2
            w = MIN_BOX_SIDE
        if h < MIN_BOX_SIDE:
            y -= (MIN_BOX_SIDE - h) // 2
            h = MIN_BOX_SIDE
        boxes.append([max(int(x), 0), max(int(y), 0), int(w), int(h)])
    return boxes
