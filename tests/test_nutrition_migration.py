"""Actual BODY→NUT migration preserves historical facts and refuses data loss."""

import pytest
from alembic import command
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
from test_body_operations_migration import migration_config


def test_nutrition_upgrade_keeps_populated_body_parent_byte_exact(tmp_path):
    from app.models.user import User
    from app.services.body_measurement_commands import apply_command

    cfg, engine = migration_config(tmp_path)
    try:
        command.upgrade(cfg, "body_measurement_operations_01")
        with Session(engine) as db:
            db.add(User(id=1, username="migration-synthetic", password_hash="synthetic"))
            db.commit()
            apply_command(db, 1, {"operation": "CREATE", "request_id": "body-parent",
                "measured_on": "2020-01-02", "values": {"weight_kg": 80}},
                source="MANUAL_ENTRY", require_consent=False)
            names = ("body_measurements", "body_measurement_operations_v1")
            before = {name: [tuple(row) for row in db.execute(text(f"SELECT * FROM {name}"))]
                      for name in names}
            ddl = {name: db.scalar(text("SELECT sql FROM sqlite_master WHERE name=:name"),
                                  {"name": name}) for name in names}
        command.upgrade(cfg, "nutrition_manual_01")
        assert {"nutrition_day_revisions_v1", "nutrition_target_revisions_v1"} <= set(inspect(engine).get_table_names())
        with Session(engine) as db:
            for name in names:
                assert [tuple(row) for row in db.execute(text(f"SELECT * FROM {name}"))] == before[name]
                assert db.scalar(text("SELECT sql FROM sqlite_master WHERE name=:name"), {"name": name}) == ddl[name]
            assert db.scalar(text("SELECT count(*) FROM nutrition_day_revisions_v1")) == 0
            assert db.scalar(text("SELECT count(*) FROM nutrition_target_revisions_v1")) == 0
        command.downgrade(cfg, "body_measurement_operations_01")
        assert "body_measurement_operations_v1" in inspect(engine).get_table_names()
        assert "nutrition_day_revisions_v1" not in inspect(engine).get_table_names()
        with engine.connect() as conn:
            assert conn.scalar(text("SELECT count(*) FROM body_measurement_operations_v1")) == 1
    finally:
        engine.dispose()


def test_populated_nutrition_refuses_destructive_downgrade(tmp_path):
    from test_nutrition_models import target

    from app.models.user import User

    cfg, engine = migration_config(tmp_path)
    try:
        command.upgrade(cfg, "nutrition_manual_01")
        with Session(engine) as db:
            db.add(User(id=1, username="nutrition-migration", password_hash="synthetic"))
            db.commit()
            db.add(target())
            db.commit()
        with pytest.raises(RuntimeError, match="Nutrition history is not empty"):
            command.downgrade(cfg, "body_measurement_operations_01")
        with engine.connect() as conn:
            assert conn.scalar(text("SELECT count(*) FROM nutrition_target_revisions_v1")) == 1
            assert conn.scalar(text("SELECT version_num FROM alembic_version")) == "nutrition_manual_01"
    finally:
        engine.dispose()
