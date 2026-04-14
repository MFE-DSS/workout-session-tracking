"""End-to-end flow tests for Sprint 1 (session creation + logging).

Covers the 12 acceptance criteria listed in the sprint spec.
"""
from __future__ import annotations

import re

from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _start_session(client: TestClient, slug: str = "push-a") -> int:
    r = client.post(
        "/sessions",
        data={"template_slug": slug},
        follow_redirects=False,
    )
    assert r.status_code == 303, r.text
    loc = r.headers["location"]
    m = re.match(r"/sessions/(\d+)", loc)
    assert m, f"unexpected redirect: {loc}"
    return int(m.group(1))


def _get_set_log_ids(client: TestClient, session_id: int) -> list[int]:
    from sqlalchemy import select
    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog

    with SessionLocal() as db:
        stmt = (
            select(SetLog.id)
            .join(SessionExercise, SessionExercise.id == SetLog.session_exercise_id)
            .where(SessionExercise.session_id == session_id)
            .order_by(SetLog.id)
        )
        return [row for row in db.execute(stmt).scalars().all()]


# ---------------------------------------------------------------------------
# 1. template selection page renders
# ---------------------------------------------------------------------------


def test_library_renders_start_forms_for_every_template(client):
    r = client.get("/library")
    assert r.status_code == 200
    body = r.text
    for slug in ["push-a", "pull-a", "push-b", "pull-b", "legs-a", "liss-abs"]:
        assert f'value="{slug}"' in body, f"missing start form for {slug}"
    # Starlette's url_for emits absolute URLs under TestClient.
    assert body.count('/sessions"') >= 6
    assert body.count("Démarrer") >= 6


# ---------------------------------------------------------------------------
# 2-5. creating a session persists rows and timestamps
# ---------------------------------------------------------------------------


def test_post_sessions_creates_and_redirects(client):
    sid = _start_session(client, "push-a")
    assert sid >= 1


def test_created_session_has_snapshots_and_started_at(client):
    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    sid = _start_session(client, "push-a")
    with SessionLocal() as db:
        s = db.get(WorkoutSession, sid)
        assert s is not None
        assert s.template_slug_snapshot == "push-a"
        assert s.template_name_snapshot.startswith("Push A")
        assert s.started_at is not None
        assert s.status == "in_progress"


def test_created_session_has_one_session_exercise_per_template_exercise(client):
    from app.database import SessionLocal
    from app.models.session import SessionExercise

    sid = _start_session(client, "push-a")
    with SessionLocal() as db:
        ses = db.query(SessionExercise).filter(SessionExercise.session_id == sid).all()
        # Push A has 8 exercises
        assert len(ses) == 8
        codes = sorted(se.exercise_code_snapshot for se in ses)
        assert codes == sorted(["E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8"])


def test_created_session_pre_populates_warmup_and_work_sets(client):
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog

    sid = _start_session(client, "push-a")
    with SessionLocal() as db:
        # Exercise 1 (E1 Incline Smith Press, 3 rep targets): expect 2 warmup + 3 work
        se = db.execute(
            select(SessionExercise)
            .where(SessionExercise.session_id == sid)
            .where(SessionExercise.exercise_code_snapshot == "E1")
        ).scalar_one()
        sets = db.execute(
            select(SetLog).where(SetLog.session_exercise_id == se.id)
        ).scalars().all()
        warmups = [s for s in sets if s.kind == "warmup"]
        work = [s for s in sets if s.kind == "work"]
        assert len(warmups) == 2
        assert len(work) == 3
        assert all(s.completed is False for s in sets)


def test_create_session_with_unknown_template_returns_404(client):
    r = client.post(
        "/sessions", data={"template_slug": "nope"}, follow_redirects=False
    )
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# 6. session detail renders persisted content
# ---------------------------------------------------------------------------


