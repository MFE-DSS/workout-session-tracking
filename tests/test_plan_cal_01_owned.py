"""Seven real owner-bound guided encounters, not imported READY examples."""

from datetime import UTC, datetime

import pytest

from tests import plan_v3_test_support as support
from tests.test_blueprint_runtime_http import ROOT, enable, token
from tests.test_plan_v3_persistence import install


@pytest.fixture(scope="session")
def science_bundle(tmp_path_factory):
    from tools.plan_calibration_runtime_bundle import build_bundle

    root = tmp_path_factory.mktemp("cal-seven") / "private"
    return root, build_bundle(root)


plan_bundle = support.plan_bundle
INVENTORY = "plan-calibration-inventory/2.0.0"


def setup_runtime(client, monkeypatch, science_bundle):
    from app.config import get_settings
    from app.database import SessionLocal

    enable(monkeypatch)
    for flag in ("guidance", "evaluation", "creation"):
        monkeypatch.setattr(get_settings(), "plan_v3_" + flag + "_enabled", True)
    install()
    with SessionLocal() as db:
        authorities, pins = support.activate_test_authority(db, science_bundle)
    h = {
        **token(client),
        "X-Auren-Calibration": "first-calibration-encounter/1.0.0",
        "X-Auren-Calibration-Inventory": INVENTORY,
    }
    return h, authorities, pins


def test_negotiated_inventory_and_first_open_without_history(client, monkeypatch, science_bundle):
    h, authorities, _ = setup_runtime(client, monkeypatch, science_bundle)
    capability = client.get(ROOT + "/me/first-plan/capabilities", headers=h)
    assert capability.status_code == 200, capability.text
    assert capability.json()["calibration_inventory"]["version"] == INVENTORY
    assert (
        sum(p["initial_guidance_supported"] for p in capability.json()["supported_realizations"])
        == 7
    )
    assert capability.headers["X-Auren-Calibration-Inventory"] == INVENTORY
    wrong = client.get(
        ROOT + "/me/first-plan/capabilities",
        headers={**h, "X-Auren-Calibration-Inventory": "future"},
    )
    assert wrong.status_code == 406
    spec = authorities["calibration_inventory"]["profiles"][1]
    body = {
        "request_id": "open-zero",
        "expected_revision": 0,
        "context": context(spec, "device:first"),
        "availability": "UNKNOWN",
        "concern_state": "UNKNOWN",
    }
    opened = client.post(ROOT + "/me/blueprint/calibration-encounters", headers=h, json=body)
    assert opened.status_code == 200, opened.text
    ref = opened.json()["encounter_ref"]
    view = client.get(ROOT + "/me/blueprint/calibration-encounters/" + ref, headers=h).json()[
        "encounter"
    ]
    assert view["authority"]["inventory_version"] == INVENTORY
    assert view["progress"]["observed_attempt_count"] == 0
    assert "INITIATE_TRIAL" not in view["allowed_actions"]
    assert view["selected"] is True
    assert (
        client.get(
            ROOT + "/me/blueprint/calibration-encounters/" + ref,
            headers={k: v for k, v in h.items() if k != "X-Auren-Calibration-Inventory"},
        ).status_code
        == 406
    )
    legacy = client.get(
        ROOT + "/me/first-plan/capabilities",
        headers={k: v for k, v in h.items() if k != "X-Auren-Calibration-Inventory"},
    )
    assert (
        sum(p["initial_guidance_supported"] for p in legacy.json()["supported_realizations"]) == 1
    )


def context(spec, device):
    return {
        "canonical_exercise_id": spec["candidate_id"],
        "realization_ref": spec["realization_ref"],
        "context_ref": "synthetic:actual-room",
        "equipment_ref": device,
        "side": "BILATERAL",
        "load_semantics": spec["load_semantics"],
    }


