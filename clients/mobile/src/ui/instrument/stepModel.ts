/**
 * DA-02.4B.3 — the step controls' pure part: which step a press selects, how the
 * buttons are laid out, and what they say. Nothing here computes a domain step: the
 * previous / next one is read from the supplied `steps` (and `stepValues`), which the
 * domain owns.
 */
import { densityFor, formatValue, nearestStep, UNIT } from '../calibration/layout';
import { ACTION_HEIGHT } from '../theme';

export type Direction = -1 | 1;

/** The step a press selects, and the value it moves by (when the values are known). */
export type StepMove = { position: number; delta: number | null };

/**
 * The supplied step immediately before (`-1`) or after (`+1`) the selected one;
 * `null` at either end, or when there are no steps.
 */
export function neighborStep(
  steps: readonly number[] | undefined,
  stepValues: readonly number[] | undefined,
  selectedPosition: number,
  dir: Direction,
): StepMove | null {
  if (!steps?.length) return null;
  const pairs = steps.map((s, i) => ({ s, v: stepValues?.[i] })).sort((a, b) => a.s - b.s);
  const sorted = pairs.map((p) => p.s);
  const at = sorted.indexOf(nearestStep(selectedPosition, sorted));
  const next = pairs[at + dir];
  if (!next) return null;
  const from = pairs[at].v;
  return { position: next.s, delta: next.v !== undefined && from !== undefined ? next.v - from : null };
}

const UNIT_SPOKEN: Record<string, string> = { kg: 'kilos' };

/** « Diminuer de 2,5 kilos » · « Augmenter de 2,5 kilos »; without a value: « Diminuer la charge ». */
export function stepLabel(dir: Direction, move: StepMove | null, unit?: string): string {
  const verb = dir < 0 ? 'Diminuer' : 'Augmenter';
  if (!move || move.delta === null) return `${verb} la charge`;
  const spoken = unit ? ` ${UNIT_SPOKEN[unit] ?? unit}` : '';
  return `${verb} de ${formatValue(Math.abs(move.delta))}${spoken}`;
}

/** What the button shows next to its glyph: the step it moves by, or nothing. */
export function stepText(move: StepMove | null): string | null {
  return move && move.delta !== null ? formatValue(Math.abs(move.delta)) : null;
}

export type ControlBox = { x: number; y: number; w: number; h: number };

/**
 * Two buttons under the frame, grouped toward the centre (operator, 2026-10-25:
 * « beaucoup plus gros », « plutôt vers le centre »). Geometry depends on the width
 * only: it never moves between REST and ADJUSTING, or from one value to the next.
 */
export function stepControlsLayout(width: number) {
  const u = UNIT[densityFor(width)];
  const gapTop = 2 * u;
  const h = ACTION_HEIGHT;
  const w = Math.round(width * 0.35);
  const gap = 4 * u;
  const x0 = Math.round((width - 2 * w - gap) / 2);
  const decrement: ControlBox = { x: x0, y: gapTop, w, h };
  const increment: ControlBox = { x: x0 + w + gap, y: gapTop, w, h };
  return { u, height: gapTop + h, stroke: 0.35 * u, decrement, increment };
}
