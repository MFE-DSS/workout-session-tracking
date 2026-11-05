/** Non-secret identity bindings, separate from workout facts and SecureStore credentials. */
import * as SQLite from 'expo-sqlite';
import { ApiFailure } from '../api/http';
import type { OwnershipBook } from './ownership';
import { createSerialQueue } from './serial';

let opened: Promise<OwnershipBook> | null = null;
export function openOwnershipBook(): Promise<OwnershipBook> {
  if (!opened) {
    opened = open().catch((error) => { opened = null; throw error; });
  }
  return opened;
}
async function open(): Promise<OwnershipBook> {
  const db = await SQLite.openDatabaseAsync('auren-owners-v1.db');
  await db.execAsync(`PRAGMA journal_mode = WAL;
    PRAGMA busy_timeout = 2000;
    CREATE TABLE IF NOT EXISTS owner_devices (device_id TEXT PRIMARY KEY NOT NULL, user_id INTEGER NOT NULL);
    CREATE TABLE IF NOT EXISTS owner_journals (user_id INTEGER PRIMARY KEY NOT NULL, name TEXT UNIQUE NOT NULL);
    CREATE TABLE IF NOT EXISTS legacy_owner (id INTEGER PRIMARY KEY NOT NULL CHECK(id = 1), user_id INTEGER NOT NULL);`);
  const serial = createSerialQueue();
  const write = <T>(current: () => boolean, action: (tx: SQLite.SQLiteDatabase) => Promise<T>) => serial(async () => {
    let result!: T;
    await db.withExclusiveTransactionAsync(async (tx) => {
      if (!current()) throw new ApiFailure('http', 401, 'stale_identity');
      result = await action(tx);
      // Throw inside the exclusive transaction so a late identity change rolls back metadata.
      if (!current()) throw new ApiFailure('http', 401, 'stale_identity');
    });
    return result;
  });
  return {
    ownerOfDevice: async (device) => (await db.getFirstAsync<{ user_id: number }>('SELECT user_id FROM owner_devices WHERE device_id = ?', device))?.user_id ?? null,
    journalOf: async (id) => (await db.getFirstAsync<{ name: string }>('SELECT name FROM owner_journals WHERE user_id = ?', id))?.name ?? null,
    legacyOwner: async () => (await db.getFirstAsync<{ user_id: number }>('SELECT user_id FROM legacy_owner WHERE id = 1'))?.user_id ?? null,
    bindDevice: (device, id, current = () => true) => write(current, async (tx) => {
      await tx.runAsync('INSERT INTO owner_devices(device_id,user_id) VALUES (?,?) ON CONFLICT(device_id) DO UPDATE SET user_id = excluded.user_id', device, id);
    }),
    assignJournal: (id, name, current = () => true) => write(current, async (tx) => {
      await tx.runAsync('INSERT OR IGNORE INTO owner_journals(user_id,name) VALUES (?,?)', id, name);
      const row = await tx.getFirstAsync<{ name: string }>('SELECT name FROM owner_journals WHERE user_id = ?', id);
      if (row?.name !== name) throw Error('journal-owner-conflict');
    }),
    claimLegacy: (id, current = () => true) => write(current, async (tx) => {
      await tx.runAsync('INSERT OR IGNORE INTO legacy_owner(id,user_id) VALUES (1,?)', id);
      const row = await tx.getFirstAsync<{ user_id: number }>('SELECT user_id FROM legacy_owner WHERE id = 1');
      if (row?.user_id !== id) return false;
      await tx.runAsync('INSERT OR IGNORE INTO owner_journals(user_id,name) VALUES (?,?)', id, 'auren.db');
      const mapping = await tx.getFirstAsync<{ name: string }>('SELECT name FROM owner_journals WHERE user_id = ?', id);
      if (mapping?.name !== 'auren.db') throw Error('journal-owner-conflict');
      return true;
    }),
  };
}
