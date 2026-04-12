"""Tests for body measurement service."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.services.measurements import (
    MEASUREMENT_LABELS,
    MEASUREMENT_MUSCLE_MAP,
    find_related_templates,
    get_latest_measurement,
    get_measurement_series,
)
from tests.helpers import get_test_user_id


def test_muscle_map_has_all_fields():
    assert set(MEASUREMENT_MUSCLE_MAP.keys()) == {
        "weight_kg", "chest_cm", "arm_cm", "waist_cm", "thigh_cm", "calf_cm",
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
    result = find_related_templates("thigh_cm", templates)
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
