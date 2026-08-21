"""Tests for behavioral engine scoring logic."""
from __future__ import annotations

import dataclasses
import re

from app.services.behavioral import (
    BehavioralState,
    compute_session_fatigue,
    compute_weighted_fatigue,
    compute_consistency,
    compute_readiness,
)


def test_session_fatigue_high():
    f = compute_session_fatigue(global_state="fatigued", concentration="low")
    assert f == 75.0


def test_session_fatigue_low():
    f = compute_session_fatigue(global_state="good", concentration="high")
    assert f == 15.0


def test_session_fatigue_null_defaults():
    f = compute_session_fatigue(global_state=None, concentration=None)
    assert f == 45.0


def test_session_fatigue_mixed():
    f = compute_session_fatigue(global_state="flat", concentration="high")
    assert f == 30.0


def test_weighted_fatigue_three_sessions():
    fatigue_scores = [75.0, 30.0, 15.0]
    result = compute_weighted_fatigue(fatigue_scores)
    assert abs(result - 49.5) < 0.01


def test_weighted_fatigue_two_sessions():
    result = compute_weighted_fatigue([60.0, 30.0])
    assert abs(result - 48.0) < 0.01


def test_weighted_fatigue_one_session():
    result = compute_weighted_fatigue([75.0])
    assert result == 75.0


def test_weighted_fatigue_no_sessions():
    result = compute_weighted_fatigue([])
    assert result == 50.0


def test_consistency_daily():
    assert compute_consistency(sessions_14d=14) == 100.0


def test_consistency_none():
    assert compute_consistency(sessions_14d=0) == 0.0


def test_consistency_partial():
    result = compute_consistency(sessions_14d=3)
    assert abs(result - 21.43) < 0.1


def test_consistency_capped():
    assert compute_consistency(sessions_14d=20) == 100.0


def test_readiness_formula():
    r = compute_readiness(fatigue=30.0, consistency=80.0, performance=90.0)
    assert abs(r - 77.0) < 0.01


def test_readiness_high_fatigue():
    r = compute_readiness(fatigue=90.0, consistency=50.0, performance=50.0)
    assert abs(r - 30.0) < 0.01


# ── `UX4_03B` — trois tests de tendance et cinq de recommandation, MIGRÉS ────
#
# Ils vérifiaient `compute_trend` et `compute_recommendation`, supprimés par
# `OPERATOR_DECISION` D6. Les supprimer sans rien mettre à la place laisserait
# la porte ouverte à leur retour silencieux : ce qui suit garde la DÉCISION,
# pas l'implémentation disparue.


def test_the_trend_producer_is_gone_and_replaced_by_raw_counts():
    """`compute_trend(0, 0)` rendait **« stable »** — donc un utilisateur qui
    n'avait jamais rien enregistré lisait que son rythme était stable.
    `UX4_03` l'a affiché, l'opérateur l'a refusé.

    La suppression arrive **après** son remplacement, jamais avant
    (`CLAUDE.md §5.3`) : `fc786a2` rend déjà les deux comptages bruts.
    """
    import app.services.behavioral as behavioral

    assert not hasattr(behavioral, "compute_trend")

    # Le remplacement existe, sinon ceci serait une soustraction sèche.
    from app.services.progress_facts import ProgressFacts

    assert {"sessions_last_7", "sessions_prev_7"} <= {
        f.name for f in dataclasses.fields(ProgressFacts)
    }


def test_the_coaching_string_producer_is_gone_with_its_loaded_branches():
    """`compute_recommendation` n'était rendue nulle part, et deux de ses
    branches étaient indéfendables : elle lisait `readiness_score` — fabriqué à
    100 % sur un compte vide — et écrivait « Série en cours, garde le
    rythme ! », la chaîne même que `DO_NOT_SURFACE` interdit.

    **Capacité supprimée, non déplacée.** Si AUREN veut un jour des messages de
    coaching, ils devront être rebâtis sur des entrées honnêtes.
    """
    import inspect

    import app.services.behavioral as behavioral

    assert not hasattr(behavioral, "compute_recommendation")

    src = inspect.getsource(behavioral)
    code = re.sub(r"#.*", " ", src)
    for banned in ("Série en cours", "Belle série"):
        assert banned not in code, (
            f"le vocabulaire de série est revenu dans le moteur : « {banned} »"
        )


