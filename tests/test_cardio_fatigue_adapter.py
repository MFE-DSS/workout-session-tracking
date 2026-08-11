"""Sb_CARDIO_FATIGUE_ADAPTER_01 — bounded deterministic cardio exposure.

Spec: `Sx_RECOVERY_READINESS_01_SPEC` §5 and §11, operator decision OQ-4.

The properties worth defending here are all of the form "the adapter does not
claim more than the data supports":

* **calories never influence the result** — they are not even a parameter;
* **BPM never scales the magnitude** — with no individual heart-rate anchor an
  absolute BPM is not comparable between people, so it may only raise evidence;
* **duration is the only quantitative input**, through one named bounded rule;
* **a vague modality gets no zone distribution** rather than a fabricated one;
* **`Confidence.HIGH` is unreachable**, whatever the inputs.

Pure tests: no `client` fixture, no DB. Module-level `app.*` imports per the
repo convention for pure tests.
"""
from __future__ import annotations

import ast
import inspect
import textwrap
from pathlib import Path

import pytest

from app.services import recovery_contract as rc
from app.services.muscle_mapping import ZONE_LABELS
from app.services.recovery_contract import (
    CARDIO_DURATION_REFERENCE_MINUTES,
    CARDIO_PRIMARY_ZONE_WEIGHT,
    CARDIO_SECONDARY_ZONE_WEIGHT,
    CARDIO_SPECIFIC_MODALITIES,
    CARDIO_UI_VOCABULARY,
    CardioModality,
    Confidence,
    cardio_load_estimate,
    cardio_zone_exposure,
    normalize_cardio_modality,
)

UNUSABLE_NUMBERS = [None, "30", "", [], {}, object(), True, False,
                    float("nan"), float("inf"), float("-inf")]


# ---------------------------------------------------------------------------
# Vocabulary
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("raw", ["velo", "marche", "rameur", "elliptique", "autre"])
def test_every_ui_select_value_is_recognised(raw):
    """The five values `session_detail.html` can currently produce."""
    modality, off_list = normalize_cardio_modality(raw)
    assert modality is CardioModality(raw)
    assert off_list is None


def test_ui_vocabulary_matches_the_template_exactly():
    """If someone adds an option to the select, this fails until the adapter knows."""
    template = Path(rc.__file__).resolve().parents[1] / "templates" / "session_detail.html"
    html = template.read_text(encoding="utf-8")
    select = html.split('<select name="cardio_machine_type">', 1)[1].split("</select>", 1)[0]
    options = {
        line.split('value="', 1)[1].split('"', 1)[0]
        for line in select.splitlines() if 'value="' in line
    }
    assert options - {""} == set(CARDIO_UI_VOCABULARY)


@pytest.mark.parametrize("raw", [None, "", "   ", 3, [], object()])
def test_no_modality_is_fabricated_for_an_empty_field(raw):
    modality, off_list = normalize_cardio_modality(raw)
    assert modality is None
    assert off_list is None


@pytest.mark.parametrize(("raw", "expected"), [
    ("VELO", CardioModality.VELO),
    ("  velo  ", CardioModality.VELO),
    ("Rameur", CardioModality.RAMEUR),
    ("ELLIPTIQUE", CardioModality.ELLIPTIQUE),
])
def test_normalisation_is_trim_and_case_only(raw, expected):
    assert normalize_cardio_modality(raw)[0] is expected


def test_stairmaster_the_one_off_list_value_evidenced_in_the_repo():
    """`tests/test_session_done.py` defaults machine_type to "stairmaster".

    A real off-list value already present in this repository — which is why the
    adapter cannot assume the UI's closed select bounds what is stored.
    """
    modality, off_list = normalize_cardio_modality("stairmaster")
    assert modality is CardioModality.UNKNOWN
    assert off_list == "stairmaster"


def test_off_list_value_is_echoed_back_not_silently_dropped():
    _, off_list = normalize_cardio_modality("  Tapis De Course  ")
    assert off_list == "Tapis De Course"


