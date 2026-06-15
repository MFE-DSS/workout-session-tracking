"""Sb_27.2 — Session Review V1 payload composer.

Composes the data shown on `GET /sessions/{id}/done` so the user
understands at a glance:

* what the session was (summary)
* whether it was qualitative (quality)
* how it felt (implicit_signal, aggregate label)
* which movements were notable (notable_movements, max 3, no inventions)
* what to do next (next_hint, deterministic)

Read-only composition on top of existing services. Never modifies
state, never touches scoring/implicit_signal/quality_score internals
(Sx_27 §9 + Sb_27.2 hard contracts) — only calls them.

Contract (Sx_27 §11, §16):
* Never invents a value. Every missing data path returns a `*_note`
  with "Non déductible" rather than a fabricated number/phrase.
* Phrases are deterministic (no LLM).
* Caller responsibility: the session is already ownership-checked by
  the route via `_load_session(db, id, user.id)` (Sb_26.7) — this
  builder does NOT re-check.
"""
from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
from typing import Any

from app.models.session import SessionExercise, WorkoutSession

_IMPLICIT_LABEL_FR = {
    "intense": "intense",
    "fluide": "fluide",
    "fluid": "fluide",
    "difficult": "difficile",
    "difficile": "difficile",
    "light": "légère",
    "easy": "légère",
}

# Labels that count as "intense / hard" for notable_movements detection.
_HARD_LABELS = {"intense", "difficult", "difficile"}

_MAX_NOTABLE = 3


def build_session_review(
    db, session: WorkoutSession, *, now: datetime | None = None
) -> dict[str, Any]:
    """Top-level composer. Always returns the 5 promised keys.

    `db` is unused by the V1 implementation (everything we need is
    already eagerly loaded on `session` by the calling route). It is
    kept in the signature so future sub-builders can issue DB lookups
    without changing the public API.
    """
    ref = now or datetime.now(UTC)
    payload = {
        "summary": _safe(_build_summary, session, ref),
        "quality": _safe(_build_quality, session),
        "implicit_signal": _safe(_build_implicit_signal, session),
        "notable_movements": _safe_list(_build_notable_movements, session),
        "next_hint": _safe(_build_next_hint, session, ref),
    }
    # Sb_27.5 — deterministic narrative one-liner. Pure function on the
    # payload we just built, never raises on missing fields.
    try:
        from app.services.narrative import narrate_session_review

        payload["narrative"] = narrate_session_review(payload)
    except Exception:  # noqa: BLE001, S110 — narrative is best-effort, never blocks
        pass
    return payload


def _safe(fn, *args) -> dict[str, Any]:
    """Wrap a sub-builder; on exception return a fallback dict.

    Observability hygiene (Sb_26.3): a sub-builder outage degrades the
    review tile, never crashes the whole page.
    """
    try:
        return fn(*args)
    except Exception as exc:  # noqa: BLE001 — fallback by design
        return {"available": False, "error_type": exc.__class__.__name__}


def _safe_list(fn, *args) -> dict[str, Any]:
    """Same as `_safe` but for builders that return a list payload."""
    try:
        return fn(*args)
    except Exception as exc:  # noqa: BLE001 — fallback by design
        return {"available": False, "movements": [], "error_type": exc.__class__.__name__}


# ─────────────────── SUMMARY ───────────────────


def _normalize_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt


