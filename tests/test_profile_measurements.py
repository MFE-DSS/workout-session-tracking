"""Tests for measurement integration on profile page."""
from __future__ import annotations


def test_profile_shows_measurement_form(client):
    body = client.get("/profile").text
    assert "measured_at" in body
    assert "mesure" in body.lower()


def test_profile_measurement_submit(client):
    r = client.post("/profile/measurements", data={
        "measured_at": "2026-04-12",
        "chest_cm": "100",
        "arm_cm_left": "36",
        "arm_cm_right": "37",
        "thigh_cm_left": "",
        "thigh_cm_right": "",
    }, follow_redirects=False)
    assert r.status_code == 303

    # Verify data persisted
    from app.database import SessionLocal
    from app.models.measurement import BodyMeasurement
    from tests.helpers import get_test_user_id
    from sqlalchemy import select

    uid = get_test_user_id()
    with SessionLocal() as db:
        m = db.execute(
            select(BodyMeasurement).where(BodyMeasurement.user_id == uid)
        ).scalar_one()
        assert m.chest_cm == 100.0
        assert m.arm_cm_left == 36.0
        assert m.arm_cm_right == 37.0
        assert m.thigh_cm_left is None
        assert m.thigh_cm_right is None


def test_profile_measurement_same_day_appends_instead_of_overwriting(client):
    """Two submissions on one date produce two dated facts.

    Sb_MORPHO_PROFILE_RUNTIME_01 — this test previously asserted the opposite
    (upsert-by-day: one row, overwritten). The contract changed deliberately:
    `body_profile.create_measurement` is now the single canonical writer and it
    treats `body_measurements` as an append-only series
    (`Sx_MORPHO_CAPTURE_01_SPEC` §2.1). Correcting an entry means adding a later
    fact, not rewriting the earlier one — so the first value must survive.

    The guard is kept, not dropped: it now pins the new contract, including the
    part that matters most, which is that the original reading is still there.
    """
    client.post("/profile/measurements", data={
        "measured_at": "2026-04-10",
        "chest_cm": "95",
    }, follow_redirects=False)

    client.post("/profile/measurements", data={
        "measured_at": "2026-04-10",
        "chest_cm": "96",
        "arm_cm_left": "35",
    }, follow_redirects=False)

    from app.database import SessionLocal
    from app.models.measurement import BodyMeasurement
    from tests.helpers import get_test_user_id
    from sqlalchemy import select
    from datetime import datetime, timezone

    uid = get_test_user_id()
    day = datetime(2026, 4, 10, tzinfo=timezone.utc)
    day_end = datetime(2026, 4, 11, tzinfo=timezone.utc)
    with SessionLocal() as db:
        rows = db.execute(
            select(BodyMeasurement)
            .where(BodyMeasurement.user_id == uid)
            .where(BodyMeasurement.measured_at >= day)
            .where(BodyMeasurement.measured_at < day_end)
            .order_by(BodyMeasurement.id)
        ).scalars().all()

    assert len(rows) == 2
    # The earlier reading is intact — nothing was rewritten.
    assert rows[0].chest_cm == 95.0
    assert rows[0].arm_cm_left is None
    assert rows[1].chest_cm == 96.0
    assert rows[1].arm_cm_left == 35.0


def test_profile_measurement_skip_when_all_empty(client):
    """All fields empty → no row inserted."""
    from app.database import SessionLocal
    from app.models.measurement import BodyMeasurement
    from tests.helpers import get_test_user_id
    from sqlalchemy import select, func

    uid = get_test_user_id()
    with SessionLocal() as db:
        before = db.execute(
            select(func.count(BodyMeasurement.id))
            .where(BodyMeasurement.user_id == uid)
        ).scalar_one()

    client.post("/profile/measurements", data={
        "measured_at": "2026-04-11",
        "chest_cm": "",
        "arm_cm_left": "",
        "arm_cm_right": "",
        "thigh_cm_left": "",
        "thigh_cm_right": "",
    }, follow_redirects=False)

    with SessionLocal() as db:
        after = db.execute(
            select(func.count(BodyMeasurement.id))
            .where(BodyMeasurement.user_id == uid)
        ).scalar_one()

    assert after == before  # no new row


def test_profile_measurement_future_date_capped(client):
    """Date in the future is capped to today."""
    client.post("/profile/measurements", data={
        "measured_at": "2030-01-01",
        "chest_cm": "99",
        "arm_cm_left": "",
        "arm_cm_right": "",
        "thigh_cm_left": "",
        "thigh_cm_right": "",
    }, follow_redirects=False)

    from app.database import SessionLocal
    from app.models.measurement import BodyMeasurement
    from tests.helpers import get_test_user_id
    from sqlalchemy import select
    from datetime import datetime, timezone

    uid = get_test_user_id()
    with SessionLocal() as db:
        m = db.execute(
            select(BodyMeasurement)
            .where(BodyMeasurement.user_id == uid)
            .where(BodyMeasurement.chest_cm == 99.0)
        ).scalar_one_or_none()
        assert m is not None
        assert m.measured_at.date() <= datetime.now(timezone.utc).date()
