"""Isolated proposed workflow: synthetic policy/proofs, no routes or destructive worker."""

from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import Session

from app.database import Base
from app.models.user import User
from app.services.account_deletion_requests import (
    DeletionRequestService,
    Policy,
    PolicyRequired,
    RequestRejected,
    StatusDenied,
    requests,
    workflow_metadata,
)
from app.services.account_lifecycle import AccountRejected
from app.services.auth import hash_password

NOW = datetime(2026, 11, 5, 12, tzinfo=UTC)
POLICY = Policy(
    "SYNTHETIC_TEST_ONLY",
    "scope-fixture",
    "retention-fixture",
    "controller-fixture",
    timedelta(minutes=5),
    "MANUAL",
    True,
)


@pytest.fixture
def database(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path / 'workflow.db'}",
        connect_args={"check_same_thread": False, "timeout": 10},
    )
    Base.metadata.create_all(engine)
    workflow_metadata.create_all(engine)  # Explicit fixture initialization, never app startup.
    with Session(engine) as db:
        password = hash_password("testpass")
        db.add_all(
            [
                User(id=7, username="owner7", password_hash=password),
                User(id=8, username="owner8", password_hash=password),
            ]
        )
        db.commit()
    yield engine
    engine.dispose()


def service(**kwargs):
    return DeletionRequestService({POLICY.ref: POLICY}, **kwargs)


def submit(engine, key="request-key-0001", owner=7, svc=None):
    with Session(engine) as db:
        result = (svc or service()).request(
            db,
            db.get(User, owner),
            request_id=key,
            current_password="testpass",
            policy_ref=POLICY.ref,
            now=NOW,
        )
        db.commit()
        return result


def test_no_policy_means_no_request_no_revocation(database):
    with Session(database) as db:
        with pytest.raises(PolicyRequired):
            DeletionRequestService().request(
                db,
                db.get(User, 7),
                request_id="request-key-0001",
                current_password="testpass",
                policy_ref=POLICY.ref,
                now=NOW,
            )
        assert db.execute(select(requests)).all() == []
        assert db.get(User, 7).session_epoch == 0


@pytest.mark.parametrize("key", ["", "short", "x" * 129, "request/key/invalid", "secret\nrequest"])
def test_invalid_request_identity_is_not_recorded(database, key):
    with pytest.raises(RequestRejected):
        submit(database, key)
    with Session(database) as db:
        assert db.execute(select(requests)).all() == []


def test_restart_and_lost_response_keep_same_durable_operation(database):
    first = submit(database)
    database.dispose()  # Real connection closed/reopened, not an in-memory repository.
    repeated = submit(database)
    active = submit(database, "other-request-key")
    assert first == repeated == active
    assert first["state"] == "PENDING"
    with Session(database) as db:
        assert len(db.execute(select(requests)).all()) == 1
        assert db.get(User, 7).session_epoch == 0
        assert "testpass" not in str(db.execute(select(requests)).all())
        assert service().read(db, db.get(User, 7), first["request_id"]) == first
        with pytest.raises(StatusDenied):
            service().read(db, db.get(User, 8), first["request_id"])


def test_two_connections_cannot_accept_two_active_requests(database):
    with ThreadPoolExecutor(max_workers=2) as executor:
        a, b = list(
            executor.map(
                lambda key: submit(database, key), ["concurrent-key-a", "concurrent-key-b"]
            )
        )
    assert a == b
    with Session(database) as db:
        assert len(db.execute(select(requests)).all()) == 1


def test_bad_password_stale_epoch_and_inactive_identity_are_refused(database):
    with Session(database) as db:
        user = db.get(User, 7)
        with pytest.raises(AccountRejected):
            service().request(
                db,
                user,
                request_id="request-key-0001",
                current_password="wrong",
                policy_ref=POLICY.ref,
                now=NOW,
            )
    with Session(database) as old, Session(database) as other:
        stale = old.get(User, 7)
        other.execute(update(User).where(User.id == 7).values(session_epoch=1))
        other.commit()
        with pytest.raises(AccountRejected):
            service().request(
                old,
                stale,
                request_id="request-key-0001",
                current_password="testpass",
                policy_ref=POLICY.ref,
                now=NOW,
            )
        with pytest.raises(StatusDenied):
            service().read(old, stale, "request-key-0001")
    with Session(database) as db:
        db.execute(update(User).where(User.id == 7).values(is_active=False))
        db.commit()
    with pytest.raises(AccountRejected):
        submit(database)


def test_interrupted_before_commit_leaves_no_accepted_request(database):
    with Session(database) as db:
        service().request(
            db,
            db.get(User, 7),
            request_id="request-key-0001",
            current_password="testpass",
            policy_ref=POLICY.ref,
            now=NOW,
        )
        db.rollback()
    with Session(database) as db:
        assert db.execute(select(requests)).all() == []
    assert submit(database)["state"] == "PENDING"


def test_scoped_capability_rotates_expires_and_survives_account_revocation_only_for_status(
    database,
):
    receipt = submit(database)
    svc = service()
    with Session(database) as db:
        user = db.get(User, 7)
        token = svc.issue_status_capability(
            db, user, receipt["request_id"], current_password="testpass", now=NOW
        )
        db.commit()
        assert token not in str(db.execute(select(requests)).all())
        assert token not in str(receipt)
        assert svc.read_status_capability(db, 7, receipt["request_id"], token, now=NOW) == receipt
        with pytest.raises(StatusDenied):
            svc.read_status_capability(db, 8, receipt["request_id"], token, now=NOW)
        with pytest.raises(StatusDenied):
            svc.read_status_capability(
                db, 7, receipt["request_id"], token, now=NOW + timedelta(minutes=6)
            )
        rotated = svc.issue_status_capability(
            db, user, receipt["request_id"], current_password="testpass", now=NOW
        )
        db.commit()
        with pytest.raises(StatusDenied):
            svc.read_status_capability(db, 7, receipt["request_id"], token, now=NOW)
        # Fixture simulates future irreversible authority; service never performs this transition.
        db.execute(update(User).where(User.id == 7).values(session_epoch=1, is_active=False))
        db.commit()
        assert svc.read_status_capability(db, 7, receipt["request_id"], rotated, now=NOW) == receipt
        with pytest.raises(StatusDenied):
            svc.read(db, user, receipt["request_id"])


