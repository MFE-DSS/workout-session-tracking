/**
 * DA-02.5 — Recessed Window (`RECESSED-WINDOW-V1`, LOCKED 2026-10-25: W1 · Inset).
 *
 * A subfield cut into an InstrumentFrame — not a card. Pure geometry on the parent's
 * grid: every inset, break and mark is a multiple of `u` (one rail index). Rectilinear
 * only, no colour: the renderer maps the roles to monochrome tokens that stay QUIETER
 * than Frame C (the parent strokes in `ink3`, the window in `line`).
 *
 * W2 (slot) and W3 (rail recess) were explored and not retained (operator, 2026-10-25):
 * the closed outline frames information best.
 */
import type { Block, Segment } from './frameGeometry';

export type WindowGeometry = {
  width: number;
  height: number;
  u: number;
  /** the stroke width of the window's line — thinner than Frame C's secondary stroke */
  stroke: number;
  /** the recessed field: one solid rectangle, the window itself */
  field: { x: number; y: number; w: number; h: number };
  segments: Segment[];
  /** the registration mark */
  blocks: Block[];
  /** where the information goes: never overlapped by the window's structure */
  content: { x: number; y: number; w: number; h: number };
};

/** Window stroke: 0.25u, under Frame C's 0.35u — the child never outweighs the parent. */
export const WINDOW_STROKE_U = 0.25;
/** Internal padding from the window's structure to its content. */
export const WINDOW_PADDING_U = 2;

const h = (y: number, x1: number, x2: number): Segment => ({ x1, y1: y, x2, y2: y, weight: 'secondary' });
const v = (x: number, y1: number, y2: number): Segment => ({ x1: x, y1, x2: x, y2, weight: 'secondary' });

/**
 * A quiet recessed field; a thin perimeter with ONE intentional break (top edge, 3u,
 * near the right) and one 1u × 1.6u registration mark at the bottom-left corner.
 */
export function recessedWindowGeometry(W: number, H: number, u: number): WindowGeometry {
  const s = WINDOW_STROKE_U * u;
  const a = s / 2;
  const breakFrom = W - 7 * u;
  const breakTo = W - 4 * u;
  const segments = [h(a, a, breakFrom), h(a, breakTo, W - a), v(W - a, a, H - a), h(H - a, a, W - a), v(a, a, H - a)];
  const blocks: Block[] = [{ x: 0, y: H - 1.6 * u, w: u, h: 1.6 * u, role: 'structure' }];
  const pad = WINDOW_PADDING_U * u + s;
  return {
    width: W,
    height: H,
    u,
    stroke: s,
    field: { x: 0, y: 0, w: W, h: H },
    segments,
    blocks,
    content: { x: pad + u, y: pad, w: W - 2 * pad - u, h: H - 2 * pad },
  };
}

export type WindowBox = { x: number; y: number; w: number; h: number };
export type WindowLayout = 'single' | 'pair' | 'split-60-40';

/** Windows placed in a parent content field, separated by 2u — never overlapping, never outside. */
export function windowLayout(layout: WindowLayout, content: WindowBox, u: number): WindowBox[] {
  const gap = 2 * u;
  if (layout === 'single') return [{ ...content }];
  const free = content.w - gap;
  const first = layout === 'pair' ? Math.floor(free / 2) : Math.floor(free * 0.6);
  return [
    { x: content.x, y: content.y, w: first, h: content.h },
    { x: content.x + first + gap, y: content.y, w: free - first, h: content.h },
  ];
}
