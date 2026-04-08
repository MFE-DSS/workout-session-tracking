"""Backup / export of the workout journal.

Personal-use only: no auth, no filtering, intentionally simple.
Two formats:

- ``GET /export/sessions.json`` — full nested payload, stable
  shape gated by ``SCHEMA_VERSION``. Suitable for archival and
  for a future import endpoint.
- ``GET /export/sessions.csv`` — flat one-row-per-set view with
  every parent column denormalised. Drops into a spreadsheet
  with no transformation.

A small landing page at ``GET /export`` shows totals and links
to both formats so the user doesn't have to remember the URLs.
"""
from __future__ import annotations

import csv
from datetime import datetime, timezone
from io import StringIO
from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models.session import SessionExercise, SetLog, WorkoutSession
from app.services.session_state import latest_open_session
from app.templating import templates

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


@router.get("/export", response_class=HTMLResponse)
def export_landing(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    """Small page summarising the journal + links to both formats."""
    total_sessions = db.execute(
        select(func.count(WorkoutSession.id))
    ).scalar_one() or 0
    completed_sessions = db.execute(
        select(func.count(WorkoutSession.id)).where(
            WorkoutSession.status == "completed"
        )
    ).scalar_one() or 0
    work_sets_done = db.execute(
        select(func.count(SetLog.id))
        .where(SetLog.kind == "work")
        .where(SetLog.completed.is_(True))
    ).scalar_one() or 0
    first_started = db.execute(
        select(WorkoutSession.started_at)
        .order_by(WorkoutSession.started_at.asc())
        .limit(1)
    ).scalar_one_or_none()
    last_started = db.execute(
        select(WorkoutSession.started_at)
        .order_by(WorkoutSession.started_at.desc())
        .limit(1)
    ).scalar_one_or_none()

    return templates.TemplateResponse(
        request,
        "export.html",
        {
            "page_title": "Export",
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "work_sets_done": work_sets_done,
            "first_started": first_started,
            "last_started": last_started,
            "schema_version": SCHEMA_VERSION,
            "active_session": latest_open_session(db),
        },
    )


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


# ----------------------------------------------------------------------
# CSV export (Sprint 5)
# ----------------------------------------------------------------------

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


@router.get("/export/sessions.csv")
def export_sessions_csv(db: Session = Depends(get_db)) -> Response:
    """Flat one-row-per-set CSV view of every session.

    Sessions with no exercises (e.g. cardio templates) emit one
    row with empty exercise/set fields so they still show up.
    Sessions with exercises emit one row per SetLog (warmups
    first, then work, in set_index order).
    """
    stmt = (
        select(WorkoutSession)
        .order_by(WorkoutSession.started_at.asc())
        .options(
            selectinload(WorkoutSession.session_exercises)
            .selectinload(SessionExercise.set_logs)
        )
    )
    sessions = db.execute(stmt).scalars().all()

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

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    filename = f"workout-export-{stamp}.csv"
    return Response(
        content=buf.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store",
        },
    )
