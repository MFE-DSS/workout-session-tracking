"""Logging-confidence score for a session (Sx_08 §5).

Returns an integer 0..100 that gauges how well the session was logged
(not performance). Formula:

  40 pts × (work_sets_with_data / total_work_sets)
  15 pts × max(0, 15 − (completed_sans_donnees / total_work_sets × 15))
  10 pts if session.concentration present
  10 pts if session.global_state present
  15 pts depending on anomaly count (0 → 15 ; 1-2 → 10 ; 3-4 → 5 ; >4 → 0)
  10 pts if session.bodyweight_kg present

Every component always contributes to ``max_points`` so that the final
score is a percentage.
"""
from __future__ import annotations

from app.services.anomalies import compute_anomalies


LEVEL_HIGH = "eleve"
LEVEL_MID = "moyen"
LEVEL_LOW = "faible"


def level_for(score: int) -> str:
    if score >= 80:
        return LEVEL_HIGH
    if score >= 50:
        return LEVEL_MID
    return LEVEL_LOW


def _work_sets(session) -> list:
    out = []
    for se in session.session_exercises:
        out.extend(sl for sl in se.set_logs if sl.kind == "work")
    return out


def compute_confidence_score(
    session,
    prior_weight_by_code: dict[str, float | None] | None = None,
    anomalies: list | None = None,
) -> int:
    """Return 0..100 logging confidence."""
    points = 0.0
    max_points = 0.0

    work = _work_sets(session)
    total_work = len(work)
    with_data = sum(
        1 for sl in work if sl.weight_kg is not None or sl.reps is not None
    )
    completed_empty = sum(
        1 for sl in work if sl.completed and sl.weight_kg is None and sl.reps is None
    )

    # 1. Work sets renseignés (40 pts)
    if total_work > 0:
        points += (with_data / total_work) * 40
        max_points += 40

    # 2. Completed flag cohérent (15 pts — penalty for completed-empty)
    if total_work > 0:
        penalty = (completed_empty / total_work) * 15
        points += max(0.0, 15 - penalty)
        max_points += 15

    # 3. Feedback séance (10 + 10 pts)
    if session.concentration:
        points += 10
    max_points += 10
    if session.global_state:
        points += 10
    max_points += 10

    # 4. Anomalies (15 pts)
    anomalies_list = anomalies if anomalies is not None else compute_anomalies(
        session, prior_weight_by_code=prior_weight_by_code
    )
    n = len(anomalies_list)
    if n == 0:
        points += 15
    elif n <= 2:
        points += 10
    elif n <= 4:
        points += 5
    max_points += 15

    # 5. Bodyweight (10 pts)
    if session.bodyweight_kg:
        points += 10
    max_points += 10

    if max_points == 0:
        return 0
    return round((points / max_points) * 100)
