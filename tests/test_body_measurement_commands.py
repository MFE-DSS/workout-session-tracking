"""BODY-01: real canonical facts, lineage and transaction boundaries."""

from datetime import UTC, datetime

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session


@pytest.fixture()
def body_db(tmp_path):
    from app import models  # noqa: F401
    from app.database import Base
    from app.models.user import User
    from app.services.body_profile import set_consent

    engine = create_engine(f"sqlite:///{tmp_path / 'body.db'}")
    Base.metadata.create_all(engine)
    with Session(engine, autoflush=False) as db:
        db.add_all(
            [
                User(id=1, username="body-owner", password_hash="not-an-actual-password"),
                User(id=2, username="body-other", password_hash="not-an-actual-password"),
            ]
        )
        db.commit()
        set_consent(db, 1, True)
        yield db
    engine.dispose()


def create(db, *, request_id="body-create", owner=1, values=None):
    from app.services.body_measurement_commands import apply_command

    return apply_command(
        db,
        owner,
        {
            "request_id": request_id,
            "operation": "CREATE",
            "measured_on": "2025-01-02",
            "values": {"weight_kg": 80, "waist_cm": 90} if values is None else values,
        },
        source="MANUAL_ENTRY",
    )


def correction(db, root, values, *, request_id="body-correct", token=None, date=None):
    from app.services.body_measurement_commands import apply_command
    from app.services.body_measurement_reads import owned_head

    command = {
        "request_id": request_id,
        "operation": "CORRECT",
        "root_ref": root,
        "expected_head_token": token or owned_head(db, 1, root)[1],
        "values": values,
    }
    if date:
        command["measured_on"] = date
    return apply_command(db, 1, command, source="MANUAL_CORRECTION")


def test_correction_preserves_original_and_replaces_only_current_head(body_db):
    from app.models.measurement import BodyMeasurement
    from app.services.body_measurement_reads import current_measurement_predicate

    first = create(body_db)
    original = body_db.get(BodyMeasurement, first["measurement_id"])
    timestamp = original.created_at
    fixed = correction(body_db, first["root_ref"], {"waist_cm": 85})
    body_db.expire_all()
    assert original.waist_cm == 90
    assert original.created_at == timestamp
    assert fixed["root_ref"] == first["root_ref"]
    assert fixed["measurement_id"] != original.id
    rows = list(body_db.scalars(select(BodyMeasurement).where(current_measurement_predicate())))
    assert [(r.weight_kg, r.waist_cm) for r in rows] == [(80, 85)]
    assert len(list(body_db.scalars(select(BodyMeasurement)))) == 2


def test_null_and_date_correction_do_not_create_independent_observation(body_db):
    from app.services.body_measurement_reads import owned_head

    first = create(body_db)
    fixed = correction(body_db, first["root_ref"], {"weight_kg": None}, date="2025-01-01")
    row, _, revision = owned_head(body_db, 1, first["root_ref"])
    assert row.weight_kg is None
    assert row.waist_cm == 90
    assert row.measured_at.date().isoformat() == "2025-01-01"
    assert revision == 2
    assert fixed["root_ref"] == first["root_ref"]


def test_stale_head_refuses_second_correction(body_db):
    from app.services.body_measurement_commands import BodyCommandError
    from app.services.body_measurement_reads import owned_head

    first = create(body_db)
    token = owned_head(body_db, 1, first["root_ref"])[1]
    correction(body_db, first["root_ref"], {"weight_kg": 81}, token=token)
    with pytest.raises(BodyCommandError, match="head_conflict"):
        correction(body_db, first["root_ref"], {"weight_kg": 82}, token=token, request_id="stale")


def test_exact_replay_returns_original_receipt_after_later_correction(body_db):
    first = create(body_db)
    correction(body_db, first["root_ref"], {"weight_kg": 81})
    assert create(body_db) == first


def test_idempotency_mismatch_is_not_a_new_fact(body_db):
    from app.models.measurement import BodyMeasurement
    from app.services.body_measurement_commands import BodyCommandError

    create(body_db)
    with pytest.raises(BodyCommandError, match="idempotency_mismatch"):
        create(body_db, values={"weight_kg": 82})
    assert len(list(body_db.scalars(select(BodyMeasurement)))) == 1


@pytest.mark.parametrize(
    "values",
    [
        {"weight_kg": True},
        {"weight_kg": float("inf")},
        {"weight_kg": float("nan")},
        {"weight_kg": 10**500},
        {"weight_kg": 1},
        {"unknown": 80},
        {},
        {"weight_kg": None},
    ],
)
def test_invalid_command_never_creates_half_fact(body_db, values):
    from app.models.measurement import BodyMeasurement
    from app.services.body_measurement_commands import BodyCommandError

    with pytest.raises(BodyCommandError):
        create(body_db, values=values)
    assert list(body_db.scalars(select(BodyMeasurement))) == []


