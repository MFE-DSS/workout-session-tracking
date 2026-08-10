"""Tests for Martin's DERIVED morphology-aware program (Sb_MARTIN_PROGRAM_01).

Proves the 4ᵗʰ queue build is a pure, deterministic *derivation* of Martin's program from his
private morphology fixture through the delivered generator: it reproduces the Full Body —
Morphotype Priority intent shape, fills the pool-covered slots with genuine EKB exercises,
honestly flags his uncovered morphotype-priority muscles (lateral delts / rear delts / calves),
mutates nothing, persists nothing, and keeps all Martin-specific data private (test-only).
"""
from __future__ import annotations

import ast
import hashlib
import pathlib
import sys

from app.services import substitution as SUB

_ROOT = pathlib.Path(__file__).resolve().parent.parent
_FIXTURE_DIR = _ROOT / "tests" / "fixtures" / "dogfood"
sys.path.insert(0, str(_FIXTURE_DIR))
import martin_program  # noqa: E402

_DATA = _ROOT / "data"

# The 8 canonical intents of the "Full Body — Morphotype Priority" shape (order = Martin's
# morphology-descriptor-driven intents first, then his priority-driven remainder).
EXPECTED_INTENT_IDS = {
    "lateral_delt_priority",
    "upper_chest_primary_press",
    "rear_delt_upper_back_accessory",
    "calves_gastrocnemius_priority",
    "calves_soleus_priority",
    "upper_back_depth_row",
    "quad_minimum_effective_dose",
    "posterior_chain_hinge",
}
# Martin's morphotype-priority muscles that the current exercise_properties pool does NOT cover.
# Sb_MORPHO_POOL_COVERAGE_01 covered Martin's headline morphotype-priority muscles (lateral &
# rear delts, calves) + the posterior-chain hinge, so all 8 slots now fill from the pool.
NOW_COVERED_MORPHOTYPE_INTENTS = {
    "lateral_delt_priority",
    "rear_delt_upper_back_accessory",
    "calves_gastrocnemius_priority",
    "calves_soleus_priority",
    "posterior_chain_hinge",
}
ALWAYS_COVERED_INTENTS = {
    "upper_chest_primary_press",
    "upper_back_depth_row",
    "quad_minimum_effective_dose",
}


def _sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _by_intent(program):
    return {s.intent_id: s for s in program.selections}


# ─────────────────────────── deterministic derivation ───────────────────────────


def test_martin_program_is_deterministic():
    a = martin_program.martin_program()
    b = martin_program.martin_program()
    assert a.generated_program_id == b.generated_program_id
    assert a.to_dict() == b.to_dict()
    assert a.generated_program_id.startswith("mpg1-")


def test_martin_program_reproduces_full_body_morphotype_shape():
    program = martin_program.martin_program()
    assert {s.intent_id for s in program.selections} == EXPECTED_INTENT_IDS
    assert len(program.selections) == 8


# ─────────────────── covered slots filled with genuine EKB exercises ───────────────────


def test_covered_slots_get_genuine_pool_exercises():
    program = martin_program.martin_program()
    by = _by_intent(program)
    pool = SUB.load_exercise_properties()
    for intent_id in ALWAYS_COVERED_INTENTS:
        sel = by[intent_id]
        assert sel.preferred_exercise is not None
        assert sel.preferred_exercise in pool  # a real EKB/properties exercise, never invented
        assert sel.warning is None

    # The concrete picks, anchored (deterministic).
    assert pool[by["upper_chest_primary_press"].preferred_exercise]["zone_primary"] == "pecs"
    assert pool[by["upper_back_depth_row"].preferred_exercise]["zone_primary"] == "back_thickness"
    assert pool[by["quad_minimum_effective_dose"].preferred_exercise]["muscle_group"] == "quadriceps"


def test_covered_picks_respect_martin_availability():
    program = martin_program.martin_program()
    pool = SUB.load_exercise_properties()
    availability = martin_program.martin_availability()
    for sel in program.selections:
        if sel.preferred_exercise is not None:
            assert pool[sel.preferred_exercise]["equipment_family"] in availability


# ─────────────────── honest coverage-gap finding (no fabrication) ───────────────────


def test_morphotype_priorities_now_fill_from_the_pool():
    """After Sb_MORPHO_POOL_COVERAGE_01 Martin's headline morphotype priorities (lateral & rear
    delts, calves) and the posterior-chain hinge fill with genuine pool exercises — no more gaps."""
    program = martin_program.martin_program()
    by = _by_intent(program)
    pool = SUB.load_exercise_properties()
    for intent_id in NOW_COVERED_MORPHOTYPE_INTENTS:
        sel = by[intent_id]
        assert sel.preferred_exercise is not None, intent_id
        assert sel.preferred_exercise in pool
        assert sel.warning is None, intent_id


def test_program_is_now_complete_and_distinct():
    """All 8 slots fill (0 warnings) with 8 DISTINCT exercises — a program never prescribes the
    same exercise twice (the two calf slots get different calf raises)."""
    program = martin_program.martin_program()
    filled = {s.intent_id for s in program.selections if s.preferred_exercise is not None}
    assert filled == NOW_COVERED_MORPHOTYPE_INTENTS | ALWAYS_COVERED_INTENTS
    assert len(program.warnings) == 0
    picks = [s.preferred_exercise for s in program.selections]
    assert len(picks) == 8
    assert len(set(picks)) == 8  # all distinct


# ─────────────────── purity: no mutation, no persistence, private ───────────────────


def test_deriving_martin_program_mutates_no_data_files():
    ref = _DATA / "reference_split.json"
    props = _DATA / "exercise_properties.json"
    before = (_sha(ref), _sha(props))
    martin_program.martin_program()
    after = (_sha(ref), _sha(props))
    assert before == after


def test_martin_program_fixture_has_no_persistence_or_publication_coupling():
    """Static guard: the private fixture imports only the pure generator + the morphology fixture —
    no DB, no publication, no session builder, no routes/models."""
    source = pathlib.Path(martin_program.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)
    forbidden = ("session_builder", "publication", "routes", "models", "database", "sqlalchemy", ".db")
    assert not [m for m in imported if any(f in m for f in forbidden)]


def test_martin_data_stays_private_and_test_only():
    assert "private" in martin_program.MARTIN_PROGRAM_SOURCE.lower()
    assert "private" in martin_program.MARTIN_SOURCE.lower()
    # The fixture lives under tests/ — never in app/, data/, or a catalog template.
    assert "tests/fixtures/dogfood" in martin_program.__file__.replace("\\", "/")


def test_no_new_exercise_names_introduced():
    """Every preferred exercise Martin's program selects is an existing pool (EKB/properties)
    name — the derivation never coins a new exercise (no EKB expansion)."""
    program = martin_program.martin_program()
    pool = SUB.load_exercise_properties()
    picked = {s.preferred_exercise for s in program.selections if s.preferred_exercise}
    assert picked <= set(pool)


def test_martin_priorities_are_ranked_and_closed_vocab():
    """Martin's declared priorities are a ranked list over the generator's known priority keys."""
    from app.services.slot_intent import PRIORITY_TO_INTENTS

    priorities = martin_program.martin_training_priorities()
    keys = [k for k, _ in priorities]
    ranks = [r for _, r in priorities]
    assert len(keys) == len(set(keys))  # no duplicate priority
    assert ranks == sorted(ranks)  # ranked
    assert all(k in PRIORITY_TO_INTENTS for k in keys)  # closed vocabulary, no fabrication
