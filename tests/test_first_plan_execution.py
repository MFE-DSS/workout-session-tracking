"""Typed set facts stay distinct from prescription and legacy total mass."""

import json
from datetime import UTC, datetime, timedelta, timezone

import pytest

from tests import plan_v3_test_support as support
from tests.test_first_session_commands import final_evaluation, start_body
from tests.test_plan_v3_persistence import install

science_bundle = support.science_bundle
plan_bundle = support.plan_bundle


def test_exact_execution_typed_log_correction_and_withdrawal(client, monkeypatch, science_bundle):
    from app.config import get_settings
    from app.database import SessionLocal
    from app.models.first_plan_runtime import FirstPlanRuntimeAuthority
    from app.models.session import SessionExercise, SetLog
    from app.models.user import User
    from app.services.plan_v3.commands import start_owned_first_session
    from app.services.plan_v3.execution import first_plan_execution_read_model
    from app.services.plan_v3.journal import record_first_plan_set
    from app.services.plan_v3.transactions import RuntimeFailure

    monkeypatch.setattr(get_settings(), "plan_v3_guidance_enabled", True)
    install()
    with SessionLocal() as db:
        owner = db.query(User).one().id
        ev = final_evaluation(db, owner, science_bundle, monkeypatch)
        command = start_owned_first_session(
            db, owner, request_id="typed-first", body=start_body(ev)
        )
        db.commit()
        execution = first_plan_execution_read_model(db, owner, command.session_id)
        assert len(execution["exercises"]) == 7
        assert execution["exercises"][0]["transition_after_exercise"] == {
            "kind": "SETUP_NEXT_EXERCISE",
            "duration_seconds": None,
        }
        # Recomputed checksum is content identity, not proof of SCI prescription.
        from sqlalchemy import update

        from app.models.first_plan_runtime import FirstPlanExecutionBinding
        from app.services.plan_v3.snapshots import canonical, digest

        binding = db.get(FirstPlanExecutionBinding, command.session_id)
        original_payload = binding.immutable_payload_json
        original_digest = binding.binding_digest
        changed = json.loads(original_payload)
        changed["scientific_session"]["slots"][0]["prescription"]["dose"]["work_sets"] = 99
        db.execute(
            update(FirstPlanExecutionBinding)
            .where(FirstPlanExecutionBinding.session_id == command.session_id)
            .values(immutable_payload_json=canonical(changed), binding_digest=digest(changed))
        )
        db.commit()
        db.expire_all()
        with pytest.raises(RuntimeFailure, match="execution_binding_unavailable"):
            first_plan_execution_read_model(db, owner, command.session_id)
        db.execute(
            update(FirstPlanExecutionBinding)
            .where(FirstPlanExecutionBinding.session_id == command.session_id)
            .values(immutable_payload_json=original_payload, binding_digest=original_digest)
        )
        db.commit()
        missing_key = json.loads(original_payload)
        del missing_key["authority"]["binding_digest"]
        db.execute(
            update(FirstPlanExecutionBinding)
            .where(FirstPlanExecutionBinding.session_id == command.session_id)
            .values(
                immutable_payload_json=canonical(missing_key), binding_digest=digest(missing_key)
            )
        )
        db.commit()
        db.expire_all()
        with pytest.raises(RuntimeFailure, match="execution_binding_unavailable"):
            first_plan_execution_read_model(db, owner, command.session_id)
        db.execute(
            update(FirstPlanExecutionBinding)
            .where(FirstPlanExecutionBinding.session_id == command.session_id)
            .values(immutable_payload_json=original_payload, binding_digest=original_digest)
        )
        db.commit()
        first = execution["exercises"][0]
        set_id = first["sets"][0]["set_id"]
        assert first["prescription"]["dose"]["rest_seconds"] == 90
        assert first["sets"][0]["observation"] is None
        assert execution["applicability"]["state"] == "CURRENT"
        fact = {
            "setting": {"kind": "MASS_KG", "value": 19.0, "unit": "kg"},
            "context": first["prescription"]["context"],
            "performed_at_estimated": True,
            "reps": 9,
            "completed": True,
            "performed_at": datetime.now(UTC).astimezone(timezone(timedelta(hours=2))).isoformat(),
        }
        receipt = record_first_plan_set(
            db,
            owner,
            command.session_id,
            set_id,
            op_id="actual",
            expected_set_revision=0,
            observation=fact,
        )
        db.commit()
        assert receipt["applied_revision"] == 1
        assert db.get(SetLog, set_id).weight_kg is None
        assert db.get(SetLog, set_id).reps == 9
        original_time = db.get(SetLog, set_id).completed_at
        assert original_time.replace(tzinfo=UTC) <= datetime.now(UTC)
        correction = {**fact, "reps": 8}
        record_first_plan_set(
            db,
            owner,
            command.session_id,
            set_id,
            op_id="correct",
            expected_set_revision=1,
            observation=correction,
        )
        db.commit()
        assert (
            record_first_plan_set(
                db,
                owner,
                command.session_id,
                set_id,
                op_id="actual",
                expected_set_revision=0,
                observation=fact,
            )
            == receipt
        )
        assert db.get(SetLog, set_id).reps == 8
        assert db.get(SetLog, set_id).completed_at == original_time
        assert all(
            se.success_score is None and se.implicit_label is None
            for se in db.query(SessionExercise)
        )
        with pytest.raises(RuntimeFailure, match="set_revision_changed"):
            record_first_plan_set(
                db,
                owner,
                command.session_id,
                set_id,
                op_id="stale",
                expected_set_revision=0,
                observation=fact,
            )
        db.rollback()
        operational = db.get(FirstPlanRuntimeAuthority, "first-session-runtime/3.0.0")
        operational.state = "WITHDRAWN"
        operational.generation += 1
        db.commit()
        after = first_plan_execution_read_model(db, owner, command.session_id)
        assert after["applicability"]["state"] == "BLOCKED"
        assert after["observation_only"] is True
        assert after["exercises"][0]["sets"][0]["observation"]["setting"]["value"] == 19.0
        assert after["exercises"][0]["sets"][0]["reps"] == 8
        assert after["exercises"][0]["sets"][0]["observation"]["performed_at_estimated"] is True
        assert "NEXT_WORK_SET" not in after["allowed_actions"]
        assert "RECORD_FACT" in after["allowed_actions"]
        # Facts performed while offline remain factual, no new guidance permission.
        record_first_plan_set(
            db,
            owner,
            command.session_id,
            first["sets"][1]["set_id"],
            op_id="late-fact",
            expected_set_revision=0,
            observation=fact,
        )
        db.commit()
