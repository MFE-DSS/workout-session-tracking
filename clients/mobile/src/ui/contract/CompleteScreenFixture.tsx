import React from 'react';
import { View } from 'react-native';
import { SafeAreaFrameContext, SafeAreaInsetsContext } from 'react-native-safe-area-context';

import { sessionPerformance } from '../../domain/performance';
import type { LabFixture } from '../../domain/types';
import { draftFor, initialState, reduce, type WorkoutState } from '../../domain/workout';
import rawFixture from '../../fixtures/lab_fixture.json';
import { CompleteScreen } from '../CompleteScreen';

/**
 * The REAL completion screen, frozen for review: a lab plan played set after set through the workout reducer
 * (every set validated at its prefilled load, three minutes apart, from 10:00 UTC on 31 October 2026), then
 * the screen as the lab shows it — a first week (no history), three sessions a week, the lab's mission next.
 * It scrolls on a phone: the review frame is TALL so the whole page is seen at once.
 */
const fixture = rawFixture as unknown as LabFixture;
const NOOP = () => undefined;
const INSETS = { top: 47, bottom: 34, left: 0, right: 0 };
const START_MS = Date.UTC(2026, 9, 31, 10, 0);
const SET_EVERY_MS = 3 * 60_000;

export function completedState(planSlug: string): WorkoutState {
  const plan = fixture.plans[planSlug];
  if (!plan) throw new Error(`no lab plan ${planSlug}`);
  let state = reduce(initialState, { type: 'START', plan, nowMs: START_MS });
  let now = START_MS;
  while (state.phase !== 'COMPLETE') {
    if (state.phase === 'REST') {
      state = reduce(state, { type: 'REST_END', nowMs: now });
      continue;
    }
    const setId = state.cursorSetId;
    if (setId === null) throw new Error(`stuck in ${state.phase}`);
    now += SET_EVERY_MS;
    if (draftFor(state, setId).weight === null) state = reduce(state, { type: 'SET_VALUE', setId, field: 'weight', value: 40 });
    state = reduce(state, { type: 'VALIDATED', setId, performedAt: { epochMs: now, estimated: false }, nowMs: now });
    state = reduce(state, { type: 'LOCAL_COMMIT', setId, ok: true });
  }
  return state;
}

export function CompleteScreenFixture(p: { width: number; height: number; plan: string }) {
  const state = completedState(p.plan);
  const performance = sessionPerformance(state.plan!, state.done, state.requiresSync);
  return (
    <SafeAreaFrameContext.Provider value={{ x: 0, y: 0, width: p.width, height: p.height }}>
      <SafeAreaInsetsContext.Provider value={INSETS}>
        <View testID="complete-screen" style={{ width: p.width, height: p.height, overflow: 'hidden' }}>
          <CompleteScreen
            state={state}
            performance={performance}
            history={[]}
            sessionsPerWeek={3}
            next={fixture.mission}
            reducedMotion
            onClose={NOOP}
            onOpenLab={NOOP}
          />
        </View>
      </SafeAreaInsetsContext.Provider>
    </SafeAreaFrameContext.Provider>
  );
}
