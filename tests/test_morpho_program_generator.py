"""Tests for the pure morphology-aware program generator (Sb_MORPHO_PROGRAM_GENERATOR_01).

Proves the generator is a pure, deterministic composition of the delivered layers
(morphology_profile → slot_intent → substitution.compute_proximity read-only + the
exercise_properties pool): same inputs ⇒ same output & fingerprint; morphology descriptors
select the mapped intents; the merged "Full Body — Morphotype Priority" intents are
reproducible; guarded/unsupported descriptors generate no slot; nothing is mutated; no
publication/session-builder is touched; the substitution contract is unchanged.
"""
from __future__ import annotations

import ast
import hashlib
import pathlib
import sys

from app.services import morpho_program_generator as GEN
from app.services import slot_intent as SI
from app.services import substitution as SUB
from app.services.morphology_profile import build_morphology_profile, guarded_not_deductible

_ROOT = pathlib.Path(__file__).resolve().parent.parent
_FIXTURE_DIR = _ROOT / "tests" / "fixtures" / "dogfood"
sys.path.insert(0, str(_FIXTURE_DIR))
import martin_morphology  # noqa: E402

# The 7 training priorities that reproduce the 8 canonical intents of the merged
# "Full Body — Morphotype Priority" catalog program.
FULL_BODY_PRIORITIES = [
    ("upper_chest", 1),
    ("back", 2),
    ("quads_maintenance", 3),
    ("posterior_chain", 4),
    ("lateral_delts", 5),
    ("rear_delts_upper_back", 6),
    ("calves", 7),
]
FULL_BODY_INTENT_IDS = [
    "upper_chest_primary_press",
    "upper_back_depth_row",
    "quad_minimum_effective_dose",
    "posterior_chain_hinge",
    "lateral_delt_priority",
    "rear_delt_upper_back_accessory",
    "calves_gastrocnemius_priority",
    "calves_soleus_priority",
]

_DATA = _ROOT / "data"


def _sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _by_intent(program) -> dict:
    return {s.intent_id: s for s in program.selections}


# ─────────────────────────── determinism ───────────────────────────


def test_deterministic_from_martin_fixture():
    facts = martin_morphology.martin_morphology_facts()
    a = GEN.generate_program(facts=facts)
    b = GEN.generate_program(facts=facts)
    assert a.generated_program_id == b.generated_program_id
    assert a.to_dict() == b.to_dict()
    # A stable fingerprint, prefixed and content-addressed (not a clock/random value).
    assert a.generated_program_id.startswith("mpg1-")
    assert len(a.generated_program_id) == len("mpg1-") + 16


def test_fingerprint_changes_with_inputs():
    base = GEN.generate_program(priorities=[("upper_chest", 1)])
    more = GEN.generate_program(priorities=[("upper_chest", 1), ("back", 2)])
    assert base.generated_program_id != more.generated_program_id


def test_fingerprint_is_a_full_content_address():
    """The id folds in the pool and each slot's fallbacks/warning: different pools that yield the
    same preferred pick still get different ids, and the same custom pool stays deterministic."""
    default = GEN.generate_program(priorities=[("upper_chest", 1)])
    pool = dict(SUB.load_exercise_properties())
    # An extra pecs press: same preferred (ties break by name, "Chest Press machine" wins) but the
    # pool differs and a new fallback appears → the id must differ.
    pool["Zzz incline press"] = {
        "zone_primary": "pecs", "pattern_motor": "push_horizontal",
        "equipment_family": "machine", "chain": "compound", "muscle_group": None,
    }
    custom = GEN.generate_program(priorities=[("upper_chest", 1)], pool=pool)
    custom_again = GEN.generate_program(priorities=[("upper_chest", 1)], pool=pool)
    assert custom.selections[0].preferred_exercise == default.selections[0].preferred_exercise
    assert custom.generated_program_id != default.generated_program_id  # pool folded in
    assert custom.generated_program_id == custom_again.generated_program_id  # still deterministic


