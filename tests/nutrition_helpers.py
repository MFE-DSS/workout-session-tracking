"""Explicit synthetic nutrition fixtures; never grants at application startup."""

from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session


@contextmanager
def nutrition_db(tmp_path):
    from app import models  # noqa: F401 — load existing metadata in tests only
    from app.database import Base
    from app.models.nutrition import NutritionDayRevision, NutritionTargetRevision  # noqa: F401
    from app.models.user import User

    engine = create_engine(f"sqlite:///{tmp_path / 'nutrition-synthetic.db'}")

    @event.listens_for(engine, "connect")
    def foreign_keys(connection, _):
        connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add_all([
            User(id=1, username="nutrition-synthetic-a", password_hash="synthetic-only"),
            User(id=2, username="nutrition-synthetic-b", password_hash="synthetic-only"),
        ])
        session.commit()
        yield session
    engine.dispose()


@contextmanager
def nutrition_environment(monkeypatch):
    from app.config import get_settings

    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("APP_SECRET_KEY", "nutrition-synthetic-signing-secret-only")
    monkeypatch.setenv("NUTRITION_MANUAL_CONTROLLED_TEST_ENABLED", "true")
    monkeypatch.setenv("NUTRITION_BACKEND_IDENTITY", "synthetic-nut-backend-a")
    monkeypatch.setenv("NUTRITION_SIGNING_KEY", "synthetic-nut-specific-signing-key-only")
    get_settings.cache_clear()
    try:
        yield
    finally:
        get_settings.cache_clear()


def proof(session):
    from app.models.user import User

    owner = session.get(User, 1)
    return {"expected_epoch": owner.session_epoch, "expected_hash": owner.password_hash,
            "device_id": None}
