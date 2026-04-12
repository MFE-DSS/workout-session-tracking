"""Deterministic behavioral engine for SPIGNOS.

Transforms raw workout data into actionable user feedback using
simple, interpretable formulas. No AI, no randomness.

Scoring:
  - Performance: composite score from most recent session
  - Consistency: sessions_14d / 14 * 100 (capped at 100)
  - Fatigue: weighted avg of subjective feedback (last 3 sessions)
  - Readiness: 0.5*(100-fatigue) + 0.3*consistency + 0.2*performance
  - Streak: consecutive calendar days with sessions
  - Trend: session count last 7d vs previous 7d

Recommendations: priority-based rules, first match wins.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BehavioralState:
    """Complete behavioral snapshot for a user."""

    performance_score: float
    consistency_score: float
    fatigue_score: float
    trend_direction: str
    streak_days: int
    readiness_score: float
    recommendation: str


_GLOBAL_STATE_FATIGUE = {"fatigued": 80.0, "flat": 50.0, "good": 20.0}
_CONCENTRATION_FATIGUE = {"low": 70.0, "medium": 40.0, "high": 10.0}

_DEFAULT_GLOBAL_STATE_FATIGUE = 50.0
_DEFAULT_CONCENTRATION_FATIGUE = 40.0
_DEFAULT_FATIGUE = 50.0


def compute_session_fatigue(
    *, global_state: str | None, concentration: str | None
) -> float:
    gs = _GLOBAL_STATE_FATIGUE.get(global_state or "", _DEFAULT_GLOBAL_STATE_FATIGUE)
    co = _CONCENTRATION_FATIGUE.get(concentration or "", _DEFAULT_CONCENTRATION_FATIGUE)
    return (gs + co) / 2


def compute_weighted_fatigue(fatigue_scores: list[float]) -> float:
    n = len(fatigue_scores)
    if n == 0:
        return _DEFAULT_FATIGUE
    if n == 1:
        return fatigue_scores[0]
    if n == 2:
        return 0.6 * fatigue_scores[0] + 0.4 * fatigue_scores[1]
    return 0.5 * fatigue_scores[0] + 0.3 * fatigue_scores[1] + 0.2 * fatigue_scores[2]


def compute_consistency(sessions_14d: int) -> float:
    return min(100.0, (sessions_14d / 14) * 100)


def compute_readiness(
    fatigue: float, consistency: float, performance: float
) -> float:
    return 0.5 * (100 - fatigue) + 0.3 * consistency + 0.2 * performance


def compute_trend(last_7: int, prev_7: int) -> str:
    if last_7 > prev_7:
        return "up"
    if last_7 < prev_7:
        return "down"
    return "stable"


def compute_recommendation(state: BehavioralState) -> str:
    if state.fatigue_score >= 75:
        return "Fatigue élevée détectée. Privilégie le repos ou une séance légère."
    if state.streak_days >= 5 and state.fatigue_score >= 60:
        return "Belle série ! Mais pense à récupérer pour maintenir la qualité."
    if state.consistency_score < 30:
        return "La régularité est la clé. Vise au moins 2 séances cette semaine."
    if state.trend_direction == "down" and state.performance_score >= 60:
        return "Tendance en baisse malgré un bon niveau. Un boost de régularité suffirait."
    if state.readiness_score >= 80:
        return "Excellente forme. C'est le moment de pousser l'intensité."
    if state.readiness_score >= 50:
        return "Bonne condition générale. Continue sur ta lancée."
    if state.streak_days >= 3:
        return "Série en cours, garde le rythme !"
    return "Chaque séance compte. Lance-toi quand tu es prêt."


from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.session import SessionExercise, WorkoutSession
from app.services.performance import compute_composite_score
from app.services.quality_score import compute_session_quality


def compute_behavioral_state(db: Session, user_id: int) -> BehavioralState:
    """Compute the full behavioral state for a user from DB data."""
    now = datetime.now(timezone.utc)
    today = now.date()

    _uf = WorkoutSession.user_id == user_id
    _completed = WorkoutSession.status == "completed"
    _not_excluded = WorkoutSession.excluded_from_stats.is_(False)

    # --- Last 3 completed sessions (for fatigue + performance) ---
    last_3 = list(
        db.execute(
            select(WorkoutSession)
            .where(_uf, _completed, _not_excluded)
            .order_by(WorkoutSession.started_at.desc())
            .limit(3)
            .options(
                selectinload(WorkoutSession.session_exercises)
                .selectinload(SessionExercise.set_logs)
            )
        ).scalars().all()
    )

    # Performance: composite score of most recent session
    performance = 0.0
    if last_3:
        s = last_3[0]
        quality = compute_session_quality(s)
        total_work = sum(
            1 for se in s.session_exercises
            for sl in se.set_logs if sl.kind == "work"
        )
        done_work = sum(
            1 for se in s.session_exercises
            for sl in se.set_logs if sl.kind == "work" and sl.completed
        )
        cr = done_work / total_work if total_work > 0 else 0.0
        performance = compute_composite_score(quality, cr)

    # Fatigue: weighted average of subjective feedback
    fatigue_scores = [
        compute_session_fatigue(
            global_state=s.global_state, concentration=s.concentration
        )
        for s in last_3
    ]
    fatigue = compute_weighted_fatigue(fatigue_scores)

    # --- Consistency: sessions in last 14 days ---
    window_14 = now - timedelta(days=14)
    sessions_14d = db.execute(
        select(func.count(WorkoutSession.id))
        .where(_uf, _completed, _not_excluded)
        .where(WorkoutSession.started_at >= window_14)
    ).scalar_one() or 0
    consistency = compute_consistency(sessions_14d)

    # --- Trend: last 7 vs previous 7 ---
    window_7 = now - timedelta(days=7)
    window_14_for_trend = now - timedelta(days=14)
    last_7_count = db.execute(
        select(func.count(WorkoutSession.id))
        .where(_uf, _completed, _not_excluded)
        .where(WorkoutSession.started_at >= window_7)
    ).scalar_one() or 0
    prev_7_count = db.execute(
        select(func.count(WorkoutSession.id))
        .where(_uf, _completed, _not_excluded)
        .where(WorkoutSession.started_at >= window_14_for_trend)
        .where(WorkoutSession.started_at < window_7)
    ).scalar_one() or 0
    trend = compute_trend(last_7_count, prev_7_count)

    # --- Streak: consecutive calendar days with sessions ---
    window_30 = now - timedelta(days=30)
    recent_dates_rows = db.execute(
        select(WorkoutSession.started_at)
        .where(_uf)
        .where(WorkoutSession.started_at >= window_30)
        .order_by(WorkoutSession.started_at.desc())
    ).scalars().all()
    session_dates = {d.date() for d in recent_dates_rows}

    streak = 0
    check_date = today
    while check_date in session_dates:
        streak += 1
        check_date -= timedelta(days=1)

    # --- Readiness ---
    readiness = compute_readiness(fatigue, consistency, performance)

    # --- Build state + recommendation ---
    state = BehavioralState(
        performance_score=round(performance, 1),
        consistency_score=round(consistency, 1),
        fatigue_score=round(fatigue, 1),
        trend_direction=trend,
        streak_days=streak,
        readiness_score=round(readiness, 1),
        recommendation="",
    )
    state.recommendation = compute_recommendation(state)

    return state