# ─────────────────── intents match morphology priorities ───────────────────


def test_martin_descriptors_select_mapped_intents():
    """Martin's morphology descriptors select exactly the 3 mapped priority-candidate intents."""
    program = GEN.generate_program(facts=martin_morphology.martin_morphology_facts())
    assert [s.intent_id for s in program.selections] == [
        "lateral_delt_priority",
        "upper_chest_primary_press",
        "rear_delt_upper_back_accessory",
    ]


def test_required_descriptor_to_intent_mappings():
    """The three required descriptor→intent invariants hold through the generator."""
    from app.services.morphology_profile import MorphologyDescriptor

    def _desc(descriptor_id):
        return MorphologyDescriptor(
            descriptor_id=descriptor_id, layer="INFERENCE", value="candidate",
            confidence="inferred", evidence=(f"focus_candidate:{descriptor_id}",),
            non_medical_guardrail="", rationale="",
        )

    cases = {
        "lateral_delts_priority_candidate": "lateral_delt_priority",
        "upper_chest_priority_candidate": "upper_chest_primary_press",
        "rear_delts_upper_back_priority_candidate": "rear_delt_upper_back_accessory",
    }
    for descriptor_id, intent_id in cases.items():
        program = GEN.generate_program(descriptors=[_desc(descriptor_id)])
        assert [s.intent_id for s in program.selections] == [intent_id]


# ─────────────────── Full Body — Morphotype Priority reproducible ───────────────────


def test_full_body_intents_reproducible():
    a = GEN.generate_program(priorities=FULL_BODY_PRIORITIES)
    b = GEN.generate_program(priorities=FULL_BODY_PRIORITIES)
    assert [s.intent_id for s in a.selections] == FULL_BODY_INTENT_IDS
    assert a.generated_program_id == b.generated_program_id
    assert a.to_dict() == b.to_dict()


def test_full_body_preferred_selections_are_genuine_matches():
    """The pool-covered slots pick a genuinely matching exercise; sparse slots warn, never fake."""
    program = GEN.generate_program(priorities=FULL_BODY_PRIORITIES)
    by = _by_intent(program)
    pool = SUB.load_exercise_properties()

    # upper_chest → a pecs push_horizontal exercise, score 80.
    chest = by["upper_chest_primary_press"]
    assert chest.preferred_exercise is not None
    assert pool[chest.preferred_exercise]["zone_primary"] == "pecs"
    assert pool[chest.preferred_exercise]["pattern_motor"] == "push_horizontal"
    assert chest.preferred_score == 80

    # upper_back → a back_thickness pull_horizontal row, score 80.
    back = by["upper_back_depth_row"]
    assert back.preferred_exercise is not None
    assert pool[back.preferred_exercise]["zone_primary"] == "back_thickness"
    assert pool[back.preferred_exercise]["pattern_motor"] == "pull_horizontal"
    assert back.preferred_score == 80

    # quad → a quadriceps exercise in the lower region (maintenance dose), score 60.
    quad = by["quad_minimum_effective_dose"]
    assert quad.preferred_exercise is not None
    assert pool[quad.preferred_exercise]["muscle_group"] == "quadriceps"
    assert quad.preferred_score == 60


def test_quads_stay_maintenance_not_specialization():
    """The quad intent is the minimum-effective-dose intent and yields a single quad slot."""
    program = GEN.generate_program(priorities=FULL_BODY_PRIORITIES)
    quad_slots = [s for s in program.selections if s.primary_zone == "quads"]
    assert len(quad_slots) == 1
    assert quad_slots[0].intent_id == "quad_minimum_effective_dose"


# ─────────────────── coverage gaps: honest warnings, no fabrication ───────────────────


