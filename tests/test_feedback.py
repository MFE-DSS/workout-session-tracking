"""Tests for compute_success_score in app.services.feedback.

All tests use MagicMock objects — no database required.
"""
from __future__ import annotations

from unittest.mock import MagicMock

from app.services.feedback import compute_success_score

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_set_log(set_index: int, kind: str = "work", completed: bool = True, reps=None):
    sl = MagicMock()
    sl.kind = kind
    sl.set_index = set_index
    sl.completed = completed
    sl.reps = reps
    return sl


def _make_rep_target(set_index: int, min_reps: int, max_reps: int):
    rt = MagicMock()
    rt.set_index = set_index
    rt.min_reps = min_reps
    rt.max_reps = max_reps
    return rt


def _make_session_exercise(set_logs):
    se = MagicMock()
    se.set_logs = set_logs
    return se


def _make_template_exercise(rep_targets):
    te = MagicMock()
    te.rep_targets = rep_targets
    return te


# ---------------------------------------------------------------------------
# Test 1: All sets at max reps → 100
# ---------------------------------------------------------------------------

def test_all_sets_at_max_reps():
    """3 completed work sets all at max → raw = 100*1.0 = 100 → snapped 100."""
    logs = [
        _make_set_log(1, reps=10),
        _make_set_log(2, reps=10),
        _make_set_log(3, reps=10),
    ]
    se = _make_session_exercise(logs)
    te = _make_template_exercise([
        _make_rep_target(1, 8, 10),
        _make_rep_target(2, 8, 10),
        _make_rep_target(3, 8, 10),
    ])
    assert compute_success_score(se, te) == 100


# ---------------------------------------------------------------------------
# Test 2: All sets in range → 80
# ---------------------------------------------------------------------------

def test_all_sets_in_range():
    """All sets at min_reps (in range, not at max) → mean=80, ratio=1 → raw=80 → 80."""
    logs = [
        _make_set_log(1, reps=8),
        _make_set_log(2, reps=8),
    ]
    se = _make_session_exercise(logs)
    te = _make_template_exercise([
        _make_rep_target(1, 8, 12),
        _make_rep_target(2, 8, 12),
    ])
    assert compute_success_score(se, te) == 80


# ---------------------------------------------------------------------------
# Test 3: All sets below range → 50
# ---------------------------------------------------------------------------

def test_all_sets_below_range():
    """All sets below min_reps → mean=50, ratio=1 → raw=50 → 50."""
    logs = [
        _make_set_log(1, reps=4),
        _make_set_log(2, reps=4),
    ]
    se = _make_session_exercise(logs)
    te = _make_template_exercise([
        _make_rep_target(1, 8, 12),
        _make_rep_target(2, 8, 12),
    ])
    assert compute_success_score(se, te) == 50


# ---------------------------------------------------------------------------
# Test 4: No completed sets → None
# ---------------------------------------------------------------------------

def test_no_completed_sets_returns_none():
    """No completed work sets → return None."""
    logs = [
        _make_set_log(1, completed=False, reps=None),
        _make_set_log(2, completed=False, reps=None),
    ]
    se = _make_session_exercise(logs)
    te = _make_template_exercise([_make_rep_target(1, 8, 12)])
    assert compute_success_score(se, te) is None


# ---------------------------------------------------------------------------
# Test 5: Partial completion (2/3 at max) → reduced score
# ---------------------------------------------------------------------------

def test_partial_completion_reduces_score():
    """2 of 3 work sets completed, both at max reps.

    set_scores = [100, 100], mean = 100
    completion_ratio = 2/3 ≈ 0.667
    raw = 100 * 0.667 ≈ 66.7 → snapped to 80
    """
    logs = [
        _make_set_log(1, reps=10),
        _make_set_log(2, reps=10),
        _make_set_log(3, completed=False, reps=None),
    ]
    se = _make_session_exercise(logs)
    te = _make_template_exercise([
        _make_rep_target(1, 8, 10),
        _make_rep_target(2, 8, 10),
        _make_rep_target(3, 8, 10),
    ])
    result = compute_success_score(se, te)
    assert result == 80


# ---------------------------------------------------------------------------
# Test 6: No template_exercise (None) → 80
# ---------------------------------------------------------------------------

def test_no_template_exercise_defaults_to_80():
    """When template_exercise is None all sets default to 80; ratio=1 → 80."""
    logs = [
        _make_set_log(1, reps=10),
        _make_set_log(2, reps=8),
    ]
    se = _make_session_exercise(logs)
    assert compute_success_score(se, None) == 80


# ---------------------------------------------------------------------------
# Test 7: Empty rep_targets → 80
# ---------------------------------------------------------------------------

def test_empty_rep_targets_defaults_to_80():
    """TemplateExercise present but rep_targets is empty → all sets default to 80."""
    logs = [
        _make_set_log(1, reps=10),
    ]
    se = _make_session_exercise(logs)
    te = _make_template_exercise([])  # empty list
    assert compute_success_score(se, te) == 80


# ---------------------------------------------------------------------------
# Test 8: Reps None on completed set → 80 default
# ---------------------------------------------------------------------------

def test_reps_none_on_completed_set_uses_default():
    """Completed set with reps=None → conservative 80 default."""
    logs = [
        _make_set_log(1, reps=None),
    ]
    se = _make_session_exercise(logs)
    te = _make_template_exercise([_make_rep_target(1, 8, 12)])
    assert compute_success_score(se, te) == 80


# ---------------------------------------------------------------------------
# Test 9: Warmup sets ignored
# ---------------------------------------------------------------------------

def test_warmup_sets_are_ignored():
    """Warmup sets (kind='warmup') are excluded from scoring entirely."""
    logs = [
        _make_set_log(1, kind="warmup", completed=True, reps=5),
        _make_set_log(1, kind="warmup", completed=True, reps=5),
        # No work sets at all
    ]
    se = _make_session_exercise(logs)
    te = _make_template_exercise([_make_rep_target(1, 8, 12)])
    # No completed work sets → None
    assert compute_success_score(se, te) is None


# ---------------------------------------------------------------------------
# Test 10: Mixed scores snap correctly
# ---------------------------------------------------------------------------

def test_mixed_scores_snap_correctly():
    """One set at max (100), one below range (50).

    set_scores = [100, 50], mean = 75
    completion_ratio = 2/2 = 1.0
    raw = 75 → snapped to 80 (>= 65)
    """
    logs = [
        _make_set_log(1, reps=12),  # at max → 100
        _make_set_log(2, reps=4),   # below min → 50
    ]
    se = _make_session_exercise(logs)
    te = _make_template_exercise([
        _make_rep_target(1, 8, 12),
        _make_rep_target(2, 8, 12),
    ])
    assert compute_success_score(se, te) == 80