class Journey:
    def __init__(self, client, headers):
        self.client, self.h, self.revision, self.n = client, headers, 0, 0

    def call(self, method, path, body=None, extra=None):
        response = self.client.request(
            method, ROOT + path, headers={**self.h, **(extra or {})}, json=body
        )
        assert response.status_code == 200, (path, response.status_code, response.text)
        return response.json()

    def key(self):
        self.n += 1
        return f"act:{self.n}"

    def view(self, ref):
        return self.call("GET", "/me/blueprint/calibration-encounters/" + ref)["encounter"]

    def act(self, ref, observation):
        view = self.view(ref)
        body = {
            "request_id": self.key(),
            "expected_revision": self.revision,
            "event": {
                "kind": "ENCOUNTER_OBSERVATION",
                "encounter_ref": ref,
                "expected_authority": view["authority"],
                "observation": observation,
            },
        }
        response = self.call("POST", "/me/blueprint/observations", body)
        self.revision = response["source_revision"]
        # Simulate a lost response, retry original identity/body after revision advanced.
        replay = self.call("POST", "/me/blueprint/observations", body)
        assert replay["event_ref"] == response["event_ref"]
        return response

    def open(self, spec, device="synthetic:device"):
        opened = self.call(
            "POST",
            "/me/blueprint/calibration-encounters",
            {
                "request_id": self.key(),
                "expected_revision": self.revision,
                "context": context(spec, device),
                "availability": "AVAILABLE",
                "concern_state": "CLEAR",
            },
        )
        self.revision = opened["source_revision"]
        return opened["encounter_ref"]

    def qualify(self, spec, value):
        ref = self.open(spec)
        setting = {"kind": "MASS_KG", "unit": "kg", "value": value}
        self.act(
            ref,
            {
                "kind": "PREPARATION_REPORTED",
                "instruction_ref": "synthetic:applicable-device-instructions",
                "setup_ref": "synthetic:actual-setup",
                "understood": True,
                "controlled": True,
            },
        )
        self.act(ref, {"kind": "SETTING_CHOICE_REPORTED", "setting": setting, "available": True})
        self.act(
            ref,
            {
                "kind": "CALIBRATION_EVENT_REPORTED",
                "event": {"kind": "CONTEXT_CONFIRMED", "setting": setting},
            },
        )
        self.act(
            ref,
            {
                "kind": "CALIBRATION_EVENT_REPORTED",
                "event": {"kind": "FAMILIARIZATION_CONFIRMED", "setting": setting},
            },
        )
        assert "INITIATE_TRIAL" in self.view(ref)["allowed_actions"]
        observed = self.act(
            ref,
            {
                "kind": "CALIBRATION_EVENT_REPORTED",
                "stop_reason": "COMPLETED",
                "event": {
                    "kind": "ATTEMPT_OBSERVED",
                    "setting": setting,
                    "reps": 10,
                    "completed": True,
                    "successful": True,
                    "technique": "ACCEPTABLE",
                    "discomfort": "NO_CONCERN",
                    "occurred_at": datetime.now(UTC).isoformat(),
                },
            },
        )
        self.act(
            ref,
            {
                "kind": "CALIBRATION_EVENT_REPORTED",
                "event": {"kind": "SETTING_ACCEPTED", "reference_event_id": observed["event_ref"]},
            },
        )
        assert self.view(ref)["result"]["state"] == "QUALIFIED"
        return ref, setting


