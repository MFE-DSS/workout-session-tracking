"""Conditional arithmetic is not a validated predictive session-duration policy."""

import copy
import importlib
import importlib.util

import pytest

from tests.science_calibration_samples import digest, time_components, time_session


def api():
    name = "tools.science_initial_policy.session_time"
    assert importlib.util.find_spec(name) is not None, "component time model is not implemented"
    return importlib.import_module(name).assess_session_time


def test_rest_floor_can_refute_but_never_certify_a_large_budget():
    run = api()
    small = run(time_session(), budget_minutes=1, components=[])
    assert small["ordinal"] == "LIKELY_EXCEEDS"
    assert small["known_rest_floor_seconds"] == 60
    assert small["constraint"]["scope"] == "THIS_CONFIGURATION_ONLY"
    assert small["constraint"]["prescribed_rest_preserved"] is True
    big = run(time_session(), budget_minutes=75, components=[])
    assert big["ordinal"] == "UNKNOWN"
    assert big["duration"]["state"] == "UNKNOWN"


def test_complete_explicit_experimental_intervals_can_conditionally_fit_not_admit_duration():
    s, pieces = time_session(), time_components()
    original = copy.deepcopy((s, pieces))
    out = api()(s, budget_minutes=2, components=pieces, layout="DISJOINT_SEQUENTIAL")
    assert out["ordinal"] == "LIKELY_FITS"
    assert out["lower_seconds"] == 100.0
    assert out["upper_seconds"] == 100.0
    assert out["duration"]["state"] == "UNKNOWN"
    assert out["duration"]["upper_minutes"] is None
    assert "NO_ADMITTED_TIME_MODEL" in out["uncertainty"]
    assert out["constraint"] is None
    assert (s, pieces) == original


def test_interval_overlap_with_budget_is_borderline_not_a_probability():
    pieces = time_components()
    pieces[-1]["upper_seconds"] = 50.0
    out = api()(time_session(), budget_minutes=2, components=pieces, layout="DISJOINT_SEQUENTIAL")
    assert out["ordinal"] == "BORDERLINE"
    assert (out["lower_seconds"], out["upper_seconds"]) == (100.0, 140.0)


def test_equality_at_total_upper_bound_fits_under_explicit_conditions():
    pieces = time_components()
    pieces[-1]["upper_seconds"] = 30.0
    out = api()(time_session(), budget_minutes=2, components=pieces, layout="DISJOINT_SEQUENTIAL")
    assert out["upper_seconds"] == 120.0
    assert out["ordinal"] == "LIKELY_FITS"


def test_known_component_lower_bound_refutes_only_this_configuration():
    pieces = time_components()
    pieces[-1].update(lower_seconds=100.0, upper_seconds=150.0)
    out = api()(time_session(), budget_minutes=2, components=pieces, layout="DISJOINT_SEQUENTIAL")
    assert out["ordinal"] == "LIKELY_EXCEEDS"
    assert out["constraint"]["code"] == "CONSTRAINT_VIOLATION"
    assert "NO_FEASIBLE_PLAN" not in str(out)


@pytest.mark.parametrize("missing", ["session/prep", "press/prep", "press/work/2", "press/operations"])
def test_missing_essential_component_never_gets_a_default_duration(missing):
    pieces = [p for p in time_components() if p["coverage_key"] != missing]
    out = api()(time_session(), budget_minutes=75, components=pieces, layout="DISJOINT_SEQUENTIAL")
    assert out["ordinal"] == "UNKNOWN"
    assert missing in out["missing_coverage"]
    assert out["upper_seconds"] is None


def test_unknown_component_bounds_keep_uncertainty_explicit():
    pieces = time_components()
    pieces[-1].update(lower_seconds=None, upper_seconds=None)
    out = api()(time_session(), budget_minutes=75, components=pieces, layout="DISJOINT_SEQUENTIAL")
    assert out["ordinal"] == "UNKNOWN"
    assert "COMPONENT_BOUND_UNKNOWN" in out["uncertainty"]


