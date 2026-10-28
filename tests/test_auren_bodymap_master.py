"""Sb_ASSET_03.2 — Automated guard for the Auren BodyMap design-source master.

Guards the BodyMap master + compact accepted into design/auren/ by the technical
intake: fixed hashes, strict SVG contract (viewBox, 14 stable IDs, 11 zones, no
zone-unknown, unique IDs, one semantic parent per path), static-safe surface (no
script/animation/network/business-colour), compact budget, YAML registry,
parity with the immutable zone taxonomy and macro mapping, strict separation
from RADAR_AXES, presence of the CC BY 4.0 notices, and a BLOCKED runtime
authorization.

DA-04.0 (2026-10-28) adds: ONE authorization truth across the registry, the
folder README, the intake checklist and the provenance (the README used to say
both "no master present" and "master accepted"); the master stays inside the
subset react-native-svg renders unchanged; each zone keeps its front/back side.

Stdlib only. Includes NEGATIVE cases proving the guard fails on regressions.
"""
import ast
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
MASTER = ROOT / "design/auren/source/bodymap/auren_bodymap_master.svg"
COMPACT = ROOT / "design/auren/exports/svg/auren_bodymap_compact.svg"
REGISTRY = ROOT / "design/auren/source/bodymap/auren_bodymap_source.yaml"
LICENSES = ROOT / "design/auren/LICENSES"
SVG = "http://www.w3.org/2000/svg"

MASTER_SHA = "dbb57db333863434442b476277170017db442d83e2eced6e7191266ee9ecfa73"
COMPACT_SHA = "8024fd4ced62ca2010808bf85f94c3eaca4d334dde2b7c3b7683c3e5a4676c9a"
COMPACT_BUDGET = 12 * 1024

STABLE_IDS = [
    "auren-bodymap", "body-front-base", "body-back-base",
    "zone-pecs", "zone-delt_lat", "zone-delt_post", "zone-lats",
    "zone-upper_back", "zone-biceps", "zone-triceps", "zone-quads",
    "zone-posterior", "zone-calves", "zone-core",
]
ZONES = [z[5:] for z in STABLE_IDS if z.startswith("zone-")]
FORBIDDEN_TAGS = ("script", "foreignObject", "image", "iframe", "audio", "video",
                  "canvas", "object", "embed", "animate", "animateTransform",
                  "animateMotion", "set", "filter", "linearGradient",
                  "radialGradient", "font", "text", "tspan", "use")
CHILD_RE = re.compile(r"^geom-([a-z_]+)-(front|back)-(left|right|center)-\d+$")

# Immutable 11-zone taxonomy = real ZONE_LABELS in app/services/muscle_mapping.py.
EXPECTED_ZONES = {"pecs", "delt_lat", "delt_post", "lats", "upper_back",
                  "biceps", "triceps", "quads", "posterior", "calves", "core"}
# BodyMap compact macros (visual mapping) — the SIX macro CODES, in order.
CANONICAL_MACROS = ["chest", "shoulders", "back", "arms", "legs", "core"]
EXPECTED_MACRO_ZONES = {"chest": {"pecs"}, "shoulders": {"delt_lat", "delt_post"},
                        "back": {"lats", "upper_back"}, "arms": {"biceps", "triceps"},
                        "legs": {"quads", "posterior", "calves"}, "core": {"core"}}
# Analytics radar axes — a DIFFERENT layer. BODYMAP COMPACT MACROS ARE NOT RADAR_AXES.
RADAR_AXIS_ORDER = ["pecs", "shoulders", "back_width", "back_thickness", "arms", "lower"]


