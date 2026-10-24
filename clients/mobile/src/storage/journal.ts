/**
 * Expo SQLite journal + outbox (N0 §12) — native implementation.
 *
 * `withExclusiveTransactionAsync` is used deliberately: only statements run on
 * the `txn` handle belong to the transaction, so no concurrent query can slip
 * in between the set fact and its command (the non-exclusive variant allows
 * that, per the SDK 58 docs). WAL keeps commits short.
 */
import * as SQLite from 'expo-sqlite';

import type { WorkoutState } from '../domain/workout';
import type { Journal, LabKey, Metric, Restored } from './journalTypes';
import type { Command, JournalRow, OutboxRow, SetCommand } from './outbox';
import { createSerialQueue, withRetry } from './serial';

const SCHEMA = `
PRAGMA journal_mode = WAL;
PRAGMA busy_timeout = 2000;
CREATE TABLE IF NOT EXISTS journal_sets (
  set_id INTEGER PRIMARY KEY NOT NULL,
  session_id INTEGER NOT NULL,
  se_id INTEGER NOT NULL,
  weight_kg REAL NOT NULL,
  reps INTEGER NOT NULL,
  performed_at_ms INTEGER NOT NULL,
  performed_at_estimated INTEGER NOT NULL,
  local_state TEXT NOT NULL,
  created_at_ms INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS outbox (
  op_id TEXT PRIMARY KEY NOT NULL,
  kind TEXT NOT NULL,
  target TEXT NOT NULL,
  payload TEXT NOT NULL,
  created_at_ms INTEGER NOT NULL,
  attempts INTEGER NOT NULL DEFAULT 0,
  state TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS active_session (
  id INTEGER PRIMARY KEY NOT NULL CHECK (id = 1),
  snapshot TEXT NOT NULL,
  updated_at_ms INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS lab_metrics (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  value REAL NOT NULL,
  at_ms INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS lab_kv (
  key TEXT PRIMARY KEY NOT NULL,
  value TEXT NOT NULL
);`;

const UPSERT_SNAPSHOT =
  'INSERT INTO active_session (id, snapshot, updated_at_ms) VALUES (1, ?, ?) ' +
  'ON CONFLICT(id) DO UPDATE SET snapshot = excluded.snapshot, updated_at_ms = excluded.updated_at_ms';

/**
 * `name`: the lab keeps its own file; the connected app (D9) uses another, so a
 * lab command aimed at a fixture session can never reach the real server.
 */
export async function openJournal(name = 'auren-n0-lab.db'): Promise<Journal> {
  const db = await SQLite.openDatabaseAsync(name);
  await db.execAsync(SCHEMA);
  // a command caught in flight by a force-kill has an unknown outcome: send it
  // again — the server acknowledges a fact it already holds (§10)
  await db.runAsync("UPDATE outbox SET state = 'pending' WHERE state = 'inflight'");
  // every write, on any connection, goes through one queue (see serial.ts)
  const serial = createSerialQueue();

  return {
    kind: 'sqlite',

    async restore(): Promise<Restored> {
      const row = await db.getFirstAsync<{ snapshot: string }>(
        'SELECT snapshot FROM active_session WHERE id = 1',
      );
      const sets = await db.getAllAsync<JournalRow>('SELECT * FROM journal_sets ORDER BY created_at_ms');
      const outbox = await db.getAllAsync<OutboxRow>('SELECT * FROM outbox ORDER BY created_at_ms');
      return { snapshot: row ? (JSON.parse(row.snapshot) as WorkoutState) : null, sets, outbox };
    },

    commitValidation: (r: JournalRow, c: SetCommand, snapshot: WorkoutState): Promise<number> =>
      serial(() => withRetry(async () => {
        const t0 = performance.now();
        await db.withExclusiveTransactionAsync(async (txn) => {
          await txn.runAsync(
            'INSERT OR REPLACE INTO journal_sets (set_id, session_id, se_id, weight_kg, reps, ' +
              'performed_at_ms, performed_at_estimated, local_state, created_at_ms) ' +
              'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            [r.set_id, r.session_id, r.se_id, r.weight_kg, r.reps, r.performed_at_ms,
              r.performed_at_estimated, r.local_state, r.created_at_ms],
          );
          await txn.runAsync(
            // OR IGNORE: a retried commit must not fail on its own command
            'INSERT OR IGNORE INTO outbox (op_id, kind, target, payload, created_at_ms, attempts, state) ' +
              "VALUES (?, ?, ?, ?, ?, 0, 'pending')",
            [c.op_id, c.kind, c.target, JSON.stringify(c.payload), r.created_at_ms],
          );
          await txn.runAsync(UPSERT_SNAPSHOT, [JSON.stringify(snapshot), r.created_at_ms]);
        });
        return performance.now() - t0;
      })),

    saveSnapshot: (snapshot: WorkoutState): Promise<void> =>
      serial(async () => {
        await db.runAsync(UPSERT_SNAPSHOT, [JSON.stringify(snapshot), Date.now()]);
      }),

    enqueue: (c: Command, snapshot: WorkoutState): Promise<void> =>
      serial(() => withRetry(async () => {
        const now = Date.now();
        await db.withExclusiveTransactionAsync(async (txn) => {
          await txn.runAsync(
            'INSERT OR IGNORE INTO outbox (op_id, kind, target, payload, created_at_ms, attempts, state) ' +
              "VALUES (?, ?, ?, ?, ?, 0, 'pending')",
            [c.op_id, c.kind, c.target, JSON.stringify(c.payload), now],
          );
          await txn.runAsync(UPSERT_SNAPSHOT, [JSON.stringify(snapshot), now]);
        });
      })),

    async outboxRows(): Promise<OutboxRow[]> {
      return db.getAllAsync<OutboxRow>(
        "SELECT * FROM outbox WHERE state != 'acked' ORDER BY created_at_ms, rowid",
      );
    },

    markOutbox: (opId: string, state: OutboxRow['state'], attempts: number): Promise<void> =>
      serial(async () => {
        await db.runAsync('UPDATE outbox SET state = ?, attempts = ? WHERE op_id = ?', [state, attempts, opId]);
      }),

    recordMetric: (name: string, value: number): Promise<void> =>
      serial(async () => {
        await db.runAsync('INSERT INTO lab_metrics (name, value, at_ms) VALUES (?, ?, ?)', [
          name, value, Date.now(),
        ]);
      }),

    async metrics(): Promise<Metric[]> {
      return db.getAllAsync<Metric>('SELECT name, value, at_ms FROM lab_metrics ORDER BY at_ms');
    },

    async getLab<T>(key: LabKey): Promise<T | null> {
      const row = await db.getFirstAsync<{ value: string }>('SELECT value FROM lab_kv WHERE key = ?', [key]);
      return row ? (JSON.parse(row.value) as T) : null;
    },

    setLab: (key: LabKey, value: unknown): Promise<void> =>
      serial(async () => {
        await db.runAsync(
          'INSERT INTO lab_kv (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value',
          [key, JSON.stringify(value)],
        );
      }),

    reset: (): Promise<void> =>
      serial(async () => {
        await db.execAsync(
          'DELETE FROM journal_sets; DELETE FROM outbox; DELETE FROM active_session; DELETE FROM lab_metrics; DELETE FROM lab_kv;',
        );
      }),
  };
}
