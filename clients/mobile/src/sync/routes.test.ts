import { closeCommand, setCommand, substituteCommand } from '../storage/outbox';
import type { OutboxRow } from '../storage/outbox';
import { routeFor } from './routes';

function asRow(c: { op_id: string; kind: string; target: string; payload: unknown }): OutboxRow {
  return { op_id: c.op_id, kind: c.kind, target: c.target, payload: JSON.stringify(c.payload), created_at_ms: 1, attempts: 0, state: 'pending' };
}

test('a set command becomes the per-set PUT, never the exercise form', () => {
  const r = routeFor(asRow(setCommand('op-1', 9, 196, 42.5, 8, { epochMs: Date.UTC(2026, 9, 24, 10), estimated: false })));
  expect(r).toEqual({
    method: 'PUT',
    path: '/sessions/9/sets/196',
    body: { op_id: 'op-1', weight_kg: 42.5, reps: 8, performed_at: '2026-10-24T10:00:00.000Z', performed_at_estimated: false },
  });
});

test('finish and abandon carry the moment the user decided', () => {
  const at = Date.UTC(2026, 9, 24, 11);
  expect(routeFor(asRow(closeCommand('op-2', 'SESSION_FINISH', 9, at)))).toEqual({
    method: 'POST', path: '/sessions/9/finish', body: { op_id: 'op-2', at: '2026-10-24T11:00:00.000Z' },
  });
  expect(routeFor(asRow(closeCommand('op-3', 'SESSION_ABANDON', 9, at))).path).toBe('/sessions/9/abandon');
});

test('a substitution targets its exercise', () => {
  expect(routeFor(asRow(substituteCommand('op-4', 9, 48, 'Développé haltères')))).toEqual({
    method: 'POST', path: '/sessions/9/exercises/48/substitute', body: { op_id: 'op-4', name: 'Développé haltères' },
  });
});

test('an unknown command is refused loudly, never sent somewhere by default', () => {
  expect(() => routeFor({ ...asRow(closeCommand('op-5', 'SESSION_FINISH', 9, 0)), kind: 'DELETE_ALL' })).toThrow();
});
