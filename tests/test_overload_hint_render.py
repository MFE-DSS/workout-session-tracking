"""Sb_30.3 — Overload hint UI first render tests.

Couvre :
- rendu visible quand hint présent sur la carte active
- absence de rendu quand silent / unknown (router skip + partial guard)
- présence UNIQUEMENT sur la carte active (jamais sur autres cards)
- wording non autoritaire en HTML rendu
- absence de régression du flow session (GET 200)
- engine_version transporté en data attribute
- partial existe et utilise <details> natif
- CSS contient les 5 états avec non-color cues
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
from datetime import UTC, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PARTIAL = ROOT / "app" / "templates" / "_partials" / "overload_hint.html"
FOCUS_CSS = ROOT / "app" / "static" / "css" / "session_focus.css"
CARD = ROOT / "app" / "templates" / "_partials" / "exercise_card.html"


# ───────── seed helpers ─────────


def _seed_with_history(db, user_id, *, history_pattern: str = "progress"):
    """Crée 1 session in_progress + 2 sessions COMPLETED historiques pour
    forcer un état overload donné côté engine.

    history_pattern :
      - "progress"     : 2 séances ≥ target_max, quality OK
      - "consolidate"  : 2 séances dans range mais pas top
      - "deload"       : 2 séances quality très basse
    """
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
        slug=f"render-{user_id}-{history_pattern}",
        name=f"Render {history_pattern}",
        kind="strength",
    )
    db.add(t)
    db.flush()
    te1 = TemplateExercise(
        template_id=t.id,
        position=1,
        code="A1",
        name="Back squat",
        set_scheme="3×6-10",
    )
    te2 = TemplateExercise(
        template_id=t.id,
        position=2,
        code="A2",
        name="Lateral raise",
        set_scheme="3×8-12",
    )
    db.add_all([te1, te2])
    db.flush()
    db.add_all([
        RepTarget(
            template_exercise_id=te1.id, set_index=1, min_reps=6, max_reps=10
        ),
        RepTarget(
            template_exercise_id=te2.id, set_index=1, min_reps=8, max_reps=12
        ),
    ])
    db.flush()

    now = datetime.now(UTC)

    # Forcer compute_session_quality(s) à atteindre les seuils overload :
    # formula = 40*work + 40*(success/100) + 10*concentration + 10*global_state
    # progress requiert quality ≥ 0.75 ; deload requiert ≤ 0.55.
    if history_pattern == "progress":
        hist_reps, hist_success = 10, 100  # 40+40+10+10 = 100 → 1.0
    elif history_pattern == "deload":
        hist_reps, hist_success = 10, 0    # 40+0+10+3 = 53 → 0.53
    else:  # consolidate
        hist_reps, hist_success = 8, 50    # 40+20+10+10 = 80 → 0.80

    # 2 historiques COMPLETED sur A1 (active card forcée — A1 = position 1)
    for k in range(2):
        past = WorkoutSession(
            user_id=user_id,
            template_id=t.id,
            template_slug_snapshot=t.slug,
            template_name_snapshot=t.name,
            started_at=now - timedelta(days=7 * (k + 1)),
            ended_at=now - timedelta(days=7 * (k + 1)),
            status="completed",
            global_state=("fatigued" if history_pattern == "deload" else "good"),
            concentration="high",
        )
        pse = SessionExercise(
            template_exercise_id=te1.id,
            exercise_code_snapshot="A1",
            exercise_name_snapshot="Back squat",
            position=1,
            success_score=hist_success,
        )
        pse.set_logs.append(
            SetLog(
                kind="work",
                set_index=1,
                weight_kg=100.0,
                reps=hist_reps,
                completed=True,
            )
        )
        past.session_exercises.append(pse)
        db.add(past)

    # session courante in_progress, 2 exercices
    cur = WorkoutSession(
        user_id=user_id,
        template_id=t.id,
        template_slug_snapshot=t.slug,
        template_name_snapshot=t.name,
        started_at=now,
        status="in_progress",
    )
    se1 = SessionExercise(
        template_exercise_id=te1.id,
        exercise_code_snapshot="A1",
        exercise_name_snapshot="Back squat",
        position=1,
    )
    se1.set_logs.append(
        SetLog(kind="work", set_index=1, weight_kg=100.0, reps=8, completed=False)
    )
    se2 = SessionExercise(
        template_exercise_id=te2.id,
        exercise_code_snapshot="A2",
        exercise_name_snapshot="Lateral raise",
        position=2,
    )
    se2.set_logs.append(
        SetLog(kind="work", set_index=1, weight_kg=10.0, reps=10, completed=False)
    )
    cur.session_exercises.extend([se1, se2])
    db.add(cur)
    db.commit()
    db.refresh(cur)
    return cur


def _render(client, session_id) -> str:
    r = client.get(f"/sessions/{session_id}", follow_redirects=False)
    assert r.status_code == 200, r.text[:400]
    return r.text


# ───────── partial existe + structure ─────────


def test_overload_partial_exists():
    assert PARTIAL.exists(), "_partials/overload_hint.html missing"
    body = PARTIAL.read_text(encoding="utf-8")
    assert "overload-hint" in body
    assert "data-engine-version" in body
    assert "<details" in body, "must use native <details> for reasons (no-JS)"


def test_overload_partial_guards_silent():
    """Garde défensive : le partial ne rend rien si hint absent ou silent."""
    body = PARTIAL.read_text(encoding="utf-8")
    assert "if hint and not hint.is_silent" in body


# ───────── rendu visible quand hint présent ─────────


def test_hint_rendered_on_active_card_when_progress(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _seed_with_history(db, user.id, history_pattern="progress")
        sid = s.id

    body = _render(client, sid)
    assert "overload-hint" in body
    assert 'data-overload-state="progress"' in body
    # cible chiffrée présente
    assert "102.5 kg" in body
    # engine_version transporté
    assert 'data-engine-version="1"' in body


def test_hint_rendered_on_active_card_when_deload(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _seed_with_history(db, user.id, history_pattern="deload")
        sid = s.id

    body = _render(client, sid)
    assert 'data-overload-state="deload"' in body
    # Deload compound 100*0.9 = 90 kg → "90 kg"
    assert "90 kg" in body


# ───────── pas de rendu pour unknown / silent ─────────


def test_no_render_when_history_empty(client):
    """Pas d'historique → engine retourne unknown → router skip
    (is_silent=True) → aucun marqueur overload-hint dans le HTML."""
    from app.database import SessionLocal
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
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        t = WorkoutTemplate(
            slug="no-hist", name="No hist", kind="strength"
        )
        db.add(t)
        db.flush()
        te = TemplateExercise(
            template_id=t.id,
            position=1,
            code="N1",
            name="Brand new",
            set_scheme="3×6-10",
        )
        db.add(te)
        db.flush()
        db.add(
            RepTarget(
                template_exercise_id=te.id,
                set_index=1,
                min_reps=6,
                max_reps=10,
            )
        )
        s = WorkoutSession(
            user_id=user.id,
            template_id=t.id,
            template_slug_snapshot=t.slug,
            template_name_snapshot=t.name,
            started_at=datetime.now(UTC),
            status="in_progress",
        )
        se = SessionExercise(
            template_exercise_id=te.id,
            exercise_code_snapshot="N1",
            exercise_name_snapshot="Brand new",
            position=1,
        )
        se.set_logs.append(
            SetLog(kind="work", set_index=1, weight_kg=80.0, reps=8, completed=False)
        )
        s.session_exercises.append(se)
        db.add(s)
        db.commit()
        db.refresh(s)
        sid = s.id

    body = _render(client, sid)
    assert "overload-hint" not in body, (
        "unknown state must not render any overload hint markup"
    )


# ───────── carte active uniquement ─────────


def test_hint_only_on_active_card_not_others(client):
    """Avec 2 exercices, seul A1 (position 1, active) doit voir le hint.
    A2 ne doit pas être rendu avec un hint (l'engine a calculé son hint
    aussi mais le template ne le rend pas car {% if is_active %})."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _seed_with_history(db, user.id, history_pattern="progress")
        sid = s.id

    body = _render(client, sid)
    # Exactement 1 wrapper overload-hint dans la page (active card only)
    occurrences = len(re.findall(r'class="overload-hint overload-hint--', body))
    assert occurrences == 1, (
        f"overload hint must render exactly once (active card), got {occurrences}"
    )


