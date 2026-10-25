import type { TextStyle } from 'react-native';

import { type } from '../theme';

/**
 * DA-02.5 — a window's value is as large as it can be (operator, 2026-10-25: « les
 * valeurs les plus grosses possibles »): the largest EXISTING numeral role that fits the
 * window's content, never a new size. The estimate is deliberately generous; the review
 * capture then checks in the rendered page that no value is cut.
 */
export const VALUE_ROLES: readonly TextStyle[] = [type.readout, type.figure, type.exercise];

/** Average advance of a digit, as a share of the font size (tabular numerals). */
const DIGIT_ADVANCE = 0.62;
/** The unit is set at this share of the value's size. */
export const UNIT_SCALE = 0.4;
/** The label line above the value (`type.eyebrow`) and the gap under it. */
const LABEL_BLOCK = 16 + 4;

export function valueLineHeight(role: TextStyle): number {
  return Math.round((role.fontSize ?? 40) * 1.05);
}

export function largestValueRole(contentW: number, contentH: number, value: string, unit: string): TextStyle {
  for (const role of VALUE_ROLES) {
    const fs = role.fontSize ?? 40;
    const width = value.length * DIGIT_ADVANCE * fs + (unit.length + 1) * DIGIT_ADVANCE * fs * UNIT_SCALE;
    if (width <= contentW && LABEL_BLOCK + valueLineHeight(role) <= contentH) return role;
  }
  return VALUE_ROLES[VALUE_ROLES.length - 1];
}
