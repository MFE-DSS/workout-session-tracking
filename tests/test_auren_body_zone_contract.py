"""Sb_ASSET_01.2 — Auren Body Zone Taxonomy & Mapping Contract guard.

Validates the design contract `design/auren/source/bodymap/auren_bodymap_mapping.yaml`
(YAML 1.2 in JSON-compatible syntax, read with the standard library `json` — no
PyYAML) against itself AND against runtime truth:

  - exactly eleven zones, canonical order, unique codes;
  - labels_fr identical to ZONE_LABELS (parity);
  - unknown is a qualification state, never an anatomical zone;
  - exactly six compact macros; union = the eleven zones; each zone in one macro;
  - macro mapping identical to _WA_ZONE_TO_REGION (parity, ast.literal_eval);
  - compact macros are explicitly NOT RADAR_AXES; RADAR_AXES/ORDER untouched;
  - stable SVG ids (one per zone, no zone-unknown, no gendered id, unique);
  - exactly five presentation states; exactly three body variants (none produced);
  - NO geometry (path/polygon/coordinates/activation/percentage/EMG) in data;
  - owner IP ownership is not presented as legally proven;
  - the descriptor still yields only the eleven known codes or `unknown`.

Standard library only. Design contract mirrors runtime truth; it does not
replace it.
"""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path

from app.services.body_map_descriptor import build_body_map_descriptor
from app.services.muscle_mapping import RADAR_AXES, RADAR_AXIS_ORDER, ZONE_LABELS

ROOT = Path(__file__).resolve().parent.parent
CONTRACT = ROOT / "design" / "auren" / "source" / "bodymap" / "auren_bodymap_mapping.yaml"
TAXONOMY = ROOT / "design" / "auren" / "AUREN_BODY_ZONE_TAXONOMY.md"
WA_TEMPLATE = ROOT / "app" / "templates" / "_partials" / "worked_area_body_map.html"

CANONICAL_ZONES = [
    "pecs", "delt_lat", "delt_post", "lats", "upper_back",
    "biceps", "triceps", "quads", "posterior", "calves", "core",
]
CANONICAL_MACROS = ["chest", "shoulders", "back", "arms", "legs", "core"]


def _contract() -> dict:
    """Parse the JSON-compatible YAML with the stdlib (no PyYAML)."""
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def _wa_zone_to_region() -> dict[str, str]:
    """Extract the Jinja literal _WA_ZONE_TO_REGION via ast.literal_eval —
    no HTML render, no dependency."""
    html = WA_TEMPLATE.read_text(encoding="utf-8")
    m = re.search(r"\{%\s*set\s+_WA_ZONE_TO_REGION\s*=\s*(\{.*?\})\s*%\}", html, re.DOTALL)
    assert m, "could not locate _WA_ZONE_TO_REGION literal in template"
    return ast.literal_eval(m.group(1))


# ───────── 22.1 parsing ─────────


def test_contract_parses_with_stdlib_json():
    d = _contract()
    assert d["schema"] == "auren.body-zone-mapping"
    assert d["schema_version"] == 1
    assert d["contract_version"] == "1.0.0"


# ───────── 22.2 taxonomy ─────────


def test_exactly_eleven_zones_canonical_order():
    d = _contract()
    codes = [z["code"] for z in d["zones"]]
    assert codes == CANONICAL_ZONES, f"zones must be exactly {CANONICAL_ZONES} in order, got {codes}"


def test_zone_codes_unique():
    codes = [z["code"] for z in _contract()["zones"]]
    assert len(codes) == len(set(codes))


def test_labels_fr_match_zone_labels():
    for z in _contract()["zones"]:
        assert z["label_fr"] == ZONE_LABELS[z["code"]], (
            f"label_fr mismatch for {z['code']}: {z['label_fr']!r} != {ZONE_LABELS[z['code']]!r}"
        )


