"""Real limited-plan compilation, with explicitly synthetic execution facts."""

import copy
import importlib
import json
from pathlib import Path

import pytest

from tests.science_calibration_samples import calibrated_episode, context
from tools.science_initial_policy.calibration_time_contracts import content_digest
from tools.science_initial_policy.v3_admission import load_v3_registry

ROOT = Path(__file__).resolve().parents[1]


def api():
    return importlib.import_module("tools.science_initial_policy.v3_producer")


def request(registry=None):
    registry = registry or load_v3_registry()
    cases = json.loads((ROOT / "docs/science/sci-p01-p02/v3/contract-fixtures.v3.json").read_text())
    value = copy.deepcopy(next(c["request"] for c in cases if c["scenario"] == "sufficient"))
    value.update(
        as_of="2026-11-07T12:00:00Z",
        bundle_digest=registry.bundle_digest,
        effective_science_digest=registry.effective_science_digest,
        requested_binding_ref=registry.binding_ref,
        episodes=[],
        timing_inputs=[],
        acknowledgment=None,
    )
    value["versions"].update(
        engine=registry.policy["engine_version"], policy=registry.policy["policy_version"]
    )
    env = value["blueprint"]["environment"]
    env.update(context_ref="gym:test-a", exercise_confirmations=[])
    unknown = copy.deepcopy(value["blueprint"]["legacy_weight_kg"])
    unknown.update(state="UNKNOWN", value=None, conflicts=[])
    env["equipment_items"] = copy.deepcopy(unknown)
    for field in ["weight_kg", "height_cm", "experience", "declared_priorities"]:
        value["blueprint"][field] = copy.deepcopy(unknown)
    for selected in registry.policy["selection"]:
        identity = selected["candidate_id"]
        ctx = context(
            canonical_exercise_id=identity,
            realization_ref=selected["realization_ref"],
            equipment_ref="synthetic:device:" + identity,
            load_semantics="PER_IMPLEMENT"
            if identity == "romanian-deadlift-halteres"
            else "MACHINE_DISPLAY_KG",
        )
        # 40 is a synthetic observed device value inherited from the test dataset;
        # the engine never prescribes it from demographics or another exercise.
        ep = calibrated_episode(ctx=ctx)
        ep.update(episode_id="synthetic:episode:" + identity, subject_ref=value["subject_ref"])
        ep["ledger_source_ref"] = "synthetic:ledger:" + identity
        for source in [ep["context_provenance"], *[e["provenance"] for e in ep["events"]]]:
            source["source_ref"] += ":" + identity
        ep = json.loads(json.dumps(ep).replace("2026-11-06", "2026-11-07"))
        for event in ep["events"]:
            event["subject_ref"] = value["subject_ref"]
            old_id = event["event_id"]
            event["event_id"] = identity + ":" + old_id
            if event.get("reference_event_id"):
                event["reference_event_id"] = identity + ":" + event["reference_event_id"]
        value["episodes"].append(ep)
    return value


def test_compiles_two_seven_slot_sessions_and_honest_qualitative_report():
    registry = load_v3_registry()
    value = api().compile_plan_v3(request(registry), registry)
    assert not value.issues
    assert value.plan.physical_work_sets_total == 28
    assert len(value.plan.sessions) == 2
    assert all(len(s.slots) == 7 for s in value.plan.sessions)
    assert len(value.plan.zone_reports) == 15
    hip = next(z for z in value.plan.zone_reports if z.zone == "hip_flexors")
    assert hip.role_status == "UNKNOWN"
    assert len(hip.unresolved_slot_ids) == 14
    assert all(t.state == "BUDGET_UNCERTAIN" for t in value.time_assessments)
    assert all(t.known_rest_floor_seconds == 750 for t in value.time_assessments)
    assert value.plan.review_state == "DRAFT" or registry.admitted
    for session in value.plan.sessions:
        for slot in session.slots:
            assert slot.prescription.mode == "OBSERVED_SETTING"
            assert slot.prescription.setting.value == 40.0
            assert slot.selected.realization_ref == slot.prescription.context.realization_ref


