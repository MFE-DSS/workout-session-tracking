import { ApiFailure, type Transport } from './http';
import { AuthSession } from '../auth/authSession';
import { TrainingPreferencesClient } from './trainingPreferences';

const declarations = { sessions_per_week: null, focus_priorities: null, available_equipment: null };
const snapshot = { contract_version: 1, declarations, options: {
  sessions_per_week: { min: 1, max: 7 }, focus_priorities: [{ value: 'arms', label: 'Bras' }],
  available_equipment: [{ value: 'barbell', label: 'Barre libre' }],
} };
const pair = { access_token: 'test-access', refresh_token: 'rt1.test.secret', access_expires_in: 900,
  server_now: '2026-11-05T12:00:00Z', token_type: 'Bearer' as const };

function deferred<T>() {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>((r) => { resolve = r; });
  return { promise, resolve };
}
async function setup(resource: Transport) {
  let credential: string | null = null;
  const seen: { path: string; method?: string }[] = [];
  const call: Transport = async (path, init) => {
    seen.push({ path, method: init?.method });
    if (path === '/auth/login' || path === '/auth/refresh') return pair as any;
    if (path === '/auth/logout') return undefined as any;
    return resource(path, init);
  };
  const auth = new AuthSession(call, { read: async () => credential, write: async (v) => { credential = v; }, clear: async () => { credential = null; } });
  await auth.login('test-user', 'test-password', null);
  return { auth, seen, client: new TrainingPreferencesClient(auth, call) };
}

test('read preserves absent and explicitly empty declarations from the server', async () => {
  const s = await setup(async () => ({ ...snapshot, declarations: { ...declarations, focus_priorities: [] } }) as any);
  expect(await s.client.read()).toEqual({ state: 'confirmed', value: { ...snapshot, declarations: { ...declarations, focus_priorities: [] } } });
});

test('save sends a complete declaration with a bearer, once, and returns the server fact', async () => {
  const sent: any[] = [];
  const s = await setup(async (path, init) => {
    sent.push({ path, ...init });
    return { ...snapshot, declarations: { ...declarations, sessions_per_week: 4 } } as any;
  });
  expect(await s.client.save({ ...declarations, sessions_per_week: 4 })).toEqual({ state: 'confirmed', value: { ...snapshot, declarations: { ...declarations, sessions_per_week: 4 } } });
  expect(sent).toEqual([{ path: '/me/training-preferences/declarations', method: 'PUT', token: 'test-access', body: { ...declarations, sessions_per_week: 4 } }]);
});

test.each([new ApiFailure('network'), new ApiFailure('http', 503)])('a lost or uncertain response never acknowledges or replays a write (%s)', async (failure) => {
  const s = await setup(async () => { throw failure; });
  expect(await s.client.save(declarations)).toEqual({ state: 'unknown' });
  expect(s.seen.filter((r) => r.method === 'PUT')).toHaveLength(1);
});

test('401 on a write is refused without refreshing and replaying that mutation', async () => {
  const s = await setup(async () => { throw new ApiFailure('http', 401, 'expired'); });
  expect(await s.client.save(declarations)).toEqual({ state: 'rejected', code: 'expired' });
  expect(s.seen.map((r) => r.path)).toEqual(['/auth/login', '/me/training-preferences/declarations']);
});

test('late responses from an old account cannot become current preferences', async () => {
  const reply = deferred<any>();
  const s = await setup(async () => reply.promise);
  const reading = s.client.read();
  await Promise.resolve();
  await s.auth.logout();
  await s.auth.login('another-user', 'another-password', null);
  reply.resolve(snapshot);
  expect(await reading).toEqual({ state: 'cancelled' });
});

test('a second write cannot replace or acknowledge a different in-flight declaration', async () => {
  const reply = deferred<any>();
  const s = await setup(async () => reply.promise);
  const first = s.client.save(declarations);
  expect(await s.client.save({ ...declarations, sessions_per_week: 6 })).toEqual({ state: 'rejected', code: 'request_in_flight' });
  reply.resolve(snapshot);
  expect((await first).state).toBe('confirmed');
  expect(s.seen.filter((r) => r.method === 'PUT')).toHaveLength(1);
});

test('an unknown contract version cannot be displayed as confirmed', async () => {
  const s = await setup(async () => ({ ...snapshot, contract_version: 2 }) as any);
  expect(await s.client.read()).toEqual({ state: 'unknown' });
});
