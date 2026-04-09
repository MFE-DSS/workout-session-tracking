"""Backup integrity verifier.

The Sprint 6 backup script writes JSON + CSV dumps. This module
adds a *practical* sanity check on top of the JSON file:

    - Does a backup exist?
    - Can it be parsed?
    - Does it carry the expected `schema_version`?
    - Are `count` and `sessions` consistent?
    - As an informational signal, how many sessions does the live
      DB hold today?

The verifier is intentionally pure and small. It is reused by:
- `scripts/verify_backup.py` (CLI)
- `app/routers/health.py` (`GET /healthz/strict`)
- `app/routers/export.py` (`GET /export` status block)

`ok` is True iff zero fatal errors were collected. The live DB
count comparison is **informational only** — backups are nightly,
the live DB drifts during the day, so a count mismatch is normal
and never marks the backup as bad. The errors list captures only
truly broken states (missing file, broken JSON, missing fields,
wrong schema version, internal inconsistency).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Union

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.session import WorkoutSession
from app.services.export_builder import SCHEMA_VERSION


@dataclass
class BackupVerification:
    ok: bool
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    file_modified_at: Optional[datetime] = None
    file_age_seconds: Optional[float] = None
    file_size_bytes: Optional[int] = None
    schema_version: Optional[int] = None
    exported_count: Optional[int] = None
    live_session_count: Optional[int] = None
    errors: list[str] = field(default_factory=list)
    summary: str = ""


def _newest_json(backup_dir: Union[str, Path]) -> Optional[Path]:
    """Latest `sessions-*.json` file in `backup_dir`, or None."""
    p = Path(backup_dir)
    if not p.is_dir():
        return None
    files = list(p.glob("sessions-*.json"))
    if not files:
        return None
    return max(files, key=lambda f: f.stat().st_mtime)


def verify_latest_backup(
    backup_dir: Union[str, Path],
    db: Optional[Session] = None,
    *,
    now: Optional[datetime] = None,
) -> BackupVerification:
    """Run the verifier and return a `BackupVerification`.

    Pass `db` to also report the live session count. Pass nothing
    to skip the DB call (the file checks are still run).
    """
    now = now or datetime.now(timezone.utc)
    result = BackupVerification(ok=False)

    # The verifier only cares about JSON dumps. `latest_backup_info`
    # globs both JSON and CSV, and the CSV is written milliseconds
    # after the JSON — on any given run its mtime is newer. Always
    # pick the newest *.json explicitly so we don't try to parse
    # the CSV as JSON.
    target = _newest_json(backup_dir)

    if target is None or not target.exists():
        result.errors.append(f"no JSON backup file found in {backup_dir!s}")
        result.summary = "no backup found"
        return result

    stat = target.stat()
    file_modified_at = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
    file_age_seconds = max((now - file_modified_at).total_seconds(), 0.0)
    result.file_name = target.name
    result.file_path = str(target)
    result.file_modified_at = file_modified_at
    result.file_age_seconds = file_age_seconds
    result.file_size_bytes = stat.st_size

    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        result.errors.append(f"cannot parse JSON: {exc}")
        result.summary = "JSON parse failed"
        return result

    if not isinstance(payload, dict):
        result.errors.append("payload is not a JSON object")
        result.summary = "bad payload shape"
        return result

    schema_version = payload.get("schema_version")
    if schema_version is None:
        result.errors.append("schema_version missing")
    elif not isinstance(schema_version, int):
        result.errors.append(
            f"schema_version is {schema_version!r}, expected int"
        )
    elif schema_version != SCHEMA_VERSION:
        result.errors.append(
            f"schema_version is {schema_version}, expected {SCHEMA_VERSION}"
        )
    else:
        result.schema_version = schema_version

    count = payload.get("count")
    if count is None or not isinstance(count, int):
        result.errors.append("count field missing or not int")
    else:
        result.exported_count = count

    sessions = payload.get("sessions")
    if sessions is None or not isinstance(sessions, list):
        result.errors.append("sessions field missing or not list")
    elif result.exported_count is not None and len(sessions) != result.exported_count:
        result.errors.append(
            f"sessions length ({len(sessions)}) does not match count ({result.exported_count})"
        )

    if db is not None:
        try:
            live = db.execute(
                select(func.count(WorkoutSession.id))
            ).scalar_one() or 0
            result.live_session_count = int(live)
        except Exception as exc:  # pragma: no cover
            result.errors.append(f"could not count live sessions: {exc}")

    result.ok = len(result.errors) == 0
    if result.ok:
        result.summary = (
            f"{result.file_name} ok "
            f"(schema_version={result.schema_version}, "
            f"exported={result.exported_count}"
            + (
                f", live={result.live_session_count}"
                if result.live_session_count is not None
                else ""
            )
            + ")"
        )
    else:
        result.summary = "; ".join(result.errors)

    return result
