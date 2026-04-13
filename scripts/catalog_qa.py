"""Catalog QA Script — Structural Checks for reference_split.json.

Runs 7 structural checks against the exercise catalog and produces:
  - A JSON summary printed to stdout
  - A human-readable markdown report at docs/strategy/SPIGNOS_CATALOG_QA_REPORT.md

Exit code: 1 if any errors found, 0 if clean (warnings are allowed).
"""
from __future__ import annotations

import json
import sys
import os
from datetime import date
from pathlib import Path
from typing import Any

# Add project root to sys.path so we can import app.services.*
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.services.muscle_mapping import classify_exercise  # noqa: E402

DATA_FILE = PROJECT_ROOT / "data" / "reference_split.json"
REPORT_FILE = PROJECT_ROOT / "docs" / "strategy" / "SPIGNOS_CATALOG_QA_REPORT.md"

VALID_TECHNIQUES = {None, "RP", "DS"}

# Maps focus tokens (lowercased) found in template "focus" fields to zone keys.
FOCUS_TOKEN_MAP: dict[str, str] = {
    "pectoraux": "pecs",
    "pecs": "pecs",
    "deltoïdes": "delt_lat",
    "deltoïdes latéraux": "delt_lat",
    "deltoïdes postérieurs": "delt_post",
    "épaules": "delt_lat",
    "dos largeur": "lats",
    "grand dorsal": "lats",
    "largeur du dos": "lats",
    "dos": "lats",
    "dos épaisseur": "upper_back",
    "biceps": "biceps",
    "triceps": "triceps",
    "bras": "biceps",
    "quadriceps": "quads",
    "adducteurs": "posterior",
    "ischio-jambiers": "posterior",
    "fessiers": "posterior",
    "mollets": "calves",
    "core": "core",
    "core / abdos": "core",
    "abdos": "core",
    "cardio bas régime + core": "core",
    "cardio": None,  # not a zone, skip
}


def _focus_to_zones(focus_str: str) -> list[str]:
    """Parse a template focus string into a list of zone keys."""
    zones: list[str] = []
    for token in focus_str.split(","):
        token = token.strip().lower()
        if token in FOCUS_TOKEN_MAP:
            zone = FOCUS_TOKEN_MAP[token]
            if zone is not None and zone not in zones:
                zones.append(zone)
    return zones


# ---------------------------------------------------------------------------
# Check implementations
# ---------------------------------------------------------------------------

def check_schema(templates: list[dict]) -> list[dict]:
    """Check 1: every template and exercise has required fields."""
    errors: list[dict] = []
    template_required = {"slug", "name", "kind", "focus", "catalog_section", "display_order"}
    exercise_required = {"position", "code", "name", "set_scheme", "rep_targets"}

    for t in templates:
        slug = t.get("slug", "<missing>")
        missing_t = template_required - set(t.keys())
        if missing_t:
            errors.append({
                "check": "schema",
                "slug": slug,
                "message": f"Template missing fields: {sorted(missing_t)}",
            })
        exercises = t.get("exercises", [])
        if not exercises:
            errors.append({
                "check": "schema",
                "slug": slug,
                "message": "Template has no exercises",
            })
        for ex in exercises:
            code = ex.get("code", "<missing>")
            missing_e = exercise_required - set(ex.keys())
            if missing_e:
                errors.append({
                    "check": "schema",
                    "slug": slug,
                    "exercise": code,
                    "message": f"Exercise missing fields: {sorted(missing_e)}",
                })
            rep_targets = ex.get("rep_targets", [])
            if not rep_targets:
                errors.append({
                    "check": "schema",
                    "slug": slug,
                    "exercise": code,
                    "message": "Exercise has no rep_targets",
                })
    return errors


def check_code_uniqueness(templates: list[dict]) -> list[dict]:
    """Check 2: no duplicate E-codes within a single template."""
    errors: list[dict] = []
    for t in templates:
        slug = t.get("slug", "<missing>")
        codes: list[str] = [ex.get("code", "") for ex in t.get("exercises", [])]
        seen: set[str] = set()
        for code in codes:
            if code in seen:
                errors.append({
                    "check": "code_uniqueness",
                    "slug": slug,
                    "message": f"Duplicate exercise code: {code}",
                })
            seen.add(code)
    return errors


def check_position_sequentiality(templates: list[dict]) -> list[dict]:
    """Check 3: positions form 1, 2, 3... with no gaps."""
    errors: list[dict] = []
    for t in templates:
        slug = t.get("slug", "<missing>")
        positions = sorted(
            ex.get("position") for ex in t.get("exercises", [])
            if ex.get("position") is not None
        )
        expected = list(range(1, len(positions) + 1))
        if positions != expected:
            errors.append({
                "check": "position_sequentiality",
                "slug": slug,
                "message": f"Positions {positions} != expected {expected}",
            })
    return errors


