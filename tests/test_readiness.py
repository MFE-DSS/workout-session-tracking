"""Tests for readiness model + service layer."""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from tests.helpers import get_test_user_id

# ---------------------------------------------------------------------------
# Model basics
# ---------------------------------------------------------------------------


def test_readiness_model_fields(client):
    """ReadinessEntry has all expected columns."""
    from app.models.readiness import ReadinessEntry

    mapper = ReadinessEntry.__table__.columns
    expected = {
        "id", "user_id", "recorded_on",
        "sleep_quality", "fatigue_level", "soreness_level",
        "stress_level", "motivation_level",
        "resting_hr", "note", "created_at",
    }
    assert expected == {c.name for c in mapper}


# ---------------------------------------------------------------------------
# save_readiness + get_today_readiness
# ---------------------------------------------------------------------------


def test_save_and_get_today(client):
    """save_readiness persists an entry retrievable via get_today_readiness."""
    from app.database import SessionLocal
    from app.services.readiness import get_today_readiness, save_readiness

    uid = get_test_user_id()
    data = {
        "sleep_quality": 4, "fatigue_level": 3, "soreness_level": 2,
        "stress_level": 5, "motivation_level": 4,
        "resting_hr": 62, "note": "Feeling okay",
    }
    with SessionLocal() as db:
        entry = save_readiness(db, uid, data)
        assert entry.id is not None
        assert entry.recorded_on == date.today()
        assert entry.sleep_quality == 4
        assert entry.resting_hr == 62
        assert entry.note == "Feeling okay"

        today = get_today_readiness(db, uid)
        assert today is not None
        assert today.id == entry.id


def test_save_without_optional_fields(client):
    """resting_hr and note can be omitted."""
    from app.database import SessionLocal
    from app.services.readiness import save_readiness

    uid = get_test_user_id()
    data = {
        "sleep_quality": 3, "fatigue_level": 3, "soreness_level": 3,
        "stress_level": 3, "motivation_level": 3,
    }
    with SessionLocal() as db:
        entry = save_readiness(db, uid, data)
        assert entry.resting_hr is None
        assert entry.note is None


# ---------------------------------------------------------------------------
# Upsert same day
# ---------------------------------------------------------------------------


def test_upsert_same_day(client):
    """Second save on same day updates, does not duplicate."""
    from app.database import SessionLocal
    from app.services.readiness import save_readiness

    uid = get_test_user_id()
    base = {
        "sleep_quality": 2, "fatigue_level": 2, "soreness_level": 2,
        "stress_level": 2, "motivation_level": 2,
    }
    with SessionLocal() as db:
        first = save_readiness(db, uid, base)
        first_id = first.id

        updated = {**base, "sleep_quality": 5, "note": "Updated"}
        second = save_readiness(db, uid, updated)
        assert second.id == first_id
        assert second.sleep_quality == 5
        assert second.note == "Updated"

        # Confirm only one row
        from sqlalchemy import func, select

        from app.models.readiness import ReadinessEntry

        count = db.execute(
            select(func.count()).select_from(ReadinessEntry).where(
                ReadinessEntry.user_id == uid,
                ReadinessEntry.recorded_on == date.today(),
            )
        ).scalar()
        assert count == 1


# ---------------------------------------------------------------------------
# get_readiness_history
# ---------------------------------------------------------------------------


def test_readiness_history_order(client):
    """History returns entries ordered by recorded_on DESC."""
    from app.database import SessionLocal
    from app.models.readiness import ReadinessEntry
    from app.services.readiness import get_readiness_history

    uid = get_test_user_id()
    today = date.today()
    with SessionLocal() as db:
        for offset in [5, 2, 8, 0]:
            entry = ReadinessEntry(
                user_id=uid, recorded_on=today - timedelta(days=offset),
                sleep_quality=3, fatigue_level=3, soreness_level=3,
                stress_level=3, motivation_level=3,
            )
            db.add(entry)
        db.commit()

        history = get_readiness_history(db, uid, days=30)
        dates = [e.recorded_on for e in history]
        assert dates == sorted(dates, reverse=True)
        assert len(history) == 4


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def test_validate_rejects_out_of_range(client):
    """Scale values outside 1-5 raise ValueError."""
    from app.database import SessionLocal
    from app.services.readiness import save_readiness

    uid = get_test_user_id()
    bad = {
        "sleep_quality": 0, "fatigue_level": 3, "soreness_level": 3,
        "stress_level": 3, "motivation_level": 3,
    }
    with SessionLocal() as db:
        with pytest.raises(ValueError):
            save_readiness(db, uid, bad)


def test_validate_rejects_non_int(client):
    """Non-integer scale values raise ValueError."""
    from app.database import SessionLocal
    from app.services.readiness import save_readiness

    uid = get_test_user_id()
    bad = {
        "sleep_quality": "high", "fatigue_level": 3, "soreness_level": 3,
        "stress_level": 3, "motivation_level": 3,
    }
    with SessionLocal() as db:
        with pytest.raises(ValueError):
            save_readiness(db, uid, bad)


def test_validate_rejects_value_above_5(client):
    """Scale value of 6 raises ValueError."""
    from app.database import SessionLocal
    from app.services.readiness import save_readiness

    uid = get_test_user_id()
    bad = {
        "sleep_quality": 6, "fatigue_level": 3, "soreness_level": 3,
        "stress_level": 3, "motivation_level": 3,
    }
    with SessionLocal() as db:
        with pytest.raises(ValueError):
            save_readiness(db, uid, bad)