def test_no_alias_table_was_invented():
    """No alias is evidenced anywhere in the repo, so none is encoded.

    Guessing spellings nobody has ever stored is exactly the fabrication §5
    forbids. `velo` is stored unaccented; `vélo` is only ever a display label.
    """
    for never_observed in ("vélo", "bike", "cycling", "walk", "rower", "treadmill"):
        modality, off_list = normalize_cardio_modality(never_observed)
        assert modality is CardioModality.UNKNOWN, never_observed
        assert off_list is not None


# ---------------------------------------------------------------------------
# Duration — the only quantitative input
# ---------------------------------------------------------------------------


def test_the_duration_reference_comes_from_the_product_catalog():
    """Both cardio templates prescribe "20-30 min LISS"; 30 is the top of it."""
    import json

    data = Path(rc.__file__).resolve().parents[2] / "data" / "reference_split.json"
    notes = [
        t["cardio_note"] for t in json.loads(data.read_text(encoding="utf-8"))["templates"]
        if t.get("cardio_note")
    ]
    assert notes, "the catalog no longer prescribes any cardio duration"
    assert all("20-30 min" in n for n in notes)
    assert CARDIO_DURATION_REFERENCE_MINUTES == 30.0


@pytest.mark.parametrize("raw", [*UNUSABLE_NUMBERS, 0, 0.0, -1, -30])
def test_unusable_duration_yields_no_estimate(raw):
    value, confidence, basis = cardio_load_estimate(machine_type="velo", duration_min=raw)
    assert value is None
    assert confidence is Confidence.NONE
    assert any("no usable cardio_duration_min" in b for b in basis)


def test_value_is_monotonic_in_duration():
    values = [
        cardio_load_estimate(machine_type="velo", duration_min=d)[0]
        for d in (1, 5, 10, 20, 29)
    ]
    assert values == sorted(values)
    assert len(set(values)) == len(values)


def test_the_reference_duration_is_exactly_full_exposure():
    value, _, _ = cardio_load_estimate(
        machine_type="velo", duration_min=CARDIO_DURATION_REFERENCE_MINUTES)
    assert value == 1.0


def test_longer_than_the_reference_saturates_rather_than_exceeding_one():
    for minutes in (31, 60, 120, 600):
        value, _, _ = cardio_load_estimate(machine_type="velo", duration_min=minutes)
        assert value == 1.0, minutes


def test_the_rule_is_exactly_duration_over_reference():
    """No hidden non-linearity, no pseudo-scientific coefficient."""
    for minutes in (3, 7.5, 12, 21, 29):
        value, _, _ = cardio_load_estimate(machine_type="velo", duration_min=minutes)
        assert value == pytest.approx(minutes / CARDIO_DURATION_REFERENCE_MINUTES)


def test_output_stays_inside_the_unit_interval():
    for minutes in (0.1, 1, 15, 30, 1000):
        value, _, _ = cardio_load_estimate(machine_type="velo", duration_min=minutes)
        assert 0.0 <= value <= 1.0


def test_booleans_are_not_accepted_as_a_duration():
    """`True` is an `int` and would otherwise read as one minute."""
    assert cardio_load_estimate(machine_type="velo", duration_min=True)[0] is None


# ---------------------------------------------------------------------------
# BPM — evidence, never magnitude
# ---------------------------------------------------------------------------


def test_bpm_alone_cannot_produce_a_magnitude():
    value, confidence, _ = cardio_load_estimate(machine_type="velo", bpm_avg=150)
    assert value is None
    assert confidence is Confidence.NONE


def test_changing_bpm_alone_never_changes_the_magnitude():
    """The core guarantee: no individual anchor, so no intensity scaling."""
    baseline, _, _ = cardio_load_estimate(machine_type="velo", duration_min=20)
    for bpm in (60, 100, 125, 150, 190, 220):
        value, _, _ = cardio_load_estimate(
            machine_type="velo", duration_min=20, bpm_avg=bpm)
        assert value == baseline, bpm


def test_absent_bpm_still_allows_a_low_confidence_estimate():
    value, confidence, _ = cardio_load_estimate(machine_type="velo", duration_min=20)
    assert value == pytest.approx(20 / CARDIO_DURATION_REFERENCE_MINUTES)
    assert confidence is Confidence.LOW


