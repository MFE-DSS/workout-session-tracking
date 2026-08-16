"""Tests for app.services.confidence (Sb_08 — logging confidence score)."""
from __future__ import annotations

from tests.test_anomalies import _load, _mk_session_for_anomalies


def test_confidence_high_on_clean_complete_session(client):
    from app.services.confidence import compute_confidence_score, level_for
    sid = _mk_session_for_anomalies(
        exercises=[{
            "code": "E1",
            "rep_targets": [{"min_reps": 8, "max_reps": 12}],
            "success_score": 80,
            "work_sets": [
                {"weight_kg": 50, "reps": 10, "completed": True},
                {"weight_kg": 50, "reps": 9, "completed": True},
                {"weight_kg": 50, "reps": 8, "completed": True},
            ],
        }],
        concentration="high",
        global_state="good",
    )
    db, s = _load(sid)
    try:
        s.bodyweight_kg = 78.0
        score = compute_confidence_score(s)
        assert 80 <= score <= 100
        assert level_for(score) == "eleve"
    finally:
        db.close()


def test_confidence_drops_with_empty_completed_sets(client):
    from app.services.confidence import compute_confidence_score
    sid = _mk_session_for_anomalies(
        exercises=[{
            "code": "E1",
            "work_sets": [
                {"weight_kg": None, "reps": None, "completed": True},
                {"weight_kg": None, "reps": None, "completed": True},
            ],
        }],
        concentration=None,
        global_state=None,
    )
    db, s = _load(sid)
    try:
        score = compute_confidence_score(s)
        assert score < 50
    finally:
        db.close()


def test_confidence_bodyweight_bonus(client):
    from app.services.confidence import compute_confidence_score
    sid = _mk_session_for_anomalies(
        exercises=[{
            "code": "E1",
            "work_sets": [{"weight_kg": 50, "reps": 10, "completed": True}],
        }],
    )
    db, s = _load(sid)
    try:
        base = compute_confidence_score(s)
        s.bodyweight_kg = 78.0
        bumped = compute_confidence_score(s)
        assert bumped > base
    finally:
        db.close()


def test_confidence_within_0_100_bounds(client):
    from app.services.confidence import compute_confidence_score
    sid = _mk_session_for_anomalies(
        exercises=[{
            "code": "E1",
            "work_sets": [{"weight_kg": 50, "reps": 10, "completed": True}],
        }],
    )
    db, s = _load(sid)
    try:
        score = compute_confidence_score(s)
        assert 0 <= score <= 100
    finally:
        db.close()


def test_confidence_level_thresholds():
    from app.services.confidence import level_for
    assert level_for(100) == "eleve"
    assert level_for(80) == "eleve"
    assert level_for(79) == "moyen"
    assert level_for(50) == "moyen"
    assert level_for(49) == "faible"
    assert level_for(0) == "faible"


def test_confidence_penalised_by_many_anomalies(client):
    from app.services.anomalies import compute_anomalies
    from app.services.confidence import compute_confidence_score

    sid = _mk_session_for_anomalies(
        exercises=[{
            "code": "E1",
            "work_sets": [
                {"weight_kg": 40, "reps": 8, "completed": True},
                {"weight_kg": 45, "reps": 9, "completed": True},   # B
                {"weight_kg": 50, "reps": 10, "completed": True},
                {"weight_kg": None, "reps": None, "completed": True},  # A
            ],
        }],
    )
    db, s = _load(sid)
    try:
        anomalies = compute_anomalies(s)
        assert len(anomalies) >= 2
        score_all = compute_confidence_score(s)
        score_none = compute_confidence_score(s, anomalies=[])
        assert score_none > score_all
    finally:
        db.close()
