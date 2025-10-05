from __future__ import annotations

from collections.abc import Generator
from pathlib import Path
import logging

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url, URL
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

LOGGER = logging.getLogger("app.db.session")


def _mask_url(url: URL) -> URL:
    if url.password:
        return url.set(password="***")
    return url


url = make_url(settings.database_url)
connect_args: dict[str, object] = {}

if url.drivername.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    if url.database:
        db_path = Path(url.database)
        if not db_path.is_absolute():
            db_path = Path.cwd() / db_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
else:
    if settings.db_sslmode:
        connect_args["sslmode"] = settings.db_sslmode

LOGGER.info(
    "Creating SQLAlchemy engine",
    extra={
        "driver": url.drivername,
        "db_url": str(_mask_url(url)),
        "connect_args": connect_args,
    },
)

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=settings.database_echo,
    future=True,
    connect_args=connect_args,
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)



def get_db() -> Generator[Session, None, None]:
    """Yield a database session for dependency injection."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