def test_exact_common_clock_counts_setup_overlapping_rest_once():
    pieces = time_components()
    spans = [(0, 0), (0, 10), (10, 20), (20, 80), (80, 90), (30, 40)]
    for p, (start, end) in zip(pieces, spans, strict=True):
        p.update(clock_ref="synthetic:clock-a", start_seconds=float(start), end_seconds=float(end))
    out = api()(time_session(), budget_minutes=2, components=pieces, layout="COMMON_CLOCK")
    assert out["ordinal"] == "LIKELY_FITS"
    assert out["lower_seconds"] == out["upper_seconds"] == 90.0
    assert out["overlap_seconds"] == 10.0


def test_mixed_clocks_or_unspecified_overlap_do_not_yield_positive_total():
    pieces = time_components()
    out = api()(time_session(), budget_minutes=75, components=pieces)
    assert out["ordinal"] == "UNKNOWN"
    pieces[0].update(clock_ref="clock-a", start_seconds=0.0, end_seconds=0.0)
    out = api()(time_session(), budget_minutes=75, components=pieces, layout="COMMON_CLOCK")
    assert out["ordinal"] == "UNKNOWN"


def test_unsupported_superset_structure_does_not_reuse_sequential_floor_or_multiplier():
    out = api()(time_session(), budget_minutes=1, components=time_components(), structure="SUPERSET")
    assert out["ordinal"] == "UNKNOWN"
    assert out["known_rest_floor_seconds"] is None


def test_past_observed_duration_is_not_a_forecast_interval():
    pieces = time_components()
    for p in pieces:
        p["basis_kind"] = "OBSERVED_HISTORY"
    out = api()(time_session(), budget_minutes=75, components=pieces, layout="DISJOINT_SEQUENTIAL")
    assert out["ordinal"] == "UNKNOWN"
    assert "HISTORY_IS_NOT_A_PREDICTIVE_BOUND" in out["uncertainty"]


def test_declared_validated_model_label_cannot_create_admitted_authority():
    pieces = time_components()
    pieces[1]["basis_kind"] = "VALIDATED_MODEL"
    pieces[1]["basis_ref"] = "client-says-approved"
    out = api()(time_session(), budget_minutes=75, components=pieces, layout="DISJOINT_SEQUENTIAL")
    assert out["ordinal"] == "UNKNOWN"
    assert out["duration"]["state"] == "UNKNOWN"


def test_explicit_product_assumptions_are_conditional_not_observed_facts():
    pieces = time_components()
    for p in pieces:
        p["basis_kind"] = "PRODUCT_ASSUMPTION"
        p["provenance"].update(origin="PRODUCT_CONTRACT", acquisition="DECLARED", measured_at=None)
    out = api()(time_session(), budget_minutes=2, components=pieces, layout="DISJOINT_SEQUENTIAL")
    assert out["ordinal"] == "LIKELY_FITS"
    assert out["basis_class"] == "PRODUCT_ASSUMPTIONS_ONLY"
    assert out["duration"]["state"] == "UNKNOWN"


def test_stale_prescription_or_other_owner_scope_cannot_supply_timing():
    s, pieces = time_session(), time_components()
    s["subject_ref"] = "subject:B"
    out = api()(s, budget_minutes=75, components=pieces, layout="DISJOINT_SEQUENTIAL")
    assert out["ordinal"] == "UNKNOWN"
    assert "SCOPE_MISMATCH" in out["uncertainty"]
    s = time_session()
    s["slots"][0]["prescription"]["work_sets"] = 3
    out = api()(s, budget_minutes=75, components=pieces, layout="DISJOINT_SEQUENTIAL")
    assert out["ordinal"] == "UNKNOWN"


def test_duplicate_or_unrelated_coverage_cannot_inflate_or_hide_time():
    run = api()
    pieces = time_components()
    pieces.append(copy.deepcopy(pieces[1]))
    with pytest.raises(ValueError):
        run(time_session(), budget_minutes=75, components=pieces, layout="DISJOINT_SEQUENTIAL")
    pieces = time_components()
    pieces[-1]["coverage_key"] = "other-exercise/operations"
    with pytest.raises(ValueError):
        run(time_session(), budget_minutes=75, components=pieces, layout="DISJOINT_SEQUENTIAL")


def test_shortened_rest_estimate_is_rejected_instead_of_fitting_budget():
    pieces = time_components()
    pieces[3].update(lower_seconds=10.0, upper_seconds=10.0)
    run = api()
    with pytest.raises(ValueError):
        run(time_session(), budget_minutes=1, components=pieces, layout="DISJOINT_SEQUENTIAL")


