import React from 'react';
import { View } from 'react-native';
import Svg, { Line, Rect } from 'react-native-svg';

import { densityFor, UNIT } from '../calibration/layout';
import { color } from '../theme';
import { frameGeometry, type FrameVariant } from './frameGeometry';

/**
 * DA-02.3 — EXPLORATION API, deliberately thin: the operator chooses one family
 * before any hardening. Not mounted on any product screen.
 */
export type InstrumentFrameProps = {
  width: number;
  height: number;
  variant: FrameVariant;
  /** the grid unit; defaults to the CalibrationRail's for this width (one index) */
  u?: number;
  children?: React.ReactNode;
  testID?: string;
};

/**
 * Three monochrome roles, all existing tokens: the chassis (the module's face),
 * the structure (perimeter, reinforcement, rail, marks) and the recessed field.
 * No shadow, no gradient, no glow, no texture — the structure reads without them.
 */
export const FRAME_ROLE = {
  chassis: color.plate,
  structure: color.ink3,
  field: color.field,
} as const;

export function InstrumentFrame(p: InstrumentFrameProps) {
  const u = p.u ?? UNIT[densityFor(p.width)];
  const g = frameGeometry(p.variant, p.width, p.height, u);
  return (
    <View testID={p.testID} style={{ width: p.width, height: p.height }}>
      <Svg
        width={p.width}
        height={p.height}
        style={{ position: 'absolute' }}
        accessible={false}
        importantForAccessibility="no-hide-descendants"
      >
        <Rect x={0} y={0} width={p.width} height={p.height} fill={FRAME_ROLE.chassis} />
        {g.blocks.map((b) => (
          <Rect key={`${b.role}-${b.x}-${b.y}-${b.w}`} x={b.x} y={b.y} width={b.w} height={b.h} fill={FRAME_ROLE[b.role]} />
        ))}
        {g.segments.map((s) => (
          <Line
            key={`${s.x1}-${s.y1}-${s.x2}-${s.y2}`}
            x1={s.x1}
            y1={s.y1}
            x2={s.x2}
            y2={s.y2}
            stroke={FRAME_ROLE.structure}
            strokeWidth={s.weight === 'primary' ? g.primary : g.secondary}
            strokeLinecap="square"
          />
        ))}
      </Svg>
      <View style={{ position: 'absolute', left: g.content.x, top: g.content.y, width: g.content.w, height: g.content.h }}>
        {p.children}
      </View>
    </View>
  );
}

type Named = Omit<InstrumentFrameProps, 'variant'>;
/** A — RECESSED: the most neutral candidate. */
export const InstrumentFrameA = (p: Named) => <InstrumentFrame {...p} variant="recessed" />;
/** B — INDEXED: a 1u targeting notch, the markers' slot (never a drawn cursor). */
export const InstrumentFrameB = (p: Named) => <InstrumentFrame {...p} variant="indexed" />;
/** C — RAIL-MOUNTED: one edge is a mounting rail with two registration marks. */
export const InstrumentFrameC = (p: Named) => <InstrumentFrame {...p} variant="rail" />;
/** D — ASYMMETRIC FACEPLATE: reinforced spine, one interruption opposite. */
export const InstrumentFrameD = (p: Named) => <InstrumentFrame {...p} variant="faceplate" />;
