/**
 * DA-02.2 — the Calibration Rail laid out from a WIDTH, never stretched.
 *
 * Pure presentation: every position, boundary and step comes from the caller
 * (the domain layer, `VNEXT §8.11`). Nothing here knows what a prescription is
 * or where a threshold should be; it only places what it is given, and says in
 * words what the picture shows.
 *
 * An index of the rail is exactly one `u` wide: the width of the markers' slot.
 * When the caller supplies the selectable `steps`, every step is an index and
 * the cursor lands on one, so its slot is always filled by the index it frames.
 */
import { ACTIVE_CURSOR, REFERENCE_MARKER } from './geometry';

export type Density = 'compact' | 'regular' | 'expanded';
export type Zone = 'EASY' | 'TARGET' | 'PUSH' | 'HIGH_COST';

/** Normalized 0..1, ascending: EASY [low, targetLow) · TARGET [targetLow, targetHigh] · PUSH (targetHigh, highCost) · HIGH_COST [highCost, 1]. */
export type Boundaries = {
  lowBoundary: number;
  targetLowBoundary: number;
  targetHighBoundary: number;
  highCostBoundary: number;
};

/** AUREN_CALIBRATION_SYSTEM §7. */
export function densityFor(width: number): Density {
  if (width >= 360) return 'expanded';
  if (width >= 240) return 'regular';
  return 'compact';
}

/** The grid unit per density = the width of one rail index, in px. */
export const UNIT: Record<Density, number> = { compact: 2, regular: 3, expanded: 4 };

/** Without supplied steps: index spacing in px, recomputed per width (never a scaled drawing). */
const FREE_STEP: Record<Density, number> = { compact: 24, regular: 16, expanded: 20 };
const MAJOR_EVERY = 2;

export function clamp01(v: number): number {
  if (!Number.isFinite(v)) return 0;
  return Math.min(1, Math.max(0, v));
}

/** Which locked zone a position falls in; `null` below the model's low boundary. */
export function zoneAt(p: number, b: Boundaries): Zone | null {
  const x = clamp01(p);
  if (x < clamp01(b.lowBoundary)) return null;
  if (x < clamp01(b.targetLowBoundary)) return 'EASY';
  if (x <= clamp01(b.targetHighBoundary)) return 'TARGET';
  if (x < clamp01(b.highCostBoundary)) return 'PUSH';
  return 'HIGH_COST';
}

/** The supplied step nearest to `p` (the cursor never rests between two indexes). */
export function nearestStep(p: number, steps: readonly number[]): number {
  let best = steps[0];
  for (const s of steps) if (Math.abs(s - p) < Math.abs(best - p)) best = s;
  return best;
}

/** Signature of a zone WITHOUT colour (AUREN_CALIBRATION_SYSTEM §2, §9). */
export type TickStyle = 'neutral' | 'short' | 'normal' | 'strong' | 'diagonal';
const STYLE: Record<Zone, TickStyle> = { EASY: 'short', TARGET: 'normal', PUSH: 'strong', HIGH_COST: 'diagonal' };

export type Tick = {
  x: number;
  major: boolean;
  zone: Zone | null;
  style: TickStyle;
  /** top of the index (the bottom is the baseline) */
  y1: number;
  /** horizontal lean of the top end: non-zero only for the HIGH COST hatch */
  lean: number;
  /** a hatch stroke between two indexes, not a selectable index */
  hatch: boolean;
};

export type RailLayout = {
  width: number;
  density: Density;
  u: number;
  height: number;
  baselineY: number;
  trackStart: number;
  trackEnd: number;
  referenceX: number;
  selectedX: number;
  selectedZone: Zone | null;
  cursorTop: number;
  referenceTop: number;
  /** the reference index, from the baseline into the marker's slot */
  referenceTick: { x: number; y1: number; y2: number };
  /** the selected index, framed by the cursor's slot */
  selectedTick: { x: number; y1: number; y2: number };
  segments: { zone: Zone; x1: number; x2: number }[];
  /** the zone band under the baseline: each range drawn as a flat strip carrying its pattern */
  band: { y: number; height: number } | null;
  /** the boundaries between two ranges — calibration brackets across the band */
  brackets: number[];
  ticks: Tick[];
  /** expanded only: the value printed under each major index (never inside an asset) */
  scale: { x: number; text: string }[];
  /** px → normalized position, for a finger on the rail */
  positionAt: (x: number) => number;
};