def test_zone_labels_covered_exactly():
    contract_codes = {z["code"] for z in _contract()["zones"]}
    assert contract_codes == set(ZONE_LABELS), "contract zones must mirror ZONE_LABELS exactly"


def test_unknown_absent_from_zones():
    codes = [z["code"] for z in _contract()["zones"]]
    assert "unknown" not in codes


def test_unknown_state_is_not_anatomy():
    u = _contract()["unknown_state"]
    assert u["code"] == "unknown"
    assert u["anatomical_zone"] is False


# ───────── 22.3 mapping ─────────


def test_exactly_six_macros_canonical():
    macros = _contract()["compact_macros"]
    assert [m["code"] for m in macros] == CANONICAL_MACROS


def test_each_zone_belongs_to_exactly_one_macro():
    d = _contract()
    seen: dict[str, str] = {}
    for m in d["compact_macros"]:
        for z in m["zones"]:
            assert z not in seen, f"zone {z} appears in two macros: {seen.get(z)} and {m['code']}"
            seen[z] = m["code"]
    assert set(seen) == set(CANONICAL_ZONES)


def test_macro_union_equals_eleven_zones():
    union = [z for m in _contract()["compact_macros"] for z in m["zones"]]
    assert sorted(union) == sorted(CANONICAL_ZONES)
    assert len(union) == len(set(union))


def test_zone_compact_macro_matches_macro_membership():
    d = _contract()
    z2m_field = {z["code"]: z["compact_macro"] for z in d["zones"]}
    z2m_macros = {z: m["code"] for m in d["compact_macros"] for z in m["zones"]}
    assert z2m_field == z2m_macros


def test_mapping_matches_runtime_wa_zone_to_region():
    z2m = {z["code"]: z["compact_macro"] for z in _contract()["zones"]}
    assert z2m == _wa_zone_to_region(), "contract macro mapping must equal _WA_ZONE_TO_REGION"


def test_no_extra_codes_in_mapping():
    region = _wa_zone_to_region()
    assert set(region) == set(CANONICAL_ZONES)


# ───────── 22.4 analytics separation ─────────


def test_contract_declares_not_radar_axes():
    src = CONTRACT.read_text(encoding="utf-8") + TAXONOMY.read_text(encoding="utf-8")
    assert "BODYMAP COMPACT MACROS ARE NOT RADAR_AXES" in src


def test_macros_differ_from_radar_axes():
    macros = [m["code"] for m in _contract()["compact_macros"]]
    assert macros != list(RADAR_AXES.keys()), "compact macros must not equal RADAR_AXES keys"


def test_radar_axes_untouched_by_this_build():
    # Guard the analytics model against accidental drift in this sprint.
    assert RADAR_AXIS_ORDER == ["pecs", "shoulders", "back_width", "back_thickness", "arms", "lower"]
    assert set(RADAR_AXES) == set(RADAR_AXIS_ORDER)
    assert "core" not in RADAR_AXES  # BodyMap has core; radar does not


# ───────── 22.5 stable SVG ids ─────────


def test_stable_svg_ids_exact_set():
    expected = ["auren-bodymap", "body-front-base", "body-back-base"] + [
        f"zone-{c}" for c in CANONICAL_ZONES
    ]
    assert _contract()["stable_svg_ids"] == expected


def test_one_svg_id_per_zone():
    d = _contract()
    for z in d["zones"]:
        assert z["stable_svg_id"] == f"zone-{z['code']}"
        assert z["stable_svg_id"] in d["stable_svg_ids"]


def test_no_zone_unknown_id():
    assert "zone-unknown" not in _contract()["stable_svg_ids"]


def test_no_gendered_svg_id():
    lowered = " ".join(_contract()["stable_svg_ids"]).lower()
    for token in ("male", "female", "man", "woman", "-m-", "-f-"):
        assert token not in lowered, f"gendered token in svg ids: {token}"


