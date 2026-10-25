/**
 * DA-02.2 — the Calibration System's two markers, rebuilt on ONE normalized grid
 * (`docs/strategy/AUREN_CALIBRATION_SYSTEM.md`, LOCKED v1).
 *
 * The operator's traced SVGs (design/auren/source/calibration/reference/) fix the
 * direction only. Here both objects share, exactly: the targeting-slot width, the
 * wall thickness, the overall WIDTH, the bottom notch, square corners and the axis
 * x = 0. The unit `u` IS the width of a rail index: the slot is one index wide, so
 * the index it frames fills it exactly (operator review, 2026-10-25).
 *
 * Units are `u`. A polygon is listed clockwise from its top-left point; y grows
 * downward, y = 0 is the object's top. No colour lives here.
 */

/** The shared invariants. SLOT = one rail index. */
export const SLOT = 1;
export const WALL = 2.5;
export const NOTCH = { width: 1, depth: 0.6 } as const;

export type Point = readonly [number, number];
export type MarkerGeometry = {
  width: number;
  height: number;
  /** how deep the slot runs from the top: the part of the rail index it frames */
  slotDepth: number;
  polygon: readonly Point[];
};

const s = SLOT / 2; // slot half-width
const o = s + WALL; // outer face of a wall = half the shared width
const n = NOTCH.width / 2;

/**
 * ActiveCursor — held by the operator: the massive one, TALL. Two walls around
 * the slot, closed into a solid body below it. 6u × 10u.
 */
export const ACTIVE_CURSOR: MarkerGeometry = (() => {
  const height = 10;
  const slotDepth = 4;
  return {
    width: 2 * o,
    height,
    slotDepth,
    polygon: [
      [-o, 0], [-s, 0], [-s, slotDepth], [s, slotDepth], [s, 0], [o, 0],
      [o, height], [n, height], [n, height - NOTCH.depth], [-n, height - NOTCH.depth], [-n, height],
      [-o, height],
    ],
  };
})();

/**
 * ReferenceMarker — set by the instrument: the same width, LOW and flat. The
 * same two walls on a sole. 6u × 4u: only its height tells it from the cursor.
 */
export const REFERENCE_MARKER: MarkerGeometry = (() => {
  const height = 4;
  const slotDepth = 2;
  return {
    width: 2 * o,
    height,
    slotDepth,
    polygon: [
      [-o, 0], [-s, 0], [-s, slotDepth], [s, slotDepth], [s, 0], [o, 0],
      [o, height], [n, height], [n, height - NOTCH.depth], [-n, height - NOTCH.depth], [-n, height],
      [-o, height],
    ],
  };
})();

/** SVG path data for a polygon, scaled by `u` and shifted so x = 0 lands on `cx`. */
export function polygonPath(g: MarkerGeometry, u: number, cx = (g.width / 2) * u): string {
  return (
    g.polygon.map(([x, y], i) => `${i ? 'L' : 'M'}${round(cx + x * u)} ${round(y * u)}`).join(' ') + ' Z'
  );
}

function round(v: number): number {
  return Math.round(v * 1000) / 1000;
}
