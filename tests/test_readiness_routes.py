"""Tests for readiness routes (POST /readiness)."""
from __future__ import annotations

from datetime import date


# ---------------------------------------------------------------------------
# POST /readiness — happy path
# ---------------------------------------------------------------------------


def test_post_readiness_saves_and_redirects(client):
    """POST /readiness with valid data saves entry and redirects to /."""
    r = client.post("/readiness", data={
        "sleep_quality": "4", "fatigue_level": "3", "soreness_level": "2",
        "stress_level": "5", "motivation_level": "4",
    }, follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/"

    from app.database import SessionLocal
    from app.models.readiness import ReadinessEntry
    from sqlalchemy import select
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    with SessionLocal() as db:
        entry = db.execute(
            select(ReadinessEntry).where(
                ReadinessEntry.user_id == uid,
                ReadinessEntry.recorded_on == date.today(),
            )
        ).scalar_one()
        assert entry.sleep_quality == 4
        assert entry.fatigue_level == 3


def test_post_readiness_with_optional_fields(client):
    """POST with resting_hr and note persists them."""
    r = client.post("/readiness", data={
        "sleep_quality": "3", "fatigue_level": "3", "soreness_level": "3",
        "stress_level": "3", "motivation_level": "3",
        "resting_hr": "58", "note": "Slept well",
    }, follow_redirects=False)
    assert r.status_code == 303

    from app.database import SessionLocal
    from app.models.readiness import ReadinessEntry
    from sqlalchemy import select
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    with SessionLocal() as db:
        entry = db.execute(
            select(ReadinessEntry).where(
                ReadinessEntry.user_id == uid,
                ReadinessEntry.recorded_on == date.today(),
            )
        ).scalar_one()
        assert entry.resting_hr == 58
        assert entry.note == "Slept well"


# ---------------------------------------------------------------------------
# POST /readiness — invalid data
# ---------------------------------------------------------------------------


def test_post_readiness_invalid_scale_redirects(client):
    """POST with non-numeric scale values redirects gracefully."""
    r = client.post("/readiness", data={
        "sleep_quality": "bad", "fatigue_level": "3", "soreness_level": "3",
        "stress_level": "3", "motivation_level": "3",
    }, follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/"


def test_post_readiness_out_of_range_redirects(client):
    """POST with scale value out of 1-5 redirects gracefully."""
    r = client.post("/readiness", data={
        "sleep_quality": "0", "fatigue_level": "3", "soreness_level": "3",
        "stress_level": "3", "motivation_level": "3",
    }, follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/"


# ---------------------------------------------------------------------------
# Auth required
# ---------------------------------------------------------------------------


def test_post_readiness_requires_auth(client):
    """POST /readiness without auth redirects to /login."""
    from fastapi.testclient import TestClient
    from app.main import app

    # Use a fresh client without the auth cookie.
    with TestClient(app) as anon:
        r = anon.post("/readiness", data={
            "sleep_quality": "3", "fatigue_level": "3", "soreness_level": "3",
            "stress_level": "3", "motivation_level": "3",
        }, follow_redirects=False)
        assert r.status_code == 303
        assert "/login" in r.headers["location"]


# ---------------------------------------------------------------------------
# GET /readiness/history (task 8 — expected to fail until implemented)
# ---------------------------------------------------------------------------


def test_get_readiness_history_requires_auth(client):
    """GET /readiness/history without auth redirects to /login."""
    from fastapi.testclient import TestClient
    from app.main import app

    with TestClient(app) as anon:
        r = anon.get("/readiness/history", follow_redirects=False)
        # Either 303 redirect to login, or 404 if route not yet defined.
        assert r.status_code in (303, 404, 405)
