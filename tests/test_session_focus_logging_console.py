"""Sb_UI_04.4 — Set Logging Console + Progression Guidance tests.

Verifies the set-logging surface is now an *execution console* (Sx_UI_04
§18.E / §22), not a plain form of rows.

Asserts:
- console container present on the active card
- console header + work-set progression (done / total)
- reference (previous performance) + target surfaces render, with
  conservative fallbacks when data is absent (never invented, never
  guilt-inducing)
- work-set rows carry a presentation state (completed / active / upcoming)
- exactly one active set (first uncompleted work set) on the active card
- completed sets show a check ledger marker
- progression guidance wraps the overload hint (presentation only)

Invariants (must NOT change):
- input names set_{id}_weight_kg / set_{id}_reps unchanged
- form action / method unchanged
- anchors #exercise-N + #session-feedback preserved
- rest timer data-* contracts unchanged
- worked area panel / up-next / mini-stepper still present
- no JS added, no macro changed, no forbidden zone touched

Reads rendered HTML + template/CSS source only — no pixels.
"""
from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FOCUS_CSS = ROOT / "app" / "static" / "css" / "session_focus.css"
EXERCISE_CARD = ROOT / "app" / "templates" / "_partials" / "exercise_card.html"
OVERLOAD_HINT = ROOT / "app" / "templates" / "_partials" / "overload_hint.html"
JS_DIR = ROOT / "app" / "static" / "js"


# ───────── seed helpers ─────────