def test_missing_rest_and_unilateral_scope_stay_unknown():
    s = time_session()
    s["slots"][0]["prescription"]["rest_seconds"] = None
    out = api()(s, budget_minutes=75, components=[])
    assert out["ordinal"] == "UNKNOWN"
    assert "REST_UNSPECIFIED" in out["uncertainty"]
    s = time_session()
    s["slots"][0]["unilateral"] = True
    out = api()(s, budget_minutes=75, components=time_components(s), layout="DISJOINT_SEQUENTIAL")
    assert out["ordinal"] == "UNKNOWN"
    assert "UNILATERAL_TIME_SCOPE_UNRESOLVED" in out["uncertainty"]


def test_one_set_has_no_invented_intra_slot_rest():
    s = time_session()
    s["slots"][0]["prescription"] = {"work_sets": 1, "rest_seconds": None}
    out = api()(s, budget_minutes=75, components=[])
    assert out["known_rest_floor_seconds"] == 0
    assert "REST_UNSPECIFIED" not in out["uncertainty"]


@pytest.mark.parametrize("value", [True, -1.0, float("nan"), float("inf")])
def test_illegal_interval_value_is_not_a_known_duration(value):
    pieces = time_components()
    pieces[-1]["upper_seconds"] = value
    run = api()
    with pytest.raises(ValueError):
        run(time_session(), budget_minutes=75, components=pieces)


def test_future_time_source_and_reversed_bounds_are_rejected():
    run = api()
    pieces = time_components()
    pieces[-1]["provenance"]["recorded_at"] = "2026-11-06T12:01:00Z"
    with pytest.raises(ValueError):
        run(time_session(), budget_minutes=75, components=pieces)
    pieces = time_components()
    pieces[-1]["lower_seconds"] = 50.0
    with pytest.raises(ValueError):
        run(time_session(), budget_minutes=75, components=pieces)


def test_unknown_budget_never_claims_fit_and_prescription_scope_is_reproducible():
    s, pieces = time_session(), time_components()
    out = api()(s, budget_minutes=None, components=pieces, layout="DISJOINT_SEQUENTIAL")
    assert out["ordinal"] == "UNKNOWN"
    assert out["scope_fingerprint"] == digest({"session": s, "structure": "TRADITIONAL_SEQUENTIAL"})
    assert out == api()(s, budget_minutes=None, components=list(reversed(pieces)), layout="DISJOINT_SEQUENTIAL")


def test_clock_work_cannot_consume_prescribed_rest_or_leave_unaccounted_gaps():
    run = api()
    spans = [(0, 0), (0, 10), (10, 20), (20, 80), (80, 90), (30, 40)]
    for wrong in ("overlap", "gap"):
        pieces = time_components()
        for p, (start, end) in zip(pieces, spans, strict=True):
            p.update(clock_ref="one-clock", start_seconds=float(start), end_seconds=float(end))
        if wrong == "overlap":
            pieces[4].update(start_seconds=70.0, end_seconds=80.0)
        else:
            pieces[4].update(start_seconds=100.0, end_seconds=110.0)
        out = run(time_session(), budget_minutes=75, components=pieces, layout="COMMON_CLOCK")
        assert out["ordinal"] == "UNKNOWN"


def test_unknown_source_and_unknown_side_scope_do_not_look_fully_timed():
    pieces = time_components()
    pieces[-1]["provenance"].update(origin="UNKNOWN", acquisition="UNKNOWN", source_ref=None)
    out = api()(time_session(), budget_minutes=75, components=pieces, layout="DISJOINT_SEQUENTIAL")
    assert out["ordinal"] == "UNKNOWN"
    s = time_session()
    s["slots"][0].pop("unilateral")
    out = api()(s, budget_minutes=75, components=time_components(s), layout="DISJOINT_SEQUENTIAL")
    assert out["ordinal"] == "UNKNOWN"


