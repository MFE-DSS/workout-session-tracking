"""Sb_30.bugfix.history-identity-guard — tests racine de l'overload.

Cas reproduisant le bug dogfood réel :

- exercice : "Élévations latérales câble", code ``E2`` sur le template
  ``catch-up-shoulders``, prior 5 kg
- collision : code ``E2`` sur ``pull-b`` = Rowing câble assis prise neutre,
  parfois substitué en "Rowing câble assis prise serrée" à 57 kg
- avant ce fix : ``_history_signals_for_code`` agrégeait les sessions
  inter-templates et l'overload renvoyait ~57 kg sur une séance
  ``catch-up-shoulders``
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.services.overload_engine import compute_overload_hint
from app.services.overload_explainer import explain_overload_hint
from app.services.overload_inputs import build_overload_input_for_exercise

# ───────── seed helpers ─────────


def _make_template(db, *, slug: str, name: str):
    from app.models.catalog import WorkoutTemplate

    t = WorkoutTemplate(slug=slug, name=name, kind="strength")
    db.add(t)
    db.flush()
    return t


def _make_template_exercise(db, *, template_id: int, code: str, name: str):
    from app.models.catalog import RepTarget, TemplateExercise

    te = TemplateExercise(
        template_id=template_id,
        position=1,
        code=code,
        name=name,
        set_scheme="3×6-10",
    )
    db.add(te)
    db.flush()
    db.add(
        RepTarget(template_exercise_id=te.id, set_index=1, min_reps=6, max_reps=10)
    )
    db.flush()
    return te


def _make_session(
    db,
    *,
    user_id: int,
    template,
    te,
    weight_kg: float,
    reps: int,
    started_at: datetime,
    status: str = "completed",
    substituted_name: str | None = None,
    code_override: str | None = None,
):
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    s = WorkoutSession(
        user_id=user_id,
        template_id=template.id,
        template_slug_snapshot=template.slug,
        template_name_snapshot=template.name,
        started_at=started_at,
        ended_at=started_at if status == "completed" else None,
        status=status,
        global_state="good",
        concentration="high",
    )
    se = SessionExercise(
        template_exercise_id=te.id,
        exercise_code_snapshot=code_override or te.code,
        exercise_name_snapshot=te.name,
        substituted_name=substituted_name,
        position=1,
        success_score=80 if status == "completed" else None,
    )
    se.set_logs.append(
        SetLog(
            kind="work",
            set_index=1,
            weight_kg=weight_kg,
            reps=reps,
            completed=(status == "completed"),
        )
    )
    s.session_exercises.append(se)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s, s.session_exercises[0]


# ───────── 1. Collision inter-template ─────────


def test_collision_across_templates_does_not_leak(client):
    """Bug racine : E2 sur ``catch-up-shoulders`` (5 kg) ne doit JAMAIS
    consommer l'historique de E2 sur ``pull-b`` (57 kg)."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        # Template A : élévations latérales câble (code E2), 5 kg
        tpl_a = _make_template(db, slug="catch-up-shoulders-test", name="Catch-up shoulders test")
        te_a = _make_template_exercise(
            db, template_id=tpl_a.id, code="E2",
            name="Élévations latérales câble (test)",
        )
        # Template B : rowing câble assis (code E2 aussi), 57 kg
        tpl_b = _make_template(db, slug="pull-b-test", name="Pull B test")
        te_b = _make_template_exercise(
            db, template_id=tpl_b.id, code="E2",
            name="Rowing câble assis (test)",
        )

        base = datetime.now(UTC)
        # 3 historiques sur template B à 57 kg (le bug aurait fait fuiter ce 57)
        for k in range(3):
            _make_session(
                db, user_id=user.id, template=tpl_b, te=te_b,
                weight_kg=57.0, reps=10,
                started_at=base - timedelta(days=k * 3 + 1),
            )
        # 2 historiques sur template A à 5 kg (le vrai historique)
        for k in range(2):
            _make_session(
                db, user_id=user.id, template=tpl_a, te=te_a,
                weight_kg=5.0, reps=10,
                started_at=base - timedelta(days=k * 3 + 2),
            )

        # Session courante : sur template A (Élévations latérales)
        cur, se_cur = _make_session(
            db, user_id=user.id, template=tpl_a, te=te_a,
            weight_kg=0.0, reps=0,
            started_at=base,
            status="in_progress",
        )

        ov_input = build_overload_input_for_exercise(db, cur, se_cur)
        assert ov_input is not None
        # Historique ne doit contenir QUE 5 kg, jamais 57 kg
        weights = [h.weight_kg for h in ov_input.history]
        assert weights, "history must not be empty for same-template prescribed exercise"
        assert all(w == 5.0 for w in weights), (
            f"history must only contain template A's 5 kg, got {weights}"
        )
        assert 57.0 not in weights


