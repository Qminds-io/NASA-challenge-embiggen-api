from __future__ import annotations

import logging
from pathlib import Path

from alembic import command
from alembic.config import Config

from app.core.config import settings

LOGGER = logging.getLogger(__name__)


def _alembic_config() -> Config:
    project_root = Path(__file__).resolve().parents[2]
    cfg = Config(str(project_root / "alembic.ini"))
    cfg.set_main_option("script_location", str(project_root / "alembic"))
    cfg.set_main_option("sqlalchemy.url", settings.database_url)
    return cfg


def run_migrations() -> None:
    """Apply the latest Alembic migrations."""

    LOGGER.info("Running database migrations...")
    try:
        command.upgrade(_alembic_config(), "head")
    except Exception as exc:  # pragma: no cover - defensive logging for production runtime
        LOGGER.exception("Alembic upgrade failed", exc_info=exc)
        raise
    LOGGER.info("Database migrations completed.")