"""Restore the latest JSON backup into the live database.

Usage:
  python -m scripts.restore_latest_backup

Reads `BACKUP_DIR` (defaults to `<repo>/var/backups`), finds the
newest `sessions-*.json` file, validates its shape, and INSERTs
every session into the database.

Safety:
  - REFUSES to run if the target DB already has sessions. The
    operator must wipe the DB first (`rm var/workout.db` then
    `alembic upgrade head`).
  - Validates the payload shape before touching the DB.
  - Commits only on success; rolls back entirely on failure.

Exit codes:
  0  - restore succeeded, all sessions inserted and validated
  1  - any failure (no backup, corrupt file, shape mismatch,
       non-empty DB, post-restore sanity failure, ...)
"""
from __future__ import annotations

import json
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


def _newest_json(backup_dir: Path) -> Path | None:
    if not backup_dir.is_dir():
        return None
    files = list(backup_dir.glob("sessions-*.json"))
    if not files:
        return None
    return max(files, key=lambda f: f.stat().st_mtime)


def main() -> int:
    from app.database import SessionLocal
    from app.services.restore import restore_from_json_payload

    backup_dir = _backup_dir()
    target = _newest_json(backup_dir)

    if target is None:
        print(
            f"restore: FAIL — no JSON backup found in {backup_dir}",
            file=sys.stderr,
        )
        return 1

    print(f"restore: source file = {target.name}")

    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"restore: FAIL — cannot read JSON: {exc}", file=sys.stderr)
        return 1

    with SessionLocal() as db:
        result = restore_from_json_payload(db, payload)

        if result.ok:
            db.commit()
            print(f"restore: OK — {result.summary}")

            # Post-commit verification: re-read one session to prove
            # data is exploitable.
            from sqlalchemy import select
            from app.models.session import WorkoutSession

            first = db.execute(
                select(WorkoutSession).limit(1)
            ).scalar_one_or_none()
            if first is not None:
                print(
                    f"  verify: first session = "
                    f"{first.template_name_snapshot} "
                    f"started_at={first.started_at}"
                )
            else:
                print("  verify: DB is empty (0 sessions restored)")
            return 0
        else:
            db.rollback()
            print(f"restore: FAIL — {result.summary}")
            for err in result.errors:
                print(f"  - {err}")
            return 1


if __name__ == "__main__":
    raise SystemExit(main())
