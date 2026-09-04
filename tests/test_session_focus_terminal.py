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

# ══════════════════════════════════════════════════════════════════════
#  Migré par `UIV3_SESSION_EXECUTION_CONSOLE_01` (2026-08-19)
#  ─────────────────────────────────────────────────────────────────────
#  Ce module épinglait des marqueurs d'IMPLÉMENTATION que `Sx_UIV3_02`
#  remplace. Les renommages sont mécaniques ; les invariants sont
#  inchangés. Là où le contrat lui-même change, le test porte une note
#  explicite — jamais une suppression silencieuse.
#
#    session-focus__console        → console__band
#    session-focus__console-list   → console__band
#    session-focus__console-refs   → console__delta
#    session-focus__console-row-*  → setline--*
#    session-focus__sticky-cta     → dock (plus AUCUN collant)
#    session-focus__set-action     → dock__cmd (commande unique)
# ══════════════════════════════════════════════════════════════════════

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

    def test_elevation_is_a_hairline_edge_not_a_halo(self):
        """Remplace `test_shadows_neutralized` — **la doctrine a changé, sur
        arbitrage opérateur.**

        L'ancienne garde exigeait `--shadow-sm: none` au nom du « terminal
        chrome ». C'était `SYS-078` (« surface par défaut sans ombre, une seule
        élévation »), que `AUREN_VISUAL_BACKBONE §6` supersède explicitement
        après les arbitrages `L-07` (profondeur assumée), `K-01` (échelle à
        quatre niveaux), `Q1=C` et `Q4=B` du 2026-09-04.

        Elle avait en outre un effet pervers mesuré : **elle exigeait le
        défaut**. Trois règles écrivaient `box-shadow: var(--shadow-sm)` — dont
        l'en-tête et la barre collants — et rendaient `none`. La garde
        garantissait que l'intention écrite dans le code ne produise rien.

        Ce qui la remplace protège ce qui, lui, ne périme pas : **le registre
        reste terminal.** Une élévation y est une ARÊTE — un trait de lumière
        et un trait d'ombre, flou ≤ 2 px — jamais un halo diffus. C'est la
        différence entre un instrument et une carte de tableau de bord web.
        """
        css = FOCUS_CSS.read_text(encoding="utf-8")
        for token in ("--shadow-sm", "--shadow-md"):
            m = re.search(rf"{re.escape(token)}:\s*([^;]+);", css)
            assert m, f"{token} n'est plus déclaré"
            value = m.group(1).strip()
            assert value != "none", (
                f"{token} vaut `none` — les règles qui le consomment ne "
                "rendent rien, alors que le code se lit comme une intention"
            )
            assert value.startswith("var(--relief-"), (
                f"{token} = {value!r} : l'élévation doit passer par le relief "
                "partagé, pas par une ombre déclarée sur place"
            )

        # Le relief lui-même reste une arête, pas un halo.
        app_css = (FOCUS_CSS.parent / "app.css").read_text(encoding="utf-8")
        relief = re.search(r"--relief-raised:\s*([^;]+);", app_css)
        assert relief, "--relief-raised introuvable"
        blurs = [int(b) for b in re.findall(r"\b(\d+)px\b", relief.group(1))]
        # Deux assertions distinctes, et pas par conformité : « aucune longueur
        # lisible » et « flou trop large » sont deux défauts différents. Les
        # réunir par un `and` rendait le même message pour les deux.
        assert blurs, (
            f"--relief-raised ne contient aucune longueur en px : "
            f"{relief.group(1).strip()!r} — la garde ne mesurerait rien"
        )
        assert max(blurs) <= 2, (
            f"flou {max(blurs)}px — au-delà de 2 px ce n'est plus une arête "
            "d'instrument, c'est une ombre portée de carte web"
        )

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
        assert "console__band" in _body(client)

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
        """MIGRÉ par `UIV3_SESSION_EXECUTION_CONSOLE_01` : le minuteur n'existe plus que dans l'état `REST` (`Sx_UIV3_02 §7.2`). Le rendre en permanence est précisément ce qui a masqué le défaut `D3` — le bloc était là, non démarré, et le JS partait quand même. Le contrat conservé est que le minuteur n'est JAMAIS requis pour enregistrer."""
        body = _body(client)
        assert "data-rest-display" not in body
        assert 'name="nav"' in body, "enregistrer ne dépend pas du minuteur"

    def test_anchors_and_feedback_preserved(self, client):
        body = _body(client, n=3)
        assert len(re.findall(r'href="[^"]*#exercise-\d+"', body)) >= 3
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
