"""Server-rendered SVG hexagonal radar chart for physique dashboard."""
from __future__ import annotations

import math


def build_radar_svg(axes: list, size: int = 300) -> str:
    if not axes:
        return ""

    n = len(axes)
    cx = size / 2
    cy = size / 2
    radius = size / 2 - 40
    angle_step = 2 * math.pi / n
    start_angle = -math.pi / 2

    def polar(angle, r):
        return cx + r * math.cos(angle), cy + r * math.sin(angle)

    parts = []
    parts.append(
        f'<svg viewBox="0 0 {size} {size}" '
        f'xmlns="http://www.w3.org/2000/svg" '
        f'class="chart--interactive" '
        f'style="width:100%;max-width:{size}px;height:auto;" '
        f'role="img" aria-label="Radar physique">'
    )
    parts.append(f'<rect x="0" y="0" width="{size}" height="{size}" fill="#161a22" rx="8"/>')

    # Concentric hexagons
    for pct in [0.33, 0.66, 1.0]:
        r = radius * pct
        hex_pts = " ".join(
            f"{polar(start_angle + i * angle_step, r)[0]:.1f},"
            f"{polar(start_angle + i * angle_step, r)[1]:.1f}"
            for i in range(n)
        )
        parts.append(f'<polygon points="{hex_pts}" fill="none" stroke="#232834" stroke-width="1"/>')

    # Axis lines
    for i in range(n):
        angle = start_angle + i * angle_step
        x2, y2 = polar(angle, radius)
        parts.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#232834" stroke-width="1"/>')

    # Score polygon
    score_pts = []
    for i, axis in enumerate(axes):
        angle = start_angle + i * angle_step
        r = radius * (axis.score / 100) if axis.score > 0 else 0
        score_pts.append(f"{polar(angle, r)[0]:.1f},{polar(angle, r)[1]:.1f}")
    parts.append(
        f'<polygon points="{" ".join(score_pts)}" '
        f'fill="#f25f3a" fill-opacity="0.15" '
        f'stroke="#f25f3a" stroke-width="2" stroke-linejoin="round"/>'
    )

    # Interactive data points
    for i, axis in enumerate(axes):
        angle = start_angle + i * angle_step
        r = radius * (axis.score / 100) if axis.score > 0 else 0
        x, y = polar(angle, r)
        score_txt = f"{axis.score:.0f}"
        label_r = r + 14 if r > 20 else 22
        lx, ly = polar(angle, label_r)
        parts.append('<g class="chart-point">')
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="14" fill="transparent" class="chart-point__hit"/>')
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="#f25f3a" class="chart-point__dot"/>')
        parts.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" dominant-baseline="middle" '
            f'fill="#e8ecf1" font-size="11" font-weight="600" '
            f'font-family="\'JetBrains Mono\',monospace" class="chart-point__label">{score_txt}</text>'
        )
        parts.append(f'<title>{axis.label}: {score_txt}/100</title>')
        parts.append('</g>')

    # Axis labels outside
    for i, axis in enumerate(axes):
        angle = start_angle + i * angle_step
        lx, ly = polar(angle, radius + 24)
        if abs(lx - cx) < 5:
            anchor = "middle"
        elif lx < cx:
            anchor = "end"
        else:
            anchor = "start"
        parts.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" dominant-baseline="middle" '
            f'fill="#9aa3ad" font-size="11" font-family="\'Inter\',system-ui,sans-serif">{axis.label}</text>'
        )

    # Global score center
    global_avg = sum(a.score for a in axes) / len(axes) if axes else 0
    parts.append(
        f'<text x="{cx:.1f}" y="{cy:.1f}" text-anchor="middle" dominant-baseline="middle" '
        f'fill="#e8ecf1" font-size="28" font-weight="700" '
        f'font-family="\'JetBrains Mono\',monospace">{global_avg:.0f}</text>'
    )

    parts.append("</svg>")
    return "\n".join(parts)
