"""Unified performance metrics: PerformanceSnapshot.

A single dataclass consumed by Board, Profile, and Leaderboard
to ensure scoring consistency across all pages.

Composite score formula:
  score = 0.6 * quality_score + 0.4 * (completion_rate * 100)

Grade score (for A/B/C grading):
  grade_score = avg_points * log(1 + total_sessions)

Grade thresholds:
  A: grade_score >= 120
  B: grade_score >= 50
  C: grade_score < 50
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class PerformanceSnapshot:
    """Performance summary for a user, shared across pages."""

    score: float
    trend: str
    consistency: float
    last_session_score: Optional[int]
    grade: str
    grade_label: str


GRADE_LABELS = {
    "A": "Exécution régulière et de haute qualité",
    "B": "Bonne régularité, marge de progression",
    "C": "En progression, chaque séance compte",
}

_GRADE_A_THRESHOLD = 120.0
_GRADE_B_THRESHOLD = 50.0


def compute_composite_score(
    quality_score: float, completion_rate: float
) -> float:
    """Composite score: 60% quality + 40% completion rate (as %).

    quality_score: 0..100
    completion_rate: 0..1
    Returns: 0..100
    """
    return 0.6 * quality_score + 0.4 * (completion_rate * 100)


def compute_grade_score(avg_points: float, total_sessions: int) -> float:
    """Grade score: avg_points * log(1 + total_sessions)."""
    return avg_points * math.log(1 + total_sessions)


def compute_grade(avg_points: float, total_sessions: int) -> str:
    """Compute A/B/C grade from avg_points and session count."""
    gs = compute_grade_score(avg_points, total_sessions)
    if gs >= _GRADE_A_THRESHOLD:
        return "A"
    elif gs >= _GRADE_B_THRESHOLD:
        return "B"
    return "C"
