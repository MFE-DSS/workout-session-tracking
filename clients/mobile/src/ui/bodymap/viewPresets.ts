/**
 * DA-04.1 — BodyMap view presets: CAMERAS over the one master, never a second anatomy.
 *
 * A preset names a zone, the single view that shows it best, and the box of master units
 * that must stay visible (the zone plus enough body to orient the eye). `cameraFor` widens
 * that box to the window's aspect — it only ever ADDS context, never cuts the box — and
 * keeps it inside its own half of the master (front: x 0–120, back: x 120–240), so a
 * front camera never shows a piece of the back figure.
 *
 * Deterministic: same preset + same aspect → same viewBox, on every device.
 */
import type { BodySide, ZoneCode } from './masterGeometry';

export type Box = { x: number; y: number; w: number; h: number };

export type BodyMapViewPresetId = 'push-pecs' | 'push-delt-lat' | 'push-triceps';

export type BodyMapViewPreset = {
  id: BodyMapViewPresetId;
  /** the zone put in the foreground — the only one drawn in colour (`system`) */
  zone: ZoneCode;
  side: BodySide;
  /** master units that must stay visible */
  frame: Box;
  /** product language (mapping contract `label_fr`) — interface text, never in the SVG */
  label: string;
};

/**
 * Both sides of the body in each camera: a symmetric torso orients the eye at a glance,
 * and a one-sided crop measured no better (DA-04.1 report). The lateral deltoid is shown
 * from the FRONT: from the back the master's posterior deltoid covers it almost entirely.
 */
export const PUSH_A_PRESETS: readonly BodyMapViewPreset[] = [
  { id: 'push-pecs', zone: 'pecs', side: 'front', frame: { x: 38, y: 38, w: 44, h: 34 }, label: 'Pectoraux' },
  { id: 'push-delt-lat', zone: 'delt_lat', side: 'front', frame: { x: 34, y: 36, w: 52, h: 30 }, label: 'Deltoïdes latéraux' },
  { id: 'push-triceps', zone: 'triceps', side: 'back', frame: { x: 152, y: 40, w: 56, h: 40 }, label: 'Triceps' },
];

export function presetById(id: BodyMapViewPresetId): BodyMapViewPreset {
  const p = PUSH_A_PRESETS.find((q) => q.id === id);
  if (!p) throw new Error(`unknown BodyMap preset: ${id}`);
  return p;
}

const HALF: Record<BodySide, { lo: number; hi: number }> = { front: { lo: 0, hi: 120 }, back: { lo: 120, hi: 240 } };
const MASTER_H = 200;
const r3 = (v: number) => Math.round(v * 1000) / 1000;

/** The viewBox for a window of aspect `w / h`: the preset's box, widened to that aspect. */
export function cameraFor(preset: BodyMapViewPreset, aspect: number): Box {
  const { frame, side } = preset;
  const cx = frame.x + frame.w / 2;
  const cy = frame.y + frame.h / 2;
  let w = frame.w;
  let h = frame.h;
  if (w / h < aspect) w = h * aspect;
  else h = w / aspect;
  const { lo, hi } = HALF[side];
  w = Math.min(w, hi - lo);
  h = Math.min(h, MASTER_H);
  const x = Math.min(Math.max(cx - w / 2, lo), hi - w);
  const y = Math.min(Math.max(cy - h / 2, 0), MASTER_H - h);
  return { x: r3(x), y: r3(y), w: r3(w), h: r3(h) };
}

export const viewBoxString = (b: Box) => `${b.x} ${b.y} ${b.w} ${b.h}`;
