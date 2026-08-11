"""Sb_FATIGUE_SCALE_FIX_01 — the fatigue scale boundary.

`behavioral.compute_behavioral_state` produces `fatigue_score` on a **0–100**
scale (good 20 / flat 50 / fatigued 80). `recommendation.py` forwards it
verbatim into `context["fatigue_score"]`. The explainer compared that value
against 0.7 and 0.2 as if it were 0–1, so:

* the "fatigue élevée" branch fired for **every** real value (20, 50 and 80 are
  all >= 0.7) — the user was told they were exhausted no matter what;
* the "fatigue basse" branch was **unreachable** unless the value happened to
  be in [0, 0.2], which `behavioral` cannot produce;
* the one thing that *did* land in that window was `0.0` — the value
  `recommendation.py` substitutes when `compute_behavioral_state` **raises** —
  so a computation failure was rendered as "you're fresh, go push".

These tests pin the conversion, the reachability of both bands, and the refusal
to turn missing or malformed data into good news. `behavioral.py` and
`recommendation.py` are not modified.
"""
from __future__ import annotations

import pytest

from app.services.behavioral import (
    _CONCENTRATION_FATIGUE,
    _DEFAULT_CONCENTRATION_FATIGUE,
    _DEFAULT_FATIGUE,
    _DEFAULT_GLOBAL_STATE_FATIGUE,
    _GLOBAL_STATE_FATIGUE,
    compute_session_fatigue,
    compute_weighted_fatigue,
)
from app.services.recommendation_explainer import (
    FATIGUE_HIGH,
    FATIGUE_LOW,
    FATIGUE_RAW_MIN_PRODUCIBLE,
    FATIGUE_RAW_SCALE_MAX,
    _fatigue_reason,
    explain_recommendation,
    normalize_fatigue_score,
)

HIGH_PHRASE = "Niveau de fatigue élevé — séance légère privilégiée."
LOW_PHRASE = "Niveau de fatigue bas — bon moment pour pousser."


# ---------------------------------------------------------------------------
# The producer's real range — derived, so the constant cannot drift
# ---------------------------------------------------------------------------


def test_producible_floor_is_derived_from_behavioral_not_guessed():
    """`FATIGUE_RAW_MIN_PRODUCIBLE` must equal what `behavioral` can emit.

    compute_session_fatigue = (global_state + concentration) / 2. The floor is
    therefore the mean of the two dicts' minima (defaults included, since an
    unknown key falls back to them).
    """
    gs_min = min([*_GLOBAL_STATE_FATIGUE.values(), _DEFAULT_GLOBAL_STATE_FATIGUE])
    co_min = min([*_CONCENTRATION_FATIGUE.values(), _DEFAULT_CONCENTRATION_FATIGUE])
    assert FATIGUE_RAW_MIN_PRODUCIBLE == (gs_min + co_min) / 2


def test_session_fatigue_never_leaves_the_declared_band():
    """Every combination of the closed vocabularies, plus unknown keys."""
    gs_keys = [*_GLOBAL_STATE_FATIGUE, None, "nonsense"]
    co_keys = [*_CONCENTRATION_FATIGUE, None, "nonsense"]
    gs_max = max([*_GLOBAL_STATE_FATIGUE.values(), _DEFAULT_GLOBAL_STATE_FATIGUE])
    co_max = max([*_CONCENTRATION_FATIGUE.values(), _DEFAULT_CONCENTRATION_FATIGUE])
    ceiling = (gs_max + co_max) / 2

    for gs in gs_keys:
        for co in co_keys:
            value = compute_session_fatigue(global_state=gs, concentration=co)
            assert FATIGUE_RAW_MIN_PRODUCIBLE <= value <= ceiling, (gs, co)


def test_weighted_fatigue_stays_inside_the_band():
    """It is a convex combination, so it cannot escape its inputs' range."""
    floor = FATIGUE_RAW_MIN_PRODUCIBLE
    ceiling = 75.0
    for scores in ([floor], [ceiling], [floor, ceiling], [ceiling, floor],
                   [floor, ceiling, floor], [ceiling, floor, ceiling]):
        value = compute_weighted_fatigue(list(scores))
        assert floor <= value <= ceiling, scores


def test_no_history_yields_the_flat_default_not_zero():
    """The empty case is 50 ("flat"), which is exactly why 0.0 is a sentinel."""
    assert compute_weighted_fatigue([]) == _DEFAULT_FATIGUE
    assert _DEFAULT_FATIGUE > FATIGUE_RAW_MIN_PRODUCIBLE


def test_zero_is_not_producible_by_behavioral():
    """The premise the whole sentinel rule rests on."""
    assert FATIGUE_RAW_MIN_PRODUCIBLE > 0.0


# ---------------------------------------------------------------------------
# Threshold alignment with the (unmodifiable) recommendation engine
# ---------------------------------------------------------------------------


def test_high_band_matches_the_recommendation_engine_threshold():
    """0.7 is not an invented number: it is 70/100, the engine's own cut.

    `recommendation.py` filters templates on `FATIGUE_HIGH_THRESHOLD = 70` on
    the raw 0–100 scale. After normalisation the explainer must call "high
    fatigue" exactly what the engine already treats as high fatigue.
    """
    from app.services.recommendation import FATIGUE_HIGH_THRESHOLD

    assert FATIGUE_HIGH * FATIGUE_RAW_SCALE_MAX == FATIGUE_HIGH_THRESHOLD


