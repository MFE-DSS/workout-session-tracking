import React from 'react';
import { View } from 'react-native';

import { densityFor, UNIT } from '../calibration/layout';
import { CALIBRATION_LINE_DEMO, selectedPositionOf } from '../contract/fixtures';
import { HorizontalInstrumentSurface } from '../instrument/HorizontalInstrumentSurface';
import { SESSION_CARD, SessionSetCard } from '../instrument/SessionSetCard';
import { color, space } from '../theme';
import { AurenMark } from './AurenMark';

/**
 * DA-03.2 — the contract's `AUREN-MARK-V1` fixtures. The approved components are rendered
 * untouched and the mark is laid over them, engraved in `ink3` like Frame C's own
 * registration marks. Bench only: no product screen mounts the mark yet.
 */
export type MarkFixture =
  | { kind: 'swatch'; size: number; on: 'paper' | 'field' }
  | { kind: 'frame-c' | 'session-card' | 'splash' };

const PUSH = { ...CALIBRATION_LINE_DEMO, selectedValue: 75, selectedPosition: selectedPositionOf({ selectedValue: 75 }) };

export function MarkPlacementFixture({ f }: { f: MarkFixture }) {
  if (f.kind === 'swatch') {
    // paper = the lightest token behind the darkest one: the monochrome master
    const paper = f.on === 'paper';
    return (
      <View style={{ backgroundColor: paper ? color.ink : color.field }}>
        <AurenMark size={f.size} color={paper ? color.field : color.ink} />
      </View>
    );
  }
  if (f.kind === 'frame-c') {
    // the corner of the frame's content field: its 2u margin plus the secondary stroke
    const u = UNIT[densityFor(390)];
    const inset = Math.round(2 * u + 0.35 * u);
    return (
      <View style={{ width: 390, height: 290 }}>
        <HorizontalInstrumentSurface {...PUSH} width={390} height={290} presentation="rest" />
        <View style={{ position: 'absolute', top: inset, right: inset }}>
          <AurenMark size={16} color={color.ink3} />
        </View>
      </View>
    );
  }
  if (f.kind === 'session-card') {
    return (
      <View style={{ width: 390, height: 844 }}>
        <SessionSetCard screenWidth={390} screenHeight={844} selectedValue={75} presentation="rest" />
        <View style={{ position: 'absolute', top: SESSION_CARD.top, right: space.gutter }}>
          <AurenMark size={16} color={color.ink3} />
        </View>
      </View>
    );
  }
  return (
    <View style={{ width: 390, height: 844, backgroundColor: color.field, alignItems: 'center', justifyContent: 'center' }}>
      <AurenMark size={64} color={color.ink} />
    </View>
  );
}
