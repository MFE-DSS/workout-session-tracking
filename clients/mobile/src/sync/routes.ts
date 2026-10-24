/**
 * D9 — which server command an outbox row becomes. Pure, so the mapping is
 * tested without a network: a wrong route here would silently lose facts.
 */
import type { OutboxRow } from '../storage/outbox';

export type Route = { method: 'PUT' | 'POST'; path: string; body: Record<string, unknown> };

export function routeFor(row: OutboxRow): Route {
  const p = JSON.parse(row.payload) as Record<string, unknown>;
  const sid = Number(p.session_id);
  switch (row.kind) {
    case 'SET_COMPLETION':
      return {
        method: 'PUT',
        path: `/sessions/${sid}/sets/${Number(p.set_id)}`,
        body: {
          op_id: row.op_id,
          weight_kg: p.weight_kg,
          reps: p.reps,
          performed_at: p.performed_at,
          performed_at_estimated: p.performed_at_estimated,
        },
      };
    case 'SESSION_FINISH':
      return { method: 'POST', path: `/sessions/${sid}/finish`, body: { op_id: row.op_id, at: p.at } };
    case 'SESSION_ABANDON':
      return { method: 'POST', path: `/sessions/${sid}/abandon`, body: { op_id: row.op_id, at: p.at } };
    case 'SUBSTITUTE':
      return {
        method: 'POST',
        path: `/sessions/${sid}/exercises/${Number(p.se_id)}/substitute`,
        body: { op_id: row.op_id, name: p.name },
      };
    default:
      throw new Error(`unknown outbox command ${row.kind}`);
  }
}
