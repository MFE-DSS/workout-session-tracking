"""Server-rendered inline SVG timeline charts.

Pure-Python SVG builder with:
  - Area fill under the curve (gradient for depth)
  - Interactive hover on data points (CSS :hover, no JS)
  - Y-axis based on mean ± 2σ for logical range
  - Native SVG <title> tooltips on each point

Charts:
  - quality score over time (0..100 Y axis)
  - bodyweight over time (auto-ranged)
  - body measurement evolution (mean ± 2σ range)
  - sparkline (compact, no axes)
"""
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class TimelinePoint:
    label: str       # X axis label (e.g., "05/04")
    value: float     # Y axis value
    kind: str | None = None  # "strength" | "cardio" | None (Sb_09)


# Sb_09 — canonical palette for session-kind dispatch in timeline dots.
KIND_COLORS: dict[str, str] = {
    "strength": "#f25f3a",
    "cardio": "#38b2ac",
}
KIND_LABELS: dict[str, str] = {
    "strength": "musculation",
    "cardio": "cardio",
}


def _compute_smart_range(values: list[float], padding_factor: float = 0.5) -> tuple[float, float]:
    """Compute Y-axis range using mean ± 2σ, with minimum padding.

    Produces a range that focuses on the meaningful variation zone
    rather than just min/max with arbitrary padding.
    """
    if len(values) < 2:
        lo, hi = min(values) - 2, max(values) + 2
        return lo, hi

    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    std = math.sqrt(variance)

    # Use mean ± 2σ, but ensure at least min/max are included
    range_lo = min(mean - 2 * std, min(values))
    range_hi = max(mean + 2 * std, max(values))

    # Ensure minimum visible range (at least 2 units)
    span = range_hi - range_lo
    if span < 2:
        mid = (range_lo + range_hi) / 2
        range_lo = mid - 1
        range_hi = mid + 1

    # Add small padding
    pad = (range_hi - range_lo) * 0.1
    return range_lo - pad, range_hi + pad


