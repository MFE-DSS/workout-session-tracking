"""SQLAlchemy engine + session factory.

Dialect-agnostic: works with SQLite for V1 and PostgreSQL later by only
changing `DATABASE_URL`. We only set SQLite-specific `connect_args` when the
URL points at sqlite.
"""
from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

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
