"""Apply machine atlas links to data/reference_split.json.

For each exercise in the catalog, resolve machine_slug (and machine_family)
using:
  1. Exact match on the atlas machine name or alias (case-insensitive).
  2. Explicit VARIANT_OVERRIDES mapping for names that are clearly a
     variant of a listed machine (e.g. "Leg Press (pieds bas)" -> "leg-press").

Then rewrite reference_split.json with the new fields and bump the version.

Run manually: python scripts/apply_machine_atlas_links.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ATLAS_FILE = PROJECT_ROOT / "data" / "machine_atlas.json"
CATALOG_FILE = PROJECT_ROOT / "data" / "reference_split.json"

# Explicit variant -> machine slug overrides (case-insensitive keys).
# Only list exercises that aren't covered by name/alias exact match.
VARIANT_OVERRIDES: dict[str, str] = {
    "butterfly pec machine": "butterfly-machine",
    "cable cross-over (bas→haut)": "cable-crossover",
    "écarté pec aux câbles (incliné bas→haut)": "cable-crossover",
    "hip thrust smith machine": "hip-thrust-smith",
    "leg press (pieds bas)": "leg-press",
    "leg press (pieds bas, serrés)": "leg-press",
    "leg press (pieds hauts, écartés)": "leg-press",
    "rear delt fly machine (pec deck inversé)": "rear-delt-fly-machine",
    "relevés mollets debout": "standing-calf-raise",
    "relevés mollets debout machine": "standing-calf-raise",
    "rowing câble assis prise large": "seated-cable-row",
    "rowing câble assis prise neutre": "seated-cable-row",
    "rowing câble assis prise serrée": "seated-cable-row",
    "rowing haltère un bras (banc)": "one-arm-dumbbell-row",
    "rowing machine chest-supported": "chest-supported-row",
    "squat smith machine (pieds avancés)": "smith-squat",
    "tirage front câble (prise large)": "lat-pulldown",
    "tirage poulie haute prise large": "lat-pulldown",
    "tirage poulie haute prise neutre": "lat-pulldown",
    "tirage vertical unilatéral câble": "lat-pulldown",
    "face pull câble (corde)": "face-pull-cable",
    "élévations latérales câble (derrière le dos)": "cable-lateral-raise",
    "pullover câble (bras tendus)": "pullover-machine",
    "pullover câble (bras tendus, poulie haute)": "pullover-machine",
    "neutral grip shoulder press machine": "shoulder-press-machine",
    "élévations latérales haltères assis": None,  # no specific atlas entry; leave null
}


def build_name_index(atlas: dict) -> dict[str, tuple[str, str]]:
    """name-or-alias (lowercased) -> (machine_slug, family_slug)."""
    idx: dict[str, tuple[str, str]] = {}
    for fam in atlas["families"]:
        for m in fam["machines"]:
            for key in [m["name"]] + m.get("aliases", []):
                idx[key.lower().strip()] = (m["slug"], fam["slug"])
    return idx


def resolve(name: str, name_index: dict[str, tuple[str, str]], slug_to_family: dict[str, str]) -> tuple[str | None, str | None]:
    """Return (machine_slug, machine_family) for an exercise name."""
    key = name.lower().strip()
    if key in name_index:
        mslug, fslug = name_index[key]
        return mslug, fslug
    if key in VARIANT_OVERRIDES:
        mslug = VARIANT_OVERRIDES[key]
        if mslug is None:
            return None, None
        fslug = slug_to_family.get(mslug)
        return mslug, fslug
    return None, None


def main() -> int:
    atlas = json.loads(ATLAS_FILE.read_text(encoding="utf-8"))
    catalog = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))

    name_index = build_name_index(atlas)
    slug_to_family: dict[str, str] = {}
    for fam in atlas["families"]:
        for m in fam["machines"]:
            slug_to_family[m["slug"]] = fam["slug"]

    stats = {"linked_machine": 0, "linked_family_only": 0, "unlinked": 0}
    unlinked_names: list[str] = []

    for tpl in catalog["templates"]:
        for ex in tpl.get("exercises", []):
            mslug, fslug = resolve(ex["name"], name_index, slug_to_family)
            # Only set if not already present (idempotent-ish on re-run).
            if mslug is not None:
                ex["machine_slug"] = mslug
                ex["machine_family"] = fslug
                stats["linked_machine"] += 1
            elif fslug is not None:
                ex["machine_slug"] = None
                ex["machine_family"] = fslug
                stats["linked_family_only"] += 1
            else:
                ex["machine_slug"] = None
                ex["machine_family"] = None
                stats["unlinked"] += 1
                unlinked_names.append(ex["name"])

    # Bump version v10 -> v11
    catalog["version"] = "2026-04-18.v11"

    CATALOG_FILE.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(json.dumps({
        "atlas_version": atlas.get("version"),
        "catalog_version": catalog["version"],
        "stats": stats,
        "unlinked_sample": sorted(set(unlinked_names))[:30],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
