"""Settings loaded from .env (see .env.example). Import `settings` from here everywhere."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
DEMO_CACHE_DIR = FIXTURES_DIR / "demo_cache"
VALIDATION_PATH = REPO_ROOT / "ml" / "results" / "validation.json"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=REPO_ROOT / ".env", env_file_encoding="utf-8", extra="ignore")

    roboflow_api_key: str = ""
    roboflow_model_id: str = ""
    roboflow_api_url: str = "https://serverless.roboflow.com"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    mongodb_uri: str = ""
    mongodb_db: str = "ms_lesion"

    use_mock_inference: bool = True
    cors_origins: list[str] = ["http://localhost:5173"]


settings = Settings()
