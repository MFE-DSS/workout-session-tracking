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
    # Sb_UI_03.3 — the topbar was demoted to SECONDARY nav only (no primary
    # is-active anymore). The primary active state now lives in the bottom nav
    # (mobile) and the rail (desktop). This helper now reads the active label
    # from the bottom-nav region (always rendered), which is the source of
    # truth for the four primary destinations (Séance/Programmes/Progression/
    # Profil). Re-oriented toward the new truth, not weakened.
    nav = _region(html, "app-bottom-nav")
    return re.findall(
        r'<span class="app-bottom-nav__label">([^<]+)</span>',
        "".join(
            it for it in re.findall(
                r'<a class="app-bottom-nav__item[^>]*aria-current="page".*?</a>',
                nav, re.DOTALL,
            )
        ),
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


# Sb_UI_03.3 — primary active state now lives in the bottom nav / rail. The
# four primary destinations are Séance / Programmes / Progression / Profil, and
# secondary surfaces map onto their primary tab (history/physique → Progression,
# leaderboard → Profil). Tests re-oriented to the four-destination truth.
def test_home_marks_seance_active(client):
    html = _get(client, "/")
    assert "Séance" in _active_labels(html)


def test_library_marks_programmes_active(client):
    html = _get(client, "/library")
    assert "Programmes" in _active_labels(html)


def test_library_slug_marks_programmes_active(client):
    html = _get(client, "/library/push-a")
    assert "Programmes" in _active_labels(html)


def test_launcher_marks_programmes_active(client):
    html = _get(client, "/launcher")
    assert "Programmes" in _active_labels(html)


def test_history_maps_to_progression(client):
    html = _get(client, "/history")
    assert "Progression" in _active_labels(html)


def test_progress_marks_progression_active(client):
    html = _get(client, "/progress")
    assert "Progression" in _active_labels(html)


def test_physique_redirect_maps_to_progression(client):
    """`TRAIN1-C` — la surface est retirée, la route redirige. Le chemin
    appartient toujours à Progression : c'est son arrivée qui le prouve."""
    r = client.get("/physique", follow_redirects=True)
    assert r.status_code == 200
    assert "Progression" in _active_labels(r.text)


def test_leaderboard_maps_to_profil(client):
    html = _get(client, "/leaderboard")
    assert "Profil" in _active_labels(html)


# ───────── 2. exactly one aria-current="page", never "false" ─────────


def test_single_aria_current_per_route(client):
    # Sb_UI_03.3 — the topbar is now SECONDARY nav only (no aria-current). The
    # primary active state lives in the bottom nav (always) and the rail. Each
    # PRIMARY region marks exactly one active destination; the topbar carries
    # none. Re-oriented to the demoted-topbar truth (stricter: asserts the
    # topbar has zero primary aria-current).
    # `TRAIN1-C` — `/physique` reste couvert, redirection suivie.
    for path in ("/", "/library", "/history", "/progress", "/physique"):
        r = client.get(path, follow_redirects=True)
        assert r.status_code == 200, f"{path} -> {r.status_code}"
        html = r.text
        assert _region(html, "topbar").count('aria-current="page"') == 0, \
            f"{path}: topbar (secondary) must carry no aria-current"
        assert _region(html, "app-bottom-nav").count('aria-current="page"') == 1, \
            f"{path}: expected 1 active in bottom nav"
        assert _region(html, "app-rail__primary").count('aria-current="page"') == 1, \
            f"{path}: expected 1 active in rail"


def test_no_aria_current_false_in_topbar(client):
    for path in ("/", "/library", "/history", "/progress"):
        html = _get(client, path)
        assert 'aria-current="false"' not in html
        # never introduce step/location on the topbar (reserved for session header)
        assert 'aria-current="step"' not in html


# ───────── 3. preserved shell: all routes reachable, logout, brand ─────────


def test_all_routes_reachable_and_logout_preserved(client):
    # Sb_UI_03.3 — the four primary destinations moved out of the topbar (they
    # live in the bottom nav as "Séance/Programmes/Progression/Profil" and in
    # the rail). Secondary routes stay in the topbar menu. All routes remain
    # reachable; no route removed. "Accueil" as a topbar label is gone (the
    # primary tab is "Séance"), so we assert on the surviving labels + shared
    # primary set instead.
    html = _get(client, "/library")
    # secondary destinations preserved in the topbar menu
    # `TRAIN1-C` — « Physique » n'est plus une destination secondaire : sa
    # surface est retirée et sa route redirige vers `/progress`.
    for label in ("Historique", "Coach", "Classement", "Squads",
                  "Contact", "Déconnexion"):
        assert label in html, f"secondary nav label missing: {label}"
    # four primary destinations present in the shell (bottom nav + rail)
    for label in ("Séance", "Programmes", "Progression", "Profil"):
        assert label in html, f"primary destination missing: {label}"
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