def test_session_detail_renders_full_tree(client):
    sid = _start_session(client, "push-a")
    r = client.get(f"/sessions/{sid}")
    assert r.status_code == 200
    body = r.text
    assert "Push A" in body
    # Weekday label derived from started_at
    assert any(d in body for d in ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"])
    # All 8 exercise cards are rendered
    for code in ["E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8"]:
        assert code in body
    # Session feedback form present
    assert 'name="concentration"' in body
    assert 'name="global_state"' in body
    assert 'name="bodyweight_kg"' in body
    assert "En cours" in body
    # Method reminder present
    assert "Rappel méthode" in body


def test_session_detail_for_unknown_id_returns_404(client):
    r = client.get("/sessions/99999")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# 7. session-level update persists
# ---------------------------------------------------------------------------


def test_session_level_update_persists(client):
    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    sid = _start_session(client, "push-a")

    r = client.post(
        f"/sessions/{sid}",
        data={
            "concentration": "high",
            "global_state": "good",
            "bodyweight_kg": "78.5",
            "free_note": "solide, focus pec",
        },
        follow_redirects=False,
    )
    assert r.status_code == 303

    with SessionLocal() as db:
        s = db.get(WorkoutSession, sid)
        assert s.concentration == "high"
        assert s.global_state == "good"
        assert s.bodyweight_kg == 78.5
        assert s.free_note == "solide, focus pec"
        assert s.status == "in_progress"
        assert s.ended_at is None


def test_session_end_action_sets_status_and_ended_at(client):
    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    sid = _start_session(client, "push-a")
    client.post(
        f"/sessions/{sid}",
        data={
            "concentration": "medium",
            "global_state": "flat",
            "action": "end",
        },
        follow_redirects=False,
    )

    with SessionLocal() as db:
        s = db.get(WorkoutSession, sid)
        assert s.status == "completed"
        assert s.ended_at is not None


def test_invalid_enum_values_are_dropped_silently(client):
    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    sid = _start_session(client, "push-a")
    client.post(
        f"/sessions/{sid}",
        data={"concentration": "EXTREME", "global_state": "nuclear"},
        follow_redirects=False,
    )
    with SessionLocal() as db:
        s = db.get(WorkoutSession, sid)
        assert s.concentration is None
        assert s.global_state is None


# ---------------------------------------------------------------------------
# 8. exercise-level update persists
# ---------------------------------------------------------------------------


def test_exercise_card_update_persists_feedback_and_sets(client):
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
        sets = db.execute(
            select(SetLog).where(SetLog.session_exercise_id == se_id).order_by(SetLog.id)
        ).scalars().all()
        warmups = [s for s in sets if s.kind == "warmup"]
        work = [s for s in sets if s.kind == "work"]

    # Fill the card: 1 warmup done, all 3 work sets done with values
    data = {
        "muscle_sensation": "strong",
        "free_note": "belle contraction",
        # warmup #1: weight+reps, completed
        f"set_{warmups[0].id}_weight_kg": "20",
        f"set_{warmups[0].id}_reps": "10",
        f"set_{warmups[0].id}_completed": "1",
        # work #1
        f"set_{work[0].id}_weight_kg": "60",
        f"set_{work[0].id}_reps": "10",
        f"set_{work[0].id}_completed": "1",
        # work #2
        f"set_{work[1].id}_weight_kg": "62.5",
        f"set_{work[1].id}_reps": "8",
        f"set_{work[1].id}_completed": "1",
        # work #3
        f"set_{work[2].id}_weight_kg": "55",
        f"set_{work[2].id}_reps": "12",
        f"set_{work[2].id}_completed": "1",
    }

    r = client.post(
        f"/sessions/{sid}/exercises/{se_id}",
        data=data,
        follow_redirects=False,
    )
    assert r.status_code == 303

    with SessionLocal() as db:
        se2 = db.get(SessionExercise, se_id)
        assert se2.success_score in {100, 80, 50}  # derived by compute_success_score
        assert se2.muscle_sensation == "strong"
        assert se2.free_note == "belle contraction"

        sets_after = db.execute(
            select(SetLog)
            .where(SetLog.session_exercise_id == se_id)
            .order_by(SetLog.id)
        ).scalars().all()
        # Warmup #1 is stored
        w1 = next(s for s in sets_after if s.id == warmups[0].id)
        assert w1.completed is True
        assert w1.weight_kg == 20.0
        assert w1.reps == 10
        # Work sets are stored with normalized selectors
        for wk in sets_after:
            if wk.kind != "work":
                continue
            assert wk.completed is True
            assert wk.weight_kg is not None
            assert wk.reps is not None
            # execution_quality and reps_target are no longer sent via form
            assert wk.execution_quality is None
            assert wk.reps_target is None


# ---------------------------------------------------------------------------
# 9. set-level values persist (covered above, also assert reload)
# 12. values preserved after reload
# ---------------------------------------------------------------------------


def test_values_are_preserved_after_reload_via_http(client):
    sid = _start_session(client, "push-a")
    client.post(
        f"/sessions/{sid}",
        data={
            "concentration": "low",
            "global_state": "fatigued",
            "bodyweight_kg": "77.2",
            "free_note": "seance calme",  # no apostrophe -> no HTML escape noise
        },
        follow_redirects=False,
    )
    r = client.get(f"/sessions/{sid}")
    assert r.status_code == 200
    body = r.text
    # The bodyweight_kg value must be echoed back
    assert 'value="77.2"' in body
    # The free note must be echoed back
    assert "seance calme" in body
    # The low / fatigued radios must be checked
    assert re.search(r'value="low"[^>]*checked', body)
    assert re.search(r'value="fatigued"[^>]*checked', body)


# ---------------------------------------------------------------------------
# 10. history lists created sessions
# ---------------------------------------------------------------------------


def test_history_lists_created_sessions(client):
    _start_session(client, "push-a")
    _start_session(client, "legs-a")
    r = client.get("/history")
    assert r.status_code == 200
    body = r.text
    assert "Push A" in body
    assert "Legs A" in body
    # At least 2 session cards with status badges
    assert body.count("en cours") >= 2


# ---------------------------------------------------------------------------
# 11. resume behaviour
# ---------------------------------------------------------------------------


def test_home_offers_resume_when_an_open_session_exists(client):
    sid = _start_session(client, "push-a")

    # No resume yet on a fresh home? Actually there IS because we just created one.
    r = client.get("/")
    assert r.status_code == 200
    body = r.text
    assert "Reprendre" in body
    assert f"/sessions/{sid}" in body

    # End the session, resume tile should disappear
    client.post(
        f"/sessions/{sid}",
        data={"action": "end"},
        follow_redirects=False,
    )
    r = client.get("/")
    assert "Reprendre" not in r.text


# ---------------------------------------------------------------------------
# Rules page + seed
# ---------------------------------------------------------------------------


def test_science_page_renders_seeded_rules(client):
    r = client.get("/science")
    assert r.status_code == 200
    body = r.text
    assert "Science" in body
    # Apostrophes get HTML-escaped by Jinja — match a title that doesn't contain any.
    assert "Surcharge progressive" in body or "Plages de répétitions" in body


def test_session_detail_shows_inline_method_reminder_link(client):
    sid = _start_session(client, "push-a")
    r = client.get(f"/sessions/{sid}")
    body = r.text
    assert "Voir toutes les règles" in body
    assert "/rules" in body
