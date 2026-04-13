"""Tests for muscle mapping, scoring, and dashboard."""
from __future__ import annotations

from app.services.muscle_mapping import (
    RADAR_AXES,
    ZONE_LABELS,
    classify_exercise,
)


def test_zone_labels_has_11_zones():
    assert len(ZONE_LABELS) == 11


def test_radar_axes_has_6():
    assert len(RADAR_AXES) == 6


def test_classify_chest_press():
    zone, secondary = classify_exercise("Chest Press machine")
    assert zone == "pecs"
    assert "triceps" in secondary


def test_classify_incline_smith():
    zone, _ = classify_exercise("Incline Smith Press")
    assert zone == "pecs"


def test_classify_lateral_raise():
    zone, _ = classify_exercise("Élévations latérales câble")
    assert zone == "delt_lat"


def test_classify_face_pull():
    zone, _ = classify_exercise("Face pull câble")
    assert zone == "delt_post"


def test_classify_lat_pulldown():
    zone, secondary = classify_exercise("Tirage poulie haute prise neutre")
    assert zone == "lats"
    assert "biceps" in secondary


def test_classify_rowing():
    zone, _ = classify_exercise("Rowing machine chest-supported")
    assert zone == "upper_back"


def test_classify_curl():
    zone, _ = classify_exercise("Curl incliné haltères")
    assert zone == "biceps"


def test_classify_triceps():
    zone, _ = classify_exercise("Triceps extension poulie haute")
    assert zone == "triceps"


def test_classify_hack_squat():
    zone, _ = classify_exercise("Hack Squat machine")
    assert zone == "quads"


def test_classify_rdl():
    zone, _ = classify_exercise("Romanian Deadlift haltères")
    assert zone == "posterior"


def test_classify_calf():
    zone, _ = classify_exercise("Relevés mollets debout")
    assert zone == "calves"


def test_classify_ab_wheel():
    zone, _ = classify_exercise("Roulette abdominale (ab wheel rollout)")
    assert zone == "core"


def test_classify_unknown():
    zone, secondary = classify_exercise("Exercice inconnu xyz")
    assert zone == "unknown"
    assert secondary == []


def test_classify_butterfly():
    zone, _ = classify_exercise("Butterfly pec machine")
    assert zone == "pecs"


def test_classify_dips():
    zone, _ = classify_exercise("Dips pectoraux (buste penché)")
    assert zone == "pecs"


def test_classify_skull_crushers():
    zone, _ = classify_exercise("Skull crushers EZ-bar")
    assert zone == "triceps"


def test_classify_leg_curl():
    zone, _ = classify_exercise("Leg curls assis")
    assert zone == "posterior"


def test_classify_leg_extension():
    zone, _ = classify_exercise("Leg extensions assises")
    assert zone == "quads"


def test_classify_hip_thrust():
    zone, _ = classify_exercise("Hip thrust Smith machine")
    assert zone == "posterior"


def test_classify_shoulder_press():
    zone, _ = classify_exercise("Machine shoulder press")
    assert zone == "delt_lat"
