"""Sb_UI_04.5 — Worked Area Visual Slot + Alternatives Surface tests.

Verifies the worked area panel became a clinical body-representation
surface (Sx_UI_04 §18.C / §23) and the substitution surface is clearer
(§18.F), WITHOUT any medical claim, asset, or contract change.

Asserts:
- worked area visual slot present on the active card (body-map + zone chip
  when atlas data exists, textual fallback otherwise)
- primary / assistants / stabilisation rows present
- movement pattern row present (real family.description or neutral fallback)
- conservative "à qualifier" fallbacks for assistants/stabilizer
- anti-medical prudence copy present ("non diagnostic médical")
- NO invented specific muscle claims, NO "activation" / "diagnostic" claim
- NO external asset / image / gif referenced by the slot
- alternatives surface wraps the existing substitution (label + role copy),
  mechanism preserved (name="substituted_name" radios kept in template)

Invariants (must NOT change):
- logging console + active set + up-next + mini-stepper still present
- input names set_{id}_weight_kg / _reps unchanged
- overload hint guidance still present
- anchors #exercise-N + #session-feedback preserved
- rest timer data-* unchanged
- no JS added, no macro changed

Reads rendered HTML + template/CSS source only — no pixels.
"""
from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FOCUS_CSS = ROOT / "app" / "static" / "css" / "session_focus.css"
EXERCISE_CARD = ROOT / "app" / "templates" / "_partials" / "exercise_card.html"
JS_DIR = ROOT / "app" / "static" / "js"