def test_clock_length_and_coverage_kind_must_match_claimed_components():
    run = api()
    pieces = time_components()
    pieces[-1].update(clock_ref="c", start_seconds=0.0, end_seconds=20.0)
    with pytest.raises(ValueError):
        run(time_session(), budget_minutes=75, components=pieces, layout="COMMON_CLOCK")
    pieces = time_components()
    pieces[3]["kind"] = "WORK"
    with pytest.raises(ValueError):
        run(time_session(), budget_minutes=75, components=pieces, layout="DISJOINT_SEQUENTIAL")


def test_calibration_exertion_cannot_be_hidden_inside_prescribed_rest():
    pieces = time_components()
    spans = [(0, 0), (30, 40), (0, 10), (10, 70), (70, 80), (80, 90)]
    for p, (start, end) in zip(pieces, spans, strict=True):
        p.update(clock_ref="clock", start_seconds=float(start), end_seconds=float(end))
    assert api()(time_session(), budget_minutes=75, components=pieces, layout="COMMON_CLOCK")["ordinal"] == "UNKNOWN"


def test_population_prior_is_not_a_personal_forecast_bound():
    pieces = time_components()
    pieces[-1]["provenance"]["origin"] = "POPULATION_PRIOR"
    assert api()(time_session(), budget_minutes=75, components=pieces, layout="DISJOINT_SEQUENTIAL")["ordinal"] == "UNKNOWN"


def test_aggregate_overflow_is_rejected_instead_of_emitting_infinity():
    pieces = time_components()
    for p in pieces:
        p.update(lower_seconds=1e308, upper_seconds=1e308)
    run = api()
    with pytest.raises(ValueError):
        run(time_session(), budget_minutes=75, components=pieces, layout="DISJOINT_SEQUENTIAL")


def test_two_prescribed_rest_periods_cannot_overlap_to_shrink_the_total():
    s = time_session()
    s["slots"][0]["prescription"]["work_sets"] = 3
    pieces = time_components(s)
    third_work = copy.deepcopy(pieces[4])
    third_work.update(component_id="extra-work", coverage_key="press/work/3")
    second_rest = copy.deepcopy(pieces[3])
    second_rest.update(component_id="extra-rest", coverage_key="press/rest/2")
    pieces += [third_work, second_rest]
    spans = [(0, 0), (0, 10), (10, 20), (20, 80), (80, 90), (100, 110), (90, 100), (20, 80)]
    for p, (start, end) in zip(pieces, spans, strict=True):
        p.update(clock_ref="clock", start_seconds=float(start), end_seconds=float(end))
    out = api()(s, budget_minutes=3, components=pieces, layout="COMMON_CLOCK")
    assert out["ordinal"] == "UNKNOWN"


@pytest.mark.parametrize("placement", ["rest_before_work", "rest_after_work", "work_reversed", "preparation_after_work"])
def test_common_clock_preserves_between_set_rest_and_work_preparation_order(placement):
    pieces = time_components()
    spans = {
        "rest_before_work": [(0, 0), (0, 10), (70, 80), (10, 70), (80, 90), (90, 100)],
        "rest_after_work": [(0, 0), (0, 10), (10, 20), (30, 90), (20, 30), (90, 100)],
        "work_reversed": [(0, 0), (0, 10), (80, 90), (20, 80), (10, 20), (30, 40)],
        "preparation_after_work": [(0, 0), (80, 90), (0, 10), (10, 70), (70, 80), (20, 30)],
    }[placement]
    for p, (start, end) in zip(pieces, spans, strict=True):
        p.update(clock_ref="synthetic:clock", start_seconds=float(start), end_seconds=float(end))
    out = api()(time_session(), budget_minutes=2, components=pieces, layout="COMMON_CLOCK")
    assert out["ordinal"] == "UNKNOWN"
    assert out["upper_seconds"] is None
    assert "PRESCRIBED_CLOCK_ORDER_CONFLICT" in out["uncertainty"]


@pytest.mark.filterwarnings("ignore:Pydantic serializer warnings:UserWarning")
def test_nested_typed_slot_is_revalidated_at_dict_boundary():
    from tools.science_initial_policy.session_time import TimeSlot
    s = time_session()
    slot = TimeSlot.model_validate(s["slots"][0]).model_copy(update={"unilateral": "false"})
    s["slots"] = [slot]
    run = api()
    with pytest.raises(ValueError):
        run(s, budget_minutes=2, components=[])
