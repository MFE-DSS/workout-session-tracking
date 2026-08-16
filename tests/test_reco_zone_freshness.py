"""Sb_24.next.reco — _zone_freshness_bonus tests.

Hard contract validated:
* Le gradient répond correctement à 0/1/2/3+ zones de chevauchement.
* Le scénario dogfooding push → pull → push doit produire un bonus
  négatif (overlap fort avec la N-2 session push).
* Le scénario sain push → pull → legs doit produire le bonus max.
* Aucune session récente → 0 (neutre).
* L'ancien _antagonist_bonus reste accessible pour les explanations.
"""
from __future__ import annotations

import pytest

from app.services.recommendation import (
    ANTAGONIST_BONUS_NONE,
    ANTAGONIST_BONUS_PARTIAL,
    ANTAGONIST_BONUS_PERFECT,
    RECENT_STRENGTH_SESSIONS_LOOKBACK,
    ZONE_FRESHNESS_BONUS_BASE,
    ZONE_FRESHNESS_BONUS_MIN,
    ZONE_FRESHNESS_BONUS_STEP,
    _antagonist_bonus,
    _zone_freshness_bonus,
)

# ---------------------------------------------------------------------------
# Gradient formula sanity
# ---------------------------------------------------------------------------


def test_zone_freshness_returns_zero_when_no_history():
    """Pas de session récente → 0 (neutre)."""
    assert _zone_freshness_bonus(["pecs"], []) == 0


def test_zone_freshness_no_overlap_returns_base():
    """0 zone partagée → bonus max."""
    out = _zone_freshness_bonus(
        ["pecs", "delt_lat", "triceps"],
        [["lats", "upper_back", "biceps"]],
    )
    assert out == ZONE_FRESHNESS_BONUS_BASE  # 15


def test_zone_freshness_one_overlap_decremented():
    """1 zone partagée → BASE - STEP."""
    out = _zone_freshness_bonus(
        ["pecs", "delt_lat", "triceps"],
        [["delt_lat", "lats", "biceps"]],
    )
    assert out == ZONE_FRESHNESS_BONUS_BASE - ZONE_FRESHNESS_BONUS_STEP  # 9


def test_zone_freshness_two_overlaps():
    """2 zones partagées → BASE - 2·STEP."""
    out = _zone_freshness_bonus(
        ["pecs", "delt_lat", "triceps"],
        [["pecs", "delt_lat", "biceps"]],
    )
    assert out == ZONE_FRESHNESS_BONUS_BASE - 2 * ZONE_FRESHNESS_BONUS_STEP  # 3


def test_zone_freshness_three_overlaps_bottoms_out():
    """3 zones partagées → BASE - 3·STEP = -3, mais clamped à MIN=-6
    on s'attend à -3 (au-dessus du MIN)."""
    out = _zone_freshness_bonus(
        ["pecs", "delt_lat", "triceps"],
        [["pecs", "delt_lat", "triceps"]],
    )
    expected = max(ZONE_FRESHNESS_BONUS_MIN, ZONE_FRESHNESS_BONUS_BASE - 3 * ZONE_FRESHNESS_BONUS_STEP)
    assert out == expected  # -3


def test_zone_freshness_huge_overlap_clamped_to_min():
    """Cas pathologique — 5+ zones partagées → clamp à MIN=-6."""
    out = _zone_freshness_bonus(
        ["pecs", "delt_lat", "triceps", "lats", "biceps", "core"],
        [["pecs", "delt_lat", "triceps", "lats", "biceps", "core"]],
    )
    assert out == ZONE_FRESHNESS_BONUS_MIN


# ---------------------------------------------------------------------------
# Scénario dogfooding : push → pull → push doit être pénalisé
# ---------------------------------------------------------------------------


