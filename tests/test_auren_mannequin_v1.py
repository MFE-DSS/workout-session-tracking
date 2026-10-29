"""DA-05.0 — the canonical exercise mannequin V1: a governed reference, never a silent final source.

The five approved views are an AI-generated (Midjourney) VISUAL REFERENCE. AUREN_VISUAL_BACKBONE §8.2 is closed:
« jamais d'IA comme source finale (IA = moodboard) » and « un mannequin vectoriel commun articulé ». So:

* the registry names exactly five views, by sha256, with their orientation and measured framing;
* the reference is never a runtime asset (blocked), its AI provenance is declared, legal review stays required;
* the production asset is a vector reconstruction carrying the eleven BodyMap zone codes — no new code;
* no raster ever enters design/auren/ (the existing permanent guard), the rasters live in operator storage.
Stdlib only.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "design/auren/source/mannequin/auren_mannequin_v1_source.yaml"
SPEC = ROOT / "docs/strategy/AUREN_CANONICAL_MANNEQUIN_V1_SPEC.md"
MAPPING = ROOT / "design/auren/source/bodymap/auren_bodymap_mapping.yaml"
VIEWS = ["front", "profile", "three-quarter-front", "three-quarter-back", "back"]


def _registry():
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def test_exactly_the_five_approved_views_by_hash():
    views = _registry()["views"]
    assert [v["view"] for v in views] == VIEWS
    hashes = [v["sha256"] for v in views]
    assert all(re.fullmatch(r"[0-9a-f]{64}", h) for h in hashes)
    assert len(set(hashes)) == 5


def test_canonical_file_names_follow_the_convention():
    for v in _registry()["views"]:
        assert v["file"] == f"auren_mannequin_v1_{v['view'].replace('-', '_')}.png", v["file"]


def test_the_selected_back_view_is_named():
    back = next(v for v in _registry()["views"] if v["view"] == "back")
    assert back["operator_file"] == "mannequin_back_v1.png"
    assert "mannequin-dos-2.png" in _registry()["back_selection_note"]


def test_one_framing_for_five_views():
    r = _registry()
    assert r["canvas"] == [1024, 1024]
    heights = [v["body_height_px"] for v in r["views"]]
    assert max(heights) - min(heights) <= 5, heights  # ± 0,5 % of a 1024 canvas
    feet = [v["body_bbox"][3] for v in r["views"]]
    assert max(feet) - min(feet) <= 2, "one ground line for the five views"


def test_a_reference_never_crosses_into_the_runtime():
    r = _registry()
    assert r["status"] == "canonical-visual-reference-accepted"
    assert r["production_asset_status"] == "vector-reconstruction-required"
    assert r["runtime_authorization"] == "blocked"
    assert r["legal_review"] == "required"
    assert r["professional_anatomical_review"] == "not-claimed"
    for f in ("status", "runtime_authorization", "legal_review", "production_asset_status"):
        assert r[f] not in {"approved", "legally-cleared", "runtime-integrated"}, f


def test_the_ai_provenance_is_declared_as_reference_only():
    ai = _registry()["ai_usage"]
    assert "midjourney" in ai.lower()
    assert "reference only" in ai
    assert "jamais d'IA comme source finale" in SPEC.read_text(encoding="utf-8")


def test_the_reconstruction_carries_the_eleven_bodymap_zone_codes_and_no_other():
    codes = {z["code"] for z in json.loads(MAPPING.read_text(encoding="utf-8"))["zones"]}
    named = set(re.findall(r"`zone-([a-z_]+)`", SPEC.read_text(encoding="utf-8")))
    assert named == codes


def test_no_mannequin_raster_lives_in_the_repository():
    for path in ROOT.rglob("*"):
        if {"node_modules", ".git", ".venv"} & set(path.parts):
            continue
        if path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
            assert "mannequin" not in path.name.lower(), path