def test_behavioral_state_dataclass():
    state = BehavioralState(
        performance_score=88.0, consistency_score=71.4, fatigue_score=35.0,
        streak_days=3, readiness_score=72.0,
    )
    assert state.readiness_score == 72.0
    assert state.streak_days == 3


from datetime import datetime, timezone, timedelta
from tests.helpers import get_test_user_id


def _add_completed_session(user_id, *, concentration="high", global_state="good",
                           success_score=100, n_work=2, n_done=2, started_at=None):
    """Insert a completed session with controlled inputs."""
    from app.database import SessionLocal
    from app.models.session import WorkoutSession, SessionExercise, SetLog

    with SessionLocal() as db:
        s = WorkoutSession(
            user_id=user_id,
            template_slug_snapshot="push-a",
            template_name_snapshot="Push A",
            started_at=started_at or datetime.now(timezone.utc),
            status="completed",
            concentration=concentration,
            global_state=global_state,
        )
        se = SessionExercise(
            exercise_code_snapshot="E1",
            exercise_name_snapshot="Ex",
            position=1,
            success_score=success_score,
        )
        for i in range(1, n_work + 1):
            se.set_logs.append(SetLog(
                kind="work", set_index=i,
                completed=(i <= n_done),
                weight_kg=60.0, reps=10,
            ))
        s.session_exercises.append(se)
        db.add(s)
        db.commit()
        return s.id


def test_compute_behavioral_state_no_sessions(client):
    from app.database import SessionLocal
    from app.services.behavioral import compute_behavioral_state

    uid = get_test_user_id()
    with SessionLocal() as db:
        state = compute_behavioral_state(db, uid)

    assert state.performance_score == 0.0
    assert state.consistency_score == 0.0
    assert state.fatigue_score == 50.0
    assert state.streak_days == 0

    # ⚠ `readiness_score > 0` sur un compte SANS AUCUNE DONNÉE. Ce test
    # l'affirmait déjà, et personne n'avait relevé ce que ça voulait dire :
    # 25,0, dont la totalité vient du défaut de fatigue — `0,5 × (100 − 50)`.
    #
    # L'assertion est conservée telle quelle parce qu'elle décrit le
    # comportement RÉEL du moteur gelé. Elle est simplement nommée pour ce
    # qu'elle est : la preuve que ce champ ne doit jamais atteindre un écran.
    assert state.readiness_score == 25.0, (
        "la valeur fabriquée a changé — la garde de non-exposition doit être "
        "relue avant d'accepter la nouvelle"
    )


def test_compute_behavioral_state_with_sessions(client):
    from app.database import SessionLocal
    from app.services.behavioral import compute_behavioral_state

    uid = get_test_user_id()
    now = datetime.now(timezone.utc)

    for i in range(3):
        _add_completed_session(
            uid, concentration="high", global_state="good",
            started_at=now - timedelta(days=i),
        )

    with SessionLocal() as db:
        state = compute_behavioral_state(db, uid)

    assert state.performance_score > 0
    assert state.consistency_score > 0
    assert state.fatigue_score < 50
    assert state.streak_days >= 3
    assert state.readiness_score > 50


def test_compute_behavioral_state_streak_breaks(client):
    from app.database import SessionLocal
    from app.services.behavioral import compute_behavioral_state

    uid = get_test_user_id()
    now = datetime.now(timezone.utc)

    _add_completed_session(uid, started_at=now)
    _add_completed_session(uid, started_at=now - timedelta(days=1))
    _add_completed_session(uid, started_at=now - timedelta(days=3))

    with SessionLocal() as db:
        state = compute_behavioral_state(db, uid)

    assert state.streak_days == 2
