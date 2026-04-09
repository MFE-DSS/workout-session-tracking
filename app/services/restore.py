"""Restore a workout journal from a JSON export payload.

This is the reverse path of `app.services.export_builder`:
given a dict with the `schema_version == 1` shape produced by
`build_json_payload`, it INSERTs every session, exercise, and
set into an **empty** database.

Safety rules:
  - Refuses to run if the target DB already contains any
    `WorkoutSession` row. The caller must wipe or use a fresh
    DB. This is intentional: V1 has no merge logic.
  - Validates the payload shape before touching the DB.
  - Returns a `RestoreResult` with `ok`, counts, and an errors
    list so the caller can decide whether to commit or rollback.

The function does NOT commit. The caller owns the transaction:
  - `scripts/restore_latest_backup.py` commits on success,
    rolls back on failure.
  - `tests/test_restore.py` always rolls back (via fixture
    teardown).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.session import SessionExercise, SetLog, WorkoutSession
from app.services.export_builder import SCHEMA_VERSION


@dataclass
class RestoreResult:
    ok: bool = False
    sessions_restored: int = 0
    exercises_restored: int = 0
    sets_restored: int = 0
    errors: list[str] = field(default_factory=list)
    summary: str = ""


def _parse_datetime(raw: Optional[str]) -> Optional[datetime]:
    if raw is None:
        return None
    try:
        return datetime.fromisoformat(raw)
    except (ValueError, TypeError):
        return None


def _validate_payload(payload: Any) -> list[str]:
    """Return a list of fatal validation errors (empty = valid)."""
    errors: list[str] = []
    if not isinstance(payload, dict):
        errors.append("payload is not a dict")
        return errors

    sv = payload.get("schema_version")
    if sv is None:
        errors.append("schema_version missing")
    elif sv != SCHEMA_VERSION:
        errors.append(
            f"schema_version is {sv}, expected {SCHEMA_VERSION}"
        )

    count = payload.get("count")
    if count is None or not isinstance(count, int):
        errors.append("count field missing or not int")

    sessions = payload.get("sessions")
    if sessions is None or not isinstance(sessions, list):
        errors.append("sessions field missing or not list")
    elif isinstance(count, int) and len(sessions) != count:
        errors.append(
            f"sessions length ({len(sessions)}) != count ({count})"
        )

    return errors


def restore_from_json_payload(
    db: Session, payload: Any
) -> RestoreResult:
    """Insert every session from a JSON export payload into `db`.

    Does NOT commit. Returns a `RestoreResult` so the caller can
    decide whether to commit or rollback.
    """
    result = RestoreResult()

    # 1. Validate payload shape
    validation_errors = _validate_payload(payload)
    if validation_errors:
        result.errors = validation_errors
        result.summary = "; ".join(validation_errors)
        return result

    # 2. Refuse to run on a non-empty DB
    existing = db.execute(
        select(func.count(WorkoutSession.id))
    ).scalar_one() or 0
    if existing > 0:
        result.errors.append(
            f"target DB is not empty ({existing} sessions exist). "
            "Wipe the DB or use a fresh file before restoring."
        )
        result.summary = "DB not empty"
        return result

    # 3. Insert
    sessions = payload["sessions"]
    for s_data in sessions:
        session = WorkoutSession(
            template_slug_snapshot=s_data.get("template_slug", ""),
            template_name_snapshot=s_data.get("template_name", ""),
            started_at=_parse_datetime(s_data.get("started_at"))
            or datetime.utcnow(),
            ended_at=_parse_datetime(s_data.get("ended_at")),
            status=s_data.get("status", "completed"),
            concentration=s_data.get("concentration"),
            global_state=s_data.get("global_state"),
            bodyweight_kg=s_data.get("bodyweight_kg"),
            free_note=s_data.get("free_note"),
        )

        for ex_data in s_data.get("exercises", []):
            se = SessionExercise(
                exercise_code_snapshot=ex_data.get("code", ""),
                exercise_name_snapshot=ex_data.get("name", ""),
                position=ex_data.get("position", 0),
                success_score=ex_data.get("success_score"),
                muscle_sensation=ex_data.get("muscle_sensation"),
                free_note=ex_data.get("free_note"),
            )

            for set_data in ex_data.get("sets", []):
                sl = SetLog(
                    kind=set_data.get("kind", "work"),
                    set_index=set_data.get("set_index", 1),
                    weight_kg=set_data.get("weight_kg"),
                    reps=set_data.get("reps"),
                    technique=set_data.get("technique"),
                    execution_quality=set_data.get("execution_quality"),
                    reps_target=set_data.get("reps_target"),
                    completed=bool(set_data.get("completed", False)),
                )
                se.set_logs.append(sl)
                result.sets_restored += 1

            session.session_exercises.append(se)
            result.exercises_restored += 1

        db.add(session)
        result.sessions_restored += 1

    db.flush()  # trigger DB-level validation without committing

    # 4. Post-restore sanity: count the rows we just flushed
    live_count = db.execute(
        select(func.count(WorkoutSession.id))
    ).scalar_one() or 0

    if live_count != result.sessions_restored:
        result.errors.append(
            f"post-restore count mismatch: expected "
            f"{result.sessions_restored}, got {live_count}"
        )

    result.ok = len(result.errors) == 0
    result.summary = (
        f"restored {result.sessions_restored} sessions, "
        f"{result.exercises_restored} exercises, "
        f"{result.sets_restored} sets"
        if result.ok
        else "; ".join(result.errors)
    )
    return result
