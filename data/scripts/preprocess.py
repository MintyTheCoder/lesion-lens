"""
OpenCV preprocessing applied to EVERY slice - both when building the training set
and at inference time in ml/pipeline.py. If train and inference preprocessing
differ, the model silently gets worse, so this is the only place it lives.

Owner: teammate 3. This file is already functional; tune constants, don't fork it.
"""

import cv2
import numpy as np

TARGET_SIZE = 560          # RF-DETR-B input resolution (must be divisible by 56)
CLAHE_CLIP = 2.0
CLAHE_TILE = (8, 8)


def normalize_intensity(slice_2d: np.ndarray) -> np.ndarray:
    """Any dtype/range (raw NIfTI floats, 16-bit) -> uint8 0..255 using 1st-99th percentile clipping."""
    s = slice_2d.astype(np.float32)
    lo, hi = np.percentile(s, (1, 99))
    if hi <= lo:
        return np.zeros_like(s, dtype=np.uint8)
    s = np.clip((s - lo) / (hi - lo), 0, 1)
    return (s * 255).astype(np.uint8)


def apply_clahe(gray_u8: np.ndarray) -> np.ndarray:
    """Local contrast enhancement - makes small WMH lesions pop against white matter."""
    clahe = cv2.createCLAHE(clipLimit=CLAHE_CLIP, tileGridSize=CLAHE_TILE)
    return clahe.apply(gray_u8)


def resize_pad(gray_u8: np.ndarray, size: int = TARGET_SIZE) -> np.ndarray:
    """Scale longest side to `size`, pad the rest with black so aspect ratio is preserved."""
    h, w = gray_u8.shape
    scale = size / max(h, w)
    resized = cv2.resize(gray_u8, (round(w * scale), round(h * scale)), interpolation=cv2.INTER_AREA)
    out = np.zeros((size, size), dtype=np.uint8)
    rh, rw = resized.shape
    top, left = (size - rh) // 2, (size - rw) // 2
    out[top : top + rh, left : left + rw] = resized
    return out


def preprocess_slice(slice_2d: np.ndarray) -> np.ndarray:
    """Full chain: normalize -> CLAHE -> resize/pad. Returns TARGET_SIZE x TARGET_SIZE uint8."""
    return resize_pad(apply_clahe(normalize_intensity(slice_2d)))


def transform_mask(mask_2d: np.ndarray, size: int = TARGET_SIZE) -> np.ndarray:
    """
    Apply the SAME geometric transform (resize/pad only, nearest-neighbour) to a label mask
    so boxes computed from it line up with the preprocessed image.
    """
    m = (mask_2d > 0).astype(np.uint8)
    h, w = m.shape
    scale = size / max(h, w)
    resized = cv2.resize(m, (round(w * scale), round(h * scale)), interpolation=cv2.INTER_NEAREST)
    out = np.zeros((size, size), dtype=np.uint8)
    rh, rw = resized.shape
    top, left = (size - rh) // 2, (size - rw) // 2
    out[top : top + rh, left : left + rw] = resized
    return out
