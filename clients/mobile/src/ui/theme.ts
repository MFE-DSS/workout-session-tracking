/**
 * N0 art direction — ATHLETIC INSTRUMENTATION.
 *
 * Roles first (AUREN_VISUAL_BACKBONE §3.1, retained as method): one warm voice
 * for « your move », one cool voice for what AUREN computes and for time, ink in
 * three strengths. Contrast is a COUPLE contract — every pair below is measured
 * on its real background (scripts/contrast_n0.py, results in the N0 report).
 */
import { TextStyle } from 'react-native';

import { fontFamily } from '../native/platformUi';

export const color = {
  field: '#0A0B0D',
  fieldRest: '#071219',
  plate: '#191C22',
  plateRest: '#0E2230',
  line: '#2A2F37',
  lineRest: '#1F4256',
  ink: '#F5F3EE',
  ink2: '#B9BDC5',
  ink3: '#8F959E',
  signal: '#FFB23E',
  onSignal: '#0A0B0D',
  system: '#7CCBF5',
  alert: '#FF8A7A',
  // R11 — how close a substitute is (the engine's N1/N2/N3), green → orange.
  // Measured 2026-10-25 (WCAG ratio on plate #191C22 · on field #0A0B0D · CIE76
  // distance to the roles already taken). NEVER the only carrier: the engine's
  // own badge (« Équivalent », « Proche », « Élargi ») always says it in words.
  subN1: '#6FD69A', //  9.56 : 1 · 11.03 : 1 · ΔE signal 77, alert 87, system 57
  subN2: '#C9D46B', // 10.66 : 1 · 12.29 : 1 · ΔE signal 41, alert 66
  subN3: '#E8935F', //  7.13 : 1 ·  8.22 : 1 · ΔE signal 29, alert 20 — the closest; shown as a tint + badge, never a fill
  // R13 — a set against its prescription. « conforme » is plain ink: no colour.
  perfAbove: '#6FD69A', //  9.56 : 1 on plate
  perfBelow: '#B7A3F0', //  7.73 : 1 on plate · ΔE alert 67: « below » is a reading, not an error
} as const;

const family = fontFamily.text;
const condensed = fontFamily.numerals;

const tabular: TextStyle = { fontVariant: ['tabular-nums'] };

export const type = {
  eyebrow: { fontFamily: family, fontSize: 12, fontWeight: '700', letterSpacing: 1.4, textTransform: 'uppercase', color: color.ink3 } as TextStyle,
  title: { fontFamily: family, fontSize: 34, fontWeight: '800', letterSpacing: -0.6, color: color.ink } as TextStyle,
  exercise: { fontFamily: family, fontSize: 30, fontWeight: '800', letterSpacing: -0.4, lineHeight: 34, color: color.ink } as TextStyle,
  body: { fontFamily: family, fontSize: 17, fontWeight: '500', lineHeight: 23, color: color.ink2 } as TextStyle,
  bodyStrong: { fontFamily: family, fontSize: 17, fontWeight: '700', lineHeight: 23, color: color.ink } as TextStyle,
  small: { fontFamily: family, fontSize: 14, fontWeight: '500', lineHeight: 19, color: color.ink3 } as TextStyle,
  readout: { fontFamily: condensed, fontSize: 68, fontWeight: '800', letterSpacing: -1.5, color: color.ink, ...tabular } as TextStyle,
  clock: { fontFamily: condensed, fontSize: 112, fontWeight: '800', letterSpacing: -3, color: color.ink, ...tabular } as TextStyle,
  figure: { fontFamily: family, fontSize: 40, fontWeight: '800', letterSpacing: -0.8, color: color.ink, ...tabular } as TextStyle,
  action: { fontFamily: family, fontSize: 19, fontWeight: '800', letterSpacing: 0.4 } as TextStyle,
  tabular,
};

export const space = { gutter: 20, s: 8, m: 16, l: 24, xl: 32 } as const;

/** Primary action height: well above the 44-pt contract, sized for a thumb in a gym. */
export const ACTION_HEIGHT = 68;
/** Never let huge numerals grow past the layout; body text keeps full Dynamic Type. */
export const NUMERAL_FONT_SCALE_CAP = 1.25;
