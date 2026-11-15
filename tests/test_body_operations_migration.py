"""BODY-01 migration preserves observations and refuses destructive rollback."""

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session


def migration_config(tmp_path):
    cfg = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    url = f"sqlite:///{tmp_path / 'migrated.db'}"
    cfg.set_main_option("sqlalchemy.url", url)
    return cfg, create_engine(url)


def test_additive_upgrade_preserves_existing_measurement_and_ddl(tmp_path):
    from app.models.measurement import BodyMeasurement
    from app.models.user import User

    cfg, engine = migration_config(tmp_path)
    command.upgrade(cfg, "plan_v3_20261107_01")
    with Session(engine) as db:
        db.add(User(id=1, username="legacy", password_hash="synthetic"))
        db.commit()
        db.execute(
            text(
                "INSERT INTO body_measurements (id,user_id,measured_at,weight_kg) VALUES (7,1,'2020-01-02',800)"
            )
        )
        db.commit()
        before = tuple(db.execute(text("SELECT * FROM body_measurements")).one())
        ddl = db.scalar(text("SELECT sql FROM sqlite_master WHERE name='body_measurements'"))
    command.upgrade(cfg, "head")
    assert "body_measurement_operations_v1" in inspect(engine).get_table_names()
    with Session(engine) as db:
        assert tuple(db.execute(text("SELECT * FROM body_measurements")).one()) == before
        assert (
            db.scalar(text("SELECT sql FROM sqlite_master WHERE name='body_measurements'")) == ddl
        )
        assert db.scalar(text("SELECT count(*) FROM body_measurement_operations_v1")) == 0
        row = db.get(BodyMeasurement, 7)
        assert row.weight_kg == 800
    engine.dispose()


def test_nonempty_lineage_prevents_destructive_downgrade(tmp_path):
    from app.models.user import User
    from app.services.body_measurement_commands import apply_command

    cfg, engine = migration_config(tmp_path)
    command.upgrade(cfg, "head")
    with Session(engine) as db:
        db.add(User(id=1, username="migration-test", password_hash="synthetic"))
        db.commit()
        apply_command(
            db,
            1,
            {
                "operation": "CREATE",
                "request_id": "migration-fact",
                "measured_on": "2020-01-02",
                "values": {"weight_kg": 80},
            },
            source="MANUAL_ENTRY",
            require_consent=False,
        )
    with pytest.raises(RuntimeError, match="BODY lineage is not empty"):
        # Pin BODY parent even when a later child is present.
        command.downgrade(cfg, "plan_v3_20261107_01")
    with engine.connect() as conn:
        assert conn.scalar(text("SELECT count(*) FROM body_measurements")) == 1
        assert conn.scalar(text("SELECT count(*) FROM body_measurement_operations_v1")) == 1
    engine.dispose()
