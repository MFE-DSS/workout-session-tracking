"""Sb_UI_03.2 — Desktop Rail / Secondary Shell (2nd build of Sx_UI_03).

A persistent left-hand desktop rail (visible ≥1024px) that becomes the primary
navigation on large screens, carrying the SAME four destinations as the mobile
bottom nav (Séance / Programmes / Progression / Profil) with the SAME active
mapping (shared Jinja vars, no divergent classification). Secondary routes stay
reachable in a native <details> "Plus"; Contact + logout POST live in the rail
footer. Below 1024px the rail is hidden and the bottom nav (Sb_UI_03.1) is the
navigation. Template + CSS only — no route/service/model/data/JS/POST change.
Session-active hardening is deferred to Sb_UI_03.3.
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


def _rail_html(html: str) -> str:
    m = re.search(r'<aside class="app-rail".*?</aside>', html, re.DOTALL)
    assert m, "app-rail not found in rendered HTML"
    return m.group(0)


def _rail_primary(html: str) -> str:
    m = re.search(r'<nav class="app-rail__primary".*?</nav>', _rail_html(html), re.DOTALL)
    assert m, "app-rail__primary nav not found"
    return m.group(0)


# ───────── structure ─────────


def test_rail_present(client):
    assert 'class="app-rail"' in _get(client)


def test_rail_primary_has_accessible_label(client):
    assert 'aria-label="Navigation principale (desktop)"' in _rail_primary(_get(client))


def test_rail_has_exactly_four_primary_items(client):
    assert _rail_primary(_get(client)).count("app-rail__item") == 4


def test_rail_primary_labels_and_order(client):
    prim = _rail_primary(_get(client))
    labels = re.findall(r'__label">([^<]+)</span>', prim)
    assert labels == ["Séance", "Programmes", "Progression", "Profil"]


def test_rail_primary_links_exact(client):
    prim = _rail_primary(_get(client))
    hrefs = re.findall(r'href="([^"]+)"', prim)
    paths = [re.sub(r"^https?://[^/]+", "", h) or "/" for h in hrefs]
    assert "/" in paths
    assert any(p.rstrip("/") == "/library" for p in paths), paths
    assert any(p.rstrip("/") == "/progress" for p in paths), paths
    assert any(p.rstrip("/") == "/profile" for p in paths), paths


def test_rail_icons_decorative(client):
    prim = _rail_primary(_get(client))
    assert prim.count("app-rail__icon") == 4
    assert prim.count('aria-hidden="true"') == 4
    assert prim.count('focusable="false"') == 4


def test_rail_primary_has_no_form_or_cta(client):
    """Primary nav = links only; no business CTA / logout in the primary nav."""
    prim = _rail_primary(_get(client))
    assert "<form" not in prim
    assert "<button" not in prim
    assert "Démarrer" not in prim
    assert "Reprendre" not in prim


# ───────── active mapping (same families as bottom nav) ─────────


def _active_primary(html: str) -> list[str]:
    prim = _rail_primary(html)
    out = []
    for item in re.findall(r'<a class="app-rail__item[^>]*>.*?</a>', prim, re.DOTALL):
        if 'aria-current="page"' in item:
            m = re.search(r'__label">([^<]+)<', item)
            if m:
                out.append(m.group(1))
    return out


def test_rail_home_active_seance(client):
    assert _active_primary(_get(client, "/")) == ["Séance"]


def test_rail_library_active_programmes(client):
    assert _active_primary(_get(client, "/library")) == ["Programmes"]


def test_rail_launcher_active_programmes(client):
    assert _active_primary(_get(client, "/launcher")) == ["Programmes"]


def test_rail_progress_active_progression(client):
    assert _active_primary(_get(client, "/progress")) == ["Progression"]


def test_rail_history_active_progression(client):
    assert _active_primary(_get(client, "/history")) == ["Progression"]


def test_rail_physique_active_progression(client):
    assert _active_primary(_get(client, "/physique")) == ["Progression"]


def test_rail_coach_active_progression(client):
    assert _active_primary(_get(client, "/coach-report")) == ["Progression"]


def test_rail_profile_active_profil(client):
    assert _active_primary(_get(client, "/profile")) == ["Profil"]


def test_rail_squads_active_profil(client):
    assert _active_primary(_get(client, "/squads")) == ["Profil"]


def test_rail_leaderboard_active_profil(client):
    assert _active_primary(_get(client, "/leaderboard")) == ["Profil"]


def test_rail_exactly_one_primary_active_per_route(client):
    for path in ("/", "/library", "/launcher", "/progress", "/history",
                 "/physique", "/coach-report", "/profile", "/squads",
                 "/leaderboard"):
        prim = _rail_primary(_get(client, path))
        assert prim.count('aria-current="page"') == 1, f"{path}: expected 1 active in rail"


def test_rail_never_aria_current_false(client):
    for path in ("/", "/library", "/progress", "/profile"):
        assert 'aria-current="false"' not in _rail_html(_get(client, path))


def test_rail_and_bottom_nav_same_mapping(client):
    """Both regions mark the same primary destination for a given route."""
    for path, label in [("/history", "Progression"), ("/squads", "Profil"),
                        ("/launcher", "Programmes"), ("/", "Séance")]:
        html = _get(client, path)
        assert _active_primary(html) == [label], f"rail {path}"
        # bottom nav item carrying aria-current maps to same label
        nav = re.search(r'<nav class="app-bottom-nav".*?</nav>', html, re.DOTALL).group(0)
        active = [re.search(r'__label">([^<]+)<', it).group(1)
                  for it in re.findall(r'<a class="app-bottom-nav__item[^>]*>.*?</a>', nav, re.DOTALL)
                  if 'aria-current="page"' in it]
        assert active == [label], f"bottom nav {path}"


# ───────── secondary ─────────


def test_rail_secondary_routes_present(client):
    rail = _rail_html(_get(client))
    for label in ("Historique", "Physique", "Coach", "Squads", "Classement", "Contact"):
        assert f">{label}</a>" in rail, f"secondary link missing in rail: {label}"


def test_rail_secondary_is_details_no_js(client):
    rail = _rail_html(_get(client))
    assert "<details class=\"app-rail__secondary\"" in rail
    assert "<summary" in rail


def test_rail_logout_is_post(client):
    rail = _rail_html(_get(client))
    assert 'method="post"' in rail
    assert re.search(r'<button[^>]*app-rail__logout', rail)


def test_rail_no_second_aria_current(client):
    """A secondary-active route must not create a 2nd aria-current in the rail;
    the primary keeps aria-current, sublinks use is-subactive only."""
    rail = _rail_html(_get(client, "/history"))
    assert rail.count('aria-current="page"') == 1
    assert "is-subactive" in rail


# ───────── CSS contract ─────────


def _css():
    return APP_CSS.read_text(encoding="utf-8")


def test_css_rail_hidden_below_1024():
    css = _css()
    assert ".app-rail { display: none; }" in css


def test_css_rail_visible_at_1024():
    css = _css()
    assert re.search(
        r"@media \(min-width: 1024px\)\s*\{[^@]*\.app-rail\s*\{[^}]*display:\s*flex",
        css, re.DOTALL,
    )


def test_css_bottom_nav_hidden_at_1024_not_769():
    css = _css()
    assert re.search(
        r"@media \(min-width: 1024px\)\s*\{[^@]*\.app-bottom-nav\s*\{\s*display:\s*none",
        css, re.DOTALL,
    )
    # the old 769px breakpoint must no longer hide the bottom nav
    assert not re.search(
        r"@media \(min-width: 769px\)\s*\{[^@]*\.app-bottom-nav\s*\{\s*display:\s*none",
        css, re.DOTALL,
    )


def test_css_rail_width_token():
    css = _css()
    assert "--app-rail-w:" in css
    assert "width: var(--app-rail-w)" in css


def test_css_content_shifted_and_capped():
    css = _css()
    assert "margin-left: var(--app-rail-w)" in css
    assert "--app-shell-content-max:" in css


def test_css_topbar_hidden_on_desktop():
    css = _css()
    assert re.search(
        r"@media \(min-width: 1024px\)\s*\{[^@]*\.topbar\s*\{\s*display:\s*none",
        css, re.DOTALL,
    )


def test_css_focus_mode_tightened_desktop():
    focus = FOCUS_CSS.read_text(encoding="utf-8")
    assert re.search(
        r"@media \(min-width: 1024px\)\s*\{[^@]*\.session-focus\s*\{[^}]*max-width:\s*720px",
        focus, re.DOTALL,
    )


def test_css_rail_no_new_hex_color():
    css = _css()
    block = css[css.index("Sb_UI_03.2 — Desktop Rail"):]
    assert not re.search(r"#[0-9a-fA-F]{3,6}", block), "raw hex in rail CSS"
    assert "var(--accent)" in block


def test_css_rail_active_not_color_only():
    """Active state carries a border-left accent + weight, not color alone."""
    css = _css()
    m = re.search(r"\.app-rail__item\.is-active\s*\{([^}]*)\}", css)
    assert m
    body = m.group(1)
    assert "border-left-color" in body
    assert "font-weight" in body


def test_css_rail_focus_visible():
    css = _css()
    block = css[css.index("Sb_UI_03.2 — Desktop Rail"):]
    assert ":focus-visible" in block


def test_css_rail_tap_target():
    css = _css()
    m = re.search(r"\.app-rail__item\s*\{([^}]*)\}", css)
    assert m and "min-height: 44px" in m.group(1)


# ───────── non-regression ─────────


def test_bottom_nav_still_present(client):
    """Sb_UI_03.1 bottom nav is untouched (mobile navigation preserved)."""
    assert 'class="app-bottom-nav"' in _get(client)


def test_active_session_indicator_replaces_banner(client):
    # Sb_UI_03.3 — .active-banner removed; active-session state carried by the
    # Séance tab (has-active-session). Re-oriented to the new truth.
    src = BASE_TPL.read_text(encoding="utf-8")
    assert "active-banner" not in src
    assert "has-active-session" in src


def test_pwa_heads_intact(client):
    html = _get(client)
    assert 'rel="manifest"' in html
    assert 'rel="apple-touch-icon"' in html


def test_no_js_added(client):
    src = BASE_TPL.read_text(encoding="utf-8")
    assert "<script" not in src.lower()
    assert "addEventListener" not in src


def test_rail_derived_from_shared_mapping():
    """Rail reuses is_sess/is_programs/is_prog/is_prof — no divergent logic."""
    src = BASE_TPL.read_text(encoding="utf-8")
    rail = src[src.index('<aside class="app-rail"'):]
    for var in ("is_sess", "is_programs", "is_prog", "is_prof"):
        assert var in rail, f"rail must reuse shared mapping var {var}"
