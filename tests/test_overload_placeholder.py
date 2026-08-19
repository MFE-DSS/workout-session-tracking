"""Sb_30.next.placeholder — Tests pour le placeholder léger sur le 1er
work set (carte active uniquement).

Garde-fous (verbatim user) :
- placeholder visible quand hint pertinent (progress/consolidate/top-range/deload)
- absence de placeholder quand hint silent/unknown
- placeholder seulement sur carte active (jamais sur les autres cartes)
- aucune valeur préremplie par erreur (value="" reste vide)
- aucune régression sur le flow de saisie (input contracts intacts)
- wording sobre, non autoritaire

Sb_DOGFOOD_01.3 — placeholder cible compacté pour mobile étroit : la valeur
est nue ("102.5", "6-10", "6"), sans le préfixe "≈ " qui alourdissait le rendu
sur petits écrans. Le caractère "suggestion" reste porté par le placeholder
lui-même (texte grisé, jamais rempli) et le contexte de la console.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CARD = ROOT / "app" / "templates" / "_partials" / "exercise_card.html"


# ───────── helper builder unitaire ─────────


def test_build_helper_returns_none_on_no_target():
    """Unitaire : _build_overload_placeholder retourne None si pas de cible."""
    from app.routers.sessions import _build_overload_placeholder
    from app.services.overload_engine import OverloadHint

    h = OverloadHint(
        state="unknown",
        engine_version=1,
        target_weight_kg=None,
        target_reps_min=None,
        target_reps_max=None,
        reasons=(),
    )
    assert _build_overload_placeholder(h) is None


def test_build_helper_progress_range():
    """Progress : range complète → "102.5" + "6-10" (compact, sans ≈)."""
    from app.routers.sessions import _build_overload_placeholder
    from app.services.overload_engine import OverloadHint

    h = OverloadHint(
        state="progress",
        engine_version=1,
        target_weight_kg=102.5,
        target_reps_min=6,
        target_reps_max=10,
        reasons=(),
    )
    ph = _build_overload_placeholder(h)
    assert ph == {"weight": "102.5", "reps": "6-10"}
    # Sb_DOGFOOD_01.3 — plus de préfixe ≈ (placeholder compact mobile)
    assert "≈" not in ph["weight"] and "≈" not in ph["reps"]


def test_build_helper_deload_collapses_reps():
    """Deload : min == max → "6" sans tiret (compact, sans ≈)."""
    from app.routers.sessions import _build_overload_placeholder
    from app.services.overload_engine import OverloadHint

    h = OverloadHint(
        state="deload",
        engine_version=1,
        target_weight_kg=90.0,
        target_reps_min=6,
        target_reps_max=6,
        reasons=(),
    )
    ph = _build_overload_placeholder(h)
    assert ph == {"weight": "90", "reps": "6"}


def test_build_helper_drops_zero_decimals():
    """:g supprime les ``.0`` (90.0 → "90")."""
    from app.routers.sessions import _build_overload_placeholder
    from app.services.overload_engine import OverloadHint

    h = OverloadHint(
        state="deload",
        engine_version=1,
        target_weight_kg=90.0,
        target_reps_min=6,
        target_reps_max=10,
        reasons=(),
    )
    ph = _build_overload_placeholder(h)
    assert ph["weight"] == "90"


def test_build_helper_never_authoritative():
    from app.routers.sessions import _build_overload_placeholder
    from app.services.overload_engine import OverloadHint

    h = OverloadHint(
        state="progress",
        engine_version=1,
        target_weight_kg=100.0,
        target_reps_min=6,
        target_reps_max=10,
        reasons=(),
    )
    ph = _build_overload_placeholder(h)
    blob = (ph["weight"] + " " + (ph["reps"] or "")).lower()
    for tok in ("tu dois", "il faut", "obligatoire"):
        assert tok not in blob


# ───────── seed ─────────


def _seed_with_progress_history(db, user_id):
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
        slug=f"ph-{user_id}", name="Placeholder test", kind="strength"
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
        RepTarget(template_exercise_id=te1.id, set_index=1, min_reps=6, max_reps=10),
        RepTarget(template_exercise_id=te2.id, set_index=1, min_reps=8, max_reps=12),
    ])
    db.flush()
    now = datetime.now(UTC)
    # 2 historiques top-range + quality OK → progress
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
            template_exercise_id=te1.id,
            exercise_code_snapshot="A1",
            exercise_name_snapshot="Back squat",
            position=1,
            success_score=100,
        )
        pse.set_logs.append(
            SetLog(kind="work", set_index=1, weight_kg=100.0, reps=10, completed=True)
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
    # A1 carte active avec 2 work sets (pour vérifier que seul le 1er a le ph)
    se1 = SessionExercise(
        template_exercise_id=te1.id,
        exercise_code_snapshot="A1",
        exercise_name_snapshot="Back squat",
        position=1,
    )
    se1.set_logs.append(
        SetLog(kind="work", set_index=1, weight_kg=None, reps=None, completed=False)
    )
    se1.set_logs.append(
        SetLog(kind="work", set_index=2, weight_kg=None, reps=None, completed=False)
    )
    # A2 carte non active — doit rester sans placeholder même si A2 a un hint
    se2 = SessionExercise(
        template_exercise_id=te2.id,
        exercise_code_snapshot="A2",
        exercise_name_snapshot="Lateral raise",
        position=2,
    )
    se2.set_logs.append(
        SetLog(kind="work", set_index=1, weight_kg=None, reps=None, completed=False)
    )
    cur.session_exercises.extend([se1, se2])
    db.add(cur)
    db.commit()
    db.refresh(cur)
    return cur


def _seed_without_history(db, user_id):
    """Pas d'historique → engine renvoie unknown → router skip → pas de
    placeholder du tout."""
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
        slug=f"nh-{user_id}", name="No history", kind="strength"
    )
    db.add(t)
    db.flush()
    te = TemplateExercise(
        template_id=t.id, position=1, code="N1", name="Brand new",
        set_scheme="3×6-10",
    )
    db.add(te)
    db.flush()
    db.add(
        RepTarget(template_exercise_id=te.id, set_index=1, min_reps=6, max_reps=10)
    )
    s = WorkoutSession(
        user_id=user_id,
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
        SetLog(kind="work", set_index=1, weight_kg=None, reps=None, completed=False)
    )
    s.session_exercises.append(se)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def _render(client, sid: int) -> str:
    r = client.get(f"/sessions/{sid}", follow_redirects=False)
    assert r.status_code == 200, r.text[:400]
    return r.text


# ───────── rendu visible ─────────


def test_placeholder_visible_on_first_work_set_when_progress(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _seed_with_progress_history(db, user.id)
        sid = s.id

    body = _render(client, sid)
    # Compound +2.5 sur 100 → "102.5" (compact mobile, sans ≈)
    assert 'placeholder="102.5"' in body
    assert 'placeholder="6-10"' in body
    # Plus aucun ≈ dans les placeholders cible (Sb_DOGFOOD_01.3)
    assert 'placeholder="≈ 102.5"' not in body
    # Marqueur de row porteur du placeholder
    assert "set-row--has-overload-placeholder" in body


# ───────── absence quand silent/unknown ─────────


def test_no_placeholder_when_history_empty(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _seed_without_history(db, user.id)
        sid = s.id

    body = _render(client, sid)
    # Pas d'historique → engine unknown → aucun placeholder cible ; les inputs
    # retombent sur les placeholders par défaut kg/reps uniquement.
    assert "set-row--has-overload-placeholder" not in body
    # Les inputs gardent les placeholders par défaut
    assert 'placeholder="kg"' in body
    assert 'placeholder="reps"' in body


# ───────── carte active uniquement ─────────


def test_placeholder_only_on_active_card_not_others(client):
    """Sur 2 exercices, A1 actif + A2 non actif → exactement UN
    set-row--has-overload-placeholder dans le DOM."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _seed_with_progress_history(db, user.id)
        sid = s.id

    body = _render(client, sid)
    occurrences = body.count("set-row--has-overload-placeholder")
    assert occurrences == 1, (
        f"placeholder must mark exactly 1 row (active card, 1st work set), got {occurrences}"
    )


