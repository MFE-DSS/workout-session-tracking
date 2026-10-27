"""DA-03.3 — AUREN-APP-ICON-V1 guard (LOCKED, operator 2026-10-27: « ACCEPT I2 — SEMANTIC »).

The pixels of the app icon are Apple's (Icon Composer), so they are gated on macOS by
scripts/check_app_icon.py. This guard runs everywhere (CI is Linux)
and checks what does not need Apple's renderer:
  - the .icon document is exactly the approved composition: the AUREN-MARK-V1 primary
    drawing, 24 px per grid unit on 1024 (54 %), centred, lifted 16 px — cursor `signal`
    over marker `system` on `field`, two groups, restrained material, nothing else;
  - the app is configured to use it;
  - the recorded baselines are complete and untouched.
Standard library only.
"""
from __future__ import annotations

import hashlib
import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MOBILE = ROOT / "clients" / "mobile"
DOCUMENT = MOBILE / "assets" / "AurenAppIcon.icon"
ICON_GATE = MOBILE / "visual-contract" / "app-icon"
GATE_SCRIPT = ROOT / "scripts" / "check_app_icon.py"
MARK = ROOT / "design" / "auren" / "source" / "brand" / "mark" / "mark-primary.svg"
THEME = MOBILE / "src" / "ui" / "theme.ts"
CONTRACT = ROOT / "docs" / "strategy" / "AUREN_VISUAL_CONTRACT.md"

SCALE, LIFT, CANVAS = 24, 16, 1024


def _token(name: str) -> str:
    return re.search(rf"\b{name}: '(#[0-9A-Fa-f]{{6}})'", THEME.read_text(encoding="utf-8")).group(1).upper()


def _srgb(hexcolor: str) -> str:
    r, g, b = (int(hexcolor[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return f"srgb:{r:.5f},{g:.5f},{b:.5f},1.00000"


def _expected_layers() -> dict[str, str]:
    """The mark's two pieces, placed exactly as approved: integer px per unit, box centred, lifted."""
    d = re.search(r' d="([^"]+)"', MARK.read_text(encoding="utf-8")).group(1)
    pieces = [p.strip() for p in d.split("M") if p.strip()]
    box_w, box_h, x0, y0 = 12 * SCALE, 23 * SCALE, 10, 4
    dx = (CANVAS - box_w) // 2 - x0 * SCALE
    dy = round(CANVAS / 2 - LIFT - box_h / 2) - y0 * SCALE

    def place(piece: str) -> str:
        pts = re.findall(r"(\d+) (\d+)", piece)
        return "M" + " L".join(f"{int(x) * SCALE + dx} {int(y) * SCALE + dy}" for x, y in pts) + " Z"

    return {"cursor": place(pieces[0]), "marker": place(pieces[1])}


def _layer(name: str) -> tuple[str, str]:
    svg = (DOCUMENT / "Assets" / f"{name}.svg").read_text(encoding="utf-8")
    paths = re.findall(r'<path fill="(#[0-9A-Fa-f]{6})" d="([^"]+)"/>', svg)
    assert len(paths) == 1, f"{name}: exactly one piece per layer"
    return paths[0][0].upper(), paths[0][1]


def test_the_document_is_the_approved_composition():
    expected = _expected_layers()
    for name, role in (("cursor", "signal"), ("marker", "system")):
        colour, d = _layer(name)
        assert d == expected[name], f"{name}: not AUREN-MARK-V1 at 24 px / unit, centred, +16 px"
        assert colour == _token(role), f"{name}: must be `{role}`"
        svg = (DOCUMENT / "Assets" / f"{name}.svg").read_text(encoding="utf-8")
        assert 'viewBox="0 0 1024 1024"' in svg
        assert not re.search(r"filter|gradient|blur|opacity|stroke|<text|<image", svg), f"{name}: no baked effect"


def test_the_document_is_flat_two_groups_restrained_material():
    doc = json.loads((DOCUMENT / "icon.json").read_text(encoding="utf-8"))
    assert doc["fill"] == {"solid": _srgb(_token("field"))}
    assert [g["layers"][0]["name"] for g in doc["groups"]] == ["cursor", "marker"]  # cursor in front
    for group in doc["groups"]:
        assert len(group["layers"]) == 1
        assert set(group) == {"layers", "shadow", "translucency"}, "no extra material effect"
        assert group["shadow"] == {"kind": "neutral", "opacity": 0.35}
        assert group["translucency"]["enabled"] is False
    assert sorted(p.name for p in (DOCUMENT / "Assets").iterdir()) == ["cursor.svg", "marker.svg"]


def test_the_app_uses_the_icon_document():
    expo = json.loads((MOBILE / "app.json").read_text(encoding="utf-8"))["expo"]
    assert expo["ios"]["icon"] == "./assets/AurenAppIcon.icon"
    assert not expo["icon"].endswith(".icon"), "the root icon stays a PNG (Android, web)"


def test_flat_fallbacks_have_their_platform_sizes():
    sizes = {"icon.png": 1024, "android-icon-foreground.png": 512, "android-icon-background.png": 512,
             "android-icon-monochrome.png": 432, "favicon.png": 48}
    for name, size in sizes.items():
        data = (MOBILE / "assets" / name).read_bytes()
        assert data[:8] == b"\x89PNG\r\n\x1a\n"
        assert struct.unpack(">II", data[16:24]) == (size, size), name


def test_recorded_baselines_are_complete_and_untouched():
    manifest = json.loads((ICON_GATE / "baselines" / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["visual_id"] == "AUREN-APP-ICON-V1"
    assert manifest["approved_by"].startswith("operator")
    render = GATE_SCRIPT.read_text(encoding="utf-8")
    ids = re.findall(r'\("(app-icon-v1-[a-z0-9-]+)"', render)
    assert [b["id"] for b in manifest["baselines"]] == ids
    on_disk = {p.name for p in (ICON_GATE / "baselines").glob("*.png")}
    assert on_disk == {b["file"] for b in manifest["baselines"]}
    for b in manifest["baselines"]:
        assert hashlib.sha256((ICON_GATE / "baselines" / b["file"]).read_bytes()).hexdigest() == b["sha256"], b["id"]
    for rendition in ("Default", "Dark", "Mono", "ClearLight", "ClearDark", "TintedLight", "TintedDark"):
        assert any(b["rendition"] == rendition and b["points"] == 1024 for b in manifest["baselines"]), rendition
    for points in (60, 40, 29):
        assert any(b["points"] == points for b in manifest["baselines"]), points


def test_the_gate_refuses_off_macos_instead_of_passing():
    render = GATE_SCRIPT.read_text(encoding="utf-8")
    assert 'sys.platform != "darwin"' in render
    assert "return 2" in render


def test_the_contract_names_the_icon_and_its_baselines():
    contract = CONTRACT.read_text(encoding="utf-8")
    assert "AUREN-APP-ICON-V1" in contract
    for b in json.loads((ICON_GATE / "baselines" / "manifest.json").read_text(encoding="utf-8"))["baselines"]:
        assert b["id"] in contract, b["id"]
