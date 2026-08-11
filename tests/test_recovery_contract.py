"""Sb_RECOVERY_CONTRACT_01 — the pure semantic contract.

Spec: `docs/strategy/Sx_RECOVERY_READINESS_01_SPEC.md`, with operator decisions
OQ-1..OQ-7 resolved in §12bis.

What these tests are really guarding is a set of properties that are easy to
lose later, and expensive once lost:

* a missing value never becomes a favourable one;
* fatigue never changes direction without going through a named function;
* there is exactly ONE legacy 0-100 fatigue formula in the codebase;
* `TrainingState` never grows a global score;
* the contract never claims to measure a body.

Pure tests: no `client` fixture, no DB. Module-level `app.*` imports are the
repo convention for pure tests (the conftest purges `sys.modules` per test,
which breaks function-local imports under xdist).
"""
from __future__ import annotations

import ast
import inspect
from dataclasses import FrozenInstanceError
from datetime import UTC, date, datetime
from pathlib import Path

import pytest

from app.enums import SessionConcentration, SessionGlobalState
from app.services import recovery_contract as rc
from app.services.recovery_contract import (
    CARDIO_MAX_CONFIDENCE,
    FORBIDDEN_CONTRACT_WORDING,
    LEGACY_SCALE_CONVERSIONS,
    NEUTRAL_ESTIMATE,
    NEVER_TRAINED_HOURS_SENTINEL,
    READINESS_STALE_AFTER_DAYS,
    Confidence,
    EquipmentAvailability,
    FatigueSignal,
    MacroAxisRecovery,
    ReadinessSignal,
    RecoveryBand,
    ScheduleAvailability,
    Sufficiency,
    TrainingState,
    TrainingSuitability,
    ZoneRecoveryEstimate,
    band_for_estimate,
    cardio_load_estimate,
    clamp_unit,
    confidence_from_legacy_label,
    days_since_last_or_none,
    fatigue_to_availability,
    hours_since_last_or_none,
    mean_of_present,
    never_trained_estimate,
    normalize_behavioral_readiness,
    normalize_legacy_fatigue,
    normalize_percent_scale,
    normalize_readiness_scale,
    normalize_session_feedback,
    normalize_training_suitability,
    readiness_sufficiency_for_age,
    recovery_target_hours,
    worst_zone_rollup,
)

UNUSABLE = [None, "3", "", [], {}, (), object(), True, False,
            float("nan"), float("inf"), float("-inf")]


# ---------------------------------------------------------------------------
# Readiness — 1-5, 5 = best, including the renamed field
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(("raw", "expected"), [
    (1, 0.0), (2, 0.25), (3, 0.5), (4, 0.75), (5, 1.0),
])
def test_readiness_scale_endpoints_and_midpoint(raw, expected):
    assert normalize_readiness_scale(raw) == expected


@pytest.mark.parametrize("raw", [*UNUSABLE, 0, 6, -1, 2.5, 100])
def test_readiness_scale_rejects_anything_outside_one_to_five(raw):
    assert normalize_readiness_scale(raw) is None


def test_fatigue_level_is_exposed_as_self_reported_freshness():
    """5 on that field means "Très frais" — the name must say so.

    Keeping the legacy name on an axis where higher = better is exactly the
    direction inversion the audit found (spec §1.2 · C2).
    """
    fields = set(inspect.signature(ReadinessSignal).parameters)
    assert "self_reported_freshness" in fields
    assert "fatigue_level" not in fields


def test_a_fresh_declaration_normalises_to_the_top_of_the_scale():
    signal = ReadinessSignal(self_reported_freshness=normalize_readiness_scale(5))
    assert signal.self_reported_freshness == 1.0


@pytest.mark.parametrize(("age", "expected"), [
    (0, Sufficiency.SUFFICIENT),
    (1, Sufficiency.PARTIAL),
    (2, Sufficiency.PARTIAL),
    (3, Sufficiency.STALE),
    (30, Sufficiency.STALE),
])
def test_readiness_staleness_thresholds(age, expected):
    assert readiness_sufficiency_for_age(age) is expected


@pytest.mark.parametrize("age", [*UNUSABLE, -1, 1.5])
def test_unusable_age_is_insufficient_never_sufficient(age):
    assert readiness_sufficiency_for_age(age) is Sufficiency.INSUFFICIENT


