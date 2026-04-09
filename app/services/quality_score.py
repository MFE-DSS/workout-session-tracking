"""Deterministic session quality score on /100.

Formula (documented in docs/PRODUCT_SPEC.md):

  quality = (
      work_completion_component   # 0..40
    + success_score_component     # 0..40
    + concentration_component     # 0..10
    + global_state_component      # 0..10
  )

Components:

  work_completion (40 pts max):
    (completed_work_sets / total_work_sets) * 40
    If zero work sets: 0.

  success_score (40 pts max):
    (avg(non-null success_scores) / 100) * 40
    If no scored exercises: 0.

  concentration (10 pts max):
    high=10, medium=6, low=3, null=0

  global_state (10 pts max):
    good=10, flat=6, fatigued=3, null=0

The score is an integer 0..100. It is intentionally mechanical:
no hidden weights, no subjective interpretation. A session where
every work set is done, every exercise is scored 100, the user
was highly concentrated and feeling good, gets 100.

The function is pure: it takes a WorkoutSession (with its
relations eager-loaded) and returns the score. No DB query inside.
"""
from __future__ import annotations

from app.models.session import WorkoutSession

_CONCENTRATION_POINTS = {"high": 10, "medium": 6, "low": 3}
_GLOBAL_STATE_POINTS = {"good": 10, "flat": 6, "fatigued": 3}


def compute_session_quality(session: WorkoutSession) -> int:
    """Return 0..100 integer quality score for a session."""

    # 1. Work set completion (40 pts max)
    total_work = 0
    done_work = 0
    for se in session.session_exercises:
        for sl in se.set_logs:
            if sl.kind == "work":
                total_work += 1
                if sl.completed:
                    done_work += 1

    work_component = (done_work / total_work * 40) if total_work > 0 else 0.0

    # 2. Average exercise success score (40 pts max)
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

    # 3. Concentration (10 pts max)
    concentration_component = float(
        _CONCENTRATION_POINTS.get(session.concentration or "", 0)
    )

    # 4. Global state (10 pts max)
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
