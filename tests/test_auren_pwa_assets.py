"""Sb_UI_10.2 — PWA Manifest + App Icons Auren.

The approved Auren glyph (the existing dumbbell pictogram, recolored
#f25f3a → #C8A24B on a graphite #0f1115 canvas) is shipped as a PNG icon
pack, the manifest migrates its product name to Auren, and the standalone
auth heads gain an apple-touch-icon. String/asset/head only — no route,
service, model, migration, data, CSS, JS or service-worker change.

PNG dimensions are read from the IHDR chunk with the stdlib (no Pillow
dependency, so this runs in CI unchanged).
"""
from __future__ import annotations

import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ICONS = ROOT / "app" / "static" / "icons"
MANIFEST = ROOT / "app" / "static" / "manifest.webmanifest"
BASE = ROOT / "app" / "templates" / "base.html"
LOGIN = ROOT / "app" / "templates" / "login.html"
REGISTER = ROOT / "app" / "templates" / "register.html"
WELCOME = ROOT / "app" / "templates" / "welcome.html"


def _png_size(path: Path) -> tuple[int, int]:
    """Read (width, height) from a PNG IHDR chunk — stdlib only."""
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", f"{path.name} is not a PNG"
    # IHDR is the first chunk; width/height are big-endian uint32 at offset 16.
    width, height = struct.unpack(">II", data[16:24])
    return width, height


# ───────── manifest ─────────


def _manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_manifest_valid_json_and_auren():
    m = _manifest()
    assert m["name"] == "Auren"
    assert m["short_name"] == "Auren"


def test_manifest_no_spignos_no_orion():
    raw = MANIFEST.read_text(encoding="utf-8")
    assert "SPIGNOS" not in raw and "Workout" not in raw
    assert "Orion" not in raw and "orion" not in raw


def test_manifest_core_fields_unchanged():
    m = _manifest()
    assert m["id"] == "/"
    assert m["start_url"] == "/"
    assert m["scope"] == "/"
    assert m["display"] == "standalone"
    assert m["background_color"] == "#0f1115"
    assert m["theme_color"] == "#0f1115"
    assert m["lang"] == "fr"
    assert m["dir"] == "ltr"
    assert m["orientation"] == "portrait"


def test_manifest_icon_entries_exact():
    m = _manifest()
    icons = m["icons"]
    assert len(icons) == 3
    expected = {
        ("/static/icons/icon-192.png", "192x192", "image/png", "any"),
        ("/static/icons/icon-512.png", "512x512", "image/png", "any"),
        ("/static/icons/icon-maskable-512.png", "512x512", "image/png", "maskable"),
    }
    got = {(i["src"], i["sizes"], i["type"], i["purpose"]) for i in icons}
    assert got == expected


def test_manifest_no_extra_fields():
    m = _manifest()
    # no marketing description, screenshots, shortcuts, categories added
    for forbidden in ("description", "screenshots", "shortcuts", "categories"):
        assert forbidden not in m


# ───────── files exist + exact dimensions ─────────


def test_icon_files_exist():
    for name in (
        "auren-mark.svg", "favicon.svg",
        "icon-192.png", "icon-512.png", "icon-maskable-512.png",
        "apple-touch-icon.png",
    ):
        assert (ICONS / name).exists(), f"missing icon {name}"


def test_png_dimensions_exact():
    assert _png_size(ICONS / "icon-192.png") == (192, 192)
    assert _png_size(ICONS / "icon-512.png") == (512, 512)
    assert _png_size(ICONS / "icon-maskable-512.png") == (512, 512)
    assert _png_size(ICONS / "apple-touch-icon.png") == (180, 180)


def test_pngs_are_pngs():
    for name in ("icon-192.png", "icon-512.png", "icon-maskable-512.png", "apple-touch-icon.png"):
        data = (ICONS / name).read_bytes()
        assert data[:8] == b"\x89PNG\r\n\x1a\n"


# ───────── favicon SVG: palette + canonical path ─────────

CANONICAL_PATH = (
    "M14 26h4v12h-4zM18 30h6v4h-6zM24 22h4v20h-4zM28 30h8v4h-8z"
    "M36 22h4v20h-4zM40 30h6v4h-6zM46 26h4v12h-4z"
)


def test_favicon_palette_and_path():
    svg = (ICONS / "favicon.svg").read_text(encoding="utf-8")
    assert "#0f1115" in svg
    assert "#C8A24B" in svg
    assert "#f25f3a" not in svg  # legacy orange gone
    assert CANONICAL_PATH in svg  # glyph geometry unchanged
    assert 'viewBox="0 0 64 64"' in svg
    assert 'rx="14"' in svg  # rounded container preserved


def test_auren_mark_source():
    svg = (ICONS / "auren-mark.svg").read_text(encoding="utf-8")
    assert "#0f1115" in svg and "#C8A24B" in svg
    assert "#f25f3a" not in svg
    assert CANONICAL_PATH in svg
    assert 'viewBox="0 0 64 64"' in svg


def test_no_legacy_orange_or_orion_in_svgs():
    for name in ("favicon.svg", "auren-mark.svg"):
        svg = (ICONS / name).read_text(encoding="utf-8")
        assert "f25f3a" not in svg.lower()
        assert "orion" not in svg.lower()


# ───────── heads (source) ─────────


def test_heads_have_apple_touch_and_manifest():
    for f in (BASE, LOGIN, REGISTER, WELCOME):
        src = f.read_text(encoding="utf-8")
        assert "apple-touch-icon" in src, f"no apple-touch-icon in {f.name}"
        assert "apple-touch-icon.png" in src
        assert "manifest.webmanifest" in src
        assert "icons/favicon.svg" in src
        assert 'content="#0f1115"' in src  # theme-color unchanged


def test_no_service_worker_added():
    for f in (BASE, LOGIN, REGISTER, WELCOME):
        src = f.read_text(encoding="utf-8").lower()
        assert "serviceworker" not in src
        assert "service-worker" not in src


# ───────── rendered manifest served OK ─────────


def test_manifest_served(client):
    r = client.get("/static/manifest.webmanifest")
    assert r.status_code == 200
    body = json.loads(r.text)
    assert body["name"] == "Auren"


def test_manifest_declared_icons_are_served(client):
    for name in ("icon-192.png", "icon-512.png", "icon-maskable-512.png", "apple-touch-icon.png"):
        r = client.get(f"/static/icons/{name}")
        assert r.status_code == 200, f"/static/icons/{name} -> {r.status_code}"
        assert r.headers.get("content-type", "").startswith("image/")
