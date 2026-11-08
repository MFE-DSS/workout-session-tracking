"""V3 session is actually readable/loggable/closable through authenticated APIs."""

from datetime import UTC, datetime

from tests import plan_v3_test_support as support
from tests.test_blueprint_runtime_http import ROOT, enable, token
from tests.test_first_session_commands import final_evaluation, start_body
from tests.test_plan_v3_persistence import install

science_bundle = support.science_bundle
plan_bundle = support.plan_bundle


def test_owned_session_http_execution_logging_finish_and_typed_export(
    client, monkeypatch, science_bundle
):
    from app.config import get_settings
    from app.database import SessionLocal
    from app.models.session import SessionExercise, WorkoutSession
    from app.models.user import User
    from app.services.export_builder import build_json_payload

    enable(monkeypatch)
    for flag in (
        "plan_v3_evaluation_enabled",
        "plan_v3_creation_enabled",
        "plan_v3_guidance_enabled",
    ):
        monkeypatch.setattr(get_settings(), flag, True)
    install()
    with SessionLocal() as db:
        owner = db.query(User).one().id
        final = final_evaluation(db, owner, science_bundle, monkeypatch)
        body = start_body(final)
    headers = token(client)
    created = client.post(
        ROOT + "/me/first-session-requests",
        headers=headers,
        json={"request_id": "native-command", "command": body},
    )
    assert created.status_code == 200, created.text
    receipt = created.json()
    session_id = receipt["session_id"]
    assert receipt["state"] == "CREATED"
    assert (
        client.post(
            ROOT + "/me/first-session-requests",
            headers=headers,
            json={"request_id": "native-command", "command": body},
        ).json()["session_id"]
        == session_id
    )
    assert (
        client.get(ROOT + "/me/first-session-handoff", headers=headers).json()["handoff"][
            "session_id"
        ]
        == session_id
    )
    assert (
        client.get(
            "/api/mobile/v1/sessions/" + str(session_id) + "/execution", headers=headers
        ).status_code
        == 409
    )
    execution = client.get(ROOT + f"/sessions/{session_id}/execution", headers=headers)
    assert execution.status_code == 200, execution.text
    assert datetime.fromisoformat(execution.json()["execution"]["server_now"])
    se = execution.json()["execution"]["exercises"][0]
    set_id = se["sets"][0]["set_id"]
    fact = {
        "context": se["prescription"]["context"],
        "setting": {"kind": "MASS_KG", "value": 15.0, "unit": "kg"},
        "reps": 8,
        "completed": True,
        "performed_at": datetime.now(UTC).isoformat(),
    }
    applied = client.put(
        ROOT + f"/sessions/{session_id}/sets/{set_id}",
        headers=headers,
        json={"op_id": "typed-native-set", "expected_set_revision": 0, "observation": fact},
    )
    assert applied.status_code == 200, applied.text
    assert applied.json()["receipt"]["state"] == "APPLIED"
    assert (
        client.put(
            "/api/mobile/v1/sessions/" + str(session_id) + "/sets/" + str(set_id),
            headers=headers,
            json={
                "op_id": "legacy-forbidden",
                "reps": 8,
                "weight_kg": 15.0,
                "performed_at": datetime.now(UTC).isoformat(),
            },
        ).status_code
        == 409
    )
    ended = client.post(
        "/api/mobile/v1/sessions/" + str(session_id) + "/finish", headers=headers, json={}
    )
    assert ended.status_code == 200, ended.text
    assert ended.json()["work_sets_done"] == 1
    assert ended.json()["work_sets_total"] == 14
    readback = client.get(ROOT + f"/sessions/{session_id}/execution", headers=headers).json()[
        "execution"
    ]
    assert readback["status"] == "completed"
    assert readback["exercises"][0]["sets"][0]["observation"]["setting"]["value"] == 15.0
    assert readback["derived_metrics"] == "NON_EVALUABLE"
    with SessionLocal() as db:
        assert db.query(WorkoutSession).count() == 1
        assert all(
            se.success_score is None and se.implicit_label is None
            for se in db.query(SessionExercise)
        )
        exported = build_json_payload(db, user_id=owner)["sessions"][0]
        assert exported["quality_score"] is None
        assert exported["confidence_score"] is None
        assert (
            exported["first_plan_execution"]["operations"][0]["observation"]["setting"]["value"]
            == 15.0
        )
        assert exported["exercises"][0]["sets"][0]["weight_kg"] is None
