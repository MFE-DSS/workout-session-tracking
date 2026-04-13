"""Schema-level smoke test for the session + normalized feedback tables.

Validates that:
- a WorkoutSession can be created with normalized session / exercise
  / set feedback;
- the weekday is DERIVED from `started_at`, not stored;
- the snapshot fields are populated so history survives a catalog
  rewrite.
"""
from __future__ import annotations
from tests.helpers import get_test_user_id

from datetime import datetime, timezone


def test_can_log_a_session_with_normalized_feedback(client):
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.enums import (
        ExerciseSuccessScore,
        MuscleSensation,
        SessionConcentration,
        SessionGlobalState,
        SetExecutionQuality,
        SetKind,
        SetRepsTarget,
        Technique,
    )
    from app.models.catalog import WorkoutTemplate
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    with SessionLocal() as db:
        tpl = db.execute(
            select(WorkoutTemplate).where(WorkoutTemplate.slug == "push-a")
        ).scalar_one()
        first_ex = tpl.exercises[0]

        # 2026-01-05 is a Monday -> ISO weekday 1
        session = WorkoutSession(
            template_id=tpl.id,
            template_slug_snapshot=tpl.slug,
            template_name_snapshot=tpl.name, user_id=get_test_user_id(),
            started_at=datetime(2026, 1, 5, 18, 30, tzinfo=timezone.utc),
            concentration=SessionConcentration.HIGH,
            global_state=SessionGlobalState.GOOD,
            bodyweight_kg=78.5,
            free_note="Séance test",
        )
        se = SessionExercise(
            template_exercise_id=first_ex.id,
            exercise_code_snapshot=first_ex.code,
            exercise_name_snapshot=first_ex.name,
            position=1,
            success_score=ExerciseSuccessScore.S80,
            muscle_sensation=MuscleSensation.STRONG,
        )
        sl = SetLog(
            kind=SetKind.WORK,
            set_index=1,
            weight_kg=60.0,
            reps=10,
            technique=Technique.RP,
            execution_quality=SetExecutionQuality.CLEAN,
            reps_target=SetRepsTarget.TARGET_HIT,
            completed=True,
        )
        se.set_logs.append(sl)
        session.session_exercises.append(se)
        db.add(session)
        db.commit()
        db.refresh(session)

        assert session.id is not None
        assert session.weekday_iso == 1  # Monday derived from started_at
        assert session.concentration == "high"
        assert session.global_state == "good"
        assert session.template_slug_snapshot == "push-a"
        assert session.template_name_snapshot.startswith("Push A")

        [se_loaded] = session.session_exercises
        assert se_loaded.success_score == 80  # int-enum stored as int
        assert se_loaded.muscle_sensation == "strong"
        assert se_loaded.exercise_code_snapshot == "E1"
        assert "Smith" in se_loaded.exercise_name_snapshot or "Butterfly" in se_loaded.exercise_name_snapshot

        [sl_loaded] = se_loaded.set_logs
        assert sl_loaded.kind == "work"
        assert sl_loaded.completed is True
        assert sl_loaded.execution_quality == "clean"
        assert sl_loaded.reps_target == "target_hit"
        assert sl_loaded.technique == "RP"

        # Cleanup so the fixture stays isolated
        db.delete(session)
        db.commit()


def test_catalog_rewrite_does_not_orphan_history(client):
    """A full catalog wipe must not destroy previously logged sessions."""
    from sqlalchemy import delete, select

    from app.database import SessionLocal
    from app.models.catalog import RepTarget, TemplateExercise, WorkoutTemplate
    from app.models.session import WorkoutSession

    from datetime import datetime, timezone as tz

    with SessionLocal() as db:
        tpl = db.execute(
            select(WorkoutTemplate).where(WorkoutTemplate.slug == "legs-a")
        ).scalar_one()
        session = WorkoutSession(
            template_id=tpl.id,
            template_slug_snapshot=tpl.slug,
            template_name_snapshot=tpl.name, user_id=get_test_user_id(),
            started_at=datetime(2026, 2, 14, 9, 0, tzinfo=tz.utc),
        )
        db.add(session)
        db.commit()
        sid = session.id

        # Simulate an aggressive catalog rewrite
        db.execute(delete(RepTarget))
        db.execute(delete(TemplateExercise))
        db.execute(delete(WorkoutTemplate))
        db.commit()

        reloaded = db.execute(
            select(WorkoutSession).where(WorkoutSession.id == sid)
        ).scalar_one()
        assert reloaded.template_id is None  # FK was SET NULL
        assert reloaded.template_slug_snapshot == "legs-a"
        assert reloaded.template_name_snapshot.startswith("Legs A")

        db.delete(reloaded)
        db.commit()