def test_stale_threshold_is_three_days():
    assert READINESS_STALE_AFTER_DAYS == 3


def test_only_a_declaration_made_today_is_decision_relevant():
    today = ReadinessSignal(age_days=0, sufficiency=Sufficiency.SUFFICIENT)
    yesterday = ReadinessSignal(age_days=1, sufficiency=Sufficiency.PARTIAL)
    old = ReadinessSignal(age_days=5, sufficiency=Sufficiency.STALE)

    assert today.is_decision_relevant is True
    assert yesterday.is_decision_relevant is False
    assert old.is_decision_relevant is False


def test_stale_readiness_can_never_be_promoted_to_sufficient():
    for age in range(READINESS_STALE_AFTER_DAYS, READINESS_STALE_AFTER_DAYS + 10):
        assert readiness_sufficiency_for_age(age) is Sufficiency.STALE


def test_missing_dimensions_stay_missing_and_never_count_as_zero():
    """A dimension not declared is excluded, not read as the worst score."""
    assert mean_of_present((None, None, None)) is None
    assert mean_of_present((1.0, None)) == 1.0
    assert mean_of_present((1.0, 0.0)) == 0.5


def test_readiness_signal_defaults_to_insufficient_not_to_a_good_state():
    empty = ReadinessSignal()
    assert empty.sufficiency is Sufficiency.INSUFFICIENT
    assert empty.overall is None
    assert all(d is None for d in empty.dimensions)
    assert empty.is_decision_relevant is False


# ---------------------------------------------------------------------------
# Fatigue — one formula, one direction, no aggregate
# ---------------------------------------------------------------------------


def test_legacy_fatigue_normalisation_delegates_to_the_existing_helper(monkeypatch):
    """Proof of reuse, behavioural rather than textual.

    If someone reimplements the 0-100 conversion here, this spy stops firing.
    """
    from app.services import recommendation_explainer as explainer

    calls: list[object] = []
    real = explainer.normalize_fatigue_score

    def spy(raw):
        calls.append(raw)
        return real(raw)

    monkeypatch.setattr(explainer, "normalize_fatigue_score", spy)

    assert normalize_legacy_fatigue(80) == 0.8
    assert calls == [80]


