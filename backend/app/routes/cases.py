from fastapi import APIRouter, Header, HTTPException

from backend.app.schemas import AnalysisResult, BurdenPoint, BurdenTrend, CaseSummary
from backend.app.services import db

router = APIRouter()


def _compute_direction(points: list[BurdenPoint]) -> str:
    if len(points) < 2:
        return "insufficient_data"
    first, last = points[0].total_area_pct, points[-1].total_area_pct
    if first == 0:
        delta_pct = float("inf") if last > 0 else 0.0
    else:
        delta_pct = (last - first) / first
    if delta_pct > 0.10:
        return "rising"
    if delta_pct < -0.10:
        return "falling"
    return "stable"


@router.get("/cases", response_model=list[CaseSummary])
async def list_cases(x_session_id: str = Header(...)) -> list[CaseSummary]:
    return await db.list_cases(x_session_id)


@router.get("/cases/trend", response_model=BurdenTrend)
async def get_burden_trend(x_session_id: str = Header(...)) -> BurdenTrend:
    raw = await db.get_burden_trend(x_session_id)
    points = [BurdenPoint(**p) for p in raw]
    return BurdenTrend(session_id=x_session_id, points=points, direction=_compute_direction(points))


@router.get("/cases/{case_id}", response_model=AnalysisResult)
async def get_case(case_id: str) -> AnalysisResult:
    result = await db.get_case(case_id)
    if result is None:
        raise HTTPException(404, "Case not found")
    return result
