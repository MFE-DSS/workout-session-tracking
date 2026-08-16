"""Tests for behavioral engine scoring logic."""
from __future__ import annotations

from app.services.behavioral import (
    BehavioralState,
    compute_consistency,
    compute_readiness,
    compute_recommendation,
    compute_session_fatigue,
    compute_trend,
    compute_weighted_fatigue,
)


def test_session_fatigue_high():
    f = compute_session_fatigue(global_state="fatigued", concentration="low")
    assert f == 75.0


def test_session_fatigue_low():
    f = compute_session_fatigue(global_state="good", concentration="high")
    assert f == 15.0


def test_session_fatigue_null_defaults():
    f = compute_session_fatigue(global_state=None, concentration=None)
    assert f == 45.0


def test_session_fatigue_mixed():
    f = compute_session_fatigue(global_state="flat", concentration="high")
    assert f == 30.0


def test_weighted_fatigue_three_sessions():
    fatigue_scores = [75.0, 30.0, 15.0]
    result = compute_weighted_fatigue(fatigue_scores)
    assert abs(result - 49.5) < 0.01


def test_weighted_fatigue_two_sessions():
    result = compute_weighted_fatigue([60.0, 30.0])
    assert abs(result - 48.0) < 0.01


def test_weighted_fatigue_one_session():
    result = compute_weighted_fatigue([75.0])
    assert result == 75.0


def test_weighted_fatigue_no_sessions():
    result = compute_weighted_fatigue([])
    assert result == 50.0


def test_consistency_daily():
    assert compute_consistency(sessions_14d=14) == 100.0


def test_consistency_none():
    assert compute_consistency(sessions_14d=0) == 0.0


def test_consistency_partial():
    result = compute_consistency(sessions_14d=3)
    assert abs(result - 21.43) < 0.1


def test_consistency_capped():
    assert compute_consistency(sessions_14d=20) == 100.0


def test_readiness_formula():
    r = compute_readiness(fatigue=30.0, consistency=80.0, performance=90.0)
    assert abs(r - 77.0) < 0.01


def test_readiness_high_fatigue():
    r = compute_readiness(fatigue=90.0, consistency=50.0, performance=50.0)
    assert abs(r - 30.0) < 0.01


def test_trend_up():
    assert compute_trend(last_7=4, prev_7=2) == "up"


def test_trend_down():
    assert compute_trend(last_7=1, prev_7=3) == "down"


def test_trend_stable():
    assert compute_trend(last_7=2, prev_7=2) == "stable"


def test_reco_fatigue_critical():
    state = BehavioralState(
        performance_score=80, consistency_score=70, fatigue_score=80,
        trend_direction="stable", streak_days=2, readiness_score=40,
        recommendation="",
    )
    reco = compute_recommendation(state)
    assert "repos" in reco.lower() or "fatigue" in reco.lower()


def test_reco_streak_fatigue():
    state = BehavioralState(
        performance_score=70, consistency_score=60, fatigue_score=65,
        trend_direction="up", streak_days=6, readiness_score=50,
        recommendation="",
    )
    reco = compute_recommendation(state)
    assert "récupérer" in reco.lower() or "serie" in reco.lower() or "série" in reco.lower()


def test_reco_low_consistency():
    state = BehavioralState(
        performance_score=50, consistency_score=20, fatigue_score=40,
        trend_direction="stable", streak_days=0, readiness_score=45,
        recommendation="",
    )
    reco = compute_recommendation(state)
    assert "régularité" in reco.lower() or "regularite" in reco.lower()


def test_reco_high_readiness():
    state = BehavioralState(
        performance_score=85, consistency_score=70, fatigue_score=20,
        trend_direction="up", streak_days=2, readiness_score=85,
        recommendation="",
    )
    reco = compute_recommendation(state)
    assert "pousser" in reco.lower() or "intensité" in reco.lower()


def test_reco_fallback():
    state = BehavioralState(
        performance_score=40, consistency_score=35, fatigue_score=45,
        trend_direction="stable", streak_days=1, readiness_score=45,
        recommendation="",
    )
    reco = compute_recommendation(state)
    assert "chaque" in reco.lower() or "séance" in reco.lower() or "seance" in reco.lower()


def test_behavioral_state_dataclass():
    state = BehavioralState(
        performance_score=88.0, consistency_score=71.4, fatigue_score=35.0,
        trend_direction="up", streak_days=3, readiness_score=72.0,
        recommendation="Bonne condition.",
    )
    assert state.readiness_score == 72.0
    assert state.streak_days == 3


from datetime import UTC, datetime, timedelta

from tests.helpers import get_test_user_id


def _add_completed_session(user_id, *, concentration="high", global_state="good",
                           success_score=100, n_work=2, n_done=2, started_at=None):
    """Insert a completed session with controlled inputs."""
    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    with SessionLocal() as db:
        s = WorkoutSession(
            user_id=user_id,
            template_slug_snapshot="push-a",
            template_name_snapshot="Push A",
            started_at=started_at or datetime.now(UTC),
            status="completed",
            concentration=concentration,
            global_state=global_state,
        )
        se = SessionExercise(
            exercise_code_snapshot="E1",
            exercise_name_snapshot="Ex",
            position=1,
            success_score=success_score,
        )
        for i in range(1, n_work + 1):
            se.set_logs.append(SetLog(
                kind="work", set_index=i,
                completed=(i <= n_done),
                weight_kg=60.0, reps=10,
            ))
        s.session_exercises.append(se)
        db.add(s)
        db.commit()
        return s.id


def test_compute_behavioral_state_no_sessions(client):
    from app.database import SessionLocal
    from app.services.behavioral import compute_behavioral_state

    uid = get_test_user_id()
    with SessionLocal() as db:
        state = compute_behavioral_state(db, uid)

    assert state.performance_score == 0.0
    assert state.consistency_score == 0.0
    assert state.fatigue_score == 50.0
    assert state.streak_days == 0
    assert state.trend_direction == "stable"
    assert state.readiness_score > 0
    assert len(state.recommendation) > 0


def test_compute_behavioral_state_with_sessions(client):
    from app.database import SessionLocal
    from app.services.behavioral import compute_behavioral_state

    uid = get_test_user_id()
    now = datetime.now(UTC)

    for i in range(3):
        _add_completed_session(
            uid, concentration="high", global_state="good",
            started_at=now - timedelta(days=i),
        )

    with SessionLocal() as db:
        state = compute_behavioral_state(db, uid)

    assert state.performance_score > 0
    assert state.consistency_score > 0
    assert state.fatigue_score < 50
    assert state.streak_days >= 3
    assert state.readiness_score > 50


def test_compute_behavioral_state_streak_breaks(client):
    from app.database import SessionLocal
    from app.services.behavioral import compute_behavioral_state

    uid = get_test_user_id()
    now = datetime.now(UTC)

    _add_completed_session(uid, started_at=now)
    _add_completed_session(uid, started_at=now - timedelta(days=1))
    _add_completed_session(uid, started_at=now - timedelta(days=3))

    with SessionLocal() as db:
        state = compute_behavioral_state(db, uid)

    assert state.streak_days == 2
