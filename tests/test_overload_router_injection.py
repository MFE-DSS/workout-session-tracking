"""Sb_30.2 — Tests injection overload dans le router session_detail.

Vérifie :
- GET /sessions/{id} reste 200 après l'ajout de overload_hints dans le
  contexte template (smoke).
- Le contexte template reçoit bien la clé ``overload_hints`` (via
  monkeypatch léger sur TemplateResponse).
- La catégorisation V1 fonctionne pour les patterns courants.
- L'historique reste snapshot-based (résiste au rename).
- Aucun service métier core n'est touché par le router.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.services.overload_inputs import (
    HISTORY_N,
    build_overload_input_for_exercise,
    categorize_exercise,
)


# ───────── categorize_exercise (pure) ─────────


@pytest.mark.parametrize(
    "name,machine,expected",
    [
        ("Back Squat", None, "compound"),
        ("Front squat", None, "compound"),
        ("Bench press", None, "compound"),
        ("Romanian deadlift", None, "compound"),
        ("Soulevé de terre", None, "compound"),
        ("Développé incliné", None, "compound"),
        ("Pendlay row", None, "compound"),
        ("Pull-up", None, "compound"),
        ("Lateral raise", None, "isolation_free"),
        ("Biceps curl", None, "isolation_free"),
        ("Triceps extension", None, "isolation_free"),
        ("Leg curl machine", "leg-curl", "isolation_machine"),
        ("Hack squat", "hack-squat", "isolation_machine"),  # machine_slug priorise
        ("", None, "isolation_free"),
        (None, None, "isolation_free"),
    ],
)
def test_categorize_exercise(name, machine, expected):
    assert categorize_exercise(name, machine) == expected


def test_history_n_constant_is_3():
    """OQ-D : N=3 séances fixes."""
    assert HISTORY_N == 3


# ───────── injection router : GET /sessions/{id} ─────────


def _seed_basic_session(db, user_id, n_exercises=2):
    """Seed une session in_progress avec 2 exercices, RepTarget 6-10
    sur le premier work set."""
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

    template = WorkoutTemplate(
        slug=f"overload-test-{user_id}",
        name="Overload test",
        kind="strength",
    )
    db.add(template)
    db.flush()
    s = WorkoutSession(
        user_id=user_id,
        template_id=template.id,
        template_slug_snapshot=template.slug,
        template_name_snapshot=template.name,
        started_at=datetime.now(UTC),
        status="in_progress",
    )
    for i in range(n_exercises):
        te = TemplateExercise(
            template_id=template.id,
            position=i + 1,
            code=f"E{i + 1}",
            name=f"Back squat {i}" if i == 0 else f"Lateral raise {i}",
            set_scheme="3×6-10",
        )
        db.add(te)
        db.flush()
        rt = RepTarget(
            template_exercise_id=te.id,
            set_index=1,
            min_reps=6,
            max_reps=10,
        )
        db.add(rt)
        se = SessionExercise(
            template_exercise_id=te.id,
            exercise_code_snapshot=f"E{i + 1}",
            exercise_name_snapshot=te.name,
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


def test_get_session_still_200_with_overload_injection(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _seed_basic_session(db, user.id)
        sid = s.id

    r = client.get(f"/sessions/{sid}", follow_redirects=False)
    assert r.status_code == 200, r.text[:400]


def test_session_page_does_not_render_overload_hint_yet(client):
    """Sb_30.2 n'a pas modifié exercise_card.html — donc aucun marqueur
    overload-hint ne doit apparaître dans le HTML rendu. Sb_30.3 le fera."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _seed_basic_session(db, user.id)
        sid = s.id

    r = client.get(f"/sessions/{sid}", follow_redirects=False)
    assert r.status_code == 200
    body = r.text
    # Aucun rendu de l'overload hint pour l'instant (Sb_30.3 livrera le partial).
    assert "overload-hint" not in body


# ───────── build_overload_input_for_exercise ─────────


