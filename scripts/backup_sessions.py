"""Standalone nightly backup helper.

Writes a JSON dump and a CSV dump of the workout journal to a
local directory, then prunes anything older than the retention
window. Suitable for cron, systemd timer, or manual runs.

Configuration (in order of precedence):
  - $BACKUP_DIR              env var, fallback `<repo>/var/backups`
  - $BACKUP_RETENTION_DAYS   env var, fallback 30 (0 = keep forever)

The script does NOT go through HTTP. It opens its own SQLAlchemy
session and reuses `app.services.export_builder` to produce the
exact same bytes the web routes would.

Filenames carry a UTC timestamp:
  sessions-YYYYMMDD_HHMM.json
  sessions-YYYYMMDD_HHMM.csv

Exit codes:
  0  - both files written successfully
  1  - any failure (DB unreachable, write error, etc.)
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Make `app.*` importable when running as `python -m scripts.backup_sessions`.
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def _backup_dir() -> Path:
    raw = os.environ.get("BACKUP_DIR")
    if raw:
        return Path(raw)
    return REPO_ROOT / "var" / "backups"


def _retention_days() -> int:
    try:
        return int(os.environ.get("BACKUP_RETENTION_DAYS", "30"))
    except ValueError:
        return 30


def _prune_old(directory: Path, days: int) -> int:
    if days <= 0:
        return 0
    cutoff = time.time() - days * 86400
    pruned = 0
    for pattern in ("sessions-*.json", "sessions-*.csv"):
        for f in directory.glob(pattern):
            try:
                if f.stat().st_mtime < cutoff:
                    f.unlink()
                    pruned += 1
            except OSError:
                pass
    return pruned


def main() -> int:
    backup_dir = _backup_dir()
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Imports happen AFTER sys.path tweak.
    from app.database import SessionLocal
    from app.services.export_builder import build_csv_text, build_json_payload

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    json_path = backup_dir / f"sessions-{stamp}.json"
    csv_path = backup_dir / f"sessions-{stamp}.csv"

    try:
        with SessionLocal() as db:
            json_payload = build_json_payload(db)
            csv_text = build_csv_text(db)
    except Exception as exc:  # pragma: no cover
        print(f"backup_sessions: DB read failed: {exc}", file=sys.stderr)
        return 1

    try:
        json_path.write_text(
            json.dumps(json_payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        csv_path.write_text(csv_text, encoding="utf-8")
    except OSError as exc:  # pragma: no cover
        print(f"backup_sessions: write failed: {exc}", file=sys.stderr)
        return 1

    pruned = _prune_old(backup_dir, _retention_days())
    print(
        f"backup_sessions: wrote {json_path.name} ({json_path.stat().st_size} B) "
        f"and {csv_path.name} ({csv_path.stat().st_size} B); "
        f"pruned {pruned} old file(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
