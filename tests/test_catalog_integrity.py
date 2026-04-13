"""CI-blocking integrity tests for data/reference_split.json."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

CATALOG_PATH = Path(__file__).parent.parent / "data" / "reference_split.json"

TEMPLATE_REQUIRED = {"slug", "name", "kind", "focus", "catalog_section", "display_order"}
EXERCISE_REQUIRED = {"position", "code", "name", "set_scheme"}
VALID_TECHNIQUES = {None, "RP", "DS"}


@pytest.fixture(scope="module")
def catalog() -> dict:
    with CATALOG_PATH.open() as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def templates(catalog: dict) -> list[dict]:
    return catalog["templates"]


# ---------------------------------------------------------------------------
# 1. Version field
# ---------------------------------------------------------------------------

def test_catalog_has_version(catalog: dict) -> None:
    assert "version" in catalog, "Catalog must have a 'version' field"
    assert catalog["version"], "Catalog version must not be empty"


# ---------------------------------------------------------------------------
# 2. Template required fields
# ---------------------------------------------------------------------------

def test_templates_have_required_fields(templates: list[dict]) -> None:
    for tmpl in templates:
        missing = TEMPLATE_REQUIRED - tmpl.keys()
        assert not missing, (
            f"Template '{tmpl.get('slug', '?')}' is missing fields: {missing}"
        )


# ---------------------------------------------------------------------------
# 3. Exercise required fields
# ---------------------------------------------------------------------------

def test_exercises_have_required_fields(templates: list[dict]) -> None:
    for tmpl in templates:
        slug = tmpl.get("slug", "?")
        for ex in tmpl.get("exercises", []):
            missing = EXERCISE_REQUIRED - ex.keys()
            assert not missing, (
                f"Exercise '{ex.get('code', '?')}' in template '{slug}' "
                f"is missing fields: {missing}"
            )


# ---------------------------------------------------------------------------
# 4. At least 1 rep_target per exercise
# ---------------------------------------------------------------------------

def test_exercises_have_rep_targets(templates: list[dict]) -> None:
    for tmpl in templates:
        slug = tmpl.get("slug", "?")
        for ex in tmpl.get("exercises", []):
            rts = ex.get("rep_targets", [])
            assert len(rts) >= 1, (
                f"Exercise '{ex.get('code', '?')}' in template '{slug}' "
                f"must have at least 1 rep_target"
            )


# ---------------------------------------------------------------------------
# 5. No duplicate E-codes within a template
# ---------------------------------------------------------------------------

def test_no_duplicate_codes_within_template(templates: list[dict]) -> None:
    for tmpl in templates:
        slug = tmpl.get("slug", "?")
        codes = [ex.get("code") for ex in tmpl.get("exercises", [])]
        seen: set = set()
        for code in codes:
            assert code not in seen, (
                f"Duplicate code '{code}' found in template '{slug}'"
            )
            seen.add(code)


# ---------------------------------------------------------------------------
# 6. Positions are sequential (1, 2, 3 … no gaps)
# ---------------------------------------------------------------------------

def test_positions_are_sequential(templates: list[dict]) -> None:
    for tmpl in templates:
        slug = tmpl.get("slug", "?")
        positions = sorted(
            ex.get("position") for ex in tmpl.get("exercises", [])
        )
        expected = list(range(1, len(positions) + 1))
        assert positions == expected, (
            f"Template '{slug}' has non-sequential positions: {positions}"
        )


# ---------------------------------------------------------------------------
# 7. rep_targets coherence
# ---------------------------------------------------------------------------

def test_rep_targets_are_coherent(templates: list[dict]) -> None:
    for tmpl in templates:
        slug = tmpl.get("slug", "?")
        for ex in tmpl.get("exercises", []):
            code = ex.get("code", "?")
            for idx, rt in enumerate(ex.get("rep_targets", [])):
                min_r = rt.get("min_reps")
                max_r = rt.get("max_reps")
                technique = rt.get("technique", None)

                assert min_r is not None and max_r is not None, (
                    f"rep_target[{idx}] in {code}/{slug} missing min/max_reps"
                )
                assert min_r <= max_r, (
                    f"rep_target[{idx}] in {code}/{slug}: "
                    f"min_reps ({min_r}) > max_reps ({max_r})"
                )
                assert technique in VALID_TECHNIQUES, (
                    f"rep_target[{idx}] in {code}/{slug}: "
                    f"invalid technique '{technique}' (must be one of {VALID_TECHNIQUES})"
                )


# ---------------------------------------------------------------------------
# 8. No duplicate slugs across templates
# ---------------------------------------------------------------------------

def test_no_duplicate_slugs(templates: list[dict]) -> None:
    slugs = [tmpl.get("slug") for tmpl in templates]
    seen: set = set()
    for slug in slugs:
        assert slug not in seen, f"Duplicate template slug: '{slug}'"
        seen.add(slug)


# ---------------------------------------------------------------------------
# 9. All exercises are classifiable (no "unknown" zone)
# ---------------------------------------------------------------------------

def test_all_exercises_are_classifiable(templates: list[dict]) -> None:
    from app.services.muscle_mapping import classify_exercise

    unknown: list[str] = []
    for tmpl in templates:
        slug = tmpl.get("slug", "?")
        for ex in tmpl.get("exercises", []):
            zone, _ = classify_exercise(ex["name"])
            if zone == "unknown":
                unknown.append(f"{slug}/{ex.get('code','?')} '{ex['name']}'")

    assert not unknown, (
        f"{len(unknown)} exercise(s) returned 'unknown' zone:\n"
        + "\n".join(f"  {u}" for u in unknown)
    )


# ---------------------------------------------------------------------------
# 10. Each template has at least 1 exercise
# ---------------------------------------------------------------------------

def test_each_template_has_exercises(templates: list[dict]) -> None:
    for tmpl in templates:
        slug = tmpl.get("slug", "?")
        exercises = tmpl.get("exercises", [])
        assert len(exercises) >= 1, (
            f"Template '{slug}' has no exercises"
        )