def _seed_partial(db, user_id, n_exercises=2, sets_per=3, first_done=True):
    """In-progress session with N exercises. On the first (active) exercise,
    the first work set is completed (weight+reps) and the rest are empty ⇒
    exercises the completed/active/upcoming split."""
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    s = WorkoutSession(
        user_id=user_id,
        template_slug_snapshot="console",
        template_name_snapshot="Console test",
        started_at=datetime.now(UTC),
        status="in_progress",
    )
    for i in range(n_exercises):
        se = SessionExercise(
            exercise_code_snapshot=f"E{i + 1}",
            exercise_name_snapshot=f"Exercise {i + 1}",
            position=i + 1,
        )
        for j in range(sets_per):
            done = first_done and i == 0 and j == 0
            se.set_logs.append(
                SetLog(
                    kind="work",
                    set_index=j + 1,
                    weight_kg=80.0 if done else None,
                    reps=8 if done else None,
                    completed=done,
                )
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


def _body(client, **kw) -> str:
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _seed_partial(db, user.id, **kw)
        sid = s.id
    return _render(client, sid)


# ───────── console structure ─────────


class TestConsoleStructure:
    def test_console_present(self, client):
        assert "session-focus__console" in _body(client)

    def test_console_head_and_progress(self, client):
        body = _body(client)
        assert "session-focus__console-head" in body
        assert "session-focus__console-progress" in body

    def test_console_progress_counts_done_over_total(self, client):
        """First exercise has 1/3 work sets done."""
        body = _body(client, sets_per=3, first_done=True)
        assert re.search(
            r'session-focus__console-progress-value[^>]*>\s*1\s*/\s*3\s*<', body
        )

    def test_console_list_present(self, client):
        assert "session-focus__console-list" in _body(client)


# ───────── set states ─────────


class TestSetStates:
    def test_active_set_present(self, client):
        assert "session-focus__console-row--active" in _body(client)

    def test_completed_set_present(self, client):
        body = _body(client, first_done=True)
        assert "session-focus__console-row--completed" in body

    def test_upcoming_set_present(self, client):
        body = _body(client, sets_per=3, first_done=True)
        assert "session-focus__console-row--upcoming" in body

    def test_exactly_one_active_set_on_active_card(self, client):
        """Only the first uncompleted work set of the active card is active.
        With 2 exercises we count active rows only inside the first (open)
        card region."""
        body = _body(client, n_exercises=2, sets_per=3, first_done=True)
        # active card is the first <details open> exercise card; count the
        # active console rows globally — only the active card renders the
        # active-set badge, and only one set per active card is active.
        assert body.count("session-focus__console-badge") == 1

    def test_completed_set_has_check(self, client):
        body = _body(client, first_done=True)
        assert "session-focus__console-check" in body


# ───────── reference + target ─────────


class TestReferenceAndTarget:
    def test_reference_surface_present(self, client):
        body = _body(client)
        assert "session-focus__console-ref--prev" in body

    def test_target_lives_in_input_placeholder_not_console_row(self, client):
        """Sx_UI_06 D2 — the target suggestion no longer has its own console
        « Cible » row (de-densification). It lives ONLY as the input
        placeholder, closest to the action. The redundant row is gone."""
        body = _body(client)
        # The dedicated console target row is removed…
        assert "session-focus__console-ref--target" not in body
        # …and the input still carries a placeholder (kg / reps or a suggestion).
        assert 'placeholder="kg"' in body or 'placeholder=' in body

    def test_reference_fallback_when_no_data(self, client):
        """Synthetic exercises have no prior session ⇒ conservative
        fallback 'Non disponible', never an invented performance."""
        body = _body(client)
        assert "Non disponible" in body

    def test_target_console_row_removed(self, client):
        """Sx_UI_06 D2 — the « Cible » console row (and its « Objectif à
        qualifier » fallback) is removed; the reference-previous row stays."""
        body = _body(client)
        assert "Objectif à qualifier" not in body
        assert "session-focus__console-ref--prev" in body


# ───────── progression guidance ─────────


class TestProgressionGuidance:
    def test_guidance_wrapper_in_template(self):
        """The overload hint is presented inside a guidance wrapper
        (presentation only — the partial itself is untouched)."""
        card = EXERCISE_CARD.read_text(encoding="utf-8")
        assert "session-focus__guidance" in card
        assert 'include "_partials/overload_hint.html"' in card

    def test_overload_hint_partial_untouched(self):
        """overload_hint.html must remain the Sb_30.x metier partial —
        no coaching/imperative rewrite. Sanity: role=status + engine
        version still present."""
        hint = OVERLOAD_HINT.read_text(encoding="utf-8")
        assert 'role="status"' in hint
        assert "engine_version" in hint
        assert "is_silent" in hint


# ───────── logging invariants ─────────


class TestLoggingInvariants:
    def test_weight_input_name_unchanged(self, client):
        assert re.search(r'name="set_\d+_weight_kg"', _body(client))

    def test_reps_input_name_unchanged(self, client):
        assert re.search(r'name="set_\d+_reps"', _body(client))

    def test_no_renamed_logging_fields(self, client):
        """No new/renamed logging input names introduced."""
        body = _body(client)
        # the only set inputs must be _weight_kg / _reps
        names = set(re.findall(r'name="(set_\d+_[a-z_]+)"', body))
        for n in names:
            assert n.endswith("_weight_kg") or n.endswith("_reps"), (
                f"unexpected logging input name: {n}"
            )

    def test_form_action_method_preserved(self, client):
        """The exercise card form must still POST to the exercise-card
        endpoint (/sessions/{id}/exercises/{ex_id}) — action/method
        unchanged by the console refactor."""
        body = _body(client)
        assert 'method="post"' in body
        assert 'class="exercise-card__form"' in body
        assert re.search(r'action="[^"]*/sessions/\d+/exercises/\d+"', body)

    def test_completed_derivation_no_checkbox(self, client):
        """Sb_24.4 contract: completed derived server-side, no checkbox."""
        body = _body(client)
        assert 'type="checkbox"' not in body or "completed" not in re.findall(
            r'type="checkbox"[^>]*name="([^"]*)"', body
        )


# ───────── cockpit surfaces still present ─────────


class TestCockpitStillIntact:
    def test_worked_area_still_present(self, client):
        assert "session-focus__worked-area" in _body(client)

    def test_up_next_wired_in_template(self):
        card = EXERCISE_CARD.read_text(encoding="utf-8")
        assert "session-focus__up-next" in card

    def test_mini_stepper_still_present(self, client):
        assert "session-focus__stepper" in _body(client)

    def test_anchors_preserved(self, client):
        body = _body(client, n_exercises=2)
        assert len(re.findall(r'href="#exercise-\d+"', body)) >= 2

    def test_session_feedback_preserved(self, client):
        assert 'id="session-feedback"' in _body(client)

    def test_rest_timer_contracts_preserved(self, client):
        body = _body(client)
        assert "data-rest-display" in body or "session-focus__rest-timer" in body


# ───────── no framework leak ─────────


class TestNoFrameworkLeak:
    def test_no_new_js_file(self):
        js_files = sorted(p.name for p in JS_DIR.glob("*.js"))
        assert js_files == ["preview.js", "session_focus.js"], (
            f"Sb_UI_04.4 must add no JS: {js_files}"
        )

    def test_macros_still_rendered(self, client):
        body = _body(client)
        assert 'name="concentration"' in body
        assert 'name="global_state"' in body


# ───────── CSS presence ─────────


class TestConsoleCss:
    def test_css_defines_console(self):
        assert ".session-focus__console" in FOCUS_CSS.read_text(encoding="utf-8")

    def test_css_defines_active_set_dominance(self):
        css = FOCUS_CSS.read_text(encoding="utf-8")
        assert ".session-focus__console-row--active" in css

    def test_css_defines_completed_ledger(self):
        css = FOCUS_CSS.read_text(encoding="utf-8")
        assert ".session-focus__console-row--completed" in css

    def test_css_defines_guidance(self):
        css = FOCUS_CSS.read_text(encoding="utf-8")
        assert ".session-focus__guidance" in css
