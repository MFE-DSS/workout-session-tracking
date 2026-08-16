"""Sb_22a — tests for the tiered N1/N2/N3 substitution heuristic.

Hard contract validation per spec Sx_22a v1.1 §C.1, §C.3:
* pattern_motor enum closed and validated at load
* N1 requires 4-dim match (curated or derived)
* N2 requires same pattern_motor + proximity ≥ 50
* N3 = different pattern OR proximity < 50 (zone-only or bridge)
* Curated cross-pattern entries are demoted to N3 instead of raising
* compute_suggestions never mutates input
"""
from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest


def _make_te(name: str, subs: list[str] | None = None):
    """Build a minimal mock TemplateExercise."""
    te = MagicMock()
    te.name = name
    te.substitutes_json = json.dumps(subs) if subs else None
    return te


# ---------------------------------------------------------------------------
# Enum + registry validation
# ---------------------------------------------------------------------------


def test_pattern_motor_enum_has_11_values():
    from app.services.substitution import VALID_PATTERN_MOTORS
    assert len(VALID_PATTERN_MOTORS) == 11
    expected = {
        "push_horizontal", "push_vertical",
        "pull_horizontal", "pull_vertical",
        "squat", "hinge", "lunge",
        "isolation_upper", "isolation_lower",
        "core", "cardio",
    }
    assert VALID_PATTERN_MOTORS == expected


def test_exercise_properties_loads_and_validates():
    from app.services.substitution import VALID_PATTERN_MOTORS, load_exercise_properties
    props = load_exercise_properties()
    assert len(props) > 0, "registry should not be empty"
    for name, entry in props.items():
        assert entry["pattern_motor"] in VALID_PATTERN_MOTORS, (
            f"'{name}' has invalid pattern_motor"
        )
        assert entry["zone_primary"], f"'{name}' missing zone_primary"
        assert entry["equipment_family"], f"'{name}' missing equipment_family"
        assert entry["chain"] in ("compound", "isolation"), (
            f"'{name}' invalid chain"
        )


def test_cross_pattern_bridges_load():
    from app.services.substitution import load_cross_pattern_bridges
    bridges = load_cross_pattern_bridges()
    assert len(bridges) >= 2, "Sb_22a v1 expects ≥ 2 bridges (rowing ↔ tirage vertical)"
    for b in bridges:
        assert b["from_pattern"] and b["to_pattern"]
        assert b["intent"], "every bridge must declare its intent"


# ---------------------------------------------------------------------------
# Proximity scoring
# ---------------------------------------------------------------------------


def test_proximity_perfect_match_equals_95():
    from app.services.substitution import compute_proximity
    a = {"pattern_motor": "push_horizontal", "zone_primary": "pecs",
         "equipment_family": "machine", "chain": "compound"}
    assert compute_proximity(a, a) == 95


def test_proximity_pattern_only_equals_20():
    from app.services.substitution import compute_proximity
    a = {"pattern_motor": "push_horizontal", "zone_primary": "pecs",
         "equipment_family": "machine", "chain": "compound"}
    b = {"pattern_motor": "push_horizontal", "zone_primary": "shoulders",
         "equipment_family": "barbell", "chain": "isolation"}
    assert compute_proximity(a, b) == 20


def test_proximity_zone_only_equals_50():
    from app.services.substitution import compute_proximity
    a = {"pattern_motor": "push_horizontal", "zone_primary": "lower",
         "equipment_family": "machine", "chain": "compound"}
    b = {"pattern_motor": "squat", "zone_primary": "lower",
         "equipment_family": "barbell", "chain": "isolation"}
    assert compute_proximity(a, b) == 50


# ---------------------------------------------------------------------------
# Hard contract — pattern_motor mismatch can never reach N1/N2 derived
# ---------------------------------------------------------------------------


def test_n2_candidate_with_different_pattern_is_never_promoted():
    """Spec §C.3 v1.1 garde-fou : a candidate with a different
    pattern_motor MUST fall to N3, never N1/N2."""
    from app.services.substitution import compute_suggestions
    # Origin = adduction assise (isolation_lower). A pure squat-pattern
    # candidate (back squat ~ squat/lower/barbell/compound) shares zone
    # but differs in pattern → must be N3 only.
    te = _make_te("Adduction assise")
    out = compute_suggestions(te)
    for level in ("N1", "N2"):
        for sug in out[level]:
            # N1/N2 derived from registry must share pattern_motor with origin.
            from app.services.substitution import load_exercise_properties
            props = load_exercise_properties()
            origin_pm = props["Adduction assise"]["pattern_motor"]
            cand = props.get(sug.name)
            if cand is not None:
                assert cand["pattern_motor"] == origin_pm, (
                    f"{sug.name} in {level} has pattern {cand['pattern_motor']} "
                    f"vs origin {origin_pm}"
                )


