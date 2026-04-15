"""Read-only recap aggregation for the /done terminal state view.

Consumes existing session data. Computes no new analytics — only
assembles what's already derivable (duration, done/total work sets,
exercise summaries, substitution badges, cardio block).
"""
from __future__ import annotations

from datetime import timedelta
from typing import Any

from app.models.session import WorkoutSession
from app.services.stats import summarise_current_exercise
from app.services.time_format import format_duration_short


def _duration_label(session: WorkoutSession) -> str:
    if not (session.started_at and session.ended_at):
        return ""
    start = session.started_at
    end = session.ended_at
    # SQLite round-trips DATETIMEs as naive. Align tz frames before subtracting.
    if start.tzinfo is None and end.tzinfo is not None:
        start = start.replace(tzinfo=end.tzinfo)
    elif end.tzinfo is None and start.tzinfo is not None:
        end = end.replace(tzinfo=start.tzinfo)
    delta: timedelta = end - start
    return format_duration_short(delta)


def _kind(session: WorkoutSession) -> str:
    tpl = session.template
    if tpl is None:
        return "strength"
    return tpl.kind or "strength"


def _cardio_block(session: WorkoutSession, kind: str) -> dict[str, Any] | None:
    if kind != "cardio":
        return None
    return {
        "duration_min": session.cardio_duration_min,
        "bpm_avg": session.cardio_bpm_avg,
        "calories": session.cardio_machine_calories,
        "machine_type": session.cardio_machine_type,
    }


def build_recap(session: WorkoutSession) -> dict[str, Any]:
    """Return a dict shaped for the session_done.html template."""
    kind = _kind(session)
    duration_label = _duration_label(session)

    total_work = 0
    done_work = 0
    exercises: list[dict[str, Any]] = []
    for se in session.session_exercises:
        work_sets = [sl for sl in se.set_logs if sl.kind == "work"]
        done_sets = [sl for sl in work_sets if sl.completed]
        total_work += len(work_sets)
        done_work += len(done_sets)
        summary = summarise_current_exercise(se)
        display_name = se.substituted_name or se.exercise_name_snapshot
        exercises.append(
            {
                "code": se.exercise_code_snapshot,
                "name": se.exercise_name_snapshot,
                "substituted_name": se.substituted_name,
                "display_name": display_name,
                "done": len(done_sets),
                "total": len(work_sets),
                "score": se.success_score,
                "weights_str": summary["weights_str"] if summary else None,
                "reps_str": summary["reps_str"] if summary else None,
            }
        )

    completion_pct = round(100 * done_work / total_work) if total_work else None
    substitution_count = sum(1 for e in exercises if e["substituted_name"])

    return {
        "header": {
            "template_name": session.template_name_snapshot,
            "started_at": session.started_at,
            "ended_at": session.ended_at,
            "duration_label": duration_label,
            "kind": kind,
        },
        "summary": {
            "work_sets_done": done_work,
            "work_sets_total": total_work,
            "completion_pct": completion_pct,
            "substitution_count": substitution_count,
            "bodyweight_kg": session.bodyweight_kg,
            "concentration": session.concentration,
            "global_state": session.global_state,
            "cardio": _cardio_block(session, kind),
        },
        "exercises": exercises,
    }
