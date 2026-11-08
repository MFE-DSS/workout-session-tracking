"""Whole-branch review regressions through the real public authority."""

import copy

import pytest

from tests.science_bootstrap_samples import encounter
from tools.science_calibration_bootstrap.evaluator import evaluate
from tools.science_calibration_bootstrap.policy import load_authority
from tools.science_calibration_bootstrap.validation import validate_result


@pytest.mark.parametrize("field", ["population", "limitations"])
@pytest.mark.parametrize("origin", ["POPULATION_PRIOR", "DERIVED_FROM_HISTORY", "PRODUCT_CONTRACT"])
def test_inapplicable_provenance_never_substitutes_personal_declarations(field, origin):
    raw = encounter(stage="trial")
    raw[field]["provenance"].update(
        origin=origin,
        acquisition="DERIVED",
        source_ref="synthetic:population-default",
        recorded_at=None,
        measured_at=None,
    )
    authority = load_authority()
    out = validate_result(raw, evaluate(raw, authority), authority)
    assert "INITIATE_TRIAL" not in out.allowed_actions
    assert out.state == "INSUFFICIENT_EVIDENCE"


def test_undated_personal_declaration_is_not_a_dated_answer():
    raw = encounter(stage="trial")
    raw["limitations"]["provenance"].update(recorded_at=None, measured_at=None)
    assert "INITIATE_TRIAL" not in evaluate(raw, load_authority()).allowed_actions


@pytest.mark.parametrize(
    "confirmation_at,can_begin", [("2026-11-07T11:02:00Z", False), ("2026-11-07T11:02:45Z", True)]
)
def test_familiarization_restart_uses_real_occurrence_not_recording_order(
    confirmation_at, can_begin
):
    raw = encounter(stage="trial")
    ep = raw["episode"]
    start = copy.deepcopy(ep["events"][1])
    start.update(event_id="synthetic:restart", sequence=2, kind="FAMILIARIZATION_STARTED")
    start["provenance"].update(
        recorded_at="2026-11-07T11:03:00Z", measured_at="2026-11-07T11:02:30Z"
    )
    confirm = copy.deepcopy(ep["events"][1])
    confirm["sequence"] = 3
    confirm["provenance"].update(recorded_at="2026-11-07T11:04:00Z", measured_at=confirmation_at)
    ep["events"] = [ep["events"][0], start, confirm]
    out = evaluate(raw, load_authority())
    assert ("INITIATE_TRIAL" in out.allowed_actions) is can_begin


def test_current_context_replacement_does_not_offer_old_setting_acceptance():
    raw = encounter(stage="observed")
    ep = raw["episode"]
    newer = copy.deepcopy(ep["events"][0])
    newer.update(event_id="synthetic:new-setting", sequence=4)
    newer["setting"]["value"] = 45.0
    newer["provenance"]["recorded_at"] = "2026-11-07T11:04:00Z"
    ep["events"].append(newer)
    out = evaluate(raw, load_authority())
    assert "ACCEPT_EXACT_SETTING" not in out.allowed_actions
    assert out.qualified_setting is None
