"""Tests for session_recap.build_recap — agrégat lecture-seule pour /done."""
from __future__ import annotations

from datetime import datetime, timezone

from tests.helpers import get_test_user_id


def _mk_completed_session(
    *,
    template_slug: str = "push-a",
    template_name: str = "Push A — test",
    started_at: datetime | None = None,
    ended_at: datetime | None = None,
    template_kind: str | None = None,
    cardio: dict | None = None,
    exercises: list[dict] | None = None,
):
    """Create and commit a completed WorkoutSession for recap testing.

    Mirrors the `_mk_session` pattern used throughout the test suite
    (see tests/test_kpis.py). Returns the persisted session id so the
    caller can re-fetch in its own SessionLocal context.
    """
    from app.database import SessionLocal
    from app.models.catalog import WorkoutTemplate
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    started = started_at or datetime(2026, 4, 13, 18, 0, tzinfo=timezone.utc)
    ended = ended_at or datetime(2026, 4, 13, 19, 30, tzinfo=timezone.utc)

    with SessionLocal() as db:
        template_id = None
        if template_kind is not None:
            tpl = WorkoutTemplate(
                slug=template_slug,
                name=template_name,
                kind=template_kind,
            )
            db.add(tpl)
            db.flush()
            template_id = tpl.id

        s = WorkoutSession(
            user_id=get_test_user_id(),
            template_id=template_id,
            template_slug_snapshot=template_slug,
            template_name_snapshot=template_name,
            started_at=started,
            ended_at=ended,
            status="completed",
            concentration="high",
            global_state="good",
            bodyweight_kg=79.4,
        )
        if cardio:
            s.cardio_duration_min = cardio.get("duration_min")
            s.cardio_bpm_avg = cardio.get("bpm_avg")
            s.cardio_machine_calories = cardio.get("calories")
            s.cardio_machine_type = cardio.get("machine_type")

        exs = exercises if exercises is not None else [
            {"code": "E1", "name": "Incline Smith Press"},
            {"code": "E2", "name": "Chest Press machine"},
        ]
        for pos, ex in enumerate(exs, start=1):
            se = SessionExercise(
                exercise_code_snapshot=ex.get("code", f"E{pos}"),
                exercise_name_snapshot=ex.get("name", f"Ex {pos}"),
                position=pos,
                success_score=ex.get("success_score", 80),
                substituted_name=ex.get("substituted_name"),
            )
            # Default: 3 work sets, first 2 completed.
            work_sets = ex.get(
                "work_sets",
                [
                    {"weight_kg": 60.0, "reps": 10, "completed": True},
                    {"weight_kg": 60.0, "reps": 10, "completed": True},
                    {"weight_kg": 60.0, "reps": 10, "completed": False},
                ],
            )
            for j, sl in enumerate(work_sets, start=1):
                se.set_logs.append(
                    SetLog(
                        kind="work",
                        set_index=j,
                        weight_kg=sl.get("weight_kg"),
                        reps=sl.get("reps"),
                        completed=sl.get("completed", False),
                    )
                )
            s.session_exercises.append(se)
        db.add(s)
        db.commit()
        return s.id


def test_build_recap_returns_expected_shape(client):
    from app.database import SessionLocal
    from app.models.session import WorkoutSession
    from app.services.session_recap import build_recap

    sid = _mk_completed_session(
        started_at=datetime(2026, 4, 13, 18, 45, tzinfo=timezone.utc),
        ended_at=datetime(2026, 4, 13, 20, 2, tzinfo=timezone.utc),
    )
    with SessionLocal() as db:
        session = db.get(WorkoutSession, sid)
        recap = build_recap(session)

    assert set(recap.keys()) == {"header", "summary", "exercises"}
    header = recap["header"]
    assert header["template_name"] == "Push A — test"
    assert header["started_at"] is not None
    assert header["ended_at"] is not None
    assert header["duration_label"]  # non-empty
    assert header["kind"] == "strength"  # no template → fallback

    summary = recap["summary"]
    assert summary["work_sets_total"] == 6
    assert summary["work_sets_done"] == 4
    assert summary["completion_pct"] == 67
    assert summary["substitution_count"] == 0
    assert summary["bodyweight_kg"] == 79.4
    assert summary["concentration"] == "high"
    assert summary["global_state"] == "good"
    assert summary["cardio"] is None

    assert isinstance(recap["exercises"], list)
    assert len(recap["exercises"]) == 2
    e0 = recap["exercises"][0]
    assert e0["code"] == "E1"
    assert e0["name"] == "Incline Smith Press"
    assert e0["substituted_name"] is None
    assert e0["display_name"] == "Incline Smith Press"
    assert e0["done"] == 2
    assert e0["total"] == 3
    assert e0["score"] == 80
    assert e0["weights_str"] is not None
    assert e0["reps_str"] is not None


def test_build_recap_marks_substituted_exercise(client):
    from app.database import SessionLocal
    from app.models.session import WorkoutSession
    from app.services.session_recap import build_recap

    sid = _mk_completed_session()
    with SessionLocal() as db:
        session = db.get(WorkoutSession, sid)
        session.session_exercises[0].substituted_name = "Développé couché haltères"
        db.commit()
        db.refresh(session)
        recap = build_recap(session)

    e0 = recap["exercises"][0]
    assert e0["substituted_name"] == "Développé couché haltères"
    assert e0["display_name"] == "Développé couché haltères"
    assert recap["summary"]["substitution_count"] == 1


def test_build_recap_cardio_populates_cardio_section(client):
    from app.database import SessionLocal
    from app.models.session import WorkoutSession
    from app.services.session_recap import build_recap

    sid = _mk_completed_session(
        template_slug="liss",
        template_name="LISS cardio",
        template_kind="cardio",
        cardio={
            "duration_min": 45,
            "bpm_avg": 132,
            "calories": 380,
            "machine_type": "treadmill",
        },
        exercises=[],
    )
    with SessionLocal() as db:
        session = db.get(WorkoutSession, sid)
        recap = build_recap(session)

    assert recap["header"]["kind"] == "cardio"
    cardio = recap["summary"]["cardio"]
    assert cardio is not None
    assert cardio["duration_min"] == 45
    assert cardio["bpm_avg"] == 132
    assert cardio["calories"] == 380
    assert cardio["machine_type"] == "treadmill"


def test_build_recap_duration_label(client):
    from app.database import SessionLocal
    from app.models.session import WorkoutSession
    from app.services.session_recap import build_recap

    sid = _mk_completed_session(
        started_at=datetime(2026, 4, 13, 18, 0, tzinfo=timezone.utc),
        ended_at=datetime(2026, 4, 13, 19, 17, tzinfo=timezone.utc),
    )
    with SessionLocal() as db:
        session = db.get(WorkoutSession, sid)
        recap = build_recap(session)

    label = recap["header"]["duration_label"]
    assert "1" in label
    assert "17" in label
