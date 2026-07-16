"""Sx_NAV_01 — Active Navigation Semantics.

The shared topbar (base.html) now derives an active state from
request.url.path: the matching surface link carries `is-active` +
`aria-current="page"`. SSR / no-JS / template-only — no route/service/data
change. Inactive links carry NO aria-current (never "false").
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE_TPL = ROOT / "app" / "templates" / "base.html"
APP_CSS = ROOT / "app" / "static" / "css" / "app.css"
PAGES_ROUTER = ROOT / "app" / "routers" / "pages.py"


def _get(client, path):
    r = client.get(path, follow_redirects=False)
    assert r.status_code == 200, f"{path} -> {r.status_code}: {r.text[:200]}"
    return r.text


def _active_labels(html: str) -> list[str]:
    return re.findall(
        r'<a class="topbar__link is-active"[^>]*>([^<]+)</a>', html
    )


def _region(html: str, cls: str) -> str:
    """Isolate a nav region (<header class="topbar"> or <nav class="cls">)."""
    if cls == "topbar":
        m = re.search(r"<header class=\"topbar\".*?</header>", html, re.DOTALL)
    else:
        m = re.search(rf'<nav class="{cls}".*?</nav>', html, re.DOTALL)
    return m.group(0) if m else ""


def _aria_current_count(html: str) -> int:
    # Sb_UI_03.1 — the shell now has TWO nav regions (topbar menu + mobile
    # bottom nav), each marking its own active destination. The invariant is
    # "exactly one active PER REGION", not one globally. This re-orientation
    # tracks the new truth and is stricter (it checks both regions), never a
    # weakening. Kept for backward reference; region-aware checks below.
    return html.count('aria-current="page"')


# ───────── 1. each surface marks the right link active ─────────


def test_home_marks_accueil_active(client):
    html = _get(client, "/")
    assert "Accueil" in _active_labels(html)


def test_library_marks_programmes_active(client):
    html = _get(client, "/library")
    assert "Programmes" in _active_labels(html)


def test_library_slug_marks_programmes_active(client):
    html = _get(client, "/library/push-a")
    assert "Programmes" in _active_labels(html)


def test_launcher_marks_programmes_active(client):
    html = _get(client, "/launcher")
    assert "Programmes" in _active_labels(html)


def test_history_marks_historique_active(client):
    html = _get(client, "/history")
    assert "Historique" in _active_labels(html)


def test_progress_marks_progression_active(client):
    html = _get(client, "/progress")
    assert "Progression" in _active_labels(html)


def test_physique_marks_physique_active(client):
    html = _get(client, "/physique")
    assert "Physique" in _active_labels(html)


def test_leaderboard_marks_classement_active(client):
    html = _get(client, "/leaderboard")
    assert "Classement" in _active_labels(html)


# ───────── 2. exactly one aria-current="page", never "false" ─────────


def test_single_aria_current_per_route(client):
    # Sb_UI_03.1 — new truth: exactly one active PER REGION (topbar menu AND
    # mobile bottom nav), each derived from request.url.path. Previously the
    # shell had a single region; now both must mark exactly one active tab.
    for path in ("/", "/library", "/history", "/progress", "/physique"):
        html = _get(client, path)
        assert _region(html, "topbar").count('aria-current="page"') == 1, \
            f"{path}: expected 1 active in topbar"
        assert _region(html, "app-bottom-nav").count('aria-current="page"') == 1, \
            f"{path}: expected 1 active in bottom nav"


def test_no_aria_current_false_in_topbar(client):
    for path in ("/", "/library", "/history", "/progress"):
        html = _get(client, path)
        assert 'aria-current="false"' not in html
        # never introduce step/location on the topbar (reserved for session header)
        assert 'aria-current="step"' not in html


# ───────── 3. preserved shell: all links, logout, banner, brand ─────────


def test_all_nav_links_and_logout_preserved(client):
    html = _get(client, "/library")
    for label in (
        "Accueil", "Programmes", "Historique", "Physique", "Progression",
        "Classement", "Squads", "Profil", "Coach", "Déconnexion",
    ):
        assert label in html, f"nav label missing: {label}"
    # logout is still a POST form
    assert 'method="post"' in html
    assert "topbar__brand" in html  # brand preserved


# ───────── 4. non-goals: template-only, no JS, no new colour ─────────


def test_base_uses_request_path_not_router():
    src = BASE_TPL.read_text(encoding="utf-8")
    assert "request.url.path" in src
    assert "is-active" in src
    assert 'aria-current="page"' in src


def test_no_js_added_to_base():
    src = BASE_TPL.read_text(encoding="utf-8")
    # the active state is pure SSR — no script for nav
    assert "addEventListener" not in src
    # base already has meta only; ensure no nav <script> added
    assert "activeNav" not in src


def test_active_css_reuses_existing_variable():
    css = APP_CSS.read_text(encoding="utf-8")
    assert ".topbar__link.is-active" in css
    # reuses var(--fg); no new hex colour introduced for the active state
    m = re.search(r"\.topbar__link\.is-active\s*\{([^}]*)\}", css)
    assert m, "active rule not found"
    rule = m.group(1)
    assert "var(--fg)" in rule
    assert "#" not in rule  # no raw hex colour


def test_pages_router_not_modified():
    src = PAGES_ROUTER.read_text(encoding="utf-8")
    assert "is_programs" not in src
    assert "active_nav" not in src
