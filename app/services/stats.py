"""Read-side helpers for the session detail page.

The "Dernière fois" / "Référence précédente" surfaces are rendered per
exercise card from this lookup. The identity is:
  - identity = (template_slug_snapshot, exercise_code_snapshot,
               substitution_key)
  - scope    = prior sessions only (strictly excluding the current one)
  - source   = work sets only (warmups never count)

Sb_DOGFOOD_01.1 — substitution-aware. A previous load is only comparable
if it belongs to the SAME exercise actually performed, so the lookup
applies the SAME substitution policy as the overload inputs
(``overload_inputs._matches_substitution_policy``):
  - current PRESCRIBED (substituted_name is None) → only prescribed
    history counts (past substituted_name IS NULL);
  - current SUBSTITUTED by X → only history with the exact same
    substituted_name X counts;
  - any other case → skipped → the code is ABSENT from the returned dict
    (silence rather than a false previous load from another exercise).

The function still returns a dict keyed by `exercise_code_snapshot`, so
every consumer (`last_time.get(se.exercise_code_snapshot)`) is unchanged;
they simply inherit the coherence guarantee.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional  # noqa: F401  (used below)

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.session import SessionExercise, WorkoutSession


def _fmt_weight(w: Optional[float]) -> str:
    if w is None:
        return "—"
    # Drop .0 tails so "60.0" renders as "60"
    if w == int(w):
        return str(int(w))
    return f"{w:g}"


def _fmt_reps(r: Optional[int]) -> str:
    return "—" if r is None else str(r)


def _relative_when(now: datetime, then: datetime) -> str:
    # SQLite round-trips DATETIMEs as naive. Coerce both sides to a
    # common frame so arithmetic is safe regardless of the dialect.
    if then.tzinfo is None and now.tzinfo is not None:
        then = then.replace(tzinfo=now.tzinfo)
    elif now.tzinfo is None and then.tzinfo is not None:
        now = now.replace(tzinfo=then.tzinfo)
    delta = now - then
    days = delta.days
    if days < 0:
        return "à venir"
    if days == 0:
        return "aujourd'hui"
    if days == 1:
        return "hier"
    if days < 7:
        return f"il y a {days} j"
    if days < 30:
        weeks = days // 7
        return f"il y a {weeks} sem"
    months = days // 30
    return f"il y a {months} mois"


def _summarise_prior(prior: SessionExercise, now: datetime) -> dict:
    """Turn a prior SessionExercise into a display-ready dict."""
    work = sorted(
        (sl for sl in prior.set_logs if sl.kind == "work"),
        key=lambda s: s.set_index,
    )
    # Only completed sets contribute to the summary strings, but we
    # still need to know if the prior session had any work data at all.
    done = [sl for sl in work if sl.completed and (sl.weight_kg is not None or sl.reps is not None)]

    has_data = len(done) > 0
    first_set = None
    if has_data:
        sl = done[0]
        first_set = {"weight_kg": sl.weight_kg, "reps": sl.reps}

    return {
        "relative": _relative_when(now, prior.session.started_at),
        "started_at": prior.session.started_at,
        "session_id": prior.session.id,
        "has_data": has_data,
        "weights_str": " / ".join(_fmt_weight(sl.weight_kg) for sl in done) if has_data else "",
        "reps_str": " / ".join(_fmt_reps(sl.reps) for sl in done) if has_data else "",
        "n_work_sets": len(work),
        "n_done": len(done),
        "first_set": first_set,
        "success_score": prior.success_score,
        "sets": [
            {"set_index": sl.set_index, "weight_kg": sl.weight_kg, "reps": sl.reps}
            for sl in done
        ],
    }


def summarise_current_exercise(se: SessionExercise) -> Optional[dict]:
    """Compact summary of what was actually performed on a
    SessionExercise. Used by the completed-session readability block.

    Returns None if no work set has been marked completed — nothing
    to show for an untouched exercise.
    """
    work = sorted(
        (sl for sl in se.set_logs if sl.kind == "work"),
        key=lambda s: s.set_index,
    )
    done = [sl for sl in work if sl.completed]
    if not done:
        return None
    return {
        "work_done": len(done),
        "work_total": len(work),
        "weights_str": " / ".join(_fmt_weight(sl.weight_kg) for sl in done),
        "reps_str": " / ".join(_fmt_reps(sl.reps) for sl in done),
        "success_score": se.success_score,
        "muscle_sensation": se.muscle_sensation,
    }


def _normalize_sub(name: str | None) -> str | None:
    """Normalize a substituted_name: empty/whitespace → None, else stripped."""
    return (name or "").strip() or None


def _matches_current_substitution(
    past_sub: str | None, current_sub: str | None
) -> bool:
    """Same substitution policy as ``overload_inputs._matches_substitution_policy``.

    - current prescribed (current_sub is None) → only prescribed past (past_sub None);
    - current substituted by X → only past with the exact same X.
    Both arguments are already normalized (see :func:`_normalize_sub`).
    """
    if current_sub is None:
        return past_sub is None
    return past_sub == current_sub


def last_time_by_exercise_code(
    db: Session,
    current_session: WorkoutSession,
    now: datetime,
) -> dict[str, dict]:
    """Return a dict mapping exercise_code_snapshot -> prior summary.

    Codes that have no comparable prior match are simply absent from the
    dict. The caller decides how to render the empty case.

    Identity key: (template_slug_snapshot, exercise_code_snapshot,
    substitution_key). Sessions from other templates never contribute —
    doing so would merge "E2 Incline Smith" with "E2 Tirage nuque" etc.

    Sb_DOGFOOD_01.1 — the previous load must belong to the SAME exercise
    actually performed for the current slot. We therefore only accept a
    prior whose substitution matches the current SessionExercise's
    substitution (prescribed↔prescribed, substituted↔same substituted_name).
    """
    # Current substitution per slot (normalized). A code absent here means
    # the slot isn't in the current session → we never surface a prior for it.
    current_sub_by_code: dict[str, str | None] = {
        se.exercise_code_snapshot: _normalize_sub(se.substituted_name)
        for se in current_session.session_exercises
    }
    # One query that fetches every prior SessionExercise of the same
    # template, ordered by session started_at desc, with its parent
    # session and its set_logs eagerly loaded. We then walk the list
    # in Python and keep only the first hit per exercise code.
    stmt = (
        select(SessionExercise)
        .join(WorkoutSession, WorkoutSession.id == SessionExercise.session_id)
        .where(
            WorkoutSession.id != current_session.id,
            WorkoutSession.template_slug_snapshot == current_session.template_slug_snapshot,
            WorkoutSession.user_id == current_session.user_id,
        )
        .options(
            selectinload(SessionExercise.set_logs),
            joinedload(SessionExercise.session),
        )
        .order_by(WorkoutSession.started_at.desc())
    )

    result: dict[str, dict] = {}
    for prior in db.execute(stmt).unique().scalars().all():
        code = prior.exercise_code_snapshot
        if code in result:
            continue  # we already have a more recent comparable one
        if code not in current_sub_by_code:
            continue  # slot not present in the current session
        # Sb_DOGFOOD_01.1 — only accept a prior whose substitution matches
        # the current slot's substitution (silence rather than false load).
        if not _matches_current_substitution(
            _normalize_sub(prior.substituted_name), current_sub_by_code[code]
        ):
            continue  # keep scanning older sessions for a comparable one
        result[code] = _summarise_prior(prior, now)
    return result
