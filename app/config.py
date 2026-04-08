"""Application settings, fully env-driven.

Kept dialect-agnostic so we can swap SQLite -> PostgreSQL without touching
the rest of the code (see `DATABASE_URL`).
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_env: str = Field(default="dev")
    app_secret_key: str = Field(default="dev-secret-change-me")
    app_base_url: str = Field(default="http://localhost:8000")

    app_host: str = Field(default="127.0.0.1")
    app_port: int = Field(default=8000)

    # SQLAlchemy URL. Default = SQLite file under ./var/
    database_url: str = Field(default=f"sqlite:///{BASE_DIR / 'var' / 'workout.db'}")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    # Ensure SQLite parent dir exists
    if settings.is_sqlite:
        # sqlite:///./var/workout.db -> ./var/workout.db
        raw = settings.database_url.replace("sqlite:///", "", 1)
        db_path = Path(raw)
        if not db_path.is_absolute():
            db_path = BASE_DIR / db_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
    return settings
