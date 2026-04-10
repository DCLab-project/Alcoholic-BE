from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config.settings import get_settings

settings = get_settings()
is_sqlite = settings.database_url.startswith("sqlite")


class Base(DeclarativeBase):
    pass


engine = create_engine(
    settings.database_url,
    future=True,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if is_sqlite else {},
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)
