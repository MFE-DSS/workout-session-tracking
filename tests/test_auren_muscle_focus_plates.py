"""Sb_ASSET_03B.2R-D1 — Auren Muscle Focus P0 Regional Plate guard.

Co-written with the §5bis enactment (design/auren/AUREN_STYLE_RULES.md) and the first P0 geometry.
Enforces, on the three frozen P0 regional plate candidates intaken under design/auren/source/muscle-focus/:

  - byte-integrity: each SVG matches the C3 freeze-manifest sha256 (no drift, no rewrite);
  - ID contract: root id ∈ the 3 P0 roots; NO zone-* / master id emitted (disjoint from Layer-A API);
    child ids prefix-isolated by the plate root (ID Contract §3bis P0 scheme);
  - no forbidden attribute (score/data-score/value/activation/emg) and no hardcoded business hex;
  - no lying / measurement token (approved, legally-cleared, EMG, %, activation, recruitment, …);
  - text lives outside the plate SVG (caption in adjacent HTML — §5bis / §4);
  - descriptor registry (v0.2.0) valid: literals non_medical:true / scored:false / caption_mirrors_overlay:true,
    ai_usage NONE, attribution_required true, parts ⊆ ID-contract §4, mode/zone/exercise-granularity rules;
  - chest diagnostic partition EXCLUDED (parts empty, NOT ACCEPTED, forbidden at runtime);
  - posterior hamstring individual provenance preserved (NOT a unified source mesh);
  - §5bis carve-out is bounded to plate/N2/N3 (auren-plate-*) and §5 stays a flat prohibition for auren-bodymap;
  - NO entry is approved / professionally / legally cleared; ASSET INTEGRATION GATE stays BLOCKED.

Internal synthetic review only — NOT a qualified professional anatomical review (not claimed). Guard mirrors
tests/test_auren_bodymap_master.py / test_auren_asset_governance.py.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
MF = ROOT / "design" / "auren" / "source" / "muscle-focus"
REGISTRY = MF / "auren_muscle_focus_registry.yaml"
STYLE_RULES = ROOT / "design" / "auren" / "AUREN_STYLE_RULES.md"

FREEZE_SHA = {
    "auren-plate-region-chest": "7a4167eac1db085f1cfb41ae2b2465a3b2c720a4978361eef69e422b104bddfd",
    "auren-plate-region-shoulders": "5eb7bedfa031b2e9fe29e60c1a17c1fe2822a46c0a3153f2fab14951fcc94983",
    "auren-plate-region-posterior": "b84c8bceea47455c88d4ee2d3117a6387383187109a20850db2d54feaa71710f",
}
P0_ROOTS = set(FREEZE_SHA)
ZONE_CODES = {"pecs", "delt_lat", "delt_post", "lats", "upper_back", "biceps", "triceps",
              "quads", "posterior", "calves", "core"}
MACROS = {"chest", "shoulders", "back", "arms", "legs", "core"}
MODES = {"muscle-heads", "grouped-honest", "whole-region"}
PART_REGISTRY = {
    "part-pecs-clavicular", "part-pecs-sternocostal", "part-delt_lat-anterior", "part-delt_lat-lateral",
    "part-delt_post-posterior", "part-biceps-long", "part-biceps-short", "part-triceps-long",
    "part-triceps-lateral", "part-triceps-medial", "part-quads-rectus", "part-quads-vastus_lateralis",
    "part-quads-vastus_medialis", "part-quads-vastus_intermedius", "part-calves-gastrocnemius",
    "part-calves-soleus", "part-core-rectus", "part-core-oblique_external", "part-core-transverse",
    "part-upper_back-trapezius", "part-upper_back-rhomboid", "part-posterior-gluteus", "part-posterior-hamstring",
}
MASTER_IDS = {"auren-bodymap", "body-front-base", "body-back-base"}
LYING_TOKENS = ("approved", "legally-cleared", "legally cleared", "anatomically-validated-professionally",
                "runtime-ready", "integration-authorized")
MEASURE_TOKENS = ("emg", "activation", "recruitment", "clinique", "clinical")


def _svg(root):
    return (MF / f"{root}.svg").read_text(encoding="utf-8")


def _registry():
    return yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))


def _plates():
    return {p["plate_id"]: p for p in _registry()["plates"]}


# ───────── byte-integrity vs the freeze manifest ─────────

def test_plate_svgs_present_and_match_freeze_sha():
    for root, want in FREEZE_SHA.items():
        p = MF / f"{root}.svg"
        assert p.is_file(), f"missing plate: {root}.svg"
        got = hashlib.sha256(p.read_bytes()).hexdigest()
        assert got == want, f"{root}: sha drift {got} != freeze {want}"


def test_svg_set_is_exactly_the_three_plates():
    actual = {p.stem for p in MF.glob("*.svg")}
    assert actual == P0_ROOTS, f"plate SVG set drift: {actual}"


# ───────── ID contract (disjoint from master API; prefix isolation) ─────────

def test_root_ids_are_the_p0_roots():
    for root in P0_ROOTS:
        assert f'id="{root}"' in _svg(root), f"{root}: root id missing/incorrect"


def test_no_zone_or_master_id_emitted():
    for root in P0_ROOTS:
        ids = set(re.findall(r'id="([^"]+)"', _svg(root)))
        assert not any(i.startswith("zone-") for i in ids), f"{root}: emits a zone-* id"
        assert not (ids & MASTER_IDS), f"{root}: emits a master id"


def test_child_ids_prefix_isolated_by_root():
    for root in P0_ROOTS:
        ids = [i for i in re.findall(r'id="([^"]+)"', _svg(root)) if i != root]
        for i in ids:
            assert i.startswith(root + "--"), f"{root}: child id not prefix-isolated: {i}"


def test_no_duplicate_ids_within_a_plate():
    for root in P0_ROOTS:
        ids = re.findall(r'id="([^"]+)"', _svg(root))
        assert len(ids) == len(set(ids)), f"{root}: duplicate id"


# ───────── SVG safety (no data, no business colour, no text inside plate) ─────────

def test_no_forbidden_attributes_or_business_hex():
    for root in P0_ROOTS:
        s = _svg(root).lower()
        for attr in ("score", "data-score", 'value="', "activation", "emg"):
            assert attr not in s, f"{root}: forbidden attribute/token: {attr}"
        assert not re.search(r'(fill|stroke)\s*[:=]\s*["\']?#[0-9a-f]{3,6}', s), f"{root}: hardcoded business hex"


def test_no_text_inside_plate_svg():
    # §5bis / §4: caption lives in adjacent HTML, never in the plate SVG.
    for root in P0_ROOTS:
        s = _svg(root).lower()
        for el in ("<text", "<tspan", "<foreignobject"):
            assert el not in s, f"{root}: text element inside plate SVG: {el}"


def test_no_script_or_external_resource():
    for root in P0_ROOTS:
        s = _svg(root).lower()
        assert "<script" not in s, f"{root}: script"
        assert "onload" not in s, f"{root}: handler"
        assert not re.search(r'href="https?:(?!//www\.w3\.org)', s), f"{root}: external URL"


# ───────── descriptor registry validity (schema v0.2.0) ─────────

def test_registry_versions_and_shape():
    r = _registry()
    assert r["contract_version"] == "0.2.0"
    assert r["schema_version"] == "0.2.0"
    assert r["ai_usage"] == "NONE"
    assert {p["plate_id"] for p in r["plates"]} == P0_ROOTS


def test_each_descriptor_invariants():
    for pid, d in _plates().items():
        assert d["level"] == "2-regional"
        assert d["mode"] in MODES
        assert d["schema_version"] == "0.2.0"
        assert d["zone_codes"]
        assert set(d["zone_codes"]) <= ZONE_CODES
        assert d["macro"] in MACROS
        assert d["region_key_kind"] in ("macro", "zone")   # REQUIS since level=2-regional
        assert set(d["views"]) <= {"front", "back"}         # N2 ⊆ {front, back}
        assert set(d.get("parts") or []) <= PART_REGISTRY
        assert (d.get("markers") or []) == []               # N2 = no markers (overlay N3 only)
        assert d["exercise_link_granularity"] == "zone"     # hard: never part/head
        assert d["exercise_link_mode"] == "list"
        assert d["attribution_required"] is True
        assert d["ai_usage"] == "NONE"
        assert d["non_medical"] is True                     # literal
        assert d["scored"] is False                         # literal
        assert d["caption_mirrors_overlay"] is True
        assert d["sha256"] == FREEZE_SHA[pid]


def test_whole_region_mode_reserved_to_chest_partition_excluded():
    plates = _plates()
    chest = plates["auren-plate-region-chest"]
    assert chest["mode"] == "whole-region"
    assert chest["parts"] == []                             # partition excluded -> no sub-heads claimed
    assert "NOT ACCEPTED" in chest["diagnostic_partition"]
    assert "FORBIDDEN AT RUNTIME" in chest["diagnostic_partition"]


def test_shoulders_source_segmented_mapping_traceable():
    sh = _plates()["auren-plate-region-shoulders"]
    assert sh["mode"] == "muscle-heads"
    assert set(sh["parts"]) == {"part-delt_lat-anterior", "part-delt_lat-lateral", "part-delt_post-posterior"}
    assert set(sh["views"]) == {"front", "back"}


def test_posterior_grouped_honest_individual_provenance():
    po = _plates()["auren-plate-region-posterior"]
    assert po["mode"] == "grouped-honest"
    assert po["hamstring_unified_source_mesh"] is False
    assert len(po["hamstring_individual_sources"]) >= 3


# ───────── no lying / measurement tokens anywhere in the intake ─────────

def test_no_lying_or_measurement_tokens_in_registry():
    # Scan ONLY the parsed machine-readable content (YAML comments excluded), so honest NEGATIVE
    # disclaimers that legitimately live in comments (e.g. "NOT professionally/legally cleared") never
    # false-positive, while EVERY declared token is enforced against the actual serialized data.
    machine_registry_text = json.dumps(_registry(), sort_keys=True, ensure_ascii=False).lower()
    for tok in LYING_TOKENS:
        assert tok not in machine_registry_text, (
            f"lying token in machine-readable registry: {tok}"
        )
    for tok in MEASURE_TOKENS:
        assert tok not in machine_registry_text, (
            f"measurement token in machine-readable registry: {tok}"
        )


def test_registry_declares_gate_blocked_and_review_not_claimed():
    r = _registry()
    assert r["review_status"]["asset_integration_gate"] == "BLOCKED"
    assert r["review_status"]["professional_anatomical_review"] == "NOT_PERFORMED_NOT_CLAIMED"
    assert r["review_status"]["professional_legal_clearance"] == "NOT_PERFORMED_NOT_CLAIMED"
    for d in _plates().values():
        assert d["status"] == "technical-intake-accepted-human-review-pending"


# ───────── §5bis carve-out is bounded (co-written enforcement) ─────────

def test_5bis_names_plate_scope_and_bounds():
    src = STYLE_RULES.read_text(encoding="utf-8")
    assert "## 5bis." in src
    bis = src.split("## 5bis.", 1)[1].split("\n## 6.", 1)[0]
    assert "auren-plate-*" in bis                            # bounded to plate surfaces
    assert "N2" in bis
    assert "N3" in bis
    assert "reste inchangé" in bis                           # master global unchanged
    # measured activation / EMG stay forbidden even in the carve-out
    assert "EMG" in bis
    assert "jamais" in bis or "interdit" in bis.lower()


def test_section5_stays_flat_prohibition_for_bodymap():
    src = STYLE_RULES.read_text(encoding="utf-8")
    s5 = src.split("## 5. Anatomie", 1)[1].split("## 5bis.", 1)[0]
    assert "non médical" in s5
    assert "fibres" in s5           # §5 still forbids fibers for the master silhouette