def test_svg_ids_unique():
    ids = _contract()["stable_svg_ids"]
    assert len(ids) == len(set(ids))


# ───────── 22.6 presentation states ─────────


def test_exactly_five_presentation_states():
    states = [s["code"] for s in _contract()["presentation_states"]]
    assert states == ["neutral", "primary", "secondary", "unknown", "disabled"]


# ───────── 22.7 body variants ─────────


def test_exactly_three_body_variants_none_available():
    variants = _contract()["body_variants"]
    assert [v["code"] for v in variants] == [
        "male_neutral_v1", "female_neutral_v1", "neutral_abstract_v1",
    ]
    assert all(v["available"] is False for v in variants)
    assert _contract()["geometry_status"] == "NOT YET PRODUCED"


# ───────── 22.8 no geometry ─────────


def test_no_geometry_in_zone_data():
    """Zone entries carry no geometric/physiological data."""
    forbidden_keys = {
        "path", "paths", "polygon", "polygons", "coordinates", "coords",
        "activation", "percentage", "percent", "emg", "origin", "insertion",
        "stabilizers", "intensity",
    }
    for z in _contract()["zones"]:
        offending = forbidden_keys & set(z)
        assert not offending, f"geometry/physiology keys in zone {z['code']}: {offending}"


def test_contract_has_no_svg_geometry_tokens_in_values():
    """No path/polygon/EMG values hidden in the machine-readable structure.
    (Normative prose lives in the .md; the .yaml data must stay geometry-free.)"""
    d = _contract()
    # Serialise only the data structure (values), scan for geometry leakage.
    blob = json.dumps({
        "zones": d["zones"],
        "compact_macros": d["compact_macros"],
        "stable_svg_ids": d["stable_svg_ids"],
    }).lower()
    for token in ("<path", "<polygon", " d=", "viewbox", "activation%", "emg"):
        assert token not in blob, f"geometry token leaked into contract data: {token}"


# ───────── 22.9 owner IP nuance ─────────


def test_owner_ip_ownership_not_presented_as_proven():
    prov = (ROOT / "design" / "auren" / "AUREN_ASSET_PROVENANCE.md").read_text(encoding="utf-8")
    assert "IP OWNERSHIP NOT LEGALLY VERIFIED" in prov
    assert "ip_ownership_status: not-legally-reviewed" in prov
    # no runtime entry claims verified IP ownership
    assert "ip_ownership_status: verified" not in prov


# ───────── 22.10 evolving guard interplay ─────────


def test_contract_is_allowlisted_not_binary():
    rel = str(CONTRACT.relative_to(ROOT))
    assert rel == "design/auren/source/bodymap/auren_bodymap_mapping.yaml"
    assert CONTRACT.suffix.lower() in {".yaml", ".yml", ".json"}


def test_no_master_svg_next_to_contract():
    bodymap_dir = CONTRACT.parent
    svgs = list(bodymap_dir.rglob("*.svg")) + list(bodymap_dir.rglob("*.png"))
    assert not svgs, f"unexpected asset next to the contract: {svgs}"


# ───────── 23/24 descriptor parity (runtime untouched) ─────────


def test_descriptor_yields_only_known_codes_or_unknown():
    known = set(CANONICAL_ZONES) | {"unknown"}
    # unknown path
    d = build_body_map_descriptor("qwerty nonexistent movement zzz")
    assert d["status"] == "unknown"
    assert d["primary_zone"] == "unknown"
    assert d["secondary_zones"] == []
    assert d["needs_qualification"] is True
    # mapped path — a well-known exercise resolves to canonical codes
    d2 = build_body_map_descriptor("développé couché")
    assert d2["primary_zone"] in known
    assert all(z in known for z in d2["secondary_zones"])
    if d2["status"] == "mapped":
        assert d2["needs_qualification"] is False
        # primary not duplicated in secondary
        assert d2["primary_zone"] not in d2["secondary_zones"]
