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

export type BodyMapViewPresetId =
  | 'push-pecs'
  | 'push-delt-lat'
  | 'push-triceps'
  | 'zone-delt-post'
  | 'zone-lats'
  | 'zone-upper-back'
  | 'zone-biceps'
  | 'zone-quads'
  | 'zone-posterior'
  | 'zone-calves'
  | 'zone-core';

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

/**
 * DA-04.2 — one camera per zone for the other eight, same rule. Views: the deltoïde postérieur,
 * the back, the posterior chain and the calves from the BACK; biceps, quadriceps and core from
 * the FRONT. The posterior chain keeps the waist and the calves keep the knees in frame, so
 * the legs never float.
 */
const OTHER_ZONE_PRESETS: readonly BodyMapViewPreset[] = [
  { id: 'zone-delt-post', zone: 'delt_post', side: 'back', frame: { x: 154, y: 36, w: 52, h: 30 }, label: 'Deltoïdes postérieurs' },
  { id: 'zone-lats', zone: 'lats', side: 'back', frame: { x: 152, y: 44, w: 56, h: 62 }, label: 'Dos largeur' },
  { id: 'zone-upper-back', zone: 'upper_back', side: 'back', frame: { x: 152, y: 24, w: 56, h: 54 }, label: 'Dos épaisseur' },
  { id: 'zone-biceps', zone: 'biceps', side: 'front', frame: { x: 32, y: 40, w: 56, h: 42 }, label: 'Biceps' },
  { id: 'zone-quads', zone: 'quads', side: 'front', frame: { x: 38, y: 86, w: 44, h: 64 }, label: 'Quadriceps' },
  { id: 'zone-posterior', zone: 'posterior', side: 'back', frame: { x: 156, y: 74, w: 48, h: 78 }, label: 'Ischios / Fessiers' },
  { id: 'zone-calves', zone: 'calves', side: 'back', frame: { x: 160, y: 118, w: 40, h: 60 }, label: 'Mollets' },
  { id: 'zone-core', zone: 'core', side: 'front', frame: { x: 40, y: 60, w: 40, h: 46 }, label: 'Core / Abdos' },
];

/** Every camera, one per zone of the taxonomy (the Push A three keep their locked names). */
export const ZONE_PRESETS: readonly BodyMapViewPreset[] = [...PUSH_A_PRESETS, ...OTHER_ZONE_PRESETS];

export function presetById(id: BodyMapViewPresetId): BodyMapViewPreset {
  const p = ZONE_PRESETS.find((q) => q.id === id);
  if (!p) throw new Error(`unknown BodyMap preset: ${id}`);
  return p;
}

/** The camera of a zone; `undefined` for a code outside the taxonomy (« unknown » shows nothing). */
export function presetForZone(zone: string): BodyMapViewPreset | undefined {
  return ZONE_PRESETS.find((p) => p.zone === zone);
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
