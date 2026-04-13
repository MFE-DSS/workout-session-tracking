"""Sprint 3 readability improvements on past sessions + /progress."""
from __future__ import annotations
from tests.helpers import get_test_user_id

import re


def _start_session(client, slug="push-a") -> int:
    r = client.post("/sessions", data={"template_slug": slug}, follow_redirects=False)
    return int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))


def test_in_progress_session_has_no_completed_marker(client):
    sid = _start_session(client, "push-a")
    body = client.get(f"/sessions/{sid}").text
    assert "session-page--completed" not in body
    # Banner note only shows once the session has been terminated.
    assert "Séance terminée" not in body


def test_completed_session_has_readability_markers(client):
    sid = _start_session(client, "push-a")
    # End it immediately
    client.post(
        f"/sessions/{sid}", data={"action": "end"}, follow_redirects=False
    )
    body = client.get(f"/sessions/{sid}").text
    assert "session-page--completed" in body
    assert "Séance terminée" in body
    # Badge shows Terminée, button becomes Rouvrir
    assert "Terminée" in body
    assert "Rouvrir" in body


def test_completed_session_shows_per_card_summary_when_work_sets_filled(client):
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog

    sid = _start_session(client, "push-a")
    with SessionLocal() as db:
        se = db.execute(
            select(SessionExercise)
            .where(SessionExercise.session_id == sid)
            .where(SessionExercise.exercise_code_snapshot == "E2")
        ).scalar_one()
        se_id = se.id
        work_ids = [
            s.id for s in db.execute(
                select(SetLog)
                .where(SetLog.session_exercise_id == se_id)
            ).scalars().all()
            if s.kind == "work"
        ]

    data = {"muscle_sensation": "strong"}
    for i, wid in enumerate(sorted(work_ids), start=1):
        data[f"set_{wid}_weight_kg"] = str(60 + i)
        data[f"set_{wid}_reps"] = "10"
        data[f"set_{wid}_completed"] = "1"
    client.post(f"/sessions/{sid}/exercises/{se_id}", data=data)
    client.post(f"/sessions/{sid}", data={"action": "end"})

    body = client.get(f"/sessions/{sid}").text
    assert "done-summary" in body
    assert "Work : 3/3" in body
    assert "61 / 62 / 63 kg" in body
    assert "score 80" in body


def test_progress_page_has_exercise_activity_section(client):
    r = client.get("/progress")
    assert r.status_code == 200
    body = r.text
    assert "Activité récente par exercice" in body


def test_progress_exercise_activity_shows_completed_exercises(client):
    from datetime import datetime, timedelta, timezone

    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    with SessionLocal() as db:
        s = WorkoutSession(
            template_slug_snapshot="push-a",
            template_name_snapshot="Push A", user_id=get_test_user_id(),
            started_at=datetime.now(timezone.utc) - timedelta(days=2),
            status="completed",
        )
        se = SessionExercise(
            exercise_code_snapshot="E2",
            exercise_name_snapshot="Incline Smith Chest Press",
            position=2,
            success_score=80,
        )
        se.set_logs.append(
            SetLog(kind="work", set_index=1, weight_kg=62.5, reps=10, completed=True)
        )
        se.set_logs.append(
            SetLog(kind="work", set_index=2, weight_kg=60.0, reps=8, completed=True)
        )
        s.session_exercises.append(se)
        db.add(s)
        db.commit()

    body = client.get("/progress").text
    # Activity row content
    assert "Incline Smith" in body
    assert "62.5 / 60 kg" in body
    assert "10 / 8 reps" in body
    assert "1×" in body  # single session in the 30d window


def test_progress_exercise_activity_ignores_in_progress_sessions(client):
    from datetime import datetime, timezone

    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    with SessionLocal() as db:
        s = WorkoutSession(
            template_slug_snapshot="legs",
            template_name_snapshot="Legs", user_id=get_test_user_id(),
            started_at=datetime.now(timezone.utc),
            status="in_progress",  # should NOT surface
        )
        se = SessionExercise(
            exercise_code_snapshot="E1",
            exercise_name_snapshot="Relevés des mollets debout",
            position=1,
        )
        se.set_logs.append(
            SetLog(kind="work", set_index=1, weight_kg=100.0, reps=10, completed=True)
        )
        s.session_exercises.append(se)
        db.add(s)
        db.commit()

    body = client.get("/progress").text
    assert "Relevés des mollets" not in body