# ───────── wording non autoritaire ─────────


def test_rendered_hint_has_no_authoritative_wording(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _seed_with_history(db, user.id, history_pattern="progress")
        sid = s.id

    body = _render(client, sid).lower()
    # On scope au bloc overload uniquement pour éviter les faux positifs
    # sur d'autres parties de la page.
    m = re.search(
        r'<div class="overload-hint[^>]*>.*?</div>\s*</div>',
        body,
        re.DOTALL,
    )
    assert m is not None, "overload hint block not found"
    block = m.group(0)
    for tok in ("tu dois", "il faut absolument", "obligatoire"):
        assert tok not in block, f"forbidden token {tok!r} in rendered overload hint"


# ───────── flow session intact ─────────


def test_session_flow_intact_with_hint(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _seed_with_history(db, user.id, history_pattern="consolidate")
        sid = s.id

    body = _render(client, sid)
    # Sticky CTA + rest timer + jump bar toujours présents (non-regression Sx_29)
    assert "dock" in body
    # MIGRÉ — le minuteur n'existe QUE dans l'état `REST` (`§7.2`). Le rendre en permanence est PRÉCISÉMENT ce qui a masqué le défaut `D3` : le bloc était là, non démarré, et le JS partait quand même. La garde vérifie donc son absence hors repos.
    assert "data-rest-display" not in body
    assert "ex-nav" in body


# ───────── CSS : 5 états + non-color cues ─────────


def test_css_contains_5_overload_states():
    css = FOCUS_CSS.read_text(encoding="utf-8")
    for state in ("progress", "consolidate", "top-range", "deload", "unknown"):
        assert f".overload-hint--{state}" in css, (
            f"missing CSS class for state {state}"
        )


def test_css_non_color_cues_per_state():
    """WCAG 1.4.1 : chaque état doit avoir un cue non-color (border-left
    + icone unicode dans intent::before)."""
    css = FOCUS_CSS.read_text(encoding="utf-8")
    # border-left épais sur le wrapper
    assert "border-left: 3px solid" in css
    # icone ::before sur intent pour chaque état (au moins progress/deload/unknown)
    for icon in ("↑", "↓", "→", "🏁", "?"):
        assert icon in css, f"missing non-color cue icon {icon!r}"


# ───────── wire dans exercise_card ─────────


def test_exercise_card_includes_overload_partial():
    src = CARD.read_text(encoding="utf-8")
    assert '_partials/overload_hint.html' in src
    # Doit être dans un bloc {% if is_active %} (active card only).
    # MIGRÉ — cette assertion lisait un COMMENTAIRE. Un commentaire n'est
    # pas un comportement : le renommer faisait rougir la garde alors que
    # le partial était bien inclus. Elle épingle désormais l'inclusion.
    assert '{% include "_partials/overload_hint.html" %}' in src


# ───────── progression_hint legacy supprimé (Sb_30.4) ─────────


def test_progression_hint_legacy_removed():
    """Sb_30.4 a retiré progression_hint.py et son injection ; le hint
    overload prend désormais entièrement le relais."""
    legacy = ROOT / "app" / "services" / "progression_hint.py"
    assert not legacy.exists(), "progression_hint.py legacy must be removed"
    legacy_tests = ROOT / "tests" / "test_progression_hint.py"
    assert not legacy_tests.exists(), "tests/test_progression_hint.py must be removed"


def test_router_no_longer_imports_progression_hint():
    router = (ROOT / "app" / "routers" / "sessions.py").read_text(encoding="utf-8")
    assert "progression_hint" not in router
    assert "compute_progression_hint" not in router
    # La clé "hints" legacy ne doit plus être injectée dans le contexte.
    assert '"hints":' not in router


def test_exercise_card_no_longer_renders_repere_block():
    card = (
        ROOT / "app" / "templates" / "_partials" / "exercise_card.html"
    ).read_text(encoding="utf-8")
    assert "Repère" not in card
    assert 'class="hint__label"' not in card
    assert 'class="hint__text"' not in card
    # La variable `hints` Jinja n'est plus consommée.
    assert "hints.get(se.exercise_code_snapshot)" not in card


# ───────── owner isolation ─────────


def test_owner_isolation_preserved(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.auth import hash_password

    with SessionLocal() as db:
        owner = db.query(User).first()
        s = _seed_with_history(db, owner.id, history_pattern="progress")
        sid = s.id
        other = User(
            username="overload_other",
            password_hash=hash_password("overload_other_xyz"),  # noqa: S106
        )
        db.add(other)
        db.commit()

    client.cookies.clear()
    r = client.post(
        "/login",
        data={"username": "overload_other", "password": "overload_other_xyz"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    r = client.get(f"/sessions/{sid}", follow_redirects=False)
    assert r.status_code == 404
