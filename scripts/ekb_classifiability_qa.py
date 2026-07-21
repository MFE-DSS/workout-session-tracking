"""EKB classifiability QA — CI-able validation of the canonical EKB JSON.

Sb_CUSTOM_PROGRAM_EKB_03 (spec Sx_CUSTOM_PROGRAM_02 §9/§14). Consolidates the
8 QA checks of the spec over `data/exercise_knowledge_base.json` (EKB_02) into a
single exit-code script, on the `catalog_qa.py` pattern (errors → exit 1,
expected warnings → exit 0).

Doctrine (arbitrage EKB_03) :
- INVARIANCES = ERREURS DURES (exit 1) : noms byte-à-byte vs snapshot, unicité
  canonical_name/variant_key, complétude des `covered`, clôture des
  substitutions, alias bien formés, non-médical, traçabilité, cohérence de
  groupe.
- GAPS DE CURATION = WARNINGS À COMPTEUR FIGÉ (exit 0) : les 52 gaps et 19 trous
  noirs sont l'état délibéré livré par EKB_02. On les rapporte sans échouer —
  MAIS toute DÉRIVE du compteur attendu (un covered qui régresse, un gap ou un
  trou noir surnuméraire) devient une ERREUR. On verrouille l'état, on n'exige
  aucune curation non encore faite (curation = build ultérieur).

Lecture SEULE. N'écrit jamais dans data/.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

EKB_FILE = PROJECT_ROOT / "data" / "exercise_knowledge_base.json"
SNAPSHOT_FILE = PROJECT_ROOT / "tests" / "fixtures" / "ekb_names_snapshot.json"
REFERENCE_SPLIT_FILE = PROJECT_ROOT / "data" / "reference_split.json"
BRIDGES_FILE = PROJECT_ROOT / "data" / "cross_pattern_substitutions.json"

# Compteurs figés (état EKB_02 livré). Toute dérive = erreur.
EXPECTED_TOTAL = 103
EXPECTED_COVERED = 51
EXPECTED_GAP = 52
EXPECTED_BLACKHOLES = 19

# 11 zones fines réconciliées (RADAR_AXES) — vocabulaire fermé.
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

# Lexique médical interdit (spec §9-7) — l'EKB est opératoire, jamais clinique.
MEDICAL_LEXICON = (
    "blessure", "pathologie", "tendinite", "hernie", "diagnostic",
    "hormonal", "testostérone", "cortisol", "thérapeutique",
)


def _load(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


# ─────────────────────────── checks ───────────────────────────
# Chaque check retourne (errors: list[str], warnings: list[str]).


def check_coverage(ekb: dict, snapshot: dict) -> tuple[list[str], list[str]]:
    """Check 1 (§9) : chaque nom du snapshot a une entrée ; compteur de gaps figé."""
    errors: list[str] = []
    warnings: list[str] = []
    exercises = ekb["exercises"]
    names = set(snapshot["names"])
    missing = sorted(names - set(exercises))
    extra = sorted(set(exercises) - names)
    for name in missing:
        errors.append(f"[couverture] nom du snapshot sans entrée EKB : {name!r}")
    for name in extra:
        errors.append(f"[couverture] entrée EKB hors snapshot : {name!r}")
    if len(exercises) != EXPECTED_TOTAL:
        errors.append(
            f"[couverture] total {len(exercises)} != {EXPECTED_TOTAL} attendu"
        )
    gaps = [k for k, v in exercises.items() if v["coverage_status"] == "gap"]
    if len(gaps) != EXPECTED_GAP:
        errors.append(
            f"[couverture] gaps={len(gaps)} != compteur figé {EXPECTED_GAP} "
            "(dérive : régression d'un covered ou gap surnuméraire)"
        )
    else:
        warnings.append(
            f"[couverture] {EXPECTED_GAP} gaps de curation (état EKB_02 délibéré, "
            "curation = build ultérieur)"
        )
    return errors, warnings


def check_substitution_closure(ekb: dict, snapshot: dict) -> tuple[list[str], list[str]]:
    """Check 2 (§9) : chaque nom cité par substitutes / bridges pointe vers une
    entrée EKB (ou un alias vers une entrée)."""
    errors: list[str] = []
    exercises = set(ekb["exercises"])
    aliases = set(ekb.get("_aliases", {}))
    known = exercises | aliases
    refsplit = _load(REFERENCE_SPLIT_FILE)
    bridges = _load(BRIDGES_FILE)
    cited: set[str] = set()
    for tpl in refsplit["templates"]:
        for slot in tpl["exercises"]:
            cited.update(slot.get("substitutes", []))
    for bridge in bridges["bridges"]:
        cited.update(bridge["exercises_from"] + bridge["exercises_to"])
    for name in sorted(cited - known):
        errors.append(
            f"[substitution] nom cité sans entrée EKB ni alias connu : {name!r}"
        )
    return errors, []


def check_completeness(ekb: dict, snapshot: dict) -> tuple[list[str], list[str]]:
    """Check 3 (§9) : les `covered` ont movement_pattern/equipment_family/
    zone_primary ; les gaps incomplets = warnings quantifiés."""
    errors: list[str] = []
    warnings: list[str] = []
    for name, e in ekb["exercises"].items():
        if e["coverage_status"] == "covered":
            for field in ("movement_pattern", "equipment_family"):
                if not e.get(field):
                    errors.append(
                        f"[complétude] covered {name!r} sans {field}"
                    )
    gaps_without_zone = sum(
        1
        for e in ekb["exercises"].values()
        if e["coverage_status"] == "gap" and not e["zone_primary"]
    )
    warnings.append(
        f"[complétude] {gaps_without_zone} gaps sans zone dérivable "
        "(curation différée)"
    )
    return errors, warnings


def check_name_invariance(ekb: dict, snapshot: dict) -> tuple[list[str], list[str]]:
    """Check 4 (§9) : aucun nom renommé — canonical_name == clé, byte-à-byte,
    et l'ensemble == snapshot (invariance #1)."""
    errors: list[str] = []
    for key, e in ekb["exercises"].items():
        if e["canonical_name"] != key:
            errors.append(
                f"[invariance] canonical_name {e['canonical_name']!r} != clé {key!r}"
            )
    if sorted(ekb["exercises"]) != sorted(snapshot["names"]):
        errors.append("[invariance] ensemble des noms != snapshot opposable EKB_01")
    return errors, []


