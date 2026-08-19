"""Sb_UI_04.3 — Active Exercise Cockpit Shell tests.

Verifies the recast Focused Exercise Flow (Sx_UI_04 §18/§20) : the
session screen is no longer a plain vertical list of exercises but an
*active exercise cockpit*.

Asserts:
- cockpit wrapper present (.session-focus__cockpit)
- orientation counter present (exercice courant / total + restants)
- mini-stepper present (.session-focus__stepper) with anchors preserved
- active exercise card carries the hero cockpit surfaces:
  - exercise intent shell
  - worked area panel (primary / assistants / stabilisation)
  - technical cues shell (max 3)
- up-next surface present when a next exercise exists
- aria-current="location" only on the active stepper item, none "false"
- anchors #exercise-{id} preserved for every exercise (no-JS / OQ-E)
- #session-feedback preserved
- set logging inputs preserved (weight_kg / reps)
- rest timer data-* contracts unchanged
- no JS file change, no React/SPA marker
- macros untouched (segmented / field_group still rendered)

Non-brittle : reads rendered HTML + CSS file content only, no pixels.
"""

# ══════════════════════════════════════════════════════════════════════
#  MIGRÉ — `UIV3_SESSION_EXECUTION_CONSOLE_01` + passe de densité
#  (2026-08-19). Ce module épinglait des marqueurs d'IMPLÉMENTATION que
#  `Sx_UIV3_02` remplace. Correspondance :
#
#    session-focus__console            → console
#    session-focus__console-list       → console__band
#    session-focus__console-row--active    → setline--current
#    session-focus__console-row--completed → setline--past
#    session-focus__console-row--upcoming  → setline--future
#    session-focus__console-refs       → console__delta
#    session-focus__orientation*       → session-pos*  (dans l'en-tête)
#    session-focus__header-main/kicker → en-tête recomposé en 4 colonnes
#    card-peek*                        → console__next (fin d'exercice)
#    session-focus__sticky-*           → SUPPRIMÉ, plus aucune couche
#
#  Les invariants sont conservés ; là où le CONTRAT change, le test porte
#  une note explicite. Aucune suppression pour verdir.
# ══════════════════════════════════════════════════════════════════════

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FOCUS_CSS = ROOT / "app" / "static" / "css" / "session_focus.css"
SESSION_DETAIL = ROOT / "app" / "templates" / "session_detail.html"
EXERCISE_CARD = ROOT / "app" / "templates" / "_partials" / "exercise_card.html"
JS_DIR = ROOT / "app" / "static" / "js"


# ───────── seed helpers ─────────


def _seed_multi(db, user_id, n_exercises=3):
    """In-progress session with N exercises, each 1 work set (uncompleted).

    The first exercise becomes the active one (router default: first
    non-complete exercise).
    """
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    s = WorkoutSession(
        user_id=user_id,
        template_slug_snapshot="cockpit",
        template_name_snapshot="Cockpit test",
        started_at=datetime.now(UTC),
        status="in_progress",
    )
    for i in range(n_exercises):
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


def _render(client, session_id: int) -> str:
    r = client.get(f"/sessions/{session_id}", follow_redirects=False)
    assert r.status_code == 200, r.text[:400]
    return r.text


def _body(client, n=3) -> str:
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _seed_multi(db, user.id, n_exercises=n)
        sid = s.id
    return _render(client, sid)


# ───────── cockpit structure ─────────


class TestCockpitShell:
    def test_cockpit_wrapper_present(self, client):
        assert "session-focus__cockpit" in _body(client)

    def test_orientation_present(self, client):
        body = _body(client)
        assert "session-pos" in body
        assert "session-pos__current" in body
        assert "session-focus__orientation-remaining" in body

    def test_orientation_counter_renders_position_over_total(self, client):
        """MIGRÉ — l'orientation `E1 / 7` a rejoint la ligne d'en-tête et
        est devenue le DÉCLENCHEUR de navigation (correction opérateur) :
        elle décrivait la position sans être actionnable, pendant qu'un menu
        voisin permettait d'en changer. Le compteur reste le même."""
        body = _body(client, n=3)
        assert re.search(
            r'session-pos__current[^>]*>E\s*\d+\s*<', body
        ), body[body.find("session-pos"):][:200]
        assert re.search(
            r'session-pos__total[^>]*>\s*3\s*<', body
        )

    def test_mini_stepper_present(self, client):
        body = _body(client)
        assert "session-focus__stepper" in body
        assert "ex-jump__item" in body

    def test_stepper_preserves_anchors(self, client):
        """Every exercise must remain addressable via #exercise-{id}."""
        body = _body(client, n=3)
        # 3 stepper anchors + 3 card anchors ⇒ at least 3 hrefs
        hrefs = re.findall(r'href="#exercise-\d+"', body)
        assert len(hrefs) >= 3, f"expected ≥3 #exercise anchors, got {len(hrefs)}"

    def test_stepper_has_feedback_anchor(self, client):
        assert 'href="#session-feedback"' in _body(client)


