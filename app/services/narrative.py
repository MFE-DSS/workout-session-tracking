"""Sb_27.5 — Deterministic Coach Narrative.

Pure functions that take the existing coaching payloads (Sb_27.1 home,
Sb_27.2 session_review, Sb_27.3 weekly_loop) and produce ONE short
phrase per block, in a consistent voice.

Contract (Sx_27 §11, §16 + OQ-2/OQ-6 verbatim user):
* No LLM, no network call, no external service, no new dependency.
* "tu" informel, jamais "vous", pas d'impératif agressif.
* Phrases nominales / suggestives, max ~80 caractères, max 1 phrase.
* Mobile-first 360×640 → la phrase doit tenir sur 1-2 lignes.
* Never invents a value : si les données sont insuffisantes, la phrase
  signale explicitement l'incertitude (Sx_27 §16).
* Pure functions : aucune lecture DB, aucune mutation, aucune
  dépendance sur l'identité utilisateur.

Public API:

    from app.services.narrative import (
        narrate_reco,
        narrate_session_review,
        narrate_week,
    )

Each helper returns a dict with the same shape:
    {
        "available": bool,
        "phrase": str,
        "tone": "neutral" | "warning" | "encouragement" | "low_data",
        "data_quality": "ok" | "low",
        "fallback_note": str | None,
    }
"""
from __future__ import annotations

from typing import Any

_MAX_PHRASE_LEN = 120  # ~2 lines on a 360px viewport at 14px font
_LOW_DATA_PHRASE = "Données trop faibles — complète une séance pour affiner."
_LOW_DATA_NOTE = "Non déductible"


# ───────── shared helpers ─────────


def _empty(*, tone: str = "low_data") -> dict[str, Any]:
    """Default 'no data' payload — same shape for all three helpers."""
    return {
        "available": True,
        "phrase": _LOW_DATA_PHRASE,
        "tone": tone,
        "data_quality": "low",
        "fallback_note": _LOW_DATA_NOTE,
    }


def _ok(phrase: str, *, tone: str = "neutral") -> dict[str, Any]:
    """OK payload with explicit phrase. Phrase is clipped to _MAX_PHRASE_LEN."""
    clipped = phrase.strip()
    if len(clipped) > _MAX_PHRASE_LEN:
        clipped = clipped[: _MAX_PHRASE_LEN - 1].rstrip() + "…"
    return {
        "available": True,
        "phrase": clipped,
        "tone": tone,
        "data_quality": "ok",
        "fallback_note": None,
    }


def _safe_get(d: Any, key: str, default: Any = None) -> Any:
    """Defensive dict.get — returns default if d is not a dict."""
    if not isinstance(d, dict):
        return default
    return d.get(key, default)


# ───────── narrate_reco ─────────


def narrate_reco(today_payload: Any) -> dict[str, Any]:
    """Synthesise the "Today" tile into one short phrase.

    Consumes the `home.today` dict produced by Sb_27.1 + Sb_27.4
    (`build_home_payload._build_today`). Reads :

      * kind: "in_progress" | "reco" | "no_reco"
      * template_name
      * confidence: "ok" | "low" (from explainer)
      * cold_start: bool
      * fallback: bool
      * primary_zones (when available from the reco context)

    Never re-runs the recommendation logic. If the payload is missing
    or partial, returns the low-data fallback phrase.
    """
    if not isinstance(today_payload, dict):
        return _empty()
    kind = today_payload.get("kind")

    if kind == "in_progress":
        name = today_payload.get("template_name") or "Séance"
        return _ok(f"{name} en cours — reprends quand tu veux.", tone="neutral")

    if kind == "no_reco" or kind is None:
        return _empty()

    # kind == "reco"
    name = today_payload.get("template_name") or "Séance recommandée"
    confidence = today_payload.get("confidence")
    cold_start = bool(today_payload.get("cold_start"))
    fallback = bool(today_payload.get("fallback"))

    if cold_start:
        return {
            "available": True,
            "phrase": f"{name} pour démarrer — données encore limitées.",
            "tone": "low_data",
            "data_quality": "low",
            "fallback_note": _LOW_DATA_NOTE,
        }

    if fallback or confidence == "low":
        return {
            "available": True,
            "phrase": f"{name} — recommandation basée sur ton historique récent.",
            "tone": "low_data",
            "data_quality": "low",
            "fallback_note": _LOW_DATA_NOTE,
        }

    return _ok(f"{name} recommandée — bon créneau pour cette zone.", tone="neutral")


