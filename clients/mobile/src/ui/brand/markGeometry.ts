/**
 * DA-03.2 — `AUREN-MARK-V1` (LOCKED, operator 2026-10-27): the ActiveCursor over the
 * ReferenceMarker, one targeting axis, the negative space between them. No rail.
 *
 * One mark, three OPTICAL drawings, each exact on its own pixel grid. Byte for byte the
 * geometry of `design/auren/source/brand/mark/*.svg` (tests/test_auren_mark_v1.py).
 * Changing a coordinate here is a contract change, never a refactor.
 */
export type MarkDrawing = 'primary' | 'compact' | 'micro';

export type MarkGeometry = {
  /** viewBox side, in grid units */
  grid: number;
  /** the operator-owned piece, then the system-owned piece */
  cursor: string;
  marker: string;
};

export const AUREN_MARK_V1: Record<MarkDrawing, MarkGeometry> = {
  primary: {
    grid: 32,
    cursor: 'M10 4 L15 4 L15 10 L17 10 L17 4 L22 4 L22 18 L10 18 Z',
    marker: 'M10 20 L15 20 L15 23 L17 23 L17 20 L22 20 L22 27 L10 27 Z',
  },
  compact: {
    grid: 16,
    cursor: 'M4 1 L7 1 L7 4 L8 4 L8 1 L11 1 L11 8 L4 8 Z',
    marker: 'M4 10 L7 10 L7 12 L8 12 L8 10 L11 10 L11 14 L4 14 Z',
  },
  micro: {
    grid: 12,
    cursor: 'M3 1 L5 1 L5 3 L6 3 L6 1 L8 1 L8 6 L3 6 Z',
    marker: 'M3 7 L5 7 L5 8 L6 8 L6 7 L8 7 L8 10 L3 10 Z',
  },
};

/** Below this, the mark is not rendered at all (operator ruling). */
export const MARK_MIN_SIZE = 12;

/** The optical drawing for a rendered size: 12–15 micro · 16–19 compact · 20+ primary · under 12 none. */
export function markDrawingFor(size: number): MarkDrawing | null {
  if (Number.isNaN(size) || size < MARK_MIN_SIZE) return null;
  if (size < 16) return 'micro';
  if (size < 20) return 'compact';
  return 'primary';
}
