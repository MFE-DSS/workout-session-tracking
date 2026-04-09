"""Health endpoints.

Two distinct endpoints by design:

- ``GET /healthz``        — cheap public liveness probe.
                            Just runs `SELECT 1`. Returns 200 if the
                            DB connection works. Used by uptime
                            probes that should NOT be authenticated.

- ``GET /healthz/strict`` — operator-facing health signal.
                            Reports DB status, BACKUP_DIR existence,
                            latest backup presence + integrity. Returns
                            200 with status "ok" if everything is
                            healthy, 503 with status "degraded"
                            otherwise. Designed for cron / hook
                            invocations and the deploy verification
                            checklist.

Both stay public per the V1 rule (no app-level auth). Operators
can move /healthz/strict behind nginx auth_basic if they want;
the leak surface is small (file names, sizes, counts).
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.services.backup_verifier import verify_latest_backup

router = APIRouter(tags=["health"])


@router.get("/healthz")
def healthz(db: Session = Depends(get_db)) -> dict:
    db.execute(text("SELECT 1"))
    return {"status": "ok"}


@router.get("/healthz/strict")
def healthz_strict(db: Session = Depends(get_db)) -> JSONResponse:
    """Operator-facing health: db + backup_dir + latest backup."""
    settings = get_settings()
    now = datetime.now(timezone.utc)

    # 1. DB connectivity
    db_check: dict[str, Any] = {"ok": False, "detail": ""}
    try:
        db.execute(text("SELECT 1"))
        db_check["ok"] = True
        db_check["detail"] = "select 1 ok"
    except Exception as exc:  # pragma: no cover
        db_check["detail"] = f"select 1 failed: {exc}"

    # 2. backup_dir presence (informational, not a failure)
    backup_dir_path = Path(settings.backup_dir)
    backup_dir_check: dict[str, Any] = {
        "exists": backup_dir_path.is_dir(),
        "path": str(backup_dir_path),
    }

    # 3. Latest backup presence + verifier
    backup_check: dict[str, Any] = {
        "present": False,
        "valid": None,
        "file": None,
        "age_seconds": None,
        "schema_version": None,
        "exported_count": None,
        "live_session_count": None,
        "errors": [],
    }
    if backup_dir_path.is_dir():
        verification = verify_latest_backup(backup_dir_path, db=db, now=now)
        # `verify_latest_backup` only marks "present" via the file_name
        # field — when no JSON file is found at all it returns ok=False
        # with errors=["no JSON backup file found in ..."]. We treat
        # that as "absent" rather than "invalid".
        if verification.file_name is not None:
            backup_check["present"] = True
            backup_check["valid"] = verification.ok
            backup_check["file"] = verification.file_name
            backup_check["age_seconds"] = verification.file_age_seconds
            backup_check["schema_version"] = verification.schema_version
            backup_check["exported_count"] = verification.exported_count
            backup_check["live_session_count"] = verification.live_session_count
            backup_check["errors"] = verification.errors

    # Overall: db must be ok, AND if a backup is present it must be valid.
    overall_ok = db_check["ok"] and (
        not backup_check["present"] or backup_check["valid"] is True
    )

    payload: dict[str, Any] = {
        "status": "ok" if overall_ok else "degraded",
        "checked_at": now.isoformat(),
        "db": db_check,
        "backup_dir": backup_dir_check,
        "backup": backup_check,
    }
    return JSONResponse(content=payload, status_code=200 if overall_ok else 503)