def test_curated_cross_pattern_demoted_to_n3():
    """Spec v1.1 — a curated substitute with different pattern_motor is
    demoted silently to N3 (preserves prévu/réalisé contract), not raised."""
    from app.services.substitution import compute_suggestions
    # Origin pull_horizontal, curated sub pull_vertical (legacy v13 C2).
    te = _make_te(
        "Rowing machine chest-supported",
        subs=["Tirage poulie haute prise neutre"],
    )
    out = compute_suggestions(te)
    n3_names = [s.name for s in out["N3"]]
    assert "Tirage poulie haute prise neutre" in n3_names
    n1_names = [s.name for s in out["N1"]]
    assert "Tirage poulie haute prise neutre" not in n1_names


# ---------------------------------------------------------------------------
# Cross-pattern bridges
# ---------------------------------------------------------------------------


def test_rowing_bridges_to_tirage_vertical_in_n3():
    """Rowing → tirage vertical exists as a bridge (C2 dogfood)."""
    from app.services.substitution import compute_suggestions
    te = _make_te("Rowing machine chest-supported")
    out = compute_suggestions(te)
    n3_names = {s.name for s in out["N3"]}
    # At least one tirage vertical should surface.
    assert any("Tirage" in n or "pulldown" in n.lower() for n in n3_names), (
        f"Expected a tirage-vertical bridge target in N3, got {n3_names}"
    )


def test_n3_bridge_carries_intent_rationale():
    from app.services.substitution import compute_suggestions
    te = _make_te("Tirage poulie haute prise large")
    out = compute_suggestions(te)
    bridge_subs = [s for s in out["N3"] if s.rationale and "intention" in s.rationale]
    assert len(bridge_subs) >= 1


# ---------------------------------------------------------------------------
# Functional coverage — the 7 MVP families
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("origin_name", [
    "Adduction assise",
    "Rowing machine chest-supported",
    "Tirage poulie haute prise neutre",
    "Machine shoulder press",
    "Leg extensions assises",
    "Leg curls assis",
    "Triceps pushdown corde",
    "Curl EZ-bar debout",
    "Chest Press machine",
    "Développé incliné haltères 30°",
])
def test_mvp_family_origin_has_at_least_one_suggestion(origin_name):
    """MVP coverage : every origin in the 7 high-value families must
    surface at least one suggestion across N1+N2+N3."""
    from app.services.substitution import compute_suggestions
    te = _make_te(origin_name)
    out = compute_suggestions(te)
    total = len(out["N1"]) + len(out["N2"]) + len(out["N3"])
    assert total >= 1, f"'{origin_name}' has no suggestion at any level"


# ---------------------------------------------------------------------------
# Immutability — prévu/réalisé contract preservation
# ---------------------------------------------------------------------------


def test_compute_suggestions_does_not_mutate_template_exercise():
    """Spec §D.bis : compute_suggestions must NEVER mutate the input."""
    from app.services.substitution import compute_suggestions
    te = _make_te("Adduction assise", subs=["Adduction debout câble"])
    pre_name = te.name
    pre_subs = te.substitutes_json
    _ = compute_suggestions(te)
    assert te.name == pre_name
    assert te.substitutes_json == pre_subs


def test_compute_suggestions_unknown_origin_returns_curated_only():
    """An exercise absent from the registry returns curated N1 only."""
    from app.services.substitution import compute_suggestions
    te = _make_te("Some Exercise Not In Registry", subs=["Random sub"])
    out = compute_suggestions(te)
    assert [s.name for s in out["N1"]] == ["Random sub"]
    assert out["N2"] == []
    assert out["N3"] == []


def test_compute_suggestions_none_input_returns_empty():
    from app.services.substitution import compute_suggestions
    out = compute_suggestions(None)
    assert out == {"N1": [], "N2": [], "N3": []}


# ---------------------------------------------------------------------------
# Origin name excluded from its own suggestions
# ---------------------------------------------------------------------------


def test_origin_never_suggests_itself():
    from app.services.substitution import compute_suggestions
    te = _make_te("Adduction assise")
    out = compute_suggestions(te)
    all_names = {s.name for level in out.values() for s in level}
    assert "Adduction assise" not in all_names


# ---------------------------------------------------------------------------
# Sb_22a.next — muscle_group sub-zone for lower zone (regression guard)
# ---------------------------------------------------------------------------


