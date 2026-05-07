"""Tests for body measurement service."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from app.services.measurements import (
    MEASUREMENT_LABELS,
    MEASUREMENT_MUSCLE_MAP,
    compute_arm_avg,
    compute_thigh_avg,
    compute_zone_measurement,
    find_related_templates,
    get_latest_measurement,
    get_measurement_series,
)
from tests.helpers import get_test_user_id


def test_muscle_map_has_all_fields():
    assert set(MEASUREMENT_MUSCLE_MAP.keys()) == {
        "weight_kg", "chest_cm",
        "arm_cm_left", "arm_cm_right",
        "waist_cm",
        "thigh_cm_left", "thigh_cm_right",
        "hip_cm", "neck_cm", "calf_cm",
    }


def test_labels_has_all_fields():
    assert set(MEASUREMENT_LABELS.keys()) == set(MEASUREMENT_MUSCLE_MAP.keys())


def test_find_related_templates_chest():
    class FakeTemplate:
        def __init__(self, name, focus):
            self.name = name
            self.focus = focus

    templates = [
        FakeTemplate("Push A", "Pectoral, Delts, Triceps"),
        FakeTemplate("Pull A", "Dos, Delts arrière"),
        FakeTemplate("Legs", "Jambes"),
    ]
    result = find_related_templates("chest_cm", templates)
    assert result == ["Push A"]


def test_find_related_templates_weight_returns_empty():
    class FakeTemplate:
        def __init__(self, name, focus):
            self.name = name
            self.focus = focus

    templates = [FakeTemplate("Push A", "Pectoral")]
    result = find_related_templates("weight_kg", templates)
    assert result == []


def test_find_related_templates_thigh():
    class FakeTemplate:
        def __init__(self, name, focus):
            self.name = name
            self.focus = focus

    templates = [
        FakeTemplate("Push A", "Pectoral, Delts"),
        FakeTemplate("Legs", "Jambes"),
    ]
    result = find_related_templates("thigh_cm_left", templates)
    assert result == ["Legs"]


def test_get_latest_measurement_empty(client):
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        result = get_latest_measurement(db, uid)
    assert result is None


def test_get_latest_measurement_returns_most_recent(client):
    from app.database import SessionLocal
    from app.models.measurement import BodyMeasurement

    uid = get_test_user_id()
    now = datetime.now(timezone.utc)

    with SessionLocal() as db:
        db.add(BodyMeasurement(
            user_id=uid, measured_at=now - timedelta(days=7), weight_kg=74.0,
        ))
        db.add(BodyMeasurement(
            user_id=uid, measured_at=now, weight_kg=75.0, chest_cm=100.0,
        ))
        db.commit()

    with SessionLocal() as db:
        latest = get_latest_measurement(db, uid)
    assert latest is not None
    assert latest.weight_kg == 75.0
    assert latest.chest_cm == 100.0


def test_get_measurement_series(client):
    from app.database import SessionLocal
    from app.models.measurement import BodyMeasurement

    uid = get_test_user_id()
    now = datetime.now(timezone.utc)

    with SessionLocal() as db:
        db.add(BodyMeasurement(
            user_id=uid, measured_at=now - timedelta(days=14), weight_kg=73.0,
        ))
        db.add(BodyMeasurement(
            user_id=uid, measured_at=now - timedelta(days=7), weight_kg=74.0,
        ))
        db.add(BodyMeasurement(
            user_id=uid, measured_at=now, weight_kg=75.0,
        ))
        db.add(BodyMeasurement(
            user_id=uid, measured_at=now - timedelta(days=3), chest_cm=99.0,
        ))
        db.commit()

    with SessionLocal() as db:
        series = get_measurement_series(db, uid, "weight_kg")
    assert len(series) == 3
    assert series[0][1] == 73.0
    assert series[2][1] == 75.0


def test_get_measurement_series_weight_merges_session_bodyweight(client):
    """Sb_17 — pre-session bodyweight feeds the same timeline as the
    formal weight measurement, only for the weight_kg field."""
    from app.database import SessionLocal
    from app.models.measurement import BodyMeasurement
    from app.models.session import WorkoutSession

    uid = get_test_user_id()
    now = datetime.now(timezone.utc)

    with SessionLocal() as db:
        # Two formal measurements
        db.add(BodyMeasurement(
            user_id=uid, measured_at=now - timedelta(days=10), weight_kg=78.0,
        ))
        db.add(BodyMeasurement(
            user_id=uid, measured_at=now - timedelta(days=2), weight_kg=77.5,
        ))
        # Two completed sessions with bodyweight, on different days
        db.add(WorkoutSession(
            user_id=uid,
            template_slug_snapshot="push-a",
            template_name_snapshot="Push A",
            started_at=now - timedelta(days=7),
            ended_at=now - timedelta(days=7),
            status="completed",
            bodyweight_kg=77.8,
        ))
        db.add(WorkoutSession(
            user_id=uid,
            template_slug_snapshot="pull-a",
            template_name_snapshot="Pull A",
            started_at=now - timedelta(days=4),
            ended_at=now - timedelta(days=4),
            status="completed",
            bodyweight_kg=77.6,
        ))
        # An excluded session must NOT appear
        db.add(WorkoutSession(
            user_id=uid,
            template_slug_snapshot="legs-a",
            template_name_snapshot="Legs A",
            started_at=now - timedelta(days=5),
            ended_at=now - timedelta(days=5),
            status="completed",
            bodyweight_kg=999.0,
            excluded_from_stats=True,
        ))
        db.commit()

    with SessionLocal() as db:
        series = get_measurement_series(db, uid, "weight_kg")

    # 2 measurements + 2 valid sessions, sorted ASC, no excluded outlier
    assert len(series) == 4
    assert all(s[1] != 999.0 for s in series), "excluded session leaked"
    # ASC order
    dates = [s[0] for s in series]
    assert dates == sorted(dates)
    # Values cover both sources
    values = [s[1] for s in series]
    assert 78.0 in values   # measurement
    assert 77.8 in values   # session
    assert 77.5 in values
    assert 77.6 in values


def test_get_measurement_series_other_field_ignores_session_bodyweight(client):
    """Sb_17 — only weight_kg merges. chest_cm should not be polluted by
    WorkoutSession data."""
    from app.database import SessionLocal
    from app.models.measurement import BodyMeasurement
    from app.models.session import WorkoutSession

    uid = get_test_user_id()
    now = datetime.now(timezone.utc)

    with SessionLocal() as db:
        db.add(BodyMeasurement(
            user_id=uid, measured_at=now, chest_cm=100.0,
        ))
        db.add(WorkoutSession(
            user_id=uid,
            template_slug_snapshot="push-a",
            template_name_snapshot="Push A",
            started_at=now,
            ended_at=now,
            status="completed",
            bodyweight_kg=80.0,
        ))
        db.commit()

    with SessionLocal() as db:
        series = get_measurement_series(db, uid, "chest_cm")

    # Only the formal measurement, the session bodyweight is irrelevant
    assert len(series) == 1
    assert series[0][1] == 100.0


def test_get_measurement_series_unknown_field(client):
    """Requesting a field that doesn't exist on the model returns empty list."""
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        series = get_measurement_series(db, uid, "nonexistent_field")
    assert series == []


