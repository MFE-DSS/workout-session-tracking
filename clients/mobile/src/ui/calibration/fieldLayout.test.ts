import { packLabels } from './CalibrationField';
import { FIELD_SCALE, fieldLayout } from './fieldLayout';
import { ACTIVE_CURSOR, REFERENCE_MARKER } from './geometry';
import { type Boundaries, densityFor, UNIT } from './layout';

const B: Boundaries = { lowBoundary: 0, targetLowBoundary: 0.45, targetHighBoundary: 0.55, highCostBoundary: 0.8 };
const STEPS = Array.from({ length: 13 }, (_, i) => i / 12);
const base = { ...B, steps: STEPS, referencePosition: 0.5 };

describe('Calibration FIELD — the rail as the frame background', () => {
  it.each([180, 320, 390])('at %i px: one bar per step, all hanging from the same top', (w) => {
    const l = fieldLayout({ ...base, width: w, height: 160, selectedPosition: 0.75 });
    expect(l.bars).toHaveLength(STEPS.length);
    expect(new Set(l.bars.map((b) => b.y1)).size).toBe(1);
  });

  it('the cursor slot grips the chosen bar; the reference slot grips the prescription bar', () => {
    const l = fieldLayout({ ...base, width: 390, height: 180, selectedPosition: 0.75 });
    const chosen = l.bars.find((b) => b.selected)!;
    const ref = l.bars.find((b) => b.reference)!;
    expect(chosen.x).toBe(l.selectedX);
    expect(ref.x).toBe(l.referenceX);
    expect(chosen.y1).toBeLessThan(l.cursorTop + ACTIVE_CURSOR.slotDepth * l.u); // the bar enters the cursor slot
    expect(ref.y2).toBeCloseTo(l.referenceTop + REFERENCE_MARKER.slotDepth * l.u, 9); // down to the reference slot floor
  });

  it('the lit bars are exactly the ones from the prescription to the decision, on either side', () => {
    const up = fieldLayout({ ...base, width: 390, height: 180, selectedPosition: 0.75 });
    expect(up.bars.filter((b) => b.lit).map((b) => b.x)).toEqual(
      up.bars.filter((b) => b.x >= up.referenceX && b.x <= up.selectedX).map((b) => b.x),
    );
    const down = fieldLayout({ ...base, width: 390, height: 180, selectedPosition: 0.2 });
    expect(down.bars.filter((b) => b.lit).every((b) => b.x >= down.selectedX && b.x <= down.referenceX)).toBe(true);
    const exact = fieldLayout({ ...base, width: 390, height: 180, selectedPosition: 0.5 });
    expect(exact.bars.filter((b) => b.lit)).toHaveLength(1);
  });

  it('each zone keeps a signature without colour: bar length, and the HIGH COST lean', () => {
    const l = fieldLayout({ ...base, width: 390, height: 180, selectedPosition: 0.5 });
    const len = (z: string) => Math.max(...l.bars.filter((b) => b.zone === z).map((b) => b.y2 - b.y1));
    expect(len('EASY')).toBeLessThan(len('PUSH'));
    expect(len('PUSH')).toBeLessThan(len('TARGET'));
    expect(l.bars.filter((b) => b.zone === 'HIGH_COST').every((b) => b.lean > 0)).toBe(true);
    expect(l.bars.filter((b) => b.zone !== 'HIGH_COST').every((b) => b.lean === 0)).toBe(true);
  });

  it('a finger anywhere reports a step — the metronome moves by clicks, never between two', () => {
    const l = fieldLayout({ ...base, width: 390, height: 180, selectedPosition: 0.5 });
    for (let x = -20; x <= 410; x += 9) expect(STEPS).toContain(l.positionAt(x));
  });

  it('the field is the cockpit size: twice the rail unit, at every width', () => {
    for (const w of [180, 320, 390]) {
      const l = fieldLayout({ ...base, width: w, height: 300, selectedPosition: 0.5 });
      expect(l.u).toBe(FIELD_SCALE * UNIT[densityFor(w)]);
    }
    expect(FIELD_SCALE).toBe(2);
  });

  it('zone names never overlap and stay inside the field, even around a narrow TARGET', () => {
    for (const w of [240, 320, 390]) {
      const l = fieldLayout({ ...base, width: w, height: 300, selectedPosition: 0.5 });
      const boxes = packLabels(l.segments, w);
      expect(boxes.map((b) => b.zone)).toEqual(['EASY', 'TARGET', 'PUSH', 'HIGH_COST']);
      for (let k = 1; k < boxes.length; k++) {
        expect(boxes[k].left).toBeGreaterThanOrEqual(boxes[k - 1].left + boxes[k - 1].width - 1e-9);
      }
      expect(boxes[boxes.length - 1].left + boxes[boxes.length - 1].width).toBeLessThanOrEqual(w + 1e-9);
    }
  });

  it('holds no colour', () => {
    expect(JSON.stringify(fieldLayout({ ...base, width: 390, height: 180, selectedPosition: 0.6 }))).not.toMatch(/#|rgb/);
  });
});