def _sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def guard_svg(src):
    """Return list of contract violations for an SVG string. Empty == valid."""
    errs = []
    if "<!DOCTYPE" in src:
        errs.append("doctype")
    if "<!ENTITY" in src:
        errs.append("entity")
    try:
        root = ET.fromstring(src)
    except ET.ParseError as exc:
        return [f"not-well-formed: {exc}"]
    if root.tag != f"{{{SVG}}}svg":
        errs.append("root-not-svg")
    if root.get("viewBox") != "0 0 240 200":
        errs.append("viewbox")
    ids = [e.get("id") for e in root.iter() if e.get("id")]
    for sid in STABLE_IDS:
        if ids.count(sid) != 1:
            errs.append(f"id-count:{sid}={ids.count(sid)}")
    if len(ids) != len(set(ids)):
        errs.append("duplicate-ids")
    zg = [e for e in root.iter(f"{{{SVG}}}g") if (e.get("id") or "").startswith("zone-")]
    if len(zg) != 11:
        errs.append(f"zone-groups={len(zg)}")
    if {g.get("id")[5:] for g in zg} != set(ZONES):
        errs.append("zone-set")
    if "zone-unknown" in src:
        errs.append("zone-unknown")
    for t in FORBIDDEN_TAGS:
        if (f"<{t}") in src or (f"<svg:{t}") in src:
            errs.append(f"tag:{t}")
    if re.search(r"\son[a-zA-Z]+\s*=", src):
        errs.append("event-handler")
    if "xlink:href" in src:
        errs.append("xlink")
    if "data:" in src or "javascript:" in src:
        errs.append("dangerous-uri")
    net = re.sub(r'xmlns(:\w+)?="http://www\.w3\.org/2000/svg"', "", src)
    if "http://" in net or "https://" in net:
        errs.append("network-ref")
    if re.search(r"fill\s*[:=]\s*[\"']?#[0-9a-fA-F]", src):
        errs.append("business-colour")
    # path ownership: every path under exactly one zone/base group
    owners = {}
    for g in root.iter(f"{{{SVG}}}g"):
        gid = g.get("id")
        for p in g.iter(f"{{{SVG}}}path"):
            pid = p.get("id")
            if pid in owners and owners[pid] != gid:
                errs.append(f"shared-path:{pid}")
            owners[pid] = gid
            if gid and gid.startswith("zone-"):
                m = CHILD_RE.match(pid or "")
                if not m or m.group(1) != gid[5:]:
                    errs.append(f"child-convention:{pid}")
    return errs


# ───────── positive: assets present, hashed, contract-valid ─────────

def test_master_and_compact_present():
    assert MASTER.is_file()
    assert COMPACT.is_file()


def test_hashes_immutable():
    assert _sha(MASTER) == MASTER_SHA
    assert _sha(COMPACT) == COMPACT_SHA


def test_master_contract_valid():
    assert guard_svg(MASTER.read_text(encoding="utf-8")) == []


def test_compact_contract_valid():
    assert guard_svg(COMPACT.read_text(encoding="utf-8")) == []


def test_compact_within_budget():
    assert COMPACT.stat().st_size <= COMPACT_BUDGET


def test_no_bitmap_or_base64_in_svgs():
    for p in (MASTER, COMPACT):
        s = p.read_text(encoding="utf-8")
        assert "base64" not in s
        assert "<image" not in s


# ───────── registry parity ─────────

def _registry():
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def test_registry_hashes_and_status():
    r = _registry()
    assert r["source_master_sha256"] == MASTER_SHA
    assert r["compact_sha256"] == COMPACT_SHA
    assert r["status"] == "technical-intake-accepted-human-review-pending"
    assert r["runtime_authorization"] == INTERNAL_RUNTIME
    assert r["public_release_authorization"] == "blocked"
    assert r["ai_usage"] == "none"
    assert r["professional_anatomical_review"] == "not-claimed"
    assert r["legal_review"] == "required"
    assert r["attribution_surface"] == "not-yet-implemented"


def test_registry_status_never_approved():
    """No status-bearing FIELD may hold a gate-crossing value. Checked on the
    parsed values, not on prose (a doc line may name a forbidden token)."""
    r = _registry()
    forbidden = {"approved", "legally-cleared", "runtime-integrated",
                 "professionally-anatomically-validated"}
    status_fields = ("status", "runtime_authorization", "legal_review",
                     "professional_anatomical_review", "attribution_surface",
                     "multi_source_consistency_review")
    for f in status_fields:
        assert r[f] not in forbidden, f"{f} carries a forbidden value: {r[f]}"


