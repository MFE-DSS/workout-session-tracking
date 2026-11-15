"""Regression witnesses for independent review P2 backend/schema boundaries."""

import pytest
from nutrition_helpers import nutrition_db, nutrition_environment, proof
from sqlalchemy import CheckConstraint, ForeignKeyConstraint, MetaData, create_engine
from sqlalchemy.orm import Session
from test_nutrition_transactions import apply, prepared


@pytest.fixture(autouse=True)
def controlled_environment(monkeypatch):
    with nutrition_environment(monkeypatch):
        yield


def test_tokens_and_cursors_do_not_cross_backend_or_schema(tmp_path, monkeypatch):
    from app.config import get_settings
    from app.services.nutrition_commands import NutritionError, owned_head
    from app.services.nutrition_consent import read_consent, set_consent
    from app.services.nutrition_reads import read_days

    with nutrition_db(tmp_path) as db:
        apply(db, prepared(db, key="2026-11-11", request="one"), key="2026-11-11")
        apply(db, prepared(db))
        a = read_days(db, 1, "2026-11-11", "2026-11-12", limit=1)
        _, absent = owned_head(db, 1, "DAY", "2026-11-10")
        _, present = owned_head(db, 1, "DAY", "2026-11-12")
        consent = read_consent(db, 1)
        monkeypatch.setenv("NUTRITION_BACKEND_IDENTITY", "synthetic-backend-b")
        get_settings.cache_clear()
        assert absent != owned_head(db, 1, "DAY", "2026-11-10")[1]
        assert present != owned_head(db, 1, "DAY", "2026-11-12")[1]
        assert consent["consent_token"] != read_consent(db, 1)["consent_token"]
        with pytest.raises(NutritionError, match="foreign_or_missing"):
            read_days(db, 1, "2026-11-11", "2026-11-12", limit=1, cursor=a["next_cursor"])
        with pytest.raises(NutritionError, match="stale_consent"):
            set_consent(db, 1, consent["consent_token"], False, 1, auth_proof=proof(db))
        old_command = prepared(db, request="stale-backend", values={"kcal_milli": 2200000})
        old_command["expected_head_token"] = present
        with pytest.raises(NutritionError, match="stale_head"):
            apply(db, old_command)
        b = read_days(db, 1, "2026-11-11", "2026-11-12", limit=1)
        import app.services.nutrition_identity as identity

        monkeypatch.setattr(identity, "SCHEMA", "incompatible-synthetic-schema")
        with pytest.raises(NutritionError, match="foreign_or_missing"):
            read_days(db, 1, "2026-11-11", "2026-11-12", limit=1, cursor=b["next_cursor"])


def test_missing_explicit_backend_identity_or_signing_secret_is_unavailable(tmp_path, monkeypatch):
    from app.config import get_settings
    from app.services.nutrition_commands import NutritionError, owned_head

    with nutrition_db(tmp_path) as db:
        monkeypatch.setenv("NUTRITION_BACKEND_IDENTITY", "")
        get_settings.cache_clear()
        with pytest.raises(NutritionError, match="storage_unavailable"):
            owned_head(db, 1, "DAY", "2026-11-12")
        monkeypatch.setenv("NUTRITION_BACKEND_IDENTITY", "synthetic-restored")
        monkeypatch.setenv("NUTRITION_SIGNING_KEY", "")
        get_settings.cache_clear()
        with pytest.raises(NutritionError, match="storage_unavailable"):
            owned_head(db, 1, "DAY", "2026-11-12")


@pytest.mark.parametrize("damage", ["checks", "foreign_keys", "unique_columns", "nullable", "index", "pk", "check_literal"])
def test_schema_probe_refuses_weakened_same_name_tables(damage):
    from app.models.nutrition import NutritionDayRevision, NutritionTargetRevision
    from app.models.user import User
    from app.routers.mobile_nutrition import _available

    metadata = MetaData()
    for model in (User, NutritionTargetRevision, NutritionDayRevision):
        model.__table__.to_metadata(metadata)
    table = metadata.tables[NutritionDayRevision.__tablename__]
    for constraint in list(table.constraints):
        if damage == "checks" and isinstance(constraint, CheckConstraint):
            table.constraints.remove(constraint)
        if damage == "check_literal" and constraint.name == "ck_nutrition_day_state":
            table.constraints.remove(constraint)
            table.append_constraint(CheckConstraint(str(constraint.sqltext).replace("'ACTIVE'", "'active'"), name=constraint.name))
        if damage == "foreign_keys" and isinstance(constraint, ForeignKeyConstraint):
            table.constraints.remove(constraint)
        if damage == "unique_columns" and constraint.name == "uq_nutrition_day_request":
            from sqlalchemy import UniqueConstraint

            table.constraints.remove(constraint)
            table.append_constraint(UniqueConstraint("user_id", "timezone", name=constraint.name))
    if damage == "nullable":
        table.c.user_id.nullable = True
    if damage == "index":
        table.indexes.clear()
    if damage == "pk":
        table.c.id.type = __import__("sqlalchemy").BigInteger()
        table.dialect_options["sqlite"]["autoincrement"] = False
    engine = create_engine("sqlite://")
    try:
        metadata.create_all(engine)
        with Session(engine) as db:
            assert _available(db) is False
    finally:
        engine.dispose()


def test_actual_startup_keeps_body_and_nutrition_schema_migration_only(tmp_path, monkeypatch):
    from sqlalchemy import inspect
    from sqlalchemy.orm import sessionmaker

    from app import database, models  # noqa: F401

    engine = create_engine(f"sqlite:///{tmp_path / 'startup.sqlite'}")
    try:
        monkeypatch.setattr(database, "engine", engine)
        monkeypatch.setattr(database, "SessionLocal", sessionmaker(bind=engine))
        database.init_db()
        tables = set(inspect(engine).get_table_names())
        assert {"users", "body_measurements"} <= tables
        migration_only = {
            "body_measurement_operations_v1",
            "nutrition_day_revisions_v1",
            "nutrition_target_revisions_v1",
        }
        assert tables.isdisjoint(migration_only), tables & migration_only
    finally:
        engine.dispose()