def _build_svg(
    points: list[TimelinePoint],
    *,
    y_min: float,
    y_max: float,
    height: int = 220,
    width: int = 600,
    color: str = "#f25f3a",
    dot_radius: float = 4.5,
    title: str = "",
    area_fill: bool = True,
    interactive: bool = True,
    unit: str = "",
) -> str:
    """Build a self-contained <svg> chart with area fill and hover points."""
    if not points or y_max <= y_min:
        return ""

    pad_left = 48
    pad_right = 16
    pad_top = 28 if title else 12
    pad_bottom = 36
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

    # Unique ID for gradient
    grad_id = f"g{abs(hash(title or 'chart')) % 99999}"

    # Polyline coords
    coords = " ".join(f"{x_pos(i):.1f},{y_pos(p.value):.1f}" for i, p in enumerate(points))

    # Area polygon coords (polyline + baseline closure)
    area_coords = coords + f" {x_pos(n - 1):.1f},{pad_top + chart_h:.1f} {x_pos(0):.1f},{pad_top + chart_h:.1f}"

    # Y axis: 5 grid lines evenly spaced
    y_step_count = 4
    y_labels = []
    for j in range(y_step_count + 1):
        v = y_min + (y_max - y_min) * j / y_step_count
        yp = y_pos(v)
        # Format: 1 decimal if fractional, integer otherwise
        txt = f"{v:.1f}" if v != int(v) else f"{int(v)}"
        y_labels.append((yp, txt))

    x_label_indices = _pick_label_indices(n, max_labels=7)

    parts: list[str] = []

    # SVG open with class for CSS hover
    css_class = "chart--interactive" if interactive else ""
    parts.append(
        f'<svg viewBox="0 0 {width} {height}" '
        f'xmlns="http://www.w3.org/2000/svg" '
        f'class="{css_class}" '
        f'style="width:100%;max-width:{width}px;height:auto;" '
        f'role="img" aria-label="{title}">'
    )

    # Gradient definition for area fill
    if area_fill:
        parts.append(
            f'<defs><linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0%" stop-color="{color}" stop-opacity="0.25"/>'
            f'<stop offset="100%" stop-color="{color}" stop-opacity="0.02"/>'
            f'</linearGradient></defs>'
        )

    # Background
    parts.append(
        f'<rect x="0" y="0" width="{width}" height="{height}" '
        f'fill="#161a22" rx="8"/>'
    )

    # Grid lines (horizontal, subtle)
    for yp, _ in y_labels:
        parts.append(
            f'<line x1="{pad_left}" y1="{yp:.1f}" '
            f'x2="{width - pad_right}" y2="{yp:.1f}" '
            f'stroke="#ffffff08" stroke-width="1"/>'
        )

    # Y axis labels
    for yp, txt in y_labels:
        parts.append(
            f'<text x="{pad_left - 8}" y="{yp:.1f}" '
            f'text-anchor="end" dominant-baseline="middle" '
            f'fill="#5a6270" font-size="10" '
            f'font-family="\'JetBrains Mono\',monospace">{txt}</text>'
        )

    # Area fill (gradient under the curve)
    if area_fill:
        parts.append(
            f'<polygon points="{area_coords}" '
            f'fill="url(#{grad_id})"/>'
        )

    # Polyline
    parts.append(
        f'<polyline points="{coords}" fill="none" '
        f'stroke="{color}" stroke-width="2" '
        f'stroke-linejoin="round" stroke-linecap="round"/>'
    )

    # Interactive data points with hover
    for i, p in enumerate(points):
        cx = x_pos(i)
        cy = y_pos(p.value)
        val_txt = f"{p.value:g}{unit}"
        # Per-point color if kind is provided and resolves in the palette.
        dot_color = KIND_COLORS.get(p.kind, color) if p.kind else color

        if interactive:
            # Group with hover behavior (CSS enlarges circle + shows label)
            parts.append(f'<g class="chart-point">')
            # Invisible larger hit area for touch
            parts.append(
                f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="16" '
                f'fill="transparent" class="chart-point__hit"/>'
            )
            # Visible dot
            parts.append(
                f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{dot_radius}" '
                f'fill="{dot_color}" class="chart-point__dot"/>'
            )
            # Value label (hidden by default, shown on hover via CSS)
            label_y = cy - 14
            if label_y < pad_top:
                label_y = cy + 18
            parts.append(
                f'<text x="{cx:.1f}" y="{label_y:.1f}" '
                f'text-anchor="middle" '
                f'fill="#e8ecf1" font-size="11" font-weight="600" '
                f'font-family="\'JetBrains Mono\',monospace" '
                f'class="chart-point__label">{val_txt}</text>'
            )
            # Date label below value
            parts.append(
                f'<text x="{cx:.1f}" y="{label_y + 12:.1f}" '
                f'text-anchor="middle" '
                f'fill="#5a6270" font-size="9" '
                f'font-family="\'JetBrains Mono\',monospace" '
                f'class="chart-point__label">{p.label}</text>'
            )
            # Native tooltip fallback
            parts.append(f'<title>{p.label}: {val_txt}</title>')
            parts.append('</g>')
        else:
            parts.append(
                f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{dot_radius}" fill="{dot_color}"/>'
            )

    # X axis labels
    for i in x_label_indices:
        parts.append(
            f'<text x="{x_pos(i):.1f}" y="{height - 8}" '
            f'text-anchor="middle" fill="#5a6270" font-size="10" '
            f'font-family="\'JetBrains Mono\',monospace">{points[i].label}</text>'
        )

    # Title
    if title:
        parts.append(
            f'<text x="{pad_left}" y="18" fill="#e8ecf1" '
            f'font-size="12" font-weight="600" '
            f'font-family="\'Inter\',system-ui,sans-serif">{title}</text>'
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
    """Bodyweight timeline: auto-ranged Y axis with mean±2σ."""
    if not points:
        return ""
    vals = [p.value for p in points]
    lo, hi = _compute_smart_range(vals)
    return _build_svg(
        points,
        y_min=lo,
        y_max=hi,
        color="#2ecc71",
        title="Poids corporel (kg)",
        interactive=True,
        area_fill=True,
        unit=" kg",
    )


def build_sparkline_svg(
    scores: list[tuple[float, ...]],
    *,
    width: int = 200,
    height: int = 40,
    color: str = "#f25f3a",
    kinds: list[str | None] | None = None,
) -> str | None:
    """Build a compact sparkline SVG (no axes, no labels).

    Input: list of tuples where the first element is the score value.
    If ``kinds`` is provided (same length as ``scores``), each data point
    gets a coloured dot based on session kind (Sb_09 dispatcher).
    Returns None if fewer than 2 data points.
    """
    if len(scores) < 2:
        return None

    values = [s[0] for s in scores]
    v_min = min(values)
    v_max = max(values)
    v_range = v_max - v_min if v_max != v_min else 1.0

    pad = 4
    chart_w = width - 2 * pad
    chart_h = height - 2 * pad
    n = len(values)

    def x_pos(i: int) -> float:
        return pad + (i / (n - 1)) * chart_w

    def y_pos(v: float) -> float:
        ratio = (v - v_min) / v_range
        return pad + chart_h * (1 - ratio)

    coords = " ".join(f"{x_pos(i):.1f},{y_pos(v):.1f}" for i, v in enumerate(values))

    dots = ""
    if kinds and len(kinds) == n:
        dot_parts: list[str] = []
        for i, k in enumerate(kinds):
            c = KIND_COLORS.get(k, color) if k else color
            dot_parts.append(
                f'<circle cx="{x_pos(i):.1f}" cy="{y_pos(values[i]):.1f}" '
                f'r="2.5" fill="{c}"/>'
            )
        dots = "".join(dot_parts)

    return (
        f'<svg viewBox="0 0 {width} {height}" '
        f'xmlns="http://www.w3.org/2000/svg" '
        f'style="width:100%;max-width:{width}px;height:auto;" '
        f'role="img" aria-label="Sparkline de progression">'
        f'<polyline points="{coords}" fill="none" '
        f'stroke="{color}" stroke-width="2" '
        f'stroke-linejoin="round" stroke-linecap="round"/>'
        f'{dots}'
        f'</svg>'
    )


def build_measurement_timeline_svg(
    points: list[TimelinePoint],
    *,
    title: str = "",
    unit: str = "",
) -> str:
    """Measurement evolution timeline with mean±2σ Y-axis range.

    Returns empty string if fewer than 2 data points.
    Interactive hover on data points. Area fill for depth.
    """
    if len(points) < 2:
        return ""
    vals = [p.value for p in points]
    lo, hi = _compute_smart_range(vals)
    return _build_svg(
        points,
        y_min=lo,
        y_max=hi,
        color="#f25f3a",
        title=title,
        height=220,
        interactive=True,
        area_fill=True,
        unit=unit,
    )
