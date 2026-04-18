"""Tests for app.services.hints (Sb_08 — 2 active-card rules)."""
from __future__ import annotations

from types import SimpleNamespace


def _se(work_sets: list[dict]):
    """Build a lightweight SessionExercise stand-in with set_logs."""
    set_logs = [
        SimpleNamespace(
            kind="work", set_index=i + 1,
            weight_kg=w.get("weight_kg"), reps=w.get("reps"),
            completed=w.get("completed", False),
        )
        for i, w in enumerate(work_sets)
    ]
    return SimpleNamespace(set_logs=set_logs)


def test_hint_a_triggers_on_load_plus_15pct():
    from app.services.hints import compute_hints
    se = _se([{"weight_kg": 57.5, "reps": 10, "completed": False}])
    prior = {"first_set": {"weight_kg": 50.0, "reps": 10}, "sets": []}
    hints = compute_hints(se, prior)
    assert any(h.rule_code == "A" for h in hints)


def test_hint_a_silent_below_10pct():
    from app.services.hints import compute_hints
    se = _se([{"weight_kg": 54.0, "reps": 10}])
    prior = {"first_set": {"weight_kg": 50.0, "reps": 10}, "sets": []}
    assert not any(h.rule_code == "A" for h in compute_hints(se, prior))


def test_hint_a_silent_without_prior():
    from app.services.hints import compute_hints
    se = _se([{"weight_kg": 80.0, "reps": 10}])
    assert compute_hints(se, None) == []


def test_hint_b_triggers_on_reps_drop():
    from app.services.hints import compute_hints
    se = _se([
        {"weight_kg": 50, "reps": 10},
        {"weight_kg": 50, "reps": 6},  # -4 vs prior same index
    ])
    prior = {
        "first_set": {"weight_kg": 50, "reps": 10},
        "sets": [
            {"set_index": 1, "reps": 10, "weight_kg": 50},
            {"set_index": 2, "reps": 10, "weight_kg": 50},
        ],
    }
    hints = compute_hints(se, prior)
    assert any(h.rule_code == "B" for h in hints)
    b = next(h for h in hints if h.rule_code == "B")
    assert b.set_index == 2


def test_hint_b_silent_when_reps_within_2():
    from app.services.hints import compute_hints
    se = _se([
        {"weight_kg": 50, "reps": 10},
        {"weight_kg": 50, "reps": 9},
    ])
    prior = {
        "first_set": {"weight_kg": 50, "reps": 10},
        "sets": [
            {"set_index": 1, "reps": 10},
            {"set_index": 2, "reps": 10},
        ],
    }
    assert not any(h.rule_code == "B" for h in compute_hints(se, prior))


def test_hints_both_a_and_b_can_coexist():
    from app.services.hints import compute_hints
    se = _se([
        {"weight_kg": 60, "reps": 10},  # +20%
        {"weight_kg": 60, "reps": 5},   # reps -5 vs prior set 2
    ])
    prior = {
        "first_set": {"weight_kg": 50, "reps": 10},
        "sets": [
            {"set_index": 1, "reps": 10},
            {"set_index": 2, "reps": 10},
        ],
    }
    codes = {h.rule_code for h in compute_hints(se, prior)}
    assert codes == {"A", "B"}


def test_hint_b_caps_at_one_per_card():
    from app.services.hints import compute_hints
    se = _se([
        {"weight_kg": 50, "reps": 5},
        {"weight_kg": 50, "reps": 5},
    ])
    prior = {
        "first_set": {"weight_kg": 50, "reps": 10},
        "sets": [
            {"set_index": 1, "reps": 10},
            {"set_index": 2, "reps": 10},
        ],
    }
    b_hints = [h for h in compute_hints(se, prior) if h.rule_code == "B"]
    assert len(b_hints) == 1


def test_compute_hints_empty_when_no_data():
    from app.services.hints import compute_hints
    se = _se([])
    assert compute_hints(se, None) == []
