/** Exact operational intents on the owned journal, never another programme model. */
import {builderBackendScope, builderExact, builderId, builderKey, builderSorted,
  prepareBuilderCommand, verifyPreparedBuilderCommand, type PreparedBuilderCommand} from '../domain/programBuilderCommand';
import {decodeBuilderReceipt, type BuilderReceipt} from '../api/programBuilderDTO';
import type {PlanSQL} from './planV3Journal';
import type {Serial} from './serial';

export type PendingBuilderCommand = PreparedBuilderCommand & {
  state: 'PREPARED' | 'SENT_UNKNOWN' | 'ACKED' | 'REFUSED';
  receipt: BuilderReceipt | null; rejection: string | null; rejection_status: number | null; created_at_ms: number;
};
export interface ProgramBuilderPendingCommands {
  readonly ownerId: number; readonly backendScope: string;
  prepare(body: unknown, current: () => boolean): Promise<PendingBuilderCommand>;
  get(key: string, current: () => boolean): Promise<PendingBuilderCommand | null>;
  pending(current: () => boolean): Promise<PendingBuilderCommand[]>;
  markUnknown(key: string, digest: string, current: () => boolean, initialOnly?: boolean): Promise<void>;
  ack(key: string, receipt: BuilderReceipt, current: () => boolean): Promise<void>;
  refuse(key: string, digest: string, code: string, status: number, current: () => boolean): Promise<void>;
}
const TABLE = 'program_builder_pending_commands_v1';
const INDEX = 'program_builder_one_pending_root_v1';
const columns = ['owner_id', 'backend_scope', 'command_id', 'local_version', 'logical_key', 'operation',
  'program_id', 'expected_source_digest', 'payload_json', 'request_sha256', 'created_at_ms', 'state',
  'receipt_json', 'rejection', 'rejection_status'];
const predicate = "WHERE state IN ('PREPARED','SENT_UNKNOWN')";
const SCHEMA = `CREATE TABLE IF NOT EXISTS ${TABLE}(
 owner_id INTEGER NOT NULL,backend_scope TEXT NOT NULL,command_id TEXT NOT NULL,
 local_version INTEGER NOT NULL CHECK(local_version=1),logical_key TEXT NOT NULL,operation TEXT NOT NULL,
 program_id INTEGER,expected_source_digest TEXT,payload_json TEXT NOT NULL,request_sha256 TEXT NOT NULL,
 created_at_ms INTEGER NOT NULL CHECK(created_at_ms>=0),
 state TEXT NOT NULL CHECK(state IN ('PREPARED','SENT_UNKNOWN','ACKED','REFUSED')),
 receipt_json TEXT,rejection TEXT,rejection_status INTEGER,
 PRIMARY KEY(owner_id,backend_scope,command_id));
 CREATE UNIQUE INDEX IF NOT EXISTS ${INDEX} ON ${TABLE}(owner_id,backend_scope,logical_key) ${predicate};`;
const invalid = (): never => {throw Error('invalid_builder_command');};
const logicalKey = (row: PreparedBuilderCommand) => row.program_id === null ? 'CREATE' : `PROGRAM:${row.program_id}`;

