"""Machine Atlas QA Script — structural checks for data/machine_atlas.json.

Checks:
  1. Every family has slug / name / zone / machines (>=1)
  2. Slug uniqueness (family slugs globally, machine slugs globally)
  3. Every machine has required fields and at least 2 execution_cues + 2 common_mistakes
  4. Enumerations: equipment in {machine, smith, cable, haltere, barbell, bodyweight},
                   laterality in {bilateral, unilateral, both},
                   load_semantics in {total, per_side}

Exit code: 1 if errors, 0 if clean.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "machine_atlas.json"

VALID_EQUIPMENT = {"machine", "smith", "cable", "haltere", "barbell", "bodyweight"}
VALID_LATERALITY = {"bilateral", "unilateral", "both"}
VALID_LOAD_SEMANTICS = {"total", "per_side"}

FAMILY_REQUIRED = {"slug", "name", "zone", "machines"}
MACHINE_REQUIRED = {
    "slug", "name", "aliases", "variants", "equipment",
    "laterality", "load_semantics", "execution_cues", "common_mistakes",
}


def check_families(families: list[dict]) -> list[str]:
    errors: list[str] = []
    family_slugs: dict[str, int] = {}
    for i, fam in enumerate(families):
        missing = FAMILY_REQUIRED - set(fam.keys())
        if missing:
            errors.append(f"family[{i}] missing fields: {sorted(missing)}")
        slug = fam.get("slug", f"<idx {i}>")
        family_slugs[slug] = family_slugs.get(slug, 0) + 1
        if not fam.get("machines"):
            errors.append(f"family '{slug}' has no machines")
    for slug, count in family_slugs.items():
        if count > 1:
            errors.append(f"duplicate family slug: {slug} (x{count})")
    return errors


def check_machines(families: list[dict]) -> list[str]:
    errors: list[str] = []
    machine_slugs: dict[str, int] = {}

    for fam in families:
        fslug = fam.get("slug", "<?>")
        for machine in fam.get("machines", []):
            mslug = machine.get("slug", "<?>")
            ref = f"{fslug}/{mslug}"

            missing = MACHINE_REQUIRED - set(machine.keys())
            if missing:
                errors.append(f"{ref}: missing fields {sorted(missing)}")
                continue

            machine_slugs[mslug] = machine_slugs.get(mslug, 0) + 1

            equipment = machine.get("equipment")
            if equipment not in VALID_EQUIPMENT:
                errors.append(f"{ref}: invalid equipment '{equipment}'")

            lat = machine.get("laterality")
            if lat not in VALID_LATERALITY:
                errors.append(f"{ref}: invalid laterality '{lat}'")

            ls = machine.get("load_semantics")
            if ls not in VALID_LOAD_SEMANTICS:
                errors.append(f"{ref}: invalid load_semantics '{ls}'")

            cues = machine.get("execution_cues") or []
            if len(cues) < 2:
                errors.append(f"{ref}: needs >=2 execution_cues (has {len(cues)})")

            mistakes = machine.get("common_mistakes") or []
            if len(mistakes) < 2:
                errors.append(f"{ref}: needs >=2 common_mistakes (has {len(mistakes)})")

            if not isinstance(machine.get("aliases"), list):
                errors.append(f"{ref}: 'aliases' must be a list")
            if not isinstance(machine.get("variants"), list):
                errors.append(f"{ref}: 'variants' must be a list")

    for slug, count in machine_slugs.items():
        if count > 1:
            errors.append(f"duplicate machine slug across atlas: {slug} (x{count})")

    return errors


def main() -> int:
    with open(DATA_FILE, encoding="utf-8") as f:
        data: dict[str, Any] = json.load(f)

    version = data.get("version")
    families = data.get("families", [])

    errors: list[str] = []
    errors += check_families(families)
    errors += check_machines(families)

    machine_count = sum(len(f.get("machines", [])) for f in families)
    summary = {
        "file": str(DATA_FILE.relative_to(PROJECT_ROOT)),
        "version": version,
        "families": len(families),
        "machines": machine_count,
        "errors": len(errors),
        "status": "FAIL" if errors else "PASS",
        "error_details": errors,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
