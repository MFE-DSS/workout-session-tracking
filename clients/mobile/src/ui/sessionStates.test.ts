import React, { act } from 'react';
import { createRoot, Root, TestInstance } from 'test-renderer';
import { ResumeScreen } from './ResumeScreen';
import { CompleteScreen } from './CompleteScreen';
import rawFixture from '../fixtures/lab_fixture.json';
import type { LabFixture } from '../domain/types';
import { initialState, reduce } from '../domain/workout';
import { sessionPerformance } from '../domain/performance';

jest.mock('react-native-safe-area-context', () => ({
  useSafeAreaFrame: () => ({ width: 390, height: 844 }),
  useSafeAreaInsets: () => ({ top: 0, bottom: 0, left: 0, right: 0 }),
}));

jest.mock('./bodymap/BodyMapTriptych', () => ({ SessionBodyMap: () => null }));

let root: Root;
beforeEach(() => { jest.useFakeTimers(); root = createRoot(); });
afterEach(async () => { await act(async () => root.unmount()); jest.clearAllTimers(); jest.useRealTimers(); });
const text = (n: TestInstance | string): string => typeof n === 'string' ? n : n.children.map(text).join(' ');

async function render(setsDone: number, busy = false) {
  await act(async () => root.render(React.createElement(ResumeScreen, {
    name: 'Push A', subtitle: null, position: { exerciseIndex: 1, exerciseTotal: 3,
      setsDone, setsTotal: 9, exerciseName: 'Développé' }, note: null, busy,
    onResume: () => undefined, onOpenJournal: () => undefined,
  })));
}

test.each([[1, '1 série faite sur 9'], [2, '2 séries faites sur 9']])('la reprise rend le nombre %s correctement', async (count, expected) => {
  await render(Number(count));
  expect(text(root.container)).toContain(expected);
});

test('la vraie action Reprendre est désactivée et annonce son attente', async () => {
  await render(1, true);
  const button = root.container.queryAll((n) => n.props.testID === 'resume');
  expect(button).toHaveLength(1);
  expect(button[0].props.accessibilityState).toMatchObject({ busy: true, disabled: true });
  expect(text(root.container)).toContain('Reprise…');
});

async function renderBilan(sessionsPerWeek: number | null, options: { appliedReplacement?: boolean; pendingReplacement?: boolean; contextLine?: string | null } = {}) {
  const original = (rawFixture as unknown as LabFixture).plans['push-a'];
  const plan = { ...original, exercises: original.exercises.map((e, index) => options.appliedReplacement && index === 0
    ? { ...e, executed_name: 'Remplacement confirmé' } : e) };
  const started = reduce(initialState, { type: 'START', plan, nowMs: Date.now() - 60_000 });
  let state = reduce(started, { type: 'FINISH_NOW', nowMs: Date.now() });
  if (options.pendingReplacement) state = { ...state, requiresSync: { [plan.exercises[0].se_id]: { substitute: 'Demande non confirmée' } } };
  await act(async () => root.render(React.createElement(CompleteScreen, {
    state, performance: sessionPerformance(plan, state.done, state.requiresSync),
    history: [], sessionsPerWeek, contextLine: options.contextLine, next: null, reducedMotion: true,
    onClose: () => undefined, onOpenLab: () => undefined,
  })));
}

test('le vrai bilan omet le programme si la fréquence n’est pas déclarée', async () => {
  await renderBilan(null);
  expect(text(root.container)).not.toContain('Ton programme');
  expect(text(root.container)).not.toContain('par défaut');
});

test('le vrai bilan conserve le programme lorsque fréquence et historique sont sourcés', async () => {
  await renderBilan(3);
  expect(text(root.container)).toContain('Ton programme');
  expect(text(root.container)).toContain('séances prévues cette semaine');
  expect(text(root.container)).not.toContain('par défaut');
});

test('le bloc actuel compte les remplacements réellement présents dans le plan canonique', async () => {
  await renderBilan(null, { appliedReplacement: true });
  expect(root.container.queryAll((n) => n.props.accessibilityLabel === 'Remplacements : 1')).toHaveLength(1);
});

test('une demande non confirmée ne devient pas un remplacement effectué dans le bilan', async () => {
  await renderBilan(null, { pendingReplacement: true });
  expect(root.container.queryAll((n) => n.props.accessibilityLabel === 'Remplacements : 0')).toHaveLength(1);
});

test('le vrai bilan affiche le contexte serveur sourcé après le bloc existant, sans carte supplémentaire', async () => {
  const line = 'Du 02/11/2026 à 00:00 au 04/11/2026 à 10:00 UTC : 2 séances terminées dans l’historique AUREN.';
  await renderBilan(null, { contextLine: line });
  const output = text(root.container);
  expect(output).toContain(line);
  expect(output.indexOf(line)).toBeGreaterThan(output.indexOf('Remplacements'));
  expect(output.indexOf(line)).toBeLessThan(output.lastIndexOf('Fermer'));
  expect(output).not.toContain('Ton programme');
});
