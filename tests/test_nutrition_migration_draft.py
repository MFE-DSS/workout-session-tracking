"""Exercise frozen migration DDL, independently of ORM create_all defaults."""

import importlib.util
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from test_nutrition_models import day, target


def test_frozen_migration_accepts_both_revision_types_and_records_server_time(tmp_path):
    source = (Path(__file__).parents[1] / "openspec/changes/"
              "nut-01-manual-daily-ledger/migration-draft/nutrition_manual_01.py")
    spec = importlib.util.spec_from_file_location("nutrition_draft_test", source)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    engine = create_engine(f"sqlite:///{tmp_path / 'migration.sqlite'}")
    try:
        with engine.begin() as connection:
            # Only the owned parent identity is required by these two additive tables.
            connection.execute(text("CREATE TABLE users (id INTEGER PRIMARY KEY)"))
            connection.execute(text("INSERT INTO users VALUES (1)"))
            with Operations.context(MigrationContext.configure(connection)):
                migration.upgrade()
        with Session(engine) as db:
            first, second = target(), day()
            db.add_all([first, second])
            db.commit()
            assert first.recorded_at is not None
            assert second.recorded_at is not None
    finally:
        engine.dispose()
