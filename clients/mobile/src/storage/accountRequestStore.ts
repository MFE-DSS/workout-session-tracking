/** Durable, non-secret request intent in the ownership metadata DB, never the workout journal. */
import * as SQLite from 'expo-sqlite';
import { ApiFailure } from '../api/http';
import type { DeletionIntent, DeletionStore } from '../api/accountDeletion';
import { createSerialQueue } from './serial';

type Value = string | number | null;
type SqlPort = {
  execAsync(sql: string): Promise<void>;
  getFirstAsync<T>(sql: string, ...values: Value[]): Promise<T | null>;
  runAsync(sql: string, ...values: Value[]): Promise<unknown>;
};
type DB = SqlPort & { withExclusiveTransactionAsync(action: (tx: SqlPort) => Promise<void>): Promise<void> };
type Row = { user_id: number; request_id: string; phase: DeletionIntent['phase']; previous_request_id: string | null };
const phases = new Set(['prepared', 'submitted', 'unknown', 'pending', 'confirmed', 'rejected', 'rejected_confirmed']);
const intent = (row: Row): DeletionIntent => {
  if (!Number.isSafeInteger(row.user_id) || row.user_id <= 0 || !row.request_id || !phases.has(row.phase)) throw Error('invalid-request-record');
  return { ownerId: row.user_id, requestId: row.request_id, phase: row.phase, ...(row.previous_request_id ? { previousRequestId: row.previous_request_id } : {}) };
};
let opened: Promise<DeletionStore> | null = null;
export function openAccountRequestStore(): Promise<DeletionStore> {
  if (!opened) opened = SQLite.openDatabaseAsync('auren-owners-v1.db').then(createAccountRequestStore).catch((e) => { opened = null; throw e; });
  return opened;
}
export async function createAccountRequestStore(db: DB): Promise<DeletionStore> {
  await db.execAsync(`PRAGMA journal_mode = WAL; PRAGMA busy_timeout = 2000;
    CREATE TABLE IF NOT EXISTS account_request_intents (
      user_id INTEGER PRIMARY KEY NOT NULL, request_id TEXT UNIQUE NOT NULL, phase TEXT NOT NULL, previous_request_id TEXT);
    CREATE TABLE IF NOT EXISTS owner_retirements (user_id INTEGER PRIMARY KEY NOT NULL, request_id TEXT NOT NULL);`);
  const serial = createSerialQueue();
  const read = async (id: number, source: SqlPort = db) => {
    const row = await source.getFirstAsync<Row>('SELECT user_id,request_id,phase,previous_request_id FROM account_request_intents WHERE user_id = ?', id);
    return row ? intent(row) : null;
  };
  const write = <T>(current: () => boolean, action: (tx: SqlPort) => Promise<T>) => serial(async () => {
    let result!: T;
    await db.withExclusiveTransactionAsync(async (tx) => {
      if (!current()) throw new ApiFailure('http', 401, 'stale_identity');
      result = await action(tx);
      if (!current()) throw new ApiFailure('http', 401, 'stale_identity');
    }); return result;
  });
  const active = async (id: number, tx: SqlPort) => {
    if (await tx.getFirstAsync('SELECT user_id FROM owner_retirements WHERE user_id = ?', id)) throw Error('retired-owner');
  };
  return {
    read,
    reserve: (id, key, current) => write(current, async (tx) => {
      if (!Number.isSafeInteger(id) || id <= 0 || !key.trim() || key.length > 128) throw Error('invalid-request');
      await active(id, tx);
      await tx.runAsync('INSERT OR IGNORE INTO account_request_intents(user_id,request_id,phase) VALUES (?,?,?)', id, key, 'prepared');
      const row = await read(id, tx); if (!row) throw Error('request-conflict'); return row;
    }),
    renewRejected: (prior, key, current) => write(current, async (tx) => {
      await active(prior.ownerId, tx);
      const old = await read(prior.ownerId, tx);
      if (!old || old.requestId !== prior.requestId || old.phase !== 'rejected_confirmed'
        || !key.trim() || key.length > 128 || key === old.requestId) return null;
      await tx.runAsync('UPDATE account_request_intents SET request_id = ?, previous_request_id = ?, phase = ? WHERE user_id = ? AND request_id = ?', key, old.requestId, 'prepared', old.ownerId, old.requestId);
      return read(prior.ownerId, tx);
    }),
    claim: (row, current) => write(current, async (tx) => {
      await active(row.ownerId, tx);
      const saved = await read(row.ownerId, tx);
      if (!saved || saved.requestId !== row.requestId || saved.phase !== 'prepared') return false;
      await tx.runAsync('UPDATE account_request_intents SET phase = ? WHERE user_id = ? AND request_id = ? AND phase = ?', 'submitted', row.ownerId, row.requestId, 'prepared');
      return true;
    }),
    write: (row, current) => write(current, async (tx) => {
      if (!phases.has(row.phase)) throw Error('invalid-request-phase');
      const saved = await read(row.ownerId, tx);
      if (!saved || saved.requestId !== row.requestId) throw Error('request-conflict');
      if (['confirmed','rejected_confirmed'].includes(saved.phase) && row.phase !== saved.phase) throw Error('terminal-request-state');
      await tx.runAsync('UPDATE account_request_intents SET phase = ? WHERE user_id = ? AND request_id = ?', row.phase, row.ownerId, row.requestId);
    }),
    retire: (row, current) => write(current, async (tx) => {
      const saved = await read(row.ownerId, tx);
      if (!saved || saved.requestId !== row.requestId || saved.phase !== 'confirmed') throw Error('unconfirmed-erasure');
      await tx.runAsync('INSERT OR IGNORE INTO owner_retirements(user_id,request_id) VALUES (?,?)', row.ownerId, row.requestId);
    }),
  };
}
