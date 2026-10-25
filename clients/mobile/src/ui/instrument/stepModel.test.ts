import { CALIBRATION_LINE_DEMO } from '../contract/fixtures';
import { ACTION_HEIGHT } from '../theme';
import { neighborStep, stepControlsLayout, stepLabel, stepText } from './stepModel';

const { steps, stepValues } = CALIBRATION_LINE_DEMO;
const at = (kg: number) => steps[stepValues.indexOf(kg)];

describe('DA-02.4B.3 — a press selects exactly one supplied step', () => {
  it('− selects the step just before, + the step just after', () => {
    expect(neighborStep(steps, stepValues, at(75), -1)).toEqual({ position: at(72.5), delta: -2.5 });
    expect(neighborStep(steps, stepValues, at(75), 1)).toEqual({ position: at(77.5), delta: 2.5 });
  });

  it('nothing past either end: the button has no step to select', () => {
    expect(neighborStep(steps, stepValues, at(55), -1)).toBeNull();
    expect(neighborStep(steps, stepValues, at(85), 1)).toBeNull();
  });

  it('a position between two steps is read as the nearest one first (the rail snaps the same way)', () => {
    const between = (at(75) + at(77.5)) / 2 - 0.001;
    expect(neighborStep(steps, stepValues, between, 1)?.position).toBe(at(77.5));
  });

  it('without steps there is no control to press', () => {
    expect(neighborStep(undefined, undefined, 0.5, 1)).toBeNull();
    expect(neighborStep([], [], 0.5, -1)).toBeNull();
  });

  it('the step it moves by is read from the supplied values, never computed', () => {
    const irregular = [0, 0.4, 1];
    const values = [50, 52, 60];
    expect(neighborStep(irregular, values, 0.4, 1)?.delta).toBe(8);
    expect(neighborStep(irregular, values, 0.4, -1)?.delta).toBe(-2);
    expect(neighborStep(irregular, undefined, 0.4, 1)?.delta).toBeNull();
  });
});

describe('DA-02.4B.3 — what the controls say', () => {
  it('the button shows the step it moves by', () => {
    expect(stepText(neighborStep(steps, stepValues, at(75), 1))).toBe('2,5');
    expect(stepText(null)).toBeNull();
  });

  it('assistive technologies hear the action and its size, in French', () => {
    expect(stepLabel(-1, neighborStep(steps, stepValues, at(75), -1), 'kg')).toBe('Diminuer de 2,5 kilos');
    expect(stepLabel(1, neighborStep(steps, stepValues, at(75), 1), 'kg')).toBe('Augmenter de 2,5 kilos');
    expect(stepLabel(1, null, 'kg')).toBe('Augmenter la charge');
  });
});

describe('DA-02.4B.3 — the controls never move', () => {
  it.each([390, 320])('%i: big, grouped toward the centre, under the frame, a thumb-sized target', (width) => {
    const l = stepControlsLayout(width);
    expect(l.decrement.h).toBe(ACTION_HEIGHT);
    expect(l.decrement.w).toBeGreaterThanOrEqual(44);
    expect(l.decrement.y).toBeGreaterThan(0);
    expect(l.decrement.x).toBeGreaterThan(0);
    expect(l.increment.x + l.increment.w).toBeLessThan(width);
    // grouped toward the centre: the same margin on both sides, the pair centred
    expect(l.decrement.x).toBe(width - (l.increment.x + l.increment.w));
    expect(l.increment.x).toBeGreaterThan(l.decrement.x + l.decrement.w);
  });

  it('the geometry depends on the width only — not on the value, the state or the scenario', () => {
    expect(stepControlsLayout(390)).toEqual(stepControlsLayout(390));
    expect(stepControlsLayout.length).toBe(1);
  });
});