export async function attachProgramBuilderPending(db: PlanSQL, serial: Serial, owner: number, scope: string,
  sha: (value: string) => Promise<string>, attachmentCurrent: () => boolean): Promise<ProgramBuilderPendingCommands> {
  if (!builderId(owner) || !builderBackendScope(scope)) throw Error('builder_partition_invalid');
  const guard = (current: () => boolean) => {if (!attachmentCurrent() || !current()) throw Error('stale_identity');};
  const transaction = async <T,>(current: () => boolean, work: (tx: PlanSQL) => Promise<T>): Promise<T> => serial(async () => {
    guard(current); let result!: T;
    await db.withExclusiveTransactionAsync(async tx => {guard(current); result = await work(tx); guard(current);});
    guard(current); return result;
  });
  await transaction(attachmentCurrent, async tx => {
    await tx.execAsync(SCHEMA);
    const shape = await tx.getAllAsync<{name: string; pk: number}>(`PRAGMA table_info(${TABLE})`);
    if (shape.length !== columns.length || shape.some((row, i) => row.name !== columns[i])
      || shape.filter(row => row.pk > 0).map(row => row.name).join('/') !== 'owner_id/backend_scope/command_id') throw Error('builder_local_schema_unavailable');
    const indexes = await tx.getAllAsync<{name: string; unique: number; partial: number}>(`PRAGMA index_list(${TABLE})`);
    const index = indexes.find(row => row.name === INDEX);
    const parts = await tx.getAllAsync<{name: string}>(`PRAGMA index_info(${INDEX})`);
    const sql = await tx.getFirstAsync<{sql: string}>('SELECT sql FROM sqlite_master WHERE type=\'index\' AND name=?', INDEX);
    if (!index || index.unique !== 1 || index.partial !== 1 || parts.map(row => row.name).join('/') !== 'owner_id/backend_scope/logical_key'
      || !sql || !sql.sql.endsWith(predicate)) throw Error('builder_local_schema_unavailable');
  });
  const decode = async (raw: unknown, current: () => boolean): Promise<PendingBuilderCommand | null> => {
    guard(current); if (raw === null) return null;
    if (!builderExact(raw, columns) || raw.owner_id !== owner || raw.backend_scope !== scope
      || raw.local_version !== 1 || typeof raw.created_at_ms !== 'number' || !Number.isSafeInteger(raw.created_at_ms) || raw.created_at_ms < 0) return invalid();
    const prepared = await verifyPreparedBuilderCommand({owner_id: raw.owner_id, backend_scope: raw.backend_scope,
      command_id: raw.command_id, operation: raw.operation, program_id: raw.program_id,
      expected_source_digest: raw.expected_source_digest, payload_json: raw.payload_json, request_sha256: raw.request_sha256}, sha);
    guard(current); if (raw.logical_key !== logicalKey(prepared)) return invalid();
    if (!['PREPARED', 'SENT_UNKNOWN', 'ACKED', 'REFUSED'].includes(String(raw.state))) return invalid();
    let receipt: BuilderReceipt | null = null;
    if (raw.state === 'ACKED') {
      if (typeof raw.receipt_json !== 'string') throw Error('builder_receipt_mismatch');
      let value: unknown; try {value = JSON.parse(raw.receipt_json);} catch {throw Error('builder_receipt_mismatch');}
      receipt = decodeBuilderReceipt(value, owner, prepared);
      if (!receipt) throw Error('builder_receipt_mismatch');
    } else if (raw.receipt_json !== null) return invalid();
    if (raw.state === 'REFUSED') {
      if (typeof raw.rejection !== 'string' || raw.rejection.length === 0 || raw.rejection.length > 128
        || typeof raw.rejection_status !== 'number' || !Number.isInteger(raw.rejection_status)
        || raw.rejection_status < 400 || raw.rejection_status >= 500) return invalid();
    } else if (raw.rejection !== null || raw.rejection_status !== null) return invalid();
    return {...prepared, state: raw.state as PendingBuilderCommand['state'], receipt,
      rejection: raw.rejection as string | null, rejection_status: raw.rejection_status as number | null,
      created_at_ms: raw.created_at_ms};
  };
  const raw = (tx: PlanSQL, key: string) => {
    if (!builderKey(key)) return invalid();
    return tx.getFirstAsync<Record<string, unknown>>(`SELECT * FROM ${TABLE} WHERE owner_id=? AND backend_scope=? AND command_id=?`, owner, scope, key);
  };
  const get = (key: string, current: () => boolean) => serial(async () => {guard(current); return decode(await raw(db, key), current);});
  return {ownerId: owner, backendScope: scope, get,
    async prepare(body, current) {
      guard(current); const prepared = await prepareBuilderCommand(owner, scope, body, sha); guard(current);
      await transaction(current, async tx => {
        const previous = await decode(await raw(tx, prepared.command_id), current);
        if (previous) {
          if (previous.payload_json !== prepared.payload_json || previous.request_sha256 !== prepared.request_sha256) throw Error('builder_command_conflict');
          return;
        }
        const occupied = await tx.getFirstAsync(`SELECT command_id FROM ${TABLE} WHERE owner_id=? AND backend_scope=? AND logical_key=? AND state IN ('PREPARED','SENT_UNKNOWN')`, owner, scope, logicalKey(prepared));
        if (occupied) throw Error('builder_root_pending');
        await tx.runAsync(`INSERT INTO ${TABLE} VALUES(?,?,?,1,?,?,?,?,?,?,?,'PREPARED',NULL,NULL,NULL)`,
          owner, scope, prepared.command_id, logicalKey(prepared), prepared.operation, prepared.program_id,
          prepared.expected_source_digest, prepared.payload_json, prepared.request_sha256, Date.now());
      });
      const saved = await get(prepared.command_id, current); if (!saved) throw Error('builder_prepare_not_durable');
      return saved;
    },
    async pending(current) {return serial(async () => {
      guard(current);
      const rows = await db.getAllAsync<Record<string, unknown>>(`SELECT * FROM ${TABLE} WHERE owner_id=? AND backend_scope=? AND state IN ('PREPARED','SENT_UNKNOWN') ORDER BY created_at_ms,command_id LIMIT 101`, owner, scope);
      if (rows.length > 100) throw Error('builder_pending_unavailable');
      const result: PendingBuilderCommand[] = [];
      for (const row of rows) {const value = await decode(row, current); if (!value) return invalid(); result.push(value);}
      return result;
    });},
    async markUnknown(key, digest, current, initialOnly = true) {await transaction(current, async tx => {
      const saved = await decode(await raw(tx, key), current);
      if (!saved || saved.request_sha256 !== digest || saved.state === 'ACKED' || saved.state === 'REFUSED') throw Error('builder_command_not_pending');
      if (initialOnly && saved.state !== 'PREPARED') throw Error('builder_verification_required');
      await tx.runAsync(`UPDATE ${TABLE} SET state='SENT_UNKNOWN' WHERE owner_id=? AND backend_scope=? AND command_id=? AND request_sha256=?`, owner, scope, key, digest);
    });},
    async ack(key, received, current) {await transaction(current, async tx => {
      const saved = await decode(await raw(tx, key), current);
      if (!saved || !['SENT_UNKNOWN', 'ACKED'].includes(saved.state)) throw Error('builder_command_not_sent');
      const receipt = decodeBuilderReceipt(received, owner, saved);
      if (!receipt || saved.state === 'ACKED' && JSON.stringify(builderSorted(receipt)) !== JSON.stringify(builderSorted(saved.receipt))) throw Error('builder_receipt_mismatch');
      await tx.runAsync(`UPDATE ${TABLE} SET state='ACKED',receipt_json=?,rejection=NULL,rejection_status=NULL WHERE owner_id=? AND backend_scope=? AND command_id=? AND request_sha256=?`, JSON.stringify(builderSorted(receipt)), owner, scope, key, saved.request_sha256);
      await decode(await raw(tx, key), current);
    });},
    async refuse(key, digest, code, status, current) {await transaction(current, async tx => {
      const saved = await decode(await raw(tx, key), current);
      if (!saved || saved.request_sha256 !== digest || saved.state !== 'SENT_UNKNOWN'
        || typeof code !== 'string' || !code.length || code.length > 128
        || !Number.isInteger(status) || status < 400 || status >= 500) throw Error('builder_refusal_invalid');
      await tx.runAsync(`UPDATE ${TABLE} SET state='REFUSED',rejection=?,rejection_status=? WHERE owner_id=? AND backend_scope=? AND command_id=? AND request_sha256=?`, code, status, owner, scope, key, digest);
      await decode(await raw(tx, key), current);
    });}
  };
}
