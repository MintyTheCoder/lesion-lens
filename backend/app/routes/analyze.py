from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.app.schemas import AnalysisResult
from backend.app.services import db, gemini
from backend.app.services.inference import InferenceUnavailable, analyze_image

router = APIRouter()

ALLOWED = {"image/png", "image/jpeg"}


@router.post("/analyze", response_model=AnalysisResult)
async def analyze(file: UploadFile = File(...)) -> AnalysisResult:
    if file.content_type not in ALLOWED:
        raise HTTPException(415, f"Upload a PNG or JPG FLAIR slice (got {file.content_type})")
    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(400, "Empty file")

    try:
        result = analyze_image(image_bytes)
    except InferenceUnavailable as exc:
        raise HTTPException(503, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc

    if not result.summary:
        result.summary = gemini.summarize(result)
    await db.save_case(result)
    return result
