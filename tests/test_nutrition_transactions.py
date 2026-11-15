"""Owned facts and receipts use real file SQLite, never mock scientific targets."""

import copy

import pytest
from nutrition_helpers import nutrition_db, nutrition_environment, proof
from sqlalchemy import select


@pytest.fixture()
def db(tmp_path):
    with nutrition_db(tmp_path) as session:
        yield session


@pytest.fixture(autouse=True)
def controlled_environment(monkeypatch):
    with nutrition_environment(monkeypatch):
        yield


def prepared(db, namespace="DAY", key="2026-11-12", values=None, request="day-1"):
    from app.services.nutrition_commands import owned_head
    from app.services.nutrition_consent import read_consent, set_consent

    consent = read_consent(db, 1)
    if not consent["granted"]:
        set_consent(db, 1, consent["consent_token"], True, 1, auth_proof=proof(db))
    _, token = owned_head(db, 1, namespace, key)
    body = {"contract_version": "nutrition-command/1.0.0", "request_id": request,
            "expected_head_token": token, "operation": "SET_FIELDS",
            "values": values if values is not None else {"kcal_milli": 1800000}}
    if namespace == "DAY":
        body.update(timezone="Europe/Paris", target_ref=None, confirm_complete=None)
    else:
        body.update(variant=key[0], effective_from=key[1])
    return body


def apply(db, body, namespace="DAY", key="2026-11-12"):
    from app.services.nutrition_commands import apply_command

    return apply_command(db, 1, namespace, key, body, auth_proof=proof(db))


def test_two_real_connections_cannot_both_commit_the_same_absent_head(db):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    from sqlalchemy.orm import Session

    from app.models.nutrition import NutritionDayRevision
    from app.services.nutrition_commands import NutritionError, apply_command

    body = prepared(db)
    auth = proof(db)
    engine = db.get_bind()
    db.rollback()
    barrier = Barrier(2)

    def attempt(request):
        with Session(engine) as other:
            barrier.wait(timeout=10)
            try:
                return apply_command(other, 1, "DAY", "2026-11-12", {**body, "request_id": request}, auth_proof=auth)["state"]
            except NutritionError as exc:
                return exc.code

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(attempt, ["concurrent-one", "concurrent-two"]))
    assert sorted(results) == ["APPLIED", "stale_head"]
    assert db.query(NutritionDayRevision).count() == 1


def test_cached_consent_and_auth_proof_are_rechecked_after_another_connection_changes_them(db):
    from sqlalchemy.orm import Session

    from app.models.nutrition import NutritionDayRevision
    from app.models.user import User
    from app.services.nutrition_commands import NutritionError, apply_command
    from app.services.nutrition_consent import read_consent, set_consent

    body = prepared(db)
    auth = proof(db)
    read_consent(db, 1)
    with Session(db.get_bind()) as other:
        grant = read_consent(other, 1)
        set_consent(other, 1, grant["consent_token"], False, 1, auth_proof=auth)
    with pytest.raises(NutritionError, match="consent_required"):
        apply_command(db, 1, "DAY", "2026-11-12", body, auth_proof=auth)
    with Session(db.get_bind()) as other:
        grant = read_consent(other, 1)
        set_consent(other, 1, grant["consent_token"], True, 1, auth_proof=auth)
        other.get(User, 1).session_epoch += 1
        other.commit()
    with pytest.raises(NutritionError, match="authentication_changed"):
        apply_command(db, 1, "DAY", "2026-11-12", body, auth_proof=auth)
    assert db.query(NutritionDayRevision).count() == 0


def test_originals_heads_completeness_and_null_zero_are_distinct(db):
    from app.models.nutrition import NutritionDayRevision
    from app.services.nutrition_commands import owned_head

    first = prepared(db, values={"kcal_milli": 1800000, "protein_milli": 0})
    first["confirm_complete"] = True
    receipt = apply(db, first)
    original = db.get(NutritionDayRevision, receipt["entity_ref"])
    second = prepared(db, values={"kcal_milli": 1750000, "protein_milli": None}, request="day-2")
    apply(db, second)
    head, _ = owned_head(db, 1, "DAY", "2026-11-12")
    assert (original.kcal_milli, original.protein_milli, original.declared_complete) == (1800000, 0, True)
    assert (head.kcal_milli, head.protein_milli, head.declared_complete) == (1750000, None, False)
    assert head.parent_ref == original.id and head.revision == 2