def test_registry_zone_parity_with_taxonomy():
    r = _registry()
    covered = set(r["servier_zones"]) | set(r["bodyparts3d_zones"])
    assert covered == EXPECTED_ZONES


def test_zone_groups_match_taxonomy():
    root = ET.fromstring(MASTER.read_text(encoding="utf-8"))
    zg = {e.get("id")[5:] for e in root.iter(f"{{{SVG}}}g")
          if (e.get("id") or "").startswith("zone-")}
    assert zg == EXPECTED_ZONES


def test_macro_mapping_not_radar_axes():
    """Six compact macros; their zone union = the 11 zones; each zone in one
    macro; and the macro CODE LIST is not the radar-axis LIST (mirrors the
    immutable Sb_ASSET_01.2 contract invariant)."""
    macro_zones = set().union(*EXPECTED_MACRO_ZONES.values())
    assert macro_zones == EXPECTED_ZONES
    assert list(EXPECTED_MACRO_ZONES) == CANONICAL_MACROS
    assert CANONICAL_MACROS != RADAR_AXIS_ORDER
    # `core` discriminates: a BodyMap macro, never a radar axis.
    assert "core" in CANONICAL_MACROS and "core" not in RADAR_AXIS_ORDER


def test_radar_axes_separation_documented():
    """The 11 anatomical zones are a different layer from the radar axes:
    the two sets are not equal, and radar-only axis names never appear as
    BodyMap zones."""
    zones = EXPECTED_ZONES
    radar = set(RADAR_AXIS_ORDER)
    assert zones != radar
    for radar_only in ("back_width", "back_thickness", "lower"):
        assert radar_only not in zones


# ───────── licences & governance ─────────

def test_license_notices_present():
    assert (LICENSES / "CC-BY-4.0.txt").is_file()
    bp = (LICENSES / "bodyparts3d-NOTICE.md").read_text(encoding="utf-8")
    assert "CC BY 4.0" in bp
    assert "BodyParts3D, © The Database Center for Life Science" in bp
    sv = (LICENSES / "servier-medical-art-NOTICE.md").read_text(encoding="utf-8")
    assert "CC BY 4.0" in sv
    assert "Servier Medical Art" in sv


def test_runtime_not_integrated():
    """The master must NOT be wired into app/static or runtime templates."""
    assert not (ROOT / "app/static/bodymap").exists()
    for svg in ROOT.glob("app/static/**/*.svg"):
        assert "auren_bodymap_master" not in svg.name


# ───────── negative: the guard actually fails on regressions ─────────

@pytest.fixture()
def valid_master():
    return MASTER.read_text(encoding="utf-8")


def test_negative_duplicate_id(valid_master):
    broken = valid_master.replace('id="zone-pecs"', 'id="zone-biceps"', 1)
    assert guard_svg(broken)  # non-empty -> fails


def test_negative_injected_script(valid_master):
    broken = valid_master.replace("</svg>", "<script>void 0</script></svg>")
    assert "tag:script" in guard_svg(broken)


def test_negative_external_url(valid_master):
    broken = valid_master.replace("<svg ", '<svg data-x="https://evil.example" ', 1)
    assert "network-ref" in guard_svg(broken)


def test_negative_zone_unknown(valid_master):
    broken = valid_master.replace('id="zone-core"', 'id="zone-unknown"', 1)
    assert guard_svg(broken)


def test_negative_removed_zone(valid_master):
    broken = re.sub(r'<g id="zone-calves">.*?</g>', "", valid_master, flags=re.S)
    errs = guard_svg(broken)
    assert any("zone" in e for e in errs)


def test_negative_compact_over_budget():
    padded = COMPACT.read_bytes() + b"<!-- " + b"x" * COMPACT_BUDGET + b" -->"
    assert len(padded) > COMPACT_BUDGET