def test_low_band_matches_the_producer_good_anchor():
    """0.2 is not invented either: it is the "good" global-state value / 100.

    Saying "fatigue basse" therefore means precisely "the athlete reported
    feeling good", which is a statement the data supports.
    """
    assert FATIGUE_LOW * FATIGUE_RAW_SCALE_MAX == _GLOBAL_STATE_FATIGUE["good"]
    assert FATIGUE_LOW < FATIGUE_HIGH


# ---------------------------------------------------------------------------
# The conversion table required by the spec
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(("raw", "expected"), [
    (0, None),          # recommendation.py's failure sentinel — NOT "fresh"
    (15, 0.15),         # the producible floor
    (20, 0.2),          # behavioral "good"
    (50, 0.5),          # behavioral "flat" / no-history default
    (70, 0.7),          # engine's high-fatigue cut
    (80, 0.8),          # behavioral "fatigued"
    (100, 1.0),         # top of the declared scale
])
def test_conversion_table(raw, expected):
    assert normalize_fatigue_score(raw) == expected


@pytest.mark.parametrize("raw", [
    None, "80", "", [], {}, (), object(), True, False,
    float("nan"), float("inf"), float("-inf"),
    -1, -0.1, 100.1, 101, 1000,
])
def test_unusable_values_yield_none(raw):
    assert normalize_fatigue_score(raw) is None


def test_booleans_are_rejected_despite_being_ints():
    """`True` is an `int`; unguarded it would normalise to 0.01 → "fresh"."""
    assert isinstance(True, int)
    assert normalize_fatigue_score(True) is None
    assert normalize_fatigue_score(False) is None


def test_conversion_is_bounded_to_the_unit_interval():
    for raw in (15, 20, 37.5, 50, 70, 80, 99.9, 100):
        value = normalize_fatigue_score(raw)
        assert value is not None
        assert 0.0 <= value <= 1.0


# ---------------------------------------------------------------------------
# What the user is actually told
# ---------------------------------------------------------------------------


def test_default_fifty_does_not_become_high_fatigue():
    """The whole point: the flat default used to read as "fatigue élevée"."""
    assert _fatigue_reason({"fatigue_score": _DEFAULT_FATIGUE}) is None


def test_medium_fatigue_emits_no_extreme_statement():
    for raw in (40, 50, 60, 69.9):
        assert _fatigue_reason({"fatigue_score": raw}) is None, raw


def test_high_fatigue_emits_the_light_session_statement():
    for raw in (70, 75, 80, 100):
        assert _fatigue_reason({"fatigue_score": raw}) == HIGH_PHRASE, raw


def test_low_fatigue_branch_is_reachable_from_real_producer_values():
    """It was unreachable before: `behavioral` cannot emit <= 0.2 raw.

    The values below are genuinely producible — 15 is good state + high
    concentration, 20 is the "good" global-state anchor.
    """
    assert _fatigue_reason({"fatigue_score": 15}) == LOW_PHRASE
    assert _fatigue_reason({"fatigue_score": 20}) == LOW_PHRASE
    genuine_floor = compute_session_fatigue(global_state="good", concentration="high")
    assert _fatigue_reason({"fatigue_score": genuine_floor}) == LOW_PHRASE


def test_failure_sentinel_does_not_become_fresh():
    """`recommendation.py` writes 0.0 when `compute_behavioral_state` raises.

    That is a computation failure, not a measurement. It must produce silence,
    never "bon moment pour pousser".
    """
    reason = _fatigue_reason({"fatigue_score": 0.0})
    assert reason is None
    assert reason != LOW_PHRASE


def test_missing_and_malformed_do_not_become_fresh():
    for raw in (None, "low", [], True, float("nan"), -5):
        assert _fatigue_reason({"fatigue_score": raw}) is None, raw


def test_absent_key_is_silent():
    assert _fatigue_reason({}) is None


# ---------------------------------------------------------------------------
# End to end through the public wrapper
# ---------------------------------------------------------------------------


def _payload(fatigue_score):
    return {
        "top": {"template": None, "score": 1.0, "phrase": "X", "primary_zones": []},
        "alternatives": [],
        "context": {"cold_start": False, "fatigue_score": fatigue_score},
    }


def test_wrapper_reports_high_fatigue_for_a_fatigued_athlete():
    out = explain_recommendation(_payload(80))
    assert HIGH_PHRASE in out["reasons"]


def test_wrapper_reports_low_fatigue_for_a_fresh_athlete():
    out = explain_recommendation(_payload(20))
    assert LOW_PHRASE in out["reasons"]


def test_wrapper_is_silent_on_the_flat_default():
    out = explain_recommendation(_payload(50))
    assert not any("fatigue" in r.lower() for r in out["reasons"])


def test_wrapper_is_silent_on_the_failure_sentinel():
    out = explain_recommendation(_payload(0.0))
    assert not any("fatigue" in r.lower() for r in out["reasons"])


def test_other_explanation_rules_are_unchanged():
    """The fatigue fix must not disturb the neighbouring rules."""
    payload = {
        "top": {"template": None, "score": 1.0,
                "phrase": "Séance poussée recommandée.", "primary_zones": []},
        "alternatives": [],
        "context": {"cold_start": True, "fallback": True, "fatigue_score": 50},
    }
    out = explain_recommendation(payload)
    assert out["available"] is True
    assert out["confidence"] == "low"
    assert out["reasons"][0].lower().startswith("première séance")
    assert "Séance poussée recommandée." in out["reasons"]
    assert len(out["reasons"]) <= 3


def test_wrapper_still_degrades_gracefully_on_a_broken_payload():
    for payload in (None, {}, {"top": None}, {"top": {}, "context": "nope"}):
        out = explain_recommendation(payload)
        assert isinstance(out, dict)
        assert "available" in out
