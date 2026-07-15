"""Sx_UI_08.2 — Public Auth Heads Alignment.

The public auth pages (welcome/login/register) have their OWN standalone
<head> (they do not extend base.html). This aligns them with the PWA
installability baseline (Sx_UI_08.1): manifest + mobile installability meta,
without touching forms, routes, wording, colours or manifest itself. No
service worker, no JS, no rebrand.

These pages redirect (303) to / when logged in, so we use a fresh
UNAUTHENTICATED client to render the public HTML.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
WELCOME = ROOT / "app" / "templates" / "welcome.html"
LOGIN = ROOT / "app" / "templates" / "login.html"
REGISTER = ROOT / "app" / "templates" / "register.html"
BASE_HTML = ROOT / "app" / "templates" / "base.html"
MANIFEST = ROOT / "app" / "static" / "manifest.webmanifest"


@pytest.fixture
def anon_client(monkeypatch):
    """Fresh app + UNAUTHENTICATED TestClient (no auto-login), so the public
    auth pages render their HTML instead of redirecting."""
    tmp = tempfile.mkdtemp(prefix="workout-test-anon-")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{Path(tmp) / 'anon.db'}")
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("APP_SECRET_KEY", "test-secret-key-for-signing")
    for m in [x for x in list(sys.modules) if x == "app" or x.startswith("app.")]:
        sys.modules.pop(m, None)
    from app import main as main_mod

    with TestClient(main_mod.app) as c:
        yield c


# ───────── expected installability meta (mirrors base.html / Sx_UI_08.1) ─────────

_REQUIRED_META = (
    'rel="manifest"',
    "manifest.webmanifest",
    'name="theme-color"',
    'content="#0f1115"',
    'name="viewport"',
    "width=device-width",
    'name="mobile-web-app-capable"',
    'name="apple-mobile-web-app-capable"',
    'name="apple-mobile-web-app-title"',
    'content="Auren"',  # Sb_UI_10.3 — visible product name migrated to Auren
)


def _assert_installable_head(html: str):
    for token in _REQUIRED_META:
        assert token in html, f"missing installability meta: {token}"
    # never a service worker on these pages
    low = html.lower()
    assert "serviceworker" not in low
    assert "service-worker" not in low
    assert "<script" not in html  # SSR + no-JS baseline preserved


# ───────── 1. /welcome ─────────


def test_welcome_status_and_installable_head(anon_client):
    r = anon_client.get("/welcome", follow_redirects=False)
    assert r.status_code == 200, r.text[:200]
    _assert_installable_head(r.text)


# ───────── 2. /login (+ form intact) ─────────


def test_login_status_and_installable_head(anon_client):
    r = anon_client.get("/login", follow_redirects=False)
    assert r.status_code == 200, r.text[:200]
    _assert_installable_head(r.text)


def test_login_form_intact(anon_client):
    html = anon_client.get("/login", follow_redirects=False).text
    assert '<form method="post"' in html
    assert 'name="username"' in html
    assert 'name="password"' in html
    assert 'type="submit"' in html


# ───────── 3. /register (+ form intact) ─────────


def test_register_status_and_installable_head(anon_client):
    r = anon_client.get("/register", follow_redirects=False)
    assert r.status_code == 200, r.text[:200]
    _assert_installable_head(r.text)


def test_register_form_intact(anon_client):
    html = anon_client.get("/register", follow_redirects=False).text
    assert '<form method="post"' in html
    assert 'name="username"' in html
    assert 'name="password"' in html


# ───────── 4. non-goals (source-level) ─────────


def test_no_js_or_service_worker_in_auth_templates():
    for f in (WELCOME, LOGIN, REGISTER):
        src = f.read_text(encoding="utf-8")
        assert "<script" not in src, f"unexpected <script> in {f.name}"
        assert "serviceworker" not in src.lower()
        assert "service-worker" not in src.lower()
        assert "apple-touch-icon" not in src  # no PNG asset → not added


def test_auth_templates_reference_shared_manifest():
    """The auth heads must point at the SAME manifest as base.html (no new
    manifest, no manifest change)."""
    for f in (WELCOME, LOGIN, REGISTER):
        src = f.read_text(encoding="utf-8")
        assert "manifest.webmanifest" in src


def test_auth_titles_auren_product_name():
    """Sb_UI_10.3 — visible product name in the auth titles is Auren; the
    functional page labels (Connexion / Inscription) are preserved."""
    assert "<title>Auren</title>" in WELCOME.read_text(encoding="utf-8")
    assert "Connexion" in LOGIN.read_text(encoding="utf-8")
    assert "Inscription" in REGISTER.read_text(encoding="utf-8")


def test_manifest_untouched_still_valid():
    """This sprint must not modify the manifest; it stays valid JSON."""
    import json

    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert m["theme_color"] == "#0f1115"
    assert m["display"] == "standalone"
