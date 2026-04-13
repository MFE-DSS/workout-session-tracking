# S0 — Catalog Integrity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stabilize the exercise catalog as a reliable, auditable foundation for analytics — without breaking any existing behavior.

**Architecture:** Script-based QA over `data/reference_split.json`, corrections to focus fields and muscle_mapping patterns, governance documentation, and CI-blocking integrity tests. No model changes, no migrations.

**Tech Stack:** Python (stdlib json), pytest, `app.services.muscle_mapping.classify_exercise`

---

## File Structure

| File | Responsibility |
|------|---------------|
| `scripts/catalog_qa.py` | Standalone QA script — reads JSON, runs checks, outputs report |
| `data/reference_split.json` | Source of truth (focus field corrections, version bump) |
| `app/services/muscle_mapping.py` | Exercise classifier patterns (add any missing) |
| `tests/test_catalog_integrity.py` | CI-blocking integrity assertions |
| `docs/strategy/SPIGNOS_CATALOG_GOVERNANCE.md` | Governance rules and conventions |
| `docs/strategy/SPIGNOS_CATALOG_QA_REPORT.md` | Generated QA report |
| `docs/SPRINT_S0_REPORT.md` | Sprint delivery report |

---

### Task 1: Catalog QA Script — Structural Checks

**Files:**
- Create: `scripts/catalog_qa.py`

- [ ] **Step 1: Create the script with JSON loading and structural checks**