def test_valid_bpm_improves_confidence_on_a_specific_modality():
    _, without, _ = cardio_load_estimate(machine_type="rameur", duration_min=20)
    _, with_bpm, _ = cardio_load_estimate(
        machine_type="rameur", duration_min=20, bpm_avg=140)
    assert without is Confidence.LOW
    assert with_bpm is Confidence.MEDIUM


def test_the_basis_says_bpm_does_not_scale_the_value():
    _, _, basis = cardio_load_estimate(
        machine_type="velo", duration_min=20, bpm_avg=130)
    assert any("never the magnitude" in b for b in basis)


def test_the_catalog_prescribes_one_bpm_band_to_everyone():
    """Why absolute BPM cannot be an individual intensity signal, from the data.

    Both LISS templates target the same "120-130 bpm" for every user, so a
    reading inside that band distinguishes nobody.
    """
    import json

    data = Path(rc.__file__).resolve().parents[2] / "data" / "reference_split.json"
    notes = [
        t["cardio_note"] for t in json.loads(data.read_text(encoding="utf-8"))["templates"]
        if t.get("cardio_note")
    ]
    assert all("120-130 bpm" in n.replace("à", "a") for n in notes)


# ---------------------------------------------------------------------------
# Calories — never read
# ---------------------------------------------------------------------------


def test_calories_are_not_even_a_parameter():
    params = set(inspect.signature(cardio_load_estimate).parameters)
    assert params == {"machine_type", "duration_min", "bpm_avg"}
    assert not any("calor" in p for p in params)


def _executable_body(func) -> str:
    """The function's code with its docstring removed.

    The docstring legitimately *names* calories and temporal decay in order to
    explain why neither is used; scanning it would flag the explanation itself.
    What must stay clean is the code.
    """
    tree = ast.parse(textwrap.dedent(inspect.getsource(func)))
    node = tree.body[0]
    body = node.body[1:] if ast.get_docstring(node) else node.body
    return "\n".join(ast.unparse(stmt) for stmt in body).casefold()


def test_no_calorie_derived_formula_exists_in_the_adapter():
    """Code-level: the adapter must not reach for calories by another name."""
    body = _executable_body(cardio_load_estimate)
    for forbidden in ("calor", "kcal"):
        assert forbidden not in body, forbidden


def test_calories_cannot_reach_the_adapter_at_all():
    with pytest.raises(TypeError):
        cardio_load_estimate(
            machine_type="velo", duration_min=20, cardio_machine_calories=400)


def test_two_sessions_differing_only_in_calories_are_indistinguishable():
    """Modelled as the caller would: calories exist on the row and are ignored."""
    rows = [
        {"cardio_machine_type": "velo", "cardio_duration_min": 20,
         "cardio_bpm_avg": 130, "cardio_machine_calories": cal}
        for cal in (0, 150, 400, 9999, None)
    ]
    results = {
        cardio_load_estimate(
            machine_type=r["cardio_machine_type"],
            duration_min=r["cardio_duration_min"],
            bpm_avg=r["cardio_bpm_avg"],
        )
        for r in rows
    }
    assert len(results) == 1


# ---------------------------------------------------------------------------
# Confidence matrix
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(("kwargs", "expected"), [
    ({"machine_type": "velo", "duration_min": 20, "bpm_avg": 130}, Confidence.MEDIUM),
    ({"machine_type": "rameur", "duration_min": 20, "bpm_avg": 130}, Confidence.MEDIUM),
    ({"machine_type": "velo", "duration_min": 20}, Confidence.LOW),
    ({"duration_min": 20}, Confidence.LOW),
    ({"duration_min": 20, "bpm_avg": 130}, Confidence.LOW),
    ({"machine_type": "autre", "duration_min": 20, "bpm_avg": 130}, Confidence.LOW),
    ({"machine_type": "stairmaster", "duration_min": 20, "bpm_avg": 130}, Confidence.LOW),
    ({"machine_type": "velo"}, Confidence.NONE),
    ({}, Confidence.NONE),
])
def test_confidence_matrix(kwargs, expected):
    assert cardio_load_estimate(**kwargs)[1] is expected


