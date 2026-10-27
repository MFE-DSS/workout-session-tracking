import { AUREN_MARK_V1, MARK_MIN_SIZE, type MarkDrawing, markDrawingFor } from './markGeometry';

type Box = { x0: number; x1: number; y0: number; y1: number };
const points = (d: string) => [...d.matchAll(/(-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?)/g)].map((m) => [Number(m[1]), Number(m[2])]);
const box = (d: string): Box => {
  const p = points(d);
  return { x0: Math.min(...p.map(([x]) => x)), x1: Math.max(...p.map(([x]) => x)), y0: Math.min(...p.map(([, y]) => y)), y1: Math.max(...p.map(([, y]) => y)) };
};
/** The slot: the two inner x of the top edge, and how deep it runs. */
const slot = (d: string) => {
  const p = points(d);
  const top = Math.min(...p.map(([, y]) => y));
  const xs = [...new Set(p.filter(([, y]) => y === top).map(([x]) => x))].sort((a, b) => a - b);
  const depth = Math.max(...p.filter(([x]) => x === xs[1]).map(([, y]) => y)) - top;
  return { x0: xs[1], x1: xs[2], depth };
};
const DRAWINGS = Object.keys(AUREN_MARK_V1) as MarkDrawing[];

describe('DA-03.2 — AUREN-MARK-V1: the caller never chooses the drawing', () => {
  it.each([
    [0, null], [8, null], [11, null], [11.5, null],
    [12, 'micro'], [14, 'micro'], [15, 'micro'], [15.5, 'micro'],
    [16, 'compact'], [18, 'compact'], [19, 'compact'],
    [20, 'primary'], [24, 'primary'], [32, 'primary'], [64, 'primary'], [128, 'primary'], [1024, 'primary'],
  ] as const)('%p px → %p', (size, drawing) => {
    expect(markDrawingFor(size)).toBe(drawing);
  });

  it('nothing is rendered under 12 px, nor for a nonsense size', () => {
    expect(MARK_MIN_SIZE).toBe(12);
    expect(markDrawingFor(Number.NaN)).toBeNull();
    expect(markDrawingFor(-16)).toBeNull();
  });
});

describe('DA-03.2 — AUREN-MARK-V1: one mark in three optical drawings', () => {
  it.each(DRAWINGS)('%s: integer coordinates only — every edge on a pixel at its own size', (k) => {
    const g = AUREN_MARK_V1[k];
    for (const [x, y] of [...points(g.cursor), ...points(g.marker)]) {
      expect(Number.isInteger(x) && Number.isInteger(y)).toBe(true);
      expect(x >= 0 && x <= g.grid && y >= 0 && y <= g.grid).toBe(true);
    }
  });

  it.each(DRAWINGS)('%s: the two pieces share one width and one targeting axis', (k) => {
    const g = AUREN_MARK_V1[k];
    const c = box(g.cursor);
    const m = box(g.marker);
    expect([m.x0, m.x1]).toEqual([c.x0, c.x1]);
    expect([slot(g.marker).x0, slot(g.marker).x1]).toEqual([slot(g.cursor).x0, slot(g.cursor).x1]);
  });

  it.each(DRAWINGS)('%s: the cursor stands above, taller; a gap separates it from the marker', (k) => {
    const g = AUREN_MARK_V1[k];
    const c = box(g.cursor);
    const m = box(g.marker);
    expect(m.y0 - c.y1).toBeGreaterThanOrEqual(1); // the negative space: never touching
    expect(c.y1 - c.y0).toBeGreaterThan(m.y1 - m.y0);
  });

  it('primary: the hardened DA-03.2 proportions — walls 2,5 × the slot, gap = one slot', () => {
    const g = AUREN_MARK_V1.primary;
    const s = slot(g.cursor);
    const c = box(g.cursor);
    const m = box(g.marker);
    expect((s.x0 - c.x0) / (s.x1 - s.x0)).toBe(2.5);
    expect(m.y0 - c.y1).toBe(s.x1 - s.x0);
    expect(s.depth / (c.y1 - c.y0)).toBeCloseTo(slot(g.marker).depth / (m.y1 - m.y0), 10);
  });
});
