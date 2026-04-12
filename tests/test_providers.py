"""Tests for MetricsProvider abstraction."""
from __future__ import annotations

from app.services.providers import (
    ActivitySummary,
    BodyMetrics,
    ManualProvider,
    ProviderRegistry,
)


def test_manual_provider_supports_body_metrics():
    provider = ManualProvider()
    assert "body_metrics" in provider.supports()


def test_manual_provider_get_body_metrics(client):
    """ManualProvider reads physical fields from User model."""
    from app.database import SessionLocal
    from app.models.user import User
    from sqlalchemy import select

    with SessionLocal() as db:
        user = db.execute(select(User).where(User.username == "testuser")).scalar_one()
        user.height_cm = 180
        user.weight_kg = 75.0
        user.bp_systolic = 120
        user.bp_diastolic = 80
        db.commit()
        uid = user.id

    with SessionLocal() as db:
        provider = ManualProvider()
        metrics = provider.get_body_metrics(db, uid)

    assert metrics is not None
    assert metrics.height_cm == 180
    assert metrics.weight_kg == 75.0
    assert metrics.bp_systolic == 120
    assert metrics.bp_diastolic == 80


def test_manual_provider_activity_returns_none(client):
    from app.database import SessionLocal
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    with SessionLocal() as db:
        provider = ManualProvider()
        result = provider.get_activity_summary(db, uid)
    assert result is None


def test_registry_register_and_get():
    registry = ProviderRegistry()
    provider = ManualProvider()
    registry.register("manual", provider)
    assert registry.get("manual") is provider
    assert registry.get("nonexistent") is None
    assert "manual" in registry.list_available()
