/** Inspect only: never initialize the legacy schema or reset inflight commands before ownership. */
import * as SQLite from 'expo-sqlite';
import type { WorkoutState } from '../domain/workout';
import type { Restored } from './journalTypes';
import type { JournalRow, OutboxRow } from './outbox';

export async function inspectLegacyJournal(): Promise<Restored> {
  const db = await SQLite.openDatabaseAsync('auren.db', { useNewConnection: true });
  try {
    await db.execAsync('PRAGMA query_only = ON');
    const tables = await db.getAllAsync<{ name: string }>("SELECT name FROM sqlite_master WHERE type = 'table'");
    if (tables.length === 0) return { snapshot: null, sets: [], outbox: [] };
    if (!['active_session', 'journal_sets', 'outbox'].every((name) => tables.some((t) => t.name === name))) throw Error('legacy-schema');
    const row = await db.getFirstAsync<{ snapshot: string }>('SELECT snapshot FROM active_session WHERE id = 1');
    const sets = await db.getAllAsync<JournalRow>('SELECT * FROM journal_sets ORDER BY created_at_ms');
    const outbox = await db.getAllAsync<OutboxRow>('SELECT * FROM outbox ORDER BY created_at_ms, rowid');
    return { snapshot: row ? JSON.parse(row.snapshot) as WorkoutState : null, sets, outbox };
  } finally {
    await db.closeAsync();
  }
}
