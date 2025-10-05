from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_DB_DRIVER = "postgresql+psycopg"
DEFAULT_DB_USER = "nasa"
DEFAULT_DB_PASSWORD = "nasa"
DEFAULT_DB_HOST = "db"
DEFAULT_DB_PORT = 5432
DEFAULT_DB_NAME = "nasa"


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        env_prefix="APP_",
        extra="ignore",
    )

    app_name: str = "nasa-service"
    version: str = "0.1.0"
    environment: str = "local"

    raw_database_url: Optional[str] = Field(default=None, alias="database_url")
    db_user: str = Field(default=DEFAULT_DB_USER, alias="db_user")
    db_password: str = Field(default=DEFAULT_DB_PASSWORD, alias="db_password")
    db_host: str = Field(default=DEFAULT_DB_HOST, alias="db_host")
    db_port: int = Field(default=DEFAULT_DB_PORT, alias="db_port")
    db_name: str = Field(default=DEFAULT_DB_NAME, alias="db_name")
    db_driver: str = Field(default=DEFAULT_DB_DRIVER, alias="db_driver")

    database_echo: bool = Field(default=False, alias="database_echo")
    allowed_origins: List[str] = Field(default_factory=lambda: ["https://nasa.qminds.io","https://api.nasa.qminds.io", "http://localhost:5173", "http://localhost:8001"])

    nasa_gibs_base_url: AnyUrl = Field(
        default="https://gibs.earthdata.nasa.gov/wmts/epsg3857/best",
        description="Base URL for NASA GIBS WMTS REST endpoint.",
    )
    nasa_treks_base_url: AnyUrl = Field(
        default="https://trek.nasa.gov/tiles",
        description="Base URL for NASA Solar System Treks WMTS REST endpoint.",
    )
    tile_cache_dir: Path = Field(
        default=Path(".cache/tiles"),
        description="Filesystem directory used to persist proxied tile responses.",
    )
    tile_cache_ttl_seconds: int = Field(
        default=3600,
        ge=0,
        description="Cache TTL for NASA tile responses in seconds.",
    )
    http_timeout_seconds: float = Field(
        default=10.0,
        ge=0.1,
        description="Timeout for outbound HTTP requests to NASA services.",
    )
    annotation_delete_secret: str = Field(default="qminds", alias="annotation_delete_secret")

    @property
    def database_url(self) -> str:
        if self.raw_database_url:
            return self.raw_database_url
        return (
            f"{self.db_driver}://{self.db_user}:{self.db_password}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def is_local(self) -> bool:
        return self.environment.lower() == "local"


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance to avoid recomputing."""

    settings = Settings()
    settings.tile_cache_dir.mkdir(parents=True, exist_ok=True)
    return settings


settings = get_settings()
