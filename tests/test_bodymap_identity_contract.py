"""Sb_BODYMAP_IDENTITY_CONTRACT_01 — the identity contract, made executable.

A naming contract that lives only in prose rots quietly: the assets drift, the
document keeps asserting the old truth, and nobody notices until a production
order is already wrong. These guards read the real SVGs, the real taxonomy and
the real stylesheet, so the document fails the build instead of ageing.

Scope discipline: this sprint is SPEC/CONTRACT ONLY. Nothing here changes
runtime behaviour, and two guards exist specifically to prove that — A5 (no id
renamed) and A8 (zone_recovery still not wired).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from app.services.bodymap_frames import FRAME_ORDER, regional_plates
from app.services.muscle_mapping import ZONE_LABELS

ROOT = Path(__file__).resolve().parent.parent
PARTIALS = ROOT / "app" / "templates" / "_partials"
TEMPLATES = ROOT / "app" / "templates"
CSS = ROOT / "app" / "static" / "css" / "app.css"
SPEC = ROOT / "docs" / "strategy" / "Sb_BODYMAP_IDENTITY_CONTRACT_01.md"
DESIGN_CONTRACT = (
    ROOT / "design" / "auren" / "source" / "bodymap" / "auren_bodymap_mapping.yaml"
)

PLATE_REGIONS = ("chest", "shoulders", "posterior")

#: Exact surface tokens present in the shipped plates, audited from the files.
#: A new token appearing here without a contract decision is a contract breach.
EXPECTED_SURFACE_TOKENS = {
    "chest": {"context", "hero"},
    "shoulders": {"context", "delt-anterior", "delt-lateral", "delt-posterior"},
    "posterior": {"context", "gluteus", "hamstring"},
}

#: Surfaces that deliberately map to no business zone, with their decision.
ORPHAN_SURFACE_DECISIONS = {
    "delt-anterior": "MERGE",
    "context": "IGNORE",
}

#: The seven zones with no geometry today.
ZONES_WITHOUT_SURFACE = [
    "lats", "upper_back", "biceps", "triceps", "quads", "calves", "core",
]

FORBIDDEN_ZONE_CODES = [
    "delt_ant", "delt_anterior", "anterior_deltoid",
    "pec_clavicular", "pec_sternal", "pec_sternocostal",
    "upper_pec", "lower_pec",
]


def _plate(region: str) -> str:
    return (PARTIALS / f"muscle_focus_plate_{region}.svg").read_text(encoding="utf-8")


def _path_ids(region: str) -> list[str]:
    """Every id in the plate except the svg root."""
    root = f"auren-plate-region-{region}"
    return [i for i in re.findall(r'\bid="([^"]+)"', _plate(region)) if i != root]


def _surface_token(region: str, path_id: str) -> str:
    """Strip root prefix, optional frame segment and the NNN counter."""
    tail = path_id.removeprefix(f"auren-plate-region-{region}--")
    tail = re.sub(r"-\d{3}$", "", tail)
    for frame in FRAME_ORDER:
        if tail.startswith(f"{frame}-"):
            return tail.removeprefix(f"{frame}-")
    return tail


def _view_groups(region: str) -> list[str]:
    return re.findall(r'<g class="(auren-mf-view-[a-z]+)"', _plate(region))


# ───────────────── A1 — the table is complete and true ─────────────────

def test_a1_every_business_zone_appears_in_the_contract_table():
    spec = SPEC.read_text(encoding="utf-8")
    for zone in ZONE_LABELS:
        assert f"`{zone}`" in spec, f"zone {zone} missing from the contract document"


def test_a1_declared_plate_zones_are_business_zones():
    for plate in regional_plates():
        for zone in plate.zones:
            assert zone in ZONE_LABELS, f"{plate.region} claims non-business zone {zone!r}"


def test_a1_zone_to_surface_coverage_is_four_of_eleven():
    covered = {z for plate in regional_plates() for z in plate.zones}
    assert covered == {"pecs", "delt_lat", "delt_post", "posterior"}
    assert len(ZONE_LABELS) - len(covered) == len(ZONES_WITHOUT_SURFACE)


# ───────────────── A2 — orphan surfaces are adjudicated ─────────────────

def test_a2_surface_tokens_match_the_audit():
    for region in PLATE_REGIONS:
        found = {_surface_token(region, i) for i in _path_ids(region)}
        assert found == EXPECTED_SURFACE_TOKENS[region], (
            f"{region}: surface vocabulary drifted from the contract audit"
        )


def test_a2_every_orphan_surface_has_a_recorded_decision():
    """A surface with no zone must be MERGE or IGNORE — never undecided."""
    zone_bearing = {"hero", "delt-lateral", "delt-posterior", "gluteus", "hamstring"}
    for region in PLATE_REGIONS:
        for token in EXPECTED_SURFACE_TOKENS[region]:
            if token in zone_bearing:
                continue
            assert token in ORPHAN_SURFACE_DECISIONS, (
                f"{region}/{token}: orphan surface with no contract decision"
            )


def test_a2_delt_anterior_is_merged_never_addressable():
    assert ORPHAN_SURFACE_DECISIONS["delt-anterior"] == "MERGE"
    shoulders = next(p for p in regional_plates() if p.region == "shoulders")
    assert shoulders.zones == ("delt_lat", "delt_post")


def test_a2_context_is_never_a_state_bearing_surface():
    assert ORPHAN_SURFACE_DECISIONS["context"] == "IGNORE"
    for region in PLATE_REGIONS:
        assert "context" in EXPECTED_SURFACE_TOKENS[region]


# ───────────────── A3 — orphan zones declare a fallback ─────────────────

def test_a3_zones_without_surface_are_exactly_seven():
    covered = {z for plate in regional_plates() for z in plate.zones}
    orphans = [z for z in ZONE_LABELS if z not in covered]
    assert orphans == ZONES_WITHOUT_SURFACE


def test_a3_contract_declares_macro_fallback_for_orphan_zones():
    spec = SPEC.read_text(encoding="utf-8")
    assert "macro" in spec
    assert "Jamais verte par défaut" in spec
    assert "Jamais empruntée à une région voisine" in spec


# ───────────────── A4 — no new taxonomy ─────────────────

def test_a4_no_forbidden_zone_code_in_the_taxonomy():
    for forbidden in FORBIDDEN_ZONE_CODES:
        assert forbidden not in ZONE_LABELS


def test_a4_no_forbidden_zone_code_in_the_design_contract():
    codes = {z["code"] for z in json.loads(DESIGN_CONTRACT.read_text(encoding="utf-8"))["zones"]}
    for forbidden in FORBIDDEN_ZONE_CODES:
        assert forbidden not in codes


def test_a4_surface_tokens_are_not_promoted_to_zones():
    """`delt-anterior` exists as a surface; its zone form must not."""
    for region in PLATE_REGIONS:
        for token in EXPECTED_SURFACE_TOKENS[region]:
            assert token.replace("-", "_") not in ZONE_LABELS or token in {
                "gluteus", "hamstring", "hero", "context",
            }, f"surface {token!r} leaked into the taxonomy"


# ───────────────── A5 — existing asset ids untouched ─────────────────

def test_a5_plate_id_counts_are_frozen():
    """Renaming or dropping an id changes these counts."""
    assert len(_path_ids("chest")) == 8
    assert len(_path_ids("shoulders")) == 35
    assert len(_path_ids("posterior")) == 10


def test_a5_every_path_id_carries_its_region_prefix():
    for region in PLATE_REGIONS:
        prefix = f"auren-plate-region-{region}--"
        for path_id in _path_ids(region):
            assert path_id.startswith(prefix), f"{path_id} breaks the id grammar"


def test_a5_path_ids_are_globally_unique():
    seen: set[str] = set()
    for region in PLATE_REGIONS:
        for path_id in _path_ids(region):
            assert path_id not in seen, f"duplicate id across plates: {path_id}"
            seen.add(path_id)


def test_a5_counter_suffix_is_three_digits():
    for region in PLATE_REGIONS:
        for path_id in _path_ids(region):
            assert re.search(r"-\d{3}$", path_id), f"{path_id} lacks a NNN counter"


# ───────────── §2 — the frame is carried by the group ─────────────

def test_frame_is_declared_by_the_view_group_in_every_plate():
    """chest omits the frame from its ids; the group must still declare it."""
    for plate in regional_plates():
        groups = _view_groups(plate.region)
        assert groups == [f"auren-mf-view-{f.code}" for f in plate.frames], (
            f"{plate.region}: view groups do not match declared frames"
        )


def test_chest_ids_have_no_frame_segment_and_that_is_allowed():
    """Pins the precedent the production contract grants to mono-frame plates."""
    for path_id in _path_ids("chest"):
        for frame in FRAME_ORDER:
            assert f"--{frame}-" not in path_id


def test_context_group_is_first_in_every_view():
    """The stylesheet counts group ranks — context must stay at rank 1."""
    for region in PLATE_REGIONS:
        for view_body in re.split(r'<g class="auren-mf-view-[a-z]+"', _plate(region))[1:]:
            groups = re.findall(r'<g class="(auren-mf-(?:context|hero|part))"', view_body)
            assert groups, f"{region}: a view declares no surface group"
            assert groups[0] == "auren-mf-context", (
                f"{region}: context is not the first group — CSS ranks would shift"
            )


# ───────────── §3 — the positional-CSS defect is recorded, not fixed ─────────────

def test_positional_css_defect_is_documented():
    spec = SPEC.read_text(encoding="utf-8")
    assert "OQ_POSITIONAL_CSS_01" in spec
    assert "nth-of-type" in spec


def test_positional_css_still_present_because_this_sprint_changes_no_runtime():
    """If someone fixes it, this test must be retired WITH the open question."""
    css = CSS.read_text(encoding="utf-8")
    # bounded to a single line: `[^{]*` would span newlines and merge the
    # selectors that share one rule block, counting 3 rules instead of 5 selectors.
    positional = re.findall(r"#auren-plate-region-\w+[^{\n]*nth-of-type\(\d\)", css)
    assert len(positional) == 5, (
        "positional plate rules changed — update OQ_POSITIONAL_CSS_01 before "
        "editing this expectation"
    )


# ───────────── A8 — zone_recovery is documented, not wired ─────────────

def test_a8_zone_recovery_reaches_no_template():
    hits = [
        p.relative_to(ROOT)
        for p in TEMPLATES.rglob("*.html")
        if "zone_recovery" in p.read_text(encoding="utf-8")
    ]
    assert hits == [], f"zone_recovery was wired into templates by this sprint: {hits}"


def test_a8_contract_records_the_gap_without_closing_it():
    spec = SPEC.read_text(encoding="utf-8")
    assert "zone_recovery" in spec
    assert "non comblé" in spec


# ───────────── A6 — the production contract is usable externally ─────────────

def test_a6_production_naming_contract_section_exists():
    spec = SPEC.read_text(encoding="utf-8")
    assert "## 5. Asset production naming contract" in spec


def test_a6_production_contract_states_grammar_structure_and_rejection():
    spec = SPEC.read_text(encoding="utf-8")
    assert "auren-plate-region-{region}--[{frame}-]{surface}-{NNN}" in spec
    assert "auren-mf-view-{frame}" in spec
    assert "fait rejeter une livraison" in spec


def test_a6_production_contract_uses_only_declared_frame_codes():
    spec = SPEC.read_text(encoding="utf-8")
    grammar = spec[spec.index("### 5.1"):spec.index("### 5.2")]
    for frame in FRAME_ORDER:
        assert f"`{frame}`" in grammar
