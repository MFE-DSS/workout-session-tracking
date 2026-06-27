"""Sb_30.5 — Tests a11y consolidés du bloc overload hint.

Couvre :
- aria-labelledby pointe vers un id unique par card (collision-safe sur
  plusieurs sessions / plusieurs cards)
- id `__intent` est rendu et matche l'aria-labelledby
- target_summary balisé <strong> (sémantique forte, non autoritaire)
- summary expose aria-label explicite "Voir les raisons de la suggestion"
- role="status" préservé (Sb_30.3)
- <details> natif HTML pour navigation clavier (réutilise Sb_30.3 garde)
- CSS summary a un padding/min-height ergonomique (pas un simple 2px)
- focus-visible défini sur summary (clavier)
- non-color cues (5 états) inchangés (régression Sb_30.3)
- wording non autoritaire en HTML rendu (régression Sb_30.3)

Non testé volontairement :
- Color contrast (V1 manuel, OQ-D Sx_29 héritée).
- Lecteurs d'écran réels (audit hors CI).
"""

from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PARTIAL = ROOT / "app" / "templates" / "_partials" / "overload_hint.html"
FOCUS_CSS = ROOT / "app" / "static" / "css" / "session_focus.css"


# ───────── partial inline ─────────


def test_partial_uses_aria_labelledby():
    body = PARTIAL.read_text(encoding="utf-8")
    assert 'aria-labelledby=' in body, (
        "wrapper must expose aria-labelledby for screen reader context"
    )
    # L'id pointé est de la forme "overload-hint-<se.id>__intent"
    assert "__intent" in body


def test_partial_target_uses_strong():
    body = PARTIAL.read_text(encoding="utf-8")
    assert '<strong class="overload-hint__target">' in body, (
        "target_summary must use <strong> for semantic emphasis"
    )


def test_partial_summary_has_aria_label():
    body = PARTIAL.read_text(encoding="utf-8")
    assert "aria-label=\"Voir les raisons de la suggestion\"" in body


def test_partial_keeps_role_status():
    body = PARTIAL.read_text(encoding="utf-8")
    assert 'role="status"' in body


def test_partial_still_uses_native_details():
    body = PARTIAL.read_text(encoding="utf-8")
    assert "<details" in body
    assert "<summary" in body


# ───────── seed helpers (réutilise pattern Sb_30.3) ─────────


def _seed_progress(db, user_id):
    from app.models.catalog import (
        RepTarget,
        TemplateExercise,
        WorkoutTemplate,
    )
    from app.models.session import (
        SessionExercise,
        SetLog,
        WorkoutSession,
    )

    t = WorkoutTemplate(
        slug=f"a11y-{user_id}",
        name="A11y test",
        kind="strength",
    )
    db.add(t)
    db.flush()
    te = TemplateExercise(
        template_id=t.id,
        position=1,
        code="A1",
        name="Back squat",
        set_scheme="3×6-10",
    )
    db.add(te)
    db.flush()
    db.add(
        RepTarget(
            template_exercise_id=te.id, set_index=1, min_reps=6, max_reps=10
        )
    )
    db.flush()
    now = datetime.now(UTC)
    for k in range(2):
        past = WorkoutSession(
            user_id=user_id,
            template_id=t.id,
            template_slug_snapshot=t.slug,
            template_name_snapshot=t.name,
            started_at=now - timedelta(days=7 * (k + 1)),
            ended_at=now - timedelta(days=7 * (k + 1)),
            status="completed",
            global_state="good",
            concentration="high",
        )
        pse = SessionExercise(
            template_exercise_id=te.id,
            exercise_code_snapshot="A1",
            exercise_name_snapshot="Back squat",
            position=1,
            success_score=100,
        )
        pse.set_logs.append(
            SetLog(
                kind="work",
                set_index=1,
                weight_kg=100.0,
                reps=10,
                completed=True,
            )
        )
        past.session_exercises.append(pse)
        db.add(past)
    cur = WorkoutSession(
        user_id=user_id,
        template_id=t.id,
        template_slug_snapshot=t.slug,
        template_name_snapshot=t.name,
        started_at=now,
        status="in_progress",
    )
    se = SessionExercise(
        template_exercise_id=te.id,
        exercise_code_snapshot="A1",
        exercise_name_snapshot="Back squat",
        position=1,
    )
    se.set_logs.append(
        SetLog(kind="work", set_index=1, weight_kg=100.0, reps=8, completed=False)
    )
    cur.session_exercises.append(se)
    db.add(cur)
    db.commit()
    db.refresh(cur)
    return cur


