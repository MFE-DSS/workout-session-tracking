"""Sb_24.3 — hook of implicit label persistence at session completion.

Hard contracts validated:
* On status transition → completed: each session_exercise with ≥3 work
  sets gets an implicit_label persisted + a computed_at timestamp.
* scoring_version bumped to 2 on the session.
* Idempotent — re-finishing a session doesn't re-touch labels.
* Sessions with < 3 work sets keep implicit_label=None.
* Reopening a session does NOT clear or downgrade anything (the labels
  freeze at first completion; scoring_version stays at 2).
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select


def _create_session_with_sets(client, template_slug: str = "push-a"):
    """Create a session via the real handler so set_logs are seeded by
    SessionBuilder. Returns (session_id, list_of_session_exercise_ids)."""
    r = client.post(
        "/sessions",
        data={"template_slug": template_slug},
        follow_redirects=False,
    )
    assert r.status_code == 303, r.text
    session_id = int(r.headers["location"].rsplit("/", 1)[-1])

    from app.database import SessionLocal
    from app.models.session import WorkoutSession
    from sqlalchemy.orm import selectinload

    with SessionLocal() as db:
        s = db.execute(
            select(WorkoutSession)
            .where(WorkoutSession.id == session_id)
            .options(
                selectinload(WorkoutSession.session_exercises)
            )
        ).scalar_one()
        se_ids = [se.id for se in s.session_exercises]
    return session_id, se_ids


def _log_work_sets(session_id: int, se_id: int, sets: list[tuple[float, int]]):
    """Write work sets directly via the DB layer (the form layer is
    less convenient for parametrising). Marks every set as completed."""
    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog
    from sqlalchemy.orm import selectinload

    with SessionLocal() as db:
        se = db.execute(
            select(SessionExercise)
            .where(SessionExercise.id == se_id)
            .options(selectinload(SessionExercise.set_logs))
        ).scalar_one()
        # Remove existing work sets (test idempotence)
        for sl in list(se.set_logs):
            if sl.kind == "work":
                db.delete(sl)
        db.flush()
        for idx, (w, r) in enumerate(sets, start=1):
            db.add(SetLog(
                session_exercise_id=se_id,
                kind="work",
                set_index=idx,
                weight_kg=w,
                reps=r,
                completed=True,
            ))
        db.commit()


def _finish_session(client, session_id: int):
    """POST the session-level form with action=end — the real path."""
    r = client.post(
        f"/sessions/{session_id}",
        data={"action": "end"},
        follow_redirects=False,
    )
    return r


# ---------------------------------------------------------------------------
# Happy path — label persisted, scoring_version bumped
# ---------------------------------------------------------------------------


def test_completion_persists_label_for_3plus_work_sets(client):
    sid, se_ids = _create_session_with_sets(client)
    # On the first exercise, log a clear "trajectoire_coherente" pattern
    _log_work_sets(sid, se_ids[0], [(80, 10), (80, 8), (80, 6)])
    r = _finish_session(client, sid)
    assert r.status_code == 303

    from app.database import SessionLocal
    from app.models.session import SessionExercise, WorkoutSession
    with SessionLocal() as db:
        s = db.execute(
            select(WorkoutSession).where(WorkoutSession.id == sid)
        ).scalar_one()
        assert s.scoring_version == 2
        se = db.execute(
            select(SessionExercise).where(SessionExercise.id == se_ids[0])
        ).scalar_one()
        assert se.implicit_label == "trajectoire_coherente"
        assert se.implicit_label_computed_at is not None


def test_completion_no_label_for_under_3_work_sets(client):
    sid, se_ids = _create_session_with_sets(client)
    _log_work_sets(sid, se_ids[0], [(80, 10), (80, 8)])  # only 2 sets
    _finish_session(client, sid)

    from app.database import SessionLocal
    from app.models.session import SessionExercise
    with SessionLocal() as db:
        se = db.execute(
            select(SessionExercise).where(SessionExercise.id == se_ids[0])
        ).scalar_one()
        assert se.implicit_label is None


def test_reserve_probable_persisted_for_flat_3x10(client):
    sid, se_ids = _create_session_with_sets(client)
    _log_work_sets(sid, se_ids[0], [(60, 10), (60, 10), (60, 10)])
    _finish_session(client, sid)

    from app.database import SessionLocal
    from app.models.session import SessionExercise
    with SessionLocal() as db:
        se = db.execute(
            select(SessionExercise).where(SessionExercise.id == se_ids[0])
        ).scalar_one()
        assert se.implicit_label == "reserve_probable"


# ---------------------------------------------------------------------------
# Idempotence — re-finish does not re-touch
# ---------------------------------------------------------------------------


def test_re_finish_keeps_first_label_intact(client):
    sid, se_ids = _create_session_with_sets(client)
    _log_work_sets(sid, se_ids[0], [(80, 10), (80, 8), (80, 6)])
    _finish_session(client, sid)

    # Capture computed_at after first finish
    from app.database import SessionLocal
    from app.models.session import SessionExercise, WorkoutSession
    with SessionLocal() as db:
        se = db.execute(
            select(SessionExercise).where(SessionExercise.id == se_ids[0])
        ).scalar_one()
        first_label = se.implicit_label
        first_ts = se.implicit_label_computed_at
        assert first_label == "trajectoire_coherente"

    # Mutate the work sets to a pattern that would yield a DIFFERENT label
    _log_work_sets(sid, se_ids[0], [(60, 10), (60, 10), (60, 10)])
    # Reopen then re-end
    client.post(
        f"/sessions/{sid}",
        data={"action": "reopen"},
        follow_redirects=False,
    )
    _finish_session(client, sid)

    with SessionLocal() as db:
        se = db.execute(
            select(SessionExercise).where(SessionExercise.id == se_ids[0])
        ).scalar_one()
        # Label is FROZEN at the first completion (Sx_24 §C, §D.2 contract)
        assert se.implicit_label == first_label
        assert se.implicit_label_computed_at == first_ts


def test_scoring_version_never_downgraded_on_reopen(client):
    sid, _ = _create_session_with_sets(client)
    _finish_session(client, sid)

    from app.database import SessionLocal
    from app.models.session import WorkoutSession
    with SessionLocal() as db:
        s = db.execute(
            select(WorkoutSession).where(WorkoutSession.id == sid)
        ).scalar_one()
        assert s.scoring_version == 2

    # Reopen
    client.post(
        f"/sessions/{sid}",
        data={"action": "reopen"},
        follow_redirects=False,
    )
    with SessionLocal() as db:
        s = db.execute(
            select(WorkoutSession).where(WorkoutSession.id == sid)
        ).scalar_one()
        # Reopen does NOT downgrade scoring_version
        assert s.scoring_version == 2


# ---------------------------------------------------------------------------
# Multi-exercise — every eligible SE gets its own label independently
# ---------------------------------------------------------------------------


def test_multi_exercise_each_gets_own_label(client):
    sid, se_ids = _create_session_with_sets(client)
    # First exo: trajectoire_coherente
    _log_work_sets(sid, se_ids[0], [(80, 10), (80, 8), (80, 6)])
    # Second exo: reserve_probable
    _log_work_sets(sid, se_ids[1], [(60, 10), (60, 10), (60, 10)])
    # Third exo: only 2 sets → no label
    _log_work_sets(sid, se_ids[2], [(50, 12), (50, 10)])
    _finish_session(client, sid)

    from app.database import SessionLocal
    from app.models.session import SessionExercise
    with SessionLocal() as db:
        e0 = db.execute(
            select(SessionExercise).where(SessionExercise.id == se_ids[0])
        ).scalar_one()
        e1 = db.execute(
            select(SessionExercise).where(SessionExercise.id == se_ids[1])
        ).scalar_one()
        e2 = db.execute(
            select(SessionExercise).where(SessionExercise.id == se_ids[2])
        ).scalar_one()
        assert e0.implicit_label == "trajectoire_coherente"
        assert e1.implicit_label == "reserve_probable"
        assert e2.implicit_label is None