def test_erasure_removes_whole_lineage_and_reserves_identity(body_db):
    from app.models.measurement import BodyMeasurement
    from app.services.body_measurement_commands import apply_command
    from app.services.body_measurement_reads import owned_head

    first = create(body_db)
    fixed = correction(body_db, first["root_ref"], {"weight_kg": 81})
    command = {
        "operation": "ERASE",
        "request_id": "erase-all-versions",
        "root_ref": first["root_ref"],
        "expected_head_token": owned_head(body_db, 1, first["root_ref"])[1],
        "confirm_all_versions": True,
    }
    receipt = apply_command(body_db, 1, command, source="MANUAL_ENTRY")
    assert receipt["state"] == "ERASED"
    assert list(body_db.scalars(select(BodyMeasurement))) == []
    next_fact = create(body_db, request_id="new-after-erasure")
    assert next_fact["measurement_id"] > fixed["measurement_id"]
    assert apply_command(body_db, 1, command, source="MANUAL_ENTRY") == receipt


def test_foreign_root_is_indistinguishable_from_unknown(body_db):
    from app.services.body_measurement_commands import BodyCommandError, apply_command

    first = create(body_db)
    for root in [first["root_ref"], 999999]:
        with pytest.raises(BodyCommandError) as error:
            apply_command(
                body_db,
                2,
                {
                    "operation": "CORRECT",
                    "request_id": f"foreign-{root}",
                    "root_ref": root,
                    "expected_head_token": "arbitrary",
                    "values": {"weight_kg": 81},
                },
                source="MANUAL_CORRECTION",
                require_consent=False,
            )
        assert (error.value.code, error.value.status) == ("measurement_not_found", 404)


def test_legacy_row_becomes_version_zero_without_rewriting_old_acquisition(body_db):
    from app.models.measurement import BodyMeasurement
    from app.services.body_measurement_reads import owned_head

    legacy = BodyMeasurement(
        user_id=1, measured_at=datetime(2020, 1, 1, tzinfo=UTC), weight_kg=800, waist_cm=90
    )
    body_db.add(legacy)
    body_db.commit()
    _, _, revision = owned_head(body_db, 1, legacy.id)
    assert revision == 0
    correction(body_db, legacy.id, {"waist_cm": 85})
    current, _, revision = owned_head(body_db, 1, legacy.id)
    assert current.weight_kg == 800
    assert revision == 1
    body_db.refresh(legacy)
    assert legacy.waist_cm == 90


def test_two_connections_cannot_branch_a_head(body_db):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    from app.models.measurement import BodyMeasurement
    from app.services.body_measurement_commands import BodyCommandError, apply_command
    from app.services.body_measurement_reads import owned_head

    first = create(body_db)
    token = owned_head(body_db, 1, first["root_ref"])[1]
    body_db.rollback()
    barrier = Barrier(2)
    engine = body_db.get_bind()

    def attempt(n):
        with Session(engine, autoflush=False) as db:
            barrier.wait()
            try:
                return apply_command(
                    db,
                    1,
                    {
                        "operation": "CORRECT",
                        "request_id": f"parallel-{n}",
                        "root_ref": first["root_ref"],
                        "expected_head_token": token,
                        "values": {"weight_kg": 81 + n},
                    },
                    source="MANUAL_CORRECTION",
                )["state"]
            except BodyCommandError as exc:
                return exc.code

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(attempt, range(2)))
    assert sorted(results) == ["APPLIED", "head_conflict"]
    assert len(list(body_db.scalars(select(BodyMeasurement)))) == 2


def test_failure_between_fact_and_receipt_leaves_no_partial_fact(body_db):
    from sqlalchemy import event

    from app.models.body_measurement_operation import BodyMeasurementOperation
    from app.models.measurement import BodyMeasurement

    def fail_receipt(*args):
        raise RuntimeError("synthetic receipt storage failure")

    event.listen(BodyMeasurementOperation, "before_insert", fail_receipt)
    try:
        with pytest.raises(RuntimeError, match="synthetic receipt storage failure"):
            create(body_db)
    finally:
        event.remove(BodyMeasurementOperation, "before_insert", fail_receipt)
    assert list(body_db.scalars(select(BodyMeasurement))) == []


def test_receipt_replay_after_withdrawal_is_not_a_new_permission(body_db):
    from app.services.body_measurement_commands import BodyCommandError
    from app.services.body_profile import set_consent

    first = create(body_db)
    set_consent(body_db, 1, False)
    assert create(body_db) == first
    with pytest.raises(BodyCommandError, match="body_consent_required"):
        create(body_db, request_id="new-after-withdrawal")