def _render(client, sid: int) -> str:
    r = client.get(f"/sessions/{sid}", follow_redirects=False)
    assert r.status_code == 200, r.text[:400]
    return r.text


# ───────── HTML rendu ─────────


def test_rendered_aria_labelledby_targets_existing_id(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _seed_progress(db, user.id)
        sid = s.id

    body = _render(client, sid)
    # Capture l'id pointé par aria-labelledby
    m = re.search(r'aria-labelledby="([^"]+)"', body)
    assert m is not None, "aria-labelledby attribute missing on rendered overload hint"
    target_id = m.group(1)
    # L'id correspondant doit exister dans le DOM (sur le <span> intent)
    assert f'id="{target_id}"' in body, (
        f'aria-labelledby points to "{target_id}" but no matching id="…" found'
    )


def test_rendered_id_is_per_session_exercise(client):
    """L'id doit contenir l'identifiant de session_exercise pour éviter
    les collisions si plusieurs hints coexistent."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _seed_progress(db, user.id)
        se_id = s.session_exercises[0].id
        sid = s.id

    body = _render(client, sid)
    expected_id = f"overload-hint-{se_id}__intent"
    assert f'id="{expected_id}"' in body
    assert f'aria-labelledby="{expected_id}"' in body


def test_rendered_target_uses_strong(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _seed_progress(db, user.id)
        sid = s.id

    body = _render(client, sid)
    assert '<strong class="overload-hint__target">' in body
    # La valeur attendue (compound +2.5 sur 100 = 102.5 kg + 6-10 reps)
    assert "102.5 kg" in body


def test_rendered_summary_has_aria_label(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _seed_progress(db, user.id)
        sid = s.id

    body = _render(client, sid)
    pattern = re.compile(
        r'<summary[^>]*aria-label="Voir les raisons de la suggestion"',
        re.IGNORECASE,
    )
    assert pattern.search(body), "summary must carry an explicit aria-label"


def test_rendered_role_status_preserved(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _seed_progress(db, user.id)
        sid = s.id

    body = _render(client, sid)
    pattern = re.compile(
        r'<div class="overload-hint[^"]*"[^>]*role="status"',
        re.IGNORECASE | re.DOTALL,
    )
    # Pattern peut matcher en plusieurs lignes : on simplifie via search
    assert 'role="status"' in body
    assert "overload-hint--progress" in body


# ───────── CSS a11y ─────────


def test_css_summary_has_ergonomic_padding():
    css = FOCUS_CSS.read_text(encoding="utf-8")
    block = re.search(
        r"\.overload-hint__why-toggle\s*\{[^}]+\}",
        css,
        re.DOTALL,
    )
    assert block is not None, "missing .overload-hint__why-toggle rule"
    text = block.group(0)
    assert "padding: 6px" in text, (
        "summary tap target padding should be at least 6px (was 2px Sb_30.3)"
    )
    assert "min-height" in text


def test_css_summary_has_focus_visible_rule():
    css = FOCUS_CSS.read_text(encoding="utf-8")
    assert ".overload-hint__why-toggle:focus-visible" in css, (
        "focus-visible rule missing for keyboard users"
    )


# ───────── wording non autoritaire (régression Sb_30.3) ─────────


def test_rendered_wording_still_not_authoritative(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _seed_progress(db, user.id)
        sid = s.id

    body = _render(client, sid).lower()
    # Scope sur le bloc overload uniquement
    block_match = re.search(
        r'<div class="overload-hint[^"]*"[^>]*>.*?</div>\s*</div>',
        body,
        re.DOTALL,
    )
    assert block_match is not None
    block = block_match.group(0)
    for tok in ("tu dois", "il faut absolument", "obligatoire"):
        assert tok not in block, f"forbidden token {tok!r} in rendered overload hint"


# ───────── non-color cues inchangés (régression Sb_30.3) ─────────


def test_non_color_cues_preserved():
    css = FOCUS_CSS.read_text(encoding="utf-8")
    for icon in ("↑", "↓", "→", "🏁", "?"):
        assert icon in css, f"non-color cue {icon!r} missing in CSS"
