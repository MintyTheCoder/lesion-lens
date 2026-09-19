"""
THE integration point. backend/app/services/inference.py calls exactly one thing:

    run_pipeline(image_bytes) -> AnalysisResult   (summary left empty; backend fills it via Gemini)

Owner: teammate 2. Do not change the signature without telling the app owner.
"""

import base64
import uuid
from datetime import datetime, timezone

import cv2
import numpy as np

from backend.app.config import settings
from backend.app.schemas import AnalysisResult, ImageInfo, Lesion, ModelInfo
from data.scripts.preprocess import preprocess_slice
from ml.burden import compute_burden
from ml.heuristics import classify_pattern, score_lesion
from ml.inference import detect


def decode_upload(image_bytes: bytes) -> np.ndarray:
    """
    Upload bytes -> grayscale 2D array. Handles PNG/JPG.

    TODO(teammate 2/3): if we accept .nii.gz uploads, load with nibabel and pick
    the middle axial slice.
    """
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Could not decode image - expected PNG or JPG")
    return img


def _to_data_url(gray: np.ndarray) -> str:
    ok, buf = cv2.imencode(".png", gray)
    if not ok:
        raise RuntimeError("PNG encode failed")
    return "data:image/png;base64," + base64.b64encode(buf.tobytes()).decode()


def run_pipeline(image_bytes: bytes) -> AnalysisResult:
    """preprocess -> detect (Roboflow API) -> heuristics per lesion -> burden -> AnalysisResult."""
    gray = preprocess_slice(decode_upload(image_bytes))
    rgb = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
    h, w = gray.shape

    lesions: list[Lesion] = []
    for i, det in enumerate(detect(rgb)):
        x, y, bw, bh = det.bbox
        crop = gray[max(y, 0) : y + bh, max(x, 0) : x + bw]
        feats = score_lesion(crop, det.bbox, (h, w))
        pattern, reasons = classify_pattern(feats, det.bbox, (h, w))
        lesions.append(
            Lesion(
                id=i,
                bbox=det.bbox,
                confidence=det.confidence,
                area_px=int(bw * bh),  # TODO(teammate 2): use blob area from regionprops, not box area
                pattern=pattern,
                features=feats,
                reasons=reasons,
            )
        )

    return AnalysisResult(
        case_id=str(uuid.uuid4()),
        created_at=datetime.now(timezone.utc),
        image=ImageInfo(data_url=_to_data_url(gray), width=w, height=h),
        lesions=lesions,
        burden=compute_burden(lesions, gray),
        summary="",  # filled in by backend/app/services/gemini.py
        model=ModelInfo(id=settings.roboflow_model_id, trained_on="MS3SEG"),
    )
