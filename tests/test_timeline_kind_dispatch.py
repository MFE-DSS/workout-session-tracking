"""Tests for the Sb_09 kind-aware timeline & sparkline rendering."""
from __future__ import annotations

from app.services.timeline import (
    KIND_COLORS,
    TimelinePoint,
    build_quality_timeline_svg,
    build_sparkline_svg,
)


def test_timeline_colors_strength_and_cardio_dots_distinctly():
    points = [
        TimelinePoint(label="01/04", value=72, kind="strength"),
        TimelinePoint(label="03/04", value=88, kind="cardio"),
        TimelinePoint(label="05/04", value=65, kind="strength"),
    ]
    svg = build_quality_timeline_svg(points)
    assert svg
    # Both dispatcher colors must appear somewhere in the output.
    assert KIND_COLORS["strength"] in svg
    assert KIND_COLORS["cardio"] in svg


def test_timeline_kind_none_falls_back_to_single_color():
    """Backward compat: points without kind still render."""
    points = [TimelinePoint(label="01/04", value=70), TimelinePoint(label="02/04", value=80)]
    svg = build_quality_timeline_svg(points)
    assert svg
    # Cardio color must NOT appear when no point carries that kind.
    assert KIND_COLORS["cardio"] not in svg


def test_sparkline_with_kinds_marks_dots_per_session():
    points = [(60.0,), (72.0,), (85.0,)]
    kinds: list[str | None] = ["strength", "cardio", "strength"]
    svg = build_sparkline_svg(points, kinds=kinds)
    assert svg
    assert KIND_COLORS["strength"] in svg
    assert KIND_COLORS["cardio"] in svg


def test_sparkline_without_kinds_omits_dots():
    svg = build_sparkline_svg([(60.0,), (72.0,)])
    assert svg
    # No cardio teal color when no kinds are provided.
    assert KIND_COLORS["cardio"] not in svg
