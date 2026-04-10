import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "Alcoholic-BE")
    app_env: str = os.getenv("APP_ENV", "local")
    app_host: str = os.getenv("APP_HOST", "127.0.0.1")
    app_port: int = int(os.getenv("APP_PORT", "8000"))
    database_url: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./alcoholic.db",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
