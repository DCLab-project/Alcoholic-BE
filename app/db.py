from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config.settings import Settings
from app.config.settings import get_settings

settings = get_settings()


class Base(DeclarativeBase):
    pass


def is_sqlite_url(database_url: str) -> bool:
    return database_url.startswith("sqlite")


def build_engine_options(app_settings: Settings) -> dict:
    options: dict = {
        "future": True,
        "pool_pre_ping": True,
        "connect_args": {},
    }

    if is_sqlite_url(app_settings.database_url):
        options["connect_args"] = {"check_same_thread": False}
    else:
        options["pool_recycle"] = app_settings.database_pool_recycle_seconds

    return options


engine = create_engine(settings.database_url, **build_engine_options(settings))

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)
