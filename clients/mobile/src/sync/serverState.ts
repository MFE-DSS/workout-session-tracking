import type { OutboxRow } from '../storage/outbox';

export type ServerSetState = 'synced' | 'refused' | 'pending' | 'unknown';

/** Le journal complet est la vérité, y compris les commandes acquittées. */
export function serverStateFromOutbox(rows: readonly OutboxRow[]): Record<number, ServerSetState> {
  const states: Record<number, ServerSetState> = {};
  const latest = new Map<number, OutboxRow>();
  for (const row of rows) {
    if (row.kind !== 'SET_COMPLETION' || !/^set\/[1-9]\d*$/.test(row.target)) continue;
    const id = Number(row.target.slice(4));
    if (!Number.isSafeInteger(id)) continue;
    const previous = latest.get(id);
    if (!previous || row.created_at_ms >= previous.created_at_ms) latest.set(id, row);
  }
  for (const [id, row] of latest) {
    if (row.state === 'acked') states[id] = 'synced';
    else if (row.state === 'failed') states[id] = 'refused';
    else if (row.state === 'pending' || row.state === 'inflight') states[id] = 'pending';
    else states[id] = 'unknown';
  }
  return states;
}
