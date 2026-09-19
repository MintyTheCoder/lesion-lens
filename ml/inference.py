"""
Roboflow hosted inference. Weights cannot be downloaded on the free plan, so
every detection is one HTTP POST to the serverless endpoint:

    POST {ROBOFLOW_API_URL}/{ROBOFLOW_MODEL_ID}?api_key=...&confidence=40
    body: base64-encoded image, content-type application/x-www-form-urlencoded
    -> {"predictions": [{"x", "y", "width", "height", "confidence", "class"}, ...], "image": {...}}

We call it directly with httpx instead of `inference-sdk` (which doesn't support
Python 3.13). Same endpoint, same JSON.

Owner: teammate 2. See ml/README.md.
"""

import base64
from dataclasses import dataclass

import cv2
import httpx
import numpy as np

from backend.app.config import settings

TIMEOUT_S = 30.0
RETRIES = 2


@dataclass
class RawDetection:
    """One box from Roboflow, converted to top-left [x, y, w, h] pixels."""

    bbox: list[int]
    confidence: float


def _encode(image: np.ndarray) -> str:
    ok, buf = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 95])
    if not ok:
        raise RuntimeError("JPEG encode failed")
    return base64.b64encode(buf.tobytes()).decode()


def detect(image: np.ndarray, confidence_threshold: float = 0.4) -> list[RawDetection]:
    """
    Run the fine-tuned RF-DETR-B on one preprocessed slice (H x W x 3, uint8).

    Roboflow returns boxes as center (x, y) + (width, height). Convert to
    top-left [x, y, w, h] ints so the frontend can draw them directly.

    Raises httpx.HTTPError on network/API failure - the backend catches this and
    falls back to the demo cache.

    TODO(teammate 2): tune confidence_threshold on real output; check whether the
    trained model's deploy URL is serverless.roboflow.com or detect.roboflow.com
    and set ROBOFLOW_API_URL accordingly.
    """
    if not settings.roboflow_api_key or not settings.roboflow_model_id:
        raise RuntimeError("ROBOFLOW_API_KEY / ROBOFLOW_MODEL_ID not set in .env")

    url = f"{settings.roboflow_api_url.rstrip('/')}/{settings.roboflow_model_id}"
    params = {"api_key": settings.roboflow_api_key, "confidence": int(confidence_threshold * 100)}
    body = _encode(image)

    last_exc: Exception | None = None
    for _ in range(RETRIES + 1):
        try:
            resp = httpx.post(
                url,
                params=params,
                content=body,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=TIMEOUT_S,
            )
            resp.raise_for_status()
            result = resp.json()
            break
        except httpx.HTTPError as exc:
            last_exc = exc
    else:
        raise last_exc  # type: ignore[misc]

    dets: list[RawDetection] = []
    for p in result.get("predictions", []):
        if p["confidence"] < confidence_threshold:
            continue
        x = int(p["x"] - p["width"] / 2)
        y = int(p["y"] - p["height"] / 2)
        dets.append(RawDetection(bbox=[x, y, int(p["width"]), int(p["height"])], confidence=float(p["confidence"])))
    return dets
