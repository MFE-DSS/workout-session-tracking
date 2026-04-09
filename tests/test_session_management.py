"""Sprint 8: session management, quality score, timelines."""
from __future__ import annotations
from tests.helpers import get_test_user_id

import re
from datetime import datetime, timedelta, timezone


def _start(client, slug: str = "push-a") -> int:
    r = client.post("/sessions", data={"template_slug": slug}, follow_redirects=False)
    return int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))


def _complete(client, sid: int) -> None:
    client.post(f"/sessions/{sid}", data={
        "concentration": "high", "global_state": "good",
        "bodyweight_kg": "78.5", "action": "end",
    }, follow_redirects=False)


def _fill_e2_and_complete(client, sid: int) -> None:
    from sqlalchemy import select
    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog

    with SessionLocal() as db:
        se = db.execute(
            select(SessionExercise)
            .where(SessionExercise.session_id == sid)
            .where(SessionExercise.exercise_code_snapshot == "E2")
        ).scalar_one()
        se_id = se.id
        work_ids = sorted(
            s.id for s in db.execute(
                select(SetLog).where(SetLog.session_exercise_id == se_id)
            ).scalars().all()
            if s.kind == "work"
        )

    data = {"success_score": "80", "muscle_sensation": "strong"}
    for i, wid in enumerate(work_ids, start=1):
        data[f"set_{wid}_weight_kg"] = str(60 + i)
        data[f"set_{wid}_reps"] = "10"
        data[f"set_{wid}_completed"] = "1"
        data[f"set_{wid}_execution_quality"] = "clean"
        data[f"set_{wid}_reps_target"] = "target_hit"
    client.post(f"/sessions/{sid}/exercises/{se_id}", data=data, follow_redirects=False)
    _complete(client, sid)


# ---------------------------------------------------------------------------
# Quality score (pure function)
# ---------------------------------------------------------------------------


def test_quality_score_perfect_session(client):
    """All work done, all scored 100, high concentration, good state → 100."""
    from app.services.quality_score import compute_session_quality
    from app.models.session import WorkoutSession, SessionExercise, SetLog

    s = WorkoutSession(
        template_slug_snapshot="x", template_name_snapshot="X", user_id=get_test_user_id(),
        started_at=datetime.now(timezone.utc), status="completed",
        concentration="high", global_state="good",
    )
    se = SessionExercise(
        exercise_code_snapshot="E1", exercise_name_snapshot="Ex", position=1,
        success_score=100,
    )
    se.set_logs = [
        SetLog(kind="work", set_index=1, completed=True),
        SetLog(kind="work", set_index=2, completed=True),
        SetLog(kind="warmup", set_index=1, completed=True),
    ]
    s.session_exercises = [se]
    assert compute_session_quality(s) == 100


def test_quality_score_zero_when_nothing_filled(client):
    from app.services.quality_score import compute_session_quality
    from app.models.session import WorkoutSession

    s = WorkoutSession(
        template_slug_snapshot="x", template_name_snapshot="X", user_id=get_test_user_id(),
        started_at=datetime.now(timezone.utc), status="completed",
    )
    s.session_exercises = []
    assert compute_session_quality(s) == 0


def test_quality_score_partial(client):
    """1/2 work done (20pts), score 80 (32pts), medium (6), flat (6) → 64."""
    from app.services.quality_score import compute_session_quality
    from app.models.session import WorkoutSession, SessionExercise, SetLog

    s = WorkoutSession(
        template_slug_snapshot="x", template_name_snapshot="X", user_id=get_test_user_id(),
        started_at=datetime.now(timezone.utc), status="completed",
        concentration="medium", global_state="flat",
    )
    se = SessionExercise(
        exercise_code_snapshot="E1", exercise_name_snapshot="Ex", position=1,
        success_score=80,
    )
    se.set_logs = [
        SetLog(kind="work", set_index=1, completed=True),
        SetLog(kind="work", set_index=2, completed=False),
    ]
    s.session_exercises = [se]
    assert compute_session_quality(s) == 64


# ---------------------------------------------------------------------------
# Admin page
# ---------------------------------------------------------------------------


def test_admin_sessions_page_renders(client):
    _start(client, "push-a")
    r = client.get("/admin/sessions")
    assert r.status_code == 200
    assert "Gestion des séances" in r.text
    assert "Push A" in r.text


