"""Actual owned transactions; no production science fixture."""

import importlib

import pytest

from tests import plan_v3_test_support as support
from tests.test_plan_v3_persistence import install

science_bundle = support.science_bundle
plan_bundle = support.plan_bundle


def api():
    return importlib.import_module("app.services.plan_v3.snapshots")


def test_guard_does_not_change_identity_and_rechecks_stale_epoch(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.plan_v3.transactions import RuntimeFailure, guard_owner

    install()
    with SessionLocal() as db:
        u = db.query(User).one()
        original = (u.id, u.username, u.password_hash, u.session_epoch)
        guard_owner(db, u.id, expected_epoch=u.session_epoch)
        db.commit()
        db.refresh(u)
        assert (u.id, u.username, u.password_hash, u.session_epoch) == original
        with pytest.raises(RuntimeFailure, match="authentication_changed"):
            guard_owner(db, u.id, expected_epoch=u.session_epoch + 1)
        db.rollback()


def test_events_replay_before_cas_and_snapshot_is_immutable(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.plan_v3.transactions import RuntimeFailure

    install()
    s = api()
    with SessionLocal() as db:
        owner = db.query(User).one().id
        event = s.declare(
            db,
            owner,
            request_id="declare",
            expected_revision=0,
            fields={
                "objective": {"state": "KNOWN", "value": "HYPERTROPHY"},
                "population_scope": {"state": "KNOWN", "value": "ADULT_NON_CLINICAL"},
                "sessions_per_week": {"state": "KNOWN", "value": 2},
                "session_budgets_minutes": {"state": "KNOWN", "value": [60, 60]},
                "limitations": {"state": "KNOWN", "value": []},
            },
        )
        db.commit()
        assert event.source_revision == 1
        snap = s.build_owned_snapshot(db, owner, request_id="capture", expected_revision=1)
        db.commit()
        original = snap.snapshot_json
        assert (
            s.declare(
                db,
                owner,
                request_id="declare",
                expected_revision=0,
                fields={
                    "objective": {"state": "KNOWN", "value": "HYPERTROPHY"},
                    "population_scope": {"state": "KNOWN", "value": "ADULT_NON_CLINICAL"},
                    "sessions_per_week": {"state": "KNOWN", "value": 2},
                    "session_budgets_minutes": {"state": "KNOWN", "value": [60, 60]},
                    "limitations": {"state": "KNOWN", "value": []},
                },
            ).id
            == event.id
        )
        with pytest.raises(RuntimeFailure, match="idempotency_mismatch"):
            s.declare(db, owner, request_id="declare", expected_revision=0, fields={})
        db.rollback()
        s.declare(
            db,
            owner,
            request_id="change",
            expected_revision=1,
            fields={"sessions_per_week": {"state": "UNKNOWN", "value": None}},
        )
        db.commit()
        db.refresh(snap)
        assert snap.snapshot_json == original
        with pytest.raises(RuntimeFailure, match="source_revision_changed"):
            s.build_owned_snapshot(db, owner, request_id="stale", expected_revision=1)
        db.rollback()


def test_flush_preferences_rollback_and_legacy_invalidation_while_disabled(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.training_preferences import (
        apply_training_preferences_in_transaction,
        get_training_preferences,
        save_training_preferences,
    )

    install()
    s = api()
    with SessionLocal() as db:
        owner = db.query(User).one().id
        s.declare(db, owner, request_id="decl", expected_revision=0, fields={})
        db.commit()
        apply_training_preferences_in_transaction(db, owner, sessions_per_week=3)
        db.rollback()
        assert get_training_preferences(db, owner).sessions_per_week is None
        save_training_preferences(db, owner, sessions_per_week=2)
        assert s.current_revision(db, owner) == 2
        assert s.events(db, owner)[-1].kind == "SOURCE_INVALIDATED"
        assert "sessions_per_week" in s.events(db, owner)[-1].payload_json
        assert "value" not in s.events(db, owner)[-1].payload_json


@pytest.mark.parametrize(
    "field,value",
    [
        ("sessions_per_week", True),
        ("session_budgets_minutes", [True, 60]),
        ("weight_kg", 70),
        ("owner_id", 2),
        ("objective", "invented"),
    ],
)
def test_invalid_declarations_do_not_leave_events(client, field, value):
    from app.database import SessionLocal
    from app.models.user import User

    install()
    s = api()
    with SessionLocal() as db:
        owner = db.query(User).one().id
        with pytest.raises(ValueError):
            s.declare(
                db,
                owner,
                request_id="invalid",
                expected_revision=0,
                fields={field: {"state": "KNOWN", "value": value}},
            )
        db.rollback()
        assert s.current_revision(db, owner) == 0


def test_empty_snapshot_preserves_unknown_and_legacy_preference_is_not_redated(client):
    import json

    from app.database import SessionLocal
    from app.models.user import User
    from app.services.training_preferences import save_training_preferences

    install()
    s = api()
    with SessionLocal() as db:
        owner = db.query(User).one().id
        save_training_preferences(db, owner, sessions_per_week=2)
        assert s.current_revision(db, owner) == 0
        snap = s.build_owned_snapshot(db, owner, request_id="empty", expected_revision=0)
        data = json.loads(snap.snapshot_json)
        assert data["blueprint"]["sessions_per_week"]["state"] == "UNKNOWN"
        assert data["blueprint"]["weight_kg"]["value"] is None
        assert data["consent_assessment"]["state"] == "UNAVAILABLE"
        assert data["subject_ref"] != "testuser"
        db.rollback()


def test_observations_are_owner_contextual_and_server_dated(client):
    import json

    from app.database import SessionLocal
    from app.models.user import User
    from app.services.plan_v3.transactions import RuntimeFailure

    install()
    s = api()
    context = {
        "canonical_exercise_id": "leg-extensions-assises",
        "context_ref": "synthetic:gym",
        "equipment_ref": "synthetic:device",
        "realization_ref": "synthetic:realization",
        "load_semantics": "MACHINE_DISPLAY_KG",
        "side": "BILATERAL",
    }
    with SessionLocal() as db:
        a = db.query(User).one()
        b = User(username="second-observer", password_hash=a.password_hash)
        db.add(b)
        db.flush()
        owner = a.id
        other = b.id
        db.commit()
        opened = s.append_owned_observation(
            db,
            owner,
            request_id="open",
            expected_revision=0,
            event={"kind": "CONTEXT_OPENED", "context": context, "availability": "AVAILABLE"},
        )
        episode = json.loads(opened.payload_json)["episode_ref"]
        db.commit()
        assert s.current_revision(db, owner) == 1
        with pytest.raises(RuntimeFailure, match="not_found"):
            s.append_owned_observation(
                db,
                other,
                request_id="foreign",
                expected_revision=0,
                event={
                    "kind": "CALIBRATION_EVENT",
                    "episode_ref": episode,
                    "event": {"kind": "FAMILIARIZATION_STARTED"},
                },
            )
        db.rollback()
        fact = s.append_owned_observation(
            db,
            owner,
            request_id="familiar",
            expected_revision=1,
            event={
                "kind": "CALIBRATION_EVENT",
                "episode_ref": episode,
                "event": {"kind": "FAMILIARIZATION_STARTED"},
            },
        )
        db.commit()
        payload = json.loads(fact.payload_json)["event"]
        assert payload["subject_ref"] == s.subject_ref(owner)
        assert payload["provenance"]["source_ref"] == fact.id
        assert payload["provenance"]["recorded_at"] is not None
        snap = s.build_owned_snapshot(db, owner, request_id="with-observation", expected_revision=2)
        data = json.loads(snap.snapshot_json)
        assert len(data["episodes"]) == 1
        assert len(data["episodes"][0]["events"]) == 1
        assert data["blueprint"]["environment"]["equipment_items"]["state"] == "UNKNOWN"
        assert data["episodes"][0]["events"][0]["kind"] == "FAMILIARIZATION_STARTED"
        db.rollback()


def test_two_connections_same_source_revision_accept_one_declaration(client):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    from app.database import SessionLocal
    from app.models.user import User
    from app.services.plan_v3.transactions import RuntimeFailure

    install()
    s = api()
    barrier = Barrier(2)
    with SessionLocal() as db:
        owner = db.query(User).one().id

    def write(key):
        with SessionLocal() as db:
            barrier.wait(timeout=5)
            try:
                row = s.declare(db, owner, request_id=key, expected_revision=0, fields={})
                db.commit()
                return ("accepted", row.source_revision)
            except RuntimeFailure as error:
                db.rollback()
                return ("refused", error.code)

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(write, ["race-a", "race-b"]))
    assert sorted(results) == [("accepted", 1), ("refused", "source_revision_changed")]


def test_cached_identity_cannot_authorize_after_revocation(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.plan_v3.transactions import RuntimeFailure, guard_owner

    with SessionLocal() as stale, SessionLocal() as revoker:
        user = stale.query(User).one()
        epoch = user.session_epoch
        current = revoker.get(User, user.id)
        current.session_epoch += 1
        revoker.commit()
        with pytest.raises(RuntimeFailure, match="authentication_changed"):
            guard_owner(stale, user.id, expected_epoch=epoch)
        stale.rollback()
