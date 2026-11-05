import { AuthSession } from '../auth/authSession';
import { ApiFailure, type Transport } from './http';
import { AccountDeletionClient, type DeletionProducer, type DeletionStore } from './accountDeletion';

const pair = { access_token: 'test-access', refresh_token: 'rt1.fixture.secret', access_expires_in: 900,
  server_now: '2026-11-05T12:00:00Z', token_type: 'Bearer' as const };
function deferred<T>() { let resolve!: (v: T) => void; const promise = new Promise<T>((r) => { resolve = r; }); return { promise, resolve }; }
async function setup() {
  let credential: string | null = null, owner = 7;
  const rows = new Map<number, any>(), retired = new Set<number>();
  const calls: string[] = [];
  const call: Transport = async (path) => {
    calls.push(path);
    if (path === '/auth/me') return { id: owner, username: 'test-owner' } as any;
    if (path === '/auth/logout') return undefined as any;
    return pair as any;
  };
  const auth = new AuthSession(call, { read: async () => credential, write: async (v) => { credential = v; }, clear: async () => { credential = null; } });
  await auth.login('test-owner', 'test-only', null);
  const store: DeletionStore = {
    read: async (id) => rows.has(id) ? { ...rows.get(id) } : null,
    reserve: async (id, requestId, current) => {
      if (!current()) throw Error('stale');
      if (!rows.has(id)) rows.set(id, { ownerId: id, requestId, phase: 'prepared' });
      return { ...rows.get(id) };
    },
    renewRejected: async (old, key, current) => {
      if (!current()) throw Error('stale');
      const value = rows.get(old.ownerId);
      if (!value || value.requestId !== old.requestId || value.phase !== 'rejected_confirmed' || key === old.requestId) return null;
      const next = { ownerId: old.ownerId, requestId: key, previousRequestId: old.requestId, phase: 'prepared' as const };
      rows.set(old.ownerId, next); return { ...next };
    },
    claim: async (row, current) => {
      if (!current()) throw Error('stale');
      const saved = rows.get(row.ownerId);
      if (!saved || saved.requestId !== row.requestId || saved.phase !== 'prepared') return false;
      rows.set(row.ownerId, { ...saved, phase: 'submitted' }); return true;
    },
    write: async (row, current) => { if (!current()) throw Error('stale'); rows.set(row.ownerId, { ...row }); },
    retire: async (row, current) => { if (!current()) throw Error('stale'); retired.add(row.ownerId); },
  };
  const receipt = (state = 'PENDING') => ({ contract_version: 'account-deletion/1.0.0', owner_id: 7,
    request_id: 'stable-request', state, policy_ref: 'test-only-approved-policy', confirmed_at: '2026-11-05T12:00:00Z',
    revocation: 'CONFIRMED', data_erasure: 'CONFIRMED', restore_protection: 'CONFIRMED' });
  const submitted: unknown[] = [];
  let reply: unknown = receipt(), verification = true;
  const producer: DeletionProducer = {
    submit: async (_token, row, password) => { submitted.push({ ...row, password }); return reply; },
    read: async () => reply,
    verify: async () => verification,
  };
  const make = (source: DeletionProducer | null = producer, key = () => 'stable-request') => new AccountDeletionClient(auth, call, store, source, key);
  return { auth, store, make, rows, retired, submitted, calls, receipt, producer,
    setReply: (value: unknown) => { reply = value; }, denyVerification: () => { verification = false; },
    owner: (id: number) => { owner = id; }, credential: () => credential };
}

