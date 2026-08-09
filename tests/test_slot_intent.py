"""Tests for the pure SlotIntent layer (Sb_PROGRAM_SLOT_INTENT_01).

Proves the morphology→programming bridge is pure & additive: slot intents build from
priorities and morphology descriptors, guarded/unsupported descriptors yield nothing, the
layer mutates neither catalog templates nor substitutions, and it reuses the EXISTING
compute_proximity contract read-only (substitution behaviour unchanged).
"""
from __future__ import annotations

import hashlib
import pathlib
import sys

from app.services import slot_intent as SI
from app.services import substitution as SUB
from app.services.morphology_profile import build_morphology_profile, guarded_not_deductible

_ROOT = pathlib.Path(__file__).resolve().parent.parent
_FIXTURE_DIR = _ROOT / "tests" / "fixtures" / "dogfood"
sys.path.insert(0, str(_FIXTURE_DIR))
import martin_morphology  # noqa: E402

# The 8 canonical intents of the merged "Full Body — Morphotype Priority" program.
FULL_BODY_INTENTS = {
    "upper_chest_primary_press": ("pecs", "pecs", "push_horizontal"),
    "upper_back_depth_row": ("upper_back", "back_thickness", "pull_horizontal"),
    "quad_minimum_effective_dose": ("quads", "lower", "squat"),
    "posterior_chain_hinge": ("posterior", "lower", "hinge"),
    "lateral_delt_priority": ("delt_lat", "shoulders", "isolation_upper"),
    "rear_delt_upper_back_accessory": ("delt_post", "shoulders", "isolation_upper"),
    "calves_gastrocnemius_priority": ("calves", "lower", "isolation_lower"),
    "calves_soleus_priority": ("calves", "lower", "isolation_lower"),
}


def _sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# ─────────────────────── build from priorities / descriptors ───────────────────────


def test_build_from_priorities():
    intents = SI.build_slot_intents_from_priorities(
        [("lateral_delts", 1), ("upper_chest", 2), ("calves", 4)]
    )
    ids = [i.intent_id for i in intents]
    # calves priority expands to gastrocnemius + soleus
    assert ids == [
        "lateral_delt_priority", "upper_chest_primary_press",
        "calves_gastrocnemius_priority", "calves_soleus_priority",
    ]
    assert intents[0].priority_level == 1
    assert all(i.engine_version == SI.SLOT_INTENT_ENGINE_VERSION for i in intents)


def test_unknown_priority_key_is_skipped():
    assert SI.build_slot_intents_from_priorities([("not_a_priority", 1)]) == ()


def test_known_morphology_descriptor_maps_to_expected_intents():
    facts = martin_morphology.martin_morphology_facts()
    descriptors = build_morphology_profile(facts)
    intents = SI.build_slot_intents_from_descriptors(descriptors)
    ids = {i.intent_id for i in intents}
    assert ids == {
        "lateral_delt_priority",
        "upper_chest_primary_press",
        "rear_delt_upper_back_accessory",
    }
    # source descriptors are carried as evidence (traceability)
    for i in intents:
        assert i.source_descriptors


def test_guarded_and_unsupported_descriptors_produce_no_slot_intent():
    # a guarded (not_deductible) descriptor -> nothing
    guarded = guarded_not_deductible("femur_length_cm")
    assert SI.build_slot_intents_from_descriptors([guarded]) == ()
    # a plain FACT / non-priority inference -> nothing (only priority candidates map)
    facts = martin_morphology.martin_morphology_facts()
    non_priority = [
        d for d in build_morphology_profile(facts)
        if not d.descriptor_id.endswith("_priority_candidate")
    ]
    assert non_priority  # there are such descriptors
    assert SI.build_slot_intents_from_descriptors(non_priority) == ()


# ─────────────────────── schema / representability ───────────────────────