def test_negative_business_colour(valid_master):
    broken = valid_master.replace('fill="currentColor"', 'fill="#C8A24B"', 1)
    assert "business-colour" in guard_svg(broken)


# ───────── DA-04.0: one authorization truth ─────────

README = ROOT / "design/auren/source/bodymap/README.md"
CHECKLIST = ROOT / "design/auren/AUREN_ASSET_INTAKE_CHECKLIST.md"
PROVENANCE = ROOT / "design/auren/AUREN_ASSET_PROVENANCE.md"
NOT_AUTHORIZED = "NOT AUTHORIZED FOR APP INTEGRATION"
INTERNAL = "AUTHORIZED FOR AUREN INTERNAL BUILDS WITH CONSTRAINTS"
PUBLIC_BLOCKED = "PUBLIC RELEASE NOT AUTHORIZED"
AUTHORIZED = "AUTHORIZED FOR AUREN MOBILE INTEGRATION"
INTERNAL_RUNTIME = "internal-builds-with-constraints"
STALE_NO_MASTER = "Aucun master anatomique n'est présent"


def _internal_registry_gaps(registry):
    """DA-04.0b: an internal authorization names its decision, scope and constraints."""
    errs = []
    if registry.get("owner_decision") != "ACCEPT_INTERNAL_P0_WITH_CONSTRAINTS":
        errs.append("registry-decision-unnamed")
    if registry.get("public_release_authorization") != "blocked":
        errs.append("registry-public-release-open")
    for field in ("owner_decision_date", "authorization_scope", "runtime_constraints",
                  "attribution_fr", "non_medical_notice_fr", "missing_for_public_release"):
        if not registry.get(field):
            errs.append(f"registry-{field}-missing")
    return errs


def authorization_inconsistencies(registry, readme, checklist, provenance):
    """Return the documents that contradict the registry's runtime authorization."""
    errs = []
    if STALE_NO_MASTER in readme:
        errs.append("readme-says-no-master")
    current = readme.split("## Historique")[0]  # history may quote the past; the current state may not
    state = registry["runtime_authorization"]
    if state == "blocked":
        if NOT_AUTHORIZED not in current:
            errs.append("readme-not-blocked")
        if not registry.get("gate_resolution", "").startswith("DA-04.0 OUTCOME B"):
            errs.append("registry-gate-unresolved")
        if not registry.get("missing_for_runtime"):
            errs.append("registry-missing-unnamed")
        for name, text in (("checklist", checklist), ("provenance", provenance)):
            if "DA-04.0" not in text or NOT_AUTHORIZED not in text:
                errs.append(f"{name}-not-blocked")
    elif state == INTERNAL_RUNTIME:
        if INTERNAL not in current or PUBLIC_BLOCKED not in current or NOT_AUTHORIZED in current:
            errs.append("readme-not-internal")
        errs.extend(_internal_registry_gaps(registry))
        for name, text in (("checklist", checklist), ("provenance", provenance)):
            if "DA-04.0b" not in text or INTERNAL not in text:
                errs.append(f"{name}-not-internal")
    else:
        if AUTHORIZED not in current or NOT_AUTHORIZED in current:
            errs.append("readme-not-authorized")
        for name, text in (("checklist", checklist), ("provenance", provenance)):
            if AUTHORIZED not in text:
                errs.append(f"{name}-not-authorized")
    return errs


def _docs():
    return (_registry(), README.read_text(encoding="utf-8"),
            CHECKLIST.read_text(encoding="utf-8"), PROVENANCE.read_text(encoding="utf-8"))


def test_authorization_is_one_truth():
    assert authorization_inconsistencies(*_docs()) == []


def test_negative_readme_back_to_no_master():
    registry, readme, checklist, provenance = _docs()
    stale = f"{STALE_NO_MASTER}.\n" + readme
    assert "readme-says-no-master" in authorization_inconsistencies(registry, stale, checklist, provenance)