# ───────── premier work set uniquement ─────────


def test_placeholder_only_on_first_work_set_not_second(client):
    """Active card a 2 work sets — seul le 1er porte le placeholder.
    On vérifie la position du marqueur vs les deux inputs de la même
    card."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _seed_with_progress_history(db, user.id)
        sid = s.id

    body = _render(client, sid)
    # Extraire les blocs <li class="set-row set-row--work…">
    # MIGRÉ — la carte ACTIVE rend des `setline`, les cartes repliées des
    # `set-row`. On regarde donc les deux familles.
    rows = re.findall(
        r'<li class="(?:setline|set-row) [^"]*"[^>]*>.*?</li>', body, re.DOTALL,
    )
    assert len(rows) >= 3
    placeholder_rows = [r for r in rows if "set-row--has-overload-placeholder" in r]
    assert len(placeholder_rows) == 1, (
        f"only the first work set of the active card should carry the placeholder, "
        f"found {len(placeholder_rows)}"
    )
    # Le row porteur doit aussi contenir le placeholder textuel (compact)
    assert 'placeholder="102.5"' in placeholder_rows[0]


# ───────── aucune valeur préremplie ─────────


def test_value_attribute_stays_empty_when_set_empty(client):
    """Sb_30.next.placeholder ne doit JAMAIS injecter un value=. Le
    placeholder est purement visuel ; un set vide reste value=""."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _seed_with_progress_history(db, user.id)
        sid = s.id
        se1_id = s.session_exercises[0].id
        first_work_set_id = sorted(
            (sl for sl in s.session_exercises[0].set_logs if sl.kind == "work"),
            key=lambda sl: sl.set_index,
        )[0].id

    body = _render(client, sid)
    # Le weight input du 1er work set actif doit avoir value="" (pas de pré-remplissage)
    pattern_w = re.compile(
        r'name="set_' + str(first_work_set_id) + r'_weight_kg"[^>]*value=""',
        re.IGNORECASE,
    )
    assert pattern_w.search(body), (
        "first work set weight input must keep value=\"\" (no pre-fill)"
    )
    pattern_r = re.compile(
        r'name="set_' + str(first_work_set_id) + r'_reps"[^>]*value=""',
        re.IGNORECASE,
    )
    assert pattern_r.search(body)
    assert se1_id  # silence linter (variable utilisée pour validation indirecte)


