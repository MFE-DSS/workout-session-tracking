/** Web review is memory-only. Native intent durability uses SQLite, not this adapter. */
import type { DeletionIntent, DeletionStore } from '../api/accountDeletion';
import { retiredOwners } from './ownershipStore.web';
const rows = new Map<number, DeletionIntent>();
const check = (current: () => boolean) => { if (!current()) throw Error('stale-identity'); };
const saved = (row: DeletionIntent) => {
  const value = rows.get(row.ownerId);
  if (!value || value.requestId !== row.requestId) throw Error('request-conflict');
  return value;
};
const store: DeletionStore = {
  read: async (id) => rows.has(id) ? { ...rows.get(id)! } : null,
  reserve: async (id, key, current) => {
    check(current);
    if (retiredOwners.has(id)) throw Error('retired-owner');
    if (!rows.has(id)) rows.set(id, { ownerId: id, requestId: key, phase: 'prepared' });
    return { ...rows.get(id)! };
  },
  renewRejected: async (old, key, current) => {
    check(current); const value = saved(old);
    if (retiredOwners.has(old.ownerId) || value.phase !== 'rejected_confirmed'
      || !key.trim() || key.length > 128 || key === old.requestId) return null;
    const next: DeletionIntent = { ownerId:old.ownerId,requestId:key,previousRequestId:old.requestId,phase:'prepared' };
    rows.set(old.ownerId,next); return {...next};
  },
  claim: async (row, current) => {
    check(current); const value = saved(row);
    if (retiredOwners.has(row.ownerId) || value.phase !== 'prepared') return false;
    rows.set(row.ownerId, { ...value, phase: 'submitted' }); return true;
  },
  write: async (row, current) => { check(current); const prior=saved(row);
    if (['confirmed','rejected_confirmed'].includes(prior.phase) && row.phase!==prior.phase) throw Error('terminal-request-state');
    rows.set(row.ownerId, { ...row }); },
  retire: async (row, current) => {
    check(current); if (saved(row).phase !== 'confirmed') throw Error('unconfirmed-erasure');
    retiredOwners.add(row.ownerId);
  },
};
export async function openAccountRequestStore(): Promise<DeletionStore> { return store; }
