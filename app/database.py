"""SQLAlchemy engine + session factory.

Dialect-agnostic: works with SQLite for V1 and PostgreSQL later by only
changing `DATABASE_URL`. We only set SQLite-specific `connect_args` when the
URL points at sqlite.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Iterator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


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
    from app.models import catalog, session  # noqa: F401

    Base.metadata.create_all(bind=engine)
