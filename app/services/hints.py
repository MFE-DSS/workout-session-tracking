"""Deterministic contextual hints for the active exercise card (Sx_08 §4).

V1: two rules max. Pure display (no bouton "Apply"), neutral wording.

Rule A — load +10% vs prior first completed work set
Rule B — reps drop >2 vs prior same set index
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class Hint:
    rule_code: str
    message: str
    context: dict[str, Any] = field(default_factory=dict)
    set_index: int | None = None  # when tied to a specific row

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _work_sets(se) -> list:
    return sorted(
        (sl for sl in se.set_logs if sl.kind == "work"),
        key=lambda sl: sl.set_index,
    )


def compute_hints(session_exercise, prior_occurrence: dict | None) -> list[Hint]:
    """Return hints for the exercise card.

    ``prior_occurrence`` is the dict produced by
    ``exercise_history.last_time_occurrence`` — optional.

    Returns up to two hints (rule A + rule B), independent of each other.
    """
    hints: list[Hint] = []
    work = _work_sets(session_exercise)

    # Rule A — load increased >10% on the first work set
    prior_first_weight = None
    if prior_occurrence and prior_occurrence.get("first_set"):
        prior_first_weight = prior_occurrence["first_set"].get("weight_kg")
    if work and prior_first_weight:
        current_first = work[0].weight_kg
        if current_first is not None and prior_first_weight > 0:
            ratio = (current_first - prior_first_weight) / prior_first_weight
            if ratio > 0.10:
                pct = round(ratio * 100)
                hints.append(Hint(
                    rule_code="A",
                    message=f"+{pct}% de charge vs dernière fois — prudence sur l'exécution",
                    context={
                        "current": current_first,
                        "prior": prior_first_weight,
                        "ratio": ratio,
                    },
                ))

    # Rule B — reps dropped >2 on a set vs prior same set index
    prior_sets = (prior_occurrence or {}).get("sets") or []
    prior_by_index = {}
    for p in prior_sets:
        idx = p.get("set_index")
        reps = p.get("reps")
        if idx is not None and reps is not None:
            prior_by_index[idx] = reps

    for sl in work:
        if sl.reps is None:
            continue
        prior_reps = prior_by_index.get(sl.set_index)
        if prior_reps is None:
            continue
        if sl.reps < prior_reps - 2:
            hints.append(Hint(
                rule_code="B",
                message=f"Set {sl.set_index} : reps réduites vs dernière fois — fatigue installée ?",
                context={"current": sl.reps, "prior": prior_reps},
                set_index=sl.set_index,
            ))
            break  # keep V1 cap at one B-hint per card

    return hints
