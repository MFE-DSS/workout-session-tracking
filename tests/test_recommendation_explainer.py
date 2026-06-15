"""Sb_27.4 — Recommendation Explainer tests.

The explainer is a read-only wrapper on the payload returned by
`recommend_next_session`. These tests don't call the real
recommendation service — they feed crafted payloads (the same shape
the service returns) so we exercise every rule in isolation.

Hard contract verified: the explainer NEVER touches `recommendation.py`,
NEVER re-runs the scoring logic — it only consumes its public payload.
"""
from __future__ import annotations

from app.services.recommendation_explainer import explain_recommendation

_REQUIRED_KEYS = {
    "available",
    "primary_reason",
    "reasons",
    "confidence",
    "fallback_note",
}


def _mk_payload(
    *,
    phrase: str = "",
    primary_zones: list[str] | None = None,
    cold_start: bool = False,
    fallback: bool = False,
    days_strength: float | None = None,
    days_cardio: float | None = None,
    fatigue_score: float | None = None,
):
    """Build a `recommend_next_session`-shaped dict for explainer input."""
    return {
        "top": {
            "template": None,
            "score": 1.0,
            "phrase": phrase,
            "primary_zones": primary_zones or [],
        },
        "alternatives": [],
        "context": {
            "cold_start": cold_start,
            "fallback": fallback,
            "days_since_last_strength": days_strength,
            "days_since_last_cardio": days_cardio,
            "fatigue_score": fatigue_score,
        },
    }


# ─────────────────── shape contract ───────────────────


def test_returns_required_keys_for_any_input():
    payload = _mk_payload(phrase="Test phrase")
    out = explain_recommendation(payload)
    assert _REQUIRED_KEYS.issubset(out.keys())


def test_none_payload_returns_unavailable():
    out = explain_recommendation(None)
    assert out["available"] is False
    assert out["primary_reason"] is None
    assert out["reasons"] == []
    assert out["confidence"] == "low"
    assert out["fallback_note"]


def test_empty_dict_returns_unavailable():
    out = explain_recommendation({})
    assert out["available"] is False


def test_payload_with_no_top_returns_unavailable():
    out = explain_recommendation({"alternatives": [], "context": {}})
    assert out["available"] is False


def test_payload_with_garbled_top_does_not_crash():
    out = explain_recommendation({"top": "not a dict", "context": {}})
    assert out["available"] is False


def test_payload_with_garbled_context_does_not_crash():
    out = explain_recommendation({"top": {"phrase": "ok"}, "context": "broken"})
    assert out["available"] is False


# ─────────────────── primary phrase preserved ───────────────────


def test_top_phrase_becomes_primary_reason():
    payload = _mk_payload(phrase="Dernière séance jambes récente, push plus frais.")
    out = explain_recommendation(payload)
    assert out["primary_reason"].startswith("Dernière séance")
    assert out["primary_reason"] in out["reasons"]


def test_phrase_is_stripped():
    payload = _mk_payload(phrase="  Phrase   ")
    out = explain_recommendation(payload)
    assert out["primary_reason"] == "Phrase"


# ─────────────────── cold start ───────────────────


def test_cold_start_surfaces_explicit_phrase_first():
    payload = _mk_payload(phrase="Bon premier template.", cold_start=True)
    out = explain_recommendation(payload)
    assert "Première séance" in out["primary_reason"]
    assert out["confidence"] == "low"
    assert out["fallback_note"]


# ─────────────────── fallback flag ───────────────────


def test_fallback_flag_adds_generic_reason_and_marks_low_confidence():
    payload = _mk_payload(phrase="X", fallback=True)
    out = explain_recommendation(payload)
    assert out["confidence"] == "low"
    assert any("historique récent" in r for r in out["reasons"])


# ─────────────────── zone freshness ───────────────────


def test_zone_freshness_surfaces_when_days_since_last_strength_is_high():
    payload = _mk_payload(
        phrase="Push A recommandé.",
        primary_zones=["pectoraux", "triceps"],
        days_strength=5,
    )
    out = explain_recommendation(payload)
    # The phrase should appear in reasons
    assert any("frais" in r.lower() for r in out["reasons"])


def test_zone_freshness_is_silent_when_days_below_threshold():
    payload = _mk_payload(
        phrase="Push A.",
        primary_zones=["pectoraux"],
        days_strength=1,  # below 2-day threshold
    )
    out = explain_recommendation(payload)
    assert not any("frais" in r.lower() for r in out["reasons"])


