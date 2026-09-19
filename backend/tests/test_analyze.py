"""Smoke tests in mock mode. Run from repo root: pytest backend/tests"""

import base64
import io

import pytest
from fastapi.testclient import TestClient

from backend.app.config import settings
from backend.app.main import app
from backend.app.schemas import AnalysisResult

# 1x1 PNG (same bytes as the fixture's data_url)
PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
)


@pytest.fixture(autouse=True)
def mock_mode(monkeypatch):
    monkeypatch.setattr(settings, "use_mock_inference", True)
    monkeypatch.setattr(settings, "gemini_api_key", "")
    monkeypatch.setattr(settings, "mongodb_uri", "")


client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_analyze_returns_contract():
    r = client.post("/analyze", files={"file": ("slice.png", io.BytesIO(PNG), "image/png")})
    assert r.status_code == 200, r.text
    result = AnalysisResult.model_validate(r.json())
    assert result.burden.lesion_count == len(result.lesions)
    assert result.summary


def test_analyze_rejects_non_image():
    r = client.post("/analyze", files={"file": ("x.txt", io.BytesIO(b"hi"), "text/plain")})
    assert r.status_code == 415


def test_case_roundtrip():
    r = client.post("/analyze", files={"file": ("slice.png", io.BytesIO(PNG), "image/png")})
    case_id = r.json()["case_id"]
    assert client.get(f"/cases/{case_id}").status_code == 200
    assert any(c["case_id"] == case_id for c in client.get("/cases").json())


def test_validation_endpoint():
    r = client.get("/validation")
    assert r.status_code == 200
    assert len(r.json()["datasets"]) == 2
