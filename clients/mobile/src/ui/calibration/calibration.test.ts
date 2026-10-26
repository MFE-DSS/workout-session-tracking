import { ACTIVE_CURSOR, type MarkerGeometry, NOTCH, polygonPath, REFERENCE_MARKER, SLOT, WALL } from './geometry';
import { type Boundaries, densityFor, describeRail, formatDelta, railLayout, zoneAt } from './layout';

/** The interior walls of the slot: the two vertical edges that bound the opening at the top. */
function slotEdges(g: MarkerGeometry): [number, number] {
  const tops = g.polygon.filter(([, y]) => y === 0).map(([x]) => x).sort((a, b) => a - b);
  // four points at y = 0: outer-left, slot-left, slot-right, outer-right
  return [tops[1], tops[2]];
}

function outerTop(g: MarkerGeometry): [number, number] {
  const tops = g.polygon.filter(([, y]) => y === 0).map(([x]) => x).sort((a, b) => a - b);
  return [tops[0], tops[3]];
}

/** The notch: the two points of the polygon at height − depth. */
function notch(g: MarkerGeometry): number[] {
  return g.polygon.filter(([, y]) => y === g.height - NOTCH.depth).map(([x]) => x).sort((a, b) => a - b);
}

const BOTH: [string, MarkerGeometry][] = [
  ['ReferenceMarker', REFERENCE_MARKER],
  ['ActiveCursor', ACTIVE_CURSOR],
];