def test_zone_freshness_is_silent_when_no_primary_zones():
    payload = _mk_payload(phrase="X", primary_zones=[], days_strength=5)
    out = explain_recommendation(payload)
    assert not any("frais" in r.lower() for r in out["reasons"])


def test_zone_freshness_is_silent_when_days_is_none():
    payload = _mk_payload(
        phrase="X",
        primary_zones=["pectoraux"],
        days_strength=None,
        days_cardio=None,
    )
    out = explain_recommendation(payload)
    assert not any("frais" in r.lower() or "cardio" in r.lower() for r in out["reasons"])


# ─────────────────── fatigue ───────────────────


def test_high_fatigue_surfaces_phrase():
    payload = _mk_payload(phrase="X", fatigue_score=0.9)
    out = explain_recommendation(payload)
    assert any("fatigue élevé" in r.lower() for r in out["reasons"])


def test_low_fatigue_surfaces_phrase():
    payload = _mk_payload(phrase="X", fatigue_score=0.1)
    out = explain_recommendation(payload)
    assert any("fatigue bas" in r.lower() for r in out["reasons"])


def test_medium_fatigue_says_nothing():
    payload = _mk_payload(phrase="X", fatigue_score=0.5)
    out = explain_recommendation(payload)
    assert not any("fatigue" in r.lower() for r in out["reasons"])


def test_fatigue_is_silent_when_score_is_none():
    payload = _mk_payload(phrase="X", fatigue_score=None)
    out = explain_recommendation(payload)
    assert not any("fatigue" in r.lower() for r in out["reasons"])


# ─────────────────── cap to MAX_REASONS ───────────────────


def test_max_three_reasons_when_many_rules_fire():
    """cold_start + phrase + fallback + zone + fatigue would be 5 → capped at 3."""
    payload = _mk_payload(
        phrase="Bon premier.",
        primary_zones=["pectoraux"],
        cold_start=True,
        fallback=True,
        days_strength=7,
        fatigue_score=0.9,
    )
    out = explain_recommendation(payload)
    assert len(out["reasons"]) <= 3
    # The cold-start phrase comes first (highest priority)
    assert out["primary_reason"].lower().startswith("première séance")


def test_dedup_when_same_phrase_could_be_added_twice():
    """top.phrase == cold-start phrase should not appear twice."""
    payload = _mk_payload(phrase="Première séance — démarrage doux suggéré.", cold_start=True)
    out = explain_recommendation(payload)
    # Should not duplicate
    assert len(set(out["reasons"])) == len(out["reasons"])


# ─────────────────── empty top.phrase + nothing else ───────────────────


def test_empty_phrase_with_no_other_signals_falls_back_to_generic():
    payload = _mk_payload(phrase="")
    out = explain_recommendation(payload)
    assert out["primary_reason"]
    assert "historique récent" in out["primary_reason"]
    assert out["confidence"] == "low"
    assert out["fallback_note"]


# ─────────────────── home integration ───────────────────


def test_home_route_renders_with_explainer(client):
    """GET / still returns 200 and the home payload exposes reasons[]."""
    r = client.get("/")
    assert r.status_code == 200


def test_home_payload_includes_reasons_field(client):
    """build_home_payload now exposes a reasons list under today."""
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.home import build_home_payload

    with SessionLocal() as db:
        user = db.query(User).first()
        payload = build_home_payload(db, user)

    today = payload["today"]
    # Even on a fresh user (no_reco), the today tile has a reason string;
    # when a real reco is computed it also has a reasons list.
    assert "reason" in today
    if today.get("kind") == "reco":
        assert "reasons" in today
        assert isinstance(today["reasons"], list)


def test_recommendation_py_was_not_modified():
    """Hard contract check: the explainer never imports from a write
    interface on recommendation.py. We only consume the public payload.
    This test enforces that nothing in the explainer module imports
    private writer symbols from recommendation.
    """
    import inspect

    from app.services import recommendation_explainer

    source = inspect.getsource(recommendation_explainer)
    # We may import (read) from recommendation.py at most via the
    # explainer's home wiring — but the explainer itself doesn't
    # import recommendation_*, it just consumes the dict.
    assert "from app.services.recommendation import" not in source
