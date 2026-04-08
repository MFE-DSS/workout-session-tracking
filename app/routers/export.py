"""JSON export of the workout journal.

Personal-use export: one call returns every persisted session
with its exercises and set logs, in a stable format suitable for
backup or offline analysis. No authentication, no filtering,
intentionally simple.

Contract is frozen by `SCHEMA_VERSION`. If the shape ever has to
change, bump the version and keep older shape producers around
so existing consumers don't break.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models.session import SessionExercise, WorkoutSession

router = APIRouter(tags=["export"])

SCHEMA_VERSION = 1


def _iso(dt: datetime | None) -> str | None:
    return dt.isoformat() if dt is not None else None


def _serialise_session(s: WorkoutSession) -> dict[str, Any]:
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
                        se.set_logs, key=lambda x: (0 if x.kind == "warmup" else 1, x.set_index)
                    )
                ],
            }
            for se in exercises_sorted
        ],
    }


@router.get("/export/sessions.json")
def export_sessions_json(db: Session = Depends(get_db)) -> JSONResponse:
    stmt = (
        select(WorkoutSession)
        .order_by(WorkoutSession.started_at.asc())
        .options(
            selectinload(WorkoutSession.session_exercises)
            .selectinload(SessionExercise.set_logs)
        )
    )
    sessions = db.execute(stmt).scalars().all()
    payload = {
        "schema_version": SCHEMA_VERSION,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "count": len(sessions),
        "sessions": [_serialise_session(s) for s in sessions],
    }
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    filename = f"workout-export-{stamp}.json"
    return JSONResponse(
        content=payload,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            # Cache-Control: never cache a data export.
            "Cache-Control": "no-store",
        },
    )