def test_seven_guided_encounters_feed_owned_v3_and_response_loss_recovery(
    client, monkeypatch, science_bundle
):
    h, authority, pins = setup_runtime(client, monkeypatch, science_bundle)
    j = Journey(client, h)
    fields = {
        k: {"state": "KNOWN", "value": v}
        for k, v in {
            "objective": "HYPERTROPHY",
            "population_scope": "ADULT_NON_CLINICAL",
            "sessions_per_week": 2,
            "session_budgets_minutes": [60, 60],
            "limitations": [],
        }.items()
    }
    j.revision = j.call(
        "PUT",
        "/me/blueprint/declarations",
        {"request_id": j.key(), "fields": fields},
        {"If-Match": "0"},
    )["source_revision"]
    refs = []
    for i, spec in enumerate(authority["calibration_inventory"]["profiles"]):
        refs.append(j.qualify(spec, 17.0 + i)[0])  # Explicit synthetic user observations only.
    snapshot = j.call(
        "POST", "/me/blueprint/snapshots", {"request_id": j.key(), "expected_revision": j.revision}
    )
    evaluated = j.call(
        "POST",
        "/me/first-plan/evaluations",
        {"request_id": j.key(), "snapshot_ref": snapshot["snapshot_ref"], "expected_pins": pins},
    )
    r = evaluated["recommendation"]
    assert r["scientific_readiness"] == "SCIENTIFICALLY_READY"
    assert r["start_permission"] == "REQUIRES_TIME_ACK"
    assert all(t["state"] == "BUDGET_UNCERTAIN" for t in r["time_assessments"])
    final = j.call(
        "POST",
        "/me/first-plan/evaluations/" + evaluated["evaluation_ref"] + "/time-acknowledgments",
        {
            "request_id": j.key(),
            "expected_context": {
                k: r[k]
                for k in (
                    "request_fingerprint",
                    "observation_fingerprint",
                    "plan_time_fingerprint",
                    "start_policy_ref",
                )
            },
        },
    )
    r = final["recommendation"]
    assert r["start_permission"] == "ELIGIBLE"
    command = {
        k: r[k]
        for k in (
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
            "contract_version",
        )
    }
    command.update(
        evaluation_ref=final["evaluation_ref"],
        snapshot_ref=snapshot["snapshot_ref"],
        source_revision=j.revision,
        registry_digest=pins["registry_digest"],
        selected_scientific_session_id=r["candidate_plan"]["sessions"][0]["session_id"],
    )
    body = {"request_id": j.key(), "command": command}
    started = j.call("POST", "/me/first-session-requests", body)
    assert started["state"] == "CREATED"
    assert j.call("POST", "/me/first-session-requests", body)["session_id"] == started["session_id"]
    execution = j.call("GET", f"/sessions/{started['session_id']}/execution")["execution"]
    assert len(execution["exercises"]) == 7
    assert sum(len(e["sets"]) for e in execution["exercises"]) == 14
    ex = next(
        e
        for e in execution["exercises"]
        if e["canonical_exercise_id"] == "romanian-deadlift-halteres"
    )
    fact = {
        "context": ex["prescription"]["context"],
        "setting": ex["prescription"]["setting"],
        "reps": 9,
        "completed": True,
        "performed_at": datetime.now(UTC).isoformat(),
    }
    receipt = j.call(
        "PUT",
        f"/sessions/{started['session_id']}/sets/{ex['sets'][0]['set_id']}",
        {"op_id": "actual-rdl", "expected_set_revision": 0, "observation": fact},
    )["receipt"]
    assert receipt["state"] == "APPLIED"
    refreshed = j.call("GET", f"/sessions/{started['session_id']}/execution")["execution"]
    logged = next(
        e
        for e in refreshed["exercises"]
        if e["canonical_exercise_id"] == "romanian-deadlift-halteres"
    )["sets"][0]["observation"]
    assert logged["setting"]["value"] == ex["prescription"]["setting"]["value"]
    assert logged["context"]["load_semantics"] == "PER_IMPLEMENT"
    import json

    from app.database import SessionLocal
    from app.models.first_plan_runtime import OwnedBlueprintSnapshot

    with SessionLocal() as db:
        data = json.loads(db.get(OwnedBlueprintSnapshot, snapshot["snapshot_ref"]).snapshot_json)
        assert len(data["calibration_runtime"]["qualified_encounters"]) == 7
        assert set(data["calibration_runtime"]["selected_encounters"].values()) == set(refs)


