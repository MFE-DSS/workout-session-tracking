"""Sb_31.2 — Tests de la couche I/O Body Intelligence v2."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.services.body_intelligence import BodyIntelligenceInput
from app.services.body_intelligence_inputs import build_body_intelligence_input

# ───────── helpers ─────────


def _seed_basic_session(db, user_id, *, weight=80.0, reps=8, completed=True):
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
        slug=f"bi-{user_id}-{datetime.now(UTC).timestamp()}",
        name="BI test",
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
    db.add(RepTarget(template_exercise_id=te.id, set_index=1, min_reps=6, max_reps=10))
    s = WorkoutSession(
        user_id=user_id,
        template_id=t.id,
        template_slug_snapshot=t.slug,
        template_name_snapshot=t.name,
        started_at=datetime.now(UTC) - timedelta(days=2),
        ended_at=datetime.now(UTC) - timedelta(days=2),
        status="completed",
        global_state="good",
        concentration="high",
    )
    se = SessionExercise(
        template_exercise_id=te.id,
        exercise_code_snapshot="A1",
        exercise_name_snapshot="Back squat",
        position=1,
        success_score=80,
    )
    se.set_logs.append(
        SetLog(
            kind="work",
            set_index=1,
            weight_kg=weight,
            reps=reps,
            completed=completed,
        )
    )
    s.session_exercises.append(se)
    db.add(s)
    db.commit()
    return s


# ───────── inputs : structure ─────────


def test_build_returns_body_intelligence_input(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        inp = build_body_intelligence_input(db, user)
    assert isinstance(inp, BodyIntelligenceInput)


def test_build_returns_zero_when_no_sessions(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        inp = build_body_intelligence_input(db, user)
    assert inp.sessions_7d == 0
    assert inp.sessions_30d == 0
    assert inp.sessions_90d == 0
    assert inp.quality_score_avg_30d is None
    assert inp.confidence_score_avg is None
    assert inp.implicit_labels_30d == {}


def test_build_counts_completed_sessions(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        _seed_basic_session(db, user.id)
        _seed_basic_session(db, user.id)
        inp = build_body_intelligence_input(db, user)
    assert inp.sessions_30d >= 2
    assert inp.sessions_90d >= 2


# ───────── inputs : body metrics ─────────


def test_build_uses_user_height_cm(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        user.height_cm = 178
        db.commit()
        db.refresh(user)
        inp = build_body_intelligence_input(db, user)
    assert inp.body_height_cm == 178


def test_build_prefers_body_measurement_weight_over_user_weight(client):
    from app.database import SessionLocal
    from app.models.measurement import BodyMeasurement
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        user.weight_kg = 75.0  # fallback statique
        db.add(
            BodyMeasurement(
                user_id=user.id,
                measured_at=datetime.now(UTC),
                weight_kg=78.5,
            )
        )
        db.commit()
        db.refresh(user)
        inp = build_body_intelligence_input(db, user)
    # La mesure datée prend le pas sur user.weight_kg
    assert inp.body_weight_kg == 78.5
    assert inp.body_weight_measured_at_iso is not None


def test_build_falls_back_to_user_weight_when_no_measurement(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        user.weight_kg = 72.0
        db.commit()
        db.refresh(user)
        inp = build_body_intelligence_input(db, user)
    assert inp.body_weight_kg == 72.0
    assert inp.body_weight_measured_at_iso is None  # pas daté


# ───────── inputs : pas de modification DB ─────────


def test_build_does_not_mutate_db(client):
    from app.database import SessionLocal
    from app.models.session import WorkoutSession
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        _seed_basic_session(db, user.id)
        before_count = db.query(WorkoutSession).count()
        for _ in range(3):
            build_body_intelligence_input(db, user)
        after_count = db.query(WorkoutSession).count()
    assert before_count == after_count


# ───────── inputs : pas de logique de priorité ─────────


def test_build_does_not_include_priorities():
    """Garde structurelle : la couche I/O ne doit RIEN exposer qui
    ressemble à une priorité (clé absente du dataclass d'input)."""
    import dataclasses

    fields = {f.name for f in dataclasses.fields(BodyIntelligenceInput)}
    assert not any("priorit" in f for f in fields)
    assert not any("recommend" in f for f in fields)


def test_inputs_module_does_not_compute_overload_compliance():
    """Sb_31.2 ne calcule pas l'overload compliance V1 (différé).
    On s'assure qu'aucun champ d'input n'évoque l'overload."""
    import dataclasses

    fields = {f.name for f in dataclasses.fields(BodyIntelligenceInput)}
    assert not any("overload" in f for f in fields)


def test_inputs_module_does_not_import_compute_body_intelligence():
    """L'inputs builder ne doit pas appeler ``compute_body_intelligence``
    — séparation router-orchestrateur stricte."""
    import inspect

    from app.services import body_intelligence_inputs

    src = inspect.getsource(body_intelligence_inputs)
    assert "compute_body_intelligence" not in src
