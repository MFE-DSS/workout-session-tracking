"""Sb_CUSTOM_PROGRAM_EKB_03 — EKB classifiability QA.

Pins the 8 spec-§9 checks over the canonical EKB JSON: green on the live EKB
(only the expected frozen-counter warnings), and RED on each controlled breakage
(renamed name, deleted entry, duplicate variant_key, incomplete covered, extra
gap, extra black hole, broken alias, alias promoted to entry, medical lexicon,
broken substitution, incoherent variant_group). Read-only, no data mutated.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

from scripts import ekb_classifiability_qa as qa

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EKB_FILE = PROJECT_ROOT / "data" / "exercise_knowledge_base.json"
SNAPSHOT_FILE = PROJECT_ROOT / "tests" / "fixtures" / "ekb_names_snapshot.json"


def _ekb() -> dict:
    return json.loads(EKB_FILE.read_text(encoding="utf-8"))


def _snapshot() -> dict:
    return json.loads(SNAPSHOT_FILE.read_text(encoding="utf-8"))


def _run_all(ekb: dict, snapshot: dict) -> tuple[list[str], list[str]]:
    """Rejoue tous les checks sur des objets en mémoire (sans toucher au disque)."""
    errors: list[str] = []
    warnings: list[str] = []
    for check in qa.CHECKS:
        e, w = check(ekb, snapshot)
        errors.extend(e)
        warnings.extend(w)
    return errors, warnings


def _first_covered(ekb: dict) -> str:
    return next(k for k, v in ekb["exercises"].items() if v["coverage_status"] == "covered")


def _first_gap(ekb: dict) -> str:
    return next(k for k, v in ekb["exercises"].items() if v["coverage_status"] == "gap")


# ───────── succès sur l'EKB réel ─────────


def test_live_ekb_has_no_errors_and_exits_zero():
    errors, warnings = qa.run_qa()
    assert errors == []
    assert warnings  # les warnings à compteur figé sont attendues
    assert qa.main() == 0


def test_expected_frozen_counters():
    assert qa.EXPECTED_TOTAL == 103
    assert qa.EXPECTED_COVERED == 51
    assert qa.EXPECTED_GAP == 52
    assert qa.EXPECTED_BLACKHOLES == 19


# ───────── cassures contrôlées → ERREUR ─────────


def test_renamed_name_is_error():
    ekb = _ekb()
    key = _first_covered(ekb)
    entry = ekb["exercises"].pop(key)
    entry["canonical_name"] = key + " RENOMMÉ"
    ekb["exercises"][key + " RENOMMÉ"] = entry
    errors, _ = _run_all(ekb, _snapshot())
    assert any("invariance" in e for e in errors)


def test_deleted_entry_is_error():
    ekb = _ekb()
    del ekb["exercises"][_first_covered(ekb)]
    errors, _ = _run_all(ekb, _snapshot())
    assert any("couverture" in e or "invariance" in e for e in errors)


def test_duplicate_variant_key_is_error():
    ekb = _ekb()
    keys = list(ekb["exercises"])
    ekb["exercises"][keys[1]]["variant_key"] = ekb["exercises"][keys[0]]["variant_key"]
    errors, _ = _run_all(ekb, _snapshot())
    assert any("unicité" in e and "variant_key" in e for e in errors)


def test_covered_without_pattern_is_error():
    ekb = _ekb()
    ekb["exercises"][_first_covered(ekb)]["movement_pattern"] = None
    errors, _ = _run_all(ekb, _snapshot())
    assert any("complétude" in e for e in errors)


def test_extra_gap_drifts_counter_and_is_error():
    ekb = _ekb()
    # bascule un covered en gap → gaps=53, dérive du compteur figé
    ekb["exercises"][_first_covered(ekb)]["coverage_status"] = "gap"
    errors, _ = _run_all(ekb, _snapshot())
    assert any("couverture" in e and "figé" in e for e in errors)


def test_extra_blackhole_drifts_counter_and_is_error():
    ekb = _ekb()
    # vide un gap déjà dérivé pour créer un trou noir surnuméraire (20 au lieu de 19)
    for k, v in ekb["exercises"].items():
        if v["coverage_status"] == "gap" and (v["zone_primary"] or v["machine_slug"] or v["equipment_family"]):
            v["zone_primary"] = None
            v["zone_macro"] = None
            v["machine_slug"] = None
            v["machine_family"] = None
            v["equipment_family"] = None
            break
    errors, _ = _run_all(ekb, _snapshot())
    assert any("trous noirs" in e and "figé" in e for e in errors)


def test_broken_alias_target_is_error():
    ekb = _ekb()
    src = next(iter(ekb["_aliases"]))
    ekb["_aliases"][src] = "Exercice qui n'existe pas"
    errors, _ = _run_all(ekb, _snapshot())
    assert any("alias" in e and "inconnue" in e for e in errors)


def test_alias_promoted_to_entry_is_error():
    ekb = _ekb()
    src = next(iter(ekb["_aliases"]))
    # l'alias devient aussi une entrée EKB → interdit
    ekb["exercises"][src] = copy.deepcopy(next(iter(ekb["exercises"].values())))
    ekb["exercises"][src]["canonical_name"] = src
    errors, _ = _run_all(ekb, _snapshot())
    assert any("alias" in e and "entrée EKB" in e for e in errors)


def test_medical_lexicon_is_error():
    ekb = _ekb()
    ekb["exercises"][_first_covered(ekb)]["curation_note"] = "prévient la tendinite"
    errors, _ = _run_all(ekb, _snapshot())
    assert any("non-médical" in e for e in errors)


def test_broken_substitution_closure_is_error():
    ekb = _ekb()
    # retire une entrée réellement citée comme substitut/bridge tout en gardant
    # le compteur cohérent ailleurs : on force un nom cité hors référentiel
    # en supprimant un alias vers lequel un substitut pourrait pointer.
    # Plus simple et robuste : vider _aliases ET retirer une entrée citée.
    # On cible un nom présent dans les bridges.
    bridges = json.loads((PROJECT_ROOT / "data" / "cross_pattern_substitutions.json").read_text(encoding="utf-8"))
    cited = bridges["bridges"][0]["exercises_from"][0]
    if cited in ekb["exercises"]:
        del ekb["exercises"][cited]
    errors, _ = _run_all(ekb, _snapshot())
    assert any("substitution" in e for e in errors)


def test_incoherent_variant_group_is_error():
    ekb = _ekb()
    keys = list(ekb["exercises"])
    a, b = keys[0], keys[1]
    ekb["exercises"][a]["variant_group"] = "grp-test"
    ekb["exercises"][a]["movement_pattern"] = "push_horizontal"
    ekb["exercises"][b]["variant_group"] = "grp-test"
    ekb["exercises"][b]["movement_pattern"] = "pull_vertical"
    errors, _ = _run_all(ekb, _snapshot())
    assert any("groupe" in e for e in errors)


# ───────── non-régression EKB_01 / EKB_02 ─────────


def test_ekb01_and_ekb02_still_green():
    from scripts.ekb_coverage_qa import run_audit

    assert not run_audit()["errors"]
    assert qa.run_qa()[0] == []
