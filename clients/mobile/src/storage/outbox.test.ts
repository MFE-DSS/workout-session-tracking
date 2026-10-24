import rawFixture from '../fixtures/lab_fixture.json';
import type { LabFixture } from '../domain/types';
import { initialState, reduce } from '../domain/workout';
import { compactPending, JournalRow, OutboxRow, restoreState, retryDelayMs, setCommand } from './outbox';

const fixture = rawFixture as unknown as LabFixture;

function row(over: Partial<OutboxRow>): OutboxRow {
  return { op_id: 'x', kind: 'SET_COMPLETION', target: 'set/1', payload: '{}', created_at_ms: 0, attempts: 0, state: 'pending', ...over };
}

describe('outbox — one command per training fact', () => {
  test('a set command targets exactly one set and carries its execution time', () => {
    const c = setCommand('op-1', 9, 194, 52.5, 11, { epochMs: Date.UTC(2026, 9, 23, 10), estimated: false });
    expect(c.target).toBe('set/194');
    expect(c.payload).toEqual({
      session_id: 9, set_id: 194, weight_kg: 52.5, reps: 11,
      performed_at: '2026-10-23T10:00:00.000Z', performed_at_estimated: false,
      // engine V2 ruling 7: RIR is OPTIONAL in the contract and never asked in N0
      rir: null,
    });
  });

  test('two pending commands on the same set collapse to the latest', () => {
    const out = compactPending([row({ op_id: 'a', created_at_ms: 1 }), row({ op_id: 'b', created_at_ms: 2 }), row({ op_id: 'c', target: 'set/2', created_at_ms: 3 })]);
    expect(out.map((r) => r.op_id)).toEqual(['b', 'c']);
  });

  test('an in-flight command is never rewritten', () => {
    const out = compactPending([row({ op_id: 'a', state: 'inflight', created_at_ms: 1 }), row({ op_id: 'b', created_at_ms: 2 })]);
    expect(out.map((r) => r.op_id)).toEqual(['a', 'b']);
  });

  test('retry backoff grows and is capped', () => {
    expect(retryDelayMs(0)).toBe(1000);
    expect(retryDelayMs(3)).toBe(8000);
    expect(retryDelayMs(30)).toBe(300_000);
  });
});

describe('restore after a kill — the journal wins over the snapshot', () => {
  const plan = fixture.plans['push-a'];
  const s1 = plan.sets[0].set_id;
  const s2 = plan.sets[1].set_id;
  const T = 1_800_000_000_000;

  const snapshot = [
    { type: 'START' as const, plan, nowMs: T },
    { type: 'VALIDATED' as const, setId: s1, performedAt: { epochMs: T + 1, estimated: false }, nowMs: T + 1 },
    { type: 'REST_END' as const, nowMs: T + 90_001 },
    { type: 'VALIDATED' as const, setId: s2, performedAt: { epochMs: T + 2, estimated: false }, nowMs: T + 120_000 },
  ].reduce(reduce, initialState);

  const journalRow: JournalRow = {
    set_id: s1, session_id: plan.session_id, se_id: plan.sets[0].se_id, weight_kg: 52.5, reps: 11,
    performed_at_ms: T + 1, performed_at_estimated: 0, local_state: 'saved_local', created_at_ms: T + 1,
  };

  test('a set in the journal is shown saved on the device', () => {
    const r = restoreState(snapshot, [journalRow]);
    expect(r.done[s1].local).toBe('saved_local');
  });

  test('a set the snapshot believed pending but the journal never got is shown NOT saved — never silently', () => {
    const r = restoreState(snapshot, [journalRow]);
    expect(r.done[s2].local).toBe('not_saved');
  });

  test('the instrument comes back where it was (phase, cursor, rest deadline)', () => {
    const r = restoreState(snapshot, [journalRow]);
    expect(r.phase).toBe('REST');
    expect(r.rest!.deadlineMs).toBe(snapshot.rest!.deadlineMs);
  });

  test('journal rows of another session are not mixed in', () => {
    const other = { ...journalRow, session_id: plan.session_id + 1, set_id: 999 };
    expect(restoreState(snapshot, [other]).done[999]).toBeUndefined();
  });
});
