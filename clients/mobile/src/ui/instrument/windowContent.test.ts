import { type } from '../theme';
import { largestValueRole, VALUE_ROLES } from './windowContent';

describe('DA-02.5 — a window value is as large as it fits, in an existing role', () => {
  it('a wide, tall window takes the readout role', () => {
    expect(largestValueRole(320, 150, '72,5', 'kg')).toBe(type.readout);
  });

  it('a narrower window steps down to the next existing role, never a new size', () => {
    expect(largestValueRole(150, 150, '72,5', 'kg')).toBe(type.figure);
    expect(largestValueRole(110, 150, '72,5', 'kg')).toBe(type.exercise);
  });

  it('a short window steps down on height too', () => {
    expect(largestValueRole(320, 70, '72,5', 'kg')).toBe(type.figure);
  });

  it('every role it can return is an existing token', () => {
    expect(VALUE_ROLES).toEqual([type.readout, type.figure, type.exercise]);
  });
});
