import { type } from '../theme';
import { chooseFittedRole, LABEL_BLOCK, NUMERAL_ROLES, readoutLineHeight, UNIT_SCALE, unitSize } from './readoutModel';

describe('DA-02.6 — the Numeric Readout, its locked rules', () => {
  it('the numeral roles are the existing tokens, largest first', () => {
    expect(NUMERAL_ROLES).toEqual([type.readout, type.figure, type.exercise]);
  });

  it('the unit is 0.4 × the value, the line box 1.05 × (operator: the unit after, small)', () => {
    expect(UNIT_SCALE).toBe(0.4);
    expect(unitSize(type.readout)).toBe(27);
    expect(readoutLineHeight(type.readout)).toBe(71);
    expect(readoutLineHeight(type.figure)).toBe(42);
  });
});

describe('DA-02.6 — the role is chosen from MEASURED widths', () => {
  const widths = [170, 100, 75]; // the value rendered at 68 / 40 / 30

  it('the largest role whose measured width fits', () => {
    expect(chooseFittedRole(widths, 200, 200, true)).toBe(0);
    expect(chooseFittedRole(widths, 160, 200, true)).toBe(1);
    expect(chooseFittedRole(widths, 90, 200, true)).toBe(2);
  });

  it('a short window steps down on height, label included', () => {
    expect(chooseFittedRole(widths, 400, readoutLineHeight(type.readout) + LABEL_BLOCK, true)).toBe(0);
    expect(chooseFittedRole(widths, 400, readoutLineHeight(type.readout) + LABEL_BLOCK - 1, true)).toBe(1);
    expect(chooseFittedRole(widths, 400, readoutLineHeight(type.readout), false)).toBe(0);
  });

  it('the smallest role is the floor: never a new, smaller size', () => {
    expect(chooseFittedRole(widths, 10, 10, true)).toBe(NUMERAL_ROLES.length - 1);
  });
});
