"""Pure builders for the JSON / CSV exports.

The HTTP routes in `app.routers.export` wrap these in a Response.
The standalone backup script in `scripts/backup_sessions.py`
writes the output directly to disk. No HTTP dependency on either
side. Single source of truth for both formats.

Schema is gated by `SCHEMA_VERSION`. Bump it on any incompatible
shape change.
"""
from __future__ import annotations

import csv
from datetime import datetime, timezone
from io import StringIO
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.session import SessionExercise, WorkoutSession

SCHEMA_VERSION = 1


# ---------------------------------------------------------------------------
# JSON
# ---------------------------------------------------------------------------


def _iso(dt: datetime | None) -> str | None:
    return dt.isoformat() if dt is not None else None


def serialise_session(s: WorkoutSession) -> dict[str, Any]:
    """One session as a nested dict, ready for JSON."""
    exercises_sorted = sorted(s.session_exercises, key=lambda x: x.position)
    return {
        "id": s.id,
        "status": s.status,
        "started_at": _iso(s.started_at),
        "ended_at": _iso(s.ended_at),
        "template_slug": s.template_slug_snapshot,
        "template_name": s.template_name_snapshot,
        "concentration": s.concentration,
        "global_state": s.global_state,
        "bodyweight_kg": s.bodyweight_kg,
        "free_note": s.free_note,
        "exercises": [
            {
                "position": se.position,
                "code": se.exercise_code_snapshot,
                "name": se.exercise_name_snapshot,
                "success_score": se.success_score,
                "muscle_sensation": se.muscle_sensation,
                "free_note": se.free_note,
                "substituted_name": se.substituted_name,
                "sets": [
                    {
                        "kind": sl.kind,
                        "set_index": sl.set_index,
                        "weight_kg": sl.weight_kg,
                        "reps": sl.reps,
                        "technique": sl.technique,
                        "execution_quality": sl.execution_quality,
                        "reps_target": sl.reps_target,
                        "completed": sl.completed,
                    }
                    for sl in sorted(
                        se.set_logs,
                        key=lambda x: (0 if x.kind == "warmup" else 1, x.set_index),
                    )
                ],
            }
            for se in exercises_sorted
        ],
    }


def _all_sessions(db: Session, *, user_id: int | None = None) -> list[WorkoutSession]:
    stmt = (
        select(WorkoutSession)
        .where(WorkoutSession.user_id == user_id if user_id is not None else True)
        .order_by(WorkoutSession.started_at.asc())
        .options(
            selectinload(WorkoutSession.session_exercises)
            .selectinload(SessionExercise.set_logs)
        )
    )
    return list(db.execute(stmt).scalars().all())


def build_json_payload(db: Session, *, user_id: int | None = None) -> dict[str, Any]:
    """Build the full JSON export as a Python dict.

    The HTTP route hands this dict to `JSONResponse`. The backup
    script writes it to disk via `json.dump`. Identical bytes for
    a given DB state.
    """
    sessions = _all_sessions(db, user_id=user_id)
    return {
        "schema_version": SCHEMA_VERSION,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "count": len(sessions),
        "sessions": [serialise_session(s) for s in sessions],
    }


# ---------------------------------------------------------------------------
# CSV
# ---------------------------------------------------------------------------


CSV_HEADERS = [
    "session_id",
    "started_at",
    "ended_at",
    "status",
    "template_slug",
    "template_name",
    "concentration",
    "global_state",
    "bodyweight_kg",
    "session_free_note",
    "exercise_position",
    "exercise_code",
    "exercise_name",
    "success_score",
    "muscle_sensation",
    "exercise_free_note",
    "substituted_name",
    "set_kind",
    "set_index",
    "weight_kg",
    "reps",
    "technique",
    "execution_quality",
    "reps_target",
    "completed",
]


def _opt(value: Any) -> str:
    """Render optional values without "None" leaking into the CSV."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "1" if value else "0"
    return str(value)


def build_csv_text(db: Session, *, user_id: int | None = None) -> str:
    """Build the full CSV export as a single text blob."""
    sessions = _all_sessions(db, user_id=user_id)
    buf = StringIO()
    writer = csv.writer(buf, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(CSV_HEADERS)

    for s in sessions:
        s_cols = [
            _opt(s.id),
            _opt(s.started_at.isoformat() if s.started_at else None),
            _opt(s.ended_at.isoformat() if s.ended_at else None),
            _opt(s.status),
            _opt(s.template_slug_snapshot),
            _opt(s.template_name_snapshot),
            _opt(s.concentration),
            _opt(s.global_state),
            _opt(s.bodyweight_kg),
            _opt(s.free_note),
        ]
        if not s.session_exercises:
            writer.writerow(s_cols + [""] * (len(CSV_HEADERS) - len(s_cols)))
            continue
        for se in sorted(s.session_exercises, key=lambda x: x.position):
            ex_cols = [
                _opt(se.position),
                _opt(se.exercise_code_snapshot),
                _opt(se.exercise_name_snapshot),
                _opt(se.success_score),
                _opt(se.muscle_sensation),
                _opt(se.free_note),
                _opt(se.substituted_name),
            ]
            for sl in sorted(
                se.set_logs,
                key=lambda x: (0 if x.kind == "warmup" else 1, x.set_index),
            ):
                writer.writerow(
                    s_cols
                    + ex_cols
                    + [
                        _opt(sl.kind),
                        _opt(sl.set_index),
                        _opt(sl.weight_kg),
                        _opt(sl.reps),
                        _opt(sl.technique),
                        _opt(sl.execution_quality),
                        _opt(sl.reps_target),
                        _opt(sl.completed),
                    ]
                )

    return buf.getvalue()