export type RailInput = Boundaries & {
  width: number;
  density?: Density;
  referencePosition: number;
  selectedPosition: number;
  /** the selectable values, normalized 0..1 — one index each */
  steps?: readonly number[];
  /** the value each step stands for, same order as `steps` — for the printed scale */
  stepValues?: readonly number[];
};

export function railLayout(input: RailInput): RailLayout {
  const density = input.density ?? densityFor(input.width);
  const u = UNIT[density];
  // half the markers' width on each side, so a marker at 0 or 1 is never clipped
  const pad = (Math.max(REFERENCE_MARKER.width, ACTIVE_CURSOR.width) / 2) * u + 1;
  const trackStart = pad;
  const trackEnd = Math.max(pad, input.width - pad);
  const span = Math.max(1, trackEnd - trackStart);
  const xAt = (p: number) => trackStart + clamp01(p) * (trackEnd - trackStart);

  // vertical: the cursor's slot spans exactly the index band above the baseline
  const cursorTop = 0;
  const baselineY = ACTIVE_CURSOR.slotDepth * u;
  const majorH = indexHeight('normal', true, u);
  const referenceTop = cursorTop + ACTIVE_CURSOR.height * u + 1.2 * u;
  const height = referenceTop + REFERENCE_MARKER.height * u;

  const pairs = input.steps?.length
    ? input.steps.map((s, i) => ({ s: clamp01(s), v: input.stepValues?.[i] })).sort((a, b) => a.s - b.s)
    : null;
  const steps = pairs ? pairs.map((p) => p.s) : null;
  const snap = (p: number) => (steps ? nearestStep(clamp01(p), steps) : clamp01(p));
  const referencePos = snap(input.referencePosition);
  const selectedPos = snap(input.selectedPosition);
  const referenceX = xAt(referencePos);
  const selectedX = xAt(selectedPos);
  const showRanges = density !== 'compact';

  const segments = showRanges ? segmentsOf(input, xAt) : [];
  const positions = steps
    ? steps.map((s, i) => ({ x: xAt(s), k: i - steps.indexOf(referencePos) }))
    : freeGrid(referenceX, trackStart, trackEnd, FREE_STEP[density]);
  const ticks = ticksOf(positions, {
    zoneOf: (x) => (showRanges ? zoneAt((x - trackStart) / span, input) : null),
    allMajor: density === 'compact',
    u,
    baselineY,
  });
  const band = showRanges ? { y: baselineY + 1, height: 2.2 * u } : null;
  const brackets = segments.slice(1).map((s) => s.x1);
  const scale =
    density === 'expanded' && pairs
      ? ticks
          .filter((t) => t.major && !t.hatch)
          .flatMap((t) => {
            const v = pairs.find((p) => xAt(p.s) === t.x)?.v;
            return v === undefined ? [] : [{ x: t.x, text: formatValue(v) }];
          })
      : [];

  return {
    width: input.width,
    density,
    u,
    height,
    baselineY,
    trackStart,
    trackEnd,
    referenceX,
    selectedX,
    selectedZone: zoneAt(selectedPos, input),
    cursorTop,
    referenceTop,
    referenceTick: { x: referenceX, y1: baselineY, y2: referenceTop + REFERENCE_MARKER.slotDepth * u },
    selectedTick: { x: selectedX, y1: baselineY - majorH, y2: baselineY },
    segments,
    band,
    brackets,
    ticks,
    scale,
    positionAt: (x: number) => snap((x - trackStart) / span),
  };
}

/** The four ranges, contiguous, in the locked order; an empty range is skipped. */
function segmentsOf(b: Boundaries, xAt: (p: number) => number): RailLayout['segments'] {
  const x = [b.lowBoundary, b.targetLowBoundary, b.targetHighBoundary, b.highCostBoundary, 1].map(xAt);
  const zones: Zone[] = ['EASY', 'TARGET', 'PUSH', 'HIGH_COST'];
  return zones.flatMap((zone, i) => (x[i + 1] > x[i] ? [{ zone, x1: x[i], x2: x[i + 1] }] : []));
}

/** Without supplied steps: a regular grid in px, anchored on the reference (k = 0). */
function freeGrid(referenceX: number, start: number, end: number, step: number): { x: number; k: number }[] {
  const out: { x: number; k: number }[] = [];
  for (let k = Math.ceil((start - referenceX) / step); k <= Math.floor((end - referenceX) / step); k++) {
    out.push({ x: referenceX + k * step, k });
  }
  return out;
}

/** Index height per zone signature: EASY short points · PUSH affirmed · the rest plain. */
function indexHeight(style: TickStyle, major: boolean, u: number): number {
  if (style === 'short') return major ? 1.8 * u : 0.9 * u;
  if (style === 'strong') return major ? 3.2 * u : 2.6 * u;
  return major ? 3.2 * u : 1.8 * u;
}

function ticksOf(
  positions: { x: number; k: number }[],
  o: { zoneOf: (x: number) => Zone | null; allMajor: boolean; u: number; baselineY: number },
): Tick[] {
  const lean = 1.2 * o.u;
  return positions.flatMap(({ x, k }, i) => {
    const major = o.allMajor || k % MAJOR_EVERY === 0;
    const zone = o.zoneOf(x);
    const style: TickStyle = zone ? STYLE[zone] : 'neutral';
    const index: Tick = {
      x, major, zone, style,
      y1: o.baselineY - indexHeight(style, major, o.u),
      lean: style === 'diagonal' ? lean : 0,
      hatch: false,
    };
    const next = positions[i + 1];
    if (style !== 'diagonal' || !next) return [index];
    // HIGH COST: a hatch, one extra diagonal stroke between two indexes
    const hatch: Tick = { x: (x + next.x) / 2, major: false, zone, style, y1: o.baselineY - 1.8 * o.u, lean, hatch: true };
    return [index, hatch];
  });
}

// ── words: the rail is never read by colour alone ───────────────────────────

const NUMBER = new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 2 });

export function formatValue(v: number): string {
  return NUMBER.format(v);
}

/** « +2,5 » · « −2,5 » · « ±0 » */
export function formatDelta(selected: number, reference: number): string {
  const d = Math.round((selected - reference) * 100) / 100;
  if (d === 0) return '±0';
  return `${d > 0 ? '+' : '−'}${NUMBER.format(Math.abs(d))}`;
}

/** The locked zone names, as shown on the instrument. */
export const ZONE_LABEL: Record<Zone, string> = {
  EASY: 'EASY',
  TARGET: 'TARGET',
  PUSH: 'PUSH',
  HIGH_COST: 'HIGH COST',
};

/** What each zone means, spoken — never « danger », « échec » or « réussite ». */
const ZONE_SPOKEN: Record<Zone, string> = {
  EASY: 'plus facile que la prescription',
  TARGET: 'dans la cible',
  PUSH: 'au-dessus de la prescription',
  HIGH_COST: 'coût nettement supérieur à la prescription',
};

const UNIT_SPOKEN: Record<string, string> = { kg: 'kilos' };

/** « Prescription 70 kilos. Choisi 72,5 kilos. Au-dessus de la prescription. » */
export function describeRail(p: { referenceValue?: number; selectedValue?: number; unit?: string; zone: Zone | null }): string {
  const unit = p.unit ? ` ${UNIT_SPOKEN[p.unit] ?? p.unit}` : '';
  const parts: string[] = [];
  if (p.referenceValue !== undefined) parts.push(`Prescription ${formatValue(p.referenceValue)}${unit}.`);
  if (p.selectedValue !== undefined) parts.push(`Choisi ${formatValue(p.selectedValue)}${unit}.`);
  if (p.zone) {
    const z = ZONE_SPOKEN[p.zone];
    parts.push(z.charAt(0).toUpperCase() + z.slice(1) + '.');
  }
  return parts.join(' ');
}
