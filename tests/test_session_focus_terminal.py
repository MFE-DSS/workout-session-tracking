"""Sb_UI_02b.2 — Auren Terminal Focus Mode re-skin tests.

Verifies the Focus Mode (session) surface migrated to Auren Terminal
(graphite + mono + amber), consistent with the Home (Sb_UI_02b.1),
WITHOUT touching the Sx_UI_04 interaction architecture.

Asserts (CSS-level, re-skin):
- teal color values fully removed from session_focus.css
- amber accent #C8A24B present
- graphite dark surfaces present (dark base bg, not white)
- monospace stack present; --font-family-sans remapped to mono
- decorative shadows neutralized (--shadow-* : none)

Asserts (render-level, contracts preserved):
- session-focus--terminal marker present on the page
- cockpit / console / worked area / mini-stepper / up-next still render
- set logging inputs (weight_kg / reps) names unchanged
- form action/method unchanged
- rest timer data-* contracts unchanged
- substitution surface + anchors + #session-feedback preserved
- no JS added, no medical claim

Reads rendered HTML + CSS source only — no pixels.
"""
from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FOCUS_CSS = ROOT / "app" / "static" / "css" / "session_focus.css"
HOME_CSS = ROOT / "app" / "static" / "css" / "home.css"
SESSION_DETAIL = ROOT / "app" / "templates" / "session_detail.html"
JS_DIR = ROOT / "app" / "static" / "js"


def _seed(db, user_id, n=3):
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    s = WorkoutSession(
        user_id=user_id,
        template_slug_snapshot="terminal",
        template_name_snapshot="Terminal test",
        started_at=datetime.now(UTC),
        status="in_progress",
    )
    for i in range(n):
        se = SessionExercise(
            exercise_code_snapshot=f"E{i + 1}",
            exercise_name_snapshot=f"Exercise {i + 1}",
            position=i + 1,
        )
        se.set_logs.append(
            SetLog(kind="work", set_index=1, weight_kg=None, reps=None, completed=False)
        )
        s.session_exercises.append(se)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def _body(client, n=3) -> str:
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _seed(db, user.id, n=n)
        sid = s.id
    r = client.get(f"/sessions/{sid}", follow_redirects=False)
    assert r.status_code == 200, r.text[:300]
    return r.text


# ───────── Auren Terminal CSS ─────────


class TestTerminalCss:
    def test_no_teal_hex_in_focus_css(self):
        """The teal color VALUES must be gone (word 'teal' may remain in a
        comment documenting removal — check hex, the visual leak risk)."""
        css = FOCUS_CSS.read_text(encoding="utf-8").lower()
        for teal_hex in ("#0f8a85", "#0b7a75", "#095e5a", "#d4edeb"):
            assert teal_hex not in css, f"leftover teal hex {teal_hex!r} in session_focus.css"

    def test_amber_accent_present(self):
        css = FOCUS_CSS.read_text(encoding="utf-8").lower()
        assert "#c8a24b" in css, "amber accent missing from session_focus.css"

    def test_graphite_surfaces_present(self):
        css = FOCUS_CSS.read_text(encoding="utf-8").lower()
        assert "#0f1318" in css or "#151a21" in css
        # the white Clinical-Lab base must be gone as a token value
        assert "--color-bg-base:       #ffffff" not in css

    def test_mono_typography(self):
        css = FOCUS_CSS.read_text(encoding="utf-8").lower()
        assert "ui-monospace" in css
        # the sans stack must be remapped onto mono (all-mono terminal)
        assert re.search(
            r"--font-family-sans:\s*var\(--font-family-mono\)", css
        ), "--font-family-sans must be remapped to mono for the terminal"

    def test_no_webfont(self):
        css = FOCUS_CSS.read_text(encoding="utf-8").lower()
        assert "@import" not in css
        assert "@font-face" not in css
        assert "fonts.googleapis" not in css

    def test_shadows_neutralized(self):
        """Terminal chrome : the shadow tokens must resolve to none."""
        css = FOCUS_CSS.read_text(encoding="utf-8")
        assert re.search(r"--shadow-sm:\s*none", css)
        assert re.search(r"--shadow-md:\s*none", css)

    def test_consistent_with_home_amber(self):
        """Focus and Home must share the same amber accent."""
        assert "#C8A24B" in FOCUS_CSS.read_text(encoding="utf-8")
        assert "#C8A24B" in HOME_CSS.read_text(encoding="utf-8")


# ───────── terminal marker + contracts preserved ─────────


class TestTerminalMarkerAndContracts:
    def test_terminal_marker_present(self, client):
        assert "session-focus--terminal" in _body(client)

    def test_cockpit_preserved(self, client):
        body = _body(client)
        assert "session-focus__cockpit" in body
        assert "session-focus__stepper" in body

    def test_console_preserved(self, client):
        assert "session-focus__console" in _body(client)

    def test_worked_area_preserved(self, client):
        assert "session-focus__worked-area" in _body(client)

    def test_weight_reps_input_names_unchanged(self, client):
        body = _body(client)
        assert re.search(r'name="set_\d+_weight_kg"', body)
        assert re.search(r'name="set_\d+_reps"', body)

    def test_form_action_method_unchanged(self, client):
        body = _body(client)
        assert 'method="post"' in body
        assert re.search(r'action="[^"]*/sessions/\d+/exercises/\d+"', body)

    def test_rest_timer_data_contracts_unchanged(self, client):
        body = _body(client)
        assert "data-rest-display" in body or "session-focus__rest-timer" in body

    def test_anchors_and_feedback_preserved(self, client):
        body = _body(client, n=3)
        assert len(re.findall(r'href="#exercise-\d+"', body)) >= 3
        assert 'id="session-feedback"' in body

    def test_aria_current_location_only(self, client):
        body = _body(client)
        assert 'aria-current="location"' in body
        assert 'aria-current="false"' not in body


# ───────── no framework / no medical ─────────


class TestNoLeak:
    def test_no_new_js(self):
        js_files = sorted(p.name for p in JS_DIR.glob("*.js"))
        # Sb_UI_PROFILE_PREFERENCES_REDESIGN_01 — inventaire JS versionné.
        #
        # Cette assertion prouvait à l'origine que CETTE tranche n'ajoutait
        # aucun JS. Écrite comme un inventaire exact du répertoire, elle a
        # transformé une garantie historique de tranche en interdiction
        # permanente de toute amélioration progressive future — ce n'était
        # pas le contrat produit visé.
        #
        # L'inventaire JS courant de l'application est désormais versionné
        # explicitement ; `prefs_focus_rank.js` est autorisé par l'opérateur
        # au titre de AUREN_INTERACTION_REFINEMENT_01. Le caractère EXACT est
        # conservé : un quatrième fichier JS inattendu fait toujours échouer.
        assert js_files == ["prefs_focus_rank.js", "preview.js", "session_focus.js"], (
            f"Sb_UI_02b.2 must add no JS: {js_files}"
        )

    def test_no_medical_claim(self, client):
        body = _body(client).lower()
        for forbidden in ("diagnostic médical confirmé", "activation mesurée"):
            assert forbidden not in body

    def test_marker_wired_in_template(self):
        src = SESSION_DETAIL.read_text(encoding="utf-8")
        assert "session-focus--terminal" in src
