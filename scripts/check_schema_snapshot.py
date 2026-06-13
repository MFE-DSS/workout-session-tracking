#!/usr/bin/env python3
"""Sb_26.2 — Verify the committed schema snapshot matches alembic head.

Regenerates a snapshot in a temp file and diffs it against
`data/schema_snapshot.sql`. Exits 1 on any drift, printing a unified
diff so the operator sees exactly what changed.

This catches:
* a Python model changed without `alembic revision --autogenerate`
* a migration that doesn't produce the schema the team expects
* a manual ALTER applied to prod that wasn't translated into a migration

Pair with `scripts/check_alembic_drift.py`:
* `check_alembic_drift` : Base.metadata vs alembic head (model side)
* `check_schema_snapshot` : alembic head vs committed snapshot (history side)

Both must pass in CI.

Usage:
    python scripts/check_schema_snapshot.py
"""
from __future__ import annotations

import difflib
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_PATH = ROOT / "data" / "schema_snapshot.sql"


def main() -> int:
    if not SNAPSHOT_PATH.exists():
        print(
            f"FATAL: {SNAPSHOT_PATH} missing. Run "
            "`python scripts/generate_schema_snapshot.py` first.",
            file=sys.stderr,
        )
        return 2

    sys.path.insert(0, str(ROOT / "scripts"))
    from generate_schema_snapshot import _alembic_upgrade, _build_snapshot

    tmp_dir = tempfile.mkdtemp(prefix="schema-snapshot-check-")
    db_path = Path(tmp_dir) / "check.db"
    db_url = f"sqlite:///{db_path}"
    _alembic_upgrade(db_url)
    current = _build_snapshot(db_path)
    committed = SNAPSHOT_PATH.read_text(encoding="utf-8")

    if current == committed:
        print(f"OK: schema snapshot matches alembic head ({SNAPSHOT_PATH.name}).")
        return 0

    print("FAIL: schema snapshot diverges from alembic head.")
    print()
    diff = difflib.unified_diff(
        committed.splitlines(keepends=True),
        current.splitlines(keepends=True),
        fromfile=f"{SNAPSHOT_PATH.name} (committed)",
        tofile="alembic head (current)",
        n=3,
    )
    sys.stdout.writelines(diff)
    print()
    print(
        "Action: if the new migration is intentional, run "
        "`python scripts/generate_schema_snapshot.py` and commit the update."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
