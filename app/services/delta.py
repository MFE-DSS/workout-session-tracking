"""Deterministic delta between two exercise occurrences.

Used both on the session detail page (current vs prior) and on
the exercise history detail page (row N vs row N+1).

Rule (documented in docs/PRODUCT_SPEC.md):

  Inputs:
    - current : (weight_kg, reps, success_score) of the current
                first completed work set
    - prior   : same tuple for the immediately previous completed
                occurrence

  Outputs (a `Delta` dict, or None if no comparable data):
    - weight_delta : float or None  (None if either side is None)
    - reps_delta   : int   or None
    - score_trend  : "up" | "flat" | "down" | None

  Formatting: `format_delta` joins non-null pieces with " · ".
  A zero delta on weight or reps shows as "=".

The function NEVER infers a "delta" from partial data. If the
prior side has no completed first work set, the delta is None.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Delta:
    weight_delta: Optional[float]
    reps_delta: Optional[int]
    score_trend: Optional[str]  # "up" | "flat" | "down" | None


def compute_delta(
    current_weight: Optional[float],
    current_reps: Optional[int],
    current_score: Optional[int],
    prior_weight: Optional[float],
    prior_reps: Optional[int],
    prior_score: Optional[int],
) -> Optional[Delta]:
    """Return a Delta or None if nothing is comparable."""
    weight_delta = None
    if current_weight is not None and prior_weight is not None:
        weight_delta = current_weight - prior_weight

    reps_delta = None
    if current_reps is not None and prior_reps is not None:
        reps_delta = current_reps - prior_reps

    score_trend = None
    if current_score is not None and prior_score is not None:
        if current_score > prior_score:
            score_trend = "up"
        elif current_score < prior_score:
            score_trend = "down"
        else:
            score_trend = "flat"

    if weight_delta is None and reps_delta is None and score_trend is None:
        return None
    return Delta(
        weight_delta=weight_delta,
        reps_delta=reps_delta,
        score_trend=score_trend,
    )


def _fmt_weight_delta(w: float) -> str:
    if w == 0:
        return "= kg"
    sign = "+" if w > 0 else ""
    # Drop the trailing ".0" on round values so "+2.0" renders as "+2".
    if w == int(w):
        return f"{sign}{int(w)} kg"
    return f"{sign}{w:g} kg"


def _fmt_reps_delta(r: int) -> str:
    if r == 0:
        return "= reps"
    sign = "+" if r > 0 else ""
    return f"{sign}{r} reps"


_SCORE_LABEL = {
    "up": "score en hausse",
    "down": "score en baisse",
    "flat": "score stable",
}


def format_delta(delta: Optional[Delta]) -> Optional[str]:
    """Turn a Delta into a compact human-readable string, or None.

    Example outputs:
        "+2.5 kg · +2 reps · score en hausse"
        "= kg · +1 reps"
        "= kg · = reps · score stable"
    """
    if delta is None:
        return None
    parts: list[str] = []
    if delta.weight_delta is not None:
        parts.append(_fmt_weight_delta(delta.weight_delta))
    if delta.reps_delta is not None:
        parts.append(_fmt_reps_delta(delta.reps_delta))
    if delta.score_trend is not None:
        parts.append(_SCORE_LABEL[delta.score_trend])
    return " · ".join(parts) if parts else None