test('no deletion producer means unavailable, without fabricated request or network endpoint', async () => {
  const s = await setup(); s.calls.length = 0;
  expect(await s.make(null).submit('test-only-password')).toEqual({ state: 'unavailable' });
  expect(s.calls).toEqual([]); expect(s.rows.size).toBe(0);
});
test('lost response persists an unknown intent and relaunch only reconciles the same request', async () => {
  const s = await setup();
  s.producer.submit = async () => { throw new ApiFailure('network'); };
  expect((await s.make().submit('test-only-password')).state).toBe('unknown');
  expect(s.rows.get(7)).toEqual({ ownerId: 7, requestId: 'stable-request', phase: 'unknown' });
  s.producer.submit = async () => { throw Error('must not replay'); };
  const relaunched = s.make();
  expect((await relaunched.submit('test-only-password')).state).toBe('unknown');
  expect((await relaunched.reconcile()).state).toBe('pending');
  expect(JSON.stringify([...s.rows.values()])).not.toContain('password');
});
test('double appui sends exactly one mutation', async () => {
  const s = await setup(), wait = deferred<unknown>(); let sends = 0;
  s.producer.submit = async () => { sends++; return wait.promise; };
  const client = s.make(), first = client.submit('test-only-password');
  expect((await client.submit('test-only-password')).state).toBe('pending');
  wait.resolve(s.receipt()); expect((await first).state).toBe('pending'); expect(sends).toBe(1);
});
test.each([401, 404, 503])('a failed reconciliation %s never proves erasure or cleans locally', async (code) => {
  const s = await setup(), client = s.make();
  await client.submit('test-only-password');
  s.producer.read = async () => { throw new ApiFailure('http', code); };
  expect((await client.reconcile()).state).toBe('unknown');
  expect(s.retired.size).toBe(0); expect(s.credential()).not.toBeNull();
});
test.each(['owner', 'request', 'version', 'revocation', 'restoration', 'authority'])('invalid %s cannot authorize client cleanup', async (kind) => {
  const s = await setup(), raw: any = s.receipt('DELETED');
  if (kind === 'owner') raw.owner_id = 8;
  if (kind === 'request') raw.request_id = 'different-request';
  if (kind === 'version') raw.contract_version = 'unknown';
  if (kind === 'revocation') raw.revocation = 'UNKNOWN';
  if (kind === 'restoration') raw.restore_protection = 'UNKNOWN';
  if (kind === 'authority') s.denyVerification();
  s.setReply(raw);
  const client = s.make(), result = await client.submit('test-only-password');
  expect(result.state).toBe('unknown');
  expect(await client.complete(result, async () => { throw Error('must not clean'); })).toBe(false);
  expect(s.retired.size).toBe(0);
});
test('only a verified result issued by this client retires before logout and scoped cleanup', async () => {
  const s = await setup(); s.setReply(s.receipt('DELETED'));
  const client = s.make(), result = await client.submit('test-only-password');
  expect(result.state).toBe('confirmed');
  expect(await client.complete({ ...result }, async () => undefined)).toBe(false);
  let cleaned = 0;
  expect(await client.complete(result, async (id) => {
    expect(id).toBe(7); expect(s.retired.has(7)).toBe(true); expect(s.auth.signedIn).toBe(false); cleaned++;
  })).toBe(true);
  expect(cleaned).toBe(1); expect(s.credential()).toBeNull();
  expect(await client.complete(result, async () => { cleaned++; })).toBe(false);
  expect(cleaned).toBe(1);
});
test('a reply from a departed account cannot retire, log out or clean the new account', async () => {
  const s = await setup(), wait = deferred<unknown>();
  s.producer.submit = async () => wait.promise;
  const client = s.make(), sending = client.submit('test-only-password');
  for (let i=0;i<12;i++) await Promise.resolve();
  await s.auth.logout(); s.owner(8); await s.auth.login('next', 'test-only', null);
  wait.resolve(s.receipt('DELETED'));
  const result = await sending; expect(result.state).toBe('cancelled');
  expect(await client.complete(result, async () => undefined)).toBe(false);
  expect(s.retired.size).toBe(0); expect(s.auth.signedIn).toBe(true);
});
test('blocked policy remains unavailable and never pretends to be deleted', async () => {
  const s = await setup(); s.setReply(s.receipt('POLICY_REQUIRED'));
  expect((await s.make().submit('test-only-password')).state).toBe('unavailable');
  expect(s.retired.size).toBe(0);
});

test('two consumers sharing durable state claim one submission only', async () => {
  const s = await setup(), wait = deferred<unknown>(); let sends = 0;
  s.producer.submit = async () => { sends++; return wait.promise; };
  const a = s.make().submit('test-only-password'), b = s.make().submit('test-only-password');
  for (let i=0;i<20;i++) await Promise.resolve();
  wait.resolve(s.receipt()); await Promise.all([a,b]);
  expect(sends).toBe(1);
});

test('a terminal rejection can be reconciled and explicitly renewed with a linked new intent', async () => {
  const s = await setup(); let sends = 0;
  s.producer.submit = async (_t, row, password) => { sends++; return { ...s.receipt(password === 'bad' ? 'REJECTED' : 'PENDING'), request_id: row.requestId }; };
  s.setReply(s.receipt('REJECTED'));
  expect((await s.make().submit('bad')).state).toBe('rejected');
  const resumed = s.make(s.producer, () => 'request-2');
  expect((await resumed.reconcile()).state).toBe('rejected');
  expect((await resumed.retryRejected('correct')).state).toBe('pending');
  expect(s.rows.get(7)).toMatchObject({ requestId: 'request-2', previousRequestId: 'stable-request', phase: 'pending' });
  expect(sends).toBe(2);
});
test('unknown or unauthenticated rejection cannot be renewed', async () => {
  const s = await setup(); s.setReply(s.receipt('REJECTED')); s.denyVerification();
  const client = s.make(s.producer, () => 'request-2');
  await s.make().submit('bad');
  expect((await client.retryRejected('correct')).state).toBe('rejected');
  expect(s.rows.get(7).requestId).toBe('stable-request');
  s.rows.set(7, { ownerId: 7, requestId: 'stable-request', phase: 'unknown' });
  expect((await client.retryRejected('correct')).state).toBe('unknown');
  expect(s.rows.get(7).requestId).toBe('stable-request');
});
test('concurrent explicit renewals still send one new request', async () => {
  const s = await setup(); s.setReply(s.receipt('REJECTED'));
  await s.make().submit('bad'); let sends = 0;
  s.producer.submit = async (_t, row) => { sends++; return { ...s.receipt(), request_id: row.requestId }; };
  await Promise.all([s.make(s.producer,()=> 'request-2').retryRejected('correct'), s.make(s.producer,()=> 'request-3').retryRejected('correct')]);
  expect(sends).toBe(1);
});