# ───────── narrate_session_review ─────────


def narrate_session_review(review_payload: Any) -> dict[str, Any]:
    """Synthesise the Session Review V1 tile into one short phrase.

    Consumes the dict produced by `build_session_review` (Sb_27.2):
      * implicit_signal: { label, source_ratio, available }
      * quality: { score, scoring_version, available }
      * notable_movements: { movements: [...], note }

    Voice : nominal / suggestif, "tu" implicite (rare ici car la phrase
    décrit la séance plutôt que l'utilisateur), max 1 phrase.
    """
    if not isinstance(review_payload, dict):
        return _empty()

    impl = _safe_get(review_payload, "implicit_signal", {})
    quality = _safe_get(review_payload, "quality", {})
    notable = _safe_get(review_payload, "notable_movements", {})

    label = _safe_get(impl, "label")
    score = _safe_get(quality, "score")
    movements_count = len(_safe_get(notable, "movements", []) or [])

    if label == "intense" or label == "difficile":
        return _ok(
            "Séance dense — récupère 24-48 h sur les zones travaillées.",
            tone="warning",
        )
    if label == "fluide" or label == "légère":
        return _ok(
            "Séance fluide — tu peux enchaîner sur la suivante quand tu veux.",
            tone="encouragement",
        )

    # Pas de label, fallback sur quality + notable_movements
    if isinstance(score, (int, float)) and score >= 70 and movements_count > 0:
        return _ok(
            "Séance solide — quelques mouvements à retenir.",
            tone="encouragement",
        )
    if isinstance(score, (int, float)) and score < 40:
        return {
            "available": True,
            "phrase": "Séance courte — note ton ressenti la prochaine fois pour affiner.",
            "tone": "low_data",
            "data_quality": "low",
            "fallback_note": _LOW_DATA_NOTE,
        }

    # Pas de signal exploitable → fallback explicite
    return {
        "available": True,
        "phrase": "Pas assez de signal sur cette séance — indique ton ressenti pour affiner.",
        "tone": "low_data",
        "data_quality": "low",
        "fallback_note": _LOW_DATA_NOTE,
    }


# ───────── narrate_week ─────────


def narrate_week(weekly_payload: Any) -> dict[str, Any]:
    """Synthesise the weekly loop tile into one short phrase.

    Consumes the dict produced by `build_weekly_loop` (Sb_27.3):
      * sessions_count, delta_sessions_count, previous_week_sessions_count
      * top_anomaly (dict or None)
      * dominant_templates (list)
      * data_quality
    """
    if not isinstance(weekly_payload, dict):
        return _empty()

    count = _safe_get(weekly_payload, "sessions_count", 0) or 0
    delta = _safe_get(weekly_payload, "delta_sessions_count")
    anomaly = _safe_get(weekly_payload, "top_anomaly")

    if count == 0:
        return _empty()

    # Anomaly highest priority — pointer to investigate
    if anomaly is not None:
        return _ok(
            "Anomalie détectée cette semaine — jette un œil au détail.",
            tone="warning",
        )

    if count >= 4:
        return _ok(
            "Semaine soutenue — pense à la récupération.",
            tone="warning",
        )

    if isinstance(delta, int) and delta >= 2:
        return _ok(
            "Tu accélères vs la semaine passée — garde le rythme.",
            tone="encouragement",
        )
    if isinstance(delta, int) and delta <= -2:
        return _ok(
            "Rythme en baisse vs la semaine passée — la prochaine séance compte.",
            tone="neutral",
        )

    if count == 1:
        return _ok(
            "Premier passage cette semaine — un deuxième solidifierait.",
            tone="encouragement",
        )

    # 2-3 sessions, no anomaly, neutral delta
    return _ok(
        "Semaine régulière — garde ce rythme.",
        tone="encouragement",
    )