def check_uniqueness(ekb: dict, snapshot: dict) -> tuple[list[str], list[str]]:
    """Check 5 (§9) : canonical_name et variant_key uniques."""
    errors: list[str] = []
    keys = list(ekb["exercises"])
    if len(keys) != len(set(keys)):
        errors.append("[unicité] canonical_name dupliqué")
    vkeys = [e["variant_key"] for e in ekb["exercises"].values()]
    seen: set[str] = set()
    for vk in vkeys:
        if not vk:
            errors.append("[unicité] variant_key vide")
        elif vk in seen:
            errors.append(f"[unicité] variant_key dupliqué : {vk!r}")
        seen.add(vk)
    return errors, []


def check_group_coherence(ekb: dict, snapshot: dict) -> tuple[list[str], list[str]]:
    """Check 6 (§9) : toute entrée d'un même variant_group partage
    movement_pattern et zone_primary. V1 : variant_group null → vacuously true ;
    le check mord dès qu'un groupe est peuplé (build de curation futur)."""
    errors: list[str] = []
    warnings: list[str] = []
    groups: dict[str, list] = {}
    for name, e in ekb["exercises"].items():
        g = e.get("variant_group")
        if g is not None:
            groups.setdefault(g, []).append((name, e))
    if not groups:
        warnings.append(
            "[groupe] variant_group null partout (V1) — cohérence vacuously true"
        )
    for g, members in groups.items():
        patterns = {e["movement_pattern"] for _, e in members}
        zones = {e["zone_primary"] for _, e in members}
        if len(patterns) > 1:
            errors.append(
                f"[groupe] {g!r} : movement_pattern hétérogènes {patterns}"
            )
        if len(zones) > 1:
            errors.append(f"[groupe] {g!r} : zone_primary hétérogènes {zones}")
    return errors, warnings


