import type { TextStyle } from 'react-native';

import { type } from '../theme';

/**
 * DA-02.6 — the Numeric Readout system, its pure part.
 *
 * Operator rulings (2026-10-25): the unit FOLLOWS the value, small, on the same line;
 * the decimal part stays the SAME size as the integer. What this sprint changes is how
 * the size is chosen: by MEASURING the rendered width, not by estimating it.
 */

/** The numeral roles, largest first — existing tokens only, never a new size. */
export const NUMERAL_ROLES: readonly TextStyle[] = [type.readout, type.figure, type.exercise];

/** The unit is set at this share of the value's size (the locked rule of every readout). */
export const UNIT_SCALE = 0.4;

/** A readout's line box: 1.05 × its size — the unit's own line box never makes it taller. */
export function readoutLineHeight(role: TextStyle): number {
  return Math.round((role.fontSize ?? 40) * 1.05);
}

export function unitSize(role: TextStyle): number {
  return Math.round((role.fontSize ?? 40) * UNIT_SCALE);
}

/** The label line above a value (`type.eyebrow`) and the gap under it. */
export const LABEL_BLOCK = 16 + 4;

/**
 * The largest role whose MEASURED width fits `maxWidth` and whose line fits `maxHeight`
 * (with its label when it has one). `widths[i]` is the rendered width of the value at
 * `NUMERAL_ROLES[i]`; the smallest role is the floor.
 */
export function chooseFittedRole(widths: readonly number[], maxWidth: number, maxHeight: number, hasLabel: boolean): number {
  for (let i = 0; i < NUMERAL_ROLES.length; i++) {
    const h = readoutLineHeight(NUMERAL_ROLES[i]) + (hasLabel ? LABEL_BLOCK : 0);
    if (widths[i] <= maxWidth && h <= maxHeight) return i;
  }
  return NUMERAL_ROLES.length - 1;
}