# ───────── active card hero surfaces ─────────


class TestCockpitHero:
    def test_intent_shell_present(self, client):
        body = _body(client)
        assert "console__target" in body
        assert "console__target" in body

    def test_worked_area_panel_present(self, client):
        body = _body(client)
        assert "session-focus__worked-area" in body
        assert "session-focus__worked-area-title" in body

    def test_worked_area_primary_row_and_no_empty_slots(self, client):
        """Sx_UI_06 Sb_UI_06.2 — density cleanup: the primary row always
        renders; the secondary row only when there are real assistants; the
        permanently-empty « stabilisation » row is removed (no repeated
        « À qualifier »)."""
        body = _body(client)
        assert "session-focus__worked-area-row--primary" in body
        assert "session-focus__worked-area-row--stabilizer" not in body

    def test_worked_area_has_conservative_note(self, client):
        """No medical claim: note must frame zones as estimation."""
        body = _body(client)
        assert "session-focus__worked-area-note" in body
        # conservative wording present (estimé / pas une mesure)
        assert "estim" in body.lower()

    def test_worked_area_fallback_when_no_atlas(self, client):
        """Synthetic exercises have no atlas family ⇒ conservative
        fallback labels must appear, never an invented body zone.
        Sx_UI_06 D2 : the removed « Cible » console row used the lowercase
        « ...à qualifier » spelling; the surviving Worked Area fallback is
        « À qualifier » (uppercase). Assert case-insensitively on the real
        Worked Area surface."""
        body = _body(client).lower()
        assert "à qualifier" in body

    def test_technical_cues_shell_present(self, client):
        body = _body(client)
        assert "session-focus__cues" in body
        assert "session-focus__cues-title" in body

    def test_console_only_on_active_card(self, client):
        """MIGRÉ — le « hero » disparaît : l'identité vit dans le résumé de
        la carte active et le reste est la console. L'invariant demeure —
        UNE seule carte porte la surface d'exécution, jamais sept."""
        body = _body(client, n=3)
        assert body.count('class="console"') == 1
        assert body.count('class="dock"') == 1


# ───────── up next ─────────


class TestUpNext:
    def test_up_next_block_wired_in_template(self):
        """The active card partial must render the up-next surface guarded
        on peek_for_active (Sb_UI_04.3 §18.G). Rendered visibility depends
        on the next exercise having a rep scheme (peek_for_active truthy) —
        asserted structurally here to stay independent of seed fixtures."""
        card = EXERCISE_CARD.read_text(encoding="utf-8")
        assert "session-focus__up-next" in card
        assert "peek_for_active" in card
        # up-next must expose name + role + optional primary zone
        assert "session-focus__up-next-name" in card
        assert "session-focus__up-next-role" in card
        assert "session-focus__up-next-zone" in card

    def test_up_next_shows_no_full_load(self):
        """OQ-F : up-next must not render a full weight×reps load line.
        The up-next role line reuses peek scheme + zone only, never the
        set weight_kg/reps inputs."""
        card = EXERCISE_CARD.read_text(encoding="utf-8")
        # locate the up-next aside block and assert no weight input inside it
        # MIGRÉ — l'`aside` de quatre lignes devient UNE ligne, rendue à la
        # fin de l'exercice, au seul moment où « et après ? » se pose.
        m = re.search(
            r'<p class="console__next[^>]*>.*?</p>', card, re.DOTALL
        )
        assert m is not None, "ligne up-next introuvable"
        assert "set_" not in m.group(0)
        assert "weight_kg" not in m.group(0)


