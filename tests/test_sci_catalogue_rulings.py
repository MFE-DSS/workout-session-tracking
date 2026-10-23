"""Sb_SCI_V2_01 — les rulings de l'opérateur, tels qu'ils sont écrits.

Ces invariants sont recopiés depuis le texte des arbitrages (rulings 1–14, rulings d'identité
G08–G31, GO BUILD `Sb_SCI_V2_01`), **pas** relus dans le générateur : une garde qui
relirait les constantes de `scripts/generate_sci_catalogue.py` ne garderait rien.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCI = ROOT / "data" / "sci"


def _catalogue() -> dict:
    return json.loads((SCI / "exercise_catalogue.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def by_id() -> dict[str, dict]:
    return {r["exercise_id"]: r for r in _catalogue()["records"]}


def _roles(record: dict) -> dict[str, str]:
    return {c["zone"]: c["role"] for c in record["exercise_science"]["contributions"]}


def _identity(record: dict) -> str:
    return record["identity"]["scientific_identity_id"]


# ── comptes de la clôture (GO BUILD : « canonical candidate count matches generated closure »)


def test_107_source_records_84_identities_23_aliases(by_id):
    canon = [r for r in by_id.values() if r["identity"]["identity_relation"] == "CANONICAL"]
    alias = [r for r in by_id.values() if r["identity"]["identity_relation"] == "LEGACY_ALIAS"]
    assert len(by_id) == 107
    assert len(canon) == 84
    assert len(alias) == 23
    assert len({_identity(r) for r in canon}) == 84


def test_no_identity_is_left_unresolved(by_id):
    unresolved = [rid for rid, r in by_id.items() if r["identity"]["group_classification"] == "UNRESOLVED"]
    assert unresolved == []


def test_machine_unspecified_and_unknown_equipment_stay_explicit(by_id):
    modes = [r["exercise_operational"]["equipment_mode"] for r in by_id.values()]
    unknown = [rid for rid, r in by_id.items()
               if r["exercise_operational"]["equipment_requirement_status"] == "UNKNOWN"]
    assert modes.count("machine_unspecified") == 29
    assert unknown == ["adduction-couchee-machine"]


# ── rulings 1–4 et 12 : les cinq cas contestés


def test_r1_pallof_is_loaded_anti_rotation_with_abs_primary(by_id):
    r = by_id["pallof-press-cable"]
    assert _roles(r)["abs"] == "PRIMARY"
    assert r["exercise_science"]["movement_pattern"] == "trunk_anti_rotation"
    assert "trunk_anti_rotation" in r["exercise_science"]["loaded_joint_actions"]


@pytest.mark.parametrize("rid", ["roulette-abdominale", "roulette-abdominale-paren-ab-wheel-rollout"])
def test_r2_ab_wheel_is_one_kneeling_rollout(by_id, rid):
    r = by_id[rid]
    roles = _roles(r)
    assert _identity(r) == "kneeling_ab_wheel_rollout"
    assert (roles["abs"], roles["lats"], roles["hip_flexors"]) == ("PRIMARY", "SECONDARY", "MINOR")
    assert r["exercise_science"]["movement_pattern"] == "trunk_anti_extension"


def test_r3_y_raise_is_the_prone_incline_variant(by_id):
    r = by_id["y-raise-haltere"]
    assert _identity(r) == "prone_incline_y_raise"
    assert _roles(r)["upper_back"] == "PRIMARY"
    assert "scapular_upward_rotation" in r["exercise_science"]["loaded_joint_actions"]
    assert r["exercise_operational"]["equipment_requirements"] == ["dumbbells", "incline_bench_support"]


def test_r4_generic_chest_supported_row_roles(by_id):
    roles = _roles(by_id["rowing-chest-supported"])
    assert (roles["upper_back"], roles["lats"], roles["rear_delts"]) == ("PRIMARY", "SECONDARY", "SECONDARY")


def test_r12_wide_grip_cable_upright_row_display(by_id):
    r = by_id["tirage-front-cable-paren-prise-large"]
    assert _roles(r)["lateral_delts"] == "PRIMARY"
    assert r["identity"]["canonical_display_name"] == "Tirage menton câble — prise large"


# ── rulings d'identité G08–G31 : qui partage une identité, qui reste distinct

SAME_IDENTITY = {
    "cable_rope_triceps_pushdown": {"triceps-pushdown-corde", "pushdown-corde",
                                    "triceps-extension-poulie-haute-paren-corde"},
    "low_cable_straight_bar_curl": {"curl-poulie-basse-paren-barre", "curl-poulie-basse", "curl-cable-basse"},
    "cable_rope_hammer_curl": {"curl-marteau-cable-paren-corde", "curl-marteau-cable-corde",
                               "curl-prise-neutre-cable"},
    "neutral_grip_lat_pulldown": {"tirage-poulie-haute-prise-neutre", "lat-pulldown-prise-neutre"},
    "straight_arm_cable_pullover": {"pullover-cable-paren-bras-tendus-poulie-haute",
                                    "pullover-cable-paren-bras-tendus", "straight-arm-pulldown-cable"},
    "chest_supported_row": {"rowing-chest-supported", "rowing-machine-chest-supported"},
    "wide_grip_cable_upright_row": {"tirage-front-cable-paren-prise-large", "upright-row-cable"},
    "leg_press_low_feet": {"leg-press-paren-pieds-bas", "leg-press-paren-pieds-bas-serres"},
    "bench_supported_one_arm_dumbbell_row": {"rowing-haltere-un-bras-paren-banc", "rowing-haltere-un-bras"},
    "cable_rope_face_pull": {"face-pull-cable-paren-corde", "face-pull-cable"},
}


@pytest.mark.parametrize("identity", sorted(SAME_IDENTITY))
def test_operator_merges_share_one_identity_and_one_canonical(by_id, identity):
    members = SAME_IDENTITY[identity]
    assert {_identity(by_id[m]) for m in members} == {identity}
    canonical = [m for m in members if by_id[m]["identity"]["identity_relation"] == "CANONICAL"]
    assert len(canonical) == 1
    for m in members - set(canonical):
        assert by_id[m]["identity"]["alias_of"] == canonical[0]


@pytest.mark.parametrize("a,b", [
    ("triceps-extension-poulie-haute-paren-corde", "extension-overhead-cable-paren-corde"),  # G08
    ("releve-de-jambes-suspendu", "hanging-knee-raise"),                                      # G30
])
def test_distinct_movements_stay_distinct(by_id, a, b):
    assert _identity(by_id[a]) != _identity(by_id[b])


def test_g30_both_hanging_raises_are_legitimate_variants(by_id):
    assert _identity(by_id["releve-de-jambes-suspendu"]) == "hanging_straight_leg_raise"
    assert _identity(by_id["hanging-knee-raise"]) == "hanging_bent_knee_raise"
    for rid in ("releve-de-jambes-suspendu", "hanging-knee-raise"):
        assert by_id[rid]["identity"]["identity_relation"] == "CANONICAL"
        assert by_id[rid]["identity"]["group_classification"] == "LEGITIMATE_VARIANT"


ROPE, BAR = "cable_attachment_rope", "cable_attachment_straight_bar"
REQUIREMENTS = {
    "tirage-poulie-haute-prise-neutre": ["pulldown_seated_station", "cable_attachment_neutral_grip"],
    "pullover-cable-paren-bras-tendus-poulie-haute": ["cable_anchor_high", {"any_of": [ROPE, BAR]}],
    "rowing-haltere-un-bras-paren-banc": ["dumbbells", "flat_bench_support"],
    "hip-thrust-halteres": ["dumbbells", "flat_bench_support"],
    "tirage-vertical-unilateral-cable": ["pulldown_seated_station", "cable_attachment_single_handle"],
    "preacher-curl": ["machine_preacher_curl"],
    "curl-poulie-basse-paren-barre": ["cable_anchor_low", BAR],
    "curl-marteau-cable-paren-corde": ["cable_anchor_low", ROPE],
    "face-pull-cable-paren-corde": ["cable_anchor_adjustable", ROPE],
    "rowing-cable-assis-prise-neutre": ["row_seated_station", "cable_attachment_close_neutral_row_handle"],
    "rowing-cable-assis-prise-serree": ["row_seated_station", "cable_attachment_close_neutral_row_handle"],
}


@pytest.mark.parametrize("rid", sorted(REQUIREMENTS))
def test_operator_equipment_requirements(by_id, rid):
    assert by_id[rid]["exercise_operational"]["equipment_requirements"] == REQUIREMENTS[rid]


def test_wide_grip_seated_row_is_untouched_by_the_close_neutral_ruling(by_id):
    assert by_id["rowing-cable-assis-prise-large"]["exercise_operational"]["equipment_requirements"] == [
        "row_seated_station"]


def test_preacher_curl_is_named_as_the_machine_it_requires(by_id):
    assert by_id["preacher-curl"]["identity"]["canonical_display_name"] == "Preacher curl machine"


# ── content alignment gate (GO BUILD Sb_SCI_V2_01)

CONTENT_MISMATCHES = {"releve-de-jambes-suspendu", "rowing-machine-chest-supported"}


def test_known_served_content_contradictions_are_recorded(by_id):
    flagged = {rid for rid, r in by_id.items() if "content_alignment" in r}
    assert flagged == CONTENT_MISMATCHES
    for rid in CONTENT_MISMATCHES:
        alignment = by_id[rid]["content_alignment"]
        assert alignment["status"] == "CONTENT_EXECUTION_MISMATCH"
        assert alignment["exact_exposure_evidence"] is False
        assert alignment["served_content"], rid


# ── TRAIN A delta proposal: no inferred accessory


def _delta() -> dict:
    return json.loads((SCI / "train_a_delta_proposal.json").read_text(encoding="utf-8"))


def test_delta_grants_no_attachment_to_a_station():
    for addition in _delta().get("item_capability_additions", []):
        assert not any(c.startswith("cable_attachment_") for c in addition["add_capabilities"]), addition


@pytest.mark.parametrize("item_id,capability", [
    ("cable_neutral_grip_handle", "cable_attachment_neutral_grip"),
    ("close_neutral_row_handle", "cable_attachment_close_neutral_row_handle"),
    ("cable_d_handle", "cable_attachment_single_handle"),
])
def test_each_attachment_is_its_own_physical_object(item_id, capability):
    delta = _delta()
    items = {i["item_id"]: i for i in delta["new_items"]}
    assert items[item_id]["capabilities"] == [capability]
    assert capability in delta["new_capabilities"]


def test_the_delta_is_not_applied_to_the_served_registry():
    registry = json.loads((ROOT / "data" / "equipment_registry.json").read_text(encoding="utf-8"))
    served = {c for item in registry["items"] for c in item["capabilities"]}
    for capability in ("cable_attachment_neutral_grip", "cable_attachment_close_neutral_row_handle",
                       "cable_attachment_single_handle"):
        assert capability not in served