def check_non_medical(ekb: dict, snapshot: dict) -> tuple[list[str], list[str]]:
    """Check 7 (§9) : aucun claim médical dans le JSON."""
    errors: list[str] = []
    blob = json.dumps(ekb, ensure_ascii=False).lower()
    for word in MEDICAL_LEXICON:
        if word in blob:
            errors.append(f"[non-médical] lexique interdit présent : {word!r}")
    return errors, []


def check_traceability(ekb: dict, snapshot: dict) -> tuple[list[str], list[str]]:
    """Check 8 (§9) : confidence renseigné et fermé ; coverage_status fermé ;
    zones dans le vocabulaire ; compteur de trous noirs figé."""
    errors: list[str] = []
    warnings: list[str] = []
    for name, e in ekb["exercises"].items():
        if e.get("confidence") not in CONFIDENCE_LEVELS:
            errors.append(f"[traçabilité] {name!r} confidence invalide : {e.get('confidence')!r}")
        if e.get("coverage_status") not in COVERAGE_STATUSES:
            errors.append(f"[traçabilité] {name!r} coverage_status invalide")
        zp = e.get("zone_primary")
        if zp is not None and zp not in FINE_TO_MACRO:
            errors.append(f"[traçabilité] {name!r} zone_primary hors vocabulaire : {zp!r}")
        if zp is not None and e.get("zone_macro") != FINE_TO_MACRO[zp]:
            errors.append(f"[traçabilité] {name!r} zone_macro non dérivée de zone_primary")
    blackholes = [
        name
        for name, e in ekb["exercises"].items()
        if e["coverage_status"] == "gap"
        and not e["zone_primary"]
        and not e["machine_slug"]
        and not e["equipment_family"]
    ]
    if len(blackholes) != EXPECTED_BLACKHOLES:
        errors.append(
            f"[traçabilité] trous noirs={len(blackholes)} != compteur figé "
            f"{EXPECTED_BLACKHOLES} (dérive)"
        )
    else:
        warnings.append(
            f"[traçabilité] {EXPECTED_BLACKHOLES} trous noirs (confidence=todo, "
            "curation différée)"
        )
    return errors, warnings


def check_aliases(ekb: dict, snapshot: dict) -> tuple[list[str], list[str]]:
    """Alias (§4/§14 EKB_02) : chaque alias pointe vers une entrée canonique
    existante et n'est jamais lui-même une entrée EKB."""
    errors: list[str] = []
    names = set(snapshot["names"])
    exercises = set(ekb["exercises"])
    for source, target in ekb.get("_aliases", {}).items():
        if target not in names:
            errors.append(f"[alias] {source!r} → cible inconnue {target!r}")
        if source in exercises:
            errors.append(f"[alias] {source!r} est aussi une entrée EKB (interdit)")
    return errors, []


# Toutes les fonctions partagent la signature (ekb, snapshot) — les checks
# qui n'utilisent pas le snapshot l'ignorent (signature uniforme volontaire).
CHECKS = (
    check_coverage,
    check_substitution_closure,
    check_completeness,
    check_name_invariance,
    check_uniqueness,
    check_group_coherence,
    check_non_medical,
    check_traceability,
    check_aliases,
)


def run_qa() -> tuple[list[str], list[str]]:
    """Exécute tous les checks read-only ; retourne (errors, warnings)."""
    ekb = _load(EKB_FILE)
    snapshot = _load(SNAPSHOT_FILE)
    errors: list[str] = []
    warnings: list[str] = []
    for check in CHECKS:
        e, w = check(ekb, snapshot)
        errors.extend(e)
        warnings.extend(w)
    return errors, warnings


def render(errors: list[str], warnings: list[str]) -> str:
    lines = [
        "=== EKB classifiability QA (Sb_CUSTOM_PROGRAM_EKB_03) ===",
        f"SUMMARY : {len(errors)} erreur(s), {len(warnings)} warning(s) attendue(s)",
    ]
    if errors:
        lines.append("--- ERRORS ---")
        lines.extend(f"  ✗ {e}" for e in errors)
    if warnings:
        lines.append("--- WARNINGS (attendues, compteur figé) ---")
        lines.extend(f"  · {w}" for w in warnings)
    if not errors:
        lines.append("OK : toutes les invariances tiennent (warnings attendues).")
    return "\n".join(lines)


def main() -> int:
    errors, warnings = run_qa()
    print(render(errors, warnings))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
