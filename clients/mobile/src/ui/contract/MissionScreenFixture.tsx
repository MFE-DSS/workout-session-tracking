import React from 'react';
import { View } from 'react-native';
import { SafeAreaFrameContext, SafeAreaInsetsContext } from 'react-native-safe-area-context';

import type { LabFixture, Mission } from '../../domain/types';
import rawFixture from '../../fixtures/lab_fixture.json';
import { MissionScreen } from '../MissionScreen';

/**
 * The REAL mission screen, frozen for review: a mission of the lab fixture (the canonical services' own output) —
 * the lab's mission, or the one served after a newcomer's first session — on an iPhone frame with its insets, on
 * a fixed day. No handler does anything.
 */
const fixture = rawFixture as unknown as LabFixture & {
  onboarding: { families: Record<string, { sessions: { next_mission?: Mission | null }[] }> };
};
const NOOP = () => undefined;
const INSETS = { top: 47, bottom: 34, left: 0, right: 0 };
/** a fixed day for the date line (Saturday 31 October 2026, noon UTC) */
const REVIEW_DAY = new Date(Date.UTC(2026, 9, 31, 12));

/** `main`, or `<family>:<session index>` for a newcomer's next mission */
export type MissionSource = string;

export function missionAt(source: MissionSource): Mission {
  if (source === 'main') return fixture.mission;
  const [family, index] = source.split(':');
  const m = fixture.onboarding.families[family]?.sessions[Number(index)]?.next_mission;
  if (!m) throw new Error(`no mission ${source} in the lab fixture`);
  return m;
}

export function MissionScreenFixture(p: { width: number; height: number; source: MissionSource }) {
  return (
    <SafeAreaFrameContext.Provider value={{ x: 0, y: 0, width: p.width, height: p.height }}>
      <SafeAreaInsetsContext.Provider value={INSETS}>
        <View testID="mission-screen" style={{ width: p.width, height: p.height, overflow: 'hidden' }}>
          <MissionScreen mission={missionAt(p.source)} onStart={NOOP} onOpenLab={NOOP} onSecondaryOpened={NOOP} today={REVIEW_DAY} />
        </View>
      </SafeAreaInsetsContext.Provider>
    </SafeAreaFrameContext.Provider>
  );
}
