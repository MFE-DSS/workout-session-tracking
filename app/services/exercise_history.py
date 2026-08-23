"""Read-side helper for the Exercise History Detail page.

Returns an ordered list of SessionExercise occurrences matching
a single `(template_slug_snapshot, exercise_code_snapshot)`
identity, with per-row deltas precomputed.

Scope rules (documented in docs/PRODUCT_SPEC.md):

- **Identity**: `(template_slug_snapshot, exercise_code_snapshot)`.
  Deliberately does not merge exercises across templates.
- **Included sessions**: both `in_progress` and `completed`. The
  status is rendered so the user can tell them apart.
- **Ordering**: newest first (`started_at DESC`).
- **Delta per row**: compared against the NEXT-OLDER row's first
  completed work set. If either side has no first completed work
  set, the delta is None.
- **first_set**: the first completed work set of each row (by
  set_index). Used both for delta computation and the per-row
  summary strings.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.session import SessionExercise, WorkoutSession
from app.services.delta import Delta, compute_delta, format_delta


def _fmt_weight(w: Optional[float]) -> str:
    if w is None:
        return "—"
    if w == int(w):
        return str(int(w))
    return f"{w:g}"


@dataclass
class ExerciseHistoryEntry:
    session_id: int
    started_at: datetime
    status: str
    weights_str: str  # joined, completed work sets only
    reps_str: str
    success_score: Optional[int]
    muscle_sensation: Optional[str]
    first_weight: Optional[float]
    first_reps: Optional[int]
    delta: Optional[Delta]
    delta_label: Optional[str]  # pre-rendered for the template


def _summarise(se: SessionExercise) -> tuple[ExerciseHistoryEntry, Optional[float], Optional[int]]:
    work = sorted(
        (sl for sl in se.set_logs if sl.kind == "work"),
        key=lambda s: s.set_index,
    )
    done = [
        sl for sl in work
        if sl.completed and (sl.weight_kg is not None or sl.reps is not None)
    ]
    first_w = done[0].weight_kg if done else None
    first_r = done[0].reps if done else None
    entry = ExerciseHistoryEntry(
        session_id=se.session_id,
        started_at=se.session.started_at,
        status=se.session.status,
        weights_str=" / ".join(_fmt_weight(sl.weight_kg) for sl in done),
        reps_str=" / ".join(
            ("—" if sl.reps is None else str(sl.reps)) for sl in done
        ),
        success_score=se.success_score,
        muscle_sensation=se.muscle_sensation,
        first_weight=first_w,
        first_reps=first_r,
        delta=None,
        delta_label=None,
    )
    return entry, first_w, first_r


def get_exercise_history_by_slug(
    db: Session, slug: str, *, user_id: int | None = None
) -> list[ExerciseHistoryEntry]:
    """`TRAIN1-B` — le MÊME historique, sur l'identité stable d'`A1`.

    Décision opérateur : « converger le drill-down d'historique d'exercice sur
    la même identité stable ; conserver les entrées héritées en compatibilité
    seulement ».

    La fonction héritée ci-dessous compare sur `(template_slug,
    exercise_code)`. Mesuré sur le catalogue : **106 identités héritées pour 68
    exercices réels**, et `Leg extensions assises` vit dans **4 gabarits sous 3
    codes différents**. Un même mouvement avait donc jusqu'à quatre historiques
    séparés, et aucun ne le disait.

    Ici, l'appartenance est décidée par `resolve_exercise` — correspondance
    **exacte après normalisation**, alias canoniques compris. **Aucun
    rapprochement approximatif** : un nom libre non résolu n'apparaît pas, il
    n'est pas rattaché au plus ressemblant.

    Le calcul des écarts est **partagé** avec la version héritée : deux
    surfaces qui compareraient des points différents se contrediraient.
    """
    from app.services.exercise_identity import resolve_exercise

    ses = db.execute(
        select(SessionExercise)
        .join(WorkoutSession, WorkoutSession.id == SessionExercise.session_id)
        .where(
            WorkoutSession.user_id == user_id if user_id is not None else True,
            WorkoutSession.status == "completed",
            WorkoutSession.excluded_from_stats.is_(False),
        )
        .options(
            selectinload(SessionExercise.set_logs),
            joinedload(SessionExercise.session),
        )
        .order_by(WorkoutSession.started_at.desc())
    ).unique().scalars().all()

    kept = []
    for se in ses:
        name = se.substituted_name or se.exercise_name_snapshot or ""
        found = resolve_exercise(db, name)
        if found is not None and found.slug == slug:
            kept.append(se)

    entries = [_summarise(se)[0] for se in kept]
    _attach_row_deltas(entries)
    return entries


def _attach_row_deltas(entries: list[ExerciseHistoryEntry]) -> None:
    """Chaque ligne contre la suivante, plus ancienne. Extrait pour que les
    deux entrées — héritée et par identité stable — partagent exactement la
    même règle de comparaison."""
    for i, entry in enumerate(entries):
        if i + 1 >= len(entries):
            continue
        older = entries[i + 1]
        if entry.first_weight is None and entry.first_reps is None:
            continue
        if older.first_weight is None and older.first_reps is None:
            continue
        entry.delta = compute_delta(
            entry.first_weight, entry.first_reps, entry.success_score,
            older.first_weight, older.first_reps, older.success_score,
        )
        entry.delta_label = format_delta(entry.delta) if entry.delta else None


def get_exercise_history(
    db: Session,
    template_slug: str,
    exercise_code: str,
    *,
    user_id: int | None = None,
) -> list[ExerciseHistoryEntry]:
    """Return the history entries (newest first) for a given
    exercise identity, with deltas precomputed row-by-row."""
    stmt = (
        select(SessionExercise)
        .join(WorkoutSession, WorkoutSession.id == SessionExercise.session_id)
        .where(
            WorkoutSession.template_slug_snapshot == template_slug,
            SessionExercise.exercise_code_snapshot == exercise_code,
            WorkoutSession.user_id == user_id if user_id is not None else True,
        )
        .options(
            selectinload(SessionExercise.set_logs),
            joinedload(SessionExercise.session),
        )
        .order_by(WorkoutSession.started_at.desc())
    )
    ses = db.execute(stmt).unique().scalars().all()
    entries: list[ExerciseHistoryEntry] = []
    for se in ses:
        entry, _, _ = _summarise(se)
        entries.append(entry)

    # `TRAIN1-B` — LA RÈGLE DE COMPARAISON EST PARTAGÉE, PAS RECOPIÉE.
    # Cette boucle était écrite ici et rien n'aurait signalé qu'elle diverge de
    # celle de `get_exercise_history_by_slug`. Deux surfaces qui comparent des
    # points différents se contredisent, et c'est précisément la classe de
    # défaut que cette tranche ferme ailleurs.
    _attach_row_deltas(entries)

    return entries
