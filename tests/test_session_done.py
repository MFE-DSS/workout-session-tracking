"""Tests for the /sessions/{id}/done terminal-state route."""
from __future__ import annotations

from datetime import UTC, datetime

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

    started = started_at or datetime(2026, 4, 13, 18, 0, tzinfo=UTC)
    ended = ended_at or datetime(2026, 4, 13, 19, 30, tzinfo=UTC)

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


def test_action_end_redirects_to_done(client):
    from app.database import SessionLocal
    from app.enums import SessionStatus
    from app.models.session import WorkoutSession

    sid = _mk_completed_session()
    # Downgrade to in_progress so action=end transitions it.
    with SessionLocal() as db:
        session = db.get(WorkoutSession, sid)
        session.status = SessionStatus.IN_PROGRESS
        session.ended_at = None
        db.commit()

    r = client.post(
        f"/sessions/{sid}",
        data={"action": "end"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert r.headers["location"] == f"/sessions/{sid}/done"


def test_action_reopen_redirects_to_editable_session(client):
    sid = _mk_completed_session()  # already status=completed
    r = client.post(
        f"/sessions/{sid}",
        data={"action": "reopen"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert r.headers["location"] == f"/sessions/{sid}"


def test_get_session_completed_redirects_to_done(client):
    sid = _mk_completed_session()
    r = client.get(f"/sessions/{sid}", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == f"/sessions/{sid}/done"


def test_get_session_in_progress_renders_normally(client):
    from app.database import SessionLocal
    from app.enums import SessionStatus
    from app.models.session import WorkoutSession

    sid = _mk_completed_session()
    with SessionLocal() as db:
        s = db.get(WorkoutSession, sid)
        s.status = SessionStatus.IN_PROGRESS
        s.ended_at = None
        db.commit()

    r = client.get(f"/sessions/{sid}")
    assert r.status_code == 200
    # Editable = session-feedback form visible on the page
    assert "session-feedback" in r.text


def test_done_page_shows_summary_block(client):
    sid = _mk_completed_session()
    r = client.get(f"/sessions/{sid}/done")
    assert r.status_code == 200
    body = r.text
    # Summary: factory creates 1 exo × 3 sets with 2/3 completed.
    assert "Work sets" in body
    assert "2 / 3" in body
    assert "79,4" in body or "79.4" in body  # bodyweight
    # Per-exercise line
    assert "E1" in body
    assert "Incline Smith Press" in body
    assert "2/3" in body
    # CTAs
    # Sb_27.6 — /dashboard deprecated → no more dashboard CTA on /done.
    # The session review now exposes its own CTAs (Retour Accueil /
    # Nouvelle séance) plus the existing Historique link in nav.
    assert 'href="/history"' in body or "Historique" in body
    # Reopen form (discreet)
    assert "Rouvrir" in body
    assert f"/sessions/{sid}" in body
    assert 'name="action" value="reopen"' in body


def _mk_completed_cardio_session(
    *,
    duration_min: int = 45,
    bpm_avg: int = 132,
    machine_calories: int = 410,
    machine_type: str = "stairmaster",
) -> int:
    """Create a completed cardio WorkoutSession (inline cardio template)."""
    from app.database import SessionLocal
    from app.models.catalog import WorkoutTemplate
    from app.models.session import WorkoutSession

    started = datetime(2026, 4, 13, 18, 0, tzinfo=UTC)
    ended = datetime(2026, 4, 13, 18, 0 + duration_min, tzinfo=UTC)

    with SessionLocal() as db:
        tpl = WorkoutTemplate(
            slug="cardio-liss-test",
            name="Cardio LISS — test",
            kind="cardio",
        )
        db.add(tpl)
        db.flush()
        s = WorkoutSession(
            user_id=get_test_user_id(),
            template_id=tpl.id,
            template_slug_snapshot=tpl.slug,
            template_name_snapshot=tpl.name,
            started_at=started,
            ended_at=ended,
            status="completed",
            cardio_duration_min=duration_min,
            cardio_bpm_avg=bpm_avg,
            cardio_machine_calories=machine_calories,
            cardio_machine_type=machine_type,
        )
        db.add(s)
        db.commit()
        return s.id


def test_done_page_shows_cardio_recap_for_cardio_kind(client):
    sid = _mk_completed_cardio_session()
    r = client.get(f"/sessions/{sid}/done")
    assert r.status_code == 200
    body = r.text
    # Cardio block rendered
    assert "Cardio" in body
    assert "45" in body and "min" in body.lower()
    assert "132" in body
    assert "bpm" in body.lower()
    assert "410" in body
    assert "stairmaster" in body
    # Strength table must NOT render
    assert "Par exercice" not in body


def test_done_page_shows_substitution_arrow(client):
    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    sid = _mk_completed_session()
    with SessionLocal() as db:
        session = db.get(WorkoutSession, sid)
        session.session_exercises[0].substituted_name = "Développé couché haltères"
        db.commit()

    r = client.get(f"/sessions/{sid}/done")
    assert r.status_code == 200
    assert "Développé couché haltères" in r.text
    assert "→" in r.text


def test_done_page_shows_confidence_badge(client):
    sid = _mk_completed_session()
    r = client.get(f"/sessions/{sid}/done")
    assert r.status_code == 200
    body = r.text
    assert "Confiance du logging" in body
    assert "confidence-badge" in body


def test_done_page_shows_zones_block(client):
    """Incline Smith Press + Chest Press machine → zone pecs detected."""
    sid = _mk_completed_session()
    r = client.get(f"/sessions/{sid}/done")
    assert "Zones sollicitées" in r.text
    assert "Pectoraux" in r.text


def test_done_page_shows_anomalies_when_present(client):
    """Inject a completed-empty set so rule A fires and 'À vérifier' renders."""
    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    sid = _mk_completed_session()
    with SessionLocal() as db:
        session = db.get(WorkoutSession, sid)
        # Mark the third set (currently uncompleted) as completed-empty.
        se = session.session_exercises[0]
        work = sorted(
            [sl for sl in se.set_logs if sl.kind == "work"],
            key=lambda s: s.set_index,
        )
        work[-1].completed = True
        work[-1].weight_kg = None
        work[-1].reps = None
        db.commit()

    r = client.get(f"/sessions/{sid}/done")
    body = r.text
    assert "À vérifier" in body
    assert "sans reps ni charge" in body
