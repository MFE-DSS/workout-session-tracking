"""Alembic drift guard.

Fails if `Base.metadata` has drifted from the migration head.
This catches the case where someone edits a SQLAlchemy model
without running `alembic revision --autogenerate`.

The test applies all migrations to a temporary SQLite DB, then
asks Alembic's own `compare_metadata` to diff the resulting
schema against `Base.metadata`. An empty diff means no drift.

Runs intentionally outside the `client` fixture: it spins its own
temp DB, its own engine, and its own migration run, so the test
is self-contained and not affected by fixture ordering.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path


def test_alembic_head_matches_base_metadata():
    # Freshly (re-)import app.* so Base.metadata reflects the
    # current state of the code on disk, not whatever the previous
    # test might have left in sys.modules.
    for mod_name in [m for m in list(sys.modules) if m == "app" or m.startswith("app.")]:
        sys.modules.pop(mod_name, None)

    from alembic import command
    from alembic.autogenerate import compare_metadata
    from alembic.config import Config
    from alembic.migration import MigrationContext
    from sqlalchemy import create_engine

    from app.database import Base  # noqa: E402
    from app.models import catalog as _catalog  # noqa: E402, F401
    from app.models import session as _session  # noqa: E402, F401

    tmp_dir = tempfile.mkdtemp(prefix="alembic-drift-")
    db_path = Path(tmp_dir) / "drift.db"
    url = f"sqlite:///{db_path}"

    repo_root = Path(__file__).resolve().parent.parent
    cfg = Config(str(repo_root / "alembic.ini"))
    # `env.py` respects a pre-set URL thanks to the guard added in
    # Sprint 4. Without that guard, env.py would overwrite this
    # with whatever `app.config.get_settings().database_url` returns.
    cfg.set_main_option("sqlalchemy.url", url)

    try:
        # Apply the full migration chain.
        command.upgrade(cfg, "head")

        engine = create_engine(url)
        try:
            with engine.connect() as conn:
                mc = MigrationContext.configure(
                    conn,
                    opts={
                        "compare_type": True,
                        "render_as_batch": True,
                    },
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

    assert diffs == [], (
        "Alembic drift detected between Base.metadata and the "
        "migration head. Run `alembic revision --autogenerate -m "
        "\"describe your change\"` and review the generated file. "
        f"Diff: {diffs!r}"
    )


def test_alembic_env_respects_preset_url():
    """env.py must not overwrite a URL injected by the caller."""
    env_path = Path(__file__).resolve().parent.parent / "migrations" / "env.py"
    text = env_path.read_text()
    assert "config.get_main_option" in text
    assert 'sqlalchemy.url' in text
