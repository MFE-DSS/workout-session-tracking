"""Sb_27.1 — Home dashboard payload composer.

Composes the three coaching tiles surfaced on `GET /`:

* `today`      — next-session recommendation + short "Pourquoi" phrase
* `last_session` — qualitative summary of the most recent completed session
* `week`       — short weekly signal (sessions count + verdict)

This service ONLY reads. It composes existing read-only services
(`recommendation`, `quality_score`, model columns) — it never mutates
state, never touches scoring core internals, never persists. If a
sub-payload cannot be built (missing data, exception), it returns an
explicit fallback dict rather than crashing the home route.

Contract (Sx_27 §11.5, §16 verbatim):
* Never invents a value. If a datum is "Non déductible", say so.
* Phrases are deterministic (no LLM).
* Caller is the authenticated user — scope is enforced via `user_id`
  filters in every query.
"""
from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.session import SessionExercise, WorkoutSession
from app.models.user import User


def build_home_payload(
    db: Session, user: User, now: datetime | None = None
) -> dict[str, Any]:
    """Top-level composer. Always returns the 3 keys.

    Each sub-builder catches its own exceptions so a partial outage on
    one tile never breaks the others.
    """
    ref = now or datetime.now(UTC)
    today = _safe(_build_today, db, user, ref)
    last_session = _safe(_build_last_session, db, user, ref)
    week = _safe(_build_week, db, user, ref)
    # Sb_RECOVERY_HOME_CONSUMER_01 — first consumer of the P0.4 chain. Wrapped
    # in the same `_safe` guard as its siblings: if the aggregator or the
    # explainer fails, this tile alone becomes unavailable and the
    # recommendation stays usable. It is EXPLANATORY — it reads state and
    # changes no training decision.
    training_state = _safe(_build_training_state, db, user, ref)

    # Sb_27.5 — attach a deterministic narrative phrase per tile. The
    # narrative helpers are pure (no DB, no LLM) and never raise on
    # missing fields, so we don't need a try/except guard here.
    try:
        from app.services.narrative import narrate_reco

        today["narrative"] = narrate_reco(today)
    except Exception:  # noqa: BLE001, S110 — narrative is best-effort, never blocks
        pass

    return {
        "today": today,
        "last_session": last_session,
        "week": week,
        "training_state": training_state,
    }


def _build_training_state(db: Session, user: User, now: datetime) -> dict[str, Any]:
    """The P0.4 « État d'entraînement » tile. Read-only, one aggregation.

    Deferred import: `training_state` pulls the behavioural producer and the
    whole recovery chain, and this module is imported by the home route on a
    hot path. Deferring matches how the sibling builders reach heavy services.
    """
    from app.services.home_training_state import build_home_training_state

    return build_home_training_state(db, user.id, now=now)


def _safe(fn, *args) -> dict[str, Any]:
    """Run a sub-builder; on any error, return a fallback marker.

    Observability hygiene (Sb_26.3): partial home view is better than
    a 500. The error name is the only thing surfaced — no PII, no SQL.
    """
    try:
        return fn(*args)
    except Exception as exc:  # noqa: BLE001 — observability fallback by design
        return {"available": False, "error_type": exc.__class__.__name__}


# ─────────────────── TODAY ───────────────────


def _build_today(db: Session, user: User, now: datetime) -> dict[str, Any]:
    """Recommendation for today + short "Pourquoi" phrase.

    Reuses `recommendation.recommend_next_session` which already returns
    a `top.phrase` string (zero modification to recommendation.py per
    Sx_27 hard contract).
    """
    # If a session is already open, the home view hides the reco block
    # anyway. We still surface a payload so the template can render a
    # consistent "Today" tile pointing at the active session.
    from app.services.session_state import latest_open_session

    open_session = latest_open_session(db, user.id)
    if open_session is not None:
        return {
            "available": True,
            "kind": "in_progress",
            "template_name": open_session.template_name_snapshot,
            "session_id": open_session.id,
            "reason": "Tu as une séance en cours.",
        }

    try:
        from app.services.recommendation import recommend_next_session

        reco = recommend_next_session(db, user.id, now=now)
    except Exception:
        reco = None

    if not reco or not reco.get("top"):
        return {
            "available": True,
            "kind": "no_reco",
            "reason": "Recommandation basée sur ton historique récent.",
        }

    top = reco["top"]
    template = top.get("template")
    phrase = (top.get("phrase") or "").strip()

    # Sb_27.4 — consume the explainer for richer multi-reason context.
    # The explainer is a read-only wrapper on the same `reco` payload
    # (it never re-runs recommendation.py).
    try:
        from app.services.recommendation_explainer import explain_recommendation

        explanation = explain_recommendation(reco)
    except Exception:
        explanation = None

    if explanation and explanation.get("available"):
        primary_reason = explanation.get("primary_reason") or phrase
        reasons = explanation.get("reasons") or []
    else:
        primary_reason = phrase
        reasons = [phrase] if phrase else []

    if not primary_reason:
        primary_reason = "Recommandation basée sur ton historique récent."
    if not reasons:
        reasons = [primary_reason]

    payload: dict[str, Any] = {
        "available": True,
        "kind": "reco",
        "template_slug": getattr(template, "slug", None),
        "template_name": getattr(template, "name", None) or getattr(
            template, "title", None
        ),
        "reason": primary_reason,
        "reasons": reasons,
        "confidence": (explanation or {}).get("confidence"),
        "fallback_note": (explanation or {}).get("fallback_note"),
    }
    ctx = reco.get("context") or {}
    if ctx.get("cold_start"):
        payload["cold_start"] = True
    if ctx.get("fallback"):
        payload["fallback"] = True
    return payload


