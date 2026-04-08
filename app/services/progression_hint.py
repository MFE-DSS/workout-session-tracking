"""Deterministic progression hints for the exercise card.

The rule is intentionally mechanical. It is NOT a coach. It only
answers one question based on the previous completed first work
set and the prescribed rep range of the current first work set:

  "what is the simplest thing to try today on this exercise?"

Rule (documented in docs/PRODUCT_SPEC.md):

  Inputs:
    - target_min, target_max : the prescribed rep range of the
      current session's first work set (from RepTarget)
    - prior_reps, prior_weight : the previous session's first
      completed work set

  Output:
    - None if any input is missing
    - "tenter d'augmenter la charge sur le premier set"
         if prior_reps >= target_max
    - "consolider la charge actuelle"
         if prior_reps < target_min
    - "viser {target_max} reps avant d'augmenter la charge"
         otherwise (prior hit the range but not the top)

The hint is a short sentence, uses no AI vocabulary, and never
claims certainty. It is displayed next to — and clearly below —
the "Dernière fois" block so the user still owns the decision.
"""
from __future__ import annotations

from typing import Optional


def compute_progression_hint(
    target_min: Optional[int],
    target_max: Optional[int],
    prior_weight_kg: Optional[float],
    prior_reps: Optional[int],
) -> Optional[str]:
    """Return a short mechanical hint, or None if data is missing."""
    if target_min is None or target_max is None:
        return None
    if prior_reps is None or prior_weight_kg is None:
        return None
    if prior_reps >= target_max:
        return "tenter d'augmenter la charge sur le premier set"
    if prior_reps < target_min:
        return "consolider la charge actuelle"
    return f"viser {target_max} reps avant d'augmenter la charge"
