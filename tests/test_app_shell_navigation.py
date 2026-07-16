"""Sb_UI_03.1 — Mobile Bottom Navigation (first build of Sx_UI_03 app shell).

A persistent, app-like mobile bottom navigation with EXACTLY four top-level
destinations (Séance / Programmes / Progression / Profil), SSR / no-JS, native
``<a>`` links, decorative inline SVG icons. Active tab derived from
``request.url.path`` (never ``aria-current="false"``). Secondary routes
(Historique / Physique / Coach / Classement / Squads / Déconnexion) are NOT
removed — they stay reachable in the existing topbar ``<details>`` menu. Desktop
rail is deferred to Sb_UI_03.2 (bottom nav hidden ≥769px, topbar = fallback).

Template + CSS only — no route/service/model/migration/manifest/asset/JS change.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE_TPL = ROOT / "app" / "templates" / "base.html"
APP_CSS = ROOT / "app" / "static" / "css" / "app.css"
FOCUS_CSS = ROOT / "app" / "static" / "css" / "session_focus.css"


def _get(client, path="/"):
    r = client.get(path, follow_redirects=False)
    assert r.status_code == 200, f"{path} -> {r.status_code}: {r.text[:200]}"
    return r.text


def _bottom_nav_html(html: str) -> str:
    """Isolate the <nav class="app-bottom-nav"> ... </nav> block."""
    m = re.search(
        r'<nav class="app-bottom-nav".*?</nav>', html, re.DOTALL
    )
    assert m, "app-bottom-nav not found in rendered HTML"
    return m.group(0)


# ───────── structure ─────────


def test_bottom_nav_present(client):
    html = _get(client)
    assert 'class="app-bottom-nav"' in html


def test_bottom_nav_has_accessible_label(client):
    html = _get(client)
    assert 'aria-label="Navigation principale"' in _bottom_nav_html(html)


def test_bottom_nav_has_exactly_four_items(client):
    nav = _bottom_nav_html(_get(client))
    assert nav.count("app-bottom-nav__item") == 4


def test_bottom_nav_labels_exact(client):
    nav = _bottom_nav_html(_get(client))
    for label in ("Séance", "Programmes", "Progression", "Profil"):
        assert f">{label}</span>" in nav, f"missing bottom-nav label: {label}"


def test_bottom_nav_links_exact(client):
    """The four destinations point at home / library / progress / profile."""
    nav = _bottom_nav_html(_get(client))
    hrefs = re.findall(r'href="([^"]+)"', nav)
    assert len(hrefs) == 4
    # url_for renders absolute URLs (http://testserver/...); match by path.
    paths = [re.sub(r"^https?://[^/]+", "", h) or "/" for h in hrefs]
    assert "/" in paths, paths
    assert any(p.rstrip("/") == "/library" for p in paths), paths
    assert any(p.rstrip("/") == "/progress" for p in paths), paths
    assert any(p.rstrip("/") == "/profile" for p in paths), paths


def test_bottom_nav_icons_are_decorative(client):
    nav = _bottom_nav_html(_get(client))
    assert nav.count("app-bottom-nav__icon") == 4
    # every icon is aria-hidden + focusable=false (never navigate by icon alone)
    assert nav.count('aria-hidden="true"') >= 4
    assert nav.count('focusable="false"') == 4


def test_bottom_nav_has_no_form_or_button(client):
    """Navigation only — no logout form / action button / CTA in the bar."""
    nav = _bottom_nav_html(_get(client))
    assert "<form" not in nav
    assert "<button" not in nav
    assert "Reprendre" not in nav
    assert "Démarrer" not in nav
    assert "Déconnexion" not in nav


# ───────── active state ─────────


def _active_bottom_labels(html: str) -> list[str]:
    """Labels of bottom-nav items carrying aria-current=page."""
    nav = _bottom_nav_html(html)
    out = []
    for item in re.findall(r'<a class="app-bottom-nav__item[^>]*>.*?</a>', nav, re.DOTALL):
        if 'aria-current="page"' in item:
            m = re.search(r"__label\">([^<]+)<", item)
            if m:
                out.append(m.group(1))
    return out


def test_home_marks_seance_active(client):
    assert _active_bottom_labels(_get(client, "/")) == ["Séance"]


def test_library_marks_programmes_active(client):
    assert _active_bottom_labels(_get(client, "/library")) == ["Programmes"]


def test_launcher_marks_programmes_active(client):
    assert _active_bottom_labels(_get(client, "/launcher")) == ["Programmes"]


def test_progress_marks_progression_active(client):
    assert _active_bottom_labels(_get(client, "/progress")) == ["Progression"]


def test_history_marks_progression_active(client):
    assert _active_bottom_labels(_get(client, "/history")) == ["Progression"]


def test_physique_marks_progression_active(client):
    assert _active_bottom_labels(_get(client, "/physique")) == ["Progression"]


def test_coach_marks_progression_active(client):
    assert _active_bottom_labels(_get(client, "/coach-report")) == ["Progression"]


def test_profile_marks_profil_active(client):
    assert _active_bottom_labels(_get(client, "/profile")) == ["Profil"]


def test_squads_marks_profil_active(client):
    assert _active_bottom_labels(_get(client, "/squads")) == ["Profil"]


def test_leaderboard_marks_profil_active(client):
    assert _active_bottom_labels(_get(client, "/leaderboard")) == ["Profil"]


def test_bottom_nav_exactly_one_active_per_route(client):
    for path in ("/", "/library", "/launcher", "/progress", "/history",
                 "/physique", "/coach-report", "/profile", "/squads",
                 "/leaderboard"):
        nav = _bottom_nav_html(_get(client, path))
        assert nav.count('aria-current="page"') == 1, f"{path}: expected 1 active tab"


def test_bottom_nav_never_aria_current_false(client):
    for path in ("/", "/library", "/progress", "/profile"):
        nav = _bottom_nav_html(_get(client, path))
        assert 'aria-current="false"' not in nav


# ───────── secondary routes preserved ─────────


def test_secondary_routes_still_reachable(client):
    """All demoted-from-bottom-nav destinations remain in the topbar menu."""
    html = _get(client)
    for label in ("Historique", "Physique", "Coach", "Classement", "Squads"):
        assert label in html, f"secondary destination missing from shell: {label}"


def test_logout_still_post(client):
    html = _get(client)
    assert 'method="post"' in html


def test_secondary_menu_is_no_js(client):
    """Topbar secondary menu is a native <details>, no JS toggle."""
    src = BASE_TPL.read_text(encoding="utf-8")
    assert "topbar__menu" in src
    assert "<details" in src


# ───────── CSS contract ─────────


def test_css_tap_target_min_size():
    css = APP_CSS.read_text(encoding="utf-8")
    block = css[css.index(".app-bottom-nav"):]
    assert "min-height: 56px" in block
    assert "min-width: 44px" in block


def test_css_safe_area_inset():
    css = APP_CSS.read_text(encoding="utf-8")
    block = css[css.index(".app-bottom-nav"):]
    assert "env(safe-area-inset-bottom" in block


def test_css_hidden_on_desktop():
    css = APP_CSS.read_text(encoding="utf-8")
    # the ≥769px media query hides the bottom nav
    assert re.search(
        r"@media \(min-width: 769px\)\s*\{[^}]*\.app-bottom-nav\s*\{\s*display:\s*none",
        css, re.DOTALL,
    ) or (".app-bottom-nav { display: none; }" in css)


def test_css_no_new_hex_color():
    """No new hex color introduced by this sprint; accent via existing token."""
    css = APP_CSS.read_text(encoding="utf-8")
    block = css[css.index("Sb_UI_03.1 — Mobile Bottom Navigation"):]
    # no raw hex in the bottom-nav block — colors come from var(--...)
    assert not re.search(r"#[0-9a-fA-F]{3,6}", block), "raw hex in bottom-nav CSS"
    assert "var(--accent)" in block


def test_css_focus_visible_present():
    css = APP_CSS.read_text(encoding="utf-8")
    block = css[css.index(".app-bottom-nav"):]
    assert ":focus-visible" in block


# ───────── Focus Mode offset (session_focus.css) ─────────


def test_focus_sticky_cta_offset_uses_token():
    """Sticky CTA is lifted above the bottom nav via the shared token, and the
    token is 0 on desktop so behaviour is unchanged there."""
    focus = FOCUS_CSS.read_text(encoding="utf-8")
    assert "var(--app-bottom-nav-h" in focus
    app = APP_CSS.read_text(encoding="utf-8")
    assert "--app-bottom-nav-h: 56px" in app
    assert "--app-bottom-nav-h: 0px" in app  # neutralised on desktop


# ───────── non-regression ─────────


def test_topbar_brand_auren_preserved(client):
    html = _get(client)
    assert re.search(r'<a class="topbar__brand"[^>]*>Auren</a>', html)


def test_active_banner_preserved_in_template():
    src = BASE_TPL.read_text(encoding="utf-8")
    assert "active-banner" in src
    assert "Reprendre →" in src


def test_pwa_heads_intact(client):
    html = _get(client)
    assert 'rel="manifest"' in html
    assert 'rel="apple-touch-icon"' in html
    assert 'name="theme-color"' in html


def test_no_js_added_to_shell():
    src = BASE_TPL.read_text(encoding="utf-8")
    assert "addEventListener" not in src
    assert "<script" not in src.lower()


def test_bottom_nav_derived_from_request_path():
    src = BASE_TPL.read_text(encoding="utf-8")
    assert "request.url.path" in src
    assert "app-bottom-nav" in src