def check_rep_target_coherence(templates: list[dict]) -> list[dict]:
    """Check 4: min_reps <= max_reps; technique in {null, 'RP', 'DS'}."""
    errors: list[dict] = []
    for t in templates:
        slug = t.get("slug", "<missing>")
        for ex in t.get("exercises", []):
            code = ex.get("code", "<missing>")
            for i, rt in enumerate(ex.get("rep_targets", [])):
                mn = rt.get("min_reps")
                mx = rt.get("max_reps")
                tech = rt.get("technique", None)
                if mn is not None and mx is not None and mn > mx:
                    errors.append({
                        "check": "rep_target_coherence",
                        "slug": slug,
                        "exercise": code,
                        "set_index": i,
                        "message": f"min_reps ({mn}) > max_reps ({mx})",
                    })
                if tech not in VALID_TECHNIQUES:
                    errors.append({
                        "check": "rep_target_coherence",
                        "slug": slug,
                        "exercise": code,
                        "set_index": i,
                        "message": f"Invalid technique '{tech}'; must be null, 'RP', or 'DS'",
                    })
    return errors


def check_slug_uniqueness(templates: list[dict]) -> list[dict]:
    """Check 5: no duplicate slugs across all templates."""
    errors: list[dict] = []
    seen: dict[str, int] = {}
    for t in templates:
        slug = t.get("slug", "<missing>")
        seen[slug] = seen.get(slug, 0) + 1
    for slug, count in seen.items():
        if count > 1:
            errors.append({
                "check": "slug_uniqueness",
                "slug": slug,
                "message": f"Slug appears {count} times",
            })
    return errors


def check_exercise_classifiability(templates: list[dict]) -> list[dict]:
    """Check 6: every exercise must classify to something other than ('unknown', [])."""
    errors: list[dict] = []
    for t in templates:
        slug = t.get("slug", "<missing>")
        for ex in t.get("exercises", []):
            code = ex.get("code", "<missing>")
            name = ex.get("name", "")
            primary, secondaries = classify_exercise(name)
            if primary == "unknown" and not secondaries:
                errors.append({
                    "check": "exercise_classifiability",
                    "slug": slug,
                    "exercise": code,
                    "name": name,
                    "message": f"Exercise not classifiable: '{name}'",
                })
    return errors


def check_focus_vs_exercises(templates: list[dict]) -> list[dict]:
    """Check 7 (WARNING): each zone mentioned in focus should have >=1 matching exercise."""
    warnings: list[dict] = []
    for t in templates:
        slug = t.get("slug", "<missing>")
        focus_str = t.get("focus", "")
        focus_zones = _focus_to_zones(focus_str)
        if not focus_zones:
            continue

        # Collect zones covered by actual exercises
        covered: set[str] = set()
        for ex in t.get("exercises", []):
            primary, secondaries = classify_exercise(ex.get("name", ""))
            if primary != "unknown":
                covered.add(primary)
            for z in secondaries:
                covered.add(z)

        for zone in focus_zones:
            if zone not in covered:
                warnings.append({
                    "check": "focus_vs_exercises",
                    "severity": "warning",
                    "slug": slug,
                    "zone": zone,
                    "message": (
                        f"Focus mentions zone '{zone}' but no matching exercise found"
                    ),
                })
    return warnings


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def _render_markdown(
    errors: list[dict],
    warnings: list[dict],
    template_count: int,
    exercise_count: int,
) -> str:
    today = date.today().isoformat()
    lines: list[str] = [
        f"# Catalog QA Report",
        f"",
        f"**Generated:** {today}  ",
        f"**Catalog:** `data/reference_split.json`  ",
        f"**Templates:** {template_count} | **Exercises:** {exercise_count}  ",
        f"",
    ]

    status = "PASS" if not errors else "FAIL"
    lines += [
        f"## Status: {status}",
        f"",
        f"- Errors: {len(errors)}",
        f"- Warnings: {len(warnings)}",
        f"",
    ]

    if errors:
        lines += ["## Errors", ""]
        for e in errors:
            slug = e.get("slug", "")
            ex = e.get("exercise", "")
            ref = f"`{slug}`" + (f" / `{ex}`" if ex else "")
            lines.append(f"- **[{e['check']}]** {ref}: {e['message']}")
        lines.append("")

    if warnings:
        lines += ["## Warnings", ""]
        for w in warnings:
            slug = w.get("slug", "")
            zone = w.get("zone", "")
            lines.append(f"- **[{w['check']}]** `{slug}` zone `{zone}`: {w['message']}")
        lines.append("")

    if not errors and not warnings:
        lines += ["All checks passed with no issues.", ""]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    with open(DATA_FILE, encoding="utf-8") as f:
        data: dict[str, Any] = json.load(f)

    templates: list[dict] = data.get("templates", [])
    exercise_count = sum(len(t.get("exercises", [])) for t in templates)

    errors: list[dict] = []
    warnings: list[dict] = []

    errors += check_schema(templates)
    errors += check_code_uniqueness(templates)
    errors += check_position_sequentiality(templates)
    errors += check_rep_target_coherence(templates)
    errors += check_slug_uniqueness(templates)
    errors += check_exercise_classifiability(templates)
    warnings += check_focus_vs_exercises(templates)

    summary = {
        "catalog": str(DATA_FILE.relative_to(PROJECT_ROOT)),
        "templates": len(templates),
        "exercises": exercise_count,
        "errors": len(errors),
        "warnings": len(warnings),
        "status": "FAIL" if errors else "PASS",
        "error_details": errors,
        "warning_details": warnings,
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2))

    # Write markdown report
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    md = _render_markdown(errors, warnings, len(templates), exercise_count)
    REPORT_FILE.write_text(md, encoding="utf-8")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
