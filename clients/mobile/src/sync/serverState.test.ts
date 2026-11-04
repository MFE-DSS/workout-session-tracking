import type { OutboxRow } from '../storage/outbox';
import { serverStateFromOutbox } from './serverState';

const row = (id: number, state: OutboxRow['state'], time = 1): OutboxRow => ({
  op_id: `op-${id}-${time}`, kind: 'SET_COMPLETION', target: `set/${id}`, payload: '{}',
  created_at_ms: time, attempts: 1, state,
});

test('les accusés persistés restent reçus après une relance, les refus restent à vérifier', () => {
  expect(serverStateFromOutbox([row(11, 'acked'), row(12, 'failed'), row(13, 'pending'), row(14, 'inflight')]))
    .toEqual({ 11: 'synced', 12: 'refused', 13: 'pending', 14: 'pending' });
});

test('un nouvel envoi en attente ne reprend pas le faux accusé d’une ancienne commande', () => {
  expect(serverStateFromOutbox([row(11, 'pending', 20), row(11, 'acked', 10)]))
    .toEqual({ 11: 'pending' });
});

test('une correction acquittée remplace un ancien refus, indépendamment de l’ordre des lignes', () => {
  expect(serverStateFromOutbox([row(11, 'acked', 30), row(11, 'failed', 10)]))
    .toEqual({ 11: 'synced' });
});

test('une commande de séance ou une cible malformée ne crée pas un état de série', () => {
  expect(serverStateFromOutbox([
    { ...row(11, 'acked'), kind: 'SESSION_FINISH' },
    { ...row(12, 'failed'), target: 'set/no-id' },
    { ...row(13, 'acked'), target: 'set/-1' },
  ])).toEqual({});
});