def test_overload_hint_never_proposes_aberrant_weight_after_fix(client):
    """Round-trip vers le hint UI : sur le scénario du bug, aucune cible
    de l'ordre de 57 kg ne doit être proposée pour les 5 kg d'historique."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        tpl_a = _make_template(db, slug="cus-fix", name="CUS fix")
        te_a = _make_template_exercise(
            db, template_id=tpl_a.id, code="E2",
            name="Élévations latérales câble",
        )
        tpl_b = _make_template(db, slug="pullb-fix", name="Pull B fix")
        te_b = _make_template_exercise(
            db, template_id=tpl_b.id, code="E2",
            name="Rowing câble assis",
        )
        base = datetime.now(UTC)
        for k in range(3):
            _make_session(
                db, user_id=user.id, template=tpl_b, te=te_b,
                weight_kg=57.0, reps=10,
                started_at=base - timedelta(days=k * 3 + 1),
            )
        for k in range(2):
            _make_session(
                db, user_id=user.id, template=tpl_a, te=te_a,
                weight_kg=5.0, reps=10,
                started_at=base - timedelta(days=k * 3 + 2),
            )
        cur, se_cur = _make_session(
            db, user_id=user.id, template=tpl_a, te=te_a,
            weight_kg=0.0, reps=0,
            started_at=base,
            status="in_progress",
        )

        ov_input = build_overload_input_for_exercise(db, cur, se_cur)
        assert ov_input is not None
        hint = compute_overload_hint(ov_input)
        # Cible plausible : 5 kg ± un incrément (isolation_free ou
        # isolation_machine selon catégorisation). Jamais 57.
        if hint.target_weight_kg is not None:
            assert hint.target_weight_kg < 15.0, (
                f"target_weight_kg leaked from other template: {hint.target_weight_kg}"
            )


# ───────── 2. Alignement avec last_time_by_exercise_code ─────────


def test_overload_history_aligns_with_last_time(client):
    """``last_time_by_exercise_code`` et l'historique overload doivent
    pointer vers le MÊME premier work set passé."""
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.stats import last_time_by_exercise_code

    with SessionLocal() as db:
        user = db.query(User).first()
        tpl = _make_template(db, slug="align-test", name="Align test")
        te = _make_template_exercise(
            db, template_id=tpl.id, code="E1", name="Test exo align",
        )
        base = datetime.now(UTC)
        _make_session(
            db, user_id=user.id, template=tpl, te=te,
            weight_kg=42.5, reps=8,
            started_at=base - timedelta(days=3),
        )
        cur, se_cur = _make_session(
            db, user_id=user.id, template=tpl, te=te,
            weight_kg=0.0, reps=0,
            started_at=base,
            status="in_progress",
        )

        lt = last_time_by_exercise_code(db, cur, base)
        assert "E1" in lt
        last_weight = lt["E1"]["first_set"]["weight_kg"]
        assert last_weight == 42.5

        ov_input = build_overload_input_for_exercise(db, cur, se_cur)
        assert ov_input is not None
        assert ov_input.history
        assert ov_input.history[0].weight_kg == last_weight


# ───────── 3. Prescrit ne consomme pas les substitutions passées ─────────


def test_prescribed_does_not_consume_substituted_history(client):
    """Si la séance courante est prescrite (substituted_name None),
    les rows passées avec substituted_name non-null ne doivent pas être
    réutilisées comme historique."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        tpl = _make_template(db, slug="prescribed-test", name="Prescribed test")
        te = _make_template_exercise(
            db, template_id=tpl.id, code="E1", name="Prescribed exo",
        )
        base = datetime.now(UTC)
        # 3 historiques substitués à 80 kg (à NE PAS consommer)
        for k in range(3):
            _make_session(
                db, user_id=user.id, template=tpl, te=te,
                weight_kg=80.0, reps=10,
                started_at=base - timedelta(days=k * 3 + 1),
                substituted_name="Substitution exotique",
            )
        # 1 historique prescrit à 40 kg
        _make_session(
            db, user_id=user.id, template=tpl, te=te,
            weight_kg=40.0, reps=10,
            started_at=base - timedelta(days=20),
        )
        # Session courante : prescrite (substituted_name=None)
        cur, se_cur = _make_session(
            db, user_id=user.id, template=tpl, te=te,
            weight_kg=0.0, reps=0,
            started_at=base,
            status="in_progress",
        )

        ov_input = build_overload_input_for_exercise(db, cur, se_cur)
        assert ov_input is not None
        weights = [h.weight_kg for h in ov_input.history]
        # Doit contenir 40 (prescrit), jamais 80 (substitué)
        assert 40.0 in weights
        assert 80.0 not in weights, (
            f"prescribed must NOT consume substituted history, got {weights}"
        )


