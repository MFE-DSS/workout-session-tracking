"""Sb_27.3 — Weekly training loop payload composer.

Composes the "Cette semaine" tile rendered at the top of `GET /progress`:

* sessions_count + previous_week comparison + delta
* volume_signal (deterministic phrase based on count)
* dominant_templates (top 2 by occurrence in the week)
* top_anomaly (first surfaced from existing `compute_anomalies` service,
  never invented)
* hint (deterministic phrase from count + delta + anomaly presence)
* data_quality flag + explicit "Non déductible" fallbacks

Read-only composition on top of existing services
(`anomalies.compute_anomalies`, model columns). Never modifies state,
never touches scoring core, never persists. Caller is the authenticated
user — every query is scoped via `user_id`.

Contract (Sx_27 §11, §16 verbatim):
* Never invents a value. Missing/insufficient data → explicit fallback
  text ("Pas encore assez de données cette semaine.", "Aucune anomalie
  détectée.", etc.).
* Phrases are deterministic (no LLM).
"""
from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.session import SessionExercise, WorkoutSession
from app.models.user import User

_LOW_DATA_NOTE = "Pas encore assez de données cette semaine."
_NO_ANOMALY_NOTE = "Aucune anomalie détectée."
_MAX_DOMINANT = 2


def build_weekly_loop(
    db: Session, user: User, now: datetime | None = None
) -> dict[str, Any]:
    """Top-level composer. Always returns the full key set.

    The whole composer is also wrapped in a `_safe` so a single
    catastrophic DB error degrades the tile rather than crashing
    `/progress`.
    """
    ref = now or datetime.now(UTC)
    try:
        return _compose(db, user, ref)
    except Exception as exc:  # noqa: BLE001 — degrade gracefully
        return _empty_payload(ref, error=exc.__class__.__name__)


def _start_of_iso_week(ref: datetime) -> datetime:
    """Monday 00:00 UTC of the ISO week containing `ref`."""
    monday = ref - timedelta(days=ref.weekday())
    return monday.replace(hour=0, minute=0, second=0, microsecond=0)


def _empty_payload(ref: datetime, *, error: str | None = None) -> dict[str, Any]:
    week_start = _start_of_iso_week(ref)
    week_end = week_start + timedelta(days=7)
    payload: dict[str, Any] = {
        "available": False if error else True,
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "sessions_count": 0,
        "previous_week_sessions_count": None,
        "delta_sessions_count": None,
        "volume_signal": _LOW_DATA_NOTE,
        "dominant_templates": [],
        "top_anomaly": None,
        "top_anomaly_note": _NO_ANOMALY_NOTE,
        "hint": None,
        "hint_note": _LOW_DATA_NOTE,
        "data_quality": "low",
        "data_quality_note": _LOW_DATA_NOTE,
    }
    if error:
        payload["error_type"] = error
    return payload


def _compose(db: Session, user: User, ref: datetime) -> dict[str, Any]:
    week_start = _start_of_iso_week(ref)
    week_end = week_start + timedelta(days=7)
    prev_start = week_start - timedelta(days=7)

    # ── current week sessions
    current_sessions = _load_window_sessions(db, user.id, week_start, week_end)
    sessions_count = len(current_sessions)

    # ── previous week count
    previous_count = _count_window_sessions(db, user.id, prev_start, week_start)

    delta = sessions_count - previous_count if previous_count is not None else None

    # ── if no session at all this week → bail to fallback payload
    if sessions_count == 0:
        payload = _empty_payload(ref)
        payload["previous_week_sessions_count"] = previous_count
        payload["delta_sessions_count"] = delta
        return payload

    # ── dominant templates (top N by count)
    template_counter = Counter(s.template_name_snapshot for s in current_sessions)
    dominant_templates = [
        {"name": name, "count": cnt}
        for name, cnt in template_counter.most_common(_MAX_DOMINANT)
    ]

    # ── top_anomaly via existing service, first non-empty wins
    top_anomaly = _pick_top_anomaly(current_sessions)

    # ── volume signal (phrase deterministe selon count)
    volume_signal = _volume_signal(sessions_count)

    # ── hint deterministe
    hint = _hint_for(sessions_count, delta, top_anomaly)

    # ── data quality flag: "ok" if >= 2 sessions, "low" otherwise
    if sessions_count >= 2:
        data_quality = "ok"
        data_quality_note = ""
    else:
        data_quality = "low"
        data_quality_note = "Données partielles — la semaine vient juste de commencer."

    return {
        "available": True,
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "sessions_count": sessions_count,
        "previous_week_sessions_count": previous_count,
        "delta_sessions_count": delta,
        "volume_signal": volume_signal,
        "dominant_templates": dominant_templates,
        "top_anomaly": top_anomaly,
        "top_anomaly_note": _NO_ANOMALY_NOTE if top_anomaly is None else None,
        "hint": hint,
        "hint_note": None if hint else _LOW_DATA_NOTE,
        "data_quality": data_quality,
        "data_quality_note": data_quality_note,
    }


