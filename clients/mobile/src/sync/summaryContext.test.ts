import { summaryContext } from './summaryContext';
import type { SessionHistoryRead } from '../api/types';

const current = { id: 1, template_slug: 'push-a', started_at: '2026-11-04T09:00:00Z', ended_at: '2026-11-04T10:00:00Z' };
const history = (sessions = [current], has_more = false): SessionHistoryRead => ({ sessions, has_more });

test('la période UTC exclut la semaine précédente et les séances postérieures à la borne attestée', () => {
  expect(summaryContext(history([current,
    { ...current, id: 2, ended_at: '2026-11-01T23:59:59Z', started_at: '2026-11-01T23:00:00Z' },
    { ...current, id: 3, ended_at: '2026-11-04T11:00:00Z' },
  ]), 1)).toBe('Du 02/11/2026 à 00:00 au 04/11/2026 à 10:00 UTC : 1 séance terminée dans l’historique AUREN.');
});

test.each([
  ['page tronquée', history([current], true)],
  ['séance courante absente', history([])],
  ['identifiant dupliqué', history([current, current])],
  ['date de fin invalide', history([{ ...current, ended_at: 'inconnue' }])],
  ['date de début invalide', history([{ ...current, started_at: 'inconnue' }])],
  ['période inversée', history([{ ...current, ended_at: '2026-11-04T08:00:00Z' }])],
])('omet la ligne lorsque les données sont incomplètes : %s', (_, value) => {
  expect(summaryContext(value, 1)).toBeNull();
});

test('la semaine peut traverser une année sans masquer l’année de chaque borne', () => {
  expect(summaryContext(history([{ ...current, started_at: '2027-01-01T09:00:00Z', ended_at: '2027-01-01T10:00:00Z' }]), 1))
    .toContain('Du 28/12/2026 à 00:00 au 01/01/2027 à 10:00 UTC');
});
