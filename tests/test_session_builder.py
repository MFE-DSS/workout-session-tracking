"""Tests for the session builder — the Sprint 1 foundation.

Validates that `instantiate_session` produces a fully pre-populated
session tree that the mobile UI can just iterate over and tap-fill.
"""
from __future__ import annotations

from datetime import UTC, datetime


def _get_template(slug: str):
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    from app.database import SessionLocal
    from app.models.catalog import TemplateExercise, WorkoutTemplate

    with SessionLocal() as db:
        stmt = (
            select(WorkoutTemplate)
            .where(WorkoutTemplate.slug == slug)
            .options(
                selectinload(WorkoutTemplate.exercises).selectinload(
                    TemplateExercise.rep_targets
                )
            )
        )
        return db, db.execute(stmt).scalar_one()


def test_builder_prepopulates_warmup_and_work_rows(client):
    from app.services.session_builder import instantiate_session

    db, tpl = _get_template("push-a")
    with db:
        # Push A has 7 exercises (v10: E8 removed for 1h15 budget).
        session = instantiate_session(db, tpl, datetime(2026, 1, 5, 18, 0, tzinfo=UTC))
        db.commit()
        db.refresh(session)

        assert len(session.session_exercises) == 7
        assert session.template_slug_snapshot == "push-a"
        assert session.template_name_snapshot.startswith("Push A")

        # Exercise 1 (Incline Smith Press): 3 rep targets -> 3 work + 2 warmup
        ex1 = session.session_exercises[0]
        assert ex1.exercise_code_snapshot == "E1"
        warmups = [s for s in ex1.set_logs if s.kind == "warmup"]
        works = [s for s in ex1.set_logs if s.kind == "work"]
        assert len(warmups) == 2
        assert len(works) == 3
        assert [s.set_index for s in warmups] == [1, 2]
        assert [s.set_index for s in works] == [1, 2, 3]

        # Exercise 2 (Chest Press machine): 3 rep targets -> 3 work + 2 warmup
        ex2 = session.session_exercises[1]
        works2 = [s for s in ex2.set_logs if s.kind == "work"]
        assert len(works2) == 3

        # Every pre-created row is unticked and empty
        for se in session.session_exercises:
            for sl in se.set_logs:
                assert sl.completed is False
                assert sl.weight_kg is None
                assert sl.reps is None
                assert sl.execution_quality is None
                assert sl.reps_target is None

        db.delete(session)
        db.commit()


def test_builder_allows_custom_warmup_count(client):
    from app.services.session_builder import instantiate_session

    db, tpl = _get_template("legs-a")
    with db:
        session = instantiate_session(
            db, tpl, datetime(2026, 2, 14, 9, 0, tzinfo=UTC), warmup_sets=1
        )
        db.commit()

        first = session.session_exercises[0]
        warmups = [s for s in first.set_logs if s.kind == "warmup"]
        assert len(warmups) == 1

        db.delete(session)
        db.commit()


def test_builder_handles_cardio_template_with_no_exercises(client):
    from app.services.session_builder import instantiate_session

    db, tpl = _get_template("liss-abs")
    with db:
        session = instantiate_session(
            db, tpl, datetime(2026, 2, 15, 7, 0, tzinfo=UTC)
        )
        db.commit()
        db.refresh(session)

        assert len(session.session_exercises) == 4
        assert session.template_slug_snapshot == "liss-abs"

        db.delete(session)
        db.commit()


def test_warmup_and_work_sets_can_share_set_index(client):
    """The composite UNIQUE (session_exercise_id, kind, set_index)
    must allow warmup#1 and work#1 to coexist on the same exercise."""
    from sqlalchemy import select

    from app.models.session import SetLog
    from app.services.session_builder import instantiate_session

    db, tpl = _get_template("push-a")
    with db:
        session = instantiate_session(
            db, tpl, datetime(2026, 1, 6, 18, 0, tzinfo=UTC)
        )
        db.commit()

        first_ex_id = session.session_exercises[0].id
        rows = db.execute(
            select(SetLog).where(SetLog.session_exercise_id == first_ex_id)
        ).scalars().all()
        indexed = {(s.kind, s.set_index) for s in rows}
        assert ("warmup", 1) in indexed
        assert ("work", 1) in indexed

        db.delete(session)
        db.commit()
