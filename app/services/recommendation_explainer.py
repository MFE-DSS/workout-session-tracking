"""Sb_27.4 — Recommendation Explainer (read-only wrapper).

Consumes the dict returned by `app.services.recommendation.recommend_next_session`
and produces a small explanation payload the UI can render:

* `available`       — boolean
* `primary_reason`  — the single most relevant short reason (string or None)
* `reasons`         — list of 1..3 short reasons (deduped, ordered)
* `confidence`      — "ok" | "low" derived from the source payload
* `fallback_note`   — explicit "Non déductible" / cold start phrase if applicable

Contract (Sx_27 §11, §16 + OQ-4 verbatim):
* NEVER touches `recommendation.py` or any service in `scoring/`, `reco/`,
  `substitution.py`, `implicit_signal.py`, `quality_score.py`,
  `coach_report.py` — purely consumes the existing payload.
* NEVER re-runs the recommendation logic. Reads only the public fields
  already present in `reco_payload` (top, context, alternatives).
* NEVER invents a reason: if a field is missing/None we either skip the
  rule or surface an explicit "Non déductible" / fallback note.
* Phrases are deterministic (no LLM).

Public API:

    from app.services.recommendation_explainer import explain_recommendation
    explanation = explain_recommendation(reco_payload)
"""
from __future__ import annotations

from typing import Any

_MAX_REASONS = 3

_FALLBACK_PHRASE = "Recommandation basée sur ton historique récent."
_LOW_DATA_PHRASE = "Pas assez de données pour expliquer plus finement."
_COLD_START_PHRASE = "Première séance — démarrage doux suggéré."
_FALLBACK_NOTE = "Pas encore assez de données pour personnaliser."


def explain_recommendation(reco_payload: Any) -> dict[str, Any]:
    """Produce an explanation dict for the home/launcher UI.

    `reco_payload` is the dict returned by `recommend_next_session` or
    None. Any shape we don't recognise degrades gracefully — we surface
    a generic fallback, never crash.
    """
    if not isinstance(reco_payload, dict) or "top" not in reco_payload:
        return _empty(available=False)

    top = reco_payload.get("top") or {}
    context = reco_payload.get("context") or {}
    if not isinstance(top, dict) or not isinstance(context, dict):
        return _empty(available=False)

    reasons: list[str] = []
    confidence = "ok"
    fallback_note: str | None = None

    # ── Rule A: cold start (highest priority — context flag explicit)
    if context.get("cold_start") is True:
        reasons.append(_COLD_START_PHRASE)
        confidence = "low"
        fallback_note = _FALLBACK_NOTE

    # ── Rule B: existing top.phrase verbatim (deterministic, pre-computed
    # by recommendation.py — primary signal). Always included if present.
    phrase = _clean(top.get("phrase"))
    if phrase and phrase not in reasons:
        reasons.append(phrase)

    # ── Rule C: explicit fallback flag → generic explanation
    if context.get("fallback") is True:
        if _FALLBACK_PHRASE not in reasons:
            reasons.append(_FALLBACK_PHRASE)
        confidence = "low"

    # ── Rule D: zone-freshness derived from days_since_last_*
    zone_reason = _zone_freshness_reason(top, context)
    if zone_reason and zone_reason not in reasons:
        reasons.append(zone_reason)

    # ── Rule E: fatigue level (informational, never invents)
    fatigue_reason = _fatigue_reason(context)
    if fatigue_reason and fatigue_reason not in reasons:
        reasons.append(fatigue_reason)

    # Cap to MAX, keeping order (most-relevant first).
    reasons = reasons[:_MAX_REASONS]

    if not reasons:
        # Top exists but we have no narrative material at all.
        reasons = [_FALLBACK_PHRASE]
        confidence = "low"
        fallback_note = _FALLBACK_NOTE

    primary_reason = reasons[0]
    return {
        "available": True,
        "primary_reason": primary_reason,
        "reasons": reasons,
        "confidence": confidence,
        "fallback_note": fallback_note,
    }


# ───────── helpers (pure, no side effects) ─────────


def _empty(*, available: bool) -> dict[str, Any]:
    return {
        "available": available,
        "primary_reason": _FALLBACK_PHRASE if available else None,
        "reasons": [_FALLBACK_PHRASE] if available else [],
        "confidence": "low",
        "fallback_note": _FALLBACK_NOTE,
    }


def _clean(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip()


def _zone_freshness_reason(top: dict, context: dict) -> str | None:
    """Build a short zone-freshness reason from `days_since_last_*` + zones.

    Never invents : if `days_since_last_strength` is None and primary_zones
    is empty, we return None rather than fabricate "muscles frais".
    """
    primary_zones = top.get("primary_zones")
    if not isinstance(primary_zones, (list, tuple)) or not primary_zones:
        return None

    days_strength = context.get("days_since_last_strength")
    days_cardio = context.get("days_since_last_cardio")

    # We pick the longest "freshness" signal we have. Only surface it
    # if it's clearly meaningful (≥ 2 days) — otherwise the phrase is
    # noise.
    candidates = [
        (d, label)
        for d, label in (
            (days_strength, "strength"),
            (days_cardio, "cardio"),
        )
        if isinstance(d, (int, float)) and d >= 2
    ]
    if not candidates:
        return None
    days, label = max(candidates, key=lambda x: x[0])

    zones_text = ", ".join(str(z) for z in primary_zones[:2]).lower()
    if not zones_text:
        return None
    if label == "strength":
        return f"{zones_text.capitalize()} {int(days)} j sans muscu — frais à travailler."
    return f"{zones_text.capitalize()} {int(days)} j sans cardio — créneau idéal."


def _fatigue_reason(context: dict) -> str | None:
    """Surface a fatigue note only when the score is explicitly informative."""
    score = context.get("fatigue_score")
    if not isinstance(score, (int, float)):
        return None
    # Scale assumption (read from recommendation.py callers): higher = more fatigued.
    # We never tell the user a precise number — only a qualitative band,
    # and only when the band is meaningful enough to act on.
    if score >= 0.7:
        return "Niveau de fatigue élevé — séance légère privilégiée."
    if score <= 0.2:
        return "Niveau de fatigue bas — bon moment pour pousser."
    return None
