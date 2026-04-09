"""Backup / export of the workout journal.

Personal-use only: no auth (single-user V1, protect via nginx
basic_auth in deploy/README.md). Three endpoints:

- ``GET /export``               — small landing page with totals,
  the latest local backup file (if a nightly job has run), and
  download buttons for both formats.
- ``GET /export/sessions.json`` — full nested payload, stable
  shape gated by ``SCHEMA_VERSION``.
- ``GET /export/sessions.csv``  — flat one-row-per-set view.

The actual JSON / CSV building lives in
``app.services.export_builder`` so the standalone backup script
can produce identical output without going through HTTP.
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.deps import require_user
from app.models.user import User
from app.models.session import SetLog, WorkoutSession
from app.services.backup_inspector import latest_backup_info
from app.services.backup_verifier import verify_latest_backup
from app.services.export_builder import (
    SCHEMA_VERSION,
    build_csv_text,
    build_json_payload,
)
from app.services.session_state import latest_open_session
from app.services.time_format import relative_hours_ago
from app.templating import templates

router = APIRouter(tags=["export"])


@router.get("/export", response_class=HTMLResponse)
def export_landing(request: Request, db: Session = Depends(get_db), user: User = Depends(require_user)) -> HTMLResponse:
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

    settings = get_settings()
    last_backup = latest_backup_info(settings.backup_dir)

    # Sprint 7: run the verifier inline so the user sees the
    # integrity state next to the backup file info. Cheap
    # (one file read + one COUNT query).
    verification = None
    backup_age_label = None
    if last_backup is not None:
        now = datetime.now(timezone.utc)
        verification = verify_latest_backup(settings.backup_dir, db=db, now=now)
        backup_age_label = relative_hours_ago(now, last_backup.modified_at)

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
            "last_backup": last_backup,
            "backup_dir": settings.backup_dir,
            "backup_age_label": backup_age_label,
            "verification": verification,
            "active_session": latest_open_session(db),
        },
    )


@router.get("/export/sessions.json")
def export_sessions_json(db: Session = Depends(get_db), user: User = Depends(require_user)) -> JSONResponse:
    payload = build_json_payload(db)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    filename = f"workout-export-{stamp}.json"
    return JSONResponse(
        content=payload,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store",
        },
    )


@router.get("/export/sessions.csv")
def export_sessions_csv(db: Session = Depends(get_db), user: User = Depends(require_user)) -> Response:
    body = build_csv_text(db)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    filename = f"workout-export-{stamp}.csv"
    return Response(
        content=body,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store",
        },
    )
