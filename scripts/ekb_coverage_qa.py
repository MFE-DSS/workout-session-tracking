"""EKB Coverage QA — read-only audit of the exercise name referential.

Sb_CUSTOM_PROGRAM_EKB_01 (spec Sx_CUSTOM_PROGRAM_02 §14). First EKB build:
no knowledge base is created here — this script only EXTRACTS the canonical
exercise-name referential from the existing catalog and MEASURES the state
the future canonical EKB JSON (EKB_02) must cover.

Reads ONLY (never writes, except --write-snapshot to an explicit non-data path):
  - data/reference_split.json              (prescribed names + N1 substitutes)
  - data/exercise_properties.json          (Sb_22a properties, partial coverage)
  - data/cross_pattern_substitutions.json  (N3 bridges)
  - tests/fixtures/classify_exercise_baseline.json (Sx_32 classification baseline)
  - tests/fixtures/ekb_names_snapshot.json (committed referential snapshot)

Exit code 1 when an INVARIANCE breaks (extraction anomaly, closure violation,
snapshot drift); 0 otherwise. Coverage gaps and orphan properties are the
measured, known state — they are REPORTED, never failures (closing them is
EKB_02's job, not this audit's).

Names are treated byte-for-byte: no trim, no case folding, no renaming —
invariance of historical names is contract #1 of the track.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

REFERENCE_SPLIT_FILE = PROJECT_ROOT / "data" / "reference_split.json"
PROPERTIES_FILE = PROJECT_ROOT / "data" / "exercise_properties.json"
BRIDGES_FILE = PROJECT_ROOT / "data" / "cross_pattern_substitutions.json"
BASELINE_FILE = (
    PROJECT_ROOT / "tests" / "fixtures" / "classify_exercise_baseline.json"
)
SNAPSHOT_FILE = PROJECT_ROOT / "tests" / "fixtures" / "ekb_names_snapshot.json"


def _load(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def extract_names(reference_split: dict) -> dict:
    """Deterministic extraction of the canonical name referential.

    Returns sorted (codepoint order) lists — the union of prescribed names
    and curated N1 substitutes is the opposable referential.
    """
    prescribed: set[str] = set()
    substitutes: set[str] = set()
    slots = 0
    for template in reference_split["templates"]:
        for exercise in template["exercises"]:
            slots += 1
            prescribed.add(exercise["name"])
            for sub in exercise.get("substitutes", []):
                substitutes.add(sub)
    return {
        "templates": len(reference_split["templates"]),
        "slots": slots,
        "prescribed": sorted(prescribed),
        "substitutes": sorted(substitutes),
        "canonical": sorted(prescribed | substitutes),
    }


def compute_report(
    reference_split: dict,
    properties: dict,
    bridges_doc: dict,
    baseline: dict,
    snapshot: dict | None,
) -> dict:
    """Full audit report: metrics, gaps, closures, invariance errors."""
    extraction = extract_names(reference_split)
    canonical = extraction["canonical"]
    canonical_set = set(canonical)
    prop_names = sorted(properties["exercises"])
    prop_set = set(prop_names)

    bridge_names = sorted(
        {
            name
            for bridge in bridges_doc["bridges"]
            for name in bridge["exercises_from"] + bridge["exercises_to"]
        }
    )
    baseline_entries = baseline["entries"]
    baseline_names = sorted({entry["name"] for entry in baseline_entries})

    errors: list[str] = []

    for name in canonical:
        if not isinstance(name, str) or not name:
            errors.append(f"nom vide ou non-string extrait: {name!r}")
        elif name != name.strip():
            errors.append(f"nom avec espaces de bord (anomalie catalogue): {name!r}")

    # Clôture N1 : vraie par construction (le référentiel inclut les
    # substituts) — l'assert pinne la construction elle-même.
    n1_outside = sorted(set(extraction["substitutes"]) - canonical_set)
    if n1_outside:
        errors.append(f"substituts N1 hors référentiel: {n1_outside}")

    bridges_outside = sorted(set(bridge_names) - canonical_set)
    if bridges_outside:
        errors.append(f"noms de bridges N3 hors référentiel: {bridges_outside}")

    baseline_outside = sorted(set(baseline_names) - canonical_set)
    if baseline_outside:
        errors.append(f"noms de la baseline hors référentiel: {baseline_outside}")
    if baseline["count"] != len(baseline_entries):
        errors.append(
            f"baseline incohérente: count={baseline['count']} "
            f"vs {len(baseline_entries)} entrées"
        )

    if snapshot is not None and snapshot["names"] != canonical:
        added = sorted(canonical_set - set(snapshot["names"]))
        removed = sorted(set(snapshot["names"]) - canonical_set)
        errors.append(
            "DRIFT snapshot vs extraction live — "
            f"ajoutés: {added} · disparus: {removed}"
        )

    gaps = sorted(canonical_set - prop_set)
    orphans = sorted(prop_set - canonical_set)

    return {
        "source_version": reference_split["version"],
        "properties_version": properties["_version"],
        "templates": extraction["templates"],
        "slots": extraction["slots"],
        "prescribed_count": len(extraction["prescribed"]),
        "substitutes_count": len(extraction["substitutes"]),
        "canonical_count": len(canonical),
        "overlap_count": len(set(extraction["prescribed"]) & set(extraction["substitutes"])),
        "canonical_names": canonical,
        "properties_count": len(prop_names),
        "covered_count": len(canonical_set & prop_set),
        "gaps": gaps,
        "orphan_properties": orphans,
        "bridge_names": bridge_names,
        "baseline_entries": len(baseline_entries),
        "baseline_unique_names": len(baseline_names),
        "snapshot_checked": snapshot is not None,
        "errors": errors,
    }


def run_audit() -> dict:
    """Load every source read-only and compute the report."""
    snapshot = _load(SNAPSHOT_FILE) if SNAPSHOT_FILE.exists() else None
    return compute_report(
        _load(REFERENCE_SPLIT_FILE),
        _load(PROPERTIES_FILE),
        _load(BRIDGES_FILE),
        _load(BASELINE_FILE),
        snapshot,
    )


def render_report(report: dict) -> str:
    lines = [
        "=== EKB coverage audit (Sb_CUSTOM_PROGRAM_EKB_01) ===",
        f"catalogue {report['source_version']} · "
        f"properties {report['properties_version']}",
        f"templates: {report['templates']} · slots: {report['slots']}",
        f"noms prescrits: {report['prescribed_count']} · "
        f"substituts N1 distincts: {report['substitutes_count']} · "
        f"overlap: {report['overlap_count']}",
        f"RÉFÉRENTIEL CANONIQUE: {report['canonical_count']} noms uniques",
        f"couverture properties: {report['covered_count']}/"
        f"{report['canonical_count']} "
        f"(gaps: {len(report['gaps'])}, à couvrir par EKB_02)",
        f"properties orphelines (hors catalogue): "
        f"{len(report['orphan_properties'])} {report['orphan_properties']}",
        f"clôture bridges N3: {len(report['bridge_names'])} noms cités, "
        f"tous dans le référentiel: {not report['errors']}",
        f"baseline classification: {report['baseline_entries']} entrées / "
        f"{report['baseline_unique_names']} noms uniques (⊆ référentiel)",
        f"snapshot vérifié: {report['snapshot_checked']}",
    ]
    if report["gaps"]:
        lines.append("--- gaps properties (noms sans entrée) ---")
        lines.extend(f"  · {name}" for name in report["gaps"])
    if report["errors"]:
        lines.append("--- ERREURS D'INVARIANCE ---")
        lines.extend(f"  ✗ {err}" for err in report["errors"])
    else:
        lines.append("OK: toutes les invariances tiennent.")
    return "\n".join(lines)


def write_snapshot(path: Path, report: dict) -> None:
    """Write the referential snapshot to an explicit path — never under data/."""
    resolved = path.resolve()
    if (PROJECT_ROOT / "data") in resolved.parents:
        raise ValueError("refus d'écrire sous data/ (contrat EKB_01)")
    payload = {
        "_doc": (
            "Snapshot opposable du référentiel de noms canoniques d'exercices "
            "(prescrits + substituts N1 de reference_split.json). Invariance "
            "contrainte #1: aucun renommage, byte-à-byte, ordre codepoint."
        ),
        "source_version": report["source_version"],
        "count": report["canonical_count"],
        "names": report["canonical_names"],
    }
    with resolved.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-snapshot",
        metavar="PATH",
        default=None,
        help="écrit le snapshot du référentiel (chemin explicite, jamais data/)",
    )
    parser.add_argument(
        "--json", action="store_true", help="sortie JSON brute au lieu du texte"
    )
    args = parser.parse_args(argv)

    report = run_audit()
    if args.write_snapshot:
        write_snapshot(Path(args.write_snapshot), report)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_report(report))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
