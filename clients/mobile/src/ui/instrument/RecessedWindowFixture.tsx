import React from 'react';
import { Text, View } from 'react-native';

import { densityFor, UNIT } from '../calibration/layout';
import { color, type } from '../theme';
import { frameGeometry } from './frameGeometry';
import { InstrumentFrame } from './InstrumentFrame';
import { RecessedWindow } from './RecessedWindow';
import { recessedWindowGeometry, type WindowLayout, windowLayout } from './recessedWindowGeometry';
import { FittedReadout } from './NumericReadout';

/**
 * DA-02.5 — the three content fixtures of the brief, mounted in an unchanged Frame C:
 * F1 text / figure · F2 BodyMap placeholder (never the real BodyMap) · F3 two windows
 * in one frame, equal or 60/40, with radically different content.
 */
export type WindowFixture = 'f1' | 'f2' | 'f3-pair' | 'f3-split';

type Content = { kind: 'figure'; label: string; value: string; unit: string } | { kind: 'bodymap' };

const LAST: Content = { kind: 'figure', label: 'Dernière', value: '72,5', unit: 'kg' };
const REST: Content = { kind: 'figure', label: 'Repos', value: '2:30', unit: 'min' };
const BODYMAP: Content = { kind: 'bodymap' };

export const WINDOW_FIXTURES: Record<WindowFixture, { layout: WindowLayout; contents: Content[] }> = {
  f1: { layout: 'single', contents: [LAST] },
  f2: { layout: 'single', contents: [BODYMAP] },
  'f3-pair': { layout: 'pair', contents: [LAST, REST] },
  'f3-split': { layout: 'split-60-40', contents: [BODYMAP, LAST] },
};

export function RecessedWindowFixture(p: { width: number; height: number; fixture: WindowFixture }) {
  const u = UNIT[densityFor(p.width)];
  const frame = frameGeometry('rail', p.width, p.height, u);
  const { layout, contents } = WINDOW_FIXTURES[p.fixture];
  const boxes = windowLayout(layout, { x: 0, y: 0, w: frame.content.w, h: frame.content.h }, u);
  return (
    <InstrumentFrame variant="rail" width={p.width} height={p.height} u={u}>
      {boxes.map((b, i) => {
        const inner = recessedWindowGeometry(b.w, b.h, u).content;
        return (
          <View key={`${b.x}-${b.w}`} style={{ position: 'absolute', left: b.x, top: b.y }}>
            <RecessedWindow width={b.w} height={b.h} u={u}>
              <WindowContent content={contents[i]} width={inner.w} height={inner.h} />
            </RecessedWindow>
          </View>
        );
      })}
    </InstrumentFrame>
  );
}

function WindowContent({ content, width, height }: { content: Content; width: number; height: number }) {
  if (content.kind === 'bodymap') {
    // a neutral placeholder: a silhouette-sized rectangle, never the real BodyMap
    return (
      <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
        <View
          testID="window-bodymap"
          style={{ width: '42%', height: '86%', borderWidth: 1, borderColor: color.ink3, borderStyle: 'dashed', alignItems: 'center', justifyContent: 'center' }}
        >
          <Text style={[type.eyebrow, { fontSize: 10 }]}>BodyMap</Text>
        </View>
      </View>
    );
  }
  // DA-02.6 — the largest numeral role that fits, MEASURED on the device (Numeric Readout)
  return <FittedReadout label={content.label} value={content.value} unit={content.unit} width={width} height={height} />;
}
