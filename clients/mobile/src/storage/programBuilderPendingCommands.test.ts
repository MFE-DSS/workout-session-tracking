import {createHash} from 'node:crypto';
import {SqliteFile} from '../../test/sqliteFile';
import {createSerialQueue} from './serial';
import {attachProgramBuilderPending} from './programBuilderPendingCommands';

const backend = 'https://qa.test.invalid';
const sha = async (raw: string) => createHash('sha256').update(raw).digest('hex');
const command = (id = 'create-1') => ({contract_version: 'program-builder/1.0.0', command_id: id,
  operation: 'CREATE', program_id: null, expected_source_digest: null, payload: {title: 'Personnel'}});
let file: SqliteFile;
beforeEach(() => {file = new SqliteFile();});
afterEach(() => file.close());
function port() {
  const db = file.db;
  const p = file.port();
  p.getAllAsync = async (sql: string, ...values: any[]) => db.prepare(sql).all(...values);
  return p;
}
const attach = (owner = 7, scope = backend) => attachProgramBuilderPending(port(), createSerialQueue(), owner, scope, sha, () => true);
const receipt = (row: any) => ({contract_version: 'program-builder/1.0.0' as const, owner_id: row.owner_id,
  command_id: row.command_id, request_sha256: row.request_sha256, operation: row.operation,
  program_id: row.program_id ?? 3, resulting_source_digest: 'b'.repeat(64), resulting_version: 1,
  publication_ids: [], selections: [], recorded_at: '2026-11-15T12:00:00Z'});

test('durable exact intent and unknown state survive SQLite close/reopen', async () => {
  let store = await attach();
  const saved = await store.prepare(command(), () => true);
  expect(saved.state).toBe('PREPARED');
  await store.markUnknown(saved.command_id, saved.request_sha256, () => true);
  file.reopen(); store = await attach();
  const restored = await store.get(saved.command_id, () => true);
  expect(restored?.state).toBe('SENT_UNKNOWN');
  expect(restored?.payload_json).toBe(saved.payload_json);
  expect(restored?.request_sha256).toBe(saved.request_sha256);
  expect(await store.pending(() => true)).toHaveLength(1);
});

test('separates accounts and backends and refuses conflicting intent bytes', async () => {
  const store = await attach(); const saved = await store.prepare(command(), () => true);
  expect(await (await attach(8)).get(saved.command_id, () => true)).toBeNull();
  expect(await (await attach(7, 'https://another.test.invalid')).get(saved.command_id, () => true)).toBeNull();
  await expect(store.prepare({...command(), payload: {title: 'Other'}}, () => true)).rejects.toThrow('builder_command_conflict');
  await expect(store.prepare(command('other-key'), () => true)).rejects.toThrow('builder_root_pending');
  expect((await store.get(saved.command_id, () => true))?.payload_json).toBe(saved.payload_json);
});

test('a real SQLite failure and late account change roll back before intent publication', async () => {
  const db = port(); const store = await attachProgramBuilderPending(db, createSerialQueue(), 7, backend, sha, () => true);
  const run = db.runAsync;
  db.runAsync = async (sql: string, ...args: any[]) => {if (sql.startsWith('INSERT')) throw Error('disk unavailable'); return run(sql, ...args);};
  await expect(store.prepare(command(), () => true)).rejects.toThrow('disk unavailable');
  expect(await store.pending(() => true)).toEqual([]);
  db.runAsync = run;
  let active = true;
  db.runAsync = async (sql: string, ...args: any[]) => {const result = await run(sql, ...args); if (sql.startsWith('INSERT')) active = false; return result;};
  await expect(store.prepare(command(), () => active)).rejects.toThrow('stale_identity');
  expect(await store.pending(() => true)).toEqual([]);
});

test('acknowledgement requires exact receipt identity and a sent intent', async () => {
  const store = await attach(); const row = await store.prepare(command(), () => true);
  await expect(store.ack(row.command_id, receipt(row), () => true)).rejects.toThrow();
  await store.markUnknown(row.command_id, row.request_sha256, () => true);
  await expect(store.ack(row.command_id, {...receipt(row), request_sha256: 'c'.repeat(64)}, () => true)).rejects.toThrow('builder_receipt_mismatch');
  expect((await store.get(row.command_id, () => true))?.state).toBe('SENT_UNKNOWN');
  await store.ack(row.command_id, receipt(row), () => true);
  expect(await store.pending(() => true)).toEqual([]);
  expect((await store.get(row.command_id, () => true))?.state).toBe('ACKED');
  expect((await store.get(row.command_id, () => true))?.receipt).toEqual(receipt(row));
});

test('corruption stops recovery instead of repairing exact bytes', async () => {
  const store = await attach(); await store.prepare(command(), () => true);
  file.db.prepare('UPDATE program_builder_pending_commands_v1 SET payload_json=?').run(JSON.stringify({...command(), payload: {title: 'Changed'}}));
  await expect(store.pending(() => true)).rejects.toThrow('invalid_builder_command');
});

test('an incompatible existing local schema is preserved and refused', async () => {
  file.db.exec('CREATE TABLE program_builder_pending_commands_v1 (owner_id INTEGER, preserved TEXT)');
  file.db.exec("INSERT INTO program_builder_pending_commands_v1 VALUES(7,'keep')");
  await expect(attach()).rejects.toThrow();
  expect(file.db.prepare('SELECT preserved FROM program_builder_pending_commands_v1').get().preserved).toBe('keep');
});
