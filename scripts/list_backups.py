"""List the local backup files for sanity / smoke checking.

Usage:
  python -m scripts.list_backups

Honours the same `BACKUP_DIR` env var as `backup_sessions.py`.
Prints one line per file, oldest first, with a total at the end.
Exit code 0 if at least one file is found, 1 otherwise (so it can
be wired into a quick health check).
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


def main() -> int:
    from app.services.backup_inspector import list_backups

    directory = _backup_dir()
    backups = list_backups(directory)
    if not backups:
        print(f"list_backups: no files in {directory}")
        return 1

    print(f"list_backups: {len(backups)} file(s) in {directory}")
    # Oldest first reads more naturally for a manual scan.
    for b in reversed(backups):
        print(
            f"  {b.modified_at.strftime('%Y-%m-%d %H:%M')}  "
            f"{b.size_bytes:>10} B  {b.name}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
