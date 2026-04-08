"""Unit tests for the pure delta functions.

The rule is in docs/PRODUCT_SPEC.md. These tests exercise each
branch so any future refactor is caught early.
"""
from __future__ import annotations


def test_delta_none_when_all_inputs_missing():
    from app.services.delta import compute_delta

    assert compute_delta(None, None, None, None, None, None) is None


def test_delta_none_when_prior_has_nothing_comparable():
    from app.services.delta import compute_delta

    assert compute_delta(60.0, 10, 80, None, None, None) is None


def test_delta_weight_only_when_reps_missing_on_one_side():
    from app.services.delta import compute_delta, format_delta

    d = compute_delta(62.5, None, None, 60.0, None, None)
    assert d is not None
    assert d.weight_delta == 2.5
    assert d.reps_delta is None
    assert d.score_trend is None
    assert format_delta(d) == "+2.5 kg"


def test_delta_reps_only_when_weight_missing_on_one_side():
    from app.services.delta import compute_delta, format_delta

    d = compute_delta(None, 12, None, None, 10, None)
    assert d is not None
    assert d.weight_delta is None
    assert d.reps_delta == 2
    assert format_delta(d) == "+2 reps"


def test_delta_full_triplet_goes_up():
    from app.services.delta import compute_delta, format_delta

    d = compute_delta(62.5, 10, 100, 60.0, 8, 80)
    assert d.weight_delta == 2.5
    assert d.reps_delta == 2
    assert d.score_trend == "up"
    assert format_delta(d) == "+2.5 kg · +2 reps · score en hausse"


def test_delta_full_triplet_goes_down():
    from app.services.delta import compute_delta, format_delta

    d = compute_delta(50.0, 6, 50, 60.0, 10, 100)
    assert d.weight_delta == -10.0
    assert d.reps_delta == -4
    assert d.score_trend == "down"
    assert format_delta(d) == "-10 kg · -4 reps · score en baisse"


def test_delta_flat_weight_and_reps():
    from app.services.delta import compute_delta, format_delta

    d = compute_delta(60.0, 10, 80, 60.0, 10, 80)
    assert d.weight_delta == 0.0
    assert d.reps_delta == 0
    assert d.score_trend == "flat"
    assert format_delta(d) == "= kg · = reps · score stable"


def test_delta_integer_weight_has_no_trailing_zero():
    from app.services.delta import compute_delta, format_delta

    d = compute_delta(62.0, 10, None, 60.0, 10, None)
    # 62.0 - 60.0 == 2.0 -> must render "+2 kg", not "+2.0 kg"
    assert format_delta(d).startswith("+2 kg")


def test_delta_format_none_returns_none():
    from app.services.delta import format_delta

    assert format_delta(None) is None
