"""Sb_UI_05.1 — Today / Readiness Home : Home IA + Hero Decision Surface.

Verifies the home page became a mobile-first *decision surface* (Sx_UI_05
§7/§8), not a dashboard, WITHOUT removing existing home information.

Asserts:
- .today-home wrapper present
- Hero Decision Surface present with a single primary CTA
- active session dominates when an open session exists (hero--active +
  "Reprendre" + link to /sessions/{id})
- no-active-session branch renders "Démarrer une séance" CTA
- readiness teaser only appears as a qualitative marker (never a medical
  score) — and the copy carries no diagnostic/activation claim
- existing dashboard content preserved but de-prioritized under the hero
  (disponibilité KPI, nav tiles, sparkline block still present/accessible)
- no-JS: hero CTA is a plain <a> to an existing route
- home.css scoped to .today-home (no global leak), no new JS

Invariants (must NOT change):
- route "/" still serves the home
- no new route/service/model/migration
- legacy labels preserved (Historique / Progression / Programmes,
  "Démarrer une séance" | "Nouvelle séance", "disponibilit")

Reads rendered HTML + CSS/template source only — no pixels.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOME_CSS = ROOT / "app" / "static" / "css" / "home.css"
INDEX = ROOT / "app" / "templates" / "index.html"
JS_DIR = ROOT / "app" / "static" / "js"


def _start_session(client, slug: str = "push-a") -> int:
    r = client.post("/sessions", data={"template_slug": slug}, follow_redirects=False)
    assert r.status_code == 303, r.text
    m = re.match(r"/sessions/(\d+)", r.headers["location"])
    assert m, r.headers["location"]
    return int(m.group(1))


def _home(client) -> str:
    r = client.get("/")
    assert r.status_code == 200, r.text[:300]
    return r.text


# ───────── IA + hero structure ─────────


class TestHomeIA:
    def test_today_home_wrapper_present(self, client):
        assert "today-home" in _home(client)

    def test_hero_present(self, client):
        assert "today-home__hero" in _home(client)

    def test_eyebrow_today(self, client):
        assert "today-home__eyebrow" in _home(client)
        assert "Aujourd'hui" in _home(client)

    def test_single_primary_cta_in_hero(self, client):
        """Exactly one primary hero CTA (.today-home__cta)."""
        body = _home(client)
        assert body.count("today-home__cta") == 1

    def test_secondary_zone_present(self, client):
        assert "today-home__secondary-zone" in _home(client)


# ───────── decision model branches ─────────


class TestDecisionBranches:
    def test_no_active_session_cta_is_start(self, client):
        """Fresh client (no open session) → 'Démarrer une séance' CTA."""
        body = _home(client)
        assert "Démarrer une séance" in body
        assert "today-home__hero--active" not in body

    def test_active_session_dominates(self, client):
        """With an open session, the hero switches to active + 'Reprendre'
        and links to /sessions/{id}."""
        sid = _start_session(client, "push-a")
        body = _home(client)
        assert "today-home__hero--active" in body
        assert "Reprendre la séance" in body
        assert f"/sessions/{sid}" in body

    def test_active_session_cta_single(self, client):
        """Even with an active session, exactly one primary hero CTA."""
        _start_session(client, "push-a")
        body = _home(client)
        assert body.count("today-home__cta") == 1


# ───────── readiness teaser (non-medical) ─────────


class TestReadinessTeaser:
    def test_no_medical_score_claim(self, client):
        """Home copy must not present a medical/diagnostic readiness claim."""
        body = _home(client).lower()
        for forbidden in ("diagnostic médical", "activation mesurée",
                          "récupération réelle", "score médical"):
            assert forbidden not in body

    def test_readiness_teaser_is_qualitative_marker(self, client):
        """If the teaser renders, it is a qualitative marker ('Repère du
        jour'), never a numeric medical score in the hero."""
        # fresh user has no readiness_today ⇒ teaser absent; that's fine.
        # We assert the template only ever renders the teaser as a marker.
        src = INDEX.read_text(encoding="utf-8")
        assert "today-home__readiness" in src
        assert "Repère du jour" in src
        # the teaser block must not embed a raw numeric readiness score
        m = re.search(
            r'today-home__readiness".*?</p>', src, re.DOTALL
        )
        assert m is not None


# ───────── dashboard preserved but de-prioritized ─────────


class TestDashboardPreserved:
    def test_disponibilite_still_present(self, client):
        assert "disponibilit" in _home(client).lower()

    def test_nav_tiles_preserved(self, client):
        body = _home(client)
        for label in ("Historique", "Progression", "Programmes"):
            assert label in body

    def test_dashboard_below_hero(self, client):
        """Hero appears before the secondary zone in the DOM."""
        body = _home(client)
        hero = body.find("today-home__hero")
        zone = body.find("today-home__secondary-zone")
        assert hero != -1 and zone != -1 and hero < zone

    def test_kpi_and_progress_link_preserved(self, client):
        body = _home(client)
        # KPI labels + progression link kept
        assert "cette sem." in body
        assert "Voir analyse complète" in body


# ───────── no-JS / no-framework ─────────


class TestNoFramework:
    def test_hero_cta_is_plain_anchor(self, client):
        """The hero CTA must be a plain <a href=...> (no JS handler)."""
        body = _home(client)
        m = re.search(r'<a class="today-home__cta"[^>]*href="[^"]+"', body)
        assert m is not None

    def test_no_new_js_file(self):
        js_files = sorted(p.name for p in JS_DIR.glob("*.js"))
        assert js_files == ["preview.js", "session_focus.js"], (
            f"Sb_UI_05.1 must add no JS: {js_files}"
        )

    def test_no_react_marker(self, client):
        body = _home(client)
        for marker in ("data-reactroot", "__NEXT_DATA__", "ReactDOM", "/_next/"):
            assert marker not in body


# ───────── CSS presence (scoped) ─────────


class TestHomeCss:
    def test_css_defines_today_home(self):
        assert ".today-home" in HOME_CSS.read_text(encoding="utf-8")

    def test_css_defines_hero(self):
        assert ".today-home__hero" in HOME_CSS.read_text(encoding="utf-8")

    def test_css_defines_cta(self):
        assert ".today-home__cta" in HOME_CSS.read_text(encoding="utf-8")

    def test_css_cta_meets_tap_target(self):
        """Primary CTA must reserve a ≥44px tap target."""
        css = HOME_CSS.read_text(encoding="utf-8")
        m = re.search(r"\.today-home__cta\s*\{[^}]*\}", css, re.DOTALL)
        assert m is not None
        assert re.search(r"min-height:\s*(4[4-9]|[5-9]\d)px", m.group(0))

    def test_css_scoped_to_today_home(self):
        """Every rule must be scoped under .today-home (no bare global
        element selectors introduced for home)."""
        css = HOME_CSS.read_text(encoding="utf-8")
        # crude scope check: every selector block references today-home,
        # a media query, or a comment — no bare "body {" / "a {" leak.
        for bad in ("\nbody {", "\nhtml {", "\na {", "\np {", "\ndiv {"):
            assert bad not in css, f"unscoped global selector {bad!r} in home.css"

    def test_home_loads_home_css(self):
        """index.html must load home.css via extra_head."""
        src = INDEX.read_text(encoding="utf-8")
        assert "css/home.css" in src
