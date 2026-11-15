"""MOB07 additive migration and mandatory no-startup-DDL boundary."""

import pytest
from alembic import command
from sqlalchemy import inspect, text
from test_body_operations_migration import migration_config


def test_receipts_are_not_created_by_startup(client):
    from app.database import engine

    assert "program_builder_operations_v1" not in inspect(engine).get_table_names()


def test_populated_parent_upgrade_empty_roundtrip_preserves_source(tmp_path):
    cfg, engine = migration_config(tmp_path)
    try:
        command.upgrade(cfg, "nutrition_manual_01")
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO users (id,username,password_hash,is_active,session_epoch) VALUES (1,'builder-migration','synthetic',1,0)"
                )
            )
            connection.execute(
                text(
                    "INSERT INTO user_programs (id,user_id,title,slug_base,status) VALUES (1,1,'Historique','historique','draft')"
                )
            )
            before = [tuple(r) for r in connection.execute(text("SELECT * FROM user_programs"))]
        command.upgrade(cfg, "program_builder_operations_01")
        schema = inspect(engine)
        # Refresh a pre-existing SQLite connection schema cache after another
        # Alembic connection changed it, before index/unique introspection.
        assert "program_builder_operations_v1" in schema.get_table_names()
        assert schema.get_unique_constraints("program_builder_operations_v1")[0][
            "column_names"
        ] == ["user_id", "command_id"]
        assert {
            tuple(fk["constrained_columns"])
            for fk in schema.get_foreign_keys("program_builder_operations_v1")
        } == {("user_id",), ("program_id",)}
        assert schema.get_indexes("program_builder_operations_v1")[0]["column_names"] == [
            "user_id",
            "program_id",
            "id",
        ]
        with engine.connect() as connection:
            assert [
                tuple(r) for r in connection.execute(text("SELECT * FROM user_programs"))
            ] == before
            assert (
                connection.scalar(text("SELECT count(*) FROM program_builder_operations_v1")) == 0
            )
        command.downgrade(cfg, "nutrition_manual_01")
        assert "program_builder_operations_v1" not in inspect(engine).get_table_names()
        with engine.connect() as connection:
            assert [
                tuple(r) for r in connection.execute(text("SELECT * FROM user_programs"))
            ] == before
    finally:
        engine.dispose()


def test_populated_receipts_refuse_downgrade(tmp_path):
    cfg, engine = migration_config(tmp_path)
    try:
        command.upgrade(cfg, "program_builder_operations_01")
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO users (id,username,password_hash,is_active,session_epoch) VALUES (1,'builder-migration','synthetic',1,0)"
                )
            )
            connection.execute(
                text(
                    "INSERT INTO program_builder_operations_v1 (id,user_id,command_id,operation,request_sha256,source_digest_after,result_version,result_json) VALUES (1,1,'historic','CREATE',:digest,:digest,1,'{}')"
                ),
                {"digest": "a" * 64},
            )
        with pytest.raises(RuntimeError, match="receipts are not empty"):
            command.downgrade(cfg, "nutrition_manual_01")
        with engine.connect() as connection:
            assert (
                connection.scalar(text("SELECT count(*) FROM program_builder_operations_v1")) == 1
            )
            assert (
                connection.scalar(text("SELECT version_num FROM alembic_version"))
                == "program_builder_operations_01"
            )
    finally:
        engine.dispose()
