/**
 * DA-04.1 — BodyMap view presets: CAMERAS over one body, never a second anatomy.
 *
 * A preset names a zone, the single view that shows it best, and the box that must stay
 * visible (the zone plus enough body to orient the eye). `cameraFor` widens that box to the
 * window's aspect — it only ever ADDS context, never cuts the box — and keeps it inside its
 * own half of the canvas (`BODY_REGION`), so a front camera never shows a piece of the back.
 *
 * DA-04.3 — the body is react-native-body-highlighter (MIT, `bodyGeometry.ts`); each box is
 * GENERATED there: centred on the zone, visible height = the fraction of the body the operator
 * validated in the focus spec (2026-10-31). Ids, labels and the camera rule are unchanged.
 *
 * Deterministic: same preset + same aspect → same viewBox, on every device.
 */
import { BODY_CANVAS_H, BODY_REGION, type BodySide, PRESET_FRAMES, type ZoneCode } from './bodyGeometry';

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
  /** canvas units that must stay visible */
  frame: Box;
  /** product language (mapping contract `label_fr`) — interface text, never in the SVG */
  label: string;
};

/** Both sides of the body in each camera: a symmetric torso orients the eye at a glance. */
export const PUSH_A_PRESETS: readonly BodyMapViewPreset[] = [
  { id: 'push-pecs', zone: 'pecs', side: 'front', frame: PRESET_FRAMES['push-pecs'], label: 'Pectoraux' },
  { id: 'push-delt-lat', zone: 'delt_lat', side: 'front', frame: PRESET_FRAMES['push-delt-lat'], label: 'Deltoïdes latéraux' },
  { id: 'push-triceps', zone: 'triceps', side: 'back', frame: PRESET_FRAMES['push-triceps'], label: 'Triceps' },
];

/**
 * DA-04.2 — one camera per zone for the other eight, same rule. Views: the deltoïde postérieur,
 * the back, the posterior chain and the calves from the BACK; biceps, quadriceps and core from
 * the FRONT.
 */
const OTHER_ZONE_PRESETS: readonly BodyMapViewPreset[] = [
  { id: 'zone-delt-post', zone: 'delt_post', side: 'back', frame: PRESET_FRAMES['zone-delt-post'], label: 'Deltoïdes postérieurs' },
  { id: 'zone-lats', zone: 'lats', side: 'back', frame: PRESET_FRAMES['zone-lats'], label: 'Dos largeur' },
  { id: 'zone-upper-back', zone: 'upper_back', side: 'back', frame: PRESET_FRAMES['zone-upper-back'], label: 'Dos épaisseur' },
  { id: 'zone-biceps', zone: 'biceps', side: 'front', frame: PRESET_FRAMES['zone-biceps'], label: 'Biceps' },
  { id: 'zone-quads', zone: 'quads', side: 'front', frame: PRESET_FRAMES['zone-quads'], label: 'Quadriceps' },
  { id: 'zone-posterior', zone: 'posterior', side: 'back', frame: PRESET_FRAMES['zone-posterior'], label: 'Ischios / Fessiers' },
  { id: 'zone-calves', zone: 'calves', side: 'back', frame: PRESET_FRAMES['zone-calves'], label: 'Mollets' },
  { id: 'zone-core', zone: 'core', side: 'front', frame: PRESET_FRAMES['zone-core'], label: 'Core / Abdos' },
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
  const { lo, hi } = BODY_REGION[side];
  w = Math.min(w, hi - lo);
  h = Math.min(h, BODY_CANVAS_H);
  const x = Math.min(Math.max(cx - w / 2, lo), hi - w);
  const y = Math.min(Math.max(cy - h / 2, 0), BODY_CANVAS_H - h);
  return { x: r3(x), y: r3(y), w: r3(w), h: r3(h) };
}

export const viewBoxString = (b: Box) => `${b.x} ${b.y} ${b.w} ${b.h}`;
