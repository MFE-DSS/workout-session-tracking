import { densityFor, UNIT } from '../calibration/layout';
import { SLOT } from '../calibration/geometry';
import { type FrameGeometry, frameGeometry, type FrameVariant, MIN_PADDING_U } from './frameGeometry';

const VARIANTS: FrameVariant[] = ['recessed', 'indexed', 'rail', 'faceplate'];
const SIZES: [number, number][] = [
  [180, 120],
  [320, 180],
  [390, 220],
];
const CASES = VARIANTS.flatMap((v) => SIZES.map(([w, h]) => [v, w, h] as const));
const geo = (v: FrameVariant, w: number, h: number) => frameGeometry(v, w, h, UNIT[densityFor(w)]);

/** Does a stroke or block touch the rectangle r? */
function touches(g: FrameGeometry, r: FrameGeometry['content']): boolean {
  const hit = (x0: number, y0: number, x1: number, y1: number) =>
    x0 < r.x + r.w && x1 > r.x && y0 < r.y + r.h && y1 > r.y;
  const strokes = g.segments.some((s) => {
    const half = (s.weight === 'primary' ? g.primary : g.secondary) / 2;
    return hit(Math.min(s.x1, s.x2) - half, Math.min(s.y1, s.y2) - half, Math.max(s.x1, s.x2) + half, Math.max(s.y1, s.y2) + half);
  });
  const blocks = g.blocks.filter((b) => b.role === 'structure').some((b) => hit(b.x, b.y, b.x + b.w, b.y + b.h));
  return strokes || blocks;
}

describe('DA-02.3 — every candidate is built on the calibration grid', () => {
  it.each(CASES)('%s at %i×%i: rectilinear only (every segment horizontal or vertical)', (v, w, h) => {
    for (const s of geo(v, w, h).segments) expect(s.x1 === s.x2 || s.y1 === s.y2).toBe(true);
  });

  it.each(CASES)('%s at %i×%i: all structure stays inside the frame', (v, w, h) => {
    const g = geo(v, w, h);
    for (const s of g.segments) {
      for (const x of [s.x1, s.x2]) expect(x >= 0 && x <= w).toBe(true);
      for (const y of [s.y1, s.y2]) expect(y >= 0 && y <= h).toBe(true);
    }
    for (const b of g.blocks) {
      expect(b.x >= 0 && b.y >= 0).toBe(true);
      expect(b.x + b.w <= w + 1e-9 && b.y + b.h <= h + 1e-9).toBe(true);
    }
  });

  it.each(CASES)('%s at %i×%i: stroke hierarchy within the brief (primary 0.5–0.75u, secondary 0.25–0.5u)', (v, w, h) => {
    const g = geo(v, w, h);
    expect(g.primary / g.u).toBeGreaterThanOrEqual(0.5);
    expect(g.primary / g.u).toBeLessThanOrEqual(0.75);
    expect(g.secondary / g.u).toBeGreaterThanOrEqual(0.25);
    expect(g.secondary / g.u).toBeLessThanOrEqual(0.5);
  });

  it.each(CASES)('%s at %i×%i: the content field is never touched by structure, with ≥ 2u around it', (v, w, h) => {
    const g = geo(v, w, h);
    expect(g.content.w).toBeGreaterThan(0);
    expect(g.content.h).toBeGreaterThan(0);
    expect(touches(g, g.content)).toBe(false);
    const m = (MIN_PADDING_U - 0.01) * g.u;
    const grown = { x: g.content.x - m, y: g.content.y - m, w: g.content.w + 2 * m, h: g.content.h + 2 * m };
    expect(touches(g, grown)).toBe(false);
  });

  it('the u of each test size is the rail index width of that size', () => {
    expect(SIZES.map(([w]) => UNIT[densityFor(w)])).toEqual([UNIT.compact, UNIT.regular, UNIT.expanded]);
  });
});

describe('DA-02.3 — each candidate carries its one structural idea, no more', () => {
  it('A: one recessed field, four corner reinforcements, one break in the perimeter', () => {
    const g = geo('recessed', 390, 220);
    expect(g.blocks.filter((b) => b.role === 'field')).toHaveLength(1);
    expect(g.blocks.filter((b) => b.role === 'structure')).toHaveLength(8); // 4 corners × 2 legs
    expect(g.segments).toHaveLength(5); // 4 edges, the top one broken in two
  });

  it('B: the notch is exactly one slot wide — the markers\' targeting slot — and on the grid', () => {
    const g = geo('indexed', 390, 220);
    // the notch walls: the only short vertical segments hanging from the top edge
    const walls = g.segments.filter((s) => s.x1 === s.x2 && Math.max(s.y1, s.y2) < g.u * 3);
    expect(walls).toHaveLength(2);
    const [a, b] = walls.map((s) => s.x1).sort((x, y) => x - y);
    expect(b - a).toBeCloseTo(SLOT * g.u, 9);
    expect(a / g.u).toBeCloseTo(Math.round(a / g.u), 9);
    expect(g.blocks).toHaveLength(0);
  });

  it('C: the mounting rail is one index thick and its two registration marks are one index wide', () => {
    const g = geo('rail', 390, 220);
    const [rail, ...marks] = g.blocks;
    expect(rail.h).toBeCloseTo(g.u, 9);
    expect(rail.w).toBe(g.width);
    expect(marks).toHaveLength(2);
    for (const m of marks) expect(m.w).toBeCloseTo(g.u, 9);
  });

  it('D: one reinforced spine, one interruption on the opposite side, nothing else', () => {
    const g = geo('faceplate', 390, 220);
    expect(g.blocks.every((b) => b.x === 0 && b.y === 0)).toBe(true);
    const right = g.segments.filter((s) => s.x1 === s.x2 && s.x1 > g.width / 2);
    expect(right).toHaveLength(2); // the right edge, broken once
    expect(g.content.w / g.width).toBeGreaterThan(0.8);
  });

  it('no candidate carries colour: geometry is roles only', () => {
    for (const v of VARIANTS) expect(JSON.stringify(geo(v, 390, 220))).not.toMatch(/#|rgb|fill|stroke/);
  });
});
