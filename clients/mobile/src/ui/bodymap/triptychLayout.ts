/**
 * DA-04.1 — the triptych composition, as Recessed Window boxes in one Frame C.
 * Same rule as `windowLayout` (RECESSED-WINDOW-V1): windows 2u apart, never overlapping,
 * never outside the parent's content field.
 *
 * T1 — three equal windows side by side (operator, 2026-10-29): equal weight for the three
 * localisation zones, and no window large enough to enlarge the source geometry past its
 * useful scale. T2 (one dominant + two stacked) was explored and not retained.
 */
import type { WindowBox } from '../instrument/recessedWindowGeometry';

/** The module height at which the triptych is governed (390 wide). */
export const TRIPTYCH_HEIGHT = 180;

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
