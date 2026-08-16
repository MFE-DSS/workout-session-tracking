"""Tests for leaderboard grade badge and tooltip."""
from __future__ import annotations

from datetime import UTC, datetime

from tests.helpers import get_test_user_id


def _add_session(user_id, *, quality_inputs, n_work=2, n_done=2):
    """Insert a completed session with controlled quality inputs."""
    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    with SessionLocal() as db:
        s = WorkoutSession(
            user_id=user_id,
            template_slug_snapshot="push-a",
            template_name_snapshot="Push A",
            started_at=datetime.now(UTC),
            status="completed",
            concentration=quality_inputs.get("concentration"),
            global_state=quality_inputs.get("global_state"),
        )
        se = SessionExercise(
            exercise_code_snapshot="E1",
            exercise_name_snapshot="Ex",
            position=1,
            success_score=quality_inputs.get("success_score"),
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


def test_leaderboard_shows_grade_badge(client):
    uid = get_test_user_id()
    _add_session(uid, quality_inputs={
        "concentration": "high", "global_state": "good", "success_score": 100,
    })
    body = client.get("/leaderboard").text
    assert "grade-badge" in body


def test_leaderboard_tooltip_has_tabindex(client):
    """Tooltip wrapper must have tabindex=0 for mobile accessibility."""
    uid = get_test_user_id()
    _add_session(uid, quality_inputs={
        "concentration": "high", "global_state": "good", "success_score": 100,
    })
    body = client.get("/leaderboard").text
    assert 'tabindex="0"' in body


def test_leaderboard_tooltip_content(client):
    uid = get_test_user_id()
    _add_session(uid, quality_inputs={
        "concentration": "high", "global_state": "good", "success_score": 100,
    })
    body = client.get("/leaderboard").text
    assert "tooltip-content" in body
    assert "Derni" in body  # "Dernière session"
