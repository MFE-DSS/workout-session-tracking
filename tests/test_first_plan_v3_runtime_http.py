"""Actual transport consumes the actual private producer, no fixture READY."""

from tests import plan_v3_test_support as support
from tests.plan_v3_test_support import activate_test_authority
from tests.test_blueprint_runtime_http import ROOT, enable, token
from tests.test_plan_v3_persistence import install

science_bundle = support.science_bundle
plan_bundle = support.plan_bundle


def test_http_negative_result_is_durable_and_authority_status_is_explicit(
    client, monkeypatch, science_bundle
):
    from app.config import get_settings
    from app.database import SessionLocal

    enable(monkeypatch)
    monkeypatch.setattr(get_settings(), "plan_v3_evaluation_enabled", True)
    install()
    with SessionLocal() as db:
        authority, pins = activate_test_authority(db, science_bundle)
    headers = token(client)
    caps = client.get(ROOT + "/me/first-plan/capabilities", headers=headers)
    assert caps.json()["controlled_authority"]["pins"] == pins
    captured = client.post(
        ROOT + "/me/blueprint/snapshots",
        headers=headers,
        json={"request_id": "empty", "expected_revision": 0},
    ).json()
    body = {
        "request_id": "evaluate-empty",
        "snapshot_ref": captured["snapshot_ref"],
        "expected_pins": pins,
    }
    response = client.post(ROOT + "/me/first-plan/evaluations", headers=headers, json=body)
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["recommendation"]["scientific_readiness"] == "INSUFFICIENT_DATA"
    assert result["recommendation"]["start_permission"] == "DENIED"
    assert (
        client.post(ROOT + "/me/first-plan/evaluations", headers=headers, json=body).json()[
            "evaluation_ref"
        ]
        == result["evaluation_ref"]
    )
    assert (
        client.get(
            ROOT + "/me/first-plan/evaluations/" + result["evaluation_ref"], headers=headers
        ).json()["recommendation"]
        == result["recommendation"]
    )
    assert (
        client.post(
            ROOT
            + "/me/first-plan/evaluations/"
            + result["evaluation_ref"]
            + "/time-acknowledgments",
            headers=headers,
            json={"request_id": "ack-denied", "expected_context": {}},
        ).status_code
        == 409
    )
    monkeypatch.setattr(get_settings(), "plan_v3_acquisition_enabled", False)
    monkeypatch.setattr(get_settings(), "plan_v3_evaluation_enabled", False)
    history = client.get(ROOT + "/me/blueprint/declarations", headers=headers)
    assert history.status_code == 200, history.text
    assert any(
        row["request_id"] == "empty" and row["snapshot_ref"] == captured["snapshot_ref"]
        for row in history.json()["receipts"]["snapshots"]
    )
    assert any(
        row["request_id"] == "evaluate-empty" and row["evaluation_ref"] == result["evaluation_ref"]
        for row in history.json()["receipts"]["evaluations"]
    )
