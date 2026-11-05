import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createAccountRequestStore } from './accountRequestStore';
jest.mock('expo-sqlite', () => ({ openDatabaseAsync: async () => { throw Error('native-open-not-used-in-port-test'); } }));
const { DatabaseSync } = require('node:sqlite');
let file: string, folder: string, connection: any;
function adapter(db: any): any {
  const port = {
    execAsync: async (sql: string) => { db.exec(sql); },
    getFirstAsync: async (sql: string, ...values: any[]) => db.prepare(sql).get(...values) ?? null,
    runAsync: async (sql: string, ...values: any[]) => db.prepare(sql).run(...values),
    withExclusiveTransactionAsync: async (action: (tx: any) => Promise<void>) => {
      db.exec('BEGIN IMMEDIATE');
      try { await action(port); db.exec('COMMIT'); }
      catch (e) { db.exec('ROLLBACK'); throw e; }
    },
  }; return port;
}
beforeEach(() => { folder = mkdtempSync(join(tmpdir(), 'auren-request-test-')); file = join(folder, 'owners.db'); connection = new DatabaseSync(file); });
afterEach(() => { connection.close(); rmSync(folder, { recursive: true, force: true }); });
test('intent persists across a real SQLite close/reopen without storing a password', async () => {
  let store = await createAccountRequestStore(adapter(connection));
  const row = await store.reserve(7, 'request-a', () => true);
  expect(await store.claim(row, () => true)).toBe(true);
  await store.write({ ...row, phase: 'unknown' }, () => true);
  connection.close(); connection = new DatabaseSync(file);
  store = await createAccountRequestStore(adapter(connection));
  expect(await store.reserve(7, 'request-b', () => true)).toEqual({ ownerId: 7, requestId: 'request-a', phase: 'unknown' });
  expect(await store.read(8)).toBeNull();
  expect(await store.claim(row, () => true)).toBe(false);
});
test('two reserve/claim consumers share exactly one durable request', async () => {
  const store = await createAccountRequestStore(adapter(connection));
  const rows = await Promise.all([store.reserve(7, 'a', () => true), store.reserve(7, 'b', () => true)]);
  expect(rows[0].requestId).toBe(rows[1].requestId);
  const claims = await Promise.all(rows.map((row) => store.claim(row, () => true)));
  expect(claims.filter(Boolean)).toHaveLength(1);
});
test('retirement requires the same confirmed owner/request and survives restart', async () => {
  const store = await createAccountRequestStore(adapter(connection));
  const row = await store.reserve(7, 'request-a', () => true);
  await expect(store.retire(row, () => true)).rejects.toThrow();
  await store.write({ ...row, phase: 'confirmed' }, () => true);
  await expect(store.retire({ ...row, requestId: 'different' }, () => true)).rejects.toThrow();
  await store.retire({ ...row, phase: 'confirmed' }, () => true);
  expect(connection.prepare('SELECT user_id FROM owner_retirements').all()).toEqual([{ user_id: 7 }]);
  await expect(store.reserve(7, 'another', () => true)).rejects.toThrow();
});
test('identity changes inside the transaction roll back metadata', async () => {
  const port = adapter(connection); let current = true;
  const run = port.runAsync;
  port.runAsync = async (...args: any[]) => { const value = await run(...args); current = false; return value; };
  const store = await createAccountRequestStore(port);
  await expect(store.reserve(7, 'request-a', () => current)).rejects.toThrow();
  expect(await store.read(7)).toBeNull();
});

test('only an authoritatively rejected current intent can be atomically renewed', async () => {
  const store = await createAccountRequestStore(adapter(connection));
  const row = await store.reserve(7, 'request-a', () => true);
  expect(await store.renewRejected(row, 'request-b', () => true)).toBeNull();
  await store.write({ ...row, phase: 'rejected_confirmed' }, () => true);
  const attempts = await Promise.all(['request-b','request-c'].map((key)=>store.renewRejected(row,key,()=>true)));
  expect(attempts.filter(Boolean)).toHaveLength(1);
  expect(await store.read(7)).toMatchObject({ previousRequestId:'request-a', phase:'prepared' });
});
