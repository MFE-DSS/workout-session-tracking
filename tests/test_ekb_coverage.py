"""Sb_CUSTOM_PROGRAM_EKB_01 — EKB coverage audit (read-only).

Pins the canonical exercise-name referential (103 names, byte-for-byte),
the measured coverage state of exercise_properties.json (52 gaps, 2 orphan
entries), the substitution closures, and the audit script's determinism.
No knowledge base is created here — EKB_02 owns the canonical JSON.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.ekb_coverage_qa import (
    BASELINE_FILE,
    BRIDGES_FILE,
    PROJECT_ROOT,
    PROPERTIES_FILE,
    REFERENCE_SPLIT_FILE,
    SNAPSHOT_FILE,
    extract_names,
    main,
    run_audit,
)

SOURCE_FILES = (REFERENCE_SPLIT_FILE, PROPERTIES_FILE, BRIDGES_FILE, BASELINE_FILE)

# Liste EXACTE des 52 noms du catalogue sans entrée properties (état mesuré
# Sb_22a.v1.1 — c'est le travail d'EKB_02 de la faire tomber à 0).
EXPECTED_GAPS = [
    "Back extension 45° (bias ischios)",
    "Butterfly pec machine",
    "Cable cross-over (bas→haut)",
    "Calf press leg press",
    "Crunch câble à genoux",
    "Decline crunch",
    "Face pull câble",
    "Face pull câble (corde)",
    "Good morning haltères",
    "Hack Squat machine",
    "Hanging knee raise",
    "Hip thrust Smith",
    "Hip thrust Smith machine",
    "Hip thrust haltères",
    "Leg Press (pieds bas)",
    "Leg Press (pieds bas, serrés)",
    "Leg Press (pieds hauts, écartés)",
    "Machine crunch",
    "Mollets assis machine",
    "Mollets debout machine",
    "Pallof press câble",
    "Pullover câble (bras tendus)",
    "Pullover câble (bras tendus, poulie haute)",
    "Pullover machine",
    "Pushdown corde",
    "Rear delt fly machine",
    "Rear delt fly machine (pec deck inversé)",
    "Relevé de jambes suspendu",
    "Relevés mollets debout",
    "Relevés mollets debout machine",
    "Reverse fly machine",
    "Romanian Deadlift barre",
    "Romanian Deadlift haltères",
    "Roulette abdominale",
    "Roulette abdominale (ab wheel rollout)",
    "Shrugs barre",
    "Shrugs câble",
    "Shrugs haltères",
    "Sissy squat machine",
    "Skull crushers EZ-bar",
    "Squat Smith machine (pieds avancés)",
    "Tirage front câble (prise large)",
    "Upright row câble",
    "Upright row haltères",
    "Y-raise haltère",
    "Écarté arrière d'épaule câble",
    "Écarté pec aux câbles (incliné bas→haut)",
    "Élévations latérales câble",
    "Élévations latérales câble (derrière le dos)",
    "Élévations latérales haltères",
    "Élévations latérales haltères assis",
    "Élévations latérales machine",
]

# Entrées properties sans nom au catalogue (anciennes graphies non renommées
# — on les CONSTATE, on ne corrige ni ne renomme rien en EKB_01).
EXPECTED_ORPHANS = ["Incline DB Press 30°", "Incline Dumbbell Press"]


def _hashes() -> dict[Path, str]:
    return {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCE_FILES}


# ───────── référentiel canonique ─────────


def test_live_extraction_matches_committed_snapshot():
    snapshot = json.loads(SNAPSHOT_FILE.read_text(encoding="utf-8"))
    report = run_audit()
    assert snapshot["names"] == report["canonical_names"]
    assert snapshot["count"] == len(snapshot["names"])
    assert snapshot["source_version"] == report["source_version"]


def test_exactly_103_unique_canonical_names():
    report = run_audit()
    assert report["canonical_count"] == 103
    assert len(report["canonical_names"]) == 103


def test_exactly_65_prescribed_and_59_substitutes():
    split = json.loads(REFERENCE_SPLIT_FILE.read_text(encoding="utf-8"))
    extraction = extract_names(split)
    assert len(extraction["prescribed"]) == 65
    assert len(extraction["substitutes"]) == 59
    # 65 + 59 − 21 (overlap) = 103 — la somme est cohérente par construction
    assert extraction["templates"] == 16
    assert extraction["slots"] == 98


def test_names_are_unique_sorted_and_byte_exact():
    report = run_audit()
    names = report["canonical_names"]
    assert len(names) == len(set(names))
    assert names == sorted(names)
    assert all(name == name.strip() and name for name in names)


# ───────── couverture properties ─────────


def test_gaps_are_exactly_the_52_known_missing_names():
    report = run_audit()
    assert report["gaps"] == EXPECTED_GAPS
    assert len(report["gaps"]) == 52
    assert report["covered_count"] == 51
    assert report["properties_count"] == 53


def test_orphan_properties_are_exactly_the_2_known_entries():
    report = run_audit()
    assert report["orphan_properties"] == EXPECTED_ORPHANS


# ───────── clôtures ─────────


def test_n1_substitutes_closed_over_referential():
    split = json.loads(REFERENCE_SPLIT_FILE.read_text(encoding="utf-8"))
    extraction = extract_names(split)
    assert set(extraction["substitutes"]) <= set(extraction["canonical"])


def test_n3_bridges_closed_over_referential():
    report = run_audit()
    assert report["bridge_names"]  # les 2 bridges citent bien des noms
    assert len(report["bridge_names"]) == 12
    assert set(report["bridge_names"]) <= set(report["canonical_names"])
    assert not report["errors"]


def test_baseline_coherence_without_inventing_mappings():
    report = run_audit()
    # La baseline Sx_32 reste la référence de classification : ses noms
    # appartiennent tous au référentiel, et l'audit n'invente AUCUN mapping
    # (aucune clé de zone/muscle dans le rapport).
    assert report["baseline_entries"] == 91
    assert report["baseline_unique_names"] == 65
    baseline = json.loads(BASELINE_FILE.read_text(encoding="utf-8"))
    names = {entry["name"] for entry in baseline["entries"]}
    assert names <= set(report["canonical_names"])
    assert not any("zone" in key or "muscle" in key for key in report)


# ───────── déterminisme et innocuité du script ─────────


def test_audit_is_deterministic_across_two_runs():
    assert run_audit() == run_audit()


def test_script_never_mutates_its_sources(capsys):
    before = _hashes()
    assert main([]) == 0
    capsys.readouterr()
    assert _hashes() == before


def test_exit_code_zero_on_current_tree_and_output_readable(capsys):
    assert main([]) == 0
    out = capsys.readouterr().out
    assert "RÉFÉRENTIEL CANONIQUE: 103 noms uniques" in out
    assert "OK: toutes les invariances tiennent." in out


def test_write_snapshot_refuses_data_dir(tmp_path):
    import pytest

    from scripts.ekb_coverage_qa import write_snapshot

    report = run_audit()
    with pytest.raises(ValueError, match="data/"):
        write_snapshot(PROJECT_ROOT / "data" / "interdit.json", report)
    target = tmp_path / "snap.json"
    write_snapshot(target, report)
    written = json.loads(target.read_text(encoding="utf-8"))
    assert written["names"] == report["canonical_names"]