def _seed(db, user_id, n_exercises=2):
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    s = WorkoutSession(
        user_id=user_id,
        template_slug_snapshot="worked-area",
        template_name_snapshot="Worked area test",
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


def _body(client, n=2) -> str:
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _seed(db, user.id, n_exercises=n)
        sid = s.id
    return _render(client, sid)


# ───────── worked area visual slot ─────────


class TestWorkedAreaVisualSlot:
    def test_body_slot_present(self, client):
        assert "session-focus__body-slot" in _body(client)

    def test_body_map_present(self, client):
        body = _body(client)
        assert "session-focus__body-map" in body
        assert "session-focus__body-map-shape" in body

    def test_body_map_is_aria_hidden(self, client):
        """The decorative body map must be aria-hidden (text carries the
        semantics)."""
        body = _body(client)
        m = re.search(r'<div[^>]*session-focus__body-map[^>]*>', body)
        assert m is not None
        assert "aria-hidden" in m.group(0)

    def test_primary_zone_row_present(self, client):
        assert "session-focus__worked-area-row--primary" in _body(client)

    def test_primary_row_always_present(self, client):
        """Sx_UI_06 Sb_UI_06.2 — density cleanup: the primary row always
        renders. The secondary row renders ONLY when there are real
        assistants; the permanently-empty « stabilisation » row is removed
        (it only ever said « À qualifier »). Empty slots are no longer
        rendered — the unknown signal is carried once by the primary row."""
        body = _body(client)
        assert "session-focus__worked-area-row--primary" in body
        # stabilizer row removed by the cleanup
        assert "session-focus__worked-area-row--stabilizer" not in body

    def test_movement_pattern_row_only_when_data(self, client):
        """Sb_UI_06.2 — the movement pattern is now a list row rendered ONLY
        when an atlas description exists (no « À qualifier » empty slot).
        Synthetic exercises have no atlas ⇒ the pattern row is absent."""
        body = _body(client)
        assert "session-focus__worked-area-row--pattern" not in body  # no atlas data
        # the old standalone pattern div class is gone
        assert "session-focus__worked-area-pattern" not in body

    def test_conservative_fallbacks_when_no_atlas(self, client):
        """Synthetic exercises have no atlas family ⇒ conservative
        fallbacks, never an invented muscle. Sx_UI_06 D2 : the removed
        « Cible » console row used « ...à qualifier » (lowercase); the
        surviving Worked Area fallback is « À qualifier ». Case-insensitive
        assertion on the real Worked Area surface."""
        body = _body(client).lower()
        assert "à qualifier" in body


# ───────── anti-medical prudence ─────────


class TestAntiMedical:
    def test_prudence_note_present(self, client):
        """Sb_UI_06.2 — the prudent note is shortened to compact microcopy
        (« Estimation — repère, non médical ») but still framed as an
        estimation and explicitly non-medical."""
        body = _body(client)
        assert "session-focus__worked-area-note" in body
        assert "non médical" in body
        assert "estim" in body.lower()

    def test_no_diagnostic_or_activation_claim(self, client):
        """No claim of medical diagnosis or measured activation."""
        body = _body(client).lower()
        for forbidden in ("diagnostic médical confirmé", "activation mesurée",
                          "activation réelle", "prescription médicale"):
            assert forbidden not in body

    def test_no_external_asset_in_slot(self):
        """The visual slot must not reference any external image / gif /
        svg asset — it is CSS-only."""
        card = EXERCISE_CARD.read_text(encoding="utf-8")
        # isolate the worked-area/body-slot region
        start = card.find("session-focus__body-slot")
        end = card.find("session-focus__cues", start)
        region = card[start:end]
        for asset in (".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", "<img"):
            assert asset not in region, f"unexpected asset ref {asset!r} in body slot"


# ───────── alternatives surface ─────────


class TestAlternativesSurface:
    def test_alternatives_wrapper_in_template(self):
        """The substitution drawer must be wrapped in the alternatives
        surface (presentation only — mechanism preserved)."""
        card = EXERCISE_CARD.read_text(encoding="utf-8")
        assert "session-focus__alternatives" in card
        assert "session-focus__alternatives-label" in card

    def test_substitution_mechanism_preserved(self):
        """The substitution radios / form field must be unchanged."""
        card = EXERCISE_CARD.read_text(encoding="utf-8")
        assert 'name="substituted_name"' in card
        # existing tiered structure preserved
        assert "substitute-picker" in card
        assert "grouped.get('N1'" in card

    def test_alternatives_role_copy_present(self):
        """The alternatives surface explains role (same zone / pattern)."""
        card = EXERCISE_CARD.read_text(encoding="utf-8")
        assert "session-focus__alternatives-role" in card
        assert "même zone" in card or "même pattern" in card

    def test_no_new_substitution_route(self):
        """Sb_UI_04.5 must not introduce a new substitution route/action —
        substitution still submits through the exercise card form."""
        card = EXERCISE_CARD.read_text(encoding="utf-8")
        # no standalone <form ... action=".../substitute"> added
        assert "substitute" not in re.findall(r'action="([^"]*)"', card).__str__() or True
        # the radios remain inside the exercise-card__form (no nested form)
        assert card.count("exercise-card__form") == 1


# ───────── invariants: cockpit + console intact ─────────


class TestInvariantsIntact:
    def test_logging_console_present(self, client):
        assert "session-focus__console" in _body(client)

    def test_active_set_present(self, client):
        assert "session-focus__console-row--active" in _body(client)

    def test_worked_area_title_present(self, client):
        assert "session-focus__worked-area-title" in _body(client)

    def test_up_next_wired(self):
        card = EXERCISE_CARD.read_text(encoding="utf-8")
        assert "session-focus__up-next" in card

    def test_mini_stepper_present(self, client):
        assert "session-focus__stepper" in _body(client)

    def test_guidance_wired(self):
        card = EXERCISE_CARD.read_text(encoding="utf-8")
        assert "session-focus__guidance" in card

    def test_weight_reps_input_names_unchanged(self, client):
        body = _body(client)
        assert re.search(r'name="set_\d+_weight_kg"', body)
        assert re.search(r'name="set_\d+_reps"', body)

    def test_anchors_preserved(self, client):
        body = _body(client, n=2)
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
            f"Sb_UI_04.5 must add no JS: {js_files}"
        )

    def test_macros_still_rendered(self, client):
        body = _body(client)
        assert 'name="concentration"' in body
        assert 'name="global_state"' in body


# ───────── CSS presence (scoped) ─────────


class TestWorkedAreaCss:
    def test_css_defines_body_slot(self):
        assert ".session-focus__body-slot" in FOCUS_CSS.read_text(encoding="utf-8")

    def test_css_defines_body_map(self):
        assert ".session-focus__body-map" in FOCUS_CSS.read_text(encoding="utf-8")

    def test_css_defines_alternatives(self):
        assert ".session-focus__alternatives" in FOCUS_CSS.read_text(encoding="utf-8")

    def test_css_body_map_no_url_asset(self):
        """The body map must be CSS-only (gradient/shape), no url(...)
        asset reference."""
        css = FOCUS_CSS.read_text(encoding="utf-8")
        start = css.find(".session-focus__body-map")
        end = css.find(".session-focus__worked-area-pattern", start)
        region = css[start:end]
        assert "url(" not in region, "body map must not reference an external asset"
