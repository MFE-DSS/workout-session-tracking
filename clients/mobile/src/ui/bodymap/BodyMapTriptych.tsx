import React from 'react';
import { Text, View } from 'react-native';

import { densityFor, UNIT } from '../calibration/layout';
import { frameGeometry } from '../instrument/frameGeometry';
import { InstrumentFrame } from '../instrument/InstrumentFrame';
import { RecessedWindow } from '../instrument/RecessedWindow';
import { recessedWindowGeometry } from '../instrument/recessedWindowGeometry';
import { type as typeRole } from '../theme';
import { BodyMapView } from './BodyMapView';
import { triptychLayout } from './triptychLayout';
import type { BodyMapViewPreset } from './viewPresets';

/**
 * DA-04.1 — the Push A triptych (T1, operator 2026-10-29): three cameras over the same
 * master, each in one of three equal Recessed Windows of one Frame C. No new card language, no shadow, no gradient. The label is
 * interface text, kept secondary (eyebrow role, smaller), never baked into the SVG.
 *
 * Review only: not mounted on any product screen before the operator's acceptance.
 */
export const LABEL = { fontSize: 10, lineHeight: 12, letterSpacing: 1.2, lines: 2, gap: 4 } as const;
const LABEL_BLOCK = LABEL.lineHeight * LABEL.lines + LABEL.gap;

export function BodyMapWindowContent(p: { preset: BodyMapViewPreset; width: number; height: number }) {
  return (
    <View style={{ width: p.width, height: p.height, gap: LABEL.gap }}>
      <Text
        testID="window-text"
        numberOfLines={LABEL.lines}
        style={[typeRole.eyebrow, { fontSize: LABEL.fontSize, lineHeight: LABEL.lineHeight, letterSpacing: LABEL.letterSpacing, height: LABEL.lineHeight * LABEL.lines }]}
      >
        {p.preset.label}
      </Text>
      <BodyMapView preset={p.preset} width={p.width} height={p.height - LABEL_BLOCK} />
    </View>
  );
}

export function BodyMapTriptych(p: { width: number; height: number; presets: readonly BodyMapViewPreset[] }) {
  const u = UNIT[densityFor(p.width)];
  const frame = frameGeometry('rail', p.width, p.height, u);
  const boxes = triptychLayout({ x: 0, y: 0, w: frame.content.w, h: frame.content.h }, u);
  return (
    <InstrumentFrame variant="rail" width={p.width} height={p.height} u={u} testID="bodymap-triptych">
      {boxes.map((b, i) => {
        const inner = recessedWindowGeometry(b.w, b.h, u).content;
        return (
          <View key={p.presets[i].id} style={{ position: 'absolute', left: b.x, top: b.y }}>
            <RecessedWindow width={b.w} height={b.h} u={u}>
              <BodyMapWindowContent preset={p.presets[i]} width={inner.w} height={inner.h} />
            </RecessedWindow>
          </View>
        );
      })}
    </InstrumentFrame>
  );
}
