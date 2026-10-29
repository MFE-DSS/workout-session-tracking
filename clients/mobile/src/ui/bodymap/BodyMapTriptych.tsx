import React from 'react';
import { Text, View } from 'react-native';

import { densityFor, UNIT } from '../calibration/layout';
import { frameGeometry } from '../instrument/frameGeometry';
import { InstrumentFrame } from '../instrument/InstrumentFrame';
import { RecessedWindow } from '../instrument/RecessedWindow';
import { recessedWindowGeometry } from '../instrument/recessedWindowGeometry';
import { type as typeRole } from '../theme';
import { BodyMapView } from './BodyMapView';
import { zoneGridHeight, zoneGridLayout } from './triptychLayout';
import { type BodyMapViewPreset, presetForZone } from './viewPresets';

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
  const boxes = zoneGridLayout(p.presets.length, { x: 0, y: 0, w: frame.content.w, h: frame.content.h }, u);
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

/**
 * DA-04.2 — the zones a session trains, in order of first appearance, from its exercises' primary
 * zone (the plan's `zone` field). An exercise without a known zone adds nothing: absence is not
 * drawn as a guess.
 */
export function sessionZones(exercises: readonly { zone: { zone: string } | null }[]): BodyMapViewPreset[] {
  const out: BodyMapViewPreset[] = [];
  for (const e of exercises) {
    const p = e.zone ? presetForZone(e.zone.zone) : undefined;
    if (p && !out.includes(p)) out.push(p);
  }
  return out;
}

/** The session's BodyMap: every zone it trains, one equal window each, in one Frame C. */
export function SessionBodyMap(p: { width: number; presets: readonly BodyMapViewPreset[] }) {
  if (p.presets.length === 0) return null;
  return <BodyMapTriptych width={p.width} height={zoneGridHeight(p.presets.length)} presets={p.presets} />;
}
