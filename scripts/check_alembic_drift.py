"""CLI-style manual drift check.

Usage:
  python -m scripts.check_alembic_drift

Exits 0 if Base.metadata matches the migration head, 1 otherwise.
Prints a human-readable diff if drift is detected.

This duplicates the logic of `tests/test_alembic_drift.py` so it
can be invoked as a pre-commit or git hook without pytest being
installed.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path


def main() -> int:
    from alembic import command
    from alembic.autogenerate import compare_metadata
    from alembic.config import Config
    from alembic.migration import MigrationContext
    from sqlalchemy import create_engine

    from app.database import Base
    from app.models import catalog as _catalog  # noqa: F401
    from app.models import session as _session  # noqa: F401

    tmp_dir = tempfile.mkdtemp(prefix="alembic-drift-")
    db_path = Path(tmp_dir) / "drift.db"
    url = f"sqlite:///{db_path}"

    repo_root = Path(__file__).resolve().parent.parent
    cfg = Config(str(repo_root / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", url)

    try:
        command.upgrade(cfg, "head")
        engine = create_engine(url)
        try:
            with engine.connect() as conn:
                mc = MigrationContext.configure(
                    conn,
                    opts={"compare_type": True, "render_as_batch": True},
                )
                diffs = compare_metadata(mc, Base.metadata)
        finally:
            engine.dispose()
    finally:
        if db_path.exists():
            os.unlink(db_path)
        try:
            os.rmdir(tmp_dir)
        except OSError:
            pass

    if not diffs:
        print("Alembic drift check: OK (no diff).")
        return 0

    print("Alembic drift check: DRIFT DETECTED")
    for d in diffs:
        print(f"  - {d!r}")
    print(
        "\nRun:\n"
        "  alembic revision --autogenerate -m \"describe your change\"\n"
        "then review the generated file and run `alembic upgrade head`."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
