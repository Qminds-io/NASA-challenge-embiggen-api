from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_SQLITE_URL = "sqlite:///./data/app.db"


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        env_prefix="APP_",
        extra="ignore",
    )

    app_name: str = "demo-service"
    version: str = "0.1.0"
    environment: str = "local"

    raw_database_url: Optional[str] = Field(default=None, alias="database_url")
    db_user: Optional[str] = Field(default=None, alias="db_user")
    db_password: Optional[str] = Field(default=None, alias="db_password")
    db_host: Optional[str] = Field(default=None, alias="db_host")
    db_port: Optional[int] = Field(default=None, alias="db_port")
    db_name: Optional[str] = Field(default=None, alias="db_name")
    db_driver: str = Field(default="postgresql+psycopg", alias="db_driver")

    database_echo: bool = Field(default=False, alias="database_echo")
    allowed_origins: List[str] = Field(default_factory=lambda: ["https://embiggen.example.com"])

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

    @property
    def database_url(self) -> str:
        if self.raw_database_url:
            return self.raw_database_url
        if self.db_user and self.db_password and self.db_host and self.db_name:
            port = self.db_port or 5432
            return (
                f"{self.db_driver}://{self.db_user}:{self.db_password}@"
                f"{self.db_host}:{port}/{self.db_name}"
            )
        return DEFAULT_SQLITE_URL

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
