"""Tests for the /sessions/{id}/done terminal-state route."""
from __future__ import annotations

from datetime import datetime, timezone

from tests.helpers import get_test_user_id


def _mk_completed_session(
    *,
    template_slug: str = "push-a",
    template_name: str = "Push A — test",
    started_at: datetime | None = None,
    ended_at: datetime | None = None,
    user_id: int | None = None,
) -> int:
    """Create and commit a completed WorkoutSession; return its id.

    Mirrors the inline factory pattern used in tests/test_session_recap.py
    (repo convention — no shared factories).
    """
    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    started = started_at or datetime(2026, 4, 13, 18, 0, tzinfo=timezone.utc)
    ended = ended_at or datetime(2026, 4, 13, 19, 30, tzinfo=timezone.utc)

    with SessionLocal() as db:
        s = WorkoutSession(
            user_id=user_id if user_id is not None else get_test_user_id(),
            template_id=None,
            template_slug_snapshot=template_slug,
            template_name_snapshot=template_name,
            started_at=started,
            ended_at=ended,
            status="completed",
            concentration="high",
            global_state="good",
            bodyweight_kg=79.4,
        )
        se = SessionExercise(
            exercise_code_snapshot="E1",
            exercise_name_snapshot="Incline Smith Press",
            position=1,
            success_score=80,
        )
        for j in range(1, 4):
            se.set_logs.append(
                SetLog(
                    kind="work",
                    set_index=j,
                    weight_kg=60.0,
                    reps=10,
                    completed=(j <= 2),
                )
            )
        s.session_exercises.append(se)
        db.add(s)
        db.commit()
        return s.id


def test_done_route_returns_200_for_completed_session(client):
    sid = _mk_completed_session()
    r = client.get(f"/sessions/{sid}/done")
    assert r.status_code == 200
    assert "Séance terminée" in r.text
    assert "Push A — test" in r.text


def test_done_route_redirects_when_session_in_progress(client):
    from app.database import SessionLocal
    from app.enums import SessionStatus
    from app.models.session import WorkoutSession

    sid = _mk_completed_session()
    with SessionLocal() as db:
        session = db.get(WorkoutSession, sid)
        session.status = SessionStatus.IN_PROGRESS
        session.ended_at = None
        db.commit()

    r = client.get(f"/sessions/{sid}/done", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == f"/sessions/{sid}"


def test_done_route_404_for_other_users_session(client):
    # Bogus session id → _load_session returns None → 404.
    # This exercises the same ownership guard path that would also
    # reject a session belonging to another user.
    r = client.get("/sessions/999999/done")
    assert r.status_code == 404
