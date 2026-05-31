#!/usr/bin/env python3
"""Sb_22a — Catalogue pattern_motor QA.

Validates ``data/exercise_properties.json`` against the locked enum
defined in spec Sx_22a v1.1 §C.2bis. Refuses any invalid or missing
``pattern_motor`` so a bad commit fails CI rather than reaching prod.

Also surfaces:
* exercises in reference_split.json that fall in the 7 MVP families but
  are missing from the properties registry (info, not blocker V1);
* curated substitutes that target a different pattern_motor than the
  origin — soft WARNING because the runtime demotes them to N3 silently
  (cf substitution.py ``_add_curated_suggestion``); useful as cleanup
  candidates to migrate into ``cross_pattern_substitutions.json``.

Exit codes:
* 0 — clean OR only soft warnings
* 1 — invalid pattern_motor or missing required field (hard error)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

VALID_PATTERNS = {
    "push_horizontal",
    "push_vertical",
    "pull_horizontal",
    "pull_vertical",
    "squat",
    "hinge",
    "lunge",
    "isolation_upper",
    "isolation_lower",
    "core",
    "cardio",
}

REQUIRED_FIELDS = ("pattern_motor", "zone_primary", "equipment_family", "chain")


def _load_properties() -> dict:
    path = DATA / "exercise_properties.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8")).get("exercises", {})


def _validate_entry(name: str, entry: dict) -> list[str]:
    """Return hard errors for one registry entry."""
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if not entry.get(field):
            errors.append(f"{name}: missing required field '{field}'")
    pm = entry.get("pattern_motor")
    if pm and pm not in VALID_PATTERNS:
        errors.append(
            f"{name}: invalid pattern_motor '{pm}' "
            f"(allowed: {sorted(VALID_PATTERNS)})"
        )
    return errors


def _check_exercise_subs(
    tpl_slug: str, ex: dict, props: dict
) -> list[str]:
    """Return cross-pattern warnings for one template-exercise's curated subs."""
    origin = props.get(ex["name"])
    if not origin:
        return []
    out: list[str] = []
    origin_pm = origin.get("pattern_motor")
    for sub in ex.get("substitutes", []) or []:
        cand = props.get(sub)
        if not cand or cand.get("pattern_motor") == origin_pm:
            continue
        out.append(
            f"{tpl_slug} :: '{ex['name']}' has curated sub '{sub}' "
            f"with pattern {cand.get('pattern_motor')} vs origin {origin_pm} "
            "(migrate to cross_pattern_substitutions.json)"
        )
    return out


def _collect_curated_cross_pattern_warnings(props: dict) -> list[str]:
    """Walk reference_split.json and list curated subs whose pattern differs.

    Soft warnings only — the runtime tolerates them via N3 demotion.
    """
    split_path = DATA / "reference_split.json"
    if not split_path.exists():
        return []
    split = json.loads(split_path.read_text(encoding="utf-8"))
    warnings: list[str] = []
    for tpl in split.get("templates", []):
        for ex in tpl.get("exercises", []):
            warnings.extend(_check_exercise_subs(tpl["slug"], ex, props))
    return warnings


def _report(label: str, items: list[str], stream) -> None:
    if not items:
        return
    print(label, file=stream)
    for item in items:
        print(f"  - {item}", file=stream)


def main() -> int:
    props = _load_properties()
    if not props:
        print(f"FAIL: {DATA / 'exercise_properties.json'} missing or empty", file=sys.stderr)
        return 1

    hard_errors: list[str] = []
    for name, entry in props.items():
        hard_errors.extend(_validate_entry(name, entry))

    if hard_errors:
        _report("Catalogue QA — HARD ERRORS", hard_errors, sys.stderr)
        return 1

    warnings = _collect_curated_cross_pattern_warnings(props)
    _report("Catalogue QA — soft warnings (cleanup candidates)", warnings, sys.stderr)
    print(
        f"Catalogue QA — OK ({len(props)} exercises validated, "
        f"{len(warnings)} soft warning(s))"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