def _build_summary(session: WorkoutSession, now: datetime) -> dict[str, Any]:
    started = _normalize_utc(session.started_at)
    ended = _normalize_utc(session.ended_at)
    payload: dict[str, Any] = {
        "available": True,
        "template_name": session.template_name_snapshot,
        "template_slug": session.template_slug_snapshot,
        "started_at": started.isoformat() if started else None,
        "ended_at": ended.isoformat() if ended else None,
    }
    if started and ended:
        seconds = int((ended - started).total_seconds())
        payload["duration_min"] = max(0, seconds // 60)
    else:
        payload["duration_min"] = None
        payload["duration_note"] = "Non déductible"
    if started:
        payload["days_ago"] = max(0, (now - started).days)
    return payload


# ─────────────────── QUALITY ───────────────────


def _build_quality(session: WorkoutSession) -> dict[str, Any]:
    """Quality score via the existing `compute_session_quality` service.

    Never re-implements the formula. If the call raises or returns a
    non-numeric value, we surface "Non déductible".
    """
    try:
        from app.services.quality_score import compute_session_quality

        value = compute_session_quality(session)
    except Exception:
        return {
            "available": True,
            "score": None,
            "note": "Non déductible",
        }
    if not isinstance(value, (int, float)):
        return {
            "available": True,
            "score": None,
            "note": "Non déductible",
        }
    return {
        "available": True,
        "score": round(float(value), 1),
        "scoring_version": int(getattr(session, "scoring_version", 1) or 1),
    }


# ─────────────────── IMPLICIT SIGNAL ───────────────────


def _build_implicit_signal(session: WorkoutSession) -> dict[str, Any]:
    labels = [
        se.implicit_label
        for se in session.session_exercises
        if se.implicit_label
    ]
    if not labels:
        return {
            "available": True,
            "label": None,
            "note": "Non déductible",
        }
    most_common, _ = Counter(labels).most_common(1)[0]
    return {
        "available": True,
        "label": _IMPLICIT_LABEL_FR.get(most_common.lower(), most_common),
        "label_raw": most_common,
        "source_ratio": f"{Counter(labels)[most_common]}/{len(session.session_exercises)}",
    }


# ─────────────────── NOTABLE MOVEMENTS ───────────────────


def _work_volume(se: SessionExercise) -> float:
    """Sum of weight × reps over completed work sets only."""
    total = 0.0
    for sl in se.set_logs:
        if sl.kind != "work" or not sl.completed:
            continue
        w = sl.weight_kg or 0.0
        r = sl.reps or 0
        total += w * r
    return total


def _work_set_stats(se: SessionExercise) -> tuple[int, int]:
    """Return (completed_work_sets, total_work_sets)."""
    total = sum(1 for sl in se.set_logs if sl.kind == "work")
    done = sum(1 for sl in se.set_logs if sl.kind == "work" and sl.completed)
    return done, total


def _build_notable_movements(session: WorkoutSession) -> dict[str, Any]:
    """Pick up to 3 notable exercises with deterministic rules.

    Rules (in priority order, first match wins per exercise):
      1. implicit_label in {intense, difficult/difficile} → "ressenti intense"
      2. all work sets completed AND ≥3 sets → "tous les sets validés (N)"
      3. highest volume among the remaining → "volume élevé (Vkg)"

    Rules 1+2 can both trigger; we merge reasons when they do. Rule 3
    fills the remaining slots, deduplicating by exercise.

    If NOTHING qualifies, returns an empty list + a single fallback
    note (the template renders it instead of an empty section). We
    never invent a "PR" — there is no PR detection logic to read from.
    """
    candidates: list[tuple[SessionExercise, list[str]]] = []
    seen_ids: set[int] = set()

    # Pass 1: implicit label intense/difficile
    for se in session.session_exercises:
        label = (se.implicit_label or "").lower()
        if label in _HARD_LABELS:
            candidates.append((se, ["ressenti intense"]))
            seen_ids.add(se.id)

    # Pass 2: all work sets completed AND >= 3 work sets
    for se in session.session_exercises:
        done, total = _work_set_stats(se)
        if total >= 3 and done == total:
            if se.id in seen_ids:
                # Merge reason into existing candidate
                for c_se, reasons in candidates:
                    if c_se.id == se.id:
                        reasons.append(f"tous les sets validés ({done})")
                        break
            else:
                candidates.append((se, [f"tous les sets validés ({done})"]))
                seen_ids.add(se.id)

    # Pass 3: highest volume among remaining
    if len(candidates) < _MAX_NOTABLE:
        remaining = [
            se for se in session.session_exercises if se.id not in seen_ids
        ]
        remaining.sort(key=_work_volume, reverse=True)
        for se in remaining:
            if len(candidates) >= _MAX_NOTABLE:
                break
            vol = _work_volume(se)
            if vol <= 0:
                continue
            candidates.append((se, [f"volume élevé ({int(vol)} kg)"]))
            seen_ids.add(se.id)

    items: list[dict[str, Any]] = []
    for se, reasons in candidates[:_MAX_NOTABLE]:
        items.append({
            "exercise_code": se.exercise_code_snapshot,
            "exercise_name": se.exercise_name_snapshot,
            "reasons": reasons,
        })

    if not items:
        return {
            "available": True,
            "movements": [],
            "note": "Aucun mouvement remarquable déductible.",
        }
    return {"available": True, "movements": items}


# ─────────────────── NEXT HINT ───────────────────


def _build_next_hint(session: WorkoutSession, now: datetime) -> dict[str, Any]:
    """One deterministic phrase pointing at the next action.

    Never references an unknown future session. Looks only at the
    completed session in hand.
    """
    labels = [
        (se.implicit_label or "").lower()
        for se in session.session_exercises
        if se.implicit_label
    ]
    hard_ratio = (
        sum(1 for label in labels if label in _HARD_LABELS) / max(1, len(labels))
        if labels
        else 0.0
    )

    if labels and hard_ratio >= 0.6:
        return {
            "available": True,
            "phrase": "Séance dense — laisse 24-48 h aux zones travaillées avant la suivante.",
        }
    if labels and hard_ratio <= 0.2:
        return {
            "available": True,
            "phrase": "Séance fluide — tu peux enchaîner sur la suivante quand tu veux.",
        }
    if not labels:
        return {
            "available": True,
            "phrase": "Pense à indiquer ton ressenti sur les prochaines séances pour affiner les recommandations.",
        }
    return {
        "available": True,
        "phrase": "Garde le cap — la prochaine recommandation tient compte de cette séance.",
    }
