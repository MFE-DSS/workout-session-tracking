import rawFixture from '../fixtures/lab_fixture.json';
import type { LabFixture } from '../domain/types';
import { initialState, reduce } from '../domain/workout';
import type { OutboxRow } from '../storage/outbox';
import { reconcileSubstitutions, substitutionStates } from './substitutionState';

const plan = (rawFixture as unknown as LabFixture).plans['push-a'];
const id = plan.exercises[0].se_id;
const pending = reduce(reduce(initialState, { type: 'START', plan, nowMs: 1 }),
  { type: 'REQUEST_SUBSTITUTE', seId: id, substitute: 'Proposé' });
function command(state: OutboxRow['state'], time = 1, name = 'Proposé'): OutboxRow {
  return { op_id: `op-${time}`, kind: 'SUBSTITUTE', target: `exercise/${id}`,
    payload: JSON.stringify({ session_id: plan.session_id, se_id: id, name }),
    created_at_ms: time, attempts: 1, state };
}

test('un ancien refus ne supprime pas une demande plus récente', () => {
  expect(reconcileSubstitutions(pending, [command('pending', 20), command('failed', 10)])).toBe(pending);
});

test('un accusé sans le plan confirmé ne libère pas la validation', () => {
  expect(reconcileSubstitutions(pending, [command('acked')])).toBe(pending);
});

test('le refus libère la demande sans changer le plan d’origine', () => {
  const state = reconcileSubstitutions(pending, [command('failed')]);
  expect(state.requiresSync).toEqual({});
  expect(state.plan).toBe(plan);
});

test('le plan confirmé et son accusé libèrent la demande', () => {
  const confirmed = { ...pending, plan: { ...plan,
    exercises: plan.exercises.map((e) => e.se_id === id ? { ...e, executed_name: 'Proposé' } : e) } };
  expect(reconcileSubstitutions(confirmed, [command('acked')]).requiresSync).toEqual({});
});

test('une autre séance ou une ligne corrompue ne peut résoudre la demande active', () => {
  const rows = [
    { ...command('failed'), payload: JSON.stringify({ session_id: plan.session_id + 1, se_id: id, name: 'Proposé' }) },
    { ...command('failed'), payload: '{' },
    { ...command('failed'), payload: 'null' },
    { ...command('failed'), target: 'exercise/other' },
  ];
  expect(substitutionStates(rows, plan.session_id)).toEqual({});
  expect(reconcileSubstitutions(pending, rows)).toBe(pending);
});
