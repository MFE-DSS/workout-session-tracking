import React from 'react';
import { Text, View } from 'react-native';

import { CalibrationRail, railBlocks, type CalibrationRailProps } from '../calibration/CalibrationRail';
import { densityFor, formatValue, railLayout, UNIT } from '../calibration/layout';
import { color, type } from '../theme';
import type { Presentation } from './disclosure';
import { frameGeometry } from './frameGeometry';
import { InstrumentFrame } from './InstrumentFrame';
import { NumericReadout } from './NumericReadout';
import { readoutLineHeight } from './readoutModel';

/**
 * DA-02.4B.1 — EXPLORATION. Frame C (unchanged) + the locked CalibrationRail at the
 * full width of the frame's content + the selected value above it, sovereign.
 *
 * The rail's own readout is opted out (`showReadout={false}`): the composition says
 * each thing once. The value comes from `selectedValue` and `unit` only; the
 * prescribed value is written under the rail's block, centred on the reference
 * marker, without a word (operator ruling D-B, option (i)).
 */
export type HorizontalInstrumentSurfaceProps = Omit<
  CalibrationRailProps,
  'width' | 'showReadout' | 'showScale' | 'showZoneLabels' | 'density'
> & {
  width: number;
  height: number;
  /**
   * DA-02.4B.2 — REST hides the printed scale and the zone names; ADJUSTING shows them.
   * Default: ADJUSTING, the B.1 rendering (`INSTRUMENT-SURFACE-B1`). Nothing moves between
   * the two: the prescribed value keeps its place (operator ruling « fixe, pas de saut »).
   */
  presentation?: Presentation;
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
  // what the rail draws under its own drawing (zone names when expanded), readout opted out —
  // measured on the ADJUSTING rail in every state, so nothing jumps when the names appear
  const railBlockH = rail.height + (railBlocks(rail.density, { showReadout: false }).zoneLabels ? 16 : 0);
  const adjusting = (p.presentation ?? 'adjusting') === 'adjusting';
  // the sovereign value: the readout role when expanded, the figure role below (DA-02.6 Numeric Readout)
  const value = rail.density === 'expanded' ? type.readout : type.figure;
  const valueLineH = readoutLineHeight(value);
  const referenceTop = railBlockH + REFERENCE_GAP_U * rail.u;
  const stackH = valueLineH + VALUE_GAP_U * rail.u + referenceTop + type.bodyStrong.lineHeight!;
  return {
    u, frame, railWidth, rail, value, valueLineH, referenceTop, stackH, adjusting,
    fits: stackH <= frame.content.h,
  };
}

export function HorizontalInstrumentSurface(p: HorizontalInstrumentSurfaceProps) {
  const s = surfaceLayout(p);
  const top = Math.max(0, Math.floor((s.frame.content.h - s.stackH) / 2));
  return (
    <InstrumentFrame testID={p.testID} variant="rail" width={p.width} height={p.height} u={s.u}>
      <View style={{ paddingTop: top, width: s.railWidth }}>
        <NumericReadout
          testID="surface-value"
          value={p.selectedValue !== undefined ? formatValue(p.selectedValue) : '—'}
          unit={p.unit}
          role={s.value}
          align="center"
        />
        <View style={{ marginTop: VALUE_GAP_U * s.rail.u, width: s.railWidth }}>
          <CalibrationRail
            {...p}
            width={s.railWidth}
            showReadout={false}
            showScale={s.adjusting}
            showZoneLabels={s.adjusting}
            testID="surface-rail"
          />
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
