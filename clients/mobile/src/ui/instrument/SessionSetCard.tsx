import React from 'react';
import { Text, View } from 'react-native';

import { CALIBRATION_LINE_DEMO, selectedPositionOf } from '../contract/fixtures';
import { color, space, type } from '../theme';
import type { Presentation } from './disclosure';
import { InstrumentWithStepControls } from './InstrumentWithStepControls';
import { BODYMAP, LAST, REST, WindowModule } from './RecessedWindowFixture';
import { stepControlsLayout } from './stepModel';

/**
 * DA-02.7 R1 — TARGET COMPOSITION of the set card (operator, 2026-10-26): one vertical
 * card, read top to bottom — the exercise, then its information and execution pieces in
 * Recessed Windows, and at the very BOTTOM the load instrument with its − / + keys, under
 * the thumb.
 *
 * Bench only: in the product the rail is NOT drawn without the engine's zone boundaries
 * (E7, AUREN_CALIBRATION_SYSTEM), so this card is never mounted on the session screen yet.
 * Demonstration data; the execution cue is a named placeholder, not designed yet.
 *
 * Full-bleed on purpose: with 20 px gutters the instrument would be 350 px wide, under
 * the expanded density (360) — a smaller grid, no zone names.
 */
export const SESSION_CARD = {
  /** status bar */
  top: 48,
  /** home indicator */
  bottom: 34,
  /** between two modules: the chassis shows, one machine */
  gap: 8,
  /** eyebrow line + 6 + exercise line + air under the title */
  header: 16 + 6 + 34 + 16,
  /** the instrument, at its governed size (R2) */
  instrument: 290,
  /** the second window module (rest · execution cue) */
  pair: 120,
} as const;

export function sessionCardLayout(screenWidth: number, screenHeight: number) {
  const c = SESSION_CARD;
  const keys = stepControlsLayout(screenWidth).height;
  const bottomBlock = c.instrument + keys + c.bottom;
  // the first window module takes what is left: no unintended void between the pieces
  const split = screenHeight - c.top - c.header - c.gap - c.pair - c.gap - bottomBlock;
  return { keys, bottomBlock, split, fits: split >= 120 };
}

export function SessionSetCard(p: {
  screenWidth: number;
  screenHeight: number;
  selectedValue: number;
  presentation: Presentation;
}) {
  const l = sessionCardLayout(p.screenWidth, p.screenHeight);
  const c = SESSION_CARD;
  return (
    <View testID="session-card" style={{ width: p.screenWidth, height: p.screenHeight, backgroundColor: color.field, paddingTop: c.top }}>
      <View style={{ height: c.header, paddingHorizontal: space.gutter, gap: 6 }}>
        <Text style={[type.eyebrow, { lineHeight: 16 }]}>Série 2 / 4 · 8 répétitions</Text>
        <Text style={type.exercise}>Développé couché</Text>
      </View>
      <View style={{ gap: c.gap }}>
        <WindowModule width={p.screenWidth} height={l.split} layout="split-60-40" contents={[BODYMAP, LAST]} />
        <WindowModule
          width={p.screenWidth}
          height={c.pair}
          layout="pair"
          contents={[REST, { kind: 'slot', label: "Consigne d'exécution" }]}
        />
        <InstrumentWithStepControls
          {...CALIBRATION_LINE_DEMO}
          width={p.screenWidth}
          height={c.instrument}
          selectedPosition={selectedPositionOf({ selectedValue: p.selectedValue })}
          selectedValue={p.selectedValue}
          presentation={p.presentation}
          onSelectPosition={() => undefined}
        />
      </View>
    </View>
  );
}