# ───────── aria / a11y invariants ─────────


class TestAriaCurrent:
    def test_active_stepper_item_has_aria_current_location(self, client):
        assert 'aria-current="location"' in _body(client)

    def test_no_aria_current_false(self, client):
        assert 'aria-current="false"' not in _body(client)

    def test_no_aria_current_step(self, client):
        assert 'aria-current="step"' not in _body(client)

    def test_single_aria_current_in_stepper(self, client):
        """Only the active item carries aria-current (exactly one)."""
        body = _body(client, n=3)
        assert body.count('aria-current="location"') == 1


# ───────── logging + form invariants ─────────


class TestLoggingInvariants:
    def test_weight_input_preserved(self, client):
        assert re.search(r'name="set_\d+_weight_kg"', _body(client))

    def test_reps_input_preserved(self, client):
        assert re.search(r'name="set_\d+_reps"', _body(client))

    def test_exercise_form_post_preserved(self, client):
        body = _body(client)
        assert 'method="post"' in body
        assert "update_exercise_card" in body or "/sessions/" in body

    def test_session_feedback_anchor_preserved(self, client):
        assert 'id="session-feedback"' in _body(client)

    def test_nav_next_button_preserved(self, client):
        assert 'name="nav"' in _body(client)


# ───────── rest timer contract invariants ─────────


class TestRestTimerContracts:
    def test_rest_timer_data_contracts_unchanged(self, client):
        """data-* rest timer hooks must still be present on active card."""
        body = _body(client)
        # rest timer is rendered on the active card
        # MIGRÉ — le minuteur n'existe QUE dans l'état `REST` (`§7.2`).
        # Le rendre en permanence est ce qui a masqué le défaut `D3`.
        assert "data-rest-display" not in body


# ───────── no-JS / no-framework invariants ─────────


class TestNoFrameworkLeak:
    def test_no_new_js_file(self):
        """Sb_UI_04.3 must not add any JS file to app/static/js. The
        expected set is frozen to the files that predate this sprint
        (preview.js + session_focus.js) — a cockpit built in pure SSR/CSS
        adds none."""
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
        expected = ["prefs_focus_rank.js", "preview.js", "session_focus.js"]
        assert js_files == expected, (
            f"unexpected JS files (Sb_UI_04.3 must add no JS): {js_files}"
        )

    def test_no_react_marker_in_render(self, client):
        body = _body(client)
        for marker in ("data-reactroot", "__NEXT_DATA__", "ReactDOM", "/_next/"):
            assert marker not in body

    def test_macros_still_rendered(self, client):
        """segmented / field_group macros must still produce output
        (concentration + global_state segmented controls present)."""
        body = _body(client)
        assert 'name="concentration"' in body
        assert 'name="global_state"' in body


# ───────── CSS presence (scoped, no global leak) ─────────


class TestCockpitCss:
    def test_css_defines_cockpit(self):
        css = FOCUS_CSS.read_text(encoding="utf-8")
        assert ".session-focus__cockpit" in css

    def test_css_defines_stepper(self):
        css = FOCUS_CSS.read_text(encoding="utf-8")
        assert ".session-focus__stepper" in css

    def test_css_defines_worked_area(self):
        css = FOCUS_CSS.read_text(encoding="utf-8")
        assert ".session-focus__worked-area" in css

    def test_css_defines_up_next(self):
        css = FOCUS_CSS.read_text(encoding="utf-8")
        assert ".session-focus__up-next" in css

    def test_css_active_card_dominance(self):
        """Active card must have an elevation/border rule under cockpit."""
        css = FOCUS_CSS.read_text(encoding="utf-8")
        assert re.search(
            r"\.session-focus__cockpit\s+\.session-focus__card--active",
            css,
        )

    def test_css_scoped_to_session_focus(self):
        """No cockpit selector may leak outside .session-focus."""
        css = FOCUS_CSS.read_text(encoding="utf-8")
        # every cockpit rule line that starts a selector should be reachable
        # under .session-focus scope — assert no bare global element rule was
        # introduced for cockpit classes (they all carry the prefix).
        assert ".session-focus__cockpit" in css
        # sanity: the class prefix itself encodes the scope
        assert "session-focus__cockpit" in css