def test_coverage_gap_warns_and_omits_no_fabrication_with_empty_pool():
    """No-fabrication behaviour, robust to the real pool's coverage: against an EMPTY candidate
    pool every slot is a coverage gap — the generator warns and omits, never inventing an exercise."""
    program = GEN.generate_program(priorities=FULL_BODY_PRIORITIES, pool={})
    for sel in program.selections:
        assert sel.preferred_exercise is None
        assert sel.fallback_candidates == ()
        assert sel.warning is not None
        assert "coverage gap" in sel.warning


def test_covered_morphotype_slots_fill_with_right_muscle():
    """After Sb_MORPHO_POOL_COVERAGE_01 the lateral/rear delt and calf slots fill from the pool,
    each disambiguated to its own muscle_group (never a sibling muscle in the macro region)."""
    program = GEN.generate_program(priorities=FULL_BODY_PRIORITIES)
    by = _by_intent(program)
    pool = SUB.load_exercise_properties()
    expected_mg = {
        "lateral_delt_priority": "delts_lateral",
        "rear_delt_upper_back_accessory": "delts_rear",
        "calves_gastrocnemius_priority": "calves",
        "calves_soleus_priority": "calves",
        "posterior_chain_hinge": "hamstrings",
    }
    for intent_id, mg in expected_mg.items():
        sel = by[intent_id]
        assert sel.preferred_exercise is not None, intent_id
        assert sel.warning is None, intent_id
        assert pool[sel.preferred_exercise]["muscle_group"] == mg


def test_distinct_assignment_is_a_maximum_matching_not_greedy():
    """Two slots contending for candidates are both filled whenever a complete distinct assignment
    exists — a greedy pass in slot order could starve the second slot (Gitar review, PR #67)."""
    two = {
        "CalfX": {
            "pattern_motor": "isolation_lower", "zone_primary": "lower",
            "muscle_group": "calves", "equipment_family": "machine", "chain": "isolation",
        },
        "CalfY": {
            "pattern_motor": "isolation_lower", "zone_primary": "lower",
            "muscle_group": "calves", "equipment_family": "cable", "chain": "isolation",
        },
    }
    program = GEN.generate_program(priorities=[("calves", 1)], pool=two)
    picks = [s.preferred_exercise for s in program.selections]
    assert set(picks) == {"CalfX", "CalfY"}  # both slots filled, distinct
    assert program.warnings == ()


def test_genuine_distinctness_gap_is_still_reported():
    """With a single candidate for two slots no complete assignment exists → exactly one slot
    fills and the other reports a real distinctness gap (never a duplicate prescription)."""
    one = {
        "CalfX": {
            "pattern_motor": "isolation_lower", "zone_primary": "lower",
            "muscle_group": "calves", "equipment_family": "machine", "chain": "isolation",
        },
    }
    program = GEN.generate_program(priorities=[("calves", 1)], pool=one)
    filled = [s for s in program.selections if s.preferred_exercise is not None]
    gapped = [s for s in program.selections if s.preferred_exercise is None]
    assert len(filled) == 1
    assert len(gapped) == 1
    assert "distinctness gap" in gapped[0].warning


def test_calves_only_selected_with_priority_evidence():
    """Morphology descriptors alone never emit a calves slot; an explicit priority does — and now
    that the pool covers calves, both slots fill with genuine, DISTINCT calf exercises."""
    from_desc = GEN.generate_program(facts=martin_morphology.martin_morphology_facts())
    assert not any("calves" in s.intent_id for s in from_desc.selections)

    from_prio = GEN.generate_program(priorities=[("calves", 1)])
    calf_slots = [s for s in from_prio.selections if "calves" in s.intent_id]
    assert len(calf_slots) == 2
    picks = [s.preferred_exercise for s in calf_slots]
    assert all(p is not None for p in picks)  # calves now covered
    assert len(set(picks)) == 2  # distinct — a program never prescribes the same exercise twice
    pool = SUB.load_exercise_properties()
    assert all(pool[p]["muscle_group"] == "calves" for p in picks)


