from fastapi import APIRouter, HTTPException

from backend.app.schemas import AnalysisResult, CaseSummary
from backend.app.services import db

router = APIRouter()


@router.get("/cases", response_model=list[CaseSummary])
async def list_cases() -> list[CaseSummary]:
    return await db.list_cases()


@router.get("/cases/{case_id}", response_model=AnalysisResult)
async def get_case(case_id: str) -> AnalysisResult:
    result = await db.get_case(case_id)
    if result is None:
        raise HTTPException(404, "Case not found")
    return result
