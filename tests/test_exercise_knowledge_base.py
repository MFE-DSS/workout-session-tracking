"""Sb_CUSTOM_PROGRAM_EKB_02 — canonical exercise knowledge base JSON.

Pins the 103-entry canonical EKB derived from the EKB_01 snapshot: byte-exact
names, unique variant keys, the covered/gap split, the alias handling of the 2
orphan properties, the 11-fine-zone / macro-zone reconciliation, and the V1
`variant_group: null` decision. No scoring, no curated fine metadata, no
anatomical claim — those stay in later builds.
"""
from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EKB_FILE = PROJECT_ROOT / "data" / "exercise_knowledge_base.json"
SNAPSHOT_FILE = PROJECT_ROOT / "tests" / "fixtures" / "ekb_names_snapshot.json"
PROPERTIES_FILE = PROJECT_ROOT / "data" / "exercise_properties.json"

# 11 fine zones reconciled to 6 macro zones + core (muscle_mapping.RADAR_AXES).
FINE_TO_MACRO = {
    "pecs": "pecs",
    "delt_lat": "shoulders",
    "delt_post": "shoulders",
    "lats": "back_width",
    "upper_back": "back_thickness",
    "biceps": "arms",
    "triceps": "arms",
    "quads": "lower",
    "posterior": "lower",
    "calves": "lower",
    "core": "core",
}

COVERAGE_STATUSES = {"covered", "gap"}
CONFIDENCE_LEVELS = {"measured", "derived", "todo"}

# Lexique médical interdit (spec 02 §9-7) — l'EKB est opératoire, jamais clinique.
_MEDICAL_LEXICON = (
    "blessure", "pathologie", "douleur", "tendinite", "hernie", "diagnostic",
    "hormonal", "testostérone", "cortisol", "médical", "thérapeutique",
)


def _load_ekb() -> dict:
    return json.loads(EKB_FILE.read_text(encoding="utf-8"))


def _exercises() -> dict:
    return _load_ekb()["exercises"]


# ───────── référentiel : 103 noms byte-à-byte ─────────


def test_exactly_103_entries():
    assert len(_exercises()) == 103


def test_keys_match_snapshot_byte_exact():
    snapshot = json.loads(SNAPSHOT_FILE.read_text(encoding="utf-8"))
    assert sorted(_exercises().keys()) == sorted(snapshot["names"])


def test_no_renaming_canonical_name_equals_key():
    for key, entry in _exercises().items():
        assert entry["canonical_name"] == key


# ───────── variant_key ─────────


def test_variant_key_present_and_unique():
    exercises = _exercises()
    keys = [e["variant_key"] for e in exercises.values()]
    assert all(k for k in keys)
    assert len(set(keys)) == 103


# ───────── variant_group : null V1 ─────────


def test_variant_group_null_in_v1():
    assert all(e["variant_group"] is None for e in _exercises().values())


# ───────── couverture 51 / 52 ─────────


def test_coverage_split_51_covered_52_gap():
    exercises = _exercises()
    covered = [e for e in exercises.values() if e["coverage_status"] == "covered"]
    gaps = [e for e in exercises.values() if e["coverage_status"] == "gap"]
    assert len(covered) == 51
    assert len(gaps) == 52


def test_covered_entries_consistent_with_properties():
    props = json.loads(PROPERTIES_FILE.read_text(encoding="utf-8"))["exercises"]
    for name, entry in _exercises().items():
        if entry["coverage_status"] == "covered":
            assert name in props
            assert entry["movement_pattern"] == props[name]["pattern_motor"]
            assert entry["chain"] == props[name]["chain"]
            assert entry["properties_source"]


def test_covered_status_matches_properties_membership():
    props = json.loads(PROPERTIES_FILE.read_text(encoding="utf-8"))["exercises"]
    for name, entry in _exercises().items():
        expected = "covered" if name in props else "gap"
        assert entry["coverage_status"] == expected


def test_gaps_remain_explicitly_marked():
    props = json.loads(PROPERTIES_FILE.read_text(encoding="utf-8"))["exercises"]
    for name, entry in _exercises().items():
        if name not in props:
            assert entry["coverage_status"] == "gap"
            # un gap n'a jamais de movement_pattern/chain inventé (source = properties)
            assert entry["movement_pattern"] is None
            assert entry["chain"] is None


def test_blackholes_stay_visible_not_masked():
    # les 19 trous noirs : gap SANS zone, SANS machine, SANS equipment → todo
    blackholes = [
        name
        for name, e in _exercises().items()
        if e["coverage_status"] == "gap"
        and not e["zone_primary"]
        and not e["machine_slug"]
        and not e["equipment_family"]
    ]
    assert len(blackholes) == 19
    for name in blackholes:
        assert _exercises()[name]["confidence"] == "todo"


# ───────── alias des 2 orphelines ─────────


def test_two_orphan_aliases_recorded():
    aliases = _load_ekb()["_aliases"]
    assert set(aliases) == {"Incline DB Press 30°", "Incline Dumbbell Press"}


def test_each_alias_points_to_existing_canonical_name():
    ekb = _load_ekb()
    names = set(ekb["exercises"])
    for source, target in ekb["_aliases"].items():
        assert target in names


def test_aliases_are_never_ekb_entries():
    ekb = _load_ekb()
    for source in ekb["_aliases"]:
        assert source not in ekb["exercises"]


# ───────── zones ─────────


def test_zone_primary_in_eleven_fine_zones():
    for entry in _exercises().values():
        if entry["zone_primary"] is not None:
            assert entry["zone_primary"] in FINE_TO_MACRO


def test_zone_macro_derived_from_zone_primary():
    for entry in _exercises().values():
        if entry["zone_primary"] is not None:
            assert entry["zone_macro"] == FINE_TO_MACRO[entry["zone_primary"]]
        else:
            assert entry["zone_macro"] is None


# ───────── enums fermés ─────────


def test_closed_enums_coverage_and_confidence():
    for entry in _exercises().values():
        assert entry["coverage_status"] in COVERAGE_STATUSES
        assert entry["confidence"] in CONFIDENCE_LEVELS


# ───────── non-médical ─────────


def test_no_medical_lexicon_in_ekb():
    blob = EKB_FILE.read_text(encoding="utf-8").lower()
    hits = [w for w in _MEDICAL_LEXICON if w in blob]
    assert not hits, f"lexique médical interdit présent: {hits}"


# ───────── non-régression EKB_01 ─────────


def test_ekb01_coverage_audit_still_green():
    from scripts.ekb_coverage_qa import run_audit

    report = run_audit()
    assert not report["errors"]
    assert report["canonical_count"] == 103


def test_alembic_head_unchanged():
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    script = ScriptDirectory.from_config(Config(str(PROJECT_ROOT / "alembic.ini")))
    # EKB_02 est data-only ; le head a ensuite avancé avec SCORING_03
    # (migration additive `o6p1j7k8m09` : 3 colonnes runtime sur
    # user_program_quality_reviews). Cette sentinelle suit le head courant.
    assert script.get_current_head() == "o6p1j7k8m09"