def test_new_setting_and_new_context_do_not_reuse_old_permission(
    client, monkeypatch, science_bundle
):
    h, authority, _ = setup_runtime(client, monkeypatch, science_bundle)
    j = Journey(client, h)
    j.revision = j.call(
        "PUT",
        "/me/blueprint/declarations",
        {
            "request_id": j.key(),
            "fields": {
                "population_scope": {"state": "KNOWN", "value": "ADULT_NON_CLINICAL"},
                "limitations": {"state": "KNOWN", "value": []},
            },
        },
        {"If-Match": "0"},
    )["source_revision"]
    spec = authority["calibration_inventory"]["profiles"][1]
    ref, setting = j.qualify(spec, 13.5)
    j.act(
        ref,
        {
            "kind": "SETTING_CHOICE_REPORTED",
            "setting": {**setting, "value": 19.0},
            "available": True,
        },
    )
    changed = j.view(ref)
    assert changed["result"]["state"] != "QUALIFIED"
    assert "INITIATE_TRIAL" not in changed["allowed_actions"]
    captured = j.call(
        "POST", "/me/blueprint/snapshots", {"request_id": j.key(), "expected_revision": j.revision}
    )
    import json

    from app.database import SessionLocal
    from app.models.first_plan_runtime import OwnedBlueprintSnapshot

    with SessionLocal() as db:
        data = json.loads(db.get(OwnedBlueprintSnapshot, captured["snapshot_ref"]).snapshot_json)
        assert ref in data["review_source_refs"]
        assert not data["episodes"]
    new_ref = j.open(spec, "synthetic:new-device")
    assert j.view(ref)["selected"] is False
    assert "ACCEPT_EXACT_SETTING" not in j.view(ref)["allowed_actions"]
    assert j.view(new_ref)["progress"]["observed_attempt_count"] == 0
    assert j.view(ref)["progress"]["observed_attempt_count"] == 1
    selected = j.call(
        "POST",
        "/me/blueprint/observations",
        {
            "request_id": j.key(),
            "expected_revision": j.revision,
            "event": {"kind": "CALIBRATION_ENCOUNTER_SELECTED", "encounter_ref": ref},
        },
    )
    j.revision = selected["source_revision"]
    assert j.view(ref)["selected"] is True
    assert j.view(ref)["result"]["state"] != "QUALIFIED"


def test_unknown_quality_and_withdrawal_preserve_facts_and_block_new_encounter(
    client, monkeypatch, science_bundle
):
    h, authority, _ = setup_runtime(client, monkeypatch, science_bundle)
    j = Journey(client, h)
    j.revision = j.call(
        "PUT",
        "/me/blueprint/declarations",
        {
            "request_id": j.key(),
            "fields": {
                "population_scope": {"state": "KNOWN", "value": "ADULT_NON_CLINICAL"},
                "limitations": {"state": "KNOWN", "value": []},
            },
        },
        {"If-Match": "0"},
    )["source_revision"]
    spec = authority["calibration_inventory"]["profiles"][1]
    ref = j.open(spec)
    # Actual concerning fact is retained even without granting an instruction.
    j.act(ref, {"kind": "CALIBRATION_EVENT_REPORTED", "event": {"kind": "CONCERN_REPORTED"}})
    new = j.open(spec, "synthetic:other-device")
    assert j.view(new)["result"]["state"] == "CONCERN_REVIEW"
    assert "INITIATE_TRIAL" not in j.view(new)["allowed_actions"]
    j.act(new, {"kind": "ENCOUNTER_WITHDRAWN"})
    assert j.view(ref)["progress"]["events"]
    assert "INITIATE_TRIAL" not in j.view(ref)["allowed_actions"]


def test_inventory2_raw_c3_is_preserved_as_facts_but_never_guidance_authority():
    from types import SimpleNamespace

    from app.services.plan_v3.calibration_profiles import project_qualified

    episode = {
        "episode_id": "raw-owned",
        "context": {"canonical_exercise_id": "chest-press-machine"},
    }
    operational = SimpleNamespace(packaging_digest="package", generation=1)
    authorities = {
        "calibration_inventory": {"version": INVENTORY, "bundle_digest": "extension"},
        "encounter": {"bundle_digest": "pilot"},
    }
    kept, review, runtime = project_qualified(
        [], 1, "2026-11-09T12:00:00Z", [episode], operational, authorities
    )
    assert kept == []
    assert review == ["raw-owned"]
    assert runtime["qualified_encounters"] == []


def test_current_projection_context_and_ambiguous_legacy_guidance():
    import json
    from types import SimpleNamespace

    from app.services.plan_v3.calibration_profiles import current_selection, projection_context

    rows = [
        SimpleNamespace(
            id=ref,
            kind="CALIBRATION_ENCOUNTER_OPENED",
            payload_json=json.dumps(
                {"context": {"canonical_exercise_id": "leg-extensions-assises"}}
            ),
        )
        for ref in ("old-a", "old-b")
    ]
    assert current_selection(rows, "old-a", "leg-extensions-assises") is False
    assert current_selection(rows[:1], "old-a", "leg-extensions-assises") is True
    assert projection_context([{"context": {"context_ref": "selected-room"}}]) == "selected-room"
    assert (
        projection_context([{"context": {"context_ref": "a"}}, {"context": {"context_ref": "b"}}])
        == "environment:unknown"
    )