def test_manual_confirmation_has_no_authority_by_default_and_never_inferrs_deletion(database):
    receipt = submit(database)
    with Session(database) as db:
        with pytest.raises(RequestRejected):
            service().confirm(db, 7, receipt["request_id"], proof={"state": "DELETED"}, now=NOW)
        assert service().read(db, db.get(User, 7), receipt["request_id"])["state"] == "PENDING"
        assert db.get(User, 7).is_active


def test_rejected_request_is_terminal_and_new_explicit_key_can_be_accepted(database):
    first = submit(database)
    with Session(database) as db:
        service().reject(db, 7, first["request_id"], reason="OPERATOR_REJECTED", now=NOW)
        db.commit()
    assert submit(database)["state"] == "REJECTED"
    second = submit(database, "request-key-0002")
    assert second["state"] == "PENDING"
    assert second["request_id"] != first["request_id"]


def test_confirmation_needs_bound_server_evidence_and_started_state(database):
    receipt = submit(database)
    proof = {
        "owner_id": 7,
        "request_id": receipt["request_id"],
        "policy_ref": POLICY.ref,
        "scope_ref": POLICY.scope_ref,
        "revocation": "CONFIRMED",
        "data_erasure": "CONFIRMED",
        "restore_protection": "CONFIRMED",
        "proof_ref": "SYNTHETIC_TEST_ONLY",
    }
    svc = service(
        verifier=lambda data: data == proof
    )  # Trusted test authority, never production registry.
    with Session(database) as db:
        with pytest.raises(RequestRejected):
            svc.confirm(db, 7, receipt["request_id"], proof=proof, now=NOW)
        db.execute(
            update(requests).values(state="IN_PROGRESS")
        )  # No production start worker exists.
        for field in [
            "owner_id",
            "request_id",
            "policy_ref",
            "scope_ref",
            "revocation",
            "data_erasure",
            "restore_protection",
        ]:
            with pytest.raises(RequestRejected):
                svc.confirm(db, 7, receipt["request_id"], proof={**proof, field: "wrong"}, now=NOW)
        confirmed = svc.confirm(db, 7, receipt["request_id"], proof=proof, now=NOW)
        db.commit()
        assert confirmed["state"] == "DELETED"
        assert svc.confirm(db, 7, receipt["request_id"], proof=proof, now=NOW) == confirmed
        assert (
            db.get(User, 7) is not None
        )  # No real purge or revocation performed by the protocol test.


def test_workflow_schema_is_not_registered_or_created_by_canonical_startup():
    assert requests.name not in Base.metadata.tables


def test_same_request_key_across_accounts_keeps_owner_and_capability_isolated(database):
    a = submit(database)
    b = submit(database, owner=8)
    assert a["owner_id"] == 7
    assert b["owner_id"] == 8
    with Session(database) as db:
        token = service().issue_status_capability(
            db, db.get(User, 7), a["request_id"], current_password="testpass", now=NOW
        )
        db.commit()
        with pytest.raises(StatusDenied):
            service().read_status_capability(db, 8, b["request_id"], token, now=NOW)
        assert len(db.execute(select(requests)).all()) == 2


def test_irreversible_status_cannot_be_recovered_by_active_identity_reuse(database):
    receipt = submit(database)
    svc = service()
    with Session(database) as db:
        user = db.get(User, 7)
        token = svc.issue_status_capability(
            db, user, receipt["request_id"], current_password="testpass", now=NOW
        )
        db.execute(update(requests).values(state="IN_PROGRESS"))  # Future executor fixture only.
        db.commit()
        # Even a fresh/current active User with the same integer id is not authority
        # to recover a started/removed request. Follow-up capability is required.
        with pytest.raises(StatusDenied):
            svc.read(db, user, receipt["request_id"])
        with pytest.raises(RequestRejected):
            svc.request(
                db,
                user,
                request_id=receipt["request_id"],
                current_password="testpass",
                policy_ref=POLICY.ref,
                now=NOW,
            )
        with pytest.raises(StatusDenied):
            svc.issue_status_capability(
                db, user, receipt["request_id"], current_password="testpass", now=NOW
            )
        assert (
            svc.read_status_capability(db, 7, receipt["request_id"], token, now=NOW)["state"]
            == "PENDING"
        )


def test_refused_stale_principal_is_not_promoted_for_repeated_status_or_capability(database):
    receipt = submit(database)
    with Session(database) as old, Session(database) as other:
        stale = old.get(User, 7)
        expected_epoch = stale.session_epoch
        expected_hash = stale.password_hash
        other.execute(update(User).where(User.id == 7).values(session_epoch=1))
        other.commit()
        svc = service()
        for _ in range(2):
            with pytest.raises(AccountRejected):
                svc.issue_status_capability(old, stale, receipt['request_id'], current_password='testpass', now=NOW)
            assert stale.session_epoch == expected_epoch
            assert stale.password_hash == expected_hash
            with pytest.raises(StatusDenied):
                svc.read(old, stale, receipt['request_id'])
        assert old.execute(select(requests.c.capability_hash)).scalar_one() is None
