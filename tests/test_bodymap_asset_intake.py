"""Sb_BODYMAP_ASSET_INTAKE_01 — the structural gate, tested against fixtures.

The validator's job is to catch a non-conforming delivery *before* anyone spends
a human anatomical review on it. These tests prove it catches each contract
breach individually, and — the load-bearing case — that it accepts the three
plates already shipped. A gate that rejects known-good assets is not a gate,
it is an outage.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

from app.services.muscle_mapping import ZONE_LABELS
from scripts.bodymap_asset_intake import (
    FORBIDDEN_ZONE_CODES,
    NON_ZONE_SURFACES,
    PANEL_SIZE,
    REGION_EXPECTED_ZONES,
    SURFACE_ZONE_MAP,
    main,
    validate,
)

ROOT = Path(__file__).resolve().parent.parent
PARTIALS = ROOT / "app" / "templates" / "_partials"
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "bodymap_intake"
SCRIPT = ROOT / "scripts" / "bodymap_asset_intake.py"

SHIPPED = ("chest", "shoulders", "posterior")


def _codes(path: Path) -> set[str]:
    return {f.code for f in validate(path).errors}


# ───────────── A3 / A4 — the shipped plates must pass ─────────────

@pytest.mark.parametrize("region", SHIPPED)
def test_shipped_plates_pass_intake(region):
    report = validate(PARTIALS / f"muscle_focus_plate_{region}.svg")
    assert report.ok, f"{region} rejected: {[f.message for f in report.errors]}"
    assert report.region == region


def test_shipped_shoulders_maps_delt_anterior_without_creating_a_zone():
    """Option A, enforced at intake: the surface exists, the zone does not."""
    report = validate(PARTIALS / "muscle_focus_plate_shoulders.svg")
    anterior = [r for r in report.rows if r.surface == "delt-anterior"]
    assert anterior, "the shoulders plate should still carry delt-anterior surfaces"
    for row in anterior:
        assert row.zone == "— [MERGE]"


def test_shipped_chest_omits_the_frame_segment_and_still_passes():
    """Mono-frame precedent: the frame lives on the group, not in the id."""
    report = validate(PARTIALS / "muscle_focus_plate_chest.svg")
    assert report.ok
    assert all(r.frame == "front" for r in report.rows)
    assert all("--front-" not in r.path_id for r in report.rows)


# ───────────── A5 / A6 / A7 — each breach is caught ─────────────

def test_valid_fixture_passes():
    assert validate(FIXTURES / "valid_back_two_frames.svg").ok


@pytest.mark.parametrize(
    ("fixture", "expected"),
    [
        ("invalid_context_not_first.svg", "CONTEXT_NOT_FIRST"),
        ("invalid_id_grammar.svg", "ID_GRAMMAR"),
        ("invalid_unmapped_surface.svg", "SURFACE_UNMAPPED"),
        ("invalid_forbidden_zone.svg", "FORBIDDEN_ZONE_TOKEN"),
        ("invalid_not_square.svg", "PANEL_NOT_SQUARE"),
        ("invalid_surface_order.svg", "SURFACE_ORDER_UNSTABLE"),
    ],
)
def test_each_breach_is_blocking(fixture, expected):
    codes = _codes(FIXTURES / fixture)
    assert expected in codes, f"{fixture}: expected {expected}, got {sorted(codes)}"


def test_runtime_unsafe_fixture_reports_every_hazard():
    codes = _codes(FIXTURES / "invalid_runtime_unsafe.svg")
    assert "SCRIPT" in codes
    assert "RASTER" in codes
    assert "INLINE_FILL" in codes


def test_missing_file_is_reported_not_raised():
    report = validate(FIXTURES / "does_not_exist.svg")
    assert not report.ok
    assert "NOT_FOUND" in {f.code for f in report.errors}


# ───────────── contract coherence ─────────────

def test_every_mapped_surface_targets_an_existing_business_zone():
    for (region, surface), zone in SURFACE_ZONE_MAP.items():
        assert zone in ZONE_LABELS, f"{region}/{surface} maps to unknown zone {zone!r}"


def test_expected_zones_are_business_zones():
    for region, zones in REGION_EXPECTED_ZONES.items():
        for zone in zones:
            assert zone in ZONE_LABELS, f"{region} expects unknown zone {zone!r}"


def test_ordered_regions_cover_the_eleven_zones_exactly():
    """The order document must account for the whole taxonomy, no more, no less."""
    ordered = [z for zones in REGION_EXPECTED_ZONES.values() for z in zones]
    assert sorted(ordered) == sorted(ZONE_LABELS)
    assert len(ordered) == len(set(ordered)), "a zone is claimed by two regions"


def test_forbidden_codes_are_not_business_zones():
    for code in FORBIDDEN_ZONE_CODES:
        assert code not in ZONE_LABELS


def test_adjudicated_surfaces_are_exempt_from_the_forbidden_check():
    """`delt-anterior` normalises to a forbidden zone code but is a legal surface.

    Pins the fix for the first version of this guard, which matched forbidden
    tokens as substrings of the id and therefore rejected the shipped shoulders
    plate.
    """
    assert "delt-anterior" in NON_ZONE_SURFACES
    assert "delt_anterior" in FORBIDDEN_ZONE_CODES
    assert validate(PARTIALS / "muscle_focus_plate_shoulders.svg").ok


def test_panel_size_matches_the_shipped_geometry():
    assert PANEL_SIZE == 2048


# ───────────── A8 — structure is not anatomy ─────────────

def test_report_always_says_a_pass_is_not_an_anatomical_review():
    for name in ("valid_back_two_frames.svg", "invalid_id_grammar.svg"):
        rendered = validate(FIXTURES / name).render()
        assert "NOT an anatomical review" in rendered
        assert "human review" in rendered


def test_report_lists_expected_zones_not_yet_covered():
    report = validate(PARTIALS / "muscle_focus_plate_chest.svg")
    assert report.missing_zones == []
    partial = validate(FIXTURES / "invalid_context_not_first.svg")
    assert "upper_back" in partial.missing_zones


# ───────────── A3 — the CLI runs ─────────────

def test_cli_exit_code_is_zero_for_a_conforming_plate():
    assert main([str(PARTIALS / "muscle_focus_plate_chest.svg")]) == 0


def test_cli_exit_code_is_one_for_a_breach():
    assert main([str(FIXTURES / "invalid_id_grammar.svg")]) == 1


def test_cli_without_arguments_explains_itself():
    assert main([]) == 2


def test_cli_is_executable_as_a_script():
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(PARTIALS / "muscle_focus_plate_posterior.svg")],
        capture_output=True, text=True, check=False, cwd=ROOT,
    )
    assert result.returncode == 0, result.stderr
    assert "PASS" in result.stdout


# ───────────── A1 / A2 — the order document ─────────────

ORDER_DOC = ROOT / "docs" / "assets" / "AUREN_PROFILE_REGIONAL_PASS_01.md"


def _order_sections() -> str:
    """The document from §2 on — what is actually being ordered.

    §1 exists to quote the mis-formulation and explain why it was wrong, so a
    guard that greps the whole file flags the very explanation that fixes the
    problem. Scope the check to the ask.
    """
    doc = ORDER_DOC.read_text(encoding="utf-8")
    return doc[doc.index("## 2. Ce qui est commandé"):]


def test_a1_order_no_longer_asks_for_a_single_full_body_svg():
    doc = ORDER_DOC.read_text(encoding="utf-8")
    assert "passe caméra `profile`, exportée en panneaux régionaux" in doc
    assert "Pas de plaque corps entier" in doc
    ask = _order_sections().lower()
    assert "produire le profil corps entier" not in ask
    assert "svg corps entier unique" not in ask


def test_a1_order_states_every_target_region_and_its_zones():
    doc = ORDER_DOC.read_text(encoding="utf-8")
    for region, zones in REGION_EXPECTED_ZONES.items():
        if region == "shoulders":
            continue  # revealing plane is `top`, outside this order
        assert f"`{region}`" in doc, f"order document omits region {region}"
        for zone in zones:
            assert f"`{zone}`" in doc, f"order document omits zone {zone}"


def test_a1_order_states_the_square_panel_constraint():
    doc = ORDER_DOC.read_text(encoding="utf-8")
    assert f"{PANEL_SIZE} × {PANEL_SIZE}" in doc or f"{PANEL_SIZE} x {PANEL_SIZE}" in doc


def test_a2_no_full_body_plate_type_exists_in_the_runtime():
    """The reformulation must not have leaked a new plate type into app/."""
    app = ROOT / "app"
    for source in list(app.rglob("*.py")) + list(app.rglob("*.html")):
        text = source.read_text(encoding="utf-8")
        for token in ("FullBodyPlate", "full_body_plate", "whole_body_plate"):
            assert token not in text, f"{source.relative_to(ROOT)} introduces {token!r}"


def test_a8_order_separates_the_structural_gate_from_the_anatomical_one():
    doc = ORDER_DOC.read_text(encoding="utf-8")
    assert "Double porte" in doc
    assert "revue anatomique humaine" in doc
    assert "ne dit **rien** de la justesse anatomique" in doc


def test_open_question_on_default_frame_is_recorded():
    doc = ORDER_DOC.read_text(encoding="utf-8")
    assert "OQ_FRAME_DEFAULT_ORDER_01" in doc
    assert "Non tranchée ici" in doc


# ───────────── fixtures carry no anatomy ─────────────

def test_fixtures_contain_no_anatomical_geometry():
    """The repository does not draw anatomy — not even in test data."""
    for svg in FIXTURES.glob("*.svg"):
        # `\s` matters: splitting on `d="` also matches the tail of `id="`.
        commands = re.findall(r'\sd="([^"]*)"', svg.read_text(encoding="utf-8"))
        assert commands, f"{svg.name} declares no path"
        for command in commands:
            assert command == "M0 0 L1 1", f"{svg.name} carries a non-stub path"