def test_missing_schema_fails_closed_without_startup_ddl(body_db):
    from app.models.body_measurement_operation import BodyMeasurementOperation
    from app.services.body_measurement_commands import BodyCommandError

    BodyMeasurementOperation.__table__.drop(body_db.get_bind())
    with pytest.raises(BodyCommandError, match="body_schema_unavailable"):
        create(body_db)


@pytest.mark.parametrize("key", ["contains/slash", "contains space", "\t", "é"])
def test_command_keys_are_safe_for_durable_receipt_lookup(body_db, key):
    from app.services.body_measurement_commands import BodyCommandError

    with pytest.raises(BodyCommandError, match="invalid_request_id"):
        create(body_db, request_id=key)


def test_replay_precedes_changed_plausibility_bounds(body_db, monkeypatch):
    from app.services import body_profile
    from app.services.body_measurement_commands import BodyCommandError

    first = create(body_db)
    specs = [body_profile.FieldSpec(spec.key, spec.label, 100, spec.max) if spec.key == "weight_kg" else spec
             for spec in body_profile.BODY_MEASUREMENT_FIELDS]
    monkeypatch.setattr(body_profile, "BODY_MEASUREMENT_FIELDS", specs)
    assert create(body_db) == first
    with pytest.raises(BodyCommandError, match="invalid_measurement_value"):
        create(body_db, request_id="new-under-changed-bounds")


def test_legacy_calf_only_record_keeps_its_fact_when_correcting_the_day(body_db):
    from app.models.measurement import BodyMeasurement
    from app.services.body_measurement_reads import owned_head

    row = BodyMeasurement(user_id=1, measured_at=datetime(2020, 1, 1, tzinfo=UTC), calf_cm=37)
    body_db.add(row)
    body_db.commit()
    correction(body_db, row.id, {}, date="2020-01-02")
    current, _, _ = owned_head(body_db, 1, row.id)
    assert current.calf_cm == 37
    assert current.measured_at.date().isoformat() == "2020-01-02"
    body_db.refresh(row)
    assert row.measured_at.date().isoformat() == "2020-01-01"


def test_resubmitted_legacy_number_is_not_a_fresh_acquisition(body_db):
    from app.models.body_measurement_operation import BodyMeasurementOperation
    from app.models.measurement import BodyMeasurement
    from app.services.body_measurement_commands import BodyCommandError
    from app.services.body_measurement_reads import owned_head

    original = BodyMeasurement(
        user_id=1, measured_at=datetime(2020, 1, 1, tzinfo=UTC), weight_kg=800, waist_cm=90
    )
    body_db.add(original)
    body_db.commit()
    receipt = correction(body_db, original.id, {"weight_kg": 800, "waist_cm": 85})
    head, _, _ = owned_head(body_db, 1, original.id)
    assert (head.weight_kg, head.waist_cm) == (800, 85)
    body_db.refresh(original)
    assert (original.weight_kg, original.waist_cm) == (800, 90)
    operation = body_db.scalar(
        select(BodyMeasurementOperation).where(
            BodyMeasurementOperation.request_id == "body-correct"
        )
    )
    assert operation.changed_fields == ["waist_cm"]
    assert set(operation.provenance_by_changed_field) == {"waist_cm"}
    assert receipt["measurement_id"] != original.id
    with pytest.raises(BodyCommandError, match="invalid_measurement_value"):
        correction(body_db, original.id, {"weight_kg": 801}, request_id="new-invalid-change")
    with pytest.raises(BodyCommandError, match="invalid_measurement_value"):
        create(body_db, request_id="new-invalid-fact", values={"weight_kg": 800})


def test_retained_consent_cannot_authorize_fresh_mutation_after_concurrent_withdrawal(body_db):
    from app.services.body_measurement_reads import BodyCommandError
    from app.services.body_profile import get_consent, set_consent

    retained = get_consent(body_db, 1)
    assert retained.granted is True
    with Session(body_db.get_bind()) as other:
        set_consent(other, 1, False)
    assert retained.granted is True  # Deliberately stale identity-map evidence.
    with pytest.raises(BodyCommandError, match="body_consent_required"):
        create(body_db, request_id="fresh-after-concurrent-withdrawal")


def test_actual_startup_leaves_body_lineage_migration_only(tmp_path, monkeypatch):
    from sqlalchemy import inspect
    from sqlalchemy.orm import sessionmaker

    from app import database, models  # noqa: F401

    engine = create_engine(f"sqlite:///{tmp_path / 'startup.db'}")
    try:
        monkeypatch.setattr(database, "engine", engine)
        monkeypatch.setattr(database, "SessionLocal", sessionmaker(bind=engine))
        database.init_db()
        tables = inspect(engine).get_table_names()
        assert "users" in tables and "body_measurements" in tables
        assert "body_measurement_operations_v1" not in tables
    finally:
        engine.dispose()