def test_http_raw_current_acquisition_cannot_bypass_inventory2(client, monkeypatch, science_bundle):
    h, authority, pins = setup_runtime(client, monkeypatch, science_bundle)
    j = Journey(client, h)
    fields = {
        k: {"state": "KNOWN", "value": v}
        for k, v in {
            "objective": "HYPERTROPHY",
            "population_scope": "ADULT_NON_CLINICAL",
            "sessions_per_week": 2,
            "session_budgets_minutes": [60, 60],
            "limitations": [],
        }.items()
    }
    j.revision = j.call(
        "PUT",
        "/me/blueprint/declarations",
        {"request_id": j.key(), "fields": fields},
        {"If-Match": "0"},
    )["source_revision"]
    spec = authority["calibration_inventory"]["profiles"][1]

    def observe(event):
        value = j.call(
            "POST",
            "/me/blueprint/observations",
            {"request_id": j.key(), "expected_revision": j.revision, "event": event},
        )
        j.revision = value["source_revision"]
        return value

    ep = observe(
        {
            "kind": "CONTEXT_OPENED",
            "context": context(spec, "synthetic:raw-device"),
            "availability": "AVAILABLE",
        }
    )["episode_ref"]
    setting = {"kind": "MASS_KG", "unit": "kg", "value": 11.0}
    for event in (
        {"kind": "CONTEXT_CONFIRMED", "setting": setting},
        {"kind": "FAMILIARIZATION_CONFIRMED"},
    ):
        observe({"kind": "CALIBRATION_EVENT", "episode_ref": ep, "event": event})
    trial = observe(
        {
            "kind": "CALIBRATION_EVENT",
            "episode_ref": ep,
            "event": {
                "kind": "ATTEMPT_OBSERVED",
                "setting": setting,
                "reps": 10,
                "completed": True,
                "successful": True,
                "technique": "ACCEPTABLE",
                "discomfort": "NO_CONCERN",
                "familiarization_confirmed": True,
                "occurred_at": datetime.now(UTC).isoformat(),
            },
        }
    )["event_ref"]
    observe(
        {
            "kind": "CALIBRATION_EVENT",
            "episode_ref": ep,
            "event": {"kind": "SETTING_ACCEPTED", "reference_event_id": trial},
        }
    )
    snap = j.call(
        "POST", "/me/blueprint/snapshots", {"request_id": j.key(), "expected_revision": j.revision}
    )
    response = client.post(
        ROOT + "/me/first-plan/evaluations",
        headers=h,
        json={"request_id": j.key(), "snapshot_ref": snap["snapshot_ref"], "expected_pins": pins},
    )
    assert response.status_code == 409
    assert response.json()["detail"]["error"] == "calibration_review_required"
    assert (
        j.call("GET", "/me/blueprint/declarations")["observation_progress"][0]["events"][-1]["kind"]
        == "SETTING_ACCEPTED"
    )


def test_factual_feedback_preserves_explicit_stop_reason_without_inferring_from_completion():
    import json
    from types import SimpleNamespace

    from app.services.plan_v3.calibration import factual_progress

    rows = [
        SimpleNamespace(
            id="enc",
            kind="CALIBRATION_ENCOUNTER_OPENED",
            payload_json=json.dumps(
                {"episode_ref": "enc", "context": {}, "availability": "AVAILABLE"}
            ),
        ),
        SimpleNamespace(
            id="reported",
            kind="CALIBRATION_EVENT_REPORTED",
            payload_json=json.dumps(
                {
                    "episode_ref": "enc",
                    "event": {
                        "event_id": "trial",
                        "kind": "ATTEMPT_OBSERVED",
                        "completed": True,
                        "provenance": {"recorded_at": "2026-11-09T10:00:00Z"},
                    },
                    "stop_reason": "TIME_LIMIT",
                }
            ),
        ),
    ]
    progress = factual_progress(rows, "enc")
    assert progress["reported_stop_reasons"]["trial"] == {
        "value": "TIME_LIMIT",
        "source_ref": "reported",
        "recorded_at": "2026-11-09T10:00:00Z",
    }