def test_adduction_n1_excludes_leg_extensions_and_curls():
    """Sb_22a.next regression — Leg extension/curl must NOT appear in N1
    of an adduction origin. They share zone_primary=lower but differ in
    muscle_group (quadriceps/hamstrings vs adductors)."""
    from app.services.substitution import compute_suggestions
    te = _make_te("Adduction assise")
    out = compute_suggestions(te)
    n1_names = [s.name for s in out["N1"]]
    forbidden = {
        "Leg extensions assises",
        "Leg extension câble unilatéral",
        "Leg curls allongé",
        "Leg curls assis",
        "Reverse Nordic",
        "Sliding leg curl",
    }
    for name in forbidden:
        assert name not in n1_names, (
            f"'{name}' must not be N1 for Adduction assise — "
            "different muscle_group (regression Sb_22a.next)"
        )


def test_adduction_keeps_legitimate_adductors_in_n1():
    """Adduction couchée machine / Adduction debout câble are real
    adductor exercises and must remain reachable via the drawer at N1
    (curated) regardless of equipment differences."""
    from app.services.substitution import compute_suggestions
    te = _make_te(
        "Adduction assise",
        subs=["Adduction debout câble", "Adduction couchée machine"],
    )
    out = compute_suggestions(te)
    n1_names = {s.name for s in out["N1"]}
    assert "Adduction couchée machine" in n1_names
    assert "Adduction debout câble" in n1_names


def test_leg_extensions_appear_in_n2_for_adduction_with_rationale():
    """Demoted from N1 to N2 (same pattern_motor isolation_lower but
    different muscle_group). The rationale must surface the difference."""
    from app.services.substitution import compute_suggestions
    te = _make_te("Adduction assise")
    out = compute_suggestions(te)
    n2_names = [s.name for s in out["N2"]]
    assert "Leg extensions assises" in n2_names
    # Find the suggestion and check rationale mentions muscle group.
    leg_ext_sug = next(s for s in out["N2"] if s.name == "Leg extensions assises")
    assert "groupe" in (leg_ext_sug.rationale or "").lower() or "quadriceps" in (
        leg_ext_sug.rationale or ""
    ).lower()


def test_compute_proximity_muscle_group_bonus_when_both_present():
    """Adductors vs adductors → +10. Adductors vs quadriceps → 0 bonus."""
    from app.services.substitution import compute_proximity
    base = {"zone_primary": "lower", "pattern_motor": "isolation_lower",
            "equipment_family": "machine", "chain": "isolation"}
    same_mg = {**base, "muscle_group": "adductors"}
    diff_mg = {**base, "muscle_group": "quadriceps"}
    a = {**same_mg}
    assert compute_proximity(a, same_mg) == 95 + 10
    assert compute_proximity(a, diff_mg) == 95


def test_compute_proximity_no_muscle_group_bonus_when_one_missing():
    """If only one side has muscle_group, no bonus (avoid spurious match
    between exos with sub-zone data and exos without)."""
    from app.services.substitution import compute_proximity
    base = {"zone_primary": "lower", "pattern_motor": "isolation_lower",
            "equipment_family": "machine", "chain": "isolation"}
    with_mg = {**base, "muscle_group": "adductors"}
    without = {**base}
    assert compute_proximity(with_mg, without) == 95
    assert compute_proximity(without, with_mg) == 95


def test_lower_exercises_all_have_muscle_group():
    """Sb_22a.next QA — every `lower` entry MUST carry a muscle_group."""
    from app.services.substitution import load_exercise_properties
    props = load_exercise_properties()
    valid = {"adductors", "quadriceps", "hamstrings", "glutes", "calves"}
    for name, entry in props.items():
        if entry.get("zone_primary") != "lower":
            continue
        mg = entry.get("muscle_group")
        assert mg is not None, f"{name}: lower zone requires muscle_group"
        assert mg in valid, f"{name}: muscle_group '{mg}' not in {valid}"


def test_non_lower_exercise_unaffected_by_muscle_group_rule():
    """A non-lower exercise (e.g. Chest Press machine) has no muscle_group
    set; the rule must not block N1 for its candidates."""
    from app.services.substitution import compute_suggestions
    # Push horizontal origin — has no muscle_group set in V1.1
    te = _make_te("Chest Press machine")
    out = compute_suggestions(te)
    # Compose N1+N2+N3 — should at least surface 2 candidates (same-pattern compounds)
    total = len(out["N1"]) + len(out["N2"]) + len(out["N3"])
    assert total >= 2
