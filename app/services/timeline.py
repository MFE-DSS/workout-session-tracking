"""Server-rendered inline SVG timeline charts.

No JS. No Chart.js. Just a pure-Python SVG polyline builder
that returns an HTML-safe string the Jinja template can inject
with `{{ svg|safe }}`.

Two timelines shipped in Sprint 8:
  - quality score over time (0..100 Y axis)
  - bodyweight over time (auto-ranged Y axis)

Both take a list of (label, value) pairs and produce a
self-contained `<svg>` element with a polyline + dots + X labels.
Mobile-first: default width 100%, viewBox-based, responsive.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class TimelinePoint:
    label: str       # X axis label (e.g., "05/04")
    value: float     # Y axis value


def _build_svg(
    points: list[TimelinePoint],
    *,
    y_min: float,
    y_max: float,
    height: int = 180,
    width: int = 600,
    color: str = "#f25f3a",
    dot_radius: float = 4.0,
    title: str = "",
) -> str:
    """Build a self-contained <svg> polyline chart."""
    if not points or y_max <= y_min:
        return ""

    pad_left = 42
    pad_right = 16
    pad_top = 24
    pad_bottom = 32
    chart_w = width - pad_left - pad_right
    chart_h = height - pad_top - pad_bottom
    n = len(points)

    def x_pos(i: int) -> float:
        if n == 1:
            return pad_left + chart_w / 2
        return pad_left + (i / (n - 1)) * chart_w

    def y_pos(v: float) -> float:
        ratio = (v - y_min) / (y_max - y_min) if y_max != y_min else 0.5
        return pad_top + chart_h * (1 - ratio)

    # Build polyline points
    coords = " ".join(f"{x_pos(i):.1f},{y_pos(p.value):.1f}" for i, p in enumerate(points))

    # Y axis labels (min, mid, max)
    y_mid = (y_min + y_max) / 2
    y_labels = [
        (y_pos(y_max), f"{y_max:g}"),
        (y_pos(y_mid), f"{y_mid:g}"),
        (y_pos(y_min), f"{y_min:g}"),
    ]

    # X axis labels (show first, last, and a few in between)
    x_label_indices = _pick_label_indices(n, max_labels=7)

    parts: list[str] = []
    parts.append(
        f'<svg viewBox="0 0 {width} {height}" '
        f'xmlns="http://www.w3.org/2000/svg" '
        f'style="width:100%;max-width:{width}px;height:auto;" '
        f'role="img" aria-label="{title}">'
    )

    # Background
    parts.append(
        f'<rect x="0" y="0" width="{width}" height="{height}" '
        f'fill="#171a21" rx="10"/>'
    )

    # Grid lines (horizontal)
    for yp, _ in y_labels:
        parts.append(
            f'<line x1="{pad_left}" y1="{yp:.1f}" '
            f'x2="{width - pad_right}" y2="{yp:.1f}" '
            f'stroke="#ffffff0d" stroke-width="1"/>'
        )

    # Y axis labels
    for yp, txt in y_labels:
        parts.append(
            f'<text x="{pad_left - 6}" y="{yp:.1f}" '
            f'text-anchor="end" dominant-baseline="middle" '
            f'fill="#9aa3b2" font-size="11" '
            f'font-family="system-ui,sans-serif">{txt}</text>'
        )

    # Polyline
    parts.append(
        f'<polyline points="{coords}" fill="none" '
        f'stroke="{color}" stroke-width="2.5" '
        f'stroke-linejoin="round" stroke-linecap="round"/>'
    )

    # Dots
    for i, p in enumerate(points):
        parts.append(
            f'<circle cx="{x_pos(i):.1f}" cy="{y_pos(p.value):.1f}" '
            f'r="{dot_radius}" fill="{color}"/>'
        )

    # X axis labels
    for i in x_label_indices:
        parts.append(
            f'<text x="{x_pos(i):.1f}" y="{height - 6}" '
            f'text-anchor="middle" fill="#9aa3b2" font-size="10" '
            f'font-family="system-ui,sans-serif">{points[i].label}</text>'
        )

    # Title
    if title:
        parts.append(
            f'<text x="{pad_left}" y="16" fill="#f5f6f8" '
            f'font-size="12" font-weight="700" '
            f'font-family="system-ui,sans-serif">{title}</text>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


def _pick_label_indices(n: int, max_labels: int = 7) -> list[int]:
    """Pick evenly spaced indices for the X axis labels."""
    if n <= max_labels:
        return list(range(n))
    step = (n - 1) / (max_labels - 1)
    return sorted({round(i * step) for i in range(max_labels)})


def build_quality_timeline_svg(
    points: list[TimelinePoint],
) -> str:
    """Quality score timeline: 0..100 fixed Y axis."""
    return _build_svg(
        points,
        y_min=0,
        y_max=100,
        color="#f25f3a",
        title="Qualité de séance",
    )


def build_bodyweight_timeline_svg(
    points: list[TimelinePoint],
) -> str:
    """Bodyweight timeline: auto-ranged Y axis with 2 kg padding."""
    if not points:
        return ""
    vals = [p.value for p in points]
    lo = min(vals) - 2
    hi = max(vals) + 2
    return _build_svg(
        points,
        y_min=lo,
        y_max=hi,
        color="#2ecc71",
        title="Poids corporel (kg)",
    )
