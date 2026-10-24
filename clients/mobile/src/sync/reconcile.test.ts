import type { ExecutionPlan } from '../api/types';
import { initialState, reduce, WorkoutState } from '../domain/workout';
import type { JournalRow } from '../storage/outbox';
import { stateFromServer } from './reconcile';

function plan(done: ExecutionPlan['done'] = {}): ExecutionPlan {
  return {
    session_id: 9, template_slug: 'push-a', template_name: 'Push A', server_now: '2026-10-24T10:00:00+00:00',
    rest_default_seconds: 90,
    exercises: [
      { se_id: 1, code: 'E1', prescribed_name: 'Bench', executed_name: 'Bench', set_scheme: '3x8', rep_range: { min: 8, max: 10 },
        guidance: null, previous: null, prefill: { weight_kg: 40, reps: 8, origin: 'LAST_SET' }, substitutes: [], zone: null, best: null },
      { se_id: 2, code: 'E2', prescribed_name: 'Fly', executed_name: 'Fly', set_scheme: '2x12', rep_range: null,
        guidance: null, previous: null, prefill: { weight_kg: 20, reps: 12, origin: 'LAST_SET' }, substitutes: [], zone: null, best: null },
    ],
    sets: [
      { set_id: 11, se_id: 1, index: 1 }, { set_id: 12, se_id: 1, index: 2 }, { set_id: 21, se_id: 2, index: 1 },
    ],
    on_complete: {
      '11': { kind: 'REST_THEN_SET', set_id: 12 },
      '12': { kind: 'REST_THEN_EXERCISE', se_id: 2, set_id: 21 },
      '21': { kind: 'BILAN' },
    },
    status: 'in_progress', excluded_from_stats: false, started_at: '2026-10-24T09:50:00+00:00', ended_at: null,
    done, cursor_set_id: 11, allowed_actions: ['COMPLETE_SET', 'FINISH', 'PAUSE', 'ABANDON'],
  };
}

function journalRow(setId: number, sessionId = 9): JournalRow {
  return { set_id: setId, session_id: sessionId, se_id: 1, weight_kg: 42.5, reps: 8, performed_at_ms: 5,
    performed_at_estimated: 0, local_state: 'saved_local', created_at_ms: 5 };
}

test('without a local snapshot, the server position is where we resume', () => {
  const s = stateFromServer(plan({ '11': { weight_kg: 40, reps: 8, performed_at: '2026-10-24T09:55:00+00:00' } }), null, [], 0);
  expect(s.phase).toBe('SET');
  expect(s.cursorSetId).toBe(12);
  expect(s.done[11]).toMatchObject({ weight: 40, reps: 8, local: 'saved_local' });
});

test('a set recorded on the device but not yet on the server is kept, and moves the cursor', () => {
  const s = stateFromServer(plan(), null, [journalRow(11)], 0);
  expect(s.done[11]).toMatchObject({ weight: 42.5, local: 'saved_local' });
  expect(s.cursorSetId).toBe(12);
});

test('the journal of ANOTHER session is never mixed in', () => {
  const s = stateFromServer(plan(), null, [journalRow(11, 8)], 0);
  expect(s.done[11]).toBeUndefined();
});

test('the same session resumes where the instrument was — the snapshot wins over the server cursor', () => {
  let local: WorkoutState = reduce(initialState, { type: 'START', plan: plan(), nowMs: 100 });
  local = reduce(local, { type: 'VALIDATED', setId: 11, performedAt: { epochMs: 5, estimated: false }, nowMs: 200 });
  expect(local.phase).toBe('REST');
  const s = stateFromServer(plan(), local, [journalRow(11)], 300);
  expect(s.phase).toBe('REST');
  expect(s.rest?.after).toEqual({ kind: 'REST_THEN_SET', set_id: 12 });
  expect(s.done[11].local).toBe('saved_local');
});

test('a snapshot of a different session is ignored', () => {
  const other = reduce(initialState, { type: 'START', plan: { ...plan(), session_id: 8 }, nowMs: 1 });
  const s = stateFromServer(plan(), other, [], 0);
  expect(s.plan?.session_id).toBe(9);
  expect(s.cursorSetId).toBe(11);
});

test('every set recorded but the session still open: what is left is to close it', () => {
  const all = { weight_kg: 40, reps: 8, performed_at: '2026-10-24T09:55:00+00:00' };
  const s = stateFromServer(plan({ '11': all, '12': all, '21': all }), null, [], 777);
  expect(s.phase).toBe('COMPLETE');
  expect(s.completedMs).toBe(777);
});