def test_admin_sessions_shows_quality_for_completed(client):
    sid = _start(client, "push-a")
    _complete(client, sid)
    body = client.get("/admin/sessions").text
    assert "qualité" in body.lower()


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------


def test_delete_session_removes_it(client):
    sid = _start(client, "push-a")
    r = client.post(f"/admin/sessions/{sid}/delete", follow_redirects=False)
    assert r.status_code == 303

    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    with SessionLocal() as db:
        assert db.get(WorkoutSession, sid) is None


def test_delete_unknown_session_returns_404(client):
    r = client.post("/admin/sessions/99999/delete", follow_redirects=False)
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Exclude / include
# ---------------------------------------------------------------------------


def test_exclude_toggle_marks_session(client):
    sid = _start(client, "push-a")
    client.post(f"/admin/sessions/{sid}/exclude", follow_redirects=False)

    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    with SessionLocal() as db:
        assert db.get(WorkoutSession, sid).excluded_from_stats is True

    # Toggle back
    client.post(f"/admin/sessions/{sid}/exclude", follow_redirects=False)
    with SessionLocal() as db:
        assert db.get(WorkoutSession, sid).excluded_from_stats is False


def test_excluded_session_not_in_kpis(client):
    from app.database import SessionLocal
    from app.services.kpis import compute_global_kpis

    sid = _start(client, "push-a")
    _complete(client, sid)

    with SessionLocal() as db:
        k1 = compute_global_kpis(db)
        assert k1.completed_last_30 >= 1

    client.post(f"/admin/sessions/{sid}/exclude", follow_redirects=False)

    with SessionLocal() as db:
        k2 = compute_global_kpis(db)
        assert k2.completed_last_30 == 0


def test_admin_page_shows_excluded_badge(client):
    sid = _start(client, "push-a")
    client.post(f"/admin/sessions/{sid}/exclude", follow_redirects=False)
    body = client.get("/admin/sessions").text
    assert "exclu des KPI" in body
    assert "admin-row--excluded" in body


# ---------------------------------------------------------------------------
# Timelines on /progress
# ---------------------------------------------------------------------------


def test_progress_shows_no_timeline_when_no_data(client):
    body = client.get("/progress").text
    # No SVG should be rendered
    assert "<svg" not in body


def test_progress_shows_quality_timeline_when_data_exists(client):
    sid = _start(client, "push-a")
    _fill_e2_and_complete(client, sid)
    body = client.get("/progress").text
    assert "Qualité de séance" in body
    assert "<svg" in body


def test_progress_shows_bodyweight_timeline_when_bodyweight_present(client):
    sid = _start(client, "push-a")
    client.post(f"/sessions/{sid}", data={
        "concentration": "high", "global_state": "good",
        "bodyweight_kg": "78.5", "action": "end",
    }, follow_redirects=False)
    body = client.get("/progress").text
    assert "Poids corporel" in body


def test_excluded_sessions_not_in_timelines(client):
    sid = _start(client, "push-a")
    _fill_e2_and_complete(client, sid)

    # Before exclude: timeline exists
    body_before = client.get("/progress").text
    assert "Qualité de séance" in body_before

    # Exclude
    client.post(f"/admin/sessions/{sid}/exclude", follow_redirects=False)

    # After exclude: timeline should vanish (only one session, now excluded)
    body_after = client.get("/progress").text
    assert "Qualité de séance" not in body_after


def test_deleted_sessions_not_in_timelines(client):
    sid = _start(client, "push-a")
    _fill_e2_and_complete(client, sid)

    client.post(f"/admin/sessions/{sid}/delete", follow_redirects=False)
    body = client.get("/progress").text
    assert "Qualité de séance" not in body


# ---------------------------------------------------------------------------
# Home has the Gestion tile
# ---------------------------------------------------------------------------


def test_home_has_gestion_tile(client):
    body = client.get("/").text
    assert "Gestion" in body
    assert "/admin/sessions" in body


# ---------------------------------------------------------------------------
# Alembic migration exists for the new column
# ---------------------------------------------------------------------------


def test_alembic_migration_for_excluded_from_stats():
    from pathlib import Path

    versions = Path(__file__).resolve().parent.parent / "migrations" / "versions"
    files = list(versions.glob("*excluded_from_stats*.py"))
    assert len(files) >= 1, "missing migration for excluded_from_stats"