def test_high_confidence_is_unreachable():
    """No combination of today's fields observes internal load."""
    for machine in (None, "", "velo", "marche", "rameur", "elliptique", "autre", "zzz"):
        for duration in (None, 0, 1, 30, 600):
            for bpm in (None, 0, 60, 130, 220):
                confidence = cardio_load_estimate(
                    machine_type=machine, duration_min=duration, bpm_avg=bpm)[1]
                assert confidence is not Confidence.HIGH


def test_the_declared_ceiling_is_the_one_actually_reached():
    """`CARDIO_MAX_CONFIDENCE` must describe reality, not aspiration.

    Two failure modes this closes: a ceiling declared above anything the code
    can produce (a promise of precision never delivered), and a ceiling declared
    below what the code actually returns (a documented bound that does not hold).
    """
    reached = {
        cardio_load_estimate(machine_type=m, duration_min=d, bpm_avg=b)[1]
        for m in (None, "", "velo", "marche", "rameur", "elliptique", "autre", "zzz")
        for d in (None, 0, 1, 30, 600)
        for b in (None, 0, 60, 130, 220)
    }
    ladder = [Confidence.NONE, Confidence.LOW, Confidence.MEDIUM, Confidence.HIGH]
    best = max(reached, key=ladder.index)
    assert best is rc.CARDIO_MAX_CONFIDENCE
    assert reached == {Confidence.NONE, Confidence.LOW, Confidence.MEDIUM}


def test_an_unknown_modality_cannot_be_lifted_to_medium_by_bpm():
    """BPM is evidence of a fuller recording, not a calibration."""
    for machine in ("stairmaster", "autre", "zzz"):
        confidence = cardio_load_estimate(
            machine_type=machine, duration_min=20, bpm_avg=130)[1]
        assert confidence is Confidence.LOW, machine


def test_only_specific_modalities_can_reach_medium():
    assert CARDIO_SPECIFIC_MODALITIES == {
        CardioModality.VELO, CardioModality.MARCHE,
        CardioModality.RAMEUR, CardioModality.ELLIPTIQUE,
    }
    assert CardioModality.AUTRE not in CARDIO_SPECIFIC_MODALITIES
    assert CardioModality.UNKNOWN not in CARDIO_SPECIFIC_MODALITIES


# ---------------------------------------------------------------------------
# Zone distribution
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("modality", list(CardioModality))
def test_every_distribution_uses_only_canonical_body_zone_codes(modality):
    exposure = cardio_zone_exposure(modality)
    for zone in (*exposure.primary_zones, *exposure.secondary_zones):
        assert zone in ZONE_LABELS, zone


def test_no_new_muscle_taxonomy_is_introduced():
    source = Path(rc.__file__).read_text(encoding="utf-8")
    assert "ZONE_LABELS = " not in source
    assert "_EXERCISE_PATTERNS" not in source


def test_lower_body_modalities_are_lower_body_dominant():
    for modality in (CardioModality.VELO, CardioModality.MARCHE,
                     CardioModality.ELLIPTIQUE):
        exposure = cardio_zone_exposure(modality)
        assert exposure.primary_zones == ("quads", "posterior"), modality
        assert exposure.secondary_zones == ("calves",), modality


def test_rowing_is_the_one_mixed_modality():
    exposure = cardio_zone_exposure(CardioModality.RAMEUR)
    assert set(exposure.primary_zones) == {"quads", "posterior", "lats", "upper_back"}
    assert exposure.secondary_zones == ("biceps",)


def test_elliptical_claims_no_upper_body_because_handle_use_is_not_captured():
    exposure = cardio_zone_exposure(CardioModality.ELLIPTIQUE)
    upper = {"lats", "upper_back", "pecs", "biceps", "triceps", "delt_lat", "delt_post"}
    assert not (set(exposure.primary_zones) | set(exposure.secondary_zones)) & upper
    assert any("handle use is not captured" in b for b in exposure.basis)