def test_all_full_body_intents_are_representable():
    for intent_id, (primary, region, pattern) in FULL_BODY_INTENTS.items():
        si = SI.build_slot_intent(intent_id, slot_id="s1", priority_level=1)
        assert si is not None, intent_id
        assert si.primary_zone == primary
        assert si.target_region == region
        assert si.movement_pattern == pattern
        assert si.rationale
        assert isinstance(si.to_dict(), dict)


def test_unknown_intent_id_returns_none():
    assert SI.build_slot_intent("no_such_intent", slot_id="s1", priority_level=1) is None


def test_intents_use_valid_taxonomy():
    for intent_id in SI.KNOWN_INTENT_IDS:
        si = SI.build_slot_intent(intent_id, slot_id="s1", priority_level=1)
        assert si.movement_pattern in SUB.VALID_PATTERN_MOTORS
        assert all(p in SUB.VALID_PATTERN_MOTORS for p in si.forbidden_substitution_patterns)
        assert si.target_region == SI.DETAILED_TO_REGION[si.primary_zone]


# ─────────────────────── read-only reuse of compute_proximity ───────────────────────


def test_score_candidate_uses_compute_proximity_contract():
    si = SI.build_slot_intent("upper_chest_primary_press", slot_id="s1", priority_level=1)
    # a matching candidate (pecs + push_horizontal + compound) scores high
    match = {"zone_primary": "pecs", "pattern_motor": "push_horizontal",
             "equipment_family": "machine", "chain": "compound"}
    mismatch = {"zone_primary": "lower", "pattern_motor": "isolation_lower",
                "equipment_family": "machine", "chain": "isolation"}
    assert SI.score_candidate(si, match) == SUB.compute_proximity(SI.target_props(si), match)
    assert SI.score_candidate(si, match) > SI.score_candidate(si, mismatch)
    assert SI.score_candidate(si, match) >= 80  # zone+pattern+chain at least


def test_forbidden_pattern_guard():
    si = SI.build_slot_intent("lateral_delt_priority", slot_id="s1", priority_level=1)
    press = {"zone_primary": "shoulders", "pattern_motor": "push_vertical"}
    raise_ = {"zone_primary": "shoulders", "pattern_motor": "isolation_upper"}
    assert SI.candidate_pattern_forbidden(si, press) is True   # a shoulder press breaks the intent
    assert SI.candidate_pattern_forbidden(si, raise_) is False


# ─────────────────────── purity / no mutation ───────────────────────


def test_layer_does_not_mutate_catalog_or_properties():
    catalog = _ROOT / "data" / "reference_split.json"
    props = _ROOT / "data" / "exercise_properties.json"
    before = (_sha(catalog), _sha(props))
    facts = martin_morphology.martin_morphology_facts()
    intents = SI.build_slot_intents_from_descriptors(build_morphology_profile(facts))
    for i in intents:
        SI.score_candidate(i, {"zone_primary": i.target_region,
                               "pattern_motor": i.movement_pattern, "chain": i.chain})
    after = (_sha(catalog), _sha(props))
    assert before == after  # slot-intent layer wrote nothing


def test_substitution_module_contract_unchanged():
    # the reuse imports the real substitution engine without altering its contract
    assert len(SUB.VALID_PATTERN_MOTORS) == 11
    assert SUB.BADGE_N1 == "Équivalent"
    assert SUB.PROXIMITY_THRESHOLD_N2 == 50
    # pattern-different can never be N1/N2 — the core invariant, verified via the classifier
    level, _badge, _r = SUB._classify_suggestion(
        {"pattern_motor": "push_horizontal", "zone_primary": "pecs"},
        {"pattern_motor": "isolation_upper", "zone_primary": "shoulders"},
    )
    assert level == "N3"


def test_build_is_deterministic():
    facts = martin_morphology.martin_morphology_facts()
    a = [i.to_dict() for i in SI.build_slot_intents_from_descriptors(build_morphology_profile(facts))]
    b = [i.to_dict() for i in SI.build_slot_intents_from_descriptors(build_morphology_profile(facts))]
    assert a == b