# ─────────────────── LAST SESSION ───────────────────

_IMPLICIT_LABEL_FR = {
    "intense": "intense",
    "fluide": "fluide",
    "fluid": "fluide",
    "difficult": "difficile",
    "difficile": "difficile",
    "light": "légère",
    "easy": "légère",
}


def _build_last_session(db: Session, user: User, now: datetime) -> dict[str, Any]:
    """Last completed session with implicit_label aggregate + quality."""
    stmt = (
        select(WorkoutSession)
        .where(
            WorkoutSession.user_id == user.id,
            WorkoutSession.status == "completed",
            WorkoutSession.excluded_from_stats.is_(False),
        )
        .order_by(WorkoutSession.started_at.desc())
        .options(
            selectinload(WorkoutSession.session_exercises).selectinload(
                SessionExercise.set_logs
            )
        )
        .limit(1)
    )
    session = db.execute(stmt).scalar_one_or_none()
    if session is None:
        return {
            "available": True,
            "kind": "none",
            "reason": "Pas encore de séance terminée.",
        }

    # SQLite drops tz on round-trip; normalize before arithmetic.
    started = session.started_at
    if started.tzinfo is None:
        started = started.replace(tzinfo=UTC)
    days_ago = max(0, (now - started).days)
    payload: dict[str, Any] = {
        "available": True,
        "kind": "summary",
        "session_id": session.id,
        "template_name": session.template_name_snapshot,
        "days_ago": days_ago,
        "started_at": started.isoformat(),
    }

    # Quality score — only if scoring_version is V2 (Sb_24.5) or we can
    # compute it without surprise. We compute and report; if it fails,
    # we say "Non déductible" rather than crash.
    try:
        from app.services.quality_score import compute_session_quality

        quality = compute_session_quality(session)
        if isinstance(quality, (int, float)):
            payload["quality_score"] = round(float(quality), 1)
    except Exception:
        # Explicit "non déductible" rather than silent absence
        payload["quality_score"] = None
        payload["quality_score_note"] = "Non déductible"

    # Implicit label aggregate — most common label across the session's
    # exercises. If none of the exercises have an implicit label, we say
    # "Non déductible" (verbatim Sb_23 triptyche).
    labels = [
        se.implicit_label
        for se in session.session_exercises
        if se.implicit_label
    ]
    if labels:
        most_common, _ = Counter(labels).most_common(1)[0]
        payload["implicit_label"] = _IMPLICIT_LABEL_FR.get(
            most_common.lower(), most_common
        )
        payload["implicit_label_source"] = (
            f"{Counter(labels)[most_common]}/{len(session.session_exercises)} exos"
        )
    else:
        payload["implicit_label"] = None
        payload["implicit_label_note"] = "Non déductible"

    return payload


# ─────────────────── WEEK ───────────────────


def _start_of_iso_week(ref: datetime) -> datetime:
    """Monday 00:00 UTC of the ISO week containing `ref`."""
    monday = ref - timedelta(days=ref.weekday())
    return monday.replace(hour=0, minute=0, second=0, microsecond=0)


def _build_week(db: Session, user: User, now: datetime) -> dict[str, Any]:
    """Sessions completed since the start of the current ISO week."""
    week_start = _start_of_iso_week(now)
    count = db.execute(
        select(func.count(WorkoutSession.id)).where(
            WorkoutSession.user_id == user.id,
            WorkoutSession.status == "completed",
            WorkoutSession.excluded_from_stats.is_(False),
            WorkoutSession.started_at >= week_start,
        )
    ).scalar_one()

    payload: dict[str, Any] = {
        "available": True,
        "sessions_done": int(count),
        "week_start": week_start.isoformat(),
    }

    if count == 0:
        payload["signal"] = "Pas encore de séance cette semaine."
    elif count == 1:
        payload["signal"] = "1 séance cette semaine. Bon départ."
    elif count <= 3:
        payload["signal"] = f"{count} séances cette semaine."
    else:
        payload["signal"] = f"{count} séances cette semaine. Volume soutenu."

    return payload
