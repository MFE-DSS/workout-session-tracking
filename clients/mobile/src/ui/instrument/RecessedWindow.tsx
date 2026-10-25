import React from 'react';
import { View } from 'react-native';
import Svg, { Line, Rect } from 'react-native-svg';

import { densityFor, UNIT } from '../calibration/layout';
import { color } from '../theme';
import { recessedWindowGeometry } from './recessedWindowGeometry';

/**
 * DA-02.5 — `RECESSED-WINDOW-V1` (LOCKED): an internal subfield mounted into an
 * InstrumentFrame. Not mounted on any product screen yet; its future uses are
 * BodyMap regions, previous performance, targets, recovery, substitutions, set
 * metadata, secondary readouts.
 */
export type RecessedWindowProps = {
  width: number;
  height: number;
  /** the parent's grid unit; defaults to the CalibrationRail's for this width */
  u?: number;
  children?: React.ReactNode;
  testID?: string;
};

/**
 * Monochrome roles, existing tokens only, all quieter than Frame C:
 * the recess is darker than the chassis (`field` on `plate`), its line is `line`
 * (Frame C strokes in `ink3`), the registration mark alone carries `ink3`.
 * No semantic colour: a window carries no state.
 */
export const WINDOW_ROLE = {
  field: color.field,
  line: color.line,
  mark: color.ink3,
} as const;

export function RecessedWindow(p: RecessedWindowProps) {
  const u = p.u ?? UNIT[densityFor(p.width)];
  const g = recessedWindowGeometry(p.width, p.height, u);
  return (
    <View testID={p.testID ?? 'recessed-window'} style={{ width: p.width, height: p.height }}>
      <Svg width={p.width} height={p.height} style={{ position: 'absolute' }} accessible={false} importantForAccessibility="no-hide-descendants">
        <Rect x={g.field.x} y={g.field.y} width={g.field.w} height={g.field.h} fill={WINDOW_ROLE.field} />
        {g.blocks.map((b) => (
          <Rect key={`${b.x}-${b.y}-${b.w}`} x={b.x} y={b.y} width={b.w} height={b.h} fill={WINDOW_ROLE.mark} />
        ))}
        {g.segments.map((s) => (
          <Line
            key={`${s.x1}-${s.y1}-${s.x2}-${s.y2}`}
            x1={s.x1}
            y1={s.y1}
            x2={s.x2}
            y2={s.y2}
            stroke={WINDOW_ROLE.line}
            strokeWidth={g.stroke}
            strokeLinecap="square"
          />
        ))}
      </Svg>
      <View testID="recessed-content" style={{ position: 'absolute', left: g.content.x, top: g.content.y, width: g.content.w, height: g.content.h }}>
        {p.children}
      </View>
    </View>
  );
}
