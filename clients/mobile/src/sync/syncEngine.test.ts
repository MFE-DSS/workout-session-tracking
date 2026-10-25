import { ApiFailure } from '../api/http';
import type { OutboxRow } from '../storage/outbox';
import { classify, SyncEngine, SyncStatus } from './syncEngine';

jest.useFakeTimers();

function row(op: string, kind = 'SET_COMPLETION', at = 1): OutboxRow {
  return { op_id: op, kind, target: `set/${op}`, payload: '{}', created_at_ms: at, attempts: 0, state: 'pending' };
}

function journal(rows: OutboxRow[]) {
  const j = {
    rows,
    outboxRows: async () => j.rows.filter((r) => r.state !== 'acked'),
    markOutbox: async (op: string, state: OutboxRow['state'], attempts: number) => {
      j.rows = j.rows.map((r) => (r.op_id === op ? { ...r, state, attempts } : r));
    },
  };
  return j;
}

function stateOf(j: ReturnType<typeof journal>) {
  return Object.fromEntries(j.rows.map((r) => [r.op_id, r.state]));
}

test('acknowledged commands leave the queue, in order', async () => {
  const j = journal([row('a', 'SET_COMPLETION', 1), row('b', 'SET_COMPLETION', 2), row('c', 'SESSION_FINISH', 3)]);
  const sent: string[] = [];
  await new SyncEngine(j, async (r) => sent.push(r.op_id), () => undefined).kick();
  expect(sent).toEqual(['a', 'b', 'c']);
  expect(stateOf(j)).toEqual({ a: 'acked', b: 'acked', c: 'acked' });
});

test('a network failure keeps the row pending and STOPS the drain (order is kept)', async () => {
  const j = journal([row('a', 'SET_COMPLETION', 1), row('finish', 'SESSION_FINISH', 2)]);
  const sent: string[] = [];
  const statuses: SyncStatus[] = [];
  const engine = new SyncEngine(j, async (r) => {
    sent.push(r.op_id);
    throw new ApiFailure('network');
  }, (s) => statuses.push(s));
  await engine.kick();
  expect(sent).toEqual(['a']);
  expect(stateOf(j)).toEqual({ a: 'pending', finish: 'pending' });
  expect(j.rows[0].attempts).toBe(1);
  expect(statuses.at(-1)).toMatchObject({ pending: 2, offline: true, syncing: false });
  engine.stop();
});

test('it retries by itself once the network is back', async () => {
  const j = journal([row('a')]);
  let online = false;
  const engine = new SyncEngine(j, async () => {
    if (!online) throw new ApiFailure('network');
  }, () => undefined);
  await engine.kick();
  online = true;
  await jest.advanceTimersByTimeAsync(1100);
  expect(stateOf(j)).toEqual({ a: 'acked' });
});

test('a refusal the server will repeat is kept as FAILED and does not block the rest', async () => {
  const j = journal([row('bad', 'SET_COMPLETION', 1), row('ok', 'SET_COMPLETION', 2)]);
  const statuses: SyncStatus[] = [];
  await new SyncEngine(j, async (r) => {
    if (r.op_id === 'bad') throw new ApiFailure('http', 422, 'performed_at_out_of_bounds');
  }, (s) => statuses.push(s)).kick();
  expect(stateOf(j)).toEqual({ bad: 'failed', ok: 'acked' });
  expect(statuses.at(-1)).toMatchObject({ attention: 1, pending: 0 });
});

test('a failed row is never discarded and can be sent again by hand', async () => {
  const j = journal([row('x')]);
  let refuse = true;
  const engine = new SyncEngine(j, async () => {
    if (refuse) throw new ApiFailure('http', 409, 'session_closed');
  }, () => undefined);
  await engine.kick();
  expect(j.rows).toHaveLength(1);
  refuse = false;
  await engine.retry('x');
  expect(stateOf(j)).toEqual({ x: 'acked' });
});

test('an inflight row left by a crash is sent again (the server acknowledges duplicates)', async () => {
  const j = journal([{ ...row('a'), state: 'inflight' }]);
  const sent: string[] = [];
  await new SyncEngine(j, async (r) => sent.push(r.op_id), () => undefined).kick();
  expect(sent).toEqual(['a']);
});

test('parallel kicks never send the same command twice at once', async () => {
  const j = journal([row('a')]);
  let inFlight = 0;
  let maxInFlight = 0;
  const engine = new SyncEngine(j, async () => {
    inFlight++;
    maxInFlight = Math.max(maxInFlight, inFlight);
    await Promise.resolve();
    inFlight--;
  }, () => undefined);
  await Promise.all([engine.kick(), engine.kick(), engine.kick()]);
  expect(maxInFlight).toBe(1);
  expect(stateOf(j)).toEqual({ a: 'acked' });
});

test('classification', () => {
  expect(classify(new ApiFailure('network'))).toBe('retry');
  expect(classify(new ApiFailure('http', 503))).toBe('retry');
  expect(classify(new ApiFailure('http', 429))).toBe('retry');
  expect(classify(new ApiFailure('http', 401))).toBe('auth');
  expect(classify(new ApiFailure('http', 404))).toBe('attention');
  expect(classify(new ApiFailure('http', 409))).toBe('attention');
  expect(classify(new ApiFailure('http', 422))).toBe('attention');
  expect(classify(new Error('boom'))).toBe('attention');
});
