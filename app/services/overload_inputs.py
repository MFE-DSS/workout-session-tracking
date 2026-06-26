"""Sb_30.2 — Build OverloadInput from DB for the session detail page.

Traduit les snapshots SQL (sessions passées, set_logs, rep_targets,
template_exercises) en :class:`OverloadInput` purs, prêts pour
:func:`overload_engine.compute_overload_hint`.

Pourquoi un module dédié :
- garde :mod:`overload_engine` strictement pur (sans accès DB)
- garde le router :mod:`app.routers.sessions` lisible
- isole la résolution des historiques (N=3 fixe — OQ-D)

Aucune modification des services métier core (``recommendation``,
``quality_score``, ``implicit_signal``, ``coach_*``, ``body_*``,
``substitution``). Lecture seule uniquement.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.enums import SessionStatus
from app.models.session import SessionExercise, SetLog, WorkoutSession
from app.services.overload_engine import (
    HistoricalSetSignal,
    OverloadInput,
)
from app.services.quality_score import compute_session_quality

HISTORY_N = 3

# Mots-clés pour catégoriser un exercice à partir du snapshot name V1.
# Conservateur : si rien ne matche compound, fallback isolation_free.
_COMPOUND_KEYWORDS: tuple[str, ...] = (
    "squat",
    "deadlift",
    "soulev",  # soulevé de terre
    "bench",
    "développé",
    "developpe",
    "press",
    "row",
    "rowing",
    "tirage",
    "tractions",
    "pull-up",
    "pullup",
    "dip",
    "clean",
    "snatch",
    "thruster",
    "lunge",
    "fente",
)


def categorize_exercise(name: str | None, machine_slug: str | None) -> str:
    """Détermine la catégorie pour les incréments d'overload V1.

    Heuristique stable et conservative :

    - ``machine_slug`` renseigné → ``"isolation_machine"`` (incrément 2.5 kg)
    - sinon nom contient un mot-clé compound → ``"compound"`` (incrément 2.5 kg)
    - sinon → ``"isolation_free"`` (incrément 1.0 kg, le plus prudent)

    Raffinable Sb_30.next sans casser le moteur (qui se contente d'un
    lookup ``str``).
    """
    if machine_slug:
        return "isolation_machine"
    low = (name or "").lower()
    for kw in _COMPOUND_KEYWORDS:
        if kw in low:
            return "compound"
    return "isolation_free"


def _first_completed_work_set(se: SessionExercise) -> SetLog | None:
    work_sets = sorted(
        (sl for sl in se.set_logs if sl.kind == "work"),
        key=lambda s: s.set_index,
    )
    for sl in work_sets:
        if sl.completed and sl.weight_kg is not None and sl.reps is not None:
            return sl
    return None


def _history_signals_for_code(
    db: Session,
    user_id: int,
    exercise_code: str,
    exclude_session_id: int,
    n: int = HISTORY_N,
) -> tuple[HistoricalSetSignal, ...]:
    """Lit les N dernières WorkoutSessions COMPLETED pour ``user_id``
    contenant un :class:`SessionExercise` ayant ``exercise_code_snapshot``
    == ``exercise_code`` (snapshot-based, résiste aux substitutions/renames).

    Ordonne du plus récent au plus ancien. Chaque entrée porte le premier
    work set complété de l'exercice + la quality_score normalisée [0..1]
    de la session + un ``fatigue_signal`` boolean dérivé de
    ``WorkoutSession.global_state`` (== ``"fatigued"``).
    """
    sessions = db.execute(
        select(WorkoutSession)
        .where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.status == SessionStatus.COMPLETED,
            WorkoutSession.id != exclude_session_id,
        )
        .order_by(WorkoutSession.started_at.desc())
        .limit(50)
    ).scalars().all()

    signals: list[HistoricalSetSignal] = []
    for s in sessions:
        if len(signals) >= n:
            break
        match = next(
            (
                se
                for se in s.session_exercises
                if se.exercise_code_snapshot == exercise_code
            ),
            None,
        )
        if match is None:
            continue
        first_set = _first_completed_work_set(match)
        if first_set is None:
            continue
        # quality_score : 0..100 → 0.0..1.0 ; None si non calculable.
        try:
            raw_quality = compute_session_quality(s)
        except Exception:
            raw_quality = None
        q: float | None
        if raw_quality is None:
            q = None
        else:
            q = max(0.0, min(1.0, float(raw_quality) / 100.0))
        fatigue = (s.global_state == "fatigued")
        signals.append(
            HistoricalSetSignal(
                weight_kg=float(first_set.weight_kg or 0.0),
                reps=int(first_set.reps or 0),
                quality_score=q,
                fatigue_signal=fatigue,
            )
        )
    return tuple(signals)


def build_overload_input_for_exercise(
    db: Session,
    session: WorkoutSession,
    se: SessionExercise,
) -> OverloadInput | None:
    """Construit un :class:`OverloadInput` ou retourne ``None`` si la
    cible (``target_min``/``target_max``) est inconnue.

    Pas d'effet de bord. Pas d'écriture DB.
    """
    te = se.template_exercise
    if te is None or not te.rep_targets:
        return None
    first_rt = sorted(te.rep_targets, key=lambda r: r.set_index)[0]
    if first_rt.min_reps is None or first_rt.max_reps is None:
        return None

    category = categorize_exercise(
        se.substituted_name or se.exercise_name_snapshot,
        getattr(te, "machine_slug", None),
    )
    history = _history_signals_for_code(
        db,
        user_id=session.user_id,
        exercise_code=se.exercise_code_snapshot,
        exclude_session_id=session.id,
    )
    return OverloadInput(
        exercise_category=category,
        target_min=int(first_rt.min_reps),
        target_max=int(first_rt.max_reps),
        history=history,
    )