describe('DA-02.2 — one manufactured family: the shared invariants', () => {
  it.each(BOTH)('%s: rectilinear, no curve, no diagonal (every edge horizontal or vertical)', (_, g) => {
    const pts = [...g.polygon, g.polygon[0]];
    for (let i = 1; i < pts.length; i++) {
      const [x0, y0] = pts[i - 1];
      const [x1, y1] = pts[i];
      expect(x0 === x1 || y0 === y1).toBe(true);
    }
    expect(polygonPath(g, 4)).not.toMatch(/[CQASTcqast]/);
  });

  it.each(BOTH)('%s: the slot is exactly 1u wide and centred on the axis x = 0', (_, g) => {
    const [l, r] = slotEdges(g);
    expect(r - l).toBe(SLOT);
    expect((l + r) / 2).toBe(0);
  });

  it.each(BOTH)('%s: both walls have the shared thickness', (_, g) => {
    const [ol, or] = outerTop(g);
    const [l, r] = slotEdges(g);
    expect(l - ol).toBe(WALL);
    expect(or - r).toBe(WALL);
  });

  it.each(BOTH)('%s: the same bottom notch, centred', (_, g) => {
    const [a, b] = notch(g);
    expect(b - a).toBeCloseTo(NOTCH.width, 10);
    expect(a + b).toBeCloseTo(0, 10);
  });

  it('operator review 2026-10-25: the same width, the cursor massive and tall, the reference low and flat', () => {
    expect([ACTIVE_CURSOR.width, ACTIVE_CURSOR.height]).toEqual([6, 10]);
    expect([REFERENCE_MARKER.width, REFERENCE_MARKER.height]).toEqual([6, 4]);
    expect(REFERENCE_MARKER.width).toBe(ACTIVE_CURSOR.width);
    expect(WALL).toBeGreaterThan(SLOT); // massive: each wall wider than the slot
  });

  it('they differ by SHAPE, so they stay distinct in a single colour', () => {
    expect(REFERENCE_MARKER.width / REFERENCE_MARKER.height).toBeGreaterThan(1);
    expect(ACTIVE_CURSOR.width / ACTIVE_CURSOR.height).toBeLessThan(1);
    expect(ACTIVE_CURSOR.height).toBeGreaterThanOrEqual(2 * REFERENCE_MARKER.height);
  });

  it('the geometry holds no colour', () => {
    expect(JSON.stringify([REFERENCE_MARKER, ACTIVE_CURSOR])).not.toMatch(/#|fill|stroke|rgb/);
  });
});

const B: Boundaries = { lowBoundary: 0, targetLowBoundary: 0.4, targetHighBoundary: 0.5, highCostBoundary: 0.8 };
const REF = 0.45;
const SCENARIOS = {
  'EXACT TARGET': REF,
  EASY: 0.2,
  PUSH: 0.62,
  'HIGH COST': 0.92,
} as const;
const WIDTHS = [180, 320, 390];

describe('DA-02.2 — the rail places what it is given, at every width', () => {
  it('density follows the locked widths', () => {
    expect([densityFor(180), densityFor(239), densityFor(240), densityFor(359), densityFor(360)]).toEqual([
      'compact', 'compact', 'regular', 'regular', 'expanded',
    ]);
  });

  it.each(WIDTHS)('at %i px, both slots centre on the SAME tick when the decision equals the prescription', (w) => {
    const l = railLayout({ ...B, width: w, referencePosition: REF, selectedPosition: REF });
    expect(l.selectedX).toBe(l.referenceX);
    expect(l.selectedTick.x).toBe(l.referenceTick.x);
    // the index is a real rail tick, and a major one
    const index = l.ticks.find((t) => t.x === l.referenceX);
    expect(index?.major).toBe(true);
    // marker and cursor are placed by their axis: x − half width, at the same unit
    const refLeft = l.referenceX - (REFERENCE_MARKER.width / 2) * l.u;
    const curLeft = l.selectedX - (ACTIVE_CURSOR.width / 2) * l.u;
    expect(refLeft + (REFERENCE_MARKER.width / 2) * l.u).toBe(curLeft + (ACTIVE_CURSOR.width / 2) * l.u);
  });

  it('R2: a host may draw the rail on a larger grid; without one, the density grid (the locked rendering)', () => {
    const at = (gridUnit?: number) => railLayout({ ...B, width: 390, referencePosition: REF, selectedPosition: REF, gridUnit });
    expect(at().u).toBe(4);
    expect(at(6).u).toBe(6);
    expect(at(6).density).toBe('expanded');
    expect(at(6).height / at().height).toBeCloseTo(1.5, 10);
  });

  it.each(WIDTHS)('at %i px, the cursor slot spans exactly the tick band above the baseline', (w) => {
    const l = railLayout({ ...B, width: w, referencePosition: REF, selectedPosition: 0.62 });
    expect(l.baselineY - l.cursorTop).toBe(ACTIVE_CURSOR.slotDepth * l.u);
    const tallest = Math.min(...l.ticks.map((t) => t.y1));
    expect(tallest).toBeGreaterThanOrEqual(l.cursorTop);
    expect(l.referenceTop).toBeGreaterThan(l.cursorTop + ACTIVE_CURSOR.height * l.u);
  });

  it.each(Object.entries(SCENARIOS))('%s is the zone the cursor reads', (name, p) => {
    const expected = { 'EXACT TARGET': 'TARGET', EASY: 'EASY', PUSH: 'PUSH', 'HIGH COST': 'HIGH_COST' }[name];
    expect(zoneAt(p, B)).toBe(expected);
    for (const w of WIDTHS) expect(railLayout({ ...B, width: w, referencePosition: REF, selectedPosition: p }).selectedZone).toBe(expected);
  });

  it('positions are clamped to [0, 1] and stay on the track', () => {
    for (const w of WIDTHS) {
      const lo = railLayout({ ...B, width: w, referencePosition: -3, selectedPosition: 9 });
      expect(lo.referenceX).toBe(lo.trackStart);
      expect(lo.selectedX).toBe(lo.trackEnd);
      for (const t of lo.ticks) {
        expect(t.x).toBeGreaterThanOrEqual(lo.trackStart - 1e-9);
        expect(t.x).toBeLessThanOrEqual(lo.trackEnd + 1e-9);
      }
    }
  });

  it('the drawing is recomputed per width, never stretched: tick spacing in px is constant within a density', () => {
    const narrow = railLayout({ ...B, width: 260, referencePosition: REF, selectedPosition: REF });
    const wide = railLayout({ ...B, width: 350, referencePosition: REF, selectedPosition: REF });
    const gap = (l: typeof narrow) => {
      const xs = l.ticks.filter((t) => !t.hatch).map((t) => t.x).sort((a, b) => a - b);
      const gaps = xs.slice(1).map((x, i) => x - xs[i]);
      expect(Math.max(...gaps) - Math.min(...gaps)).toBeLessThan(1e-9); // one spacing, everywhere
      return gaps[0];
    };
    expect(gap(narrow)).toBeCloseTo(gap(wide), 6);
    expect(wide.ticks.length).toBeGreaterThan(narrow.ticks.length);
  });

  it('compact: baseline and major ticks only, no ranges, no permanent labels', () => {
    const l = railLayout({ ...B, width: 180, referencePosition: REF, selectedPosition: 0.92 });
    expect(l.density).toBe('compact');
    expect(l.segments).toEqual([]);
    expect(l.ticks.every((t) => t.major && t.style === 'neutral')).toBe(true);
  });

  it('regular and expanded: each range has its own tick signature, so colour is never the only carrier', () => {
    for (const w of [320, 390]) {
      const l = railLayout({ ...B, width: w, referencePosition: REF, selectedPosition: REF });
      const styles = new Set(l.ticks.map((t) => `${t.zone}:${t.style}`));
      expect(styles).toEqual(new Set(['EASY:short', 'TARGET:normal', 'PUSH:strong', 'HIGH_COST:diagonal']));
      expect(l.ticks.filter((t) => t.style === 'diagonal').every((t) => t.lean > 0)).toBe(true);
      expect(l.ticks.filter((t) => t.style !== 'diagonal').every((t) => t.lean === 0)).toBe(true);
      // EASY: short points — every EASY index is shorter than the TARGET index of the same rank
      const tallest = (z: string, major: boolean) =>
        Math.max(...l.ticks.filter((t) => t.zone === z && t.major === major && !t.hatch).map((t) => l.baselineY - t.y1));
      expect(tallest('EASY', true)).toBeLessThan(tallest('TARGET', true));
      // HIGH COST: a hatch — more strokes per px than any other range
      const per = (z: string) => {
        const s = l.segments.find((x) => x.zone === z);
        return s ? l.ticks.filter((t) => t.zone === z).length / (s.x2 - s.x1) : 0;
      };
      expect(per('HIGH_COST')).toBeGreaterThan(per('PUSH'));
      expect(l.ticks.some((t) => t.hatch)).toBe(true);
    }
  });

  // operator review 2026-10-25: the cursor lands exactly on an index; a finger snaps to the nearest step
  const STEPS = Array.from({ length: 13 }, (_, i) => i / 12);
  it.each(WIDTHS)('at %i px, with steps, every step is an index and the cursor always rests on one', (w) => {
    for (const p of [0, 0.31, 0.5, 0.74, 1]) {
      const l = railLayout({ ...B, width: w, steps: STEPS, referencePosition: 0.5, selectedPosition: p });
      const indexes = l.ticks.filter((t) => !t.hatch).map((t) => t.x);
      expect(indexes).toHaveLength(STEPS.length);
      expect(indexes).toContain(l.selectedX);
      expect(indexes).toContain(l.referenceX);
    }
  });

  it('a finger anywhere on the rail reports the nearest step, never a position between two', () => {
    const l = railLayout({ ...B, width: 390, steps: STEPS, referencePosition: 0.5, selectedPosition: 0.5 });
    for (let x = 0; x <= 390; x += 7) expect(STEPS).toContain(l.positionAt(x));
    expect(l.positionAt(-50)).toBe(0);
    expect(l.positionAt(999)).toBe(1);
  });

  it('the four ranges are contiguous and in the locked order', () => {
    const l = railLayout({ ...B, width: 390, referencePosition: REF, selectedPosition: REF });
    expect(l.segments.map((s) => s.zone)).toEqual(['EASY', 'TARGET', 'PUSH', 'HIGH_COST']);
    for (let i = 1; i < l.segments.length; i++) expect(l.segments[i].x1).toBe(l.segments[i - 1].x2);
  });
});

describe('DA-02.2 — the rail in words', () => {
  it('says the prescription, the choice and the zone — never danger', () => {
    expect(describeRail({ referenceValue: 70, selectedValue: 72.5, unit: 'kg', zone: 'PUSH' })).toBe(
      'Prescription 70 kilos. Choisi 72,5 kilos. Au-dessus de la prescription.',
    );
    const high = describeRail({ referenceValue: 70, selectedValue: 80, unit: 'kg', zone: 'HIGH_COST' });
    expect(high).not.toMatch(/danger|risque|interdit|blessure/i);
    expect(high).toMatch(/coût/i);
  });

  it('formats the delta with its sign', () => {
    expect(formatDelta(72.5, 70)).toBe('+2,5');
    expect(formatDelta(67.5, 70)).toBe('−2,5');
    expect(formatDelta(70, 70)).toBe('±0');
  });
});
