import {createHash} from 'node:crypto';
import {SqliteFile} from '../../test/sqliteFile';
import {attachProgramBuilderPending} from '../storage/programBuilderPendingCommands';
import {createSerialQueue} from '../storage/serial';
import {ProgramBuilderRecovery} from './programBuilderRecovery';
import type {BuilderReceipt} from '../api/programBuilderDTO';

const scope = 'https://qa.test.invalid';
const sha = async (s: string) => createHash('sha256').update(s).digest('hex');
const command = () => ({contract_version: 'program-builder/1.0.0', command_id: 'create-1', operation: 'CREATE',
  program_id: null, expected_source_digest: null, payload: {title: 'Personnel'}});
const receipt = (row: any): BuilderReceipt => ({contract_version: 'program-builder/1.0.0', owner_id: 7,
  command_id: row.command_id, request_sha256: row.request_sha256, operation: 'CREATE', program_id: 3,
  resulting_source_digest: 'c'.repeat(64), resulting_version: 1, publication_ids: [], selections: [], recorded_at: '2026-11-15T12:00:00Z'});
let file: SqliteFile;
beforeEach(() => {file = new SqliteFile();}); afterEach(() => file.close());
function port() {const db = file.db, p = file.port(); p.getAllAsync = async (s: string, ...a: any[]) => db.prepare(s).all(...a); return p;}
const attach = () => attachProgramBuilderPending(port(), createSerialQueue(), 7, scope, sha, () => true);

test('lost response survives restart, GET never resends, and explicit replay uses the same bytes', async () => {
  let store = await attach(); const sent: any[] = []; let confirmed = false;
  const client: any = {ownerId: 7, backendScope: scope, submit: async (row: any) => {
    sent.push({...row}); return confirmed ? {state: 'confirmed', value: receipt(row)} : {state: 'unknown'};
  }, status: async () => ({state: 'unknown'})};
  let recovery = new ProgramBuilderRecovery(client, store, () => true);
  expect(await recovery.send(command())).toEqual({state: 'unknown'});
  const old = (await store.pending(() => true))[0];
  await expect(recovery.send(command())).rejects.toThrow('builder_verification_required');
  file.reopen(); store = await attach(); recovery = new ProgramBuilderRecovery(client, store, () => true);
  expect(sent).toHaveLength(1);
  const restored = (await store.pending(() => true))[0];
  await expect(recovery.replay(restored)).rejects.toThrow('builder_verification_required');
  await recovery.verify(restored); expect(sent).toHaveLength(1);
  confirmed = true;
  expect((await recovery.replay(restored)).state).toBe('confirmed');
  expect(sent[1].payload_json).toBe(sent[0].payload_json);
  expect(sent[1].request_sha256).toBe(old.request_sha256);
  expect(sent[1].command_id).toBe(old.command_id);
  expect(await store.pending(() => true)).toEqual([]);
});

test('failed durable write prevents HTTP and changed account prevents receipt acknowledgement', async () => {
  const p = port(), store = await attachProgramBuilderPending(p, createSerialQueue(), 7, scope, sha, () => true);
  let sends = 0, active = true;
  const client: any = {ownerId: 7, backendScope: scope, submit: async (row: any) => {sends++; active = false; return {state: 'confirmed', value: receipt(row)};}, status: async () => ({state: 'unknown'})};
  const recovery = new ProgramBuilderRecovery(client, store, () => active), run = p.runAsync;
  p.runAsync = async () => {throw Error('disk unavailable');};
  await expect(recovery.send(command())).rejects.toThrow('disk unavailable'); expect(sends).toBe(0);
  p.runAsync = run;
  expect(await recovery.send(command())).toEqual({state: 'cancelled'});
  active = true; expect((await store.pending(() => true))[0].state).toBe('SENT_UNKNOWN');
});

test('lookup and retry refusal cannot certify that an earlier unknown command never applied', async () => {
  const store = await attach(); let result: any = {state: 'unknown'};
  const client: any = {ownerId: 7, backendScope: scope, submit: async () => result,
    status: async () => ({state: 'rejected', status: 406, code: 'unsupported_contract'})};
  const recovery = new ProgramBuilderRecovery(client, store, () => true);
  await recovery.send(command()); const row = (await store.pending(() => true))[0];
  await recovery.verify(row); expect((await store.get(row.command_id, () => true))?.state).toBe('SENT_UNKNOWN');
  await expect(recovery.replay(row)).rejects.toThrow('builder_verification_required');
  client.status = async () => ({state: 'unknown'}); await recovery.verify(row);
  result = {state: 'rejected', status: 403, code: 'acquisition_unavailable'};
  expect((await recovery.replay(row)).state).toBe('rejected');
  expect((await store.get(row.command_id, () => true))?.state).toBe('SENT_UNKNOWN');
});

test('known initial conflict retains the exact draft and releases only that pending root', async () => {
  const store = await attach();
  const client: any = {ownerId: 7, backendScope: scope,
    submit: async () => ({state: 'rejected', status: 409, code: 'source_conflict'}), status: async () => ({state: 'unknown'})};
  const recovery = new ProgramBuilderRecovery(client, store, () => true);
  expect((await recovery.send(command())).state).toBe('rejected');
  expect(await store.pending(() => true)).toEqual([]);
  const saved = await store.get('create-1', () => true);
  expect(saved?.state).toBe('REFUSED'); expect(JSON.parse(saved!.payload_json).payload.title).toBe('Personnel');
});
