import { MASTER_ZONES } from './masterGeometry';
import { triptychLayout, zoneGridHeight, zoneGridLayout, zoneGridShape } from './triptychLayout';
import { cameraFor, presetById, presetForZone, PUSH_A_PRESETS, ZONE_PRESETS } from './viewPresets';

const ASPECTS = [195 / 162, 96 / 106, 195 / 186, 124 / 66, 1, 0.5, 3];

describe('DA-04.1 — BodyMap cameras', () => {
  it('names exactly the three Push A presets, each on an existing zone', () => {
    expect(PUSH_A_PRESETS.map((p) => p.id)).toEqual(['push-pecs', 'push-delt-lat', 'push-triceps']);
    for (const p of PUSH_A_PRESETS) expect(MASTER_ZONES[p.zone].some((q) => q.side === p.side)).toBe(true);
  });

  it('shows pecs and the lateral deltoid from the front, the triceps from the back', () => {
    expect(presetById('push-pecs').side).toBe('front');
    expect(presetById('push-delt-lat').side).toBe('front');
    expect(presetById('push-triceps').side).toBe('back');
  });

  it('is deterministic and matches the window aspect', () => {
    for (const p of PUSH_A_PRESETS) {
      for (const a of ASPECTS) {
        const c = cameraFor(p, a);
        expect(cameraFor(p, a)).toEqual(c);
        expect(Math.abs(c.w / c.h - a)).toBeLessThan(0.01);
      }
    }
  });

  it('never cuts the preset box and never leaves its own half of the master', () => {
    for (const p of PUSH_A_PRESETS) {
      const lo = p.side === 'front' ? 0 : 120;
      for (const a of ASPECTS) {
        const c = cameraFor(p, a);
        expect(c.x).toBeLessThanOrEqual(p.frame.x + 1e-3);
        expect(c.y).toBeLessThanOrEqual(p.frame.y + 1e-3);
        expect(c.x + c.w).toBeGreaterThanOrEqual(p.frame.x + p.frame.w - 1e-3);
        expect(c.y + c.h).toBeGreaterThanOrEqual(p.frame.y + p.frame.h - 1e-3);
        expect(c.x).toBeGreaterThanOrEqual(lo);
        expect(c.x + c.w).toBeLessThanOrEqual(lo + 120 + 1e-3);
      }
    }
  });
});

describe('DA-04.1 — T1 triptych layout', () => {
  const content = { x: 0, y: 0, w: 371.2, h: 152.2 };
  const u = 4;
  const b = triptychLayout(content, u);

  it('three windows, inside the content, exactly 2u apart, filling its width', () => {
    expect(b).toHaveLength(3);
    for (const w of b) {
      expect(w.y).toBe(0);
      expect(w.h).toBe(content.h);
    }
    expect(b[1].x - (b[0].x + b[0].w)).toBe(2 * u);
    expect(b[2].x - (b[1].x + b[1].w)).toBeCloseTo(2 * u);
    expect(b[2].x + b[2].w).toBeCloseTo(content.w);
  });

  it('equal weight: only the rounding remainder (under 2 px) separates the widths', () => {
    const widths = b.map((w) => w.w);
    expect(Math.max(...widths) - Math.min(...widths)).toBeLessThan(2);
  });
});

describe('DA-04.2 — every zone, every session', () => {
  it('one camera per zone of the master, each zone once', () => {
    expect(ZONE_PRESETS.map((p) => p.zone).sort()).toEqual(Object.keys(MASTER_ZONES).sort());
    for (const z of Object.keys(MASTER_ZONES)) expect(presetForZone(z)?.zone).toBe(z);
    expect(presetForZone('unknown')).toBeUndefined();
  });

  it('three zones give exactly the locked T1', () => {
    const content = { x: 0, y: 0, w: 371.2, h: 152.2 };
    expect(zoneGridLayout(3, content, 4)).toEqual(triptychLayout(content, 4));
    expect(zoneGridHeight(3)).toBe(180);
  });

  it('at most three per row, rows balanced', () => {
    expect([1, 2, 3, 4, 5, 6, 7].map((n) => zoneGridShape(n))).toEqual([
      { rows: 1, cols: 1 },
      { rows: 1, cols: 2 },
      { rows: 1, cols: 3 },
      { rows: 2, cols: 2 },
      { rows: 2, cols: 3 },
      { rows: 2, cols: 3 },
      { rows: 3, cols: 3 },
    ]);
  });

  it('windows equal and inside the content for every count', () => {
    for (const n of [1, 2, 4, 5, 6, 7]) {
      const content = { x: 0, y: 0, w: 371.2, h: zoneGridHeight(n) - 27.8 };
      const b = zoneGridLayout(n, content, 4);
      expect(b).toHaveLength(n);
      expect(new Set(b.map((w) => w.w * 10000 + w.h)).size).toBe(1);
      for (const w of b) {
        expect(w.x + w.w).toBeLessThanOrEqual(content.w + 1e-6);
        expect(w.y + w.h).toBeLessThanOrEqual(content.h + 1e-6);
      }
    }
  });
});