# ───────── 4. Exercice courant substitué → input None ─────────


def test_substituted_current_returns_none_v1(client):
    """V1 conservateur : si ``se.substituted_name`` est renseigné sur la
    séance courante, ``build_overload_input_for_exercise`` retourne
    ``None`` (silent côté UI)."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        tpl = _make_template(db, slug="sub-test", name="Sub test")
        te = _make_template_exercise(
            db, template_id=tpl.id, code="E1", name="Exo prescrit",
        )
        base = datetime.now(UTC)
        # Historique prescrit "normal"
        _make_session(
            db, user_id=user.id, template=tpl, te=te,
            weight_kg=40.0, reps=10,
            started_at=base - timedelta(days=3),
        )
        # Session courante : substituée
        cur, se_cur = _make_session(
            db, user_id=user.id, template=tpl, te=te,
            weight_kg=0.0, reps=0,
            started_at=base,
            status="in_progress",
            substituted_name="Variante machine",
        )

        ov_input = build_overload_input_for_exercise(db, cur, se_cur)
        assert ov_input is None, (
            "substituted current exercise must yield None (silent) in V1"
        )


def test_substituted_current_produces_silent_hint_in_pipeline(client):
    """Bout-en-bout : substitué courant + explainer → is_silent=True."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        tpl = _make_template(db, slug="sub-pipeline", name="Sub pipeline")
        te = _make_template_exercise(
            db, template_id=tpl.id, code="E1", name="Prescrit pipeline",
        )
        base = datetime.now(UTC)
        for k in range(2):
            _make_session(
                db, user_id=user.id, template=tpl, te=te,
                weight_kg=100.0, reps=10,
                started_at=base - timedelta(days=k * 3 + 1),
            )
        cur, se_cur = _make_session(
            db, user_id=user.id, template=tpl, te=te,
            weight_kg=0.0, reps=0,
            started_at=base,
            status="in_progress",
            substituted_name="Alternative test",
        )

        ov_input = build_overload_input_for_exercise(db, cur, se_cur)
        # Input None → le router skip ; rien n'est calculé.
        assert ov_input is None
        # Si le router appelle quand même (défense en profondeur), le
        # composer doit produire unknown sur input vide. Skippé ici car
        # le pipeline router teste déjà la branche.


# ───────── 5. Changement d'alternative ─────────


def test_two_different_substitutes_do_not_share_history(client):
    """Sur le même prescrit, deux alternatives substituées différentes
    ne doivent pas recevoir la même suggestion mécaniquement issue du
    prescrit."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        tpl = _make_template(db, slug="alt-test", name="Alt test")
        te = _make_template_exercise(
            db, template_id=tpl.id, code="E1", name="Prescrit alt",
        )
        base = datetime.now(UTC)
        # Historique prescrit à 100 kg
        for k in range(3):
            _make_session(
                db, user_id=user.id, template=tpl, te=te,
                weight_kg=100.0, reps=10,
                started_at=base - timedelta(days=k * 3 + 1),
            )
        # Session "courante" 1 : substitut A
        cur1, se1 = _make_session(
            db, user_id=user.id, template=tpl, te=te,
            weight_kg=0.0, reps=0,
            started_at=base,
            status="in_progress",
            substituted_name="Variante A",
        )
        inp1 = build_overload_input_for_exercise(db, cur1, se1)

        # Session "courante" 2 : substitut B différent
        cur2, se2 = _make_session(
            db, user_id=user.id, template=tpl, te=te,
            weight_kg=0.0, reps=0,
            started_at=base + timedelta(seconds=1),
            status="in_progress",
            substituted_name="Variante B",
        )
        inp2 = build_overload_input_for_exercise(db, cur2, se2)

        # V1 : les deux substituts → None (silent). Aucune cible chiffrée
        # ne peut leur être proposée mécaniquement depuis le prescrit.
        assert inp1 is None
        assert inp2 is None


# ───────── 6. Garde-fou aberrant ─────────


def test_implausible_history_drops_input_silently(client):
    """Si malgré les filtres une cohorte est jugée contaminée (max/min > 3×),
    l'input est rejeté pour ne pas laisser un hint trompeur passer."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        tpl = _make_template(db, slug="guard-test", name="Guard test")
        te = _make_template_exercise(
            db, template_id=tpl.id, code="E1", name="Guard exo",
        )
        base = datetime.now(UTC)
        # 3 historiques sur le MÊME template avec un écart aberrant
        # (5 kg et 57 kg). Sans le garde-fou, ces 3 entrées passent le
        # filtre template-id mais l'engine produirait une cible
        # incohérente. Avec le garde-fou, history → vide → input None.
        _make_session(
            db, user_id=user.id, template=tpl, te=te,
            weight_kg=57.0, reps=10,
            started_at=base - timedelta(days=2),
        )
        _make_session(
            db, user_id=user.id, template=tpl, te=te,
            weight_kg=5.0, reps=10,
            started_at=base - timedelta(days=4),
        )
        _make_session(
            db, user_id=user.id, template=tpl, te=te,
            weight_kg=5.0, reps=10,
            started_at=base - timedelta(days=6),
        )
        cur, se_cur = _make_session(
            db, user_id=user.id, template=tpl, te=te,
            weight_kg=0.0, reps=0,
            started_at=base,
            status="in_progress",
        )

        ov_input = build_overload_input_for_exercise(db, cur, se_cur)
        # ratio 57/5 = 11.4 > 3.0 → garde-fou actif → history vide.
        # ov_input n'est pas None (target_min/max présents), mais
        # history=() → engine renvoie unknown → silent.
        assert ov_input is not None
        assert ov_input.history == ()


