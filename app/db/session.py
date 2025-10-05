from __future__ import annotations

from collections.abc import Generator
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings

LOGGER = logging.getLogger("app.db.session")
LOGGER.info("Using database URL: %s", settings.database_url)

engine = create_engine(settings.database_url, poolclass=NullPool)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)


def get_db() -> Generator[Session, None, None]:
    db: Session | None = None
    try:
        db = SessionLocal()
        yield db
    except Exception as exc:  # pragma: no cover - explicit logging for connection issues
        LOGGER.exception("Database session failed")
        print(f"[DB ERROR] url={settings.database_url} error={exc}")
        raise
    finally:
        if db is not None:
            db.close()