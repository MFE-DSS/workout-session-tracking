/**
 * Calibration FIELD — the rail as the background of its frame (operator, 2026-10-25,
 * DA-02.3 review): « le rail devrait reprendre complètement la case […] presque en
 * style background, et on bouge le curseur dessus, comme on règle un métronome
 * digital ».
 *
 * Same primitives as the CalibrationRail (LOCKED v1), another layout: every step is
 * a full-length bar hanging from the top, one `u` wide; the zone is said by the
 * bar's LENGTH and colour; the bars from the prescription to the decision are lit
 * — the allocation, visible. The cursor rides the top, its slot gripping the chosen
 * bar; the reference sits at the bottom, its slot gripping the prescription's bar.
 *
 * Pure presentation, like `layout.ts` (not modified): it places what it is given.
 */
import { ACTIVE_CURSOR, REFERENCE_MARKER } from './geometry';
import { type Boundaries, clamp01, densityFor, nearestStep, UNIT, type Zone, zoneAt } from './layout';

export type FieldBar = {
  x: number;
  zone: Zone | null;
  y1: number;
  y2: number;
  /** horizontal lean of the bottom end: HIGH COST only */
  lean: number;
  /** between the prescription and the decision, both included */
  lit: boolean;
  selected: boolean;
  reference: boolean;
};

export type FieldLayout = {
  width: number;
  height: number;
  u: number;
  referenceX: number;
  selectedX: number;
  selectedZone: Zone | null;
  cursorTop: number;
  referenceTop: number;
  bars: FieldBar[];
  /** zone boundaries, as thin full-length registration lines */
  brackets: number[];
  /** the four ranges along the field, for their names */
  segments: { zone: Zone; x1: number; x2: number }[];
  positionAt: (x: number) => number;
};

export type FieldInput = Boundaries & {
  width: number;
  height: number;
  referencePosition: number;
  selectedPosition: number;
  /** the selectable values, normalized 0..1 — one bar each (required: a field is made of steps) */
  steps: readonly number[];
  /** the field's unit; defaults to TWICE the rail's at this width (operator: « deux fois plus gros ») */
  u?: number;
};

/** The field is the cockpit-size rail: twice the line rail's unit (operator review, 2026-10-25). */
export const FIELD_SCALE = 2;

/** Bar length per zone, as a share of the full length: the signature without colour. */
const LENGTH: Record<Zone, number> = { EASY: 0.5, TARGET: 1, PUSH: 0.8, HIGH_COST: 1 };

export function fieldLayout(i: FieldInput): FieldLayout {
  const u = i.u ?? FIELD_SCALE * UNIT[densityFor(i.width)];
  const pad = (Math.max(ACTIVE_CURSOR.width, REFERENCE_MARKER.width) / 2) * u + 1;
  const start = pad;
  const end = Math.max(pad, i.width - pad);
  const span = Math.max(1, end - start);
  const xAt = (p: number) => start + clamp01(p) * span;

  const steps = [...i.steps].map(clamp01).sort((a, b) => a - b);
  const snap = (p: number) => nearestStep(clamp01(p), steps);
  const ref = snap(i.referencePosition);
  const sel = snap(i.selectedPosition);

  // vertical: bars hang from inside the cursor's slot down into the reference's slot
  const cursorTop = 0;
  const referenceTop = i.height - REFERENCE_MARKER.height * u;
  const top = 1 * u; // inside the cursor slot (0 → 4u)
  const full = referenceTop + REFERENCE_MARKER.slotDepth * u - top; // to the reference slot's floor
  const lo = Math.min(ref, sel);
  const hi = Math.max(ref, sel);

  const bars: FieldBar[] = steps.map((s) => {
    const zone = zoneAt(s, i);
    const share = zone ? LENGTH[zone] : 0.5;
    return {
      x: xAt(s),
      zone,
      y1: top,
      y2: top + full * share,
      lean: zone === 'HIGH_COST' ? 1.2 * u : 0,
      lit: s >= lo && s <= hi,
      selected: s === sel,
      reference: s === ref,
    };
  });

  const brackets = [i.targetLowBoundary, i.targetHighBoundary, i.highCostBoundary]
    .filter((b) => b > clamp01(i.lowBoundary) && b < 1)
    .map(xAt);
  const edges = [i.lowBoundary, i.targetLowBoundary, i.targetHighBoundary, i.highCostBoundary, 1].map(xAt);
  const zones: Zone[] = ['EASY', 'TARGET', 'PUSH', 'HIGH_COST'];
  const segments = zones.flatMap((zone, k) =>
    edges[k + 1] > edges[k] ? [{ zone, x1: edges[k], x2: edges[k + 1] }] : [],
  );

  return {
    width: i.width,
    height: i.height,
    u,
    referenceX: xAt(ref),
    selectedX: xAt(sel),
    selectedZone: zoneAt(sel, i),
    cursorTop,
    referenceTop,
    bars,
    brackets,
    segments,
    positionAt: (x: number) => snap((x - start) / span),
  };
}
