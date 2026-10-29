/**
 * DA-04.1 — the triptych composition, as Recessed Window boxes in one Frame C.
 * Same rule as `windowLayout` (RECESSED-WINDOW-V1): windows 2u apart, never overlapping,
 * never outside the parent's content field.
 *
 * T1 — three equal windows side by side (operator, 2026-10-29): equal weight for the three
 * localisation zones, and no window large enough to enlarge the source geometry past its
 * useful scale. T2 (one dominant + two stacked) was explored and not retained.
 *
 * DA-04.2 — a session shows every zone it trains, so the same grammar extends to N windows:
 * at most three per row (T1's window width, never wider), rows balanced, every window the
 * same size, an incomplete last row left-aligned. Three zones give exactly T1.
 */
import type { WindowBox } from '../instrument/recessedWindowGeometry';

/** The module height at which the triptych is governed (390 wide). */
export const TRIPTYCH_HEIGHT = 180;
/** Each further row of windows adds one T1 row and its 2u gap. */
export const ROW_STEP = 160;
export const MAX_PER_ROW = 3;

/** Three equal windows, in preset order; the last takes the rounding remainder. */
export function triptychLayout(content: WindowBox, u: number): WindowBox[] {
  const gap = 2 * u;
  const w = Math.floor((content.w - 2 * gap) / 3);
  const last = content.w - 2 * gap - 2 * w;
  return [
    { x: content.x, y: content.y, w, h: content.h },
    { x: content.x + w + gap, y: content.y, w, h: content.h },
    { x: content.x + 2 * (w + gap), y: content.y, w: last, h: content.h },
  ];
}

export function zoneGridShape(n: number) {
  const rows = Math.max(1, Math.ceil(n / MAX_PER_ROW));
  const cols = Math.max(1, Math.ceil(n / rows));
  return { rows, cols };
}

/** The Frame C height for `n` zones at the governed width. */
export function zoneGridHeight(n: number): number {
  return TRIPTYCH_HEIGHT + (zoneGridShape(n).rows - 1) * ROW_STEP;
}

/** N equal windows in balanced rows of at most three; `n = 3` is `triptychLayout`. */
export function zoneGridLayout(n: number, content: WindowBox, u: number): WindowBox[] {
  if (n === 3) return triptychLayout(content, u);
  const gap = 2 * u;
  const { rows, cols } = zoneGridShape(n);
  const w = Math.floor((content.w - (cols - 1) * gap) / cols);
  const h = Math.floor((content.h - (rows - 1) * gap) / rows);
  return Array.from({ length: n }, (_, i) => {
    const r = Math.floor(i / cols);
    const c = i % cols;
    return { x: content.x + c * (w + gap), y: content.y + r * (h + gap), w, h };
  });
}
