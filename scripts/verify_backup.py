"""Standalone backup integrity verifier.

Usage:
  python -m scripts.verify_backup

Reads `BACKUP_DIR` (defaults to `<repo>/var/backups`) and runs
`app.services.backup_verifier.verify_latest_backup` against the
most recent JSON dump.

Prints a one-line summary plus a per-field block. Exits 0 if the
backup is valid (no fatal errors), 1 otherwise. Suitable for cron
or for a systemd `OnFailure=` chain.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def _backup_dir() -> Path:
    raw = os.environ.get("BACKUP_DIR")
    if raw:
        return Path(raw)
    return REPO_ROOT / "var" / "backups"


def _human_seconds(seconds: float | None) -> str:
    if seconds is None:
        return "—"
    if seconds < 60:
        return f"{int(seconds)} s"
    if seconds < 3600:
        return f"{int(seconds // 60)} min"
    if seconds < 86400:
        return f"{seconds / 3600:.1f} h"
    return f"{seconds / 86400:.1f} j"


def main() -> int:
    from app.database import SessionLocal
    from app.services.backup_verifier import verify_latest_backup

    backup_dir = _backup_dir()
    with SessionLocal() as db:
        result = verify_latest_backup(backup_dir, db=db)

    status = "OK " if result.ok else "FAIL"
    print(f"verify_backup: [{status}] {result.summary}")
    print(f"  backup_dir         : {backup_dir}")
    print(f"  file               : {result.file_name or '—'}")
    print(f"  modified_at        : {result.file_modified_at or '—'}")
    print(f"  age                : {_human_seconds(result.file_age_seconds)}")
    print(f"  size_bytes         : {result.file_size_bytes or '—'}")
    print(f"  schema_version     : {result.schema_version or '—'}")
    print(f"  exported_count     : {result.exported_count if result.exported_count is not None else '—'}")
    print(f"  live_session_count : {result.live_session_count if result.live_session_count is not None else '—'}")

    if result.errors:
        print("  errors:")
        for e in result.errors:
            print(f"    - {e}")

    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
