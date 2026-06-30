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

# Default timezone for rendering session dates and weekday labels.
# Storage remains UTC; only the display layer converts.
# V2 may introduce per-user timezone preference.
DEFAULT_TIMEZONE = "Europe/Paris"


class Settings(BaseSettings):
    app_env: str = Field(default="dev")
    app_secret_key: str = Field(default="dev-secret-change-me")
    app_base_url: str = Field(default="http://localhost:8000")

    app_host: str = Field(default="127.0.0.1")
    app_port: int = Field(default=8000)

    # SQLAlchemy URL. Default = SQLite file under ./var/
    database_url: str = Field(default=f"sqlite:///{BASE_DIR / 'var' / 'workout.db'}")

    # Where the nightly backup script writes JSON / CSV dumps. Used by
    # both `scripts/backup_sessions.py` and the /export landing page
    # (which displays the latest local backup file as a sanity signal).
    backup_dir: str = Field(default=str(BASE_DIR / "var" / "backups"))
    # Files older than this in `backup_dir` are pruned by the backup
    # script. 0 = keep everything.
    backup_retention_days: int = Field(default=30)

    # Sb_26.3 — Path to the deploy state JSON written by
    # `scripts/write_deploy_state.py` at the end of each prod deploy.
    # Empty path or missing file is fine: /healthz/strict simply reports
    # `deploy.present = false`. No business behaviour depends on it.
    deploy_state_path: str = Field(default=str(BASE_DIR / "var" / "deploy_state.json"))

    # Sb_26.3 — Sentry is strictly OPT-IN via SENTRY_DSN. When the env
    # var is unset/empty, `sentry_sdk.init` is never called, so no
    # external request is ever issued and the import is a no-op if the
    # SDK is not installed. See docs/OBSERVABILITY_RUNBOOK.md §2.
    sentry_dsn: str = Field(default="")
    sentry_environment: str = Field(default="")
    sentry_traces_sample_rate: float = Field(default=0.0)

    @property
    def sentry_enabled(self) -> bool:
        return bool(self.sentry_dsn)

    # Sb_26.6 — Slow query logging (strictly opt-in). When enabled,
    # SQLAlchemy `before_cursor_execute` / `after_cursor_execute` events
    # measure query duration and log queries above `perf_slow_query_ms`.
    # No parameters logged (Statement only, truncated). Default disabled
    # for safety.
    perf_log_slow_queries_enabled: bool = Field(default=False)
    perf_slow_query_ms: int = Field(default=250)
    perf_request_timing_enabled: bool = Field(default=False)

    # Sb_26.4 — Per-IP rate limiting on sensitive public auth endpoints.
    # In-memory single-process buckets (no Redis). Tests can disable
    # via RATE_LIMIT_ENABLED=0 to avoid 429s in functional fixtures.
    rate_limit_enabled: bool = Field(default=True)
    rate_limit_login_max: int = Field(default=10)
    rate_limit_login_window_seconds: int = Field(default=600)
    rate_limit_register_max: int = Field(default=5)
    rate_limit_register_window_seconds: int = Field(default=3600)
    rate_limit_forgot_max: int = Field(default=5)
    rate_limit_forgot_window_seconds: int = Field(default=3600)

    # Sb_Body_01 — Manual Body Profile MVP gate. Strictly opt-in.
    # When False (default), every /body route returns 404, no model is
    # exercised at runtime, and there is zero production impact. Photo
    # capture and external providers (MediaPipe/Bodygram) are NOT part of
    # this flag and are not implemented in this sprint — their own flags
    # (BODY_PHOTO_CAPTURE_ENABLED / BODY_PROVIDER_BODYGRAM_ENABLED) arrive
    # in later lots. See docs/strategy/SPIGNOS_BODY_MANUAL_PROFILE_BUILD_SPEC.md.
    body_assessment_enabled: bool = Field(default=False)

    # Sb_31.X — Body Intelligence v2 gate. SEPARATE from
    # body_assessment_enabled on purpose: the Manual Body Profile (/body)
    # must be activatable WITHOUT exposing Body Intelligence v2
    # (/body/intelligence + the /coach-report snapshot). When False
    # (default): /body/intelligence* → 404 (before auth), and /coach-report
    # neither computes nor renders the Body Intelligence snapshot. Zero
    # production surface until explicitly enabled.
    body_intelligence_enabled: bool = Field(default=False)

    # SMTP for password reset emails. Leave smtp_host empty to disable.
    smtp_host: str = Field(default="")
    smtp_port: int = Field(default=587)
    smtp_user: str = Field(default="")
    smtp_password: str = Field(default="")
    smtp_from: str = Field(default="")
    smtp_use_tls: bool = Field(default=True)

    @property
    def smtp_enabled(self) -> bool:
        return bool(self.smtp_host and self.smtp_from)

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
