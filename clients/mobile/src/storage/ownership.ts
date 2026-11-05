import { ApiFailure } from '../api/http';
import { isRestorableSnapshot } from './snapshotShape';
import type { Restored } from './journalTypes';
export type OwnershipBook = {
  ownerOfDevice(device: string): Promise<number | null>;
  journalOf(userId: number): Promise<string | null>;
  legacyOwner(): Promise<number | null>;
  claimLegacy(userId: number, isCurrent?: () => boolean): Promise<boolean>;
  assignJournal(userId: number, name: string, isCurrent?: () => boolean): Promise<void>;
  bindDevice(device: string, userId: number, isCurrent?: () => boolean): Promise<void>;
};
export type OwnershipRequest = {
  book: OwnershipBook; deviceId: string | null; online: boolean;
  isCurrent?: () => boolean;
  identity(): Promise<{ id: number; username: string }>;
  inspectLegacy(): Promise<Restored>;
  verifySession(id: number): Promise<{ session_id: number }>;
};
export type OwnedJournal = { state: 'ready'; userId: number; name: string; quarantined: boolean } | { state: 'needs-connection' };

function validId(value: unknown): value is number { return Number.isSafeInteger(value) && (value as number) > 0; }
function sessionIds(restored: Restored): number[] {
  if (restored.snapshot !== null && !isRestorableSnapshot(restored.snapshot)) throw Error('unresolved-snapshot');
  const ids = new Set<number>();
  const add = (value: unknown) => { if (!validId(value)) throw Error('unresolved-session'); ids.add(value); };
  if (restored.snapshot?.plan) add(restored.snapshot.plan.session_id);
  else if (restored.snapshot && restored.snapshot.phase !== 'MISSION') throw Error('unresolved-snapshot');
  for (const row of restored.sets) add(row.session_id);
  for (const row of restored.outbox) add(JSON.parse(row.payload).session_id);
  return [...ids];
}

export async function resolveJournal(r: OwnershipRequest): Promise<OwnedJournal> {
  const isCurrent = r.isCurrent ?? (() => true);
  const check = () => { if (!isCurrent()) throw new ApiFailure('http', 401, 'stale_identity'); };
  const step = async <T>(fn: () => Promise<T>): Promise<T> => { check(); const result = await fn(); check(); return result; };
  check();
  const cachedId = r.deviceId ? await step(() => r.book.ownerOfDevice(r.deviceId!)) : null;
  const offline = async (): Promise<OwnedJournal> => {
    const name = validId(cachedId) ? await step(() => r.book.journalOf(cachedId)) : null;
    return name && validId(cachedId) ? { state: 'ready', userId: cachedId, name, quarantined: false } : { state: 'needs-connection' };
  };
  if (!r.online) return offline();
  let id: number;
  try { id = (await step(r.identity)).id; }
  catch (e) {
    if (e instanceof ApiFailure && e.kind === 'network') return offline();
    throw e;
  }
  if (!validId(id) || !r.deviceId) return { state: 'needs-connection' };
  const existing = await step(() => r.book.journalOf(id));
  if (existing) {
    await step(() => r.book.bindDevice(r.deviceId!, id, isCurrent));
    return { state: 'ready', userId: id, name: existing, quarantined: false };
  }
  let quarantined = false;
  let name = `auren-user-${id}.db`;
  if (await step(() => r.book.legacyOwner()) === null) {
    try {
      const legacy = await step(r.inspectLegacy);
      const ids = sessionIds(legacy);
      if (ids.length) {
        for (const sessionId of ids) {
          const proof = await step(() => r.verifySession(sessionId));
          if (proof.session_id !== sessionId) throw Error('unresolved-proof');
        }
        if (await step(() => r.book.claimLegacy(id, isCurrent))) name = 'auren.db';
        else quarantined = true;
      }
    } catch (e) {
      if (e instanceof ApiFailure && (e.kind === 'network' || e.status >= 500 || e.status === 429)) return { state: 'needs-connection' };
      if (e instanceof ApiFailure && e.status === 401) throw e;
      quarantined = true;
    }
  }
  await step(() => r.book.assignJournal(id, name, isCurrent));
  await step(() => r.book.bindDevice(r.deviceId!, id, isCurrent));
  return { state: 'ready', userId: id, name, quarantined };
}
