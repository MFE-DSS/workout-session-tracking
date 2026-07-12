"""Sx_UI_08.1 — PWA Installability Baseline.

Manifest + mobile-installability metadata only. No service worker, no offline
cache, no SPA, no JS, no business-surface change. SSR/Jinja + no-JS fallback
preserved.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "app" / "static" / "manifest.webmanifest"
BASE_HTML = ROOT / "app" / "templates" / "base.html"
STATIC_DIR = ROOT / "app" / "static"


# ───────── 1. manifest is valid + complete ─────────


def _manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_manifest_is_valid_json():
    m = _manifest()
    assert isinstance(m, dict)


def test_manifest_has_required_installability_keys():
    m = _manifest()
    for key in (
        "name", "short_name", "start_url", "scope",
        "display", "theme_color", "background_color",
    ):
        assert key in m, f"manifest missing required key {key!r}"
        assert m[key] not in (None, ""), f"manifest key {key!r} is empty"


def test_manifest_display_is_installable_mode():
    m = _manifest()
    assert m["display"] in ("standalone", "minimal-ui", "fullscreen")


def test_manifest_start_url_and_scope_are_root():
    m = _manifest()
    assert m["start_url"] == "/"
    assert m["scope"] == "/"


def test_manifest_theme_and_background_are_dark_graphite():
    """Auren Terminal : theme/background stay in the existing graphite tone,
    no new palette introduced."""
    m = _manifest()
    # existing validated tone; the sprint must NOT introduce a new colour
    assert m["theme_color"] == "#0f1115"
    assert m["background_color"] == "#0f1115"


def test_manifest_icons_reference_existing_asset_only():
    m = _manifest()
    assert m.get("icons"), "manifest must declare at least one icon"
    for icon in m["icons"]:
        src = icon["src"]
        # /static/icons/favicon.svg → app/static/icons/favicon.svg
        rel = src.lstrip("/").replace("static/", "", 1)
        asset = STATIC_DIR / rel
        assert asset.exists(), f"icon asset missing on disk: {src}"


def test_manifest_start_url_route_exists(client):
    """start_url must resolve (root requires auth → 303, never 404)."""
    r = client.get(_manifest()["start_url"], follow_redirects=False)
    assert r.status_code in (200, 303), f"start_url returned {r.status_code}"


# ───────── 2. base HTML installability metadata ─────────


def _base_src() -> str:
    return BASE_HTML.read_text(encoding="utf-8")


def test_base_references_manifest():
    src = _base_src()
    assert 'rel="manifest"' in src
    assert "manifest.webmanifest" in src


def test_base_has_theme_color_and_viewport():
    src = _base_src()
    assert 'name="theme-color"' in src
    assert 'content="#0f1115"' in src
    assert 'name="viewport"' in src
    assert "width=device-width" in src


def test_base_has_mobile_web_app_meta():
    src = _base_src()
    assert 'name="mobile-web-app-capable"' in src
    assert 'name="apple-mobile-web-app-capable"' in src
    assert 'name="apple-mobile-web-app-title"' in src


def test_base_renders_meta_on_a_real_page(client):
    """The installability meta must actually render on a page that extends
    base.html. The `client` fixture is auto-logged-in, so /library (which
    extends base.html) renders the shared <head>.

    NB: the public auth pages (welcome/login/register) carry their OWN
    standalone <head> and are OUT OF SCOPE for this sprint — see report
    §limits."""
    r = client.get("/library", follow_redirects=False)
    assert r.status_code == 200, r.text[:200]
    html = r.text
    assert 'rel="manifest"' in html
    assert 'name="theme-color"' in html
    assert 'name="apple-mobile-web-app-title"' in html


# ───────── 3. non-goals: no service worker / no JS / no offline ─────────


def test_no_service_worker_referenced_in_base():
    src = _base_src().lower()
    assert "serviceworker" not in src
    assert "service-worker" not in src
    assert "navigator.serviceworker" not in src


def test_no_js_or_script_added_to_base_for_pwa():
    src = _base_src()
    # base.html carries no <script> for PWA install (SSR + no-JS baseline)
    assert "register(" not in src  # no SW registration
    assert "workbox" not in src.lower()


def test_no_service_worker_file_present():
    """No service worker asset should exist under static (Option A: no SW)."""
    for name in ("sw.js", "service-worker.js", "serviceworker.js", "workbox-sw.js"):
        assert not (STATIC_DIR / name).exists(), f"unexpected service worker: {name}"
    assert not (STATIC_DIR / "js").is_dir() or not any(
        (STATIC_DIR / "js").glob("*service*worker*")
    )