@pytest.mark.parametrize("modality", [CardioModality.AUTRE, CardioModality.UNKNOWN, None])
def test_a_vague_modality_fabricates_no_zone(modality):
    exposure = cardio_zone_exposure(modality)
    assert exposure.primary_zones == ()
    assert exposure.secondary_zones == ()
    assert exposure.is_distributed is False
    assert exposure.basis  # it says why, rather than saying nothing


def test_distribution_is_deterministic():
    first = cardio_zone_exposure(CardioModality.RAMEUR)
    second = cardio_zone_exposure(CardioModality.RAMEUR)
    assert first == second
    assert first.weights() == second.weights()


def test_primary_outranks_secondary_in_the_relative_weights():
    weights = cardio_zone_exposure(CardioModality.VELO).weights()
    assert weights["quads"] == CARDIO_PRIMARY_ZONE_WEIGHT
    assert weights["calves"] == CARDIO_SECONDARY_ZONE_WEIGHT
    assert weights["calves"] < weights["quads"]


def test_undistributed_modalities_have_no_weights():
    assert cardio_zone_exposure(CardioModality.AUTRE).weights() == {}


def test_no_zone_is_both_primary_and_secondary():
    for modality in CARDIO_SPECIFIC_MODALITIES:
        exposure = cardio_zone_exposure(modality)
        assert not set(exposure.primary_zones) & set(exposure.secondary_zones), modality


def test_the_zone_table_is_documented_as_a_heuristic():
    doc = (inspect.getdoc(rc.CardioZoneExposure) or "").casefold()
    assert "heuristic" in doc


# ---------------------------------------------------------------------------
# Scope: this slice implements no later slice
# ---------------------------------------------------------------------------


def test_no_temporal_decay_is_implemented_here():
    """Recovery over time belongs to Sb_ZONE_RECOVERY_ESTIMATE_01."""
    body = _executable_body(cardio_load_estimate)
    for forbidden in ("decay", "half_life", "elapsed", "hours_since", "started_at"):
        assert forbidden not in body, forbidden


def test_the_adapter_returns_the_contract_shape_unchanged():
    value, confidence, basis = cardio_load_estimate(
        machine_type="velo", duration_min=20, bpm_avg=130)
    assert isinstance(value, float)
    assert isinstance(confidence, Confidence)
    assert isinstance(basis, tuple)
    assert all(isinstance(b, str) for b in basis)


def test_fatigue_signal_still_has_no_aggregate():
    """Cardio stays a separate observable component (OQ-3)."""
    forbidden = {"overall", "as_availability", "aggregate", "score", "weighted"}
    assert {n for n in dir(rc.FatigueSignal) if not n.startswith("_")} & forbidden == set()


def test_training_state_still_exposes_no_score():
    forbidden = {"overall_score", "readiness_score", "recovery_percentage", "score"}
    assert {n for n in dir(rc.TrainingState) if not n.startswith("_")} & forbidden == set()


def test_no_persisted_model_or_migration_is_touched():
    source = Path(rc.__file__).read_text(encoding="utf-8")
    for forbidden in ("sqlalchemy", "mapped_column", "op.add_column", "SessionLocal"):
        assert forbidden not in source, forbidden


# ---------------------------------------------------------------------------
# Wording guardrails
# ---------------------------------------------------------------------------


def test_the_cardio_surface_never_claims_to_measure_a_body():
    surface = [
        inspect.getdoc(cardio_load_estimate) or "",
        inspect.getdoc(cardio_zone_exposure) or "",
        inspect.getdoc(normalize_cardio_modality) or "",
        inspect.getdoc(rc.CardioZoneExposure) or "",
        inspect.getdoc(rc.CardioModality) or "",
    ]
    haystack = " ".join(surface).casefold()
    for forbidden in rc.FORBIDDEN_CONTRACT_WORDING:
        assert forbidden.casefold() not in haystack, forbidden


def test_the_value_is_described_as_a_proxy_not_as_physiology():
    doc = (inspect.getdoc(cardio_load_estimate) or "").casefold()
    assert "exposure proxy" in doc
    assert "not" in doc
