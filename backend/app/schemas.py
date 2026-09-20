"""
THE CONTRACT between ml/ (produces), backend/ (serves) and frontend/ (renders).

Any change here must land in the same PR as the matching change to
frontend/src/api/types.ts and backend/app/fixtures/mock_analysis.json.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Pattern = Literal["ms_typical", "atypical"]
Location = Literal["periventricular", "juxtacortical", "deep_wm"]


class ImageInfo(BaseModel):
    data_url: str = Field(description="Preprocessed slice as data:image/png;base64,...")
    width: int
    height: int


class LesionFeatures(BaseModel):
    elongation: float = Field(description="major_axis / minor_axis of the lesion blob; >2 is elongated")
    orientation_deg: float = Field(description="Major-axis angle in degrees, 0 = horizontal")
    location: Location
    ovoid_score: float = Field(ge=0, le=1, description="1 = perfectly ovoid/elliptical, 0 = irregular")


class Lesion(BaseModel):
    id: int
    bbox: list[int] = Field(min_length=4, max_length=4, description="[x, y, w, h] in pixels of the preprocessed image")
    confidence: float = Field(ge=0, le=1)
    area_px: int
    pattern: Pattern
    features: LesionFeatures
    reasons: list[str] = Field(description="Human-readable reasons behind the pattern flag")


class Burden(BaseModel):
    lesion_count: int
    total_area_px: int
    total_area_pct: float = Field(description="Total lesion area as % of brain area in the slice")
    ms_typical_count: int
    atypical_count: int


class ModelInfo(BaseModel):
    id: str = Field(description="Roboflow model id, e.g. workspace/project/3")
    trained_on: str = "MS3SEG"


class AnalysisResult(BaseModel):
    case_id: str
    created_at: datetime
    image: ImageInfo
    lesions: list[Lesion]
    burden: Burden
    summary: str = Field(description="Gemini plain-language summary; decision support only")
    model: ModelInfo


class CaseSummary(BaseModel):
    case_id: str
    created_at: datetime
    lesion_count: int
    atypical_count: int


class DatasetValidation(BaseModel):
    name: str
    n_scans: int
    precision: float
    recall: float
    fp_per_scan: float
    atypical_pct: float = Field(description="% of detected lesions flagged atypical — descriptive only, no ground truth")


class ValidationReport(BaseModel):
    datasets: list[DatasetValidation]
    note: str = ""


class BurdenPoint(BaseModel):
    case_id: str
    created_at: datetime
    lesion_count: int
    total_area_pct: float
    atypical_count: int


class BurdenTrend(BaseModel):
    session_id: str
    points: list[BurdenPoint]
    direction: Literal["rising", "stable", "falling", "insufficient_data"]
