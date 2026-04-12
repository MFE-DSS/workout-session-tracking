"""Tests for PerformanceSnapshot and composite scoring."""
from __future__ import annotations

import math

from app.services.performance import (
    PerformanceSnapshot,
    compute_composite_score,
    compute_grade,
    compute_grade_score,
)


def test_composite_score_basic():
    """60% quality + 40% completion rate."""
    score = compute_composite_score(quality_score=80, completion_rate=1.0)
    assert score == 88.0


def test_composite_score_partial_completion():
    score = compute_composite_score(quality_score=100, completion_rate=0.5)
    assert score == 80.0


def test_composite_score_zero():
    score = compute_composite_score(quality_score=0, completion_rate=0.0)
    assert score == 0.0


def test_grade_score_rewards_volume():
    """grade_score = avg_points * log(1 + total_sessions)."""
    gs = compute_grade_score(avg_points=80.0, total_sessions=10)
    expected = 80.0 * math.log(1 + 10)
    assert abs(gs - expected) < 0.01


def test_grade_score_single_session():
    gs = compute_grade_score(avg_points=80.0, total_sessions=1)
    expected = 80.0 * math.log(2)
    assert abs(gs - expected) < 0.01


def test_grade_a():
    assert compute_grade(avg_points=90.0, total_sessions=10) == "A"


def test_grade_b():
    assert compute_grade(avg_points=65.0, total_sessions=3) == "B"


def test_grade_c():
    assert compute_grade(avg_points=30.0, total_sessions=1) == "C"


def test_performance_snapshot_dataclass():
    snap = PerformanceSnapshot(
        score=88.0,
        trend="up",
        consistency=0.85,
        last_session_score=92,
        grade="A",
        grade_label="Execution reguliere et de haute qualite",
    )
    assert snap.score == 88.0
    assert snap.grade == "A"