@pytest.mark.parametrize(
    "change",
    [
        "missing_objective",
        "cadence3",
        "limitations",
        "excluded",
        "exclusion_conflict",
        "no_episode",
        "unavailable",
        "old_observations",
        "concern",
        "side",
        "realization",
        "equipment",
        "bootstrap",
    ],
)
def test_inapplicable_or_unqualified_inputs_do_not_compile_a_positive(change):
    raw = request()
    r = load_v3_registry()
    bp = raw["blueprint"]
    ep = raw["episodes"][0]
    if change == "missing_objective":
        bp["objective"].update(state="UNKNOWN", value=None)
    elif change == "cadence3":
        bp["sessions_per_week"]["value"] = 3
        bp["session_budgets_minutes"]["value"] = [75, 75, 75]
    elif change == "limitations":
        bp["limitations"]["value"] = ["reported limitation"]
    elif change in {"excluded", "exclusion_conflict"}:
        fact = copy.deepcopy(bp["limitations"])
        fact["value"] = [ep["context"]["canonical_exercise_id"]]
        if change == "exclusion_conflict":
            fact.update(
                state="CONFLICT",
                value=None,
                conflicts=[dict(value=[], source_ref="a"), dict(value=["pompes"], source_ref="b")],
            )
        bp["excluded_exercise_ids"] = fact
    elif change == "no_episode":
        raw["episodes"].pop()
    elif change == "unavailable":
        ep["availability"] = "UNAVAILABLE"
    elif change == "old_observations":
        ep["events"] = json.loads(json.dumps(ep["events"]).replace("2026-11-07", "2026-11-06"))
    elif change == "concern":
        event = copy.deepcopy(ep["events"][-1])
        event.update(
            event_id="synthetic:concern",
            sequence=5,
            kind="CONCERN_REPORTED",
            reference_event_id=None,
        )
        event["provenance"]["recorded_at"] = "2026-11-07T11:05:00Z"
        ep["events"].append(event)
    elif change in {"side", "realization", "equipment"}:
        field = {"side": "side", "realization": "realization_ref", "equipment": "equipment_ref"}[
            change
        ]
        ep["context"][field] = {"side": "LEFT", "realization": "UNREVIEWED", "equipment": None}[
            change
        ]
        for event in ep["events"]:
            event["context_fingerprint"] = content_digest(ep["context"])
    else:
        ep["events"] = ep["events"][:2]
    out = api().compile_plan_v3(raw, r)
    assert out.plan is None
    assert out.issues


@pytest.mark.parametrize("field", ["engine", "policy"])
def test_no_silent_version_conversion(field):
    raw = request()
    raw["versions"][field] = "historical:unsupported"
    with pytest.raises(ValueError):
        api().compile_plan_v3(raw, load_v3_registry())


def test_unrelated_optional_anthropometry_conflict_is_not_a_plan_requirement():
    raw = request()
    raw["blueprint"]["weight_kg"].update(
        state="CONFLICT",
        value=None,
        conflicts=[dict(value=70.0, source_ref="a"), dict(value=80.0, source_ref="b")],
    )
    assert api().compile_plan_v3(raw, load_v3_registry()).plan is not None


@pytest.mark.parametrize("case", ["wrong_owner", "copied_bool", "nan"])
def test_structural_owner_and_scalar_attacks_are_rejected(case):
    from tools.science_contracts.blueprint_first_plan_v3 import validated_request

    raw = request()
    if case == "wrong_owner":
        raw["episodes"][0]["subject_ref"] = "subject:B"
    elif case == "nan":
        raw["episodes"][0]["events"][2]["setting"]["value"] = float("nan")
    else:
        typed = validated_request(raw)
        bad = typed.episodes[0].events[2].setting.model_copy(update={"value": True})
        raw["episodes"][0]["events"][2]["setting"] = bad
    with pytest.raises(ValueError):
        api().compile_plan_v3(raw, load_v3_registry())


