"""Sb_BODYMAP_FRAME_ATLAS_01 — acceptance guards for the declarative frame contract.

Covers A1 (taxonomy frozen), A2 (no delt_ant), A3 (no pecs split), A4 (no-JS),
A6 (honest unknown / honest absence), A7 (declarative source), A8 (shipped plates
preserved) and A9 (non-medical copy). A5 (360 px) lives in
tests/test_bodymap_frame_atlas_viewport.py because it needs a browser.

The load-bearing idea behind these tests: the *business model* owns the eleven
zones, and the *visual layer* may not add a twelfth by the back door — not as a
zone code, not as a plate id promoted to a zone, not as a frame that pretends to
be one.
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

from app.services.bodymap_frames import (
    FRAME_LABELS,
    FRAME_ORDER,
    REGIONAL_PLATES,
    RENDER_MACRO,
    RENDER_NONE,
    RENDER_PLATE,
    geometry_coverage,
    plate_for_region,
    regional_plates,
    resolve_zone_surface,
    zone_surfaces,
)
from app.services.muscle_mapping import (
    ZONE_LABELS,
    ZONE_MEASUREMENT,
    ZONE_VOLUME_TARGET,
)

ROOT = Path(__file__).resolve().parent.parent
CONTRACT = ROOT / "design" / "auren" / "source" / "bodymap" / "auren_bodymap_mapping.yaml"
WRAPPER = ROOT / "app" / "templates" / "_partials" / "muscle_focus.html"
SELECTOR = ROOT / "app" / "templates" / "_partials" / "bodymap_frame_selector.html"
SERVICE = ROOT / "app" / "services" / "bodymap_frames.py"
CSS = ROOT / "app" / "static" / "css" / "app.css"
WA_TEMPLATE = ROOT / "app" / "templates" / "_partials" / "worked_area_body_map.html"

CANONICAL_ZONES = [
    "pecs", "delt_lat", "delt_post", "lats", "upper_back",
    "biceps", "triceps", "quads", "posterior", "calves", "core",
]

#: Zone codes this build is forbidden to introduce. Architect decision:
#: Option A for the shoulders, pectoral split deferred to OQ_PEC_SPLIT_01.
FORBIDDEN_ZONE_CODES = [
    "delt_ant", "delt_anterior", "anterior_deltoid",
    "pec_clavicular", "pec_sternal", "pec_sternocostal",
    "upper_pec", "lower_pec",
]


def _contract() -> dict:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def _wa_zone_to_region() -> dict[str, str]:
    html = WA_TEMPLATE.read_text(encoding="utf-8")
    match = re.search(r"\{%\s*set\s+_WA_ZONE_TO_REGION\s*=\s*(\{.*?\})\s*%\}", html, re.DOTALL)
    assert match, "could not locate _WA_ZONE_TO_REGION literal"
    return ast.literal_eval(match.group(1))


# ───────────────────────── A1 — taxonomy unchanged ─────────────────────────

def test_a1_zone_labels_exact_list():
    assert list(ZONE_LABELS) == CANONICAL_ZONES


def test_a1_every_zone_table_covers_the_same_eleven():
    for table in (ZONE_LABELS, ZONE_VOLUME_TARGET, ZONE_MEASUREMENT):
        assert sorted(table) == sorted(CANONICAL_ZONES)


def test_a1_design_contract_still_mirrors_eleven_zones():
    codes = [z["code"] for z in _contract()["zones"]]
    assert codes == CANONICAL_ZONES


def test_a1_macro_mapping_unchanged():
    assert sorted(_wa_zone_to_region()) == sorted(CANONICAL_ZONES)


def test_a1_frame_module_declares_no_zone_of_its_own():
    """Every zone a plate claims must already exist in the business taxonomy."""
    for plate in REGIONAL_PLATES:
        for zone in plate.zones:
            assert zone in ZONE_LABELS, f"{plate.region} claims non-business zone {zone!r}"


# ─────────────────── A2 / A3 — no new business zone ────────────────────────

def test_a2_a3_no_forbidden_zone_code_in_business_tables():
    tables = {
        "ZONE_LABELS": ZONE_LABELS,
        "ZONE_VOLUME_TARGET": ZONE_VOLUME_TARGET,
        "ZONE_MEASUREMENT": ZONE_MEASUREMENT,
        "_WA_ZONE_TO_REGION": _wa_zone_to_region(),
    }
    for name, table in tables.items():
        for forbidden in FORBIDDEN_ZONE_CODES:
            assert forbidden not in table, f"{forbidden!r} leaked into {name}"


def test_a2_a3_no_forbidden_zone_code_in_design_contract():
    codes = {z["code"] for z in _contract()["zones"]}
    for forbidden in FORBIDDEN_ZONE_CODES:
        assert forbidden not in codes


def test_a2_shoulders_plate_exposes_only_the_two_business_zones():
    """Option A: the plate holds delt-anterior surfaces, the model does not."""
    shoulders = plate_for_region("shoulders")
    assert shoulders is not None
    assert shoulders.zones == ("delt_lat", "delt_post")


def test_a3_pecs_remains_one_zone():
    surface = resolve_zone_surface("pecs")
    assert surface.render_mode == RENDER_PLATE
    chest = plate_for_region("chest")
    assert chest is not None
    assert chest.zones == ("pecs",)


def test_a2_a3_frames_are_viewpoints_not_zones():
    """A frame code must never collide with a zone code."""
    for frame in FRAME_ORDER:
        assert frame not in ZONE_LABELS


# ───────────────────────── A4 — no JS required ─────────────────────────────

def test_a4_selector_partial_has_no_script_or_handler():
    src = SELECTOR.read_text(encoding="utf-8").lower()
    for token in ("<script", "onclick", "onchange", "oninput", "javascript:", "data-js"):
        assert token not in src, f"selector must not need JS: found {token!r}"


def test_a4_selector_uses_native_radio_inputs():
    src = SELECTOR.read_text(encoding="utf-8")
    assert 'type="radio"' in src
    assert "<fieldset" in src
    assert "<label" in src


def test_a4_no_webgl_or_canvas_introduced():
    for path in (SELECTOR, SERVICE, WRAPPER):
        src = path.read_text(encoding="utf-8").lower()
        for token in ("webgl", "<canvas", "three.js", "getcontext"):
            assert token not in src, f"{path.name} must stay SSR-only: found {token!r}"


# ─────────────── A6 — honest unknown and honest absence ────────────────────

def test_a6_unknown_inputs_never_produce_geometry():
    for value in (None, "unknown", "", "delt_ant", "not_a_zone"):
        surface = resolve_zone_surface(value)
        assert surface.render_mode == RENDER_NONE, f"{value!r} must not resolve to anatomy"
        assert surface.has_geometry is False


def test_a6_unknown_never_borrows_a_neighbouring_plate():
    assert resolve_zone_surface("unknown").plate is None


def test_a6_zone_without_plate_falls_back_to_macro_not_plate():
    """The seven ungeometried zones must say so rather than look available."""
    without = [s for s in zone_surfaces() if not s.has_geometry]
    assert [s.zone for s in without] == [
        "lats", "upper_back", "biceps", "triceps", "quads", "calves", "core",
    ]
    for surface in without:
        assert surface.render_mode == RENDER_MACRO
        assert surface.frames == ()


def test_a6_socle_exposes_all_eleven_zones_even_without_geometry():
    assert [s.zone for s in zone_surfaces()] == CANONICAL_ZONES


def test_a6_coverage_reports_the_real_numbers():
    assert geometry_coverage() == {
        "zones_total": 11,
        "zones_with_plate": 4,
        "zones_without_plate": 7,
        "plates_produced": 3,
    }


# ───────────────────── A7 — declarative, not scattered ─────────────────────

def test_a7_wrapper_holds_no_per_frame_branching():
    src = WRAPPER.read_text(encoding="utf-8")
    for token in ("mf-shoulders-front", "mf-shoulders-back", 'name="mf-'):
        assert token not in src, f"frame wiring must live in the contract, not the template: {token!r}"


def test_a7_wrapper_delegates_to_the_generic_macro():
    src = WRAPPER.read_text(encoding="utf-8")
    assert "bodymap_frame_selector.html" in src
    assert "frame_selector(" in src


def test_a7_selector_never_names_a_region_or_a_frame():
    """Generic over N: no `if region ==` and no hard-coded viewpoint."""
    src = SELECTOR.read_text(encoding="utf-8")
    for token in ("shoulders", "chest", "posterior", '"front"', "'front'"):
        assert token not in src, f"selector must stay generic: found {token!r}"


def test_a7_css_offsets_are_index_based_not_region_based():
    css = CSS.read_text(encoding="utf-8")
    assert "muscle-focus__frame--strip" in css
    assert "--mf-frames" in css
    assert "#mf-shoulders-back:checked" not in css, "region-specific offset rule must be gone"


def test_a7_frames_are_declared_in_canonical_order():
    for plate in regional_plates():
        codes = [f.code for f in plate.frames]
        assert codes == sorted(codes, key=FRAME_ORDER.index), f"{plate.region}: frames out of order"


def test_a7_only_declared_frame_codes_are_used():
    for plate in regional_plates():
        for frame in plate.frames:
            assert frame.code in FRAME_ORDER
            assert frame.label == FRAME_LABELS[frame.code]


# ───────────── A7 — design contract mirrors runtime, no drift ──────────────

def test_a7_contract_frames_mirror_runtime_vocabulary():
    declared = [f["code"] for f in _contract()["frames"]]
    assert declared == list(FRAME_ORDER)


def test_a7_contract_frame_labels_mirror_runtime():
    for frame in _contract()["frames"]:
        assert frame["label_fr"] == FRAME_LABELS[frame["code"]]


def test_a7_contract_frames_are_declared_as_viewpoints():
    for frame in _contract()["frames"]:
        assert frame["nature"] == "viewpoint"


def test_a7_contract_regional_plates_mirror_runtime():
    contract_plates = {
        p["region"]: (tuple(p["zones"]), tuple(p["frames_produced"]))
        for p in _contract()["regional_plates"]
    }
    runtime_plates = {
        p.region: (p.zones, tuple(f.code for f in p.frames))
        for p in regional_plates()
    }
    assert contract_plates == runtime_plates


def test_a7_contract_records_option_a_for_the_shoulders():
    decision = _contract()["shoulders_anterior_decision"]
    assert "OPTION A" in decision["decision"]
    assert "delt_ant" in decision["statement"]


def test_a3_contract_records_the_pec_split_as_deferred():
    oqs = {q["id"]: q for q in _contract()["open_questions"]}
    assert "OQ_PEC_SPLIT_01" in oqs
    assert oqs["OQ_PEC_SPLIT_01"]["status"] == "documented-not-built"


# ──────────────────── A8 — shipped plates preserved ────────────────────────

def test_a8_produced_plates_match_shipped_geometry():
    """Frame counts must match the SVGs actually in the repo, not aspirations."""
    assert plate_for_region("chest").frame_count == 1
    assert plate_for_region("shoulders").frame_count == 2
    assert plate_for_region("posterior").frame_count == 1


def test_a8_shoulders_keeps_front_then_back():
    frames = [f.code for f in plate_for_region("shoulders").frames]
    assert frames == ["front", "back"]


def test_a8_single_frame_plates_render_no_selector():
    for region in ("chest", "posterior"):
        assert plate_for_region(region).is_strip is False


def test_a8_no_frame_declared_without_produced_geometry():
    """Guards the failure mode where the selector offers an empty panel."""
    partials = ROOT / "app" / "templates" / "_partials"
    for plate in regional_plates():
        svg = partials / Path(plate.partial).name
        assert svg.is_file(), f"{plate.region}: declared plate partial missing"


# ────────────────────────── A9 — non-medical ───────────────────────────────

MEDICAL_TOKENS = [
    "emg", "activation", "diagnostic", "diagnostiq", "blessure",
    "patholog", "clinique", "prescription", "sollicitation",
]


def _user_visible_copy() -> dict[str, str]:
    """Every string this build can put in front of a reader.

    Deliberately excludes docstrings and Jinja comments: the module docstring
    *disclaims* medical meaning, and a guard that flags its own disclaimer is
    noise, not protection. What matters is what renders.
    """
    copy = {f"label:{code}": label for code, label in FRAME_LABELS.items()}
    for plate in regional_plates():
        for frame in plate.frames:
            if frame.landmark:
                copy[f"landmark:{plate.region}/{frame.code}"] = frame.landmark
    markup = SELECTOR.read_text(encoding="utf-8")
    copy["selector-markup"] = re.sub(r"\{#.*?#\}", "", markup, flags=re.DOTALL)
    return copy


def test_a9_no_medical_or_activation_claim_in_visible_copy():
    for where, text in _user_visible_copy().items():
        low = text.lower()
        for token in MEDICAL_TOKENS:
            assert token not in low, f"medical claim in {where}: {token!r}"


def test_a9_landmarks_describe_bones_not_effort():
    """A landmark says which way the body faces; it never quantifies work."""
    for plate in regional_plates():
        for frame in plate.frames:
            if frame.landmark is None:
                continue
            low = frame.landmark.lower()
            for token in ("%", "effort", "intensité", "sollicit", "récupér"):
                assert token not in low, f"{plate.region}/{frame.code}: {token!r} in landmark"
