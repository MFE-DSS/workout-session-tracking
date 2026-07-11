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
        """Exactly one primary hero CTA. Sx_UI_06 Sb_UI_06.3 : the CTA is
        either an <a> (resume / fallback start) or a <button> in a POST form
        (start the recommended session directly). In all cases exactly one
        `today-home__cta` element carries the primary action (the optional
        `today-home__cta-form` wrapper is not counted)."""
        body = _home(client)
        # count the CTA element itself: class token followed by a quote,
        # excluding the form wrapper class `today-home__cta-form`.
        assert body.count('today-home__cta"') == 1

    def test_secondary_zone_present(self, client):
        assert "today-home__secondary-zone" in _home(client)

    def test_terminal_direction_marker(self, client):
        """Sb_UI_02b.1 — the Home carries the Auren Terminal marker class."""
        assert "today-home--terminal" in _home(client)

    def test_status_label_present(self, client):
        assert "today-home__status" in _home(client)

    def test_action_block_present(self, client):
        assert "today-home__action" in _home(client)

    def test_summary_eyebrow_deprioritizes_dashboard(self, client):
        body = _home(client)
        assert "today-home__summary-eyebrow" in body
        assert "Résumé" in body


# ───────── Auren Terminal visual system (graphite / mono / amber) ─────────


class TestAurenTerminal:
    def test_no_teal_in_home_css(self):
        """The teal-light COLOR VALUES must be fully removed from home.css
        (the word 'teal' may still appear in a comment documenting the
        removal — we check hex tokens, i.e. the actual visual leak risk)."""
        css = HOME_CSS.read_text(encoding="utf-8").lower()
        for teal_hex in ("#0f8a85", "#0b7a75", "#095e5a", "#d4edeb"):
            assert teal_hex not in css, f"leftover teal hex {teal_hex!r} in home.css"

    def test_amber_accent_present(self):
        css = HOME_CSS.read_text(encoding="utf-8").lower()
        assert "#c8a24b" in css, "amber accent #C8A24B missing from home.css"

    def test_graphite_surfaces_present(self):
        """Graphite dark surfaces must be defined (dark bg, not white)."""
        css = HOME_CSS.read_text(encoding="utf-8").lower()
        assert "#0f1318" in css or "#151a21" in css
        # white surface of the teal build must be gone as a hero background
        assert "--home-surface: #ffffff" not in css

    def test_mono_typography(self):
        """The Home must use a monospace stack (terminal), not a sans stack."""
        css = HOME_CSS.read_text(encoding="utf-8").lower()
        assert "monospace" in css
        assert "ui-monospace" in css

    def test_no_webfont_import(self):
        """No @import / @font-face / external font in home.css (system mono)."""
        css = HOME_CSS.read_text(encoding="utf-8").lower()
        assert "@import" not in css
        assert "@font-face" not in css
        assert "fonts.googleapis" not in css

    def test_no_decorative_box_shadow_on_hero(self):
        """Terminal chrome: the hero uses 1px line, no decorative drop shadow."""
        css = HOME_CSS.read_text(encoding="utf-8")
        m = re.search(r"\.today-home__hero\s*\{[^}]*\}", css, re.DOTALL)
        assert m is not None
        assert "box-shadow" not in m.group(0) or "box-shadow: none" in m.group(0)


# ───────── decision model branches ─────────


class TestDecisionBranches:
    def test_no_active_session_cta_is_start(self, client):
        """Fresh client (no open session) → a start CTA. Sx_UI_06 Sb_UI_06.3 :
        with a recommendation the hero starts it directly (« Démarrer »); the
        cold-start fallback is « Démarrer une séance ». Either way it is a
        start action and the hero is not in the active state."""
        body = _home(client)
        assert "Démarrer" in body
        assert "today-home__hero--active" not in body

    def test_active_session_dominates(self, client):
        """With an open session, the hero switches to active + 'Reprendre'
        and links to /sessions/{id}."""
        sid = _start_session(client, "push-a")
        body = _home(client)
        assert "today-home__hero--active" in body
        assert "Reprendre" in body
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

    def test_readiness_teaser_removed_from_hero(self, client):
        """Sx_UI_06 Sb_UI_06.3 — the hero readiness teaser (which only said
        « détail plus bas », carrying no data) is removed. Readiness now lives
        in its single widget below the hero; no numeric medical score in the
        hero."""
        src = INDEX.read_text(encoding="utf-8")
        # teaser class gone from the hero
        assert "today-home__readiness" not in src
        # the readiness widget (self-report state) still exists
        assert "readiness-widget" in src
        assert "État du jour" in src


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
    def test_hero_cta_is_no_js(self, client):
        """The hero CTA must be no-JS: either a plain <a href> (resume /
        fallback) or a <button> submitting a POST form to /sessions (start
        the recommended session). Both are server-driven, no JS handler.
        Sx_UI_06 Sb_UI_06.3."""
        body = _home(client)
        anchor = re.search(r'<a class="today-home__cta"[^>]*href="[^"]+"', body)
        form_button = (
            'today-home__cta-form' in body
            and 'action="/sessions"' in body
            and re.search(r'<button[^>]*class="today-home__cta"', body) is not None
        )
        assert anchor is not None or form_button

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