def test_rest_floor_never_becomes_positive_fit():
    raw = request()
    raw["blueprint"]["session_budgets_minutes"]["value"] = [12, 75]
    out = api().compile_plan_v3(raw, load_v3_registry())
    assert out.plan is None
    assert any(i.gate_ref == "C6" for i in out.issues)


def test_candidate_cannot_emit_an_authoritative_positive_or_validate_it():
    r = load_v3_registry()
    if not r.admitted:
        with pytest.raises(ValueError):
            api().produce_v3(request(r), r)
    validator = importlib.import_module("tools.science_initial_policy.v3_validation")
    with pytest.raises(ValueError):
        validator.validate_admitted_exchange_v3(request(r), {}, r)


def bad_phase_order(raw, change):
    ep = raw["episodes"][0]
    events = {e["kind"]: e for e in ep["events"]}
    started = copy.deepcopy(events["FAMILIARIZATION_CONFIRMED"])
    started.update(event_id="synthetic:late-familiarization-start", kind="FAMILIARIZATION_STARTED")
    events["FAMILIARIZATION_STARTED"] = started
    orders = {
        "late_familiarization": [
            "CONTEXT_CONFIRMED",
            "ATTEMPT_OBSERVED",
            "FAMILIARIZATION_CONFIRMED",
            "SETTING_ACCEPTED",
        ],
        "late_context": [
            "FAMILIARIZATION_CONFIRMED",
            "ATTEMPT_OBSERVED",
            "CONTEXT_CONFIRMED",
            "SETTING_ACCEPTED",
        ],
        "restart_after_trial": [
            "CONTEXT_CONFIRMED",
            "FAMILIARIZATION_CONFIRMED",
            "ATTEMPT_OBSERVED",
            "FAMILIARIZATION_STARTED",
            "SETTING_ACCEPTED",
        ],
        "restart_before_trial": [
            "CONTEXT_CONFIRMED",
            "FAMILIARIZATION_CONFIRMED",
            "FAMILIARIZATION_STARTED",
            "ATTEMPT_OBSERVED",
            "SETTING_ACCEPTED",
        ],
    }
    ep["events"] = [events[kind] for kind in orders[change]]
    for seq, e in enumerate(ep["events"], 1):
        e["sequence"] = seq
        stamp = f"2026-11-07T11:{seq:02}:00Z"
        e["provenance"]["recorded_at"] = stamp
        if e["provenance"]["measured_at"] is not None:
            e["provenance"]["measured_at"] = stamp
    return raw


@pytest.mark.parametrize(
    "change",
    ["late_familiarization", "late_context", "restart_after_trial", "restart_before_trial"],
)
def test_phase_qualification_cannot_be_retroactive_or_survive_restart(change):
    r = load_v3_registry()
    raw = bad_phase_order(request(r), change)
    result = api().compile_plan_v3(raw, r)
    assert result.plan is None
    assert any(issue.gate_ref == "C3" for issue in result.issues)


@pytest.mark.parametrize(
    "change",
    ["late_familiarization", "late_context", "restart_after_trial", "restart_before_trial"],
)
def test_validator_independently_rejects_retroactive_qualification(change):
    from tools.science_contracts.blueprint_first_plan_v3 import validated_request
    from tools.science_initial_policy.v3_validation import _observed_slot

    r = load_v3_registry()
    raw = request(r)
    good = api().compile_plan_v3(raw, r)
    req = validated_request(bad_phase_order(raw, change))
    with pytest.raises(ValueError):
        _observed_slot(
            req, good.plan.sessions[0].slots[0], r.policy["selection"][0], "session-1", 0, r
        )
