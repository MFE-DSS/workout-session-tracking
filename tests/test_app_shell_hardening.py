"""Sb_UI_03.3 — App Shell Hardening (3rd & final build of Sx_UI_03).

Closes three shell residuals:
  1. the topbar mobile/tablet menu is demoted to SECONDARY navigation only
     (the four primary destinations live in the bottom nav + rail; no route
     removed);
  2. the global .active-banner is removed — the Home hero stays the single
     direct "Reprendre" surface, and the active-session state is carried by the
     "Séance" tab (has-active-session + discreet dot + sr-only "En cours");
  3. a skip link ("Aller au contenu principal" → #main-content) is added as the
     first interactive element of <body>.

Template + CSS only — no route/service/model/data/JS/POST/Home-logic change.
Broader a11y (reduced-motion, form aria-live/invalid, contrast, auth pages,
charts/BodyMap) stays deferred to Sx_UI_09.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE_TPL = ROOT / "app" / "templates" / "base.html"
INDEX_TPL = ROOT / "app" / "templates" / "index.html"
APP_CSS = ROOT / "app" / "static" / "css" / "app.css"


def _get(client, path="/"):
    r = client.get(path, follow_redirects=False)
    assert r.status_code == 200, f"{path} -> {r.status_code}: {r.text[:200]}"
    return r.text


def _topbar(html: str) -> str:
    m = re.search(r'<header class="topbar".*?</header>', html, re.DOTALL)
    assert m, "topbar not found"
    return m.group(0)


def _start(client, slug="push-a"):
    r = client.post("/sessions", data={"template_slug": slug}, follow_redirects=False)
    assert r.status_code in (200, 303), r.status_code
    return r


# ───────── 1. topbar demoted to secondary ─────────


def test_topbar_present(client):
    assert 'class="topbar"' in _get(client)


def test_topbar_nav_labelled_secondary(client):
    assert 'aria-label="Navigation secondaire"' in _topbar(_get(client))


def test_topbar_has_no_primary_destinations(client):
    tb = _topbar(_get(client))
    # the four primary destinations are no longer in the topbar menu
    assert "Accueil" not in tb
    assert ">Programmes<" not in tb
    assert ">Progression<" not in tb
    assert ">Profil<" not in tb


def test_topbar_keeps_secondary_routes(client):
    tb = _topbar(_get(client))
    # `TRAIN1-C` — « Physique » retirée : surface supprimée, route redirigée.
    # `TRAIN1-D` — « Coach » devient « Coach Report » (c'est un document, et le
    # libellé le dit) ; « Sauvegarde » entre dans le menu, la route `/export`
    # n'étant liée depuis aucun gabarit jusqu'ici.
    for label in ("Historique", "Coach Report", "Sauvegarde", "Squads",
                  "Classement", "Contact"):
        assert f">{label}</a>" in tb, f"secondary route missing from topbar: {label}"


def test_topbar_logout_is_post(client):
    tb = _topbar(_get(client))
    assert 'method="post"' in tb
    assert "topbar__link--btn" in tb


def test_topbar_no_aria_current(client):
    """Secondary nav carries no aria-current (primary tabs own it)."""
    for path in ("/", "/history", "/squads", "/progress"):
        assert 'aria-current' not in _topbar(_get(client, path))


def test_topbar_secondary_active_uses_subactive(client):
    """On /history the secondary link is is-subactive, not aria-current."""
    tb = _topbar(_get(client, "/history"))
    assert "is-subactive" in tb
    assert 'aria-current' not in tb


# ───────── 2. active-banner removed + nav indicator ─────────


def test_no_active_banner_markup_in_template():
    src = BASE_TPL.read_text(encoding="utf-8")
    assert 'class="active-banner"' not in src


def test_no_active_banner_css():
    """Dead .active-banner CSS is removed (no rendering surface uses it)."""
    css = APP_CSS.read_text(encoding="utf-8")
    # no selector rule remains (comments mentioning the removal are fine)
    assert not re.search(r"^\.active-banner[ {.]", css, re.MULTILINE)
    # the pulse keyframe rule is gone (only the banner dot used it); a comment
    # mentioning its removal is fine, so match the rule opening, not the word.
    assert "@keyframes pulse {" not in css


def test_indicator_present_when_session_open(client):
    _start(client)
    body = client.get("/library").text
    assert "has-active-session" in body
    assert "app-shell__session-dot" in body
    # accessible text present exactly once per region (bottom nav + rail = 2)
    assert body.count("En cours") == 2


def test_indicator_absent_when_no_session(client):
    body = client.get("/library").text
    assert "has-active-session" not in body
    assert "En cours" not in body


def test_seance_href_still_root_with_active_session(client):
    _start(client)
    body = client.get("/library").text
    # the Séance item still points at / (no conditional /sessions/{id} link)
    nav = re.search(r'<nav class="app-bottom-nav".*?</nav>', body, re.DOTALL).group(0)
    seance = re.search(r'<a class="app-bottom-nav__item[^"]*"[^>]*>.*?Séance.*?</a>', nav, re.DOTALL).group(0)
    href = re.search(r'href="([^"]+)"', seance).group(1)
    assert re.sub(r"^https?://[^/]+", "", href) in ("/", "")


def test_home_hero_untouched():
    """index.html keeps its Reprendre hero (single resume surface)."""
    src = INDEX_TPL.read_text(encoding="utf-8")
    assert "Reprendre" in src
    assert "open_session" in src


def test_no_global_resume_cta_on_secondary_page(client):
    """A secondary page shows no global Reprendre banner CTA."""
    _start(client)
    body = client.get("/history").text
    assert "active-banner__cta" not in body
    assert "active-banner" not in body


# ───────── 3. skip link ─────────


def test_skip_link_is_first_interactive(client):
    html = _get(client)
    body = html[html.index("<body"):]
    # first <a> / <button> after <body> is the skip link
    first = re.search(r"<(a|button)\b[^>]*>", body)
    assert first and "skip-link" in body[first.start():first.end()], \
        "skip link must be the first interactive element"


def test_skip_link_href_and_label(client):
    html = _get(client)
    assert re.search(
        r'<a class="skip-link" href="#main-content">\s*Aller au contenu principal\s*</a>',
        html,
    )


def test_main_has_id(client):
    html = _get(client)
    assert '<main id="main-content"' in html


def test_skip_link_css_hidden_then_focus_visible():
    css = APP_CSS.read_text(encoding="utf-8")
    m = re.search(r"\.skip-link\s*\{([^}]*)\}", css)
    assert m, ".skip-link rule missing"
    body = m.group(1)
    assert "position: fixed" in body
    assert "translateY(-120%" in body  # off-screen at rest
    # a focus rule reveals it
    assert re.search(r"\.skip-link:focus[^{]*\{[^}]*translateY", css, re.DOTALL)


def test_skip_link_no_new_hex():
    css = APP_CSS.read_text(encoding="utf-8")
    block = css[css.index("Sb_UI_03.3 — App Shell Hardening"):]
    assert not re.search(r"#[0-9a-fA-F]{3,6}", block), "raw hex in hardening CSS"


# ───────── CSS cleanup / no-animation ─────────


def test_session_dot_has_no_animation():
    css = APP_CSS.read_text(encoding="utf-8")
    m = re.search(r"\.app-shell__session-dot\s*\{([^}]*)\}", css)
    assert m and "animation" not in m.group(1)


def test_breakpoints_unchanged():
    """Sb_UI_03.1/.2 breakpoints preserved (bottom nav hidden ≥1024, rail ≥1024)."""
    css = APP_CSS.read_text(encoding="utf-8")
    assert "@media (min-width: 1024px)" in css
    assert ".app-rail { display: none; }" in css


# ───────── non-regression ─────────


def test_four_bottom_nav_destinations(client):
    nav = re.search(r'<nav class="app-bottom-nav".*?</nav>', _get(client), re.DOTALL).group(0)
    assert nav.count("app-bottom-nav__item") == 4


def test_four_rail_destinations(client):
    prim = re.search(r'<nav class="app-rail__primary".*?</nav>', _get(client), re.DOTALL).group(0)
    assert prim.count("app-rail__item") == 4


def test_pwa_heads_intact(client):
    html = _get(client)
    assert 'rel="manifest"' in html
    assert 'rel="apple-touch-icon"' in html


def test_no_js(client):
    src = BASE_TPL.read_text(encoding="utf-8")
    assert "<script" not in src.lower()
    assert "addEventListener" not in src


def test_shared_mapping_preserved():
    src = BASE_TPL.read_text(encoding="utf-8")
    for var in ("is_sess", "is_programs", "is_prog", "is_prof"):
        assert var in src
