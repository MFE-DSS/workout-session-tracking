"""Real owned inputs -> private producer -> canonical validator -> exact ack."""

import json

import pytest

from tests import plan_v3_test_support as support
from tests.plan_v3_test_support import acquire_qualified, activate_test_authority
from tests.test_plan_v3_persistence import install

science_bundle = support.science_bundle
plan_bundle = support.plan_bundle


def test_actual_producer_time_ack_and_replay_after_source_change(
    client, monkeypatch, science_bundle
):
    from app.config import get_settings
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.plan_v3 import evaluations as api
    from app.services.plan_v3 import snapshots as s
    from app.services.plan_v3.transactions import RuntimeFailure

    monkeypatch.setattr(get_settings(), "plan_v3_controlled_test_enabled", True)
    install()
    with SessionLocal() as db:
        owner = db.query(User).one().id
        authority, pins = activate_test_authority(db, science_bundle)
        snap = acquire_qualified(db, owner, authority)
        ev = api.evaluate_owned_snapshot(
            db, owner, snapshot_ref=snap.id, request_id="evaluate", expected_pins=pins
        )
        db.commit()
        result = json.loads(ev.result_json)
        assert result["scientific_readiness"] == "SCIENTIFICALLY_READY"
        assert result["start_permission"] == "REQUIRES_TIME_ACK"
        assert result["time_assessments"][0]["state"] == "BUDGET_UNCERTAIN"
        context = {
            key: result[key]
            for key in (
                "request_fingerprint",
                "observation_fingerprint",
                "plan_time_fingerprint",
                "start_policy_ref",
            )
        }
        acknowledged = api.acknowledge_time(
            db, owner, evaluation_ref=ev.id, request_id="ack", expected_context=context
        )
        db.commit()
        final = json.loads(acknowledged.result_json)
        assert final["start_permission"] == "ELIGIBLE"
        assert acknowledged.parent_evaluation_id == ev.id
        assert final["request_fingerprint"] == result["request_fingerprint"]
        assert final["observation_fingerprint"] == result["observation_fingerprint"]
        assert final["full_evaluation_fingerprint"] != result["full_evaluation_fingerprint"]
        s.declare(
            db, owner, request_id="changed", expected_revision=snap.source_revision, fields={}
        )
        db.commit()
        assert (
            api.acknowledge_time(
                db, owner, evaluation_ref=ev.id, request_id="ack", expected_context=context
            ).id
            == acknowledged.id
        )
        with pytest.raises(RuntimeFailure, match="source_revision_changed"):
            api.acknowledge_time(
                db, owner, evaluation_ref=ev.id, request_id="new-ack", expected_context=context
            )
        db.rollback()


def test_absent_authority_and_pins_mismatch_do_not_create_fake_evaluation(
    client, monkeypatch, science_bundle
):
    from app.config import get_settings
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.plan_v3 import evaluations as api
    from app.services.plan_v3 import snapshots as s
    from app.services.plan_v3.transactions import RuntimeFailure

    monkeypatch.setattr(get_settings(), "plan_v3_controlled_test_enabled", True)
    install()
    with SessionLocal() as db:
        owner = db.query(User).one().id
        snap = s.build_owned_snapshot(db, owner, request_id="empty", expected_revision=0)
        db.commit()
        with pytest.raises(RuntimeFailure, match="authority_not_served"):
            api.evaluate_owned_snapshot(
                db, owner, snapshot_ref=snap.id, request_id="missing", expected_pins={}
            )
        db.rollback()
        authority, pins = activate_test_authority(db, science_bundle)
        with pytest.raises(RuntimeFailure, match="authority_version_mismatch"):
            api.evaluate_owned_snapshot(
                db,
                owner,
                snapshot_ref=snap.id,
                request_id="invalid",
                expected_pins={**pins, "bundle_digest": "0" * 64},
            )
        db.rollback()
        ev = api.evaluate_owned_snapshot(
            db, owner, snapshot_ref=snap.id, request_id="unknown", expected_pins=pins
        )
        db.commit()
        assert json.loads(ev.result_json)["scientific_readiness"] == "INSUFFICIENT_DATA"
        assert json.loads(ev.result_json)["start_permission"] == "DENIED"