def test_dogfood_scenario_push_pull_push_penalized():
    """User a fait :
        N-2 : push (pecs, delt_lat, triceps)
        N-1 : pull (lats, upper_back, biceps)
    Reco pour N : un template push doit voir overlap = 3 zones (push
    apparaît dans N-2) → bonus -3, vs un template legs qui voit
    overlap = 0 zone → bonus 15.
    Le legs gagne donc le tiebreaker de 18 points."""
    push_zones = ["pecs", "delt_lat", "triceps"]
    pull_zones = ["lats", "upper_back", "biceps"]
    history = [pull_zones, push_zones]  # most recent first

    push_score = _zone_freshness_bonus(push_zones, history)
    legs_score = _zone_freshness_bonus(["quads", "posterior", "calves"], history)

    assert push_score < legs_score
    delta = legs_score - push_score
    assert delta >= 15, (
        f"Le legs doit dominer le push d'au moins 15 points, "
        f"obtenu : legs={legs_score} push={push_score} delta={delta}"
    )


def test_dogfood_scenario_push_pull_legs_optimal():
    """Si le user fait push → pull et qu'on lui propose legs : aucune
    zone du legs n'apparaît dans l'union N-1/N-2 → bonus max."""
    push_zones = ["pecs", "delt_lat", "triceps"]
    pull_zones = ["lats", "upper_back", "biceps"]
    history = [pull_zones, push_zones]
    legs_zones = ["quads", "posterior", "calves"]

    assert _zone_freshness_bonus(legs_zones, history) == ZONE_FRESHNESS_BONUS_BASE


def test_constant_lookback_is_3():
    """Documentation du choix de la fenêtre N=3."""
    assert RECENT_STRENGTH_SESSIONS_LOOKBACK == 3


# ---------------------------------------------------------------------------
# Backward compat : _antagonist_bonus reste fonctionnel pour explanations
# ---------------------------------------------------------------------------


def test_legacy_antagonist_bonus_still_works_no_overlap():
    out = _antagonist_bonus(["pecs"], ["lats", "upper_back"])
    assert out == ANTAGONIST_BONUS_PERFECT


def test_legacy_antagonist_bonus_partial_overlap():
    out = _antagonist_bonus(["pecs", "delt_lat"], ["delt_lat", "lats"])
    assert out == ANTAGONIST_BONUS_PARTIAL


def test_legacy_antagonist_bonus_strong_overlap():
    out = _antagonist_bonus(["pecs", "delt_lat", "triceps"], ["pecs", "delt_lat"])
    assert out == ANTAGONIST_BONUS_NONE


def test_legacy_antagonist_bonus_empty_safe():
    """Si la dernière session n'a pas de zones → 0 (pas d'erreur)."""
    assert _antagonist_bonus(["pecs"], []) == ANTAGONIST_BONUS_NONE
    assert _antagonist_bonus([], ["lats"]) == ANTAGONIST_BONUS_NONE


# ---------------------------------------------------------------------------
# Paramétrique sur la fonction gradient
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("overlap_count, expected_score", [
    (0, ZONE_FRESHNESS_BONUS_BASE),
    (1, ZONE_FRESHNESS_BONUS_BASE - ZONE_FRESHNESS_BONUS_STEP),
    (2, ZONE_FRESHNESS_BONUS_BASE - 2 * ZONE_FRESHNESS_BONUS_STEP),
    (3, max(ZONE_FRESHNESS_BONUS_MIN, ZONE_FRESHNESS_BONUS_BASE - 3 * ZONE_FRESHNESS_BONUS_STEP)),
])
def test_gradient_formula_parametric(overlap_count, expected_score):
    """Vérifie la formule pour chaque overlap_count attendu."""
    template_zones = ["pecs", "delt_lat", "triceps", "lats", "biceps"]
    recent = [list(template_zones[:overlap_count])] if overlap_count else [["core"]]
    if overlap_count == 0:
        recent = [["core"]]  # une zone unique non chevauchante
    out = _zone_freshness_bonus(template_zones, recent)
    assert out == expected_score