```python
#!/usr/bin/env python3
"""Catalog QA — validate reference_split.json integrity.

Usage: python scripts/catalog_qa.py
Output: JSON report to stdout, markdown to docs/strategy/SPIGNOS_CATALOG_QA_REPORT.md
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = ROOT / "data" / "reference_split.json"
REPORT_PATH = ROOT / "docs" / "strategy" / "SPIGNOS_CATALOG_QA_REPORT.md"

# Add project root to path so we can import muscle_mapping
sys.path.insert(0, str(ROOT))


def load_catalog() -> dict:
    with CATALOG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def check_schema(templates: list[dict]) -> list[str]:
    """Every template must have required fields; every exercise too."""
    errors = []
    required_tpl = {"slug", "name", "kind", "focus", "catalog_section", "display_order"}
    required_ex = {"position", "code", "name", "set_scheme"}

    for tpl in templates:
        slug = tpl.get("slug", "<no-slug>")
        missing = required_tpl - set(tpl.keys())
        if missing:
            errors.append(f"[{slug}] missing template fields: {missing}")
        for ex in tpl.get("exercises", []):
            ex_missing = required_ex - set(ex.keys())
            if ex_missing:
                errors.append(
                    f"[{slug}] exercise '{ex.get('name', '?')}' missing fields: {ex_missing}"
                )
            rts = ex.get("rep_targets", [])
            if not rts:
                errors.append(
                    f"[{slug}] exercise '{ex.get('name', '?')}' has no rep_targets"
                )
        if not tpl.get("exercises"):
            errors.append(f"[{slug}] has no exercises")
    return errors


def check_code_uniqueness(templates: list[dict]) -> list[str]:
    """No duplicate E-codes within a single template."""
    errors = []
    for tpl in templates:
        slug = tpl["slug"]
        codes = [ex["code"] for ex in tpl.get("exercises", [])]
        seen = set()
        for c in codes:
            if c in seen:
                errors.append(f"[{slug}] duplicate exercise code: {c}")
            seen.add(c)
    return errors


def check_positions(templates: list[dict]) -> list[str]:
    """Positions must be sequential 1, 2, 3... with no gaps."""
    errors = []
    for tpl in templates:
        slug = tpl["slug"]
        positions = sorted(ex["position"] for ex in tpl.get("exercises", []))
        expected = list(range(1, len(positions) + 1))
        if positions != expected:
            errors.append(f"[{slug}] positions {positions} != expected {expected}")
    return errors


def check_rep_targets(templates: list[dict]) -> list[str]:
    """min_reps <= max_reps, technique in {null, 'RP', 'DS'}."""
    errors = []
    valid_techniques = {None, "RP", "DS"}
    for tpl in templates:
        slug = tpl["slug"]
        for ex in tpl.get("exercises", []):
            for i, rt in enumerate(ex.get("rep_targets", []), 1):
                if rt["min_reps"] > rt["max_reps"]:
                    errors.append(
                        f"[{slug}] {ex['code']} set {i}: "
                        f"min_reps ({rt['min_reps']}) > max_reps ({rt['max_reps']})"
                    )
                tech = rt.get("technique")
                if tech not in valid_techniques:
                    errors.append(
                        f"[{slug}] {ex['code']} set {i}: invalid technique '{tech}'"
                    )
    return errors


def check_slug_uniqueness(templates: list[dict]) -> list[str]:
    """No duplicate slugs across all templates."""
    errors = []
    seen: set[str] = set()
    for tpl in templates:
        slug = tpl["slug"]
        if slug in seen:
            errors.append(f"duplicate slug: {slug}")
        seen.add(slug)
    return errors


def check_classifiability(templates: list[dict]) -> tuple[list[str], list[str]]:
    """Every exercise must be classifiable (not 'unknown')."""
    from app.services.muscle_mapping import classify_exercise

    errors = []
    warnings = []
    for tpl in templates:
        slug = tpl["slug"]
        for ex in tpl.get("exercises", []):
            primary, _ = classify_exercise(ex["name"])
            if primary == "unknown":
                errors.append(
                    f"[{slug}] exercise '{ex['name']}' ({ex['code']}) "
                    f"is unclassifiable"
                )
    return errors, warnings


def check_focus_alignment(templates: list[dict]) -> list[str]:
    """Each zone in focus should have >= 1 matching exercise. Warning only."""
    from app.services.muscle_mapping import ZONE_LABELS, classify_exercise

    warnings = []
    # Build reverse map: French label -> zone key
    label_to_zone: dict[str, str] = {}
    for zone_key, french_label in ZONE_LABELS.items():
        label_to_zone[french_label.lower()] = zone_key

    # Common focus tokens that map to zones
    FOCUS_TOKEN_MAP = {
        "pectoraux": "pecs",
        "pecs": "pecs",
        "deltoïdes": "delt_lat",
        "deltoïdes latéraux": "delt_lat",
        "deltoïdes postérieurs": "delt_post",
        "dos largeur": "lats",
        "dos épaisseur": "upper_back",
        "dos": "upper_back",
        "grand dorsal": "lats",
        "largeur du dos": "lats",
        "biceps": "biceps",
        "triceps": "triceps",
        "quadriceps": "quads",
        "ischio-jambiers": "posterior",
        "fessiers": "posterior",
        "adducteurs": "posterior",
        "mollets": "calves",
        "core": "core",
        "core / abdos": "core",
        "cardio bas régime + core": "core",
    }

    for tpl in templates:
        slug = tpl["slug"]
        focus = tpl.get("focus", "")
        # Collect zones actually trained
        trained_zones: set[str] = set()
        for ex in tpl.get("exercises", []):
            primary, secondary = classify_exercise(ex["name"])
            if primary != "unknown":
                trained_zones.add(primary)
            for sec in secondary:
                trained_zones.add(sec)

        # Parse focus into expected zones
        focus_lower = focus.lower().strip()
        expected_zones: set[str] = set()
        for token, zone in FOCUS_TOKEN_MAP.items():
            if token in focus_lower:
                expected_zones.add(zone)

        # Check: any expected zone not trained?
        for zone in expected_zones:
            if zone not in trained_zones:
                warnings.append(
                    f"[{slug}] focus mentions '{zone}' "
                    f"but no exercise classifies to it"
                )

    return warnings


def generate_report(
    catalog: dict,
    errors: list[str],
    warnings: list[str],
) -> str:
    """Generate markdown QA report."""
    version = catalog.get("version", "unknown")
    template_count = len(catalog.get("templates", []))
    exercise_count = sum(
        len(t.get("exercises", [])) for t in catalog.get("templates", [])
    )

    status = "PASS" if not errors else "FAIL"

    lines = [
        f"# Catalog QA Report — {version}",
        "",
        f"**Status:** {status}",
        f"**Templates:** {template_count}",
        f"**Exercises:** {exercise_count}",
        f"**Errors:** {len(errors)}",
        f"**Warnings:** {len(warnings)}",
        "",
    ]

    if errors:
        lines.append("## Errors (must fix)")
        lines.append("")
        for e in errors:
            lines.append(f"- {e}")
        lines.append("")

    if warnings:
        lines.append("## Warnings (review)")
        lines.append("")
        for w in warnings:
            lines.append(f"- {w}")
        lines.append("")

    if not errors and not warnings:
        lines.append("All checks passed. Catalog is clean.")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    catalog = load_catalog()
    templates = catalog.get("templates", [])

    all_errors: list[str] = []
    all_warnings: list[str] = []

    all_errors.extend(check_schema(templates))
    all_errors.extend(check_code_uniqueness(templates))
    all_errors.extend(check_positions(templates))
    all_errors.extend(check_rep_targets(templates))
    all_errors.extend(check_slug_uniqueness(templates))

    classify_errors, classify_warnings = check_classifiability(templates)
    all_errors.extend(classify_errors)
    all_warnings.extend(classify_warnings)

    all_warnings.extend(check_focus_alignment(templates))

    # Generate and save report
    report = generate_report(catalog, all_errors, all_warnings)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")

    # Also print JSON summary
    result = {
        "version": catalog.get("version"),
        "status": "PASS" if not all_errors else "FAIL",
        "errors": all_errors,
        "warnings": all_warnings,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))

    return 1 if all_errors else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run the script to see current catalog state**

Run: `python scripts/catalog_qa.py`
Expected: Report output showing any existing errors (likely focus alignment warnings for legs templates missing "Core" in focus). Check the JSON output and the generated `docs/strategy/SPIGNOS_CATALOG_QA_REPORT.md`.

- [ ] **Step 3: Commit**

```bash
git add scripts/catalog_qa.py
git commit -m "feat(s0): add catalog QA script with 7 structural checks"
```

---

### Task 2: Fix Catalog Focus Fields

**Files:**
- Modify: `data/reference_split.json`

- [ ] **Step 1: Fix `liss-abs` focus**

In `data/reference_split.json`, find the `liss-abs` template and change:
```json
"focus": "Cardio bas régime + Core"
```
to:
```json
"focus": "Core / Abdos"
```

- [ ] **Step 2: Add ", Core" to `legs-a` focus**

Change:
```json
"focus": "Quadriceps, Adducteurs, Mollets"
```
to:
```json
"focus": "Quadriceps, Adducteurs, Mollets, Core"
```

- [ ] **Step 3: Add ", Core" to `legs-b` focus**

Change:
```json
"focus": "Ischio-jambiers, Fessiers, Mollets"
```
to:
```json
"focus": "Ischio-jambiers, Fessiers, Mollets, Core"
```

- [ ] **Step 4: Add ", Core" to `lower-quad-bias` focus**

Change:
```json
"focus": "Quadriceps, Mollets"
```
to:
```json
"focus": "Quadriceps, Mollets, Core"
```

- [ ] **Step 5: Add ", Core" to `lower-posterior-bias` focus**

Change:
```json
"focus": "Ischio-jambiers, Fessiers, Mollets"
```
to:
```json
"focus": "Ischio-jambiers, Fessiers, Mollets, Core"
```

- [ ] **Step 6: Bump catalog version**

Change:
```json
"version": "2026-04-13.v5"
```
to:
```json
"version": "2026-04-13.v6"
```

- [ ] **Step 7: Run QA script to verify fixes**

Run: `python scripts/catalog_qa.py`
Expected: Fewer warnings. Check that focus alignment warnings for legs/liss-abs are gone.

- [ ] **Step 8: Commit**

```bash
git add data/reference_split.json
git commit -m "fix(s0): correct catalog focus fields — legs+Core, liss-abs→Core/Abdos, bump v6"
```

---

### Task 3: Fix Muscle Mapping Gaps

**Files:**
- Modify: `app/services/muscle_mapping.py`

- [ ] **Step 1: Run QA script and note any unclassifiable exercises**

Run: `python scripts/catalog_qa.py`
Expected: Check for any "unclassifiable" errors in the output. If there are none, this task is a verification-only task (skip to step 3).

- [ ] **Step 2: Add missing patterns if any**

If the QA script found unclassifiable exercises, add the needed substring patterns to `_EXERCISE_PATTERNS` in `app/services/muscle_mapping.py:64-90`. For example, if "Développé couché haltères" doesn't match, add `"développé couché"` to the pecs pattern list (it's actually already there at line 66, but verify).

Each pattern addition follows the existing format:
```python
(["keyword1", "keyword2"], "zone", ["secondary_zone1"]),
```

- [ ] **Step 3: Re-run QA script to confirm zero classifiability errors**

Run: `python scripts/catalog_qa.py`
Expected: `"status": "PASS"` and zero errors in classifiability section.

- [ ] **Step 4: Commit (only if changes were made)**

```bash
git add app/services/muscle_mapping.py
git commit -m "fix(s0): add missing exercise patterns to muscle mapping"
```

---

### Task 4: Catalog Integrity Tests

**Files:**
- Create: `tests/test_catalog_integrity.py`

- [ ] **Step 1: Write the integrity test file**

```python
"""CI-blocking tests for catalog integrity.

These tests verify data/reference_split.json against the same
rules as scripts/catalog_qa.py. They block merges on catalog regressions.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.services.muscle_mapping import ZONE_LABELS, classify_exercise

ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = ROOT / "data" / "reference_split.json"


@pytest.fixture(scope="module")
def catalog() -> dict:
    with CATALOG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def templates(catalog) -> list[dict]:
    return catalog["templates"]


def test_catalog_has_version(catalog):
    assert "version" in catalog
    assert catalog["version"]


def test_all_templates_have_required_fields(templates):
    required = {"slug", "name", "kind", "focus", "catalog_section", "display_order"}
    for tpl in templates:
        missing = required - set(tpl.keys())
        assert not missing, f"[{tpl.get('slug', '?')}] missing: {missing}"


def test_all_exercises_have_required_fields(templates):
    required = {"position", "code", "name", "set_scheme"}
    for tpl in templates:
        for ex in tpl.get("exercises", []):
            missing = required - set(ex.keys())
            assert not missing, (
                f"[{tpl['slug']}] exercise '{ex.get('name', '?')}' missing: {missing}"
            )


def test_all_exercises_have_rep_targets(templates):
    for tpl in templates:
        for ex in tpl.get("exercises", []):
            assert ex.get("rep_targets"), (
                f"[{tpl['slug']}] {ex['code']} has no rep_targets"
            )


def test_no_duplicate_codes_per_template(templates):
    for tpl in templates:
        codes = [ex["code"] for ex in tpl.get("exercises", [])]
        assert len(codes) == len(set(codes)), (
            f"[{tpl['slug']}] duplicate codes: {codes}"
        )


def test_positions_are_sequential(templates):
    for tpl in templates:
        positions = sorted(ex["position"] for ex in tpl.get("exercises", []))
        expected = list(range(1, len(positions) + 1))
        assert positions == expected, (
            f"[{tpl['slug']}] positions {positions} != {expected}"
        )


def test_rep_targets_coherent(templates):
    valid_techniques = {None, "RP", "DS"}
    for tpl in templates:
        for ex in tpl.get("exercises", []):
            for i, rt in enumerate(ex.get("rep_targets", []), 1):
                assert rt["min_reps"] <= rt["max_reps"], (
                    f"[{tpl['slug']}] {ex['code']} set {i}: "
                    f"min {rt['min_reps']} > max {rt['max_reps']}"
                )
                assert rt.get("technique") in valid_techniques, (
                    f"[{tpl['slug']}] {ex['code']} set {i}: "
                    f"bad technique '{rt.get('technique')}'"
                )


def test_no_duplicate_slugs(templates):
    slugs = [t["slug"] for t in templates]
    assert len(slugs) == len(set(slugs)), f"duplicate slugs: {slugs}"


def test_all_exercises_classifiable(templates):
    """Every exercise in the catalog must classify to a known zone."""
    unknowns = []
    for tpl in templates:
        for ex in tpl.get("exercises", []):
            primary, _ = classify_exercise(ex["name"])
            if primary == "unknown":
                unknowns.append(f"[{tpl['slug']}] {ex['code']}: {ex['name']}")
    assert not unknowns, (
        f"{len(unknowns)} unclassifiable exercises:\n"
        + "\n".join(unknowns)
    )


def test_each_template_has_exercises(templates):
    for tpl in templates:
        assert tpl.get("exercises"), f"[{tpl['slug']}] has no exercises"
```

- [ ] **Step 2: Run the tests**

Run: `pytest tests/test_catalog_integrity.py -v`
Expected: All tests PASS (since we fixed the catalog in Task 2).

- [ ] **Step 3: Commit**

```bash
git add tests/test_catalog_integrity.py
git commit -m "test(s0): add CI-blocking catalog integrity tests"
```

---

### Task 5: Governance Documentation

**Files:**
- Create: `docs/strategy/SPIGNOS_CATALOG_GOVERNANCE.md`

- [ ] **Step 1: Write the governance document**

```markdown
# SPIGNOS Catalog Governance

## Source of Truth

`data/reference_split.json` is the single source of truth for the exercise catalog.
All workout templates, exercises, rep targets, and metadata originate from this file.

## Versioning Convention

Format: `YYYY-MM-DD.vN`

Every change to the catalog JSON must bump the version. The seed service
(`app/services/seed.py`) is idempotent and keyed on this version string:
new version = full re-seed of catalog tables on next boot.

## Modification Workflow

1. Edit `data/reference_split.json`
2. Bump the `version` field
3. Run `python scripts/catalog_qa.py` and verify the report is clean
4. Run `pytest tests/test_catalog_integrity.py` — must pass
5. Commit and push
6. On next deploy, the seed service detects the new version and re-seeds

## Focus Field Role

The `focus` field is **editorial** — it serves the UI (library display, template
cards, suggested labels) and human readability.

It is **NOT** the analytical truth. The analytical truth comes from
`app/services/muscle_mapping.classify_exercise()`, which maps exercise names to
muscle zones using substring pattern matching.

The focus field and the mapping should be directionally aligned, but the mapping
is what drives scores, dashboards, and analytics. Do not encode scoring logic
into the focus text.

## Analytics Impact Policy

Scoring uses exercise names captured at session creation time (immutable
snapshots in `session_exercises.exercise_name_snapshot`). Changing catalog
focus or mapping affects future scores only — never historical data.

Session FK to catalog uses `ON DELETE SET NULL`, so catalog rewrites
never break historical sessions.

## Known Structural Decisions

These are intentional design choices, not bugs:

1. **pull-a has no direct biceps isolation** — by design (width focus).
   Vertical pulls contribute biceps as secondary zone in the classifier.

2. **push-a E6 "Écarté arrière d'épaule câble"** is a pull-pattern movement
   in a push template — common PPL practice for complete shoulder coverage
   on push day.

3. **Archived templates overlap with core templates** — the 4 archived
   templates are pre-PPL-split legacy. Retained for users who started
   sessions with them. Hidden from the catalog UI but still functional.
```

- [ ] **Step 2: Commit**

```bash
git add docs/strategy/SPIGNOS_CATALOG_GOVERNANCE.md
git commit -m "docs(s0): add catalog governance — source of truth, versioning, focus role"
```

---

### Task 6: Generate Final QA Report & Sprint Report

**Files:**
- Generate: `docs/strategy/SPIGNOS_CATALOG_QA_REPORT.md`
- Create: `docs/SPRINT_S0_REPORT.md`

- [ ] **Step 1: Generate the final QA report**

Run: `python scripts/catalog_qa.py`
Expected: `"status": "PASS"`, zero errors. The markdown report is written to `docs/strategy/SPIGNOS_CATALOG_QA_REPORT.md`.

- [ ] **Step 2: Run all tests to verify nothing is broken**

Run: `pytest -x -q`
Expected: All tests pass, including the new catalog integrity tests.

- [ ] **Step 3: Write the sprint report**

Create `docs/SPRINT_S0_REPORT.md`:

```markdown
# Sprint S0 Report — Foundation Freeze & Catalog Integrity

**Date:** 2026-04-13
**Status:** Complete

## Objective

Stabilize the exercise catalog as a reliable, auditable foundation for
future analytics (physique dashboard, body engineering, muscle scoring).

## Deliverables

| Artifact | Path | Status |
|----------|------|--------|
| QA script | `scripts/catalog_qa.py` | Done |
| QA report | `docs/strategy/SPIGNOS_CATALOG_QA_REPORT.md` | Generated, PASS |
| Governance doc | `docs/strategy/SPIGNOS_CATALOG_GOVERNANCE.md` | Done |
| Integrity tests | `tests/test_catalog_integrity.py` | Done, all pass |

## Changes Made

### Catalog Corrections (`data/reference_split.json`)
- `liss-abs` focus: "Cardio bas régime + Core" → "Core / Abdos"
- `legs-a` focus: added ", Core" (has E7 Roulette abdominale)
- `legs-b` focus: added ", Core" (has E7 Crunch câble)
- `lower-quad-bias` focus: added ", Core" (has E6 Roulette abdominale)
- `lower-posterior-bias` focus: added ", Core" (has E6 Crunch câble)
- Version bumped to `2026-04-13.v6`

### Muscle Mapping (`app/services/muscle_mapping.py`)
- Verified all 95+ exercises are classifiable — zero unknowns
- [Add any pattern additions here if they were needed]

## Documented Anomalies (intentional, not corrected)
- pull-a: no direct biceps isolation (width focus by design)
- push-a E6: rear delt on push day (PPL convention)
- Archived templates overlap with core (pre-split legacy)

## Verification Commands

```bash
python scripts/catalog_qa.py      # Should output "PASS"
pytest tests/test_catalog_integrity.py -v  # All pass
pytest -x -q                       # Full suite green
```

## Files Modified

- `data/reference_split.json` (focus corrections, version bump)
- `app/services/muscle_mapping.py` (pattern additions if any)
- `scripts/catalog_qa.py` (new)
- `tests/test_catalog_integrity.py` (new)
- `docs/strategy/SPIGNOS_CATALOG_GOVERNANCE.md` (new)
- `docs/strategy/SPIGNOS_CATALOG_QA_REPORT.md` (generated)

## Gaps for S1

- Body measurements need lateralization (arm_cm → left/right)
- No readiness tracking yet
- Focus field is now editorial-clean; mapping is analytical-clean
```

- [ ] **Step 4: Commit**

```bash
git add docs/strategy/SPIGNOS_CATALOG_QA_REPORT.md docs/SPRINT_S0_REPORT.md
git commit -m "docs(s0): add QA report and sprint S0 delivery report"
```

- [ ] **Step 5: Run full test suite one final time**

Run: `pytest -x -q`
Expected: All tests pass. S0 is complete.