# ─────────────────── guarded / empty ───────────────────


def test_guarded_descriptor_generates_no_slot():
    program = GEN.generate_program(descriptors=[guarded_not_deductible("posture_assessment")])
    assert program.selections == ()
    assert [r.descriptor_id for r in program.rejected_descriptors] == ["posture_assessment"]


def test_empty_inputs_yield_empty_proposal_with_warning():
    program = GEN.generate_program()
    assert program.selections == ()
    assert any("empty proposal" in w for w in program.warnings)


# ─────────────────── availability ───────────────────


def test_availability_filters_candidates():
    machine_only = GEN.generate_program(priorities=[("upper_chest", 1)], availability={"machine"})
    sel = machine_only.selections[0]
    assert sel.preferred_exercise is not None
    assert SUB.load_exercise_properties()[sel.preferred_exercise]["equipment_family"] == "machine"
    assert machine_only.availability == ("machine",)


def test_availability_gap_warns_when_no_available_candidate():
    program = GEN.generate_program(priorities=[("upper_chest", 1)], availability={"kettlebell"})
    sel = program.selections[0]
    assert sel.preferred_exercise is None
    assert sel.warning is not None
    assert "availability gap" in sel.warning


# ─────────────────── no mutation of data files ───────────────────


def test_generator_does_not_mutate_data_files():
    ref = _DATA / "reference_split.json"
    props = _DATA / "exercise_properties.json"
    before = (_sha(ref), _sha(props))
    GEN.generate_program(facts=martin_morphology.martin_morphology_facts())
    GEN.generate_program(priorities=FULL_BODY_PRIORITIES, availability={"machine", "cable"})
    after = (_sha(ref), _sha(props))
    assert before == after


def test_generator_does_not_mutate_the_shared_pool():
    pool = SUB.load_exercise_properties()
    keys_before = set(pool)
    GEN.generate_program(priorities=FULL_BODY_PRIORITIES)
    assert set(SUB.load_exercise_properties()) == keys_before


# ─────────────────── no publication / session-builder coupling ───────────────────


def test_generator_module_imports_no_runtime_side_effect_layer():
    """Static guard: the generator imports only pure layers — no session builder, no publication,
    no routes/models/DB. It composes; it never persists or renders."""
    source = pathlib.Path(GEN.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)
    forbidden = ("session_builder", "publication", "routes", "models", "database", "sqlalchemy", ".db")
    assert not [m for m in imported if any(f in m for f in forbidden)]


# ─────────────────── substitution contract unchanged ───────────────────


def test_substitution_proximity_contract_unchanged():
    """The generator reuses compute_proximity read-only; the canonical scores are intact."""
    props = {
        "zone_primary": "pecs", "pattern_motor": "push_horizontal",
        "equipment_family": "machine", "chain": "compound", "muscle_group": "chest",
    }
    assert SUB.compute_proximity(props, props) == 105
    assert SUB.compute_proximity(props, {**props, "pattern_motor": "push_vertical"}) == 85
    assert len(SUB.VALID_PATTERN_MOTORS) == 11
    # slot_intent.score_candidate still delegates to compute_proximity untouched.
    intent = SI.build_slot_intent("upper_chest_primary_press", slot_id="s1", priority_level=1)
    assert SI.score_candidate(intent, props) == SUB.compute_proximity(SI.target_props(intent), props)


def test_slot_intent_layer_still_maps_descriptors():
    """The composed slot_intent layer keeps its own contract (descriptor→intent) intact."""
    descs = build_morphology_profile(martin_morphology.martin_morphology_facts())
    intents = SI.build_slot_intents_from_descriptors(descs)
    assert {i.intent_id for i in intents} == {
        "lateral_delt_priority",
        "upper_chest_primary_press",
        "rear_delt_upper_back_accessory",
    }
