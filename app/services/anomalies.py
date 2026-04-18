"""Deterministic anomaly rules for the session review (Sb_08, Sx_08 §3).

Five rules, all info-level. No ML, no prediction, no accusatory wording.
Each rule inspects existing data only and returns zero or more
``Anomaly`` records.

Rule codes (stable, referenced by tests):
    A  — completed set without weight nor reps
    B  — weight and reps both grow from first to last work set
    C  — extreme weight delta (>30%) vs the prior occurrence
    D  — only warmup sets completed, no work set
    E  — success_score >= 80 but all reps below min_reps target
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class Anomaly:
    exercise_code: str | None
    rule_code: str
    severity: str
    message: str
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _work_sets(se) -> list:
    return sorted(
        (sl for sl in se.set_logs if sl.kind == "work"),
        key=lambda sl: sl.set_index,
    )


def _warmup_sets(se) -> list:
    return [sl for sl in se.set_logs if sl.kind == "warmup"]


def _min_rep_target(se) -> int | None:
    """Lowest min_reps across the template exercise's rep_targets."""
    te = getattr(se, "template_exercise", None)
    if te is None or not getattr(te, "rep_targets", None):
        return None
    mins = [rt.min_reps for rt in te.rep_targets if rt.min_reps is not None]
    return min(mins) if mins else None


def _rule_a_completed_empty(se) -> list[Anomaly]:
    out: list[Anomaly] = []
    for sl in se.set_logs:
        if sl.completed and sl.weight_kg is None and sl.reps is None:
            out.append(Anomaly(
                exercise_code=se.exercise_code_snapshot,
                rule_code="A",
                severity="info",
                message=f"Set #{sl.set_index} marqué fait sans reps ni charge saisis",
                context={"set_index": sl.set_index, "kind": sl.kind},
            ))
    return out


def _rule_b_load_and_reps_grow(se) -> list[Anomaly]:
    done = [
        sl for sl in _work_sets(se)
        if sl.completed and sl.weight_kg is not None and sl.reps is not None
    ]
    if len(done) < 2:
        return []
    first, last = done[0], done[-1]
    if last.weight_kg > first.weight_kg and last.reps > first.reps:
        return [Anomaly(
            exercise_code=se.exercise_code_snapshot,
            rule_code="B",
            severity="info",
            message=(
                f"Charge et reps croissent simultanément "
                f"(set {first.set_index}: {first.weight_kg} kg × {first.reps} → "
                f"set {last.set_index}: {last.weight_kg} kg × {last.reps}). À vérifier."
            ),
            context={
                "first_weight": first.weight_kg, "first_reps": first.reps,
                "last_weight": last.weight_kg, "last_reps": last.reps,
            },
        )]
    return []


def _rule_c_extreme_weight_delta(se, prior_weight: float | None) -> list[Anomaly]:
    if prior_weight is None or prior_weight == 0:
        return []
    done = [
        sl for sl in _work_sets(se)
        if sl.completed and sl.weight_kg is not None
    ]
    if not done:
        return []
    curr = done[0].weight_kg
    ratio = (curr - prior_weight) / prior_weight
    if abs(ratio) > 0.30:
        pct = round(ratio * 100)
        sign = "+" if pct > 0 else ""
        return [Anomaly(
            exercise_code=se.exercise_code_snapshot,
            rule_code="C",
            severity="info",
            message=f"{sign}{pct}% de charge vs dernière fois. Volontaire ?",
            context={"current_weight": curr, "prior_weight": prior_weight, "ratio": ratio},
        )]
    return []


def _rule_d_only_warmup(se) -> list[Anomaly]:
    warmups_done = any(sl.completed for sl in _warmup_sets(se))
    work_done = any(sl.completed for sl in _work_sets(se))
    if warmups_done and not work_done:
        return [Anomaly(
            exercise_code=se.exercise_code_snapshot,
            rule_code="D",
            severity="info",
            message="Échauffement fait, aucun work set réalisé",
            context={},
        )]
    return []


def _rule_e_score_vs_reps(se) -> list[Anomaly]:
    if se.success_score is None or se.success_score < 80:
        return []
    min_target = _min_rep_target(se)
    if min_target is None:
        return []
    done = [sl for sl in _work_sets(se) if sl.completed and sl.reps is not None]
    if not done:
        return []
    if all(sl.reps < min_target for sl in done):
        return [Anomaly(
            exercise_code=se.exercise_code_snapshot,
            rule_code="E",
            severity="info",
            message="Score élevé mais reps sous la cible, à vérifier.",
            context={
                "success_score": se.success_score,
                "min_target": min_target,
                "reps": [sl.reps for sl in done],
            },
        )]
    return []


def compute_anomalies(
    session,
    prior_weight_by_code: dict[str, float | None] | None = None,
) -> list[Anomaly]:
    """Return the list of anomalies for a session (0..N).

    ``prior_weight_by_code`` maps ``exercise_code_snapshot`` to the prior
    occurrence's first completed work-set weight, used by rule C.
    If omitted, rule C is skipped (returns no anomaly).
    """
    prior_map = prior_weight_by_code or {}
    out: list[Anomaly] = []
    for se in session.session_exercises:
        out += _rule_a_completed_empty(se)
        out += _rule_b_load_and_reps_grow(se)
        out += _rule_c_extreme_weight_delta(
            se, prior_map.get(se.exercise_code_snapshot)
        )
        out += _rule_d_only_warmup(se)
        out += _rule_e_score_vs_reps(se)
    return out