def test_there_is_exactly_one_legacy_fatigue_formula_in_the_codebase():
    """Regression guard against a second independent normalisation.

    `Sb_FATIGUE_SCALE_FIX_01` established the semantics — the producible floor
    of 15.0 that identifies the 0.0 failure sentinel, and the deliberately
    one-sided bound. A second formula somewhere else would be a second source of
    truth for the same conversion, and they would drift.
    """
    app_dir = Path(rc.__file__).resolve().parents[1]
    definitions: list[str] = []
    for path in sorted(app_dir.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            name = node.name.casefold()
            if "fatigue" in name and ("normal" in name or "scale" in name):
                definitions.append(f"{path.name}:{node.name}")

    # Exactly two are legitimate: the canonical implementation, and this
    # module's delegator. A third means someone wrote the formula again.
    assert sorted(definitions) == [
        "recommendation_explainer.py:normalize_fatigue_score",
        "recovery_contract.py:normalize_legacy_fatigue",
    ], f"unexpected legacy-fatigue normalisers: {definitions}"

    # And the delegator must actually delegate rather than compute.
    delegator = inspect.getsource(normalize_legacy_fatigue)
    assert "normalize_fatigue_score(value)" in delegator
    assert "/" not in delegator.split('"""')[-1], (
        "normalize_legacy_fatigue must not do arithmetic of its own"
    )


def test_fatigue_direction_is_higher_means_more_fatigued():
    assert normalize_legacy_fatigue(20) < normalize_legacy_fatigue(80)


def test_the_failure_sentinel_cannot_silently_mean_fresh():
    """`recommendation.py` writes 0.0 when behavioral raises.

    That is a computation failure, not a measurement, and the shared floor makes
    it identifiable. It must stay unusable here too.
    """
    assert normalize_legacy_fatigue(0.0) is None
    assert normalize_legacy_fatigue(0) is None
    # And it must not sneak in as an availability reading either.
    assert fatigue_to_availability(normalize_legacy_fatigue(0.0)) is None


def test_availability_complement_is_explicit_and_named():
    assert fatigue_to_availability(0.0) == 1.0
    assert fatigue_to_availability(1.0) == 0.0
    assert fatigue_to_availability(0.25) == 0.75


@pytest.mark.parametrize("raw", [*UNUSABLE, -0.1, 1.1])
def test_availability_complement_rejects_unusable_input(raw):
    assert fatigue_to_availability(raw) is None


def test_fatigue_signal_has_no_weighted_aggregate():
    """OQ-3: the three components stay separately observable.

    No `overall`, no `as_availability`, no property quietly summing them. A
    consumer that needs a scalar owns and documents its own formula.
    """
    forbidden = {"overall", "as_availability", "aggregate", "score",
                 "total", "combined", "weighted"}
    names = {n for n in dir(FatigueSignal) if not n.startswith("_")}
    assert names & forbidden == set()


def test_fatigue_components_are_addressable_and_missing_ones_excluded():
    signal = FatigueSignal(strength_component=0.6, cardio_component=None,
                           subjective_component=0.2)
    assert signal.components == {
        "strength": 0.6, "cardio": None, "subjective": 0.2}
    assert signal.observed_components == {"strength": 0.6, "subjective": 0.2}


def test_fatigue_signal_defaults_to_insufficient_and_no_confidence():
    empty = FatigueSignal()
    assert empty.sufficiency is Sufficiency.INSUFFICIENT
    assert empty.confidence is Confidence.NONE
    assert empty.observed_components == {}


def test_session_feedback_reuses_the_production_producer():
    """good + high concentration is the producible floor: 15/100."""
    value = normalize_session_feedback(
        SessionGlobalState.GOOD, SessionConcentration.HIGH)
    assert value == 0.15
    worst = normalize_session_feedback(
        SessionGlobalState.FATIGUED, SessionConcentration.LOW)
    assert worst == 0.75
    assert value < worst  # higher = more fatigued


def test_session_feedback_with_nothing_declared_is_none_not_neutral():
    """`compute_session_fatigue` would return its 50/40 defaults.

    "The user told us nothing" is not a neutral reading and must not be dressed
    up as one.
    """
    assert normalize_session_feedback(None, None) is None


# ---------------------------------------------------------------------------
# The other legacy conversions
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(("raw", "expected"), [(0, 0.0), (50, 0.5), (100, 1.0)])
def test_percent_scale(raw, expected):
    assert normalize_percent_scale(raw) == expected


@pytest.mark.parametrize("raw", [*UNUSABLE, -1, 101])
def test_percent_scale_rejects_out_of_range(raw):
    assert normalize_percent_scale(raw) is None


def test_behavioral_readiness_is_named_but_not_consumed_by_training_state():
    """OQ-1: the conversion exists so the table is complete; nothing reads it."""
    assert normalize_behavioral_readiness(80) == 0.8
    state_fields = set(inspect.signature(TrainingState).parameters)
    for forbidden in ("behavioral_readiness", "readiness_score"):
        assert forbidden not in state_fields


def test_never_trained_hours_sentinel_becomes_none():
    assert hours_since_last_or_none(NEVER_TRAINED_HOURS_SENTINEL) is None
    assert hours_since_last_or_none(NEVER_TRAINED_HOURS_SENTINEL + 1) is None
    assert hours_since_last_or_none(48) == 48.0


@pytest.mark.parametrize("raw", [*UNUSABLE, -1])
def test_hours_since_last_rejects_unusable(raw):
    assert hours_since_last_or_none(raw) is None


@pytest.mark.parametrize(("raw", "expected"), [(0, 0), (7, 7)])
def test_days_since_last_passes_through(raw, expected):
    assert days_since_last_or_none(raw) == expected


@pytest.mark.parametrize("raw", [*UNUSABLE, -1, 1.5])
def test_days_since_last_rejects_unusable(raw):
    assert days_since_last_or_none(raw) is None


def test_recovery_target_reads_the_legacy_constant_without_copying_it():
    """OQ-2: read through an adapter, never duplicated, no BodyZone column."""
    from app.services.recommendation import RECOVERY_HOURS_TARGET

    for zone, hours in RECOVERY_HOURS_TARGET.items():
        assert recovery_target_hours(zone) == float(hours)
    assert recovery_target_hours("not_a_zone") is None


def test_no_bodyzone_recovery_hours_column_was_added():
    """OQ-2 resolved: recovery duration is not an anatomical property."""
    from app.models.body_zone import BodyZone

    assert not hasattr(BodyZone, "recovery_hours")


def test_training_suitability_corrects_the_never_trained_fail_open():
    """The legacy formula gives a never-trained zone 1.0. This gives None."""
    assert normalize_training_suitability(NEVER_TRAINED_HOURS_SENTINEL, "quads") is None
    assert normalize_training_suitability(None, "quads") is None
    # A real gap still normalises against the zone's own target.
    assert normalize_training_suitability(36, "quads") == 0.5   # target 72h
    assert normalize_training_suitability(144, "quads") == 1.0  # clamped


def test_training_suitability_is_unknown_for_an_unknown_zone():
    assert normalize_training_suitability(24, "not_a_zone") is None


@pytest.mark.parametrize(("label", "expected"), [
    ("élevée", Confidence.HIGH),
    ("Moyenne", Confidence.MEDIUM),
    ("faible", Confidence.LOW),
    ("insuffisante", Confidence.NONE),
])
def test_legacy_confidence_labels(label, expected):
    assert confidence_from_legacy_label(label) is expected


@pytest.mark.parametrize("label", [None, "", "unknown", 3, []])
def test_unknown_confidence_label_is_none_not_a_default(label):
    assert confidence_from_legacy_label(label) is None


def test_cardio_estimate_is_declared_but_computes_nothing_yet():
    """OQ-4: no coefficient is invented before the stored vocabulary is audited."""
    value, confidence, basis = cardio_load_estimate(
        machine_type="bike", duration_min=45, bpm_avg=130)
    assert value is None
    assert confidence is Confidence.NONE
    assert any("Sb_CARDIO_FATIGUE_ADAPTER_01" in b for b in basis)


def test_cardio_confidence_can_never_exceed_medium():
    """No combination of today's fields observes internal load."""
    assert CARDIO_MAX_CONFIDENCE is Confidence.MEDIUM
    for kwargs in ({}, {"machine_type": "bike"}, {"duration_min": 60},
                   {"machine_type": "rower", "duration_min": 60, "bpm_avg": 150}):
        _, confidence, _ = cardio_load_estimate(**kwargs)
        assert confidence is not Confidence.HIGH


def test_cardio_basis_records_which_inputs_were_present():
    _, _, basis = cardio_load_estimate(duration_min=30)
    assert any("cardio_duration_min" in b for b in basis)
    _, _, empty_basis = cardio_load_estimate()
    assert any("no usable cardio input" in b for b in empty_basis)


# ---------------------------------------------------------------------------
# The §3.1 table cannot drift from the code
# ---------------------------------------------------------------------------


def test_all_thirteen_spec_rows_are_registered():
    assert len(LEGACY_SCALE_CONVERSIONS) == 13


def test_every_row_either_converts_or_says_why_it_does_not():
    for row in LEGACY_SCALE_CONVERSIONS:
        assert row.source and row.legacy_scale and row.target and row.note
        if row.conversion is None:
            assert "not converted" in row.note, row.source
        else:
            assert callable(row.conversion), row.source


def test_every_registered_conversion_is_a_public_module_function():
    exported = {name for name in dir(rc) if not name.startswith("_")}
    for row in LEGACY_SCALE_CONVERSIONS:
        if row.conversion is not None:
            assert row.conversion.__name__ in exported, row.source


def test_the_row_covering_scoring_weights_is_deliberately_unconverted():
    row = next(r for r in LEGACY_SCALE_CONVERSIONS if "ZONE_FRESHNESS" in r.source)
    assert row.conversion is None


def test_no_conversion_maps_a_missing_input_to_a_favourable_value():
    """The single most important property in this module.

    Every conversion that can return a normalised number must return None for
    an unusable input — never 0.0, never 1.0, never the neutral.
    """
    unit_returning = (
        normalize_readiness_scale, normalize_percent_scale,
        normalize_behavioral_readiness, normalize_legacy_fatigue,
        fatigue_to_availability,
    )
    for func in unit_returning:
        for raw in UNUSABLE:
            assert func(raw) is None, f"{func.__name__}({raw!r})"


# ---------------------------------------------------------------------------
# Availability: four words, four types
# ---------------------------------------------------------------------------


def test_the_three_availability_concepts_are_distinct_types():
    """C3: suitability, equipment and schedule must not share a field."""
    assert TrainingSuitability is not EquipmentAvailability
    assert EquipmentAvailability is not ScheduleAvailability
    assert TrainingSuitability is not ScheduleAvailability

    suitability_fields = set(inspect.signature(TrainingSuitability).parameters)
    equipment_fields = set(inspect.signature(EquipmentAvailability).parameters)
    schedule_fields = set(inspect.signature(ScheduleAvailability).parameters)

    assert "equipment_families" not in suitability_fields
    assert "minutes_available" not in suitability_fields
    assert "suitability" not in equipment_fields
    assert "suitability" not in schedule_fields


def test_no_contract_type_uses_the_bare_word_available_as_a_field():
    """`{"available": bool}` is the UI-renderability sense (C3, 4th meaning).

    It stays in the composers and must never leak into this vocabulary.
    """
    for cls in (TrainingSuitability, EquipmentAvailability, ScheduleAvailability,
                ReadinessSignal, FatigueSignal, ZoneRecoveryEstimate, TrainingState):
        assert "available" not in set(inspect.signature(cls).parameters)


def test_equipment_availability_none_means_unconstrained():
    assert EquipmentAvailability().is_constrained is False
    assert EquipmentAvailability(equipment_families=("machine",)).is_constrained is True


def test_schedule_availability_is_declared_but_empty_in_v1():
    assert ScheduleAvailability().minutes_available is None


# ---------------------------------------------------------------------------
# ZoneRecoveryEstimate
# ---------------------------------------------------------------------------


def test_a_never_trained_zone_cannot_resolve_to_perfect_recovery():
    estimate = never_trained_estimate("quads")
    assert estimate.estimate is None
    assert estimate.estimate != 1.0
    assert estimate.band is RecoveryBand.UNKNOWN
    assert estimate.confidence is Confidence.NONE
    assert estimate.hours_since_last_load is None
    assert estimate.staleness is Sufficiency.INSUFFICIENT
    assert estimate.is_informative is False


def test_an_estimate_needs_a_value_a_confidence_and_a_basis():
    assert ZoneRecoveryEstimate("pecs").is_informative is False
    assert ZoneRecoveryEstimate("pecs", estimate=0.9).is_informative is False
    assert ZoneRecoveryEstimate(
        "pecs", estimate=0.9, confidence=Confidence.MEDIUM).is_informative is False
    assert ZoneRecoveryEstimate(
        "pecs", estimate=0.9, confidence=Confidence.MEDIUM,
        basis=("48h since last load",)).is_informative is True


def test_zone_estimate_defaults_are_unknown_not_optimistic():
    empty = ZoneRecoveryEstimate("lats")
    assert empty.estimate is None
    assert empty.band is RecoveryBand.UNKNOWN
    assert empty.confidence is Confidence.NONE
    assert empty.staleness is Sufficiency.INSUFFICIENT


@pytest.mark.parametrize(("value", "expected"), [
    (1.0, RecoveryBand.LIKELY_AVAILABLE),
    (0.8, RecoveryBand.LIKELY_AVAILABLE),
    (0.5, RecoveryBand.PARTIALLY_RECOVERED),
    (0.4, RecoveryBand.PARTIALLY_RECOVERED),
    (0.0, RecoveryBand.LIKELY_FATIGUED),
])
def test_bands(value, expected):
    assert band_for_estimate(value) is expected


@pytest.mark.parametrize("raw", [*UNUSABLE, -0.1, 1.1])
def test_unusable_estimate_bands_as_unknown_not_available(raw):
    assert band_for_estimate(raw) is RecoveryBand.UNKNOWN


# ---------------------------------------------------------------------------
# Macro roll-up (OQ-5): worst zone, named
# ---------------------------------------------------------------------------


def test_macro_rollup_takes_the_worst_zone_and_names_it():
    rollup = worst_zone_rollup("lower", (
        ZoneRecoveryEstimate("quads", estimate=0.9, confidence=Confidence.HIGH,
                             basis=("x",)),
        ZoneRecoveryEstimate("posterior", estimate=0.3, confidence=Confidence.HIGH,
                             basis=("x",)),
        ZoneRecoveryEstimate("calves", estimate=0.7, confidence=Confidence.HIGH,
                             basis=("x",)),
    ))
    assert rollup.estimate == 0.3
    assert rollup.limiting_zone_code == "posterior"
    assert rollup.band is RecoveryBand.LIKELY_FATIGUED
    assert any("posterior" in b for b in rollup.basis)


def test_macro_rollup_downgrades_confidence_when_a_zone_is_unknown():
    """A partially known axis is not a known axis."""
    rollup = worst_zone_rollup("arms", (
        ZoneRecoveryEstimate("biceps", estimate=0.6, confidence=Confidence.HIGH,
                             basis=("x",)),
        ZoneRecoveryEstimate("triceps"),
    ))
    assert rollup.estimate == 0.6
    assert rollup.confidence is Confidence.MEDIUM
    assert any("triceps" in b for b in rollup.basis)


def test_macro_rollup_with_nothing_known_is_unknown():
    rollup = worst_zone_rollup("pecs", (ZoneRecoveryEstimate("pecs"),))
    assert rollup.estimate is None
    assert rollup.band is RecoveryBand.UNKNOWN
    assert rollup.confidence is Confidence.NONE


def test_macro_rollup_is_deterministic_on_a_tie():
    first = worst_zone_rollup("arms", (
        ZoneRecoveryEstimate("triceps", estimate=0.4, basis=("x",)),
        ZoneRecoveryEstimate("biceps", estimate=0.4, basis=("x",)),
    ))
    second = worst_zone_rollup("arms", (
        ZoneRecoveryEstimate("biceps", estimate=0.4, basis=("x",)),
        ZoneRecoveryEstimate("triceps", estimate=0.4, basis=("x",)),
    ))
    assert first.limiting_zone_code == second.limiting_zone_code == "biceps"


def test_macro_rollup_is_presentation_only_and_says_so():
    assert "presentation" in (MacroAxisRecovery.__doc__ or "").lower()


# ---------------------------------------------------------------------------
# TrainingState: primitives, and no score
# ---------------------------------------------------------------------------


def test_training_state_exposes_no_global_score():
    """The constraint, not an omission — see the class docstring."""
    forbidden = {
        "overall_score", "readiness_score", "recovery_percentage", "score",
        "global_score", "composite", "composite_score", "overall",
        "total_score", "index",
    }
    names = {n for n in dir(TrainingState) if not n.startswith("_")}
    assert names & forbidden == set()


def test_training_state_has_no_hidden_numeric_aggregate_property():
    """A property returning a bare float would be a score by another name."""
    state = TrainingState(
        readiness=ReadinessSignal(overall=0.8),
        fatigue=FatigueSignal(strength_component=0.4),
        zone_recovery=(ZoneRecoveryEstimate("pecs", estimate=0.5),),
    )
    for name, attr in inspect.getmembers(type(state)):
        if name.startswith("_") or not isinstance(attr, property):
            continue
        assert not isinstance(getattr(state, name), float), name


def test_training_state_preserves_the_primitives():
    readiness = ReadinessSignal(declared_on=date(2026, 8, 11), age_days=0,
                                sufficiency=Sufficiency.SUFFICIENT)
    fatigue = FatigueSignal(strength_component=0.5, cardio_component=0.1)
    zones = (ZoneRecoveryEstimate("pecs", estimate=0.7),
             ZoneRecoveryEstimate("quads", estimate=0.2))
    state = TrainingState(
        computed_at=datetime(2026, 8, 11, tzinfo=UTC),
        readiness=readiness, fatigue=fatigue, zone_recovery=zones,
        equipment=EquipmentAvailability(equipment_families=("machine",)),
    )

    assert state.readiness is readiness
    assert state.fatigue is fatigue
    assert state.zone("quads").estimate == 0.2
    assert state.zone("absent") is None
    assert state.equipment.is_constrained is True


def test_training_state_defaults_are_insufficient_and_unconfident():
    state = TrainingState()
    assert state.sufficiency is Sufficiency.INSUFFICIENT
    assert state.confidence is Confidence.NONE
    assert state.zone_recovery == ()
    assert state.schedule is None  # declared, not implemented in V1


def test_the_whole_contract_is_immutable():
    """Frozen dataclasses: a consumer cannot mutate a state it was handed."""
    for instance in (ReadinessSignal(), FatigueSignal(), ZoneRecoveryEstimate("pecs"),
                     TrainingSuitability("pecs"), EquipmentAvailability(),
                     ScheduleAvailability(), MacroAxisRecovery("lower"),
                     TrainingState()):
        with pytest.raises(FrozenInstanceError):
            instance.basis = ("mutated",)


def test_neutral_is_named_rather_than_a_bare_literal():
    """Spec §4.3 condition 1."""
    assert NEUTRAL_ESTIMATE == 0.5


def test_clamp_unit_bounds():
    assert clamp_unit(-5) == 0.0
    assert clamp_unit(5) == 1.0
    assert clamp_unit(0.3) == 0.3


# ---------------------------------------------------------------------------
# Purity and boundaries
# ---------------------------------------------------------------------------


def test_the_contract_module_touches_no_database():
    """No ORM, no session, no query — the module is a vocabulary, not a reader."""
    source = Path(rc.__file__).read_text(encoding="utf-8")
    for forbidden in ("sqlalchemy", "SessionLocal", "db.query", "select(",
                      "Depends", "APIRouter", "commit()"):
        assert forbidden not in source, forbidden


def test_the_contract_module_imports_no_orm_at_module_level():
    """Deferred imports keep it import-light; nothing heavy at import time."""
    source = Path(rc.__file__).read_text(encoding="utf-8")
    header = source.split("RECOVERY_CONTRACT_VERSION", 1)[0]
    assert "from app.services.recommendation" not in header
    assert "from app.services.behavioral" not in header


def test_recommendation_and_behavioral_are_not_modified():
    """Hard constraint: this sprint reads them, never edits them."""
    import app.services.behavioral as behavioral
    import app.services.recommendation as recommendation

    assert "recovery_contract" not in Path(
        recommendation.__file__).read_text(encoding="utf-8")
    assert "recovery_contract" not in Path(
        behavioral.__file__).read_text(encoding="utf-8")


def test_the_contract_introduces_no_new_zone_vocabulary():
    """Spec §6: zone codes come from the canonical taxonomy, full stop."""
    from app.services.muscle_mapping import ZONE_LABELS

    source = Path(rc.__file__).read_text(encoding="utf-8")
    assert "_EXERCISE_PATTERNS" not in source
    assert "ZONE_LABELS = " not in source
    # The zones it names in examples must be real ones.
    for zone in ("quads", "posterior", "calves", "pecs"):
        assert zone in ZONE_LABELS


# ---------------------------------------------------------------------------
# Wording guardrails (spec §8) — this module's public surface only
# ---------------------------------------------------------------------------


def test_the_public_contract_never_claims_to_measure_a_body():
    """Scoped to the contract's own names and docstrings, not a prose linter."""
    surface: list[str] = [rc.__doc__ or ""]
    for name in dir(rc):
        if name.startswith("_") or name == "FORBIDDEN_CONTRACT_WORDING":
            continue  # the deny-list is allowed to name the terms it denies
        obj = getattr(rc, name)
        surface.append(name)
        if inspect.isclass(obj) or inspect.isfunction(obj):
            surface.append(inspect.getdoc(obj) or "")
            for member_name, member in inspect.getmembers(obj):
                if member_name.startswith("_"):
                    continue
                surface.append(member_name)
                surface.append(inspect.getdoc(member) or "")

    haystack = " ".join(surface).casefold()
    for forbidden in FORBIDDEN_CONTRACT_WORDING:
        assert forbidden.casefold() not in haystack, (
            f"forbidden contract wording on the public surface: {forbidden!r}"
        )


def test_the_zone_estimate_is_named_and_documented_as_an_estimate():
    doc = (inspect.getdoc(ZoneRecoveryEstimate) or "").casefold()
    assert "estimate" in doc
    assert "not a measurement" in doc
    assert "percentage of" in doc  # "...not a percentage of physiological recovery"


def test_forbidden_wording_list_is_the_one_the_spec_pins():
    assert set(FORBIDDEN_CONTRACT_WORDING) == {
        "physiologically recovered", "measured muscle recovery",
        "measured activation", "diagnosis", "injury prediction",
        "therapeutic prescription",
    }
