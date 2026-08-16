"""Sprint 3 readability improvements on past sessions + /progress."""
from __future__ import annotations

import re
from datetime import UTC

from tests.helpers import get_test_user_id


def _start_session(client, slug="push-a") -> int:
    r = client.post("/sessions", data={"template_slug": slug}, follow_redirects=False)
    return int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))


def test_in_progress_session_has_no_completed_marker(client):
    sid = _start_session(client, "push-a")
    body = client.get(f"/sessions/{sid}").text
    assert "session-page--completed" not in body
    # Banner note only shows once the session has been terminated.
    assert "Séance terminée" not in body


# NOTE (Sb_R3): the former tests
#   - test_completed_session_has_readability_markers
#   - test_completed_session_shows_per_card_summary_when_work_sets_filled
# asserted against the completed-mode render of session_detail.html.
# That rendering no longer happens: completed sessions now redirect to
# /sessions/{id}/done (dedicated recap template). Equivalent coverage
# lives in tests/test_session_done.py. Task 5 will strengthen the recap
# assertions (per-exercise work set counts, weights_str).


def test_progress_page_has_exercise_activity_section(client):
    r = client.get("/progress")
    assert r.status_code == 200
    body = r.text
    assert "Activité récente par exercice" in body


def test_progress_exercise_activity_shows_completed_exercises(client):
    from datetime import datetime, timedelta

    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    with SessionLocal() as db:
        s = WorkoutSession(
            template_slug_snapshot="push-a",
            template_name_snapshot="Push A", user_id=get_test_user_id(),
            started_at=datetime.now(UTC) - timedelta(days=2),
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
    from datetime import datetime

    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    with SessionLocal() as db:
        s = WorkoutSession(
            template_slug_snapshot="legs",
            template_name_snapshot="Legs", user_id=get_test_user_id(),
            started_at=datetime.now(UTC),
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
