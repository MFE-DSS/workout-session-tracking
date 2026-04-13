"""Tests for the 5-axis dashboard service."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from app.services.dashboard import (
    AxisScore,
    DashboardResult,
    _compute_grade,
    _confidence_from_ratio,
    _trend_from_halves,
    _trend_label,
)
from tests.helpers import get_test_user_id


# ---------------------------------------------------------------------------
# Dataclass basics
# ---------------------------------------------------------------------------


def test_axis_score_creation():
    a = AxisScore(
        key="consistency",
        label="Régularité",
        score=72.5,
        trend="up",
        confidence="moyenne",
        detail="10 séances",
        active=True,
    )
    assert a.key == "consistency"
    assert a.score == 72.5
    assert a.active is True
    assert a.guidance == ""


def test_axis_score_with_guidance():
    a = AxisScore(
        key="recovery",
        label="Récupération",
        score=0,
        trend="stable",
        confidence="insuffisante",
        detail="pas de données",
        active=False,
        guidance="Remplissez le questionnaire.",
    )
    assert a.active is False
    assert a.guidance == "Remplissez le questionnaire."


def test_dashboard_result_creation():
    axes = [
        AxisScore(key="consistency", label="R", score=80, trend="up",
                  confidence="élevée", detail="ok", active=True),
    ]
    d = DashboardResult(
        global_score=80.0,
        global_grade="A",
        global_confidence="élevée",
        active_count=1,
        total_count=5,
        axes=axes,
        window_days=30,
    )
    assert d.global_score == 80.0
    assert d.total_count == 5


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def test_confidence_from_ratio_insufficient():
    assert _confidence_from_ratio(1, 5) == "insuffisante"


def test_confidence_from_ratio_faible():
    assert _confidence_from_ratio(5, 5) == "faible"


def test_confidence_from_ratio_moyenne():
    assert _confidence_from_ratio(8, 5) == "moyenne"


def test_confidence_from_ratio_elevee():
    assert _confidence_from_ratio(15, 5) == "élevée"


def test_trend_from_halves_up():
    assert _trend_from_halves(5, 7) == "up"


def test_trend_from_halves_down():
    assert _trend_from_halves(7, 5) == "down"


def test_trend_from_halves_stable():
    assert _trend_from_halves(5, 5) == "stable"


def test_trend_label():
    assert _trend_label("up") == "en hausse"
    assert _trend_label("down") == "en baisse"
    assert _trend_label("stable") == "stable"


def test_compute_grade():
    assert _compute_grade(80) == "A"
    assert _compute_grade(75) == "A"
    assert _compute_grade(60) == "B"
    assert _compute_grade(50) == "B"
    assert _compute_grade(30) == "C"


# ---------------------------------------------------------------------------
# Consistency axis
# ---------------------------------------------------------------------------


def test_consistency_with_sessions(client):
    """Consistency axis is active and has score > 0 when sessions exist."""
    from app.database import SessionLocal
    from app.models.session import WorkoutSession
    from app.services.dashboard import compute_consistency_axis

    uid = get_test_user_id()
    now = datetime.now(timezone.utc)

    with SessionLocal() as db:
        for i in range(6):
            s = WorkoutSession(
                user_id=uid,
                template_slug_snapshot="test",
                template_name_snapshot="Test",
                started_at=now - timedelta(days=i * 3),
                status="completed",
                excluded_from_stats=False,
            )
            db.add(s)
        db.commit()

        result = compute_consistency_axis(db, uid, window_days=30)

    assert result.active is True
    assert result.score > 0
    assert result.key == "consistency"
    assert result.confidence != "insuffisante"


def test_consistency_empty(client):
    """Consistency axis is inactive with no sessions."""
    from app.database import SessionLocal
    from app.services.dashboard import compute_consistency_axis

    uid = get_test_user_id()

    with SessionLocal() as db:
        result = compute_consistency_axis(db, uid, window_days=30)

    assert result.active is False
    assert result.score == 0
    assert result.confidence == "insuffisante"


# ---------------------------------------------------------------------------
# Progression axis
# ---------------------------------------------------------------------------


def test_progression_empty(client):
    """Progression axis is inactive with no training data."""
    from app.database import SessionLocal
    from app.services.dashboard import compute_progression_axis

    uid = get_test_user_id()

    with SessionLocal() as db:
        result = compute_progression_axis(db, uid, window_days=30)

    assert result.active is False
    assert result.score == 0
    assert result.key == "progression"


def test_progression_with_data(client):
    """Progression axis is active with sufficient training data."""
    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession
    from app.services.dashboard import compute_progression_axis

    uid = get_test_user_id()
    now = datetime.now(timezone.utc)

    with SessionLocal() as db:
        # Create 5 sessions with exercises in 2+ zones
        exercises = [
            ("Chest Press machine", "chest-press"),
            ("Hack Squat machine", "hack-squat"),
        ]
        for i in range(5):
            s = WorkoutSession(
                user_id=uid,
                template_slug_snapshot="test",
                template_name_snapshot="Test",
                started_at=now - timedelta(days=i * 4),
                status="completed",
                excluded_from_stats=False,
            )
            db.add(s)
            db.flush()

            for pos, (name, code) in enumerate(exercises):
                se = SessionExercise(
                    session_id=s.id,
                    exercise_code_snapshot=code,
                    exercise_name_snapshot=name,
                    position=pos,
                )
                db.add(se)
                db.flush()

                for si in range(4):
                    sl = SetLog(
                        session_exercise_id=se.id,
                        kind="work",
                        set_index=si,
                        weight_kg=60 + i * 2,
                        reps=10,
                        completed=True,
                    )
                    db.add(sl)

        db.commit()

        result = compute_progression_axis(db, uid, window_days=30)

    assert result.active is True
    assert result.score > 0
    assert result.key == "progression"


# ---------------------------------------------------------------------------
# Body trend axis
# ---------------------------------------------------------------------------


def test_body_trend_empty(client):
    """Body trend axis is inactive with no measurements."""
    from app.database import SessionLocal
    from app.services.dashboard import compute_body_trend_axis

    uid = get_test_user_id()

    with SessionLocal() as db:
        result = compute_body_trend_axis(db, uid, window_days=30)

    assert result.active is False
    assert result.score == 0
    assert result.key == "body_trend"


def test_body_trend_with_measurements(client):
    """Body trend axis is active with sufficient measurements."""
    from app.database import SessionLocal
    from app.models.measurement import BodyMeasurement
    from app.services.dashboard import compute_body_trend_axis

    uid = get_test_user_id()
    now = datetime.now(timezone.utc)

    with SessionLocal() as db:
        for i in range(4):
            m = BodyMeasurement(
                user_id=uid,
                measured_at=now - timedelta(days=(3 - i) * 7),
                chest_cm=100 + i,
                arm_cm_left=35 + i * 0.3,
                arm_cm_right=35.5 + i * 0.3,
                waist_cm=85 - i * 0.2,
                thigh_cm_left=55 + i * 0.2,
                thigh_cm_right=55.5 + i * 0.2,
            )
            db.add(m)
        db.commit()

        result = compute_body_trend_axis(db, uid, window_days=30)

    assert result.active is True
    assert result.score > 0
    assert result.key == "body_trend"


# ---------------------------------------------------------------------------
# Recovery axis
# ---------------------------------------------------------------------------


def test_recovery_empty(client):
    """Recovery axis is inactive with no readiness entries."""
    from app.database import SessionLocal
    from app.services.dashboard import compute_recovery_axis

    uid = get_test_user_id()

    with SessionLocal() as db:
        result = compute_recovery_axis(db, uid)

    assert result.active is False
    assert result.score == 0
    assert result.key == "recovery"


def test_recovery_with_entries(client):
    """Recovery axis is active with sufficient readiness data."""
    from app.database import SessionLocal
    from app.models.readiness import ReadinessEntry
    from app.services.dashboard import compute_recovery_axis

    uid = get_test_user_id()
    today = date.today()

    with SessionLocal() as db:
        for i in range(7):
            e = ReadinessEntry(
                user_id=uid,
                recorded_on=today - timedelta(days=i),
                sleep_quality=4,
                fatigue_level=3,
                soreness_level=4,
                stress_level=3,
                motivation_level=5,
            )
            db.add(e)
        db.commit()

        result = compute_recovery_axis(db, uid)

    assert result.active is True
    assert result.score > 0
    assert result.key == "recovery"
    # Mean of dims = (4+3+4+3+5)/5 = 3.8, score = (3.8-1)/4*100 = 70
    assert 65 <= result.score <= 75


# ---------------------------------------------------------------------------
# Balance axis
# ---------------------------------------------------------------------------


def test_balance_empty(client):
    """Balance axis is inactive with no training data."""
    from app.database import SessionLocal
    from app.services.dashboard import compute_balance_axis

    uid = get_test_user_id()

    with SessionLocal() as db:
        result = compute_balance_axis(db, uid, window_days=30)

    assert result.active is False
    assert result.score == 0
    assert result.key == "balance"


# ---------------------------------------------------------------------------
# Orchestrator — compute_dashboard
# ---------------------------------------------------------------------------


def test_dashboard_empty(client):
    """Dashboard with no data returns no global score."""
    from app.database import SessionLocal
    from app.services.dashboard import compute_dashboard

    uid = get_test_user_id()

    with SessionLocal() as db:
        result = compute_dashboard(db, uid, window_days=30)

    assert result.global_score is None
    assert result.global_grade == "—"
    assert result.active_count == 0
    assert result.total_count == 5
    assert len(result.axes) == 5


def test_dashboard_with_sessions_only(client):
    """Dashboard with only sessions — consistency active, rest inactive."""
    from app.database import SessionLocal
    from app.models.session import WorkoutSession
    from app.services.dashboard import compute_dashboard

    uid = get_test_user_id()
    now = datetime.now(timezone.utc)

    with SessionLocal() as db:
        for i in range(4):
            s = WorkoutSession(
                user_id=uid,
                template_slug_snapshot="test",
                template_name_snapshot="Test",
                started_at=now - timedelta(days=i * 5),
                status="completed",
                excluded_from_stats=False,
            )
            db.add(s)
        db.commit()

        result = compute_dashboard(db, uid, window_days=30)

    # At least consistency should be active
    assert result.active_count >= 1
    assert result.global_score is not None
    assert result.global_grade in ("A", "B", "C")


def test_dashboard_grade_boundaries(client):
    """Verify grade boundaries: A>=75, B>=50, C<50."""
    from app.services.dashboard import _compute_grade

    assert _compute_grade(100) == "A"
    assert _compute_grade(75) == "A"
    assert _compute_grade(74.9) == "B"
    assert _compute_grade(50) == "B"
    assert _compute_grade(49.9) == "C"
    assert _compute_grade(0) == "C"