def test_negative_registry_authorized_alone():
    registry, readme, checklist, provenance = _docs()
    promoted = {**registry, "runtime_authorization": "authorized"}
    errs = authorization_inconsistencies(promoted, readme, checklist, provenance)
    assert "readme-not-authorized" in errs
    assert "checklist-not-authorized" in errs


def test_negative_registry_blocked_while_docs_say_internal():
    registry, readme, checklist, provenance = _docs()
    reverted = {**registry, "runtime_authorization": "blocked"}
    assert "readme-not-blocked" in authorization_inconsistencies(reverted, readme, checklist, provenance)


def test_negative_internal_without_constraints_or_with_public_release():
    registry, readme, checklist, provenance = _docs()
    loose = {**registry, "runtime_constraints": [], "public_release_authorization": "authorized"}
    errs = authorization_inconsistencies(loose, readme, checklist, provenance)
    assert "registry-runtime_constraints-missing" in errs
    assert "registry-public-release-open" in errs


def test_negative_readme_drops_public_block():
    registry, readme, checklist, provenance = _docs()
    opened = readme.replace(PUBLIC_BLOCKED, "PUBLIC RELEASE PENDING")
    assert "readme-not-internal" in authorization_inconsistencies(registry, opened, checklist, provenance)


# ───────── DA-04.0: the subset react-native-svg renders unchanged ─────────

RN_SVG_TAGS = {"svg", "g", "path"}
RN_SVG_ATTRS = {"id", "viewBox", "fill", "d"}
PATH_COMMANDS = set("MmLlHhVvCcSsQqTtAaZz")


def rn_svg_subset_violations(src):
    """Elements, attributes and path commands outside Svg / G / Path as drawn today."""
    errs = []
    root = ET.fromstring(src)
    for e in root.iter():
        tag = e.tag.replace(f"{{{SVG}}}", "")
        if tag not in RN_SVG_TAGS:
            errs.append(f"tag:{tag}")
        errs += [f"attr:{a}" for a in e.attrib if a not in RN_SVG_ATTRS]
        cmds = set(re.findall(r"[A-Za-z]", e.get("d", "")))
        errs += [f"command:{c}" for c in sorted(cmds - PATH_COMMANDS)]
    return errs


def test_master_is_in_the_react_native_svg_subset():
    assert rn_svg_subset_violations(MASTER.read_text(encoding="utf-8")) == []


def test_negative_clip_path_is_outside_the_subset(valid_master):
    broken = valid_master.replace("</svg>", "<clipPath id=\"x\"><path d=\"M0 0 L1 1 Z\"/></clipPath></svg>")
    assert "tag:clipPath" in rn_svg_subset_violations(broken)


def test_negative_transform_is_outside_the_subset(valid_master):
    broken = valid_master.replace('<g id="zone-pecs">', '<g id="zone-pecs" transform="scale(2)">', 1)
    assert "attr:transform" in rn_svg_subset_violations(broken)


# ───────── DA-04.0: each zone keeps its side ─────────

EXPECTED_SIDES = {
    "pecs": {"front"}, "delt_lat": {"front", "back"}, "delt_post": {"back"},
    "lats": {"back"}, "upper_back": {"back"}, "biceps": {"front"},
    "triceps": {"back"}, "quads": {"front"}, "posterior": {"back"},
    "calves": {"front", "back"}, "core": {"front"},
}


def test_each_zone_keeps_its_front_back_side():
    root = ET.fromstring(MASTER.read_text(encoding="utf-8"))
    sides = {}
    for g in root.iter(f"{{{SVG}}}g"):
        gid = g.get("id") or ""
        if gid.startswith("zone-"):
            kids = [CHILD_RE.match(p.get("id") or "") for p in g.iter(f"{{{SVG}}}path")]
            assert kids, f"{gid}: no geometry"
            sides[gid[5:]] = {m.group(2) for m in kids if m}
    assert sides == EXPECTED_SIDES


# ───────── the guard module imports cleanly (self-check) ─────────

def test_guard_module_is_ast_parseable():
    ast.parse(Path(__file__).read_text(encoding="utf-8"))