def test_exact_replay_precedes_current_consent_and_changed_body_conflicts(db):
    from app.services.nutrition_commands import NutritionError
    from app.services.nutrition_consent import read_consent, set_consent

    body = prepared(db)
    receipt = apply(db, body)
    grant = read_consent(db, 1)
    set_consent(db, 1, grant["consent_token"], False, 1, auth_proof=proof(db))
    assert apply(db, body) == receipt
    changed = copy.deepcopy(body)
    changed["values"]["kcal_milli"] = 1
    with pytest.raises(NutritionError, match="idempotency_mismatch"):
        apply(db, changed)


def test_unchanged_values_do_not_silently_reset_declared_completeness(db):
    from app.services.nutrition_commands import NutritionError, owned_head

    first = prepared(db)
    first["confirm_complete"] = True
    receipt = apply(db, first)
    unchanged = prepared(db, request="unchanged")
    with pytest.raises(NutritionError, match="no_change"):
        apply(db, unchanged)
    head, _ = owned_head(db, 1, "DAY", "2026-11-12")
    assert head.id == receipt["entity_ref"] and head.declared_complete is True


def test_stale_head_and_commit_failure_leave_no_half_revision(db, monkeypatch):
    from app.models.nutrition import NutritionDayRevision
    from app.services.nutrition_commands import NutritionError

    one, stale = prepared(db), prepared(db, request="other")
    apply(db, one)
    with pytest.raises(NutritionError, match="stale_head"):
        apply(db, stale)
    newer = prepared(db, request="will-rollback", values={"kcal_milli": 1500000})
    with monkeypatch.context() as patch:
        patch.setattr(db, "commit", lambda: (_ for _ in ()).throw(RuntimeError("synthetic commit failure")))
        with pytest.raises(RuntimeError, match="synthetic commit failure"):
            apply(db, newer)
    assert len(list(db.scalars(select(NutritionDayRevision)))) == 1


def test_disable_target_refuses_new_binding_but_preserves_historical_reference(db):
    from app.models.nutrition import NutritionDayRevision
    from app.services.nutrition_commands import NutritionError, owned_head

    key = ("STANDARD", "2026-11-01")
    target = prepared(db, "TARGET", key, {"kcal_milli": 2000000}, "target-1")
    preset = apply(db, target, "TARGET", key)
    apply(db, prepared(db))
    binding = prepared(db, request="bind")
    binding.update(operation="SET_TARGET_REF", values={}, timezone=None, target_ref=preset["entity_ref"])
    apply(db, binding)
    disable = prepared(db, "TARGET", key, {}, "disable")
    disable["operation"] = "DISABLE"
    apply(db, disable, "TARGET", key)
    history = db.scalar(select(NutritionDayRevision).where(NutritionDayRevision.target_ref == preset["entity_ref"]))
    assert history is not None
    other_day = "2026-11-11"
    apply(db, prepared(db, key=other_day, request="other-day"), key=other_day)
    bind_again = prepared(db, key=other_day, request="stale-bind")
    bind_again.update(operation="SET_TARGET_REF", values={}, timezone=None, target_ref=preset["entity_ref"])
    with pytest.raises(NutritionError, match="stale_target"):
        apply(db, bind_again, key=other_day)
    head, _ = owned_head(db, 1, "DAY", "2026-11-12")
    assert head.target_ref == preset["entity_ref"]


def test_withdrawal_is_not_zero_and_explicit_reopen_does_not_resurrect_values(db):
    from app.services.nutrition_commands import owned_head

    apply(db, prepared(db, values={"kcal_milli": 1500000, "fat_milli": 50000}))
    withdraw = prepared(db, request="withdraw")
    withdraw.update(operation="WITHDRAW", values={}, timezone=None)
    apply(db, withdraw)
    head, _ = owned_head(db, 1, "DAY", "2026-11-12")
    assert head.state == "WITHDRAWN" and head.kcal_milli is None
    apply(db, prepared(db, request="reopen", values={"protein_milli": 0}))
    head, _ = owned_head(db, 1, "DAY", "2026-11-12")
    assert head.state == "ACTIVE" and head.protein_milli == 0
    assert head.kcal_milli is None and head.fat_milli is None