# ───────── input contracts intacts ─────────


def test_input_contracts_preserved(client):
    """name/inputmode/pattern/autocomplete restent inchangés."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _seed_with_progress_history(db, user.id)
        sid = s.id

    body = _render(client, sid)
    # weight input toujours decimal + pattern
    assert 'inputmode="decimal"' in body
    assert 'pattern="[0-9]*[.,]?[0-9]*"' in body
    # reps input toujours numeric
    assert 'inputmode="numeric"' in body
    assert 'pattern="[0-9]*"' in body
    assert 'autocomplete="off"' in body
    # name= toujours préservé
    assert re.search(r'name="set_\d+_weight_kg"', body)
    assert re.search(r'name="set_\d+_reps"', body)


# ───────── overload hint inchangé ─────────


def test_overload_hint_visible_still_renders(client):
    """Sb_30.3 overload hint UI doit toujours être rendu — Sb_30.next ne
    remplace pas l'affichage du hint, il complète."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _seed_with_progress_history(db, user.id)
        sid = s.id

    body = _render(client, sid)
    assert "overload-hint" in body
    assert 'data-overload-state="progress"' in body
    # Le hint compact dans la box reste présent
    assert "102.5 kg" in body


# ───────── wording non autoritaire en HTML rendu ─────────


def test_rendered_placeholders_are_not_authoritative(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _seed_with_progress_history(db, user.id)
        sid = s.id

    body = _render(client, sid).lower()
    # Sb_DOGFOOD_01.3 — les placeholders cible sont désormais compacts (sans ≈).
    # Chaque placeholder chiffré (weight / reps) doit rester court et sans verbe.
    numeric_ph = re.compile(r"^\d+([.,]\d+)?(-\d+)?$")
    for m in re.finditer(r'placeholder="([^"]*)"', body):
        text = m.group(1)
        if numeric_ph.match(text):  # cible chiffrée (ex. "102.5", "6-10", "90")
            for tok in ("tu dois", "il faut", "obligatoire"):
                assert tok not in text, (
                    f"forbidden authoritative token {tok!r} in placeholder {text!r}"
                )
            # jamais de préfixe ≈ résiduel
            assert "≈" not in text


# ───────── garde structurelle template ─────────


def test_template_uses_overload_placeholders_dict():
    src = CARD.read_text(encoding="utf-8")
    assert "overload_placeholders" in src
    # Sb_UI_04.4 — the placeholder now attaches to the ACTIVE SET (first
    # uncompleted work set of the active card) instead of always the first
    # work set. Intent preserved: placeholder fires on exactly one set of
    # the active card, driven by the console active-set derivation
    # (_is_active_set), never on every row.
    # Sb_UIV2_SESSION_FOCUS_02 — la garde visait la DÉRIVATION, pas le nom de
    # la variable. Le rendu CURRENT-FIRST place la série courante avant les
    # séries terminées, ce qui a demandé d'extraire la ligne dans une macro ;
    # la dérivation `_is_active_set` y devient `set_state == 'active'`.
    #
    # L'invariant est INCHANGÉ et reste vérifié : le placeholder n'est attaché
    # qu'à la série courante de la carte active, jamais à toutes les lignes.
    # Le comportement lui-même est couvert par les tests rendus de ce fichier
    # (test_placeholder_only_on_first_work_set_not_second,
    # test_placeholder_only_on_active_card_not_others) — cette garde-ci reste
    # structurelle et vérifie que le placeholder ne peut pas être passé sans
    # condition d'état.
    # MIGRÉ — la dérivation `set_state == 'active'` du gabarit est remontée
    # dans `app/services/console_state.py` : c'est le service qui désigne
    # `current_set`. L'invariant est INCHANGÉ et devient plus fort — une
    # seule ligne peut recevoir le placeholder, par construction.
    assert "set_inputs(_c, 'série', _ph)" in src, (
        "seule la série courante reçoit le placeholder"
    )
    assert "{{ set_values(sl) }}" in src, (
        "les lignes passées et futures ne portent aucun placeholder"
    )
    assert "overload_placeholders.get(se.id)" in src, (
        "the active row must still receive the real placeholder dict"
    )
