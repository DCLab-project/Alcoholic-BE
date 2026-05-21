import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


def _parse_cors_origins(value: str | None) -> list[str]:
    if not value:
        return [
            "http://127.0.0.1:5174",
            "http://localhost:5174",
            "http://127.0.0.1:5173",
            "http://localhost:5173",
        ]

    return [origin.strip() for origin in value.split(",") if origin.strip()]


def _parse_non_negative_float(value: str | None, default: float) -> float:
    if value is None:
        return default

    try:
        parsed = float(value)
    except ValueError:
        return default

    return max(parsed, 0.0)


def _parse_positive_float(value: str | None, default: float) -> float:
    parsed = _parse_non_negative_float(value, default)
    return parsed if parsed > 0 else default


class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "Alcoholic-BE")
    app_env: str = os.getenv("APP_ENV", "local")
    app_host: str = os.getenv("APP_HOST", "127.0.0.1")
    app_port: int = int(os.getenv("APP_PORT", "8000"))
    database_url: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./alcoholic.db",
    )
    cors_origins: list[str] = _parse_cors_origins(os.getenv("CORS_ORIGINS"))
    cors_origin_regex: str = os.getenv(
        "CORS_ORIGIN_REGEX",
        r"^https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+)(:\d+)?$",
    )
    recommendation_response_delay_seconds: float = _parse_non_negative_float(
        os.getenv("RECOMMENDATION_RESPONSE_DELAY_SECONDS"),
        0.0,
    )
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
    gemini_timeout_seconds: float = _parse_positive_float(
        os.getenv("GEMINI_TIMEOUT_SECONDS"),
        12.0,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