# ---------------------------------------------------------------------------
# compute_arm_avg / compute_thigh_avg / compute_zone_measurement
# ---------------------------------------------------------------------------

def test_compute_arm_avg_both():
    m = SimpleNamespace(arm_cm_left=35.0, arm_cm_right=37.0)
    assert compute_arm_avg(m) == 36.0


def test_compute_arm_avg_left_only():
    m = SimpleNamespace(arm_cm_left=35.0, arm_cm_right=None)
    assert compute_arm_avg(m) == 35.0


def test_compute_arm_avg_right_only():
    m = SimpleNamespace(arm_cm_left=None, arm_cm_right=37.0)
    assert compute_arm_avg(m) == 37.0


def test_compute_arm_avg_none():
    m = SimpleNamespace(arm_cm_left=None, arm_cm_right=None)
    assert compute_arm_avg(m) is None


def test_compute_thigh_avg_both():
    m = SimpleNamespace(thigh_cm_left=55.0, thigh_cm_right=57.0)
    assert compute_thigh_avg(m) == 56.0


def test_compute_thigh_avg_none():
    m = SimpleNamespace(thigh_cm_left=None, thigh_cm_right=None)
    assert compute_thigh_avg(m) is None


def test_compute_zone_measurement_direct():
    m = SimpleNamespace(chest_cm=100.0, waist_cm=80.0)
    assert compute_zone_measurement(m, "pecs") == 100.0
    assert compute_zone_measurement(m, "core") == 80.0


def test_compute_zone_measurement_lateralized():
    m = SimpleNamespace(
        arm_cm_left=35.0, arm_cm_right=37.0,
        thigh_cm_left=55.0, thigh_cm_right=57.0,
    )
    assert compute_zone_measurement(m, "biceps") == 36.0
    assert compute_zone_measurement(m, "triceps") == 36.0
    assert compute_zone_measurement(m, "quads") == 56.0
    assert compute_zone_measurement(m, "posterior") == 56.0


def test_compute_zone_measurement_unknown():
    m = SimpleNamespace()
    assert compute_zone_measurement(m, "calves") is None
    assert compute_zone_measurement(m, "lats") is None


# ---------------------------------------------------------------------------
# Timeline tests (existing)
# ---------------------------------------------------------------------------

from app.services.timeline import build_measurement_timeline_svg, TimelinePoint


def test_measurement_timeline_returns_svg():
    points = [
        TimelinePoint(label="01/04", value=95.0),
        TimelinePoint(label="08/04", value=97.0),
        TimelinePoint(label="12/04", value=100.0),
    ]
    svg = build_measurement_timeline_svg(points, title="Poitrine (cm)")
    assert "<svg" in svg
    assert "Poitrine (cm)" in svg


def test_measurement_timeline_empty_returns_empty():
    assert build_measurement_timeline_svg([], title="Test") == ""


def test_measurement_timeline_one_point_returns_empty():
    points = [TimelinePoint(label="01/04", value=95.0)]
    assert build_measurement_timeline_svg(points, title="Test") == ""
