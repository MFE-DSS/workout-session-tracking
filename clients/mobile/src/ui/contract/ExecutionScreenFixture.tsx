import React from 'react';
import { View } from 'react-native';
import { SafeAreaFrameContext, SafeAreaInsetsContext } from 'react-native-safe-area-context';

import type { LabFixture } from '../../domain/types';
import { draftFor, initialState, reduce, setsOf, type WorkoutState } from '../../domain/workout';
import rawFixture from '../../fixtures/lab_fixture.json';
import { ExecutionScreen, type ExecutionHandlers } from '../ExecutionScreen';

/**
 * DA-05.1 — the REAL execution screen, frozen for review: a lab plan (`lab_fixture.json`, the
 * canonical services' own output), on an iPhone-sized frame with its safe-area insets.
 * Deterministic: fixed instants, no handler does anything, no motion.
 *
 * - `set`: the first set of one exercise;
 * - `rest-next`: 30 s into the rest after the LAST set of one exercise — the rest that leads to the next.
 */
const fixture = rawFixture as unknown as LabFixture;
const NOOP = () => undefined;
const HANDLERS: ExecutionHandlers = {
  onAdjust: NOOP,
  onSetValue: NOOP,
  onValidatePressIn: NOOP,
  onValidate: NOOP,
  onShift: NOOP,
  onSkip: NOOP,
  onRequestSubstitute: NOOP,
  onOpenLab: NOOP,
  onRestPainted: NOOP,
  onSecondaryOpened: NOOP,
  onExitRequested: NOOP,
  onSkipSet: NOOP,
  serverStateOf: () => 'synced',
};
/** iPhone 13 / 14 / 15 / 16 class: status bar and home indicator */
const INSETS = { top: 47, bottom: 34, left: 0, right: 0 };
export type ScreenPhase = 'set' | 'rest-next';
const REST_ELAPSED_MS = 30_000;

export function executionStateAt(planSlug: string, exercise: number, phase: ScreenPhase): { state: WorkoutState; nowMs: number } {
  const plan = fixture.plans[planSlug];
  if (!plan) throw new Error(`no lab plan ${planSlug}`);
  const se = plan.exercises[exercise];
  if (!se) throw new Error(`no exercise ${exercise} in ${planSlug}`);
  const sets = setsOf(plan, se.se_id);
  let state: WorkoutState = { ...reduce(initialState, { type: 'START', plan, nowMs: 0 }), cursorSetId: sets[0].set_id };
  if (phase === 'set') return { state, nowMs: 0 };
  let now = 0;
  sets.forEach((s, i) => {
    if (i > 0) state = reduce(state, { type: 'REST_END', nowMs: now });
    if (draftFor(state, s.set_id).weight === null) state = reduce(state, { type: 'SET_VALUE', setId: s.set_id, field: 'weight', value: 40 });
    state = reduce(state, { type: 'VALIDATED', setId: s.set_id, performedAt: { epochMs: now, estimated: false }, nowMs: now });
    state = reduce(state, { type: 'LOCAL_COMMIT', setId: s.set_id, ok: true });
    now += 1000;
  });
  if (state.phase !== 'REST' || state.rest?.after.kind !== 'REST_THEN_EXERCISE') throw new Error(`no rest before a next exercise after ${exercise}`);
  return { state, nowMs: state.rest.startedMs + REST_ELAPSED_MS };
}

export function ExecutionScreenFixture(p: { width: number; height: number; plan: string; exercise: number; phase: ScreenPhase }) {
  const { state, nowMs } = executionStateAt(p.plan, p.exercise, p.phase);
  // the phone's frame and insets, given as they are: a SafeAreaProvider would re-measure them on the
  // web against the browser window (it found a 496 px « home indicator » in a 360 px tall viewport)
  return (
    <SafeAreaFrameContext.Provider value={{ x: 0, y: 0, width: p.width, height: p.height }}>
      <SafeAreaInsetsContext.Provider value={INSETS}>
        <View testID="execution-screen" style={{ width: p.width, height: p.height, overflow: 'hidden' }}>
          <ExecutionScreen state={state} nowMs={nowMs} reducedMotion {...HANDLERS} />
        </View>
      </SafeAreaInsetsContext.Provider>
    </SafeAreaFrameContext.Provider>
  );
}
