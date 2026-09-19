"""
NIfTI volume -> 2D axial slices (+ matching mask slices).

Owner: teammate 3. See data/README.md for the expected raw/ layout.
"""

from collections.abc import Iterator
from pathlib import Path

import nibabel as nib
import numpy as np


def load_volume(path: Path) -> np.ndarray:
    """Load a .nii/.nii.gz as a float32 array in canonical (RAS) orientation."""
    img = nib.as_closest_canonical(nib.load(str(path)))
    return np.asarray(img.dataobj, dtype=np.float32)


def iter_axial_slices(
    flair: np.ndarray,
    mask: np.ndarray | None = None,
    min_mask_pixels: int = 1,
) -> Iterator[tuple[int, np.ndarray, np.ndarray | None]]:
    """
    Yield (slice_index, flair_slice, mask_slice) along the axial (last) axis.

    Skip slices where the mask has fewer than `min_mask_pixels` lesion pixels -
    empty slices add nothing for a detector and bloat the Roboflow upload. Keep
    a small % of empty slices if you want the model to learn "no lesion here"
    (set min_mask_pixels=0 and subsample in export_coco.py).

    TODO(teammate 3): confirm axis order for MS3SEG and MSLesSeg files - after
    as_closest_canonical the last axis should be superior-inferior, but check one
    volume visually before batch-exporting.
    """
    assert mask is None or mask.shape == flair.shape, "flair/mask shape mismatch"
    for z in range(flair.shape[-1]):
        f = np.rot90(flair[..., z])  # rot90 so the image is "face up" when viewed as a PNG
        m = np.rot90(mask[..., z]) if mask is not None else None
        if m is not None and (m > 0).sum() < min_mask_pixels:
            continue
        yield z, f, m
