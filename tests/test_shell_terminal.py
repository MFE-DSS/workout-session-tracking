"""Sb_UI_02b.3 — Auren Terminal global shell hardening tests.

Verifies the global shell (app.css tokens + base.html) migrated to
Auren Terminal (graphite + mono + amber), consistent with Home and
Focus Mode, WITHOUT touching product routes/services.

Asserts (CSS-level):
- app.css :root defines Auren Terminal tokens (graphite bg, amber accent)
- the legacy orange accent (#f25f3a) is removed from tokens + not left as
  a dominant hardcoded value
- --font is remapped to a mono system stack; no webfont
- amber accent used for shell CTA / active

Asserts (shell/render-level):
- base.html loads app.css and no longer loads the Google Fonts webfont
- topbar nav links preserved (Accueil / Programmes / Historique /
  Progression / Profil / Déconnexion)
- Home still terminal (today-home--terminal)
- Focus still terminal (session-focus--terminal)
- no-JS: nav is a <details>/<a>/<form>, no script dependency

Reads rendered HTML + CSS/template source only — no pixels.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP_CSS = ROOT / "app" / "static" / "css" / "app.css"
BASE = ROOT / "app" / "templates" / "base.html"
INDEX = ROOT / "app" / "templates" / "index.html"
SESSION_DETAIL = ROOT / "app" / "templates" / "session_detail.html"
JS_DIR = ROOT / "app" / "static" / "js"


def _home(client) -> str:
    r = client.get("/")
    assert r.status_code == 200, r.text[:300]
    return r.text


# ───────── app.css Auren Terminal tokens ─────────


class TestAppCssTokens:
    def test_graphite_bg_token(self):
        css = APP_CSS.read_text(encoding="utf-8").lower()
        assert "--bg: #0f1318" in css, "app.css --bg must be graphite base"

    def test_amber_accent_token(self):
        css = APP_CSS.read_text(encoding="utf-8").lower()
        assert "--accent: #c8a24b" in css, "app.css --accent must be amber"

    def test_orange_accent_removed(self):
        """The legacy orange accent value must not be a token value nor a
        dominant hardcoded background (a comment mentioning it is fine)."""
        css = APP_CSS.read_text(encoding="utf-8").lower()
        assert "--accent: #f25f3a" not in css
        # no hardcoded orange background left in the body rules
        body = css.split(":root", 1)[-1]
        # allow the string only inside comments; assert not used as a value
        assert "background: #f25f3a" not in body
        assert "color: #f25f3a" not in body

    def test_mono_font_remap(self):
        css = APP_CSS.read_text(encoding="utf-8").lower()
        assert "--font-mono:" in css
        assert re.search(r"--font:\s*var\(--font-mono\)", css), (
            "--font must be remapped to the mono system stack"
        )
        assert "ui-monospace" in css

    def test_no_webfont_in_app_css(self):
        css = APP_CSS.read_text(encoding="utf-8").lower()
        assert "@import" not in css
        assert "@font-face" not in css

    def test_amber_focus_and_cta(self):
        css = APP_CSS.read_text(encoding="utf-8")
        # global amber focus ring
        assert re.search(r":focus-visible[^{]*\{[^}]*var\(--accent\)", css, re.DOTALL) \
            or "outline: 2px solid var(--accent)" in css
        # primary CTA uses amber
        assert re.search(r"\.btn--primary\s*\{[^}]*var\(--accent\)", css, re.DOTALL)


# ───────── base.html shell ─────────


class TestBaseShell:
    def test_base_loads_app_css(self):
        src = BASE.read_text(encoding="utf-8")
        assert "css/app.css" in src

    def test_base_no_google_webfont(self):
        """Auren Terminal uses system mono — the Google Fonts link is gone."""
        src = BASE.read_text(encoding="utf-8")
        assert "fonts.googleapis.com" not in src
        assert "fonts.gstatic.com" not in src


# ───────── nav preserved + coherence (render) ─────────


class TestNavAndCoherence:
    def test_nav_links_preserved(self, client):
        body = _home(client)
        for label in ("Accueil", "Programmes", "Historique", "Progression",
                      "Profil", "Déconnexion"):
            assert label in body, f"nav link {label!r} missing"

    def test_logout_form_preserved(self, client):
        body = _home(client)
        assert re.search(r'<form[^>]*action="[^"]*logout"', body) or "logout" in body

    def test_home_still_terminal(self, client):
        assert "today-home--terminal" in _home(client)

    def test_focus_marker_wired(self):
        src = SESSION_DETAIL.read_text(encoding="utf-8")
        assert "session-focus--terminal" in src

    def test_topbar_present(self, client):
        assert "topbar" in _home(client)


# ───────── no framework leak ─────────


class TestNoLeak:
    def test_no_new_js(self):
        js_files = sorted(p.name for p in JS_DIR.glob("*.js"))
        assert js_files == ["preview.js", "session_focus.js"], (
            f"Sb_UI_02b.3 must add no JS: {js_files}"
        )

    def test_no_react_marker(self, client):
        body = _home(client)
        for marker in ("data-reactroot", "__NEXT_DATA__", "ReactDOM"):
            assert marker not in body
