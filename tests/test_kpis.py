"""Tests for the progress KPI aggregation rules."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone


def _mk_session(
    *,
    status: str,
    template_slug: str = "push-a",
    template_name: str = "Push A",
    started_at: datetime | None = None,
    exercises: list[dict] | None = None,
):
    """Build and commit a WorkoutSession with hand-crafted exercises
    and set_logs. Used by the KPI tests so we control every field
    that enters an aggregate.
    """
    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    with SessionLocal() as db:
        s = WorkoutSession(
            template_slug_snapshot=template_slug,
            template_name_snapshot=template_name,
            started_at=started_at or datetime.now(timezone.utc),
            status=status,
        )
        for i, ex in enumerate(exercises or [], start=1):
            se = SessionExercise(
                template_exercise_id=None,
                exercise_code_snapshot=ex.get("code", f"E{i}"),
                exercise_name_snapshot=ex.get("name", f"Ex {i}"),
                position=i,
                success_score=ex.get("success_score"),
            )
            for j, sl in enumerate(ex.get("work_sets", []), start=1):
                se.set_logs.append(
                    SetLog(
                        kind="work",
                        set_index=j,
                        completed=sl.get("completed", False),
                        weight_kg=sl.get("weight_kg"),
                        reps=sl.get("reps"),
                    )
                )
            for j, sl in enumerate(ex.get("warmup_sets", []), start=1):
                se.set_logs.append(
                    SetLog(
                        kind="warmup",
                        set_index=j,
                        completed=sl.get("completed", False),
                    )
                )
            s.session_exercises.append(se)
        db.add(s)
        db.commit()
        return s.id


def test_progress_renders_with_empty_db(client):
    r = client.get("/progress")
    assert r.status_code == 200
    body = r.text
    assert "Progression" in body
    assert "sessions cette semaine" in body
    # Empty state for per-template list
    assert "Aucune session terminée" in body


def test_completion_rate_ignores_warmup_rows(client):
    from app.database import SessionLocal
    from app.services.kpis import compute_global_kpis

    _mk_session(
        status="completed",
        exercises=[
            {
                "warmup_sets": [
                    {"completed": False},
                    {"completed": False},
                ],
                "work_sets": [
                    {"completed": True, "weight_kg": 60, "reps": 10},
                    {"completed": True, "weight_kg": 60, "reps": 10},
                    {"completed": False},
                ],
            }
        ],
    )
    with SessionLocal() as db:
        k = compute_global_kpis(db)
        # Warmups are NOT in the denominator
        assert k.work_sets_total_30d == 3
        assert k.work_sets_done_30d == 2
        assert abs(k.completion_rate_30d - (2 / 3)) < 1e-6


def test_in_progress_sessions_excluded_from_kpis(client):
    from app.database import SessionLocal
    from app.services.kpis import compute_global_kpis

    # An in-progress session with everything untouched should NOT
    # drag down the completion rate.
    _mk_session(
        status="in_progress",
        exercises=[
            {
                "work_sets": [
                    {"completed": False},
                    {"completed": False},
                ],
            }
        ],
    )
    # Plus a completed session where all work sets are done.
    _mk_session(
        status="completed",
        exercises=[
            {
                "work_sets": [
                    {"completed": True, "weight_kg": 60, "reps": 10},
                    {"completed": True, "weight_kg": 60, "reps": 10},
                ],
            }
        ],
    )
    with SessionLocal() as db:
        k = compute_global_kpis(db)
        assert k.completion_rate_30d == 1.0
        # sessions_this_week counts all regardless of status
        assert k.sessions_this_week >= 2
        # completed_last_30 excludes in-progress
        assert k.completed_last_30 == 1


def test_success_score_average_ignores_nulls(client):
    from app.database import SessionLocal
    from app.services.kpis import compute_global_kpis

    _mk_session(
        status="completed",
        exercises=[
            {"success_score": 100, "work_sets": [{"completed": True}]},
            {"success_score": 80, "work_sets": [{"completed": True}]},
            {"success_score": None, "work_sets": [{"completed": True}]},
        ],
    )
    with SessionLocal() as db:
        k = compute_global_kpis(db)
        assert k.avg_success_score_30d is not None
        assert abs(k.avg_success_score_30d - 90.0) < 1e-6


def test_sessions_older_than_30_days_excluded(client):
    from app.database import SessionLocal
    from app.services.kpis import compute_global_kpis

    _mk_session(
        status="completed",
        started_at=datetime.now(timezone.utc) - timedelta(days=45),
        exercises=[
            {
                "success_score": 100,
                "work_sets": [{"completed": True, "weight_kg": 1, "reps": 1}],
            }
        ],
    )
    _mk_session(
        status="completed",
        started_at=datetime.now(timezone.utc) - timedelta(days=5),
        exercises=[
            {
                "success_score": 50,
                "work_sets": [{"completed": True, "weight_kg": 1, "reps": 1}],
            }
        ],
    )
    with SessionLocal() as db:
        k = compute_global_kpis(db)
        # 45d-old session is out of the window
        assert k.sessions_last_30 == 1
        assert k.completed_last_30 == 1
        # Average uses only the recent one (score 50)
        assert k.avg_success_score_30d == 50.0


def test_template_kpis_group_by_template_slug_snapshot(client):
    from app.database import SessionLocal
    from app.services.kpis import compute_template_kpis

    _mk_session(
        status="completed",
        template_slug="push-a",
        template_name="Push A",
        exercises=[
            {"success_score": 100, "work_sets": [{"completed": True}]},
        ],
    )
    _mk_session(
        status="completed",
        template_slug="push-a",
        template_name="Push A",
        exercises=[
            {"success_score": 80, "work_sets": [{"completed": True}]},
        ],
    )
    _mk_session(
        status="completed",
        template_slug="legs",
        template_name="Legs",
        exercises=[
            {"success_score": 60, "work_sets": [{"completed": True}]},
        ],
    )
    with SessionLocal() as db:
        rows = compute_template_kpis(db)
        by_slug = {r.slug: r for r in rows}
        assert by_slug["push-a"].n_completed == 2
        assert abs(by_slug["push-a"].avg_success_score - 90.0) < 1e-6
        assert by_slug["legs"].n_completed == 1
        assert by_slug["legs"].avg_success_score == 60.0


def test_progress_page_renders_with_real_data(client):
    _mk_session(
        status="completed",
        template_slug="push-a",
        template_name="Push A",
        exercises=[
            {
                "success_score": 80,
                "work_sets": [
                    {"completed": True, "weight_kg": 60, "reps": 10},
                    {"completed": True, "weight_kg": 60, "reps": 10},
                ],
            }
        ],
    )
    r = client.get("/progress")
    assert r.status_code == 200
    body = r.text
    # KPI card values render
    assert "taux de complétion work sets" in body
    assert "Push A" in body
    # The explicit rule note is always visible
    assert "sessions terminées" in body
