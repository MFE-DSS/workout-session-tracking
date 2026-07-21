"""Sb_ASSET_02.1 — Vendored Icon Subset & License Intake guard.

Validates the first third-party design-source intake (Tabler Icons v3.45.0 P0
subset) with the standard library only (no PyYAML, no network). Checks the
machine-readable registry, the ten SVG files, the MIT license, the manifest and
provenance records, the review preview, and NON-integration into app/**.

Design-source intake only. Human/legal review pending. No app integration.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUREN = ROOT / "design" / "auren"
REGISTRY = AUREN / "source" / "icons" / "auren_icon_subset.yaml"
OUTLINE = AUREN / "source" / "icons" / "vendor" / "tabler" / "v3.45.0" / "outline"
LICENSE = AUREN / "LICENSES" / "tabler-MIT.txt"
PREVIEW = AUREN / "previews" / "icons" / "auren-icon-subset-v0.1.0.html"

TABLER_COMMIT = "975920ff99c12c4dc9e3fe61a03738330600f9b2"
TABLER_TAG = "v3.45.0"
TABLER_TAG_OBJECT = "64bfab222b4626fafb2301358dd41d3f3f3d84b2"

# canonical order (spec §7)
CANONICAL = [
    ("arrows-exchange", "auren.icon.action.substitute"),
    ("player-play", "auren.icon.action.timer-start"),
    ("player-pause", "auren.icon.action.timer-pause"),
    ("rotate", "auren.icon.action.timer-reset"),
    ("chevron-down", "auren.icon.action.expand"),
    ("chevron-up", "auren.icon.action.collapse"),
    ("bulb", "auren.icon.information.guidance"),
    ("alert-triangle", "auren.icon.information.warning"),
    ("check", "auren.icon.status.completed"),
    ("menu-2", "auren.icon.action.menu"),
]


def _registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# ───────── registry ─────────


def test_registry_parses_with_stdlib_json():
    d = _registry()
    assert d["schema"] == "auren.functional-icon-subset"
    assert d["schema_version"] == 1
    assert d["subset_id"] == "auren.icons.vendor.tabler.p0"
    assert d["subset_version"] == "0.1.0"
    assert d["status"] == "legal-review-required"


def test_registry_vendor_pins_exact():
    v = _registry()["vendor"]
    assert v["project"] == "tabler/tabler-icons"
    assert v["version"] == "3.45.0"
    assert v["tag"] == TABLER_TAG
    assert v["tag_object"] == TABLER_TAG_OBJECT
    assert v["commit"] == TABLER_COMMIT
    assert v["style"] == "outline"


def test_registry_license_is_mit():
    lic = _registry()["license"]
    assert lic["spdx"] == "MIT"
    assert lic["upstream_path"] == "LICENSE"
    assert lic["local_path"] == "design/auren/LICENSES/tabler-MIT.txt"
    assert lic["review"] == "NOT YET REVIEWED"


def test_registry_exactly_ten_icons_canonical_order():
    icons = _registry()["icons"]
    assert [i["vendor_icon_name"] for i in icons] == [n for n, _ in CANONICAL]
    assert [i["semantic_id"] for i in icons] == [s for _, s in CANONICAL]


def test_registry_ids_and_files_unique():
    icons = _registry()["icons"]
    assert len({i["semantic_id"] for i in icons}) == 10
    assert len({i["asset_id"] for i in icons}) == 10
    assert len({i["source_file"] for i in icons}) == 10


def test_registry_no_approved_no_health_no_custom():
    d = _registry()
    # Check the status FIELDS, not descriptive prose in invariants/tooling.
    assert d["status"] != "approved"
    for i in d["icons"]:
        assert i["selection_status"] == "vendor-selected-for-intake"
        assert i["manifest_status"] == "legal-review-required"
        assert i["review_status"] == "human-review-pending"
        for k in ("selection_status", "manifest_status", "review_status"):
            assert i[k] not in ("approved", "integrated", "legally-cleared")
    # No Health Icons vendor, no custom vendor in the actual data.
    assert d["vendor"]["project"] == "tabler/tabler-icons"
    assert all(i["source_file"].startswith(
        "design/auren/source/icons/vendor/tabler/") for i in d["icons"])


def test_registry_geometry_not_modified():
    n = _registry()["normalization"]
    assert n["geometry_modified"] is False
    assert n["line_endings"] == "LF"
    assert n["final_newline"] is True
    assert n["removed"] == ["upstream XML metadata comment"]
    # no opaque minifier was actually RUN (tooling explicitly says "no SVGO/resvg")
    assert "no svgo/resvg" in n["tooling"].lower()


# ───────── files ─────────


def test_ten_svg_files_present_and_regular():
    svgs = sorted(p.name for p in OUTLINE.glob("*.svg"))
    assert svgs == sorted(f"{n}.svg" for n, _ in CANONICAL)
    for p in OUTLINE.glob("*.svg"):
        assert p.is_file() and not p.is_symlink()


def test_each_svg_respects_auren_contract():
    for name, _ in CANONICAL:
        src = (OUTLINE / f"{name}.svg").read_text(encoding="utf-8")
        assert src.startswith("<svg"), name
        assert 'xmlns="http://www.w3.org/2000/svg"' in src, name
        assert 'viewBox="0 0 24 24"' in src, name
        assert 'fill="none"' in src, name
        assert 'stroke="currentColor"' in src, name
        assert 'stroke-width="2"' in src, name
        assert 'stroke-linecap="round"' in src, name
        assert 'stroke-linejoin="round"' in src, name


def test_each_svg_is_safe_and_clean():
    # forbidden tokens EXCLUDING the standard SVG xmlns namespace URL.
    forbidden = ("<!--", "<script", "<style", "<image", "<foreignobject",
                 "xlink:href", "href=", "url(")
    for name, _ in CANONICAL:
        src = (OUTLINE / f"{name}.svg").read_text(encoding="utf-8")
        low = src.lower()
        for tok in forbidden:
            assert tok not in low, f"{name}: forbidden token {tok!r}"
        # only the w3.org SVG namespace URL is allowed — no other external URL
        assert low.count("http://") + low.count("https://") == low.count("http://www.w3.org/2000/svg"), \
            f"{name}: unexpected external URL"
        # no inline event handlers
        assert not re.search(r'\son[a-z]+\s*=', src), f"{name}: event handler"
        # no hex colours
        assert not re.search(r'#[0-9a-fA-F]{3,6}\b', src), f"{name}: hex colour"


def test_each_svg_within_budget():
    for name, _ in CANONICAL:
        assert (OUTLINE / f"{name}.svg").stat().st_size <= 2048, name


def test_each_svg_sha256_matches_registry():
    reg = {i["vendor_icon_name"]: i for i in _registry()["icons"]}
    for name, _ in CANONICAL:
        p = OUTLINE / f"{name}.svg"
        assert reg[name]["local_sha256"] == _sha256(p), f"{name}: sha256 drift"
        assert reg[name]["local_size_bytes"] == p.stat().st_size, f"{name}: size drift"


# ───────── license ─────────


def test_license_file_present_and_official():
    assert LICENSE.is_file()
    src = LICENSE.read_text(encoding="utf-8")
    assert "MIT License" in src
    assert "Paweł Kuna" in src


def test_license_sha256_matches_registry():
    lic = _registry()["license"]
    assert lic["local_sha256"] == _sha256(LICENSE)
    # registry records upstream == local (proof captured at build)
    assert lic["upstream_sha256"] == lic["local_sha256"]


def test_no_other_license_file():
    files = sorted(p.name for p in (AUREN / "LICENSES").iterdir() if p.is_file())
    assert files == ["README.md", "tabler-MIT.txt"]


# ───────── manifest / provenance ─────────


def test_manifest_has_ten_tabler_entries_none_approved():
    src = (AUREN / "AUREN_VISUAL_ASSET_MANIFEST.md").read_text(encoding="utf-8")
    for name, _ in CANONICAL:
        assert f"auren.icons.vendor.tabler.{name}" in src, name
    # no vendored icon marked approved
    assert not re.findall(r"(?m)^\s*status:\s*approved\b", src)


def test_provenance_has_tabler_intake_no_verified():
    src = (AUREN / "AUREN_ASSET_PROVENANCE.md").read_text(encoding="utf-8")
    assert "tabler/tabler-icons" in src
    assert TABLER_COMMIT in src
    assert "NOT AUREN IP OWNERSHIP" in src
    assert "ip_ownership_status: not-legally-reviewed" in src
    # these ten entries never claim verified/approved
    assert "ip_ownership_status: verified" not in src


# ───────── preview ─────────


def test_preview_uses_css_mask_not_img():
    """Sb_ASSET_02.1-fix: the preview must render icons via CSS mask (colour from
    background-color:currentColor), NOT via <img> (which cannot receive the parent
    colour → black/invisible on graphite, the original rejection cause)."""
    src = PREVIEW.read_text(encoding="utf-8")
    # static: no JS, no network (only the w3.org SVG namespace URL, if any, is allowed)
    assert "<script" not in src.lower()
    assert (src.lower().count("http://") + src.lower().count("https://")
            == src.lower().count("http://www.w3.org/2000/svg"))
    # NO <img> element used to render icons (the rejected technique)
    assert "<img " not in src.lower()
    # CSS mask present, both standard and WebKit prefixes
    assert "-webkit-mask-image" in src
    assert re.search(r"(?<!-)mask-image", src)  # standard (not only the webkit one)
    # exactly ten DISTINCT svg URLs (10 std + 10 webkit declarations, 10 unique URLs)
    urls = set(re.findall(r'mask-image:\s*url\("([^"]+\.svg)"\)', src))
    assert len(urls) == 10, f"expected 10 distinct mask svg URLs, got {len(urls)}: {sorted(urls)}"
    for u in urls:
        assert u.endswith(".svg") and "://" not in u
        assert (PREVIEW.parent / u).resolve().is_file(), f"mask URL not a real file: {u}"
    # colour driven by currentColor (so light/dark contexts colour the icons)
    assert "background-color:currentColor" in src.replace(" ", "")
    # a light context and a graphite/dark context, each setting a colour
    assert re.search(r"\.light\s*\{[^}]*color", src)
    assert re.search(r"\.dark\s*\{[^}]*color", src)
    # three sizes present
    for cls in ("icon-16", "icon-20", "icon-24"):
        assert cls in src, f"missing size class {cls}"
    # NO inline SVG geometry copied into the HTML
    assert "<path" not in src and "<svg" not in src
    # no premature approval marker (lower-case token; prose "aucun APPROVED" is fine)
    assert "approved" not in src.lower()


# ───────── non-integration ─────────


def test_no_app_static_functional_icons():
    functional = ROOT / "app" / "static" / "icons" / "functional"
    assert not functional.exists() or not any(functional.iterdir())


def test_no_app_reference_to_design_subset():
    app = ROOT / "app"
    needle = "design/auren/source/icons"
    offenders = [
        str(p.relative_to(ROOT))
        for p in app.rglob("*")
        if p.is_file() and p.suffix in {".py", ".html", ".css", ".js"}
        and needle in p.read_text(encoding="utf-8", errors="ignore")
    ]
    assert not offenders, f"app references the design subset: {offenders}"
