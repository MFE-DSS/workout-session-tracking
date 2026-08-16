"""Sb_24.2 — implicit signal classifier tests (Sx_24 §D).

Covers the 5 labels, edge cases (None values, < MIN_WORK_SETS),
determinism, and the score contribution mapping.
"""
from __future__ import annotations

import pytest

from app.services.implicit_signal import (
    LABEL_SCORE_CONTRIBUTION,
    MIN_WORK_SETS,
    ImplicitLabel,
    WorkSetPoint,
    detect_intra_set_label,
)

# ---------------------------------------------------------------------------
# Sanity
# ---------------------------------------------------------------------------


def test_enum_has_five_values():
    assert len(ImplicitLabel) == 5
    assert {v.value for v in ImplicitLabel} == {
        "reserve_probable",
        "trajectoire_coherente",
        "pyramidal_ascendant",
        "pyramidal_descendant",
        "incoherent",
    }


def test_contributions_cover_all_labels():
    assert set(LABEL_SCORE_CONTRIBUTION) == set(ImplicitLabel)
    # Order : reserve < incoherent < pyramidal_asc < pyramidal_desc < coherente
    assert LABEL_SCORE_CONTRIBUTION[ImplicitLabel.RESERVE_PROBABLE] == 30
    assert LABEL_SCORE_CONTRIBUTION[ImplicitLabel.INCOHERENT] == 50
    assert LABEL_SCORE_CONTRIBUTION[ImplicitLabel.PYRAMIDAL_ASCENDANT] == 70
    assert LABEL_SCORE_CONTRIBUTION[ImplicitLabel.PYRAMIDAL_DESCENDANT] == 75
    assert LABEL_SCORE_CONTRIBUTION[ImplicitLabel.TRAJECTOIRE_COHERENTE] == 90


def test_min_work_sets_is_3():
    assert MIN_WORK_SETS == 3


# ---------------------------------------------------------------------------
# Edge cases — below threshold
# ---------------------------------------------------------------------------


def test_zero_sets_returns_none():
    assert detect_intra_set_label([]) is None


def test_two_sets_returns_none():
    """< MIN_WORK_SETS = signal too poor."""
    assert detect_intra_set_label([(80, 10), (80, 8)]) is None


# ---------------------------------------------------------------------------
# Trajectoire cohérente — the canonical hypertrophy drop-off
# ---------------------------------------------------------------------------


def test_trajectoire_coherente_classic_drop_off():
    """80kg×10, 80kg×8, 80kg×6 — the textbook intent-rich set."""
    out = detect_intra_set_label([(80, 10), (80, 8), (80, 6)])
    assert out == ImplicitLabel.TRAJECTOIRE_COHERENTE


def test_trajectoire_coherente_small_decrease():
    """80kg×10, 80kg×10, 80kg×9 — last set lower → drop is real even if small."""
    out = detect_intra_set_label([(80, 10), (80, 10), (80, 9)])
    assert out == ImplicitLabel.TRAJECTOIRE_COHERENTE


def test_trajectoire_coherente_four_sets():
    out = detect_intra_set_label([(80, 12), (80, 10), (80, 8), (80, 6)])
    assert out == ImplicitLabel.TRAJECTOIRE_COHERENTE


# ---------------------------------------------------------------------------
# Réserve probable — effort flat or even increasing
# ---------------------------------------------------------------------------


def test_reserve_probable_flat_3x10():
    """3 sets perfectly equal — pure flat trajectory.
    Per spec §D.1 verbatim, this falls under reserve_probable."""
    out = detect_intra_set_label([(60, 10), (60, 10), (60, 10)])
    assert out == ImplicitLabel.RESERVE_PROBABLE


def test_reserve_probable_reps_climbing():
    """Reps go UP between sets — suspicious of submaximal first sets."""
    out = detect_intra_set_label([(60, 8), (60, 9), (60, 10)])
    assert out == ImplicitLabel.RESERVE_PROBABLE


def test_reserve_probable_both_climbing():
    """Both weight and reps go up — definitely not pushing the first sets."""
    out = detect_intra_set_label([(60, 8), (65, 9), (70, 10)])
    assert out == ImplicitLabel.RESERVE_PROBABLE


# ---------------------------------------------------------------------------
# Pyramidal ascendant — ramp up
# ---------------------------------------------------------------------------


def test_pyramidal_ascendant_weight_up_reps_down():
    """60kg×12, 70kg×10, 80kg×8 — classic ramping strategy."""
    out = detect_intra_set_label([(60, 12), (70, 10), (80, 8)])
    assert out == ImplicitLabel.PYRAMIDAL_ASCENDANT


def test_pyramidal_ascendant_weight_up_reps_constant():
    """Weight up, reps stay the same — still a ramp."""
    out = detect_intra_set_label([(60, 8), (70, 8), (80, 8)])
    assert out == ImplicitLabel.PYRAMIDAL_ASCENDANT


# ---------------------------------------------------------------------------
# Pyramidal descendant — drop-set strategy
# ---------------------------------------------------------------------------


def test_pyramidal_descendant_weight_down_reps_up():
    """80kg×6, 70kg×8, 60kg×10 — drop-set."""
    out = detect_intra_set_label([(80, 6), (70, 8), (60, 10)])
    assert out == ImplicitLabel.PYRAMIDAL_DESCENDANT


