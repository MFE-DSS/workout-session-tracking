import { ApiFailure } from '../api/http';
import type { OwnershipBook } from './ownership';
/** Preview memory only. Native ownership/relaunch acceptance uses SQLite, never this adapter. */
export const retiredOwners = new Set<number>();
const devices = new Map<string, number>();
const journals = new Map<number, string>();
let legacy: number | null = null;
const book: OwnershipBook = {
  isRetiredOwner: async (id) => retiredOwners.has(id),
  ownerOfDevice: async (device) => devices.get(device) ?? null,
  journalOf: async (id) => journals.get(id) ?? null,
  legacyOwner: async () => legacy,
  bindDevice: async (device, id, current = () => true) => { if (retiredOwners.has(id)) throw Error('retired-owner'); if (!current()) throw new ApiFailure('http', 401, 'stale_identity'); devices.set(device, id); },
  assignJournal: async (id, name, current = () => true) => {
    if (retiredOwners.has(id)) throw Error('retired-owner'); if (!current()) throw new ApiFailure('http', 401, 'stale_identity');
    if (journals.has(id) && journals.get(id) !== name) throw Error('journal-owner-conflict');
    journals.set(id, name);
  },
  claimLegacy: async (id, current = () => true) => {
    if (retiredOwners.has(id)) throw Error('retired-owner'); if (!current()) throw new ApiFailure('http', 401, 'stale_identity');
    if (legacy !== null && legacy !== id) return false;
    legacy = id; journals.set(id, 'auren.db'); return true;
  },
};
export async function openOwnershipBook(): Promise<OwnershipBook> { return book; }
