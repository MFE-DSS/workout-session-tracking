import type { WorkoutState } from '../domain/workout';
import type { OutboxRow } from '../storage/outbox';

export type SubstitutionState = { opId: string; name: string; state: OutboxRow['state']; createdAt: number };

/** Commandes valides de cette séance uniquement ; un ancien refus ne résout pas une nouvelle demande. */
export function substitutionStates(rows: readonly OutboxRow[], sessionId: number | undefined): Record<number, SubstitutionState> {
  const states: Record<number, SubstitutionState> = {};
  if (sessionId === undefined) return states;
  for (const row of rows) {
    if (row.kind !== 'SUBSTITUTE') continue;
    try {
      const p = JSON.parse(row.payload) as { session_id: number; se_id: number; name: string };
      if (!p || p.session_id !== sessionId || !Number.isSafeInteger(p.se_id) || p.se_id <= 0
        || row.target !== `exercise/${p.se_id}` || typeof p.name !== 'string') continue;
      if (!states[p.se_id] || row.created_at_ms >= states[p.se_id].createdAt) {
        states[p.se_id] = { opId: row.op_id, name: p.name, state: row.state, createdAt: row.created_at_ms };
      }
    } catch { /* Une ligne illisible ne permet aucune affirmation de synchronisation. */ }
  }
  return states;
}

export function reconcileSubstitutions(state: WorkoutState, rows: readonly OutboxRow[]): WorkoutState {
  if (!state.plan) return state;
  let requests = state.requiresSync;
  for (const [key, status] of Object.entries(substitutionStates(rows, state.plan.session_id))) {
    const id = Number(key);
    if (requests[id]?.substitute !== status.name) continue;
    const exercise = state.plan.exercises.find((e) => e.se_id === id);
    if (status.state === 'failed' || (status.state === 'acked' && exercise?.executed_name === status.name)) {
      if (requests === state.requiresSync) requests = { ...requests };
      delete requests[id];
    }
  }
  return requests === state.requiresSync ? state : { ...state, requiresSync: requests };
}
