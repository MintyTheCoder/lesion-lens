"""
Run from the repo root:
    uvicorn backend.app.main:app --reload
Docs at http://localhost:8000/docs
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.routes import analyze, cases, validation

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="MS Lesion Specificity", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(analyze.router)
app.include_router(cases.router)
app.include_router(validation.router)


@app.get("/health")
async def health() -> dict:
    return {
        "ok": True,
        "mock_inference": settings.use_mock_inference,
        "roboflow_configured": bool(settings.roboflow_api_key and settings.roboflow_model_id),
        "gemini_configured": bool(settings.gemini_api_key),
        "mongo_configured": bool(settings.mongodb_uri),
    }
