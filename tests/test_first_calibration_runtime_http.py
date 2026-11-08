"""Calibration is a separate negotiated interaction, not a first-session command."""

from tests import plan_v3_test_support as support
from tests.test_blueprint_runtime_http import ROOT, enable, token
from tests.test_plan_v3_persistence import install

science_bundle = support.science_bundle
plan_bundle = support.plan_bundle


def test_open_without_plan_inputs_and_read_only_own_encounter(client, monkeypatch, science_bundle):
    from app.database import SessionLocal

    enable(monkeypatch)
    install()
    with SessionLocal() as db:
        authority, pins = support.activate_test_authority(db, science_bundle)
    headers = token(client)
    spec = authority["v3"]["policy"]["selection"][0]
    body = {
        "request_id": "first-ever",
        "expected_revision": 0,
        "context": {
            "canonical_exercise_id": spec["candidate_id"],
            "realization_ref": spec["realization_ref"],
            "context_ref": None,
            "equipment_ref": None,
            "load_semantics": "UNKNOWN",
            "side": "BILATERAL",
        },
        "availability": "UNKNOWN",
        "concern_state": "UNKNOWN",
    }
    assert (
        client.post(
            ROOT + "/me/blueprint/calibration-encounters", headers=headers, json=body
        ).status_code
        == 406
    )
    headers = {**headers, "X-Auren-Calibration": "first-calibration-encounter/1.0.0"}
    opened = client.post(ROOT + "/me/blueprint/calibration-encounters", headers=headers, json=body)
    assert opened.status_code == 200, opened.text
    identity = opened.json()["encounter_ref"]
    assert (
        client.post(
            ROOT + "/me/blueprint/calibration-encounters", headers=headers, json=body
        ).json()["encounter_ref"]
        == identity
    )
    viewed = client.get(ROOT + "/me/blueprint/calibration-encounters/" + identity, headers=headers)
    assert viewed.status_code == 200, viewed.text
    assert viewed.json()["encounter"]["progress"]["observed_attempt_count"] == 0
    assert "INITIATE_TRIAL" not in viewed.json()["encounter"]["allowed_actions"]
    assert (
        client.get(
            ROOT + "/me/blueprint/calibration-encounters/unknown", headers=headers
        ).status_code
        == 404
    )
    # A valid calibration result never becomes a durable plan evaluation/session.
    with SessionLocal() as db:
        from app.models.first_plan_runtime import FirstPlanEvaluation, FirstSessionRequest

        assert db.query(FirstPlanEvaluation).count() == 0
        assert db.query(FirstSessionRequest).count() == 0
