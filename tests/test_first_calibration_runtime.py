"""First interaction needs no seven-setting history; observations are real acts."""

from datetime import UTC, datetime

import pytest

from tests import plan_v3_test_support as support
from tests.test_plan_v3_persistence import install

science_bundle = support.science_bundle
plan_bundle = support.plan_bundle


def test_pilot_actual_progress_qualification_and_old_observation_projection(
    client, monkeypatch, science_bundle
):
    from app.config import get_settings
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.plan_v3 import calibration as c
    from app.services.plan_v3 import snapshots as s
    from app.services.plan_v3.transactions import RuntimeFailure

    monkeypatch.setattr(get_settings(), "plan_v3_controlled_test_enabled", True)
    monkeypatch.setattr(get_settings(), "plan_v3_guidance_enabled", True)
    install()
    with SessionLocal() as db:
        owner = db.query(User).one().id
        authority, pins = support.activate_test_authority(db, science_bundle)
        spec = authority["v3"]["policy"]["selection"][0]
        ctx = {
            "canonical_exercise_id": spec["candidate_id"],
            "realization_ref": spec["realization_ref"],
            "context_ref": "synthetic:gym",
            "equipment_ref": "synthetic:leg-device",
            "side": "BILATERAL",
            "load_semantics": "MACHINE_DISPLAY_KG",
        }
        s.declare(
            db,
            owner,
            request_id="minimal-pilot",
            expected_revision=0,
            fields={
                "population_scope": {"state": "KNOWN", "value": "ADULT_NON_CLINICAL"},
                "limitations": {"state": "KNOWN", "value": []},
            },
        )
        db.commit()
        opened = c.open_encounter(
            db,
            owner,
            request_id="open-pilot",
            expected_revision=1,
            context=ctx,
            availability="AVAILABLE",
            concern_state="CLEAR",
        )
        db.commit()
        ref = opened.id
        first = c.read_encounter(db, owner, ref)
        assert first["result"]["state"] == "CALIBRATION_REQUIRED"
        assert first["progress"]["observed_attempt_count"] == 0
        assert "INITIATE_TRIAL" not in first["allowed_actions"]

        def act(key, observation):
            view = c.read_encounter(db, owner, ref)
            result = c.record_encounter_observation(
                db,
                owner,
                request_id=key,
                expected_revision=view["source_revision"],
                encounter_ref=ref,
                expected_authority=view["authority"],
                observation=observation,
            )
            db.commit()
            return result

        act(
            "preparation",
            {
                "kind": "PREPARATION_REPORTED",
                "instruction_ref": "synthetic:manufacturer",
                "setup_ref": "synthetic:personal-setup",
                "understood": True,
                "controlled": True,
            },
        )
        load = {"kind": "MASS_KG", "value": 17.0, "unit": "kg"}
        act("choice", {"kind": "SETTING_CHOICE_REPORTED", "setting": load, "available": True})
        act(
            "context",
            {
                "kind": "CALIBRATION_EVENT_REPORTED",
                "event": {"kind": "CONTEXT_CONFIRMED", "setting": load},
            },
        )
        act(
            "familiar",
            {"kind": "CALIBRATION_EVENT_REPORTED", "event": {"kind": "FAMILIARIZATION_CONFIRMED"}},
        )
        before = c.read_encounter(db, owner, ref)
        assert "INITIATE_TRIAL" in before["allowed_actions"]
        act(
            "initiate-intention",
            {"kind": "CALIBRATION_ACTION_REQUESTED", "action": "INITIATE_TRIAL"},
        )
        assert c.read_encounter(db, owner, ref)["progress"]["observed_attempt_count"] == 0
        trial = act(
            "actual-trial",
            {
                "kind": "CALIBRATION_EVENT_REPORTED",
                "stop_reason": "COMPLETED",
                "event": {
                    "kind": "ATTEMPT_OBSERVED",
                    "setting": load,
                    "reps": 10,
                    "completed": True,
                    "successful": True,
                    "technique": "ACCEPTABLE",
                    "discomfort": "NO_CONCERN",
                    "occurred_at": datetime.now(UTC).isoformat(),
                },
            },
        )
        act(
            "accept",
            {
                "kind": "CALIBRATION_EVENT_REPORTED",
                "event": {"kind": "SETTING_ACCEPTED", "reference_event_id": trial.id},
            },
        )
        qualified = c.read_encounter(db, owner, ref)
        assert qualified["result"]["state"] == "QUALIFIED"
        assert (
            qualified["result"]["portable_episode"]["events"][-1]["reference_event_id"] == trial.id
        )
        assert qualified["progress"]["observed_attempt_count"] == 1
        assert qualified["progress"]["context"] == ctx
        assert qualified["progress"]["observations"][0]["event_id"] == trial.id
        assert qualified["progress"]["observations"][0]["setting"] == load
        # Clearing the current setting must not rewrite the old observation.
        act(
            "clear-choice", {"kind": "SETTING_CHOICE_REPORTED", "setting": None, "available": False}
        )
        old = c.read_encounter(db, owner, ref)
        assert old["result"]["state"] == "SUPPORTED_INITIAL_EXPLORATION"
        assert old["progress"]["observed_attempt_count"] == 1
        assert old["progress"]["observation_refs"] == [trial.id]
        captured = s.build_owned_snapshot(
            db,
            owner,
            request_id="choice-cleared-snapshot",
            expected_revision=s.current_revision(db, owner),
        )
        import json

        assert json.loads(captured.snapshot_json)["review_source_refs"]
        db.commit()
        # A concern remains in the owner's ledger, including across new IDs.
        act(
            "concern", {"kind": "CALIBRATION_EVENT_REPORTED", "event": {"kind": "CONCERN_REPORTED"}}
        )
        new = c.open_encounter(
            db,
            owner,
            request_id="new-id",
            expected_revision=s.current_revision(db, owner),
            context={**ctx, "equipment_ref": "synthetic:new-device"},
            availability="AVAILABLE",
            concern_state="CLEAR",
        )
        db.commit()
        blocked = c.read_encounter(db, owner, new.id)
        assert blocked["result"]["state"] == "CONCERN_REVIEW"
        assert "INITIATE_TRIAL" not in blocked["allowed_actions"]
        with pytest.raises(RuntimeFailure, match="calibration_action_not_permitted"):
            act(
                "retry-concern",
                {"kind": "CALIBRATION_ACTION_REQUESTED", "action": "INITIATE_TRIAL"},
            )
        db.rollback()

        from app.models.first_plan_runtime import FirstPlanRuntimeAuthority

        operational = db.get(FirstPlanRuntimeAuthority, "first-session-runtime/3.0.0")
        operational.state = "WITHDRAWN"
        operational.generation += 1
        db.commit()
        history = c.read_encounter(db, owner, ref)
        assert history["result"] is None
        assert history["runtime_availability"] == "NOT_SERVED"
        assert history["progress"]["observed_attempt_count"] == 1
        assert history["allowed_actions"] == []
        assert history["progress"]["observations"][0]["event_id"] == trial.id
        assert history["progress"]["context"] == ctx

        late = c.record_encounter_observation(
            db,
            owner,
            request_id="late-fact",
            expected_revision=s.current_revision(db, owner),
            encounter_ref=ref,
            expected_authority=None,
            observation={
                "kind": "CALIBRATION_EVENT_REPORTED",
                "event": {"kind": "CONCERN_REPORTED"},
            },
        )
        db.commit()
        assert late.kind == "CALIBRATION_EVENT_REPORTED"
        assert c.read_encounter(db, owner, ref)["allowed_actions"] == []