def test_pyramidal_descendant_weight_down_reps_constant():
    out = detect_intra_set_label([(80, 8), (70, 8), (60, 8)])
    assert out == ImplicitLabel.PYRAMIDAL_DESCENDANT


# ---------------------------------------------------------------------------
# Incohérent — oscillations
# ---------------------------------------------------------------------------


def test_incoherent_oscillating_weight():
    """80→70→80 — pas de direction nette, ce n'est aucun des 4 cas."""
    out = detect_intra_set_label([(80, 8), (70, 10), (80, 8)])
    assert out == ImplicitLabel.INCOHERENT


def test_incoherent_mixed_signals():
    """Weight up then down, reps random."""
    out = detect_intra_set_label([(70, 8), (80, 12), (70, 6)])
    assert out == ImplicitLabel.INCOHERENT


# ---------------------------------------------------------------------------
# Bodyweight (weight=None) — uniform constant + reps discriminates
# ---------------------------------------------------------------------------


def test_bodyweight_constant_reps_treated_as_reserve():
    """Pullups bodyweight × 3 sets of 10 — pure flat → reserve_probable."""
    out = detect_intra_set_label([(None, 10), (None, 10), (None, 10)])
    assert out == ImplicitLabel.RESERVE_PROBABLE


def test_bodyweight_decreasing_reps_is_trajectoire_coherente():
    """Pullups bodyweight: 10, 8, 6 → drop-off cohérent."""
    out = detect_intra_set_label([(None, 10), (None, 8), (None, 6)])
    assert out == ImplicitLabel.TRAJECTOIRE_COHERENTE


# ---------------------------------------------------------------------------
# None values handling
# ---------------------------------------------------------------------------


def test_none_reps_treated_as_zero():
    out = detect_intra_set_label([(60, None), (60, None), (60, None)])
    # All zeros = flat → reserve_probable per spec
    assert out == ImplicitLabel.RESERVE_PROBABLE


def test_mixed_none_and_value():
    """An exotic mix — none reps then non-none. Treated coherently
    via the 0 coercion (None=0)."""
    out = detect_intra_set_label([(60, None), (60, 5), (60, 8)])
    # weights flat, reps 0, 5, 8 → both eq_or_inc → reserve_probable
    assert out == ImplicitLabel.RESERVE_PROBABLE


# ---------------------------------------------------------------------------
# Determinism — same input → same output, every time
# ---------------------------------------------------------------------------


def test_determinism():
    """The persist-once contract (spec §C, §D.2) hinges on this: the
    classifier MUST be a pure function."""
    inputs = [(80, 10), (80, 8), (80, 6)]
    for _ in range(20):
        assert detect_intra_set_label(inputs) == ImplicitLabel.TRAJECTOIRE_COHERENTE


def test_input_not_mutated():
    """A pure function never touches its inputs."""
    inputs = [(80, 10), (80, 8), (80, 6)]
    snapshot = list(inputs)
    _ = detect_intra_set_label(inputs)
    assert inputs == snapshot


# ---------------------------------------------------------------------------
# Input shape compatibility — accept ORM rows, tuples, WorkSetPoint
# ---------------------------------------------------------------------------


def test_accepts_workset_point_dataclass():
    points = [
        WorkSetPoint(weight_kg=80, reps=10),
        WorkSetPoint(weight_kg=80, reps=8),
        WorkSetPoint(weight_kg=80, reps=6),
    ]
    assert detect_intra_set_label(points) == ImplicitLabel.TRAJECTOIRE_COHERENTE


def test_accepts_orm_duck_typing():
    """An object with .weight_kg and .reps attributes is accepted."""
    from unittest.mock import MagicMock
    sets = []
    for w, r in [(80, 10), (80, 8), (80, 6)]:
        m = MagicMock()
        m.weight_kg = w
        m.reps = r
        sets.append(m)
    assert detect_intra_set_label(sets) == ImplicitLabel.TRAJECTOIRE_COHERENTE


# ---------------------------------------------------------------------------
# Parametric — quick regression battery
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("sets, expected", [
    # 3-set classics
    ([(80, 10), (80, 8), (80, 6)], ImplicitLabel.TRAJECTOIRE_COHERENTE),
    ([(60, 10), (60, 10), (60, 10)], ImplicitLabel.RESERVE_PROBABLE),
    ([(60, 8), (70, 8), (80, 8)], ImplicitLabel.PYRAMIDAL_ASCENDANT),
    ([(80, 8), (70, 8), (60, 8)], ImplicitLabel.PYRAMIDAL_DESCENDANT),
    ([(80, 8), (70, 10), (80, 8)], ImplicitLabel.INCOHERENT),
    # 5-set variants
    ([(80, 12), (80, 10), (80, 8), (80, 8), (80, 6)], ImplicitLabel.TRAJECTOIRE_COHERENTE),
    ([(60, 6), (70, 6), (80, 5), (85, 4), (90, 3)], ImplicitLabel.PYRAMIDAL_ASCENDANT),
])
def test_parametric_battery(sets, expected):
    assert detect_intra_set_label(sets) == expected
