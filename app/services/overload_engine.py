"""Sx_30 — Progressive Overload Engine (V1).

Moteur pur, déterministe, sans accès DB, sans I/O, sans dépendance externe.
Calcule un `OverloadHint` (état + cible + raisons) par exercice à partir
d'un `OverloadInput` (historique snapshot-based + range cible + catégorie).

Contrat (Sx_30 §6 / §9 / §10) :
- 5 états : ``unknown`` / ``progress`` / ``consolidate`` / ``top-range`` /
  ``deload``.
- Cibles concrètes (kg, reps_min, reps_max) ou ``None`` si état ``unknown``.
- Max 3 raisons, en français court, sans langage autoritaire ("tu dois"
  interdit).
- Versioning : :data:`OVERLOAD_ENGINE_VERSION` exposé sur chaque hint.

Aucune dépendance sur ``recommendation.py``, ``quality_score.py``,
``implicit_signal.py``, ``coach_*``, ``body_*``, ``substitution.py``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

OVERLOAD_ENGINE_VERSION = 1

OverloadState = Literal[
    "unknown",
    "progress",
    "consolidate",
    "top-range",
    "deload",
]

ExerciseCategory = Literal[
    "compound",
    "isolation_free",
    "isolation_machine",
]

_INCREMENT_BY_CATEGORY: dict[str, float] = {
    "compound": 2.5,
    "isolation_free": 1.0,
    "isolation_machine": 2.5,
}

# Fallback conservateur si la catégorie est inconnue : utiliser l'incrément
# le plus petit (1.0 kg) pour ne pas suggérer une marche trop ambitieuse.
_FALLBACK_INCREMENT = 1.0

_QUALITY_PROGRESS_MIN = 0.75
_QUALITY_DELOAD_MAX = 0.55
_DELOAD_FACTOR = 0.90


@dataclass(frozen=True)
class HistoricalSetSignal:
    """Snapshot d'un premier work set d'une séance passée complétée.

    ``quality_score`` : 0.0 → 1.0 (None si non mesuré ; ignoré pour
    progress/deload trigger).
    ``fatigue_signal`` : True si l'implicit signal indique fatigue.
    """

    weight_kg: float
    reps: int
    quality_score: float | None = None
    fatigue_signal: bool = False


@dataclass(frozen=True)
class OverloadInput:
    """Inputs purs pour le moteur. Aucun accès DB requis.

    ``history`` : ordonné du plus récent au plus ancien. Au plus 3
    entrées exploitées (Sx_30 OQ-D : N=3 fixe). Les entrées suivantes
    sont ignorées par le moteur V1.
    """

    exercise_category: str
    target_min: int
    target_max: int
    history: tuple[HistoricalSetSignal, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class OverloadHint:
    """Sortie du moteur. Tous champs cibles sont ``None`` si ``state`` =
    ``unknown``. ``reasons`` contient 0 à 3 strings, jamais plus.
    """

    state: OverloadState
    engine_version: int
    target_weight_kg: float | None
    target_reps_min: int | None
    target_reps_max: int | None
    reasons: tuple[str, ...] = field(default_factory=tuple)


# ──────────────────────────── internals ────────────────────────────


def _increment_for(category: str) -> float:
    return _INCREMENT_BY_CATEGORY.get(category, _FALLBACK_INCREMENT)


def _floor_to_increment(weight_kg: float, increment: float) -> float:
    if increment <= 0:
        return weight_kg
    steps = int(weight_kg // increment)
    return round(steps * increment, 4)


def _deload_weight(prior_weight_kg: float, category: str) -> float:
    increment = _increment_for(category)
    raw = prior_weight_kg * _DELOAD_FACTOR
    return _floor_to_increment(raw, increment)


def _is_consecutive_reps_decline(history: tuple[HistoricalSetSignal, ...]) -> bool:
    """True ssi reps[0] < reps[1] et reps[1] < reps[2] (2 baisses consécutives
    sur 3 séances). Spec Sx_30 §9 deload trigger #2.
    """
    if len(history) < 3:
        return False
    h0, h1, h2 = history[0], history[1], history[2]
    return h0.reps < h1.reps and h1.reps < h2.reps


def _mean_quality(history: tuple[HistoricalSetSignal, ...], n: int) -> float | None:
    """Moyenne du quality_score sur les ``n`` séances les plus récentes,
    en ignorant les ``None``. Retourne ``None`` si aucun score valide.
    """
    scores = [h.quality_score for h in history[:n] if h.quality_score is not None]
    if not scores:
        return None
    return sum(scores) / len(scores)


def _truncate_reasons(reasons: list[str]) -> tuple[str, ...]:
    """Garantit max 3 raisons + déduplication ordonnée + filtre vide."""
    seen: list[str] = []
    for r in reasons:
        if not r:
            continue
        if r in seen:
            continue
        seen.append(r)
        if len(seen) >= 3:
            break
    return tuple(seen)


# ──────────────────────────── states builders ────────────────────────────


def _hint_unknown() -> OverloadHint:
    return OverloadHint(
        state="unknown",
        engine_version=OVERLOAD_ENGINE_VERSION,
        target_weight_kg=None,
        target_reps_min=None,
        target_reps_max=None,
        reasons=("historique insuffisant",),
    )


def _hint_deload(
    last: HistoricalSetSignal,
    target_min: int,
    target_max: int,
    category: str,
    triggers: list[str],
) -> OverloadHint:
    new_kg = _deload_weight(last.weight_kg, category)
    return OverloadHint(
        state="deload",
        engine_version=OVERLOAD_ENGINE_VERSION,
        target_weight_kg=new_kg,
        target_reps_min=target_min,
        target_reps_max=target_min,
        reasons=_truncate_reasons(
            triggers + [f"charge réduite à {new_kg:g} kg"]
        ),
    )


def _hint_progress(
    last: HistoricalSetSignal,
    target_min: int,
    target_max: int,
    category: str,
    mean_quality: float | None,
) -> OverloadHint:
    increment = _increment_for(category)
    new_kg = round(last.weight_kg + increment, 4)
    reasons: list[str] = ["2 séances au haut de range"]
    if mean_quality is not None:
        reasons.append(f"quality_score moyen ≥ {_QUALITY_PROGRESS_MIN:g}")
    reasons.append("pas de signal fatigue")
    return OverloadHint(
        state="progress",
        engine_version=OVERLOAD_ENGINE_VERSION,
        target_weight_kg=new_kg,
        target_reps_min=target_min,
        target_reps_max=target_max,
        reasons=_truncate_reasons(reasons),
    )


def _hint_top_range(
    last: HistoricalSetSignal,
    target_min: int,
    target_max: int,
) -> OverloadHint:
    """État ``top-range`` : reps précédentes < target_min → viser au
    moins target_min, mêmes kg. (Naming Sx_30 §9 conservé.)"""
    return OverloadHint(
        state="top-range",
        engine_version=OVERLOAD_ENGINE_VERSION,
        target_weight_kg=last.weight_kg,
        target_reps_min=target_min,
        target_reps_max=target_max,
        reasons=_truncate_reasons(
            [
                f"reps précédentes sous {target_min}",
                "mêmes kg, viser au moins le bas de range",
            ]
        ),
    )


def _hint_consolidate(
    last: HistoricalSetSignal,
    target_min: int,
    target_max: int,
) -> OverloadHint:
    return OverloadHint(
        state="consolidate",
        engine_version=OVERLOAD_ENGINE_VERSION,
        target_weight_kg=last.weight_kg,
        target_reps_min=target_min,
        target_reps_max=target_max,
        reasons=_truncate_reasons(
            [
                "dans la range",
                f"viser {target_max} reps avant d'augmenter la charge",
            ]
        ),
    )


# ──────────────────────────── public API ────────────────────────────


def compute_overload_hint(input: OverloadInput) -> OverloadHint:
    """Calcule un `OverloadHint` à partir d'un `OverloadInput` pur.

    Règles V1 (Sx_30 §9), priorité décroissante :
    1. ``unknown`` si historique vide.
    2. ``deload`` si quality_score moyen ≤ 0.55 (sur 2 dernières)
       OU 2 baisses de reps consécutives sur 3 séances.
       **Prioritaire sur progress** : si signal de fatigue / quality drop,
       on n'augmente pas la charge.
    3. ``progress`` si 2 séances consécutives reps ≥ target_max
       ET quality_score moyen ≥ 0.75 (si mesuré)
       ET aucun signal fatigue sur les 2 dernières.
    4. ``top-range`` si reps de la dernière séance < target_min.
    5. ``consolidate`` sinon (dans la range mais < target_max).
    """
    history = tuple(input.history)
    if not history:
        return _hint_unknown()

    last = history[0]
    category = input.exercise_category
    target_min = input.target_min
    target_max = input.target_max

    # 2. deload (prioritaire)
    deload_triggers: list[str] = []
    mean_q_last2 = _mean_quality(history, 2)
    if mean_q_last2 is not None and mean_q_last2 <= _QUALITY_DELOAD_MAX:
        deload_triggers.append(
            f"quality_score moyen sous {_QUALITY_DELOAD_MAX:g}"
        )
    if _is_consecutive_reps_decline(history):
        deload_triggers.append("baisse de reps sur 3 séances")
    if deload_triggers:
        return _hint_deload(last, target_min, target_max, category, deload_triggers)

    # 3. progress
    if len(history) >= 2:
        h0, h1 = history[0], history[1]
        top_streak = h0.reps >= target_max and h1.reps >= target_max
        no_fatigue = not (h0.fatigue_signal or h1.fatigue_signal)
        mean_q = _mean_quality(history, 2)
        quality_ok = (mean_q is None) or (mean_q >= _QUALITY_PROGRESS_MIN)
        if top_streak and no_fatigue and quality_ok:
            return _hint_progress(last, target_min, target_max, category, mean_q)

    # 4. top-range (sous la range)
    if last.reps < target_min:
        return _hint_top_range(last, target_min, target_max)

    # 5. consolidate (dans la range mais < target_max)
    return _hint_consolidate(last, target_min, target_max)
