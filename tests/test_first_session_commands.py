"""One real canonical handoff, transactional materialization and lost response."""

import json

import pytest

from tests import plan_v3_test_support as support
from tests.test_plan_v3_persistence import install

science_bundle = support.science_bundle
plan_bundle = support.plan_bundle


def final_evaluation(db, owner, bundle, monkeypatch):
    from app.config import get_settings
    from app.services.plan_v3.evaluations import acknowledge_time, evaluate_owned_snapshot

    monkeypatch.setattr(get_settings(), "plan_v3_controlled_test_enabled", True)
    authority, pins = support.activate_test_authority(db, bundle)
    snapshot = support.acquire_qualified(db, owner, authority)
    ev = evaluate_owned_snapshot(
        db, owner, snapshot_ref=snapshot.id, request_id="eval-final", expected_pins=pins
    )
    db.commit()
    result = json.loads(ev.result_json)
    context = {
        key: result[key]
        for key in (
            "request_fingerprint",
            "observation_fingerprint",
            "plan_time_fingerprint",
            "start_policy_ref",
        )
    }
    final = acknowledge_time(
        db, owner, evaluation_ref=ev.id, request_id="ack-final", expected_context=context
    )
    db.commit()
    return final


def start_body(ev):
    result = json.loads(ev.result_json)
    return {
        "evaluation_ref": ev.id,
        "snapshot_ref": ev.snapshot_id,
        "source_revision": ev.source_revision,
        **{
            key: result[key]
            for key in (
                "request_fingerprint",
                "observation_fingerprint",
                "full_evaluation_fingerprint",
                "plan_time_fingerprint",
                "binding_ref",
                "binding_digest",
                "bundle_digest",
                "effective_science_digest",
                "engine_version",
                "policy_version",
            )
        },
        "registry_digest": "602ff0d32ebc625b4c9474660b5b36ee9983c4c598f16ae9b1269e67e5cea50f",
        "contract_version": "first-plan-recommendation/3.0.0",
        "selected_scientific_session_id": result["candidate_plan"]["sessions"][0]["session_id"],
    }


def test_real_creation_rollback_replay_permanent_handoff_and_exact_canonical_sets(
    client, monkeypatch, science_bundle
):
    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession
    from app.models.user import User
    from app.services.plan_v3 import commands as c
    from app.services.plan_v3.transactions import RuntimeFailure

    install()
    with SessionLocal() as db:
        owner = db.query(User).one().id
        final = final_evaluation(db, owner, science_bundle, monkeypatch)
        body = start_body(final)
        def unsupported_projection(*args, **kwargs):
            raise RuntimeFailure("execution_not_representable")
        with monkeypatch.context() as boundary:
            boundary.setattr(c, "materialize_first_plan_session", unsupported_projection)
            refused = c.start_owned_first_session(db, owner, request_id="unsupported", body=body)
            db.commit()
            assert refused.state == "DENIED" and refused.terminal_code == "execution_not_representable"
            assert db.query(WorkoutSession).count() == 0
        first = c.start_owned_first_session(db, owner, request_id="first", body=body)
        session_id = first.session_id
        assert first.state == "CREATED"
        assert db.query(WorkoutSession).count() == 1
        assert db.query(SessionExercise).count() == 7
        assert db.query(SetLog).count() == 14
        assert all(
            s.kind == "work" and not s.completed and s.reps is None and s.weight_kg is None
            for s in db.query(SetLog)
        )
        assert db.get(WorkoutSession, session_id).template_id is None
        db.rollback()
        assert db.query(WorkoutSession).count() == 0
        first = c.start_owned_first_session(db, owner, request_id="first", body=body)
        db.commit()
        session_id = first.session_id
        assert (
            c.start_owned_first_session(db, owner, request_id="first", body=body).session_id
            == session_id
        )
        with pytest.raises(RuntimeFailure, match="idempotency_mismatch"):
            c.start_owned_first_session(
                db, owner, request_id="first", body={**body, "source_revision": 999}
            )
        db.rollback()
        cancelled = c.cancel_owned_first_session(db, owner, request_id="first", body=body)
        assert cancelled.state == "CREATED" and cancelled.session_id == session_id
        # First handoff remains unique even after completion.
        db.get(WorkoutSession, session_id).status = "completed"
        db.commit()
        second = c.start_owned_first_session(db, owner, request_id="another-key", body=body)
        db.commit()
        assert second.state == "DENIED" and second.terminal_code == "first_session_already_created"
        assert db.query(WorkoutSession).count() == 1
        assert c.read_owned_first_session_handoff(db, owner).session_id == session_id


def test_cancel_before_delayed_start_needs_no_evaluation_and_preserves_tombstone(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.plan_v3 import commands as c
    from app.services.plan_v3.transactions import RuntimeFailure

    install()
    with SessionLocal() as db:
        owner = db.query(User).one().id
        body = {"evaluation_ref": "not-arrived-yet"}
        cancelled = c.cancel_owned_first_session(db, owner, request_id="late", body=body)
        db.commit()
        assert cancelled.state == "CANCELLED"
        assert (
            c.start_owned_first_session(db, owner, request_id="late", body=body).state
            == "CANCELLED"
        )
        with pytest.raises(RuntimeFailure, match="idempotency_mismatch"):
            c.start_owned_first_session(db, owner, request_id="late", body={})
        db.rollback()
