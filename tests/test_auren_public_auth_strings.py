"""Sb_UI_10.3 — Public Auth / Welcome Auren Pass (SPIGNOS → Auren).

The visible product name on the STANDALONE public pages (welcome/login/
register — they do not extend base.html) migrates from « SPIGNOS » to
« Auren » : <title>, apple-mobile-web-app-title, welcome <h1>, welcome
journey SVG title. Login/register titles drop the legacy « · Workout »
suffix for « · Auren » (base.html pattern). SPIGNOS stays the INTERNAL
name — no route, form, asset, manifest, CSS or auth-logic change here.

Template-only / strings-only. Icons & manifest stay blocked for
Sb_UI_10.2 (assets gate).
"""
from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
WELCOME = ROOT / "app" / "templates" / "welcome.html"
LOGIN = ROOT / "app" / "templates" / "login.html"
REGISTER = ROOT / "app" / "templates" / "register.html"
AUTH_TEMPLATES = (WELCOME, LOGIN, REGISTER)
MANIFEST = ROOT / "app" / "static" / "manifest.webmanifest"
STATIC_ICONS = ROOT / "app" / "static" / "icons"


@pytest.fixture
def anon_client(monkeypatch):
    """Fresh app + UNAUTHENTICATED TestClient (public pages 303-redirect
    when logged in, so we need an anonymous session to render them)."""
    tmp = tempfile.mkdtemp(prefix="workout-test-anon-")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{Path(tmp) / 'anon.db'}")
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("APP_SECRET_KEY", "test-secret-key-for-signing")
    for m in [x for x in list(sys.modules) if x == "app" or x.startswith("app.")]:
        sys.modules.pop(m, None)
    from app import main as main_mod

    with TestClient(main_mod.app) as c:
        yield c


def _get(client, path):
    r = client.get(path, follow_redirects=False)
    assert r.status_code == 200, f"{path} -> {r.status_code}: {r.text[:200]}"
    return r.text


# ───────── rendered pages: Auren visible, SPIGNOS gone ─────────


def test_welcome_renders_auren_no_spignos(anon_client):
    html = _get(anon_client, "/welcome")
    assert "SPIGNOS" not in html
    assert "<title>Auren</title>" in html
    assert ">Auren</h1>" in html


def test_login_renders_auren_no_spignos(anon_client):
    html = _get(anon_client, "/login")
    assert "SPIGNOS" not in html
    assert "<title>Connexion · Auren</title>" in html


def test_register_renders_auren_no_spignos(anon_client):
    html = _get(anon_client, "/register")
    assert "SPIGNOS" not in html
    assert "<title>Inscription · Auren</title>" in html


def test_welcome_journey_svg_title_is_auren(anon_client):
    html = _get(anon_client, "/welcome")
    assert "Parcours Auren — de la série à la synthèse" in html


# ───────── source-level: apple-title Auren on the 3 heads ─────────


def test_apple_title_is_auren_in_all_auth_templates():
    for f in AUTH_TEMPLATES:
        src = f.read_text(encoding="utf-8")
        assert re.search(
            r'<meta name="apple-mobile-web-app-title" content="Auren"\s*/?>', src
        ), f"apple-title not Auren in {f.name}"


def test_spignos_only_in_technical_comments():
    """SPIGNOS may only survive inside Jinja comments ({# … #}, stripped at
    render) documenting the internal name — never in rendered markup."""
    for f in AUTH_TEMPLATES:
        src = f.read_text(encoding="utf-8")
        rendered_side = re.sub(r"\{#.*?#\}", "", src, flags=re.DOTALL)
        assert "SPIGNOS" not in rendered_side, f"visible SPIGNOS in {f.name}"


def test_no_orion_string_introduced():
    for f in AUTH_TEMPLATES:
        src = f.read_text(encoding="utf-8")
        assert "Orion" not in src
        assert "ORION" not in src


# ───────── sentinels: forms / routes / links unchanged ─────────


def test_login_form_intact(anon_client):
    html = _get(anon_client, "/login")
    assert '<form method="post"' in html
    assert 'name="username"' in html
    assert 'name="password"' in html
    assert 'type="submit"' in html


def test_register_form_intact(anon_client):
    html = _get(anon_client, "/register")
    assert '<form method="post"' in html
    assert 'name="username"' in html
    assert 'name="email"' in html
    assert 'name="password"' in html
    assert 'name="password_confirm"' in html


def test_form_actions_point_at_same_routes():
    """url_for targets unchanged — no route renamed by the rebrand."""
    assert "url_for('login_submit')" in LOGIN.read_text(encoding="utf-8")
    assert "url_for('register_submit')" in REGISTER.read_text(encoding="utf-8")
    wsrc = WELCOME.read_text(encoding="utf-8")
    assert "url_for('login_page')" in wsrc
    assert "url_for('register_page')" in wsrc


def test_functional_labels_preserved(anon_client):
    assert "Connexion" in _get(anon_client, "/login")
    assert "Se connecter" in _get(anon_client, "/login")
    assert "Inscription" in _get(anon_client, "/register")
    assert "Créer le compte" in _get(anon_client, "/register")
    w = _get(anon_client, "/welcome")
    assert "Connexion" in w
    assert "Créer un compte" in w


def test_error_and_reset_blocks_preserved():
    """Error / password-reset conditionals stay byte-present in sources."""
    lsrc = LOGIN.read_text(encoding="utf-8")
    assert "{% if error %}" in lsrc
    assert 'success == "password_reset"' in lsrc
    assert "{% if error %}" in REGISTER.read_text(encoding="utf-8")


# ───────── non-goals: manifest / icons / assets untouched ─────────


def test_manifest_migrated_to_auren_by_10_2():
    """Sb_UI_10.2 (assets sprint) migrated the manifest product name to Auren.
    Full manifest coverage lives in tests/test_auren_pwa_assets.py."""
    src = MANIFEST.read_text(encoding="utf-8")
    assert '"name": "Auren"' in src
    assert "Workout Session Tracking" not in src


def test_auth_favicon_reference_preserved():
    """Sb_UI_10.3 shipped no new asset; Sb_UI_10.2 later added the approved
    Auren PNG icon pack + apple-touch-icon. This test now only guards that the
    auth heads keep referencing the favicon.svg (icon pack coverage lives in
    tests/test_auren_pwa_assets.py)."""
    for f in AUTH_TEMPLATES:
        src = f.read_text(encoding="utf-8")
        assert "icons/favicon.svg" in src  # same single favicon reference
        assert "apple-touch-icon" in src  # added by Sb_UI_10.2
        assert "<script" not in src  # still SSR / no-JS
