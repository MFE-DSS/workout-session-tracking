import React, { useState } from 'react';
import { Text, type TextStyle, View } from 'react-native';

import { color, NUMERAL_FONT_SCALE_CAP, type } from '../theme';
import { chooseFittedRole, NUMERAL_ROLES, readoutLineHeight, unitSize } from './readoutModel';

/**
 * DA-02.6 — the Numeric Readout: ONE way to set a number in AUREN.
 *
 * A value in an existing numeral role, its line box at 1.05 × the size; the unit after
 * it, at 0.4 × the size, its own line box no taller than itself (so it never makes the
 * line taller — the DA-02.4B.1 lesson); the decimal part the same size as the integer.
 */
export type NumericReadoutProps = {
  value: string;
  unit?: string;
  /** one of `NUMERAL_ROLES` */
  role: TextStyle;
  align?: 'left' | 'center';
  numberOfLines?: number;
  style?: TextStyle;
  testID?: string;
};

export function NumericReadout(p: NumericReadoutProps) {
  const size = unitSize(p.role);
  return (
    <Text
      testID={p.testID}
      style={[p.role, { lineHeight: readoutLineHeight(p.role) }, p.align === 'center' ? { textAlign: 'center' } : null, p.style]}
      numberOfLines={p.numberOfLines}
      maxFontSizeMultiplier={NUMERAL_FONT_SCALE_CAP}
    >
      {p.value}
      {p.unit ? <Text style={{ fontSize: size, lineHeight: size, fontWeight: '700', color: color.ink2 }}>{` ${p.unit}`}</Text> : null}
    </Text>
  );
}

/**
 * The largest numeral role that FITS, measured on the device rather than estimated:
 * the value is laid out once in each role, unconstrained and invisible; their widths
 * choose the role; the measurers are then removed. Until then the value is laid out but
 * not shown (no first frame at the wrong size).
 */
export function FittedReadout(p: { value: string; unit?: string; label?: string; width: number; height: number }) {
  const [widths, setWidths] = useState<(number | null)[]>(() => NUMERAL_ROLES.map(() => null));
  const settled = widths.every((w) => w !== null);
  const role = NUMERAL_ROLES[settled ? chooseFittedRole(widths as number[], p.width, p.height, Boolean(p.label)) : 0];
  return (
    <View style={{ flex: 1, justifyContent: 'center' }}>
      {p.label ? (
        <Text testID="window-text" style={type.eyebrow}>
          {p.label}
        </Text>
      ) : null}
      <View style={{ opacity: settled ? 1 : 0 }}>
        <NumericReadout testID="window-value" value={p.value} unit={p.unit} role={role} numberOfLines={1} style={{ marginTop: p.label ? 4 : 0 }} />
      </View>
      {settled ? null : (
        <View testID="readout-measure" pointerEvents="none" style={{ position: 'absolute', left: 0, top: 0, width: 10000, opacity: 0 }}>
          {NUMERAL_ROLES.map((r, i) => (
            <View
              key={r.fontSize}
              style={{ alignSelf: 'flex-start' }}
              onLayout={(e) => {
                const w = e.nativeEvent.layout.width;
                setWidths((prev) => (prev[i] === w ? prev : prev.map((x, j) => (j === i ? w : x))));
              }}
            >
              <NumericReadout value={p.value} unit={p.unit} role={r} />
            </View>
          ))}
        </View>
      )}
    </View>
  );
}
