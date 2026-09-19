"""
Resolution order for POST /analyze:

  1. USE_MOCK_INFERENCE=1      -> fixtures/mock_analysis.json      (frontend dev, no model yet)
  2. Roboflow hosted API       -> ml.pipeline.run_pipeline
  3. API failed (no Wi-Fi etc) -> fixtures/demo_cache/<sha256>.json (rehearsed demo scans only)
  4. nothing cached            -> InferenceUnavailable -> 503
"""

import base64
import hashlib
import json
import logging
import uuid
from datetime import datetime, timezone

from backend.app.config import DEMO_CACHE_DIR, FIXTURES_DIR, settings
from backend.app.schemas import AnalysisResult

log = logging.getLogger(__name__)


PNG_MAGIC = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])


class InferenceUnavailable(Exception):
    pass


def _fresh_ids(result: AnalysisResult) -> AnalysisResult:
    """Cached/mock results get a new case_id + timestamp so History shows distinct entries."""
    return result.model_copy(update={"case_id": str(uuid.uuid4()), "created_at": datetime.now(timezone.utc)})


def _load_mock(image_bytes: bytes | None = None) -> AnalysisResult:
    result = _fresh_ids(AnalysisResult.model_validate_json((FIXTURES_DIR / "mock_analysis.json").read_text()))
    if image_bytes:
        # Echo the upload back as the plate so the UI shows the clinician's own slice under the
        # fixture's boxes (which are in the fixture's 256x256 space) instead of a 1x1 placeholder.
        mime = "image/png" if image_bytes.startswith(PNG_MAGIC) else "image/jpeg"
        data_url = f"data:{mime};base64,{base64.b64encode(image_bytes).decode('ascii')}"
        result = result.model_copy(update={"image": result.image.model_copy(update={"data_url": data_url})})
    return result


def _load_demo_cache(image_bytes: bytes) -> AnalysisResult | None:
    path = DEMO_CACHE_DIR / f"{hashlib.sha256(image_bytes).hexdigest()}.json"
    if not path.exists():
        return None
    return _fresh_ids(AnalysisResult.model_validate_json(path.read_text()))


def save_to_demo_cache(image_bytes: bytes, result: AnalysisResult) -> None:
    """Call this (e.g. from a script) for each rehearsed demo scan before judging."""
    DEMO_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = DEMO_CACHE_DIR / f"{hashlib.sha256(image_bytes).hexdigest()}.json"
    path.write_text(json.dumps(result.model_dump(mode="json"), indent=2))


def analyze_image(image_bytes: bytes) -> AnalysisResult:
    if settings.use_mock_inference:
        return _load_mock(image_bytes)

    try:
        from ml.pipeline import run_pipeline  # imported lazily so mock mode needs no ml deps

        return run_pipeline(image_bytes)
    except Exception as exc:  # noqa: BLE001 - any failure falls through to the cache
        log.warning("Roboflow inference failed (%s); trying demo cache", exc)
        cached = _load_demo_cache(image_bytes)
        if cached is not None:
            return cached
        raise InferenceUnavailable(f"Inference failed and no cached result for this image: {exc}") from exc
