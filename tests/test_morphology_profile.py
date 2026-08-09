"""Tests for the pure morphology profile layer (Sb_MORPHO_PROFILE_01).

Pins fact/inference separation, the descriptor schema, the confidence model, the strict
non-medical guardrails (`not_deductible`), determinism, and the private Martin dogfood
fixture (10 required descriptors). No DB, no generator, no substitution — pure module.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

from app.services import morphology_profile as M
from app.services.morphology_profile import (
    BodyObservation,
    MorphologyFacts,
    build_morphology_profile,
    guarded_not_deductible,
)

# Private dogfood fixture (test-only, not runtime/global) — imported by path.
_FIXTURE_DIR = pathlib.Path(__file__).resolve().parent / "fixtures" / "dogfood"
sys.path.insert(0, str(_FIXTURE_DIR))
import martin_morphology  # noqa: E402

REQUIRED_MARTIN_DESCRIPTORS = {
    "longiligne_athletic_build",
    "slightly_positive_ape_index_not_extreme",
    "favorable_shoulder_to_waist_structure",
    "narrow_waist_pelvis_relative",
    "quads_relatively_strong",
    "calves_relative_lag",
    "lats_acceptable_not_weak",
    "lateral_delts_priority_candidate",
    "upper_chest_priority_candidate",
    "rear_delts_upper_back_priority_candidate",
}


def _by_id(descriptors):
    return {d.descriptor_id: d for d in descriptors}


# ─────────────────────── fact / inference separation ───────────────────────


def test_numeric_facts_are_fact_layer_measured():
    facts = MorphologyFacts(height_cm=179.0, waist_cm=83.0)
    by_id = _by_id(build_morphology_profile(facts))
    assert by_id["fact_height_cm"].layer == M.LAYER_FACT
    assert by_id["fact_height_cm"].confidence == M.CONF_MEASURED
    assert by_id["fact_height_cm"].value == 179.0


def test_inferences_are_inference_layer_and_never_fabricate_a_fact():
    facts = MorphologyFacts(height_cm=179.0, waist_cm=83.0)
    descriptors = build_morphology_profile(facts)
    inferences = [d for d in descriptors if d.layer == M.LAYER_INFERENCE]
    facts_out = [d for d in descriptors if d.layer == M.LAYER_FACT]
    # every inference cites evidence and is not measured-from-thin-air
    assert inferences and all(d.evidence for d in inferences)
    # a FACT descriptor id is never re-emitted as an INFERENCE
    fact_ids = {d.descriptor_id for d in facts_out}
    assert fact_ids.isdisjoint({d.descriptor_id for d in inferences})


def test_missing_inputs_are_omitted_never_fabricated():
    # No waist -> no waist/height ratio -> no narrow-waist / longiligne inference.
    facts = MorphologyFacts(height_cm=179.0)
    ids = set(_by_id(build_morphology_profile(facts)))
    assert "narrow_waist_pelvis_relative" not in ids
    assert "longiligne_athletic_build" not in ids


# ─────────────────────── descriptor schema ───────────────────────


def test_descriptor_schema_fields_present():
    facts = MorphologyFacts(height_cm=179.0, waist_cm=83.0, chest_cm=100.0)
    for d in build_morphology_profile(facts):
        assert d.descriptor_id and d.layer in (M.LAYER_FACT, M.LAYER_INFERENCE)
        assert d.confidence in (
            M.CONF_MEASURED, M.CONF_DERIVED, M.CONF_INFERRED, M.CONF_NOT_DEDUCTIBLE,
        )
        assert d.non_medical_guardrail  # every descriptor carries a guardrail
        assert d.engine_version == M.MORPHOLOGY_PROFILE_ENGINE_VERSION
        assert isinstance(d.to_dict(), dict)


# ─────────────────────── confidence model ───────────────────────


def test_ape_index_measured_when_provided_derived_when_computed():
    provided = _by_id(build_morphology_profile(MorphologyFacts(ape_index_cm=4.0)))
    assert provided["fact_ape_index_cm"].confidence == M.CONF_MEASURED
    computed = _by_id(build_morphology_profile(
        MorphologyFacts(height_cm=179.0, wingspan_cm=183.0)
    ))
    assert computed["fact_ape_index_cm"].confidence == M.CONF_DERIVED
    assert computed["fact_ape_index_cm"].value == 4.0  # 183 - 179


def test_ratio_inference_is_derived_observation_inference_is_inferred():
    facts = MorphologyFacts(
        height_cm=179.0, waist_cm=83.0, chest_cm=100.0,
        observations=(BodyObservation("quads", "relatively_strong"),),
    )
    by_id = _by_id(build_morphology_profile(facts))
    assert by_id["narrow_waist_pelvis_relative"].confidence == M.CONF_DERIVED
    assert by_id["quads_relatively_strong"].confidence == M.CONF_INFERRED


def test_ape_index_extreme_is_not_flagged_slightly_positive():
    # +10 cm is beyond the not-extreme bound -> no slightly-positive inference.
    ids = set(_by_id(build_morphology_profile(MorphologyFacts(ape_index_cm=10.0))))
    assert "slightly_positive_ape_index_not_extreme" not in ids
    # ...but a 0 or negative ape index is not flagged either.
    ids0 = set(_by_id(build_morphology_profile(MorphologyFacts(ape_index_cm=0.0))))
    assert "slightly_positive_ape_index_not_extreme" not in ids0


# ─────────────────────── non-medical guardrails / not_deductible ───────────────────────


def test_guarded_descriptors_are_never_produced():
    facts = martin_morphology.martin_morphology_facts()
    produced = set(_by_id(build_morphology_profile(facts)))
    assert produced.isdisjoint(M.GUARDED_NOT_DEDUCTIBLE)


def test_guarded_not_deductible_returns_refusal():
    for key in ("femur_length_cm", "posture_assessment", "muscle_insertions",
                "body_fat_percentage", "scapular_dyskinesis"):
        d = guarded_not_deductible(key)
        assert d.confidence == M.CONF_NOT_DEDUCTIBLE
        assert d.value is None


def test_guarded_not_deductible_rejects_non_guarded_key():
    with pytest.raises(ValueError):
        guarded_not_deductible("longiligne_athletic_build")


def test_no_descriptor_value_claims_posture_or_diagnosis():
    facts = martin_morphology.martin_morphology_facts()
    for d in build_morphology_profile(facts):
        # the VALUE is the asserted content; it must never carry a posture/diagnosis/femur claim
        val = str(d.value).lower()
        assert "diagnos" not in val
        assert "posture" not in val
        assert "femur" not in val and "fémur" not in val
        assert d.non_medical_guardrail  # every descriptor carries a guardrail


# ─────────────────────── determinism ───────────────────────


def test_deterministic_same_input_same_output():
    facts = martin_morphology.martin_morphology_facts()
    a = [d.to_dict() for d in build_morphology_profile(facts)]
    b = [d.to_dict() for d in build_morphology_profile(facts)]
    assert a == b


# ─────────────────────── Martin dogfood fixture ───────────────────────


def test_martin_fixture_produces_all_required_descriptors():
    facts = martin_morphology.martin_morphology_facts()
    ids = set(_by_id(build_morphology_profile(facts)))
    missing = REQUIRED_MARTIN_DESCRIPTORS - ids
    assert not missing, f"missing required descriptors: {sorted(missing)}"


def test_martin_priority_candidates_are_candidates_not_priorities():
    facts = martin_morphology.martin_morphology_facts()
    by_id = _by_id(build_morphology_profile(facts))
    for cid in ("lateral_delts_priority_candidate", "upper_chest_priority_candidate",
                "rear_delts_upper_back_priority_candidate"):
        d = by_id[cid]
        assert d.layer == M.LAYER_INFERENCE
        assert d.value == "candidate"  # a candidate, never an applied priority/slot


def test_martin_facts_layer_has_the_measurements():
    facts = martin_morphology.martin_morphology_facts()
    by_id = _by_id(build_morphology_profile(facts))
    for fid in ("fact_height_cm", "fact_waist_cm", "fact_chest_cm",
                "fact_calf_cm", "fact_ape_index_cm"):
        assert by_id[fid].layer == M.LAYER_FACT


def test_fixture_is_marked_private():
    # The dogfood sample must self-identify as private (never global/runtime).
    assert "private" in martin_morphology.MARTIN_SOURCE.lower()
