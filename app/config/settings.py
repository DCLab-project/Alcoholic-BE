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


def _parse_positive_int(value: str | None, default: int) -> int:
    if value is None:
        return default

    try:
        parsed = int(value)
    except ValueError:
        return default

    return parsed if parsed > 0 else default


def _normalize_database_url(value: str | None) -> str:
    database_url = (value or "sqlite:///./alcoholic.db").strip()
    if not database_url:
        return "sqlite:///./alcoholic.db"

    if database_url.startswith("mysql://"):
        database_url = f"mysql+pymysql://{database_url.removeprefix('mysql://')}"

    lowered = database_url.lower()
    is_pymysql = lowered.startswith(("mysql+pymysql://", "mariadb+pymysql://"))
    has_charset = "charset=" in lowered.split("?", 1)[-1] if "?" in lowered else False
    if is_pymysql and not has_charset:
        separator = "&" if "?" in database_url else "?"
        database_url = f"{database_url}{separator}charset=utf8mb4"

    return database_url


class Settings(BaseModel):
    app_name: str
    app_env: str
    app_host: str
    app_port: int
    database_url: str
    database_pool_recycle_seconds: int
    cors_origins: list[str]
    cors_origin_regex: str
    recommendation_response_delay_seconds: float

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            app_name=os.getenv("APP_NAME", "Alcoholic-BE"),
            app_env=os.getenv("APP_ENV", "local"),
            app_host=os.getenv("APP_HOST", "127.0.0.1"),
            app_port=int(os.getenv("APP_PORT", "8000")),
            database_url=_normalize_database_url(os.getenv("DATABASE_URL")),
            database_pool_recycle_seconds=_parse_positive_int(
                os.getenv("DATABASE_POOL_RECYCLE_SECONDS"),
                1800,
            ),
            cors_origins=_parse_cors_origins(os.getenv("CORS_ORIGINS")),
            cors_origin_regex=os.getenv(
                "CORS_ORIGIN_REGEX",
                r"^https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+)(:\d+)?$",
            ),
            recommendation_response_delay_seconds=_parse_non_negative_float(
                os.getenv("RECOMMENDATION_RESPONSE_DELAY_SECONDS"),
                0.0,
            ),
        )


@lru_cache
def get_settings() -> Settings:
    return Settings.from_env()
