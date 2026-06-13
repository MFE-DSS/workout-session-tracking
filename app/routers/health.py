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

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.config import get_settings
from app.deps import DbSession
from app.services.backup_verifier import verify_latest_backup

router = APIRouter(tags=["health"])


def _read_deploy_state(path: Path, *, now: datetime) -> dict[str, Any]:
    """Sb_26.3 — read var/deploy_state.json with full graceful degradation.

    Missing file, bad JSON, weird fields all return `present=False`
    rather than raising — observability must never break the app.
    Never leaks secrets: only sha, timestamps, service name.
    """
    out: dict[str, Any] = {
        "present": False,
        "sha": None,
        "short_sha": None,
        "deployed_at": None,
        "age_seconds": None,
        "service": None,
        "errors": [],
    }
    if not path.exists():
        return out
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        out["errors"].append(f"deploy_state read error: {exc.__class__.__name__}")
        return out
    if not isinstance(raw, dict):
        out["errors"].append("deploy_state must be a JSON object")
        return out

    sha = raw.get("sha")
    out["present"] = True
    if isinstance(sha, str):
        out["sha"] = sha
        out["short_sha"] = sha[:12]
    if isinstance(raw.get("service"), str):
        out["service"] = raw["service"]

    deployed_at_raw = raw.get("deployed_at")
    if isinstance(deployed_at_raw, str):
        out["deployed_at"] = deployed_at_raw
        try:
            ts = datetime.fromisoformat(deployed_at_raw.replace("Z", "+00:00"))
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=UTC)
            out["age_seconds"] = int((now - ts).total_seconds())
        except ValueError:
            out["errors"].append("deployed_at not parseable as ISO-8601")
    return out


def _disk_usage(path: Path) -> dict[str, Any]:
    """Best-effort disk usage of the partition holding `path`.

    Returns `available=None` if the call fails (eg. path missing on
    a fresh dev install). Never raises.
    """
    try:
        target = path if path.exists() else path.parent
        usage = shutil.disk_usage(str(target))
        free_pct = round(100 * usage.free / usage.total, 1) if usage.total else None
        return {
            "total_bytes": usage.total,
            "free_bytes": usage.free,
            "free_percent": free_pct,
            "error": None,
        }
    except OSError as exc:
        return {
            "total_bytes": None,
            "free_bytes": None,
            "free_percent": None,
            "error": exc.__class__.__name__,
        }


@router.get("/healthz")
def healthz(db: DbSession) -> dict:
    db.execute(text("SELECT 1"))
    return {"status": "ok"}


@router.get("/healthz/strict")
def healthz_strict(db: DbSession) -> JSONResponse:
    """Operator-facing health: db + backup_dir + latest backup."""
    settings = get_settings()
    now = datetime.now(UTC)

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
        # Intentionally omit the absolute path from the public
        # endpoint to avoid leaking filesystem structure.
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

    # 4. Sb_26.3 — deploy state (SHA + timestamp of last deploy).
    #    Informational: never demotes the overall status.
    deploy_check = _read_deploy_state(Path(settings.deploy_state_path), now=now)

    # 5. Sb_26.3 — disk usage of the DB partition (informational).
    disk_check = _disk_usage(backup_dir_path)

    # Overall: db must be ok, AND if a backup is present it must be valid.
    # deploy_check and disk_check are intentionally informational only —
    # /healthz/strict must not flap to 503 because we couldn't read a
    # JSON file or stat a partition.
    overall_ok = db_check["ok"] and (
        not backup_check["present"] or backup_check["valid"] is True
    )

    payload: dict[str, Any] = {
        "status": "ok" if overall_ok else "degraded",
        "checked_at": now.isoformat(),
        "db": db_check,
        "backup_dir": backup_dir_check,
        "backup": backup_check,
        "deploy": deploy_check,
        "disk": disk_check,
    }
    return JSONResponse(content=payload, status_code=200 if overall_ok else 503)
