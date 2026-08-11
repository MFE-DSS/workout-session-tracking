"""SQLAlchemy engine + session factory.

Dialect-agnostic: works with SQLite for V1 and PostgreSQL later by only
changing `DATABASE_URL`. We only set SQLite-specific `connect_args` when the
URL points at sqlite.
"""
from __future__ import annotations

import logging
import sqlite3
import time
from collections.abc import Iterator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

_slow_query_logger = logging.getLogger("spignos.slow_query")


# Ensure SQLite enforces ON DELETE SET NULL / CASCADE. Without this
# PRAGMA, FKs are parsed but never enforced on SQLite, which silently
# breaks the snapshot-based resilience strategy in `models/session.py`.
@event.listens_for(Engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, connection_record):  # pragma: no cover
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

_settings = get_settings()

_connect_args: dict = {}
if _settings.is_sqlite:
    # Required so the same connection can serve multiple threads (uvicorn).
    _connect_args["check_same_thread"] = False

engine = create_engine(
    _settings.database_url,
    connect_args=_connect_args,
    future=True,
    echo=False,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


# Sb_26.6 — opt-in slow-query logger. Registered unconditionally but
# returns immediately when the setting is False, so the runtime overhead
# with the default (disabled) config is one bool check per cursor execute.
# We log the truncated SQL statement only — never the parameter tuple,
# which can contain user data, credentials hashes, etc.
def _maybe_register_slow_query_logger() -> None:
    settings = get_settings()
    if not settings.perf_log_slow_queries_enabled:
        return

    threshold_s = settings.perf_slow_query_ms / 1000.0

    @event.listens_for(engine, "before_cursor_execute")
    def _before(conn, cursor, statement, parameters, context, executemany):
        context._spignos_perf_t0 = time.perf_counter()

    @event.listens_for(engine, "after_cursor_execute")
    def _after(conn, cursor, statement, parameters, context, executemany):
        t0 = getattr(context, "_spignos_perf_t0", None)
        if t0 is None:
            return
        dt = time.perf_counter() - t0
        if dt >= threshold_s:
            stmt_short = " ".join(statement.split())[:200]
            _slow_query_logger.warning(
                "slow query %.0fms (threshold %dms): %s",
                dt * 1000,
                settings.perf_slow_query_ms,
                stmt_short,
            )


_maybe_register_slow_query_logger()


class Base(DeclarativeBase):
    """Declarative base shared by all ORM models."""


def get_db() -> Iterator[Session]:
    """FastAPI dependency that yields a scoped SQLAlchemy session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables. Replaced by Alembic once we have migrations."""
    # Import side effect: register models with Base.metadata
    from app.models import (  # noqa: F401
        catalog,
        challenge,
        measurement,
        readiness,
        session,
        sharing,
        squad,
    )

    Base.metadata.create_all(bind=engine)

    # Sb_32.4 — `create_all` above also creates `body_zones` and
    # `exercise_muscle_mappings`, EMPTY, and the Alembic backfills only fire
    # when they themselves created the table. So on any boot that precedes
    # `alembic upgrade` — the whole test suite, a fresh dev machine — the
    # reference tables would stay empty forever and every formal lookup would
    # silently degrade to substring matching. The seed is deterministic,
    # idempotent, reference-data-only and costs ~1 ms on an empty database.
    from app.services.reference_data_seed import seed_reference_data

    with SessionLocal() as db:
        seed_reference_data(db)
