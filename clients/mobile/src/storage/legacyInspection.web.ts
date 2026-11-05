import type { Restored } from './journalTypes';
/** Web layout preview has no access to a native device journal. */
export async function inspectLegacyJournal(): Promise<Restored> { return { snapshot: null, sets: [], outbox: [] }; }
