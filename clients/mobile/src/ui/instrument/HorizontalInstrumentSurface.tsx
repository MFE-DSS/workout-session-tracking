import React from 'react';
import { Text, View } from 'react-native';

import { CalibrationRail, railBlocks, type CalibrationRailProps } from '../calibration/CalibrationRail';
import { densityFor, formatValue, railLayout, UNIT } from '../calibration/layout';
import { color, type } from '../theme';
import { frameGeometry } from './frameGeometry';
import { InstrumentFrame } from './InstrumentFrame';

/**
 * DA-02.4B.1 — EXPLORATION. Frame C (unchanged) + the locked CalibrationRail at the
 * full width of the frame's content + the selected value above it, sovereign.
 *
 * The rail's own readout is opted out (`showReadout={false}`): the composition says
 * each thing once. The value comes from `selectedValue` and `unit` only; the
 * prescribed value is written under the rail's block, centred on the reference
 * marker, without a word (operator ruling D-B, option (i)).
 */
export type HorizontalInstrumentSurfaceProps = Omit<CalibrationRailProps, 'width' | 'showReadout' | 'density'> & {
  width: number;
  height: number;
  testID?: string;
};

/** Gaps of the stack, in grid units. */
const VALUE_GAP_U = 3;
const REFERENCE_GAP_U = 1;
/** Box of the prescribed value, centred on the marker (wider than any value it writes). */
const REFERENCE_BOX = 80;

export function surfaceLayout(p: HorizontalInstrumentSurfaceProps) {
  const u = UNIT[densityFor(p.width)];
  const frame = frameGeometry('rail', p.width, p.height, u);
  const railWidth = Math.floor(frame.content.w);
  const rail = railLayout({ ...p, width: railWidth });
  // what the rail draws under its own drawing (zone names when expanded), readout opted out
  const railBlockH = rail.height + (railBlocks(rail.density, { showReadout: false }).zoneLabels ? 16 : 0);
  const value = rail.density === 'expanded' ? type.readout : type.figure;
  const valueLineH = Math.round(value.fontSize! * 1.05);
  const unitSize = Math.round(value.fontSize! * 0.4);
  const referenceTop = railBlockH + REFERENCE_GAP_U * rail.u;
  const stackH = valueLineH + VALUE_GAP_U * rail.u + referenceTop + type.bodyStrong.lineHeight!;
  return { u, frame, railWidth, rail, value, valueLineH, unitSize, referenceTop, stackH, fits: stackH <= frame.content.h };
}

export function HorizontalInstrumentSurface(p: HorizontalInstrumentSurfaceProps) {
  const s = surfaceLayout(p);
  const unit = p.unit ? ` ${p.unit}` : '';
  const top = Math.max(0, Math.floor((s.frame.content.h - s.stackH) / 2));
  return (
    <InstrumentFrame testID={p.testID} variant="rail" width={p.width} height={p.height} u={s.u}>
      <View style={{ paddingTop: top, width: s.railWidth }}>
        <Text
          testID="surface-value"
          style={[s.value, { lineHeight: s.valueLineH, textAlign: 'center' }]}
          maxFontSizeMultiplier={1.25}
        >
          {p.selectedValue !== undefined ? formatValue(p.selectedValue) : '—'}
          {/* the unit's own line box stays inside the value's: it never makes the line taller */}
          <Text style={{ fontSize: s.unitSize, lineHeight: s.unitSize, fontWeight: '700', color: color.ink2 }}>{unit}</Text>
        </Text>
        <View style={{ marginTop: VALUE_GAP_U * s.rail.u, width: s.railWidth }}>
          <CalibrationRail {...p} width={s.railWidth} showReadout={false} testID="surface-rail" />
          {p.referenceValue !== undefined ? (
            <Text
              testID="surface-reference"
              style={[
                styles.reference,
                { top: s.referenceTop, left: s.rail.referenceX - REFERENCE_BOX / 2, width: REFERENCE_BOX },
              ]}
            >
              {formatValue(p.referenceValue)}
            </Text>
          ) : null}
        </View>
      </View>
    </InstrumentFrame>
  );
}

const styles = {
  reference: {
    ...type.bodyStrong,
    ...type.tabular,
    position: 'absolute' as const,
    color: color.system,
    textAlign: 'center' as const,
  },
};
