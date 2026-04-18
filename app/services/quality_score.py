"""Deterministic session quality score on /100.

Sb_06 — Scoring is dispatched by template kind:
  - strength  → compute_session_quality_strength (legacy formula)
  - cardio    → compute_session_quality_cardio (new, Sx_06 §2.3)

A LISS session well-executed (>= 20min in target zone, subjective good)
now scores >= 85/100. A strength session with mixed completion keeps
the legacy semantics unchanged.

The dispatcher is transparent for consumers (leaderboard, kpis, timeline,
behavioral engine) which read `quality_score` without knowing the formula.
"""
from __future__ import annotations

from typing import Optional

from app.models.session import WorkoutSession


# ---------------------------------------------------------------------------
# Shared subjective points (concentration + global_state)
# ---------------------------------------------------------------------------

_CONCENTRATION_POINTS = {"high": 10, "medium": 6, "low": 3}
_GLOBAL_STATE_POINTS = {"good": 10, "flat": 6, "fatigued": 3}


def _session_kind(session: WorkoutSession) -> str:
    """Return 'strength' or 'cardio' based on template kind (safe fallback)."""
    try:
        kind = session.template.kind if session.template else None
    except Exception:
        kind = None
    if kind == "cardio":
        return "cardio"
    return "strength"


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------


def compute_session_quality(session: WorkoutSession) -> int:
    """Return 0..100 quality score, dispatched by template kind."""
    if _session_kind(session) == "cardio":
        return compute_session_quality_cardio(session)
    return compute_session_quality_strength(session)


# ---------------------------------------------------------------------------
# Strength formula (unchanged, renamed for clarity)
# ---------------------------------------------------------------------------


def compute_session_quality_strength(session: WorkoutSession) -> int:
    """Return 0..100 strength score.

    Components:
      - Work set completion (40) : completed_work_sets / total_work_sets
      - Success score (40)       : avg(non-null success_score) / 100
      - Concentration (10)       : high=10, medium=6, low=3, null=0
      - Global state (10)        : good=10, flat=6, fatigued=3, null=0
    """
    # 1. Work set completion
    total_work = 0
    done_work = 0
    for se in session.session_exercises:
        for sl in se.set_logs:
            if sl.kind == "work":
                total_work += 1
                if sl.completed:
                    done_work += 1
    work_component = (done_work / total_work * 40) if total_work > 0 else 0.0

    # 2. Average exercise success score
    scores = [
        se.success_score
        for se in session.session_exercises
        if se.success_score is not None
    ]
    if scores:
        avg_score = sum(scores) / len(scores)
        score_component = (avg_score / 100) * 40
    else:
        score_component = 0.0

    # 3. Concentration
    concentration_component = float(
        _CONCENTRATION_POINTS.get(session.concentration or "", 0)
    )

    # 4. Global state
    global_state_component = float(
        _GLOBAL_STATE_POINTS.get(session.global_state or "", 0)
    )

    raw = (
        work_component
        + score_component
        + concentration_component
        + global_state_component
    )
    return max(0, min(100, round(raw)))


# ---------------------------------------------------------------------------
# Cardio formula (Sx_06 §2.3)
# ---------------------------------------------------------------------------


def _cardio_duration_component(duration_min: Optional[int]) -> float:
    """0..50 points based on session duration."""
    if duration_min is None:
        return 0.0
    if duration_min >= 20:
        return 50.0
    if duration_min >= 15:
        return 40.0
    if duration_min >= 10:
        return 25.0
    if duration_min >= 5:
        return 10.0
    return 0.0


def _cardio_intensity_component(bpm_avg: Optional[int]) -> float:
    """0..20 points based on average BPM vs target zone.

    If bpm is null (no sensor), baseline of 15 (no penalty).
    Target LISS zone: 115..135 bpm (with tolerance).
    """
    if bpm_avg is None:
        return 15.0
    if 115 <= bpm_avg <= 135:
        return 20.0
    if 100 <= bpm_avg <= 145:
        return 12.0
    return 5.0


def _cardio_completion_component(session: WorkoutSession) -> float:
    """0..20 points based on optional abs/core exercise completion.

    If the cardio template carries no exercises (liss-only), return full
    credit. If it carries abs (liss-abs), scale by completion ratio.
    """
    exs = session.session_exercises or []
    if not exs:
        return 20.0
    total = sum(1 for se in exs for sl in se.set_logs if sl.kind == "work")
    if total == 0:
        return 20.0
    done = sum(
        1 for se in exs for sl in se.set_logs
        if sl.kind == "work" and sl.completed
    )
    return 20.0 * (done / total)


def _cardio_subjective_component(session: WorkoutSession) -> float:
    """0..10 points, half-weighted vs strength (concentration + global_state)."""
    conc = _CONCENTRATION_POINTS.get(session.concentration or "", 0) / 2
    state = _GLOBAL_STATE_POINTS.get(session.global_state or "", 0) / 2
    return float(conc + state)


def compute_session_quality_cardio(session: WorkoutSession) -> int:
    """Return 0..100 cardio score.

    Components (Sx_06 §2.3):
      - Duration (50)     : >= 20min full credit, degrades below
      - Intensity (20)    : bpm in target zone full, baseline 15 if null
      - Completion (20)   : abs/core exercises completion or 20 default
      - Subjective (10)   : half-weighted concentration + global_state
    """
    duration = _cardio_duration_component(session.cardio_duration_min)
    intensity = _cardio_intensity_component(session.cardio_bpm_avg)
    completion = _cardio_completion_component(session)
    subjective = _cardio_subjective_component(session)

    raw = duration + intensity + completion + subjective
    return max(0, min(100, round(raw)))
