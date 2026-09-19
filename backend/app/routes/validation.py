from fastapi import APIRouter

from backend.app.config import VALIDATION_PATH
from backend.app.schemas import ValidationReport

router = APIRouter()


@router.get("/validation", response_model=ValidationReport)
async def get_validation() -> ValidationReport:
    """Serves ml/results/validation.json, written by `python -m ml.validate`."""
    return ValidationReport.model_validate_json(VALIDATION_PATH.read_text())
