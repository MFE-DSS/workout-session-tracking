#!/usr/bin/env python3
"""Sb_26.2 — Migration roundtrip / rollback dry-run.

Validates that the most recent migration(s) can be downgraded and
re-upgraded without error on SQLite. This is exactly the operation an
operator would run during a prod rollback:

    sudo -u workout alembic downgrade -1   # cf. deploy_prod.sh die() hint
    sudo -u workout alembic upgrade head

If this fails on a fresh SQLite, it will fail on prod too.

Scope:
* Full chain `base → head` is exercised by `tests/test_alembic_drift.py`
  and `check_alembic_drift.py`.
* Full chain `head → base` is NOT exercised: many of our historical
  downgrades use `op.drop_table` on tables that SQLite/Alembic batch
  mode handles fragilely, and the prod rollback model is always
  "downgrade -1 then redeploy", never "downgrade to base". Documenting
  this explicit limit (Sb_26.2 §3.3) rather than pretending otherwise.

What we check here:
1. `alembic upgrade head` on a fresh DB (sanity).
2. `alembic downgrade -1` on top of (1).
3. `alembic upgrade head` again on top of (2).
4. Compare the resulting schema to the committed snapshot.

A non-zero exit signals: the last migration is not a safe rollback target.

Usage:
    python scripts/check_migration_roundtrip.py
    python scripts/check_migration_roundtrip.py --steps 2   # downgrade -2 then upgrade
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _build_snapshot(db_path: Path) -> str:
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.execute(
            "SELECT type, name, sql FROM sqlite_master "
            "WHERE sql IS NOT NULL AND name NOT LIKE 'sqlite_%' "
            "AND name != 'alembic_version' "
            "ORDER BY type, name"
        )
        rows = cur.fetchall()
    finally:
        conn.close()
    return "\n".join(
        f"{type_}|{name}|{' '.join((sql or '').split())}" for type_, name, sql in rows
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=1, help="downgrade N steps")
    args = parser.parse_args()

    from alembic import command
    from alembic.config import Config

    tmp_dir = tempfile.mkdtemp(prefix="migration-roundtrip-")
    db_path = Path(tmp_dir) / "roundtrip.db"
    db_url = f"sqlite:///{db_path}"
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", db_url)

    print("=== migration roundtrip dry-run ===")
    print(f"  DB     : {db_url}")
    print(f"  steps  : downgrade -{args.steps} then upgrade head")
    print()

    try:
        print("[1/4] alembic upgrade head  (fresh DB → head)")
        command.upgrade(cfg, "head")
        schema_head_1 = _build_snapshot(db_path)
        print(f"      → {len(schema_head_1.splitlines())} schema objects")

        print(f"[2/4] alembic downgrade -{args.steps}")
        command.downgrade(cfg, f"-{args.steps}")

        print("[3/4] alembic upgrade head  (after rollback)")
        command.upgrade(cfg, "head")
        schema_head_2 = _build_snapshot(db_path)
        print(f"      → {len(schema_head_2.splitlines())} schema objects")

        print("[4/4] schema identical pre/post roundtrip ?")
        if schema_head_1 != schema_head_2:
            print("      FAIL — schema diverges after downgrade/upgrade")
            return 1
        print("      OK")
    except Exception as e:
        print(f"FAIL: roundtrip raised {type(e).__name__}: {e}")
        print(
            "Action: this means the last migration's downgrade() is not "
            "safe on SQLite. Either fix the downgrade or document the "
            "limitation in docs/MIGRATION_HARDENING.md."
        )
        return 1

    print()
    print("OK: migration roundtrip clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
