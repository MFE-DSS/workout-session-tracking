import { resolveJournal, type OwnershipBook } from './ownership';
import { ApiFailure } from '../api/http';
import { initialState } from '../domain/workout';
import type { Restored } from './journalTypes';

function book() {
  const devices = new Map<string, number>();
  const names = new Map<number, string>();
  let legacy: number | null = null;
  const value: OwnershipBook = {
    isRetiredOwner: async () => false,
    ownerOfDevice: async (id) => devices.get(id) ?? null,
    journalOf: async (id) => names.get(id) ?? null,
    legacyOwner: async () => legacy,
    claimLegacy: async (id) => { if (legacy !== null && legacy !== id) return false; legacy = id; names.set(id, 'auren.db'); return true; },
    assignJournal: async (id, name) => { names.set(id, name); },
    bindDevice: async (device, id) => { devices.set(device, id); },
  };
  return { value, devices, names, legacy: () => legacy };
}
const empty: Restored = { snapshot: null, sets: [], outbox: [] };
function legacyWith(...ids: number[]): Restored {
  return { ...empty, outbox: ids.map((session_id, i) => ({ op_id: `op-${i}`, kind: 'SESSION_FINISH',
    target: `session/${session_id}`, payload: JSON.stringify({ session_id }), created_at_ms: i, attempts: 0, state: 'pending' })) };
}
function request(b: OwnershipBook, legacy: Restored = empty) {
  return { book: b, deviceId: 'device-a', online: true,
    identity: async () => ({ id: 7, username: 'athlete' }), inspectLegacy: async () => legacy,
    verifySession: async (id: number) => ({ session_id: id }),
  };
}

test('all legacy session identities must be verified before assigning the original file', async () => {
  const b = book(); const checked: number[] = [];
  const result = await resolveJournal({ ...request(b.value, legacyWith(11, 12)), verifySession: async (id) => { checked.push(id); return { session_id: id }; } });
  expect(checked).toEqual([11, 12]);
  expect(result).toEqual({ state: 'ready', userId: 7, name: 'auren.db', quarantined: false });
  expect(b.legacy()).toBe(7);
});

test('a mixed legacy file stays unassigned, while a different user gets an empty partition', async () => {
  const b = book();
  const result = await resolveJournal({ ...request(b.value, legacyWith(11, 12)), verifySession: async (id) => {
    if (id === 12) throw new ApiFailure('http', 404); return { session_id: id };
  } });
  expect(result).toEqual({ state: 'ready', userId: 7, name: 'auren-user-7.db', quarantined: true });
  expect(b.legacy()).toBeNull();
});

test('offline restart permits only an earlier server-bound device and partition', async () => {
  const b = book();
  await resolveJournal(request(b.value, legacyWith(11)));
  let calls = 0;
  const result = await resolveJournal({ ...request(b.value), online: false, identity: async () => { calls++; throw Error(); } });
  expect(result).toEqual({ state: 'ready', userId: 7, name: 'auren.db', quarantined: false });
  expect(calls).toBe(0);
  expect(await resolveJournal({ ...request(b.value), deviceId: 'new-device', online: false })).toEqual({ state: 'needs-connection' });
});

test('a server verified new user never reuses the previous users partition or displayed name', async () => {
  const b = book();
  await resolveJournal(request(b.value, legacyWith(11)));
  const result = await resolveJournal({ ...request(b.value), identity: async () => ({ id: 8, username: 'athlete' }) });
  expect(result).toEqual({ state: 'ready', userId: 8, name: 'auren-user-8.db', quarantined: false });
  expect(b.names.get(7)).toBe('auren.db');
});

test.each(['bad-json', JSON.stringify({ session_id: '11' }), JSON.stringify({})])('malformed command preserves an unassigned file: %s', async (payload) => {
  const b = book(); const legacy = legacyWith(11); legacy.outbox[0].payload = payload;
  const result = await resolveJournal(request(b.value, legacy));
  expect(result.state === 'ready' && result.quarantined).toBe(true);
  expect(b.legacy()).toBeNull();
});

test('legacy MISSION snapshot alone is not proof for a persisted foreign set', async () => {
  const b = book();
  const legacy: Restored = { snapshot: initialState, outbox: [], sets: [{ set_id: 1, session_id: 99, se_id: 1, weight_kg: 10, reps: 8,
    performed_at_ms: 1, performed_at_estimated: 0, local_state: 'saved_local', created_at_ms: 1 }] };
  const result = await resolveJournal({ ...request(b.value, legacy), verifySession: async () => { throw new ApiFailure('http', 404); } });
  expect(result.state === 'ready' && result.quarantined).toBe(true);
  expect(b.legacy()).toBeNull();
});

test('transient verification failure requires connection and does not assign or bind anything', async () => {
  const b = book();
  expect(await resolveJournal({ ...request(b.value, legacyWith(11)), verifySession: async () => { throw new ApiFailure('network'); } })).toEqual({ state: 'needs-connection' });
  expect(b.legacy()).toBeNull(); expect(b.devices.size).toBe(0); expect(b.names.size).toBe(0);
});

test('revoked identity cannot use cached ownership as an authentication fallback', async () => {
  const b = book(); await resolveJournal(request(b.value));
  await expect(resolveJournal({ ...request(b.value), identity: async () => { throw new ApiFailure('http', 401); } })).rejects.toMatchObject({ status: 401 });
});

test('a changed identity cancels legacy proof before any metadata attribution', async () => {
  const b = book(); let current = true;
  const result = resolveJournal({ ...request(b.value, legacyWith(11)), isCurrent: () => current,
    verifySession: async (id) => { current = false; return { session_id: id }; } });
  await expect(result).rejects.toMatchObject({ status: 401 });
  expect(b.legacy()).toBeNull(); expect(b.devices.size).toBe(0); expect(b.names.size).toBe(0);
});

test.each([
  { phase: 'SET', plan: { session_id: 11 } },
  { ...initialState, phase: 'INVALID' },
  { ...initialState, done: [] },
])('malformed snapshot never claims the legacy journal even with an owned session id', async (snapshot) => {
  const b = book();
  const result = await resolveJournal(request(b.value, { ...empty, snapshot: snapshot as never }));
  expect(result.state === 'ready' && result.quarantined).toBe(true);
  expect(b.legacy()).toBeNull();
});

test.each([true, false])('retired owner cannot reopen a journal online=%s', async (online) => {
  const b = book();
  b.devices.set('device-a', 7); b.names.set(7, 'auren.db');
  const value = { ...b.value, isRetiredOwner: async () => true };
  expect(await resolveJournal({ ...request(value), online })).toEqual({ state: 'needs-connection' });
  expect(b.names.get(7)).toBe('auren.db');
});

test('retirement during an offline metadata read cannot return a ready journal', async () => {
  const b = book(); b.devices.set('device-a',7); b.names.set(7,'auren.db'); let retired = false;
  const value = { ...b.value, isRetiredOwner: async () => retired,
    journalOf: async () => { retired = true; return 'auren.db'; } };
  expect(await resolveJournal({ ...request(value), online: false })).toEqual({ state: 'needs-connection' });
});