def test_implausible_guard_produces_silent_hint_in_pipeline(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        tpl = _make_template(db, slug="guard-pipe", name="Guard pipe")
        te = _make_template_exercise(
            db, template_id=tpl.id, code="E1", name="Guard pipe exo",
        )
        base = datetime.now(UTC)
        _make_session(
            db, user_id=user.id, template=tpl, te=te,
            weight_kg=57.0, reps=10,
            started_at=base - timedelta(days=2),
        )
        _make_session(
            db, user_id=user.id, template=tpl, te=te,
            weight_kg=5.0, reps=10,
            started_at=base - timedelta(days=4),
        )
        cur, se_cur = _make_session(
            db, user_id=user.id, template=tpl, te=te,
            weight_kg=0.0, reps=0,
            started_at=base,
            status="in_progress",
        )
        ov_input = build_overload_input_for_exercise(db, cur, se_cur)
        hint = compute_overload_hint(ov_input)
        explained = explain_overload_hint(hint)
        assert explained["is_silent"] is True
        assert hint.state == "unknown"


# ───────── 7. Non-régression : cas normal ─────────


def test_normal_same_template_prescribed_still_produces_hint(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        tpl = _make_template(db, slug="nominal-test", name="Nominal test")
        te = _make_template_exercise(
            db, template_id=tpl.id, code="E1", name="Nominal exo",
        )
        base = datetime.now(UTC)
        # 2 séances prescrites à 100 kg × 10 reps → progress attendu
        for k in range(2):
            _make_session(
                db, user_id=user.id, template=tpl, te=te,
                weight_kg=100.0, reps=10,
                started_at=base - timedelta(days=k * 3 + 1),
            )
        cur, se_cur = _make_session(
            db, user_id=user.id, template=tpl, te=te,
            weight_kg=0.0, reps=0,
            started_at=base,
            status="in_progress",
        )
        ov_input = build_overload_input_for_exercise(db, cur, se_cur)
        assert ov_input is not None
        assert len(ov_input.history) == 2
        hint = compute_overload_hint(ov_input)
        # Engine peut produire progress, consolidate, ou top-range selon
        # qualité — au minimum, NOT unknown.
        assert hint.state != "unknown"


def test_existing_overload_smoke_session_detail_still_200(client):
    """Garde minimum : la page /sessions/{id} (qui consomme le pipeline)
    continue de répondre 200 quand l'historique est légitimement
    monovaleur."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        tpl = _make_template(db, slug="smoke-200", name="Smoke 200")
        te = _make_template_exercise(
            db, template_id=tpl.id, code="E1", name="Smoke exo",
        )
        base = datetime.now(UTC)
        _make_session(
            db, user_id=user.id, template=tpl, te=te,
            weight_kg=80.0, reps=8,
            started_at=base - timedelta(days=3),
        )
        cur, _ = _make_session(
            db, user_id=user.id, template=tpl, te=te,
            weight_kg=0.0, reps=0,
            started_at=base,
            status="in_progress",
        )
        sid = cur.id

    r = client.get(f"/sessions/{sid}", follow_redirects=False)
    assert r.status_code == 200, r.text[:400]