# ───────── DB helpers ─────────


def _load_window_sessions(
    db: Session, user_id: int, start: datetime, end: datetime
) -> list[WorkoutSession]:
    stmt = (
        select(WorkoutSession)
        .where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.status == "completed",
            WorkoutSession.excluded_from_stats.is_(False),
            WorkoutSession.started_at >= start,
            WorkoutSession.started_at < end,
        )
        .order_by(WorkoutSession.started_at.asc())
        .options(
            selectinload(WorkoutSession.session_exercises).selectinload(
                SessionExercise.set_logs
            )
        )
    )
    return list(db.execute(stmt).scalars().all())


def _count_window_sessions(
    db: Session, user_id: int, start: datetime, end: datetime
) -> int:
    from sqlalchemy import func

    return int(
        db.execute(
            select(func.count(WorkoutSession.id)).where(
                WorkoutSession.user_id == user_id,
                WorkoutSession.status == "completed",
                WorkoutSession.excluded_from_stats.is_(False),
                WorkoutSession.started_at >= start,
                WorkoutSession.started_at < end,
            )
        ).scalar_one()
    )


# ───────── signals ─────────


def _volume_signal(count: int) -> str:
    """Match the Sb_27.1 home phrasing for consistency."""
    if count == 1:
        return "1 séance cette semaine. Bon départ."
    if count <= 3:
        return f"{count} séances cette semaine."
    return f"{count} séances cette semaine. Volume soutenu."


def _pick_top_anomaly(
    sessions: list[WorkoutSession],
) -> dict[str, Any] | None:
    """Run `compute_anomalies` on each session ; surface the first non-empty
    one with a small context payload. Never invents — if the service returns
    nothing, we return None."""
    try:
        from app.services.anomalies import compute_anomalies
    except Exception:
        return None

    for s in sessions:
        try:
            anomalies = compute_anomalies(s)
        except Exception:  # noqa: S112 — per-session anomaly failure is non-fatal
            continue
        if anomalies:
            first = anomalies[0]
            # Find the exercise this anomaly applies to (rule helpers attach
            # `session_exercise_id`).
            se_name = None
            se_id = getattr(first, "session_exercise_id", None)
            if se_id is not None:
                for se in s.session_exercises:
                    if se.id == se_id:
                        se_name = se.exercise_name_snapshot
                        break
            return {
                "code": getattr(first, "code", None),
                "label": getattr(first, "label", None) or getattr(first, "code", None),
                "session_id": s.id,
                "session_template": s.template_name_snapshot,
                "exercise_name": se_name,
            }
    return None


def _hint_for(
    sessions_count: int, delta: int | None, top_anomaly: dict | None
) -> str | None:
    """Deterministic single-phrase hint.

    Priority:
      1. anomaly present → "Vérifie <exercise>"
      2. ≥ 4 sessions → "Volume soutenu — pense à la récupération."
      3. delta ≥ +2 vs semaine précédente → "Tu accélères vs la semaine passée."
      4. delta ≤ -2 → "Rythme en baisse vs la semaine passée."
      5. 1 séance → "Bon démarrage — un deuxième passage solidifierait la semaine."
      6. fallback générique
    """
    if top_anomaly is not None:
        exercise = top_anomaly.get("exercise_name") or "la dernière séance"
        return f"Anomalie détectée sur {exercise} — jette un œil au détail."
    if sessions_count >= 4:
        return "Volume soutenu cette semaine — pense à la récupération."
    if delta is not None and delta >= 2:
        return "Tu accélères vs la semaine passée — garde le rythme."
    if delta is not None and delta <= -2:
        return "Rythme en baisse vs la semaine passée — la prochaine séance compte."
    if sessions_count == 1:
        return "Bon démarrage — un deuxième passage solidifierait la semaine."
    return "Continue sur cette base — les recommandations s'affinent à chaque séance."
