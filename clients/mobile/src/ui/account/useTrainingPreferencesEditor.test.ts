import React, { act } from 'react';
import { createRoot, type Root } from 'test-renderer';
import { AuthSession } from '../../auth/authSession';
import { ApiFailure, type Transport } from '../../api/http';
import { TrainingPreferencesClient, type TrainingDeclarations } from '../../api/trainingPreferences';
import { useTrainingPreferencesEditor } from './useTrainingPreferencesEditor';

const original: TrainingDeclarations = { sessions_per_week: null, focus_priorities: ['arms'], available_equipment: [] };
const projection = (declarations = original) => ({ contract_version: 1, declarations, options: {
  sessions_per_week: { min: 1, max: 7 }, focus_priorities: [{ value: 'arms', label: 'Bras' }],
  available_equipment: [{ value: 'barbell', label: 'Barre libre' }],
} });
function deferred<T>() { let resolve!: (v: T) => void; const promise = new Promise<T>((r) => { resolve = r; }); return { resolve, promise }; }
async function service(resource: Transport) {
  let credential: string | null = null;
  const writes: any[] = [];
  const call: Transport = async (path, init) => {
    if (path === '/auth/login' || path === '/auth/refresh') return { access_token: 'test', refresh_token: 'rt1.test.secret', access_expires_in: 900, server_now: '2026-11-05T12:00:00Z', token_type: 'Bearer' } as any;
    if (path === '/auth/logout') return undefined as any;
    if (init?.method === 'PUT') writes.push(init.body);
    return resource(path, init);
  };
  const auth = new AuthSession(call, { read: async () => credential, write: async (v) => { credential = v; }, clear: async () => { credential = null; } });
  await auth.login('test', 'test-password', null);
  return { client: new TrainingPreferencesClient(auth, call), auth, writes };
}
let root: Root;
let editor: ReturnType<typeof useTrainingPreferencesEditor>;
function Harness({ client }: { client: TrainingPreferencesClient }) { editor = useTrainingPreferencesEditor(client); return null; }
beforeEach(() => { root = createRoot(); });
afterEach(async () => { await act(async () => root.unmount()); });
const mount = async (client: TrainingPreferencesClient) => { await act(async () => root.render(React.createElement(Harness, { client }))); };

test('no draft exists before the first confirmed read; null and [] remain distinct', async () => {
  const reply = deferred<any>(); const s = await service(async () => reply.promise);
  await mount(s.client);
  expect(editor.phase).toBe('loading'); expect(editor.draft).toBeNull();
  await act(async () => reply.resolve(projection()));
  expect(editor.phase).toBe('ready'); expect(editor.draft).toEqual(original); expect(editor.dirty).toBe(false);
});

test('changing cadence sends all known declarations and adopts only the confirmed server result', async () => {
  const s = await service(async (_path, init) => projection(init?.body as any ?? original) as any);
  await mount(s.client);
  act(() => editor.edit({ sessions_per_week: 4 }));
  expect(editor.dirty).toBe(true);
  await act(async () => editor.save());
  expect(s.writes).toEqual([{ ...original, sessions_per_week: 4 }]);
  expect(editor.phase).toBe('saved'); expect(editor.dirty).toBe(false);
  expect(editor.snapshot?.declarations.sessions_per_week).toBe(4);
});

test('an uncertain save cannot be repeated and an explicit read preserves a different local draft', async () => {
  const s = await service(async (_path, init) => { if (init?.method === 'PUT') throw new ApiFailure('network'); return projection() as any; });
  await mount(s.client); act(() => editor.edit({ sessions_per_week: 4 }));
  await act(async () => editor.save());
  expect(editor.phase).toBe('unknown');
  await act(async () => editor.save());
  expect(s.writes).toHaveLength(1);
  await act(async () => editor.reload());
  expect(editor.phase).toBe('ready'); expect(editor.draft?.sessions_per_week).toBe(4);
  expect(editor.snapshot?.declarations.sessions_per_week).toBeNull(); expect(editor.dirty).toBe(true);
});

test('read reconciliation can find the current server values without sending another mutation', async () => {
  let current = original;
  const s = await service(async (_path, init) => { if (init?.method === 'PUT') { current = init.body as any; throw new ApiFailure('network'); } return projection(current) as any; });
  await mount(s.client); act(() => editor.edit({ sessions_per_week: 4 }));
  await act(async () => editor.save()); await act(async () => editor.reload());
  expect(editor.phase).toBe('ready'); expect(editor.dirty).toBe(false);
  expect(editor.snapshot?.declarations.sessions_per_week).toBe(4); expect(s.writes).toHaveLength(1);
});

test('business refusal preserves the draft and never displays saved', async () => {
  const s = await service(async (_path, init) => { if (init?.method === 'PUT') throw new ApiFailure('http', 400, 'invalid_training_preferences'); return projection() as any; });
  await mount(s.client); act(() => editor.edit({ sessions_per_week: 4 }));
  await act(async () => editor.save());
  expect(editor.phase).toBe('ready'); expect(editor.draft?.sessions_per_week).toBe(4);
  expect(editor.outcome).toEqual({ state: 'rejected', code: 'invalid_training_preferences' });
});

test('immediate double save and edits during a write cannot change or duplicate its payload', async () => {
  const reply = deferred<any>();
  const s = await service(async (_path, init) => init?.method === 'PUT' ? reply.promise : projection() as any);
  await mount(s.client); act(() => editor.edit({ sessions_per_week: 4 }));
  let first!: Promise<void>;
  act(() => { first = editor.save(); void editor.save(); editor.edit({ sessions_per_week: 6 }); });
  expect(editor.phase).toBe('saving'); expect(editor.draft?.sessions_per_week).toBe(4);
  await act(async () => { reply.resolve(projection({ ...original, sessions_per_week: 4 })); await first; });
  expect(s.writes).toEqual([{ ...original, sessions_per_week: 4 }]);
});

test('a failed initial read never opens a form populated with invented defaults', async () => {
  const s = await service(async () => { throw new ApiFailure('network'); });
  await mount(s.client); expect(editor.phase).toBe('unavailable');
  expect(editor.draft).toBeNull(); expect(editor.snapshot).toBeNull();
});

test('replacing the client drops old owner state and ignores its late reply and callbacks', async () => {
  const reply = deferred<any>();
  const a = await service(async () => reply.promise);
  const b = await service(async () => projection({ ...original, sessions_per_week: 6 }) as any);
  await mount(a.client); const old = editor;
  await mount(b.client);
  await act(async () => { old.edit({ sessions_per_week: 1 }); await old.save(); reply.resolve(projection()); });
  expect(editor.draft?.sessions_per_week).toBe(6); expect(a.writes).toHaveLength(0);
});

test('a response cancelled by an authentication change clears every old owner declaration', async () => {
  const reply = deferred<any>();
  const s = await service(async (_path, init) => init?.method === 'PUT' ? reply.promise : projection() as any);
  await mount(s.client); act(() => editor.edit({ sessions_per_week: 4 }));
  let first!: Promise<void>; act(() => { first = editor.save(); });
  await act(async () => { await s.auth.logout(); reply.resolve(projection()); await first; });
  expect(editor.phase).toBe('expired'); expect(editor.draft).toBeNull(); expect(editor.snapshot).toBeNull();
});
