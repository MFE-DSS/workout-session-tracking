"""Sb_29.5 — Sx_29 accessibility consolidation tests.

Re-asserts a11y contracts established across Sb_29.1 → Sb_29.4 :
- Tap targets 44x44 (WCAG 2.5.5)
- aria-current="location" on active jump bar item (Sb_UI_04.2 : replaces "step")
- aria-live="polite" on rest timer
- skip rest button = type="button" (non critical, non-submitting)
- primary CTAs are type="submit" (form-based POST)
- non-color cues for partial / done / skipped / substituted (WCAG 1.4.1)
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP_CSS = ROOT / "app" / "static" / "css" / "app.css"
FOCUS_CSS = ROOT / "app" / "static" / "css" / "session_focus.css"


def _css() -> str:
    return APP_CSS.read_text(encoding="utf-8") + "\n" + FOCUS_CSS.read_text(
        encoding="utf-8"
    )


def _seed(db, user_id, n_exercises=3):
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    s = WorkoutSession(
        user_id=user_id,
        template_slug_snapshot="a11y",
        template_name_snapshot="A11y test",
        started_at=datetime.now(UTC),
        status="in_progress",
    )
    for i in range(n_exercises):
        se = SessionExercise(
            exercise_code_snapshot=f"A{i + 1}",
            exercise_name_snapshot=f"Exercise {i + 1}",
            position=i + 1,
        )
        se.set_logs.append(
            SetLog(kind="work", set_index=1, weight_kg=80.0, reps=8, completed=False)
        )
        s.session_exercises.append(se)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def _render(client, session_id) -> str:
    r = client.get(f"/sessions/{session_id}", follow_redirects=False)
    assert r.status_code == 200, r.text[:400]
    return r.text


# ───────── tap targets 44x44 ─────────


def test_tap_target_min_height_44():
    css = _css()
    assert "min-height: 44px" in css or "min-height:44px" in css


def test_tap_target_min_width_44():
    css = _css()
    assert "min-width: 44px" in css or "min-width:44px" in css


def test_session_focus_tap_target_class_applied(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed(db, user.id)
        session_id = session.id

    body = _render(client, session_id)
    assert "session-focus__tap-target" in body


# ───────── aria-current step + aria-live ─────────


def test_aria_current_step_on_active_jump_item(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed(db, user.id)
        session_id = session.id

    body = _render(client, session_id)
    # Sb_UI_04.2 — aria-current="location" (was "step" pre-Sb_UI_04.2).
    pattern = re.compile(
        r'<a\b[^>]*\bex-jump__item--active\b[^>]*\baria-current="location"',
        re.IGNORECASE,
    )
    assert pattern.search(body), "active jump item missing aria-current=location"


def _rest_body(client, session_id) -> str:
    """La page dans l'état `REST` — le seul où le minuteur existe.

    `REST` se dérive d'un signal serveur ET d'une série de travail restante :
    les échauffements doivent donc être terminés, sinon l'état courant est
    `WARMUP` et le repos n'a rien à annoncer.
    """
    from app.database import SessionLocal
    from app.models.session import SessionExercise, WorkoutSession
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    with SessionLocal() as db:
        sess = db.execute(
            select(WorkoutSession)
            .where(WorkoutSession.id == session_id)
            .options(selectinload(WorkoutSession.session_exercises)
                     .selectinload(SessionExercise.set_logs))
        ).scalar_one()
        for se in sess.session_exercises:
            for sl in se.set_logs:
                if sl.kind == "warmup":
                    sl.completed, sl.weight_kg, sl.reps = True, 40.0, 12
        db.commit()
        # `REST` exige aussi qu'une série de travail soit DÉJÀ validée et
        # qu'il en reste une : sinon il n'y a pas de repos à annoncer.
        sess2 = db.execute(
            select(WorkoutSession)
            .where(WorkoutSession.id == session_id)
            .options(selectinload(WorkoutSession.session_exercises)
                     .selectinload(SessionExercise.set_logs))
        ).scalar_one()
        for se in sess2.session_exercises:
            work = sorted((sl for sl in se.set_logs if sl.kind == "work"),
                          key=lambda sl: sl.set_index)
            if len(work) >= 2:
                work[0].completed, work[0].weight_kg, work[0].reps = True, 60.0, 10
        db.commit()
    r = client.get(f"/sessions/{session_id}?rest=1")
    assert r.status_code == 200, r.text[:300]
    assert "rest-readout" in r.text, "l'état REST n'est pas atteint"
    return r.text


def test_rest_timer_has_aria_live_polite(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed(db, user.id)
        session_id = session.id

    # MIGRÉ — le minuteur n'existe QUE dans l'état `REST` (`§7.2`), ce qui est exactement la correction du défaut `D3`. Les gardes de repos conduisent donc la séance jusqu'à cet état.
    body = _rest_body(client, session_id)
    pattern = re.compile(
        r'<div\b[^>]*\bclass="[^"]*rest-readout[^"]*"[^>]*\baria-live="polite"',
        re.IGNORECASE | re.DOTALL,
    )
    assert pattern.search(body), "le RestReadout n'annonce pas aria-live=polite"


# ───────── button types (no-JS contract) ─────────


def test_skip_rest_is_type_button(client):
    """**Migré, et le contrat change.** « Skip rest » — anglais,
    `type="button"`, sans effet serveur — devient `PASSER LE REPOS`, la
    commande DOMINANTE de l'état `REST`, et un LIEN : soumettre marquerait
    « complétée » une série à peine commencée, puisque `completed` dérive de
    la présence d'une valeur.

    Les seuls boutons restants dans le repos sont les ±15 s, toujours
    non critiques et toujours `type="button"`.
    """
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed(db, user.id)
        session_id = session.id

    body = _rest_body(client, session_id)
    assert "PASSER LE REPOS" in body
    assert "Skip rest" not in body, "l'anglais a quitté l'interface"
    flat = " ".join(body.split())
    m = re.search(r"<button[^>]*data-rest-step[^>]*>", flat)
    assert m is not None, (
        "les ajustements ±15 s ne sont pas rendus — "
        f"data-rest-step présent ? {'data-rest-step' in flat}"
    )
    assert 'type="button"' in m.group(0), (
        "un ajustement de repos n'est jamais critique : jamais un submit"
    )


def test_primary_cta_is_type_submit(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed(db, user.id)
        session_id = session.id

    body = _render(client, session_id)
    m = re.search(
        r'<button\b[^>]*\bsession-focus__cta-primary\b[^>]*>',
        body,
        re.IGNORECASE,
    )
    assert m is not None
    assert 'type="submit"' in m.group(0), "primary CTA must remain type=submit"


# ───────── non-color cues (WCAG 1.4.1) ─────────


def test_non_color_cues_for_card_states():
    """Each non-default card state must expose a non-color cue (border-left,
    text-decoration, or ::before/::after content)."""
    css = _css()
    # partial: border-left
    assert re.search(
        r"\.session-focus__card--partial\b[^{]*\{[^}]*border-left",
        css,
        re.DOTALL,
    ), "partial state missing border-left cue"
    # done: border-left + checkmark (\2713)
    assert re.search(
        r"\.session-focus__card--done\b[^{]*\{[^}]*border-left",
        css,
        re.DOTALL,
    ), "done state missing border-left cue"
    assert "\\2713" in css, "done state missing non-color checkmark cue"
    # skipped: dashed border + line-through
    assert re.search(
        r"\.session-focus__card--skipped\b[^{]*\{[^}]*border-left:\s*\d+px\s+dashed",
        css,
        re.DOTALL,
    ), "skipped state missing dashed border cue"
    assert "line-through" in css, "skipped state missing line-through cue"
    # substituted: dotted border + arrow (\2194)
    assert re.search(
        r"\.session-focus__card--substituted\b[^{]*\{[^}]*border-left:\s*\d+px\s+dotted",
        css,
        re.DOTALL,
    ), "substituted state missing dotted border cue"
    assert "\\2194" in css, "substituted state missing arrow cue"


def test_active_state_has_non_color_cue():
    """Active card must expose a non-color cue (bullet ::before on code)."""
    css = _css()
    pattern = re.compile(
        r"\.session-focus__card--active\s*>\s*summary\s+\.exercise-card__code::before",
        re.DOTALL,
    )
    assert pattern.search(css), "active state missing ::before cue on code"