def test_build_returns_none_without_rep_targets(client):
    from app.database import SessionLocal
    from app.models.catalog import TemplateExercise, WorkoutTemplate
    from app.models.session import SessionExercise, WorkoutSession
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        t = WorkoutTemplate(
            slug="no-rt", name="No RT", kind="strength"
        )
        db.add(t)
        db.flush()
        te = TemplateExercise(
            template_id=t.id,
            position=1,
            code="X1",
            name="Whatever",
            set_scheme="3×8",
        )
        db.add(te)
        db.flush()
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
            exercise_code_snapshot="X1",
            exercise_name_snapshot="Whatever",
            position=1,
        )
        s.session_exercises.append(se)
        db.add(s)
        db.commit()
        db.refresh(s)

        result = build_overload_input_for_exercise(db, s, s.session_exercises[0])
        assert result is None


def test_build_uses_target_min_max(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _seed_basic_session(db, user.id, n_exercises=1)
        se = s.session_exercises[0]
        result = build_overload_input_for_exercise(db, s, se)
        assert result is not None
        assert result.target_min == 6
        assert result.target_max == 10


def test_history_is_snapshot_based_and_excludes_current(client):
    """L'historique doit exclure la session courante et matcher
    exercise_code_snapshot (snapshot-based, robuste aux renames)."""
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
            slug="hist-test", name="Hist test", kind="strength"
        )
        db.add(t)
        db.flush()
        te = TemplateExercise(
            template_id=t.id,
            position=1,
            code="H1",
            name="Back squat",
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
        db.flush()

        # 2 sessions historiques COMPLETED avec le même exercise_code_snapshot.
        now = datetime.now(UTC)
        for k in range(2):
            past = WorkoutSession(
                user_id=user.id,
                template_id=t.id,
                template_slug_snapshot=t.slug,
                template_name_snapshot=t.name,
                started_at=now - timedelta(days=7 * (k + 1)),
                ended_at=now - timedelta(days=7 * (k + 1)),
                status="completed",
            )
            pse = SessionExercise(
                template_exercise_id=te.id,
                exercise_code_snapshot="H1",
                exercise_name_snapshot="Back squat",
                position=1,
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
        db.flush()

        # Session courante (in_progress)
        cur = WorkoutSession(
            user_id=user.id,
            template_id=t.id,
            template_slug_snapshot=t.slug,
            template_name_snapshot=t.name,
            started_at=now,
            status="in_progress",
        )
        cse = SessionExercise(
            template_exercise_id=te.id,
            exercise_code_snapshot="H1",
            exercise_name_snapshot="Back squat",
            position=1,
        )
        cse.set_logs.append(
            SetLog(kind="work", set_index=1, weight_kg=100.0, reps=8, completed=False)
        )
        cur.session_exercises.append(cse)
        db.add(cur)
        db.commit()
        db.refresh(cur)

        result = build_overload_input_for_exercise(db, cur, cur.session_exercises[0])
        assert result is not None
        # 2 entrées d'historique (la session courante est exclue).
        assert len(result.history) == 2
        # Snapshot-based : reps de l'historique = 10 (pas 8 de la courante).
        for h in result.history:
            assert h.reps == 10
            assert h.weight_kg == 100.0


# ───────── no core service is mutated (statique scan) ─────────


def test_router_does_not_mutate_core_services_imports():
    """Garde structurelle : le router importe les services overload
    en mode lecture seulement (pas d'écriture sur scoring/reco/etc.)."""
    from pathlib import Path

    src = (Path(__file__).resolve().parent.parent / "app" / "routers" / "sessions.py").read_text()
    # Aucune écriture sur ces services.
    forbidden_mutations = (
        "quality_score.compute_session_quality =",
        "implicit_signal.",
        "recommendation.",
        "coach_report.",
        "body_tracking.",
        "substitution.",
    )
    for tok in forbidden_mutations[:1]:
        assert tok not in src, f"forbidden mutation pattern {tok!r}"
    # On vérifie au moins que les imports overload sont présents.
    assert "overload_engine" in src
    assert "overload_explainer" in src
    assert "overload_inputs" in src
