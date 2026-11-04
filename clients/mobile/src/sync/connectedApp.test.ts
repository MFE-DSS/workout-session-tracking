import React, { act } from 'react';
import { createRoot, Root, TestInstance } from 'test-renderer';

import rawFixture from '../fixtures/lab_fixture.json';
import type { LabFixture } from '../domain/types';
import { initialState, reduce } from '../domain/workout';
import { openJournal as openMemoryJournal } from '../storage/journal.web';
import type { Journal } from '../storage/journalTypes';
import { setCommand, substituteCommand } from '../storage/outbox';
import { ApiFailure } from '../api/http';
import { SyncEngine } from './syncEngine';
import type { Restored } from '../storage/journalTypes';

// Réseau et SQLite sont les frontières externes ; AuthSession, SyncEngine et le reducer restent réels.
const mockTransport = jest.fn();
let mockJournal: Journal;
jest.mock('../api/http', () => ({ ...jest.requireActual('../api/http'), createTransport: () => mockTransport }));
jest.mock('../storage/journal', () => ({ openJournal: () => Promise.resolve(mockJournal) }));
jest.mock('../auth/credentialStore', () => ({ credentialStore: {
  read: async () => 'test-refresh', write: async () => undefined, clear: async () => undefined,
} }));
let mockOperationSequence = 0;
jest.mock('expo-crypto', () => ({ randomUUID: () => `test-op-${++mockOperationSequence}` }));
jest.mock('../shell/routeContext', () => ({ shellRoutes: {} }));
jest.mock('expo-router', () => ({ ExpoRoot: () => require('../shell/ShellContext').useShell().today }));
jest.mock('react-native-safe-area-context', () => ({
  useSafeAreaInsets: () => ({ top: 47, bottom: 34, left: 0, right: 0 }),
  useSafeAreaFrame: () => ({ width: 390, height: 844 }),
  SafeAreaProvider: ({ children }: { children: React.ReactNode }) => children,
}));
jest.mock('../native/motion', () => ({ useReducedMotion: () => true, announce: () => undefined }));
jest.mock('../native/keepAwake', () => ({ keepAwake: { enable: () => undefined, disable: () => undefined } }));
jest.mock('../native/restNotification', () => ({ restNotification: {
  onDelivery: () => () => undefined, cancel: async () => undefined,
  prepare: async () => false, schedule: async () => null,
} }));
jest.mock('../native/feedback', () => ({ feedback: new Proxy({}, { get: () => () => undefined }) }));
// Écrans aux frontières : on vérifie les données et callbacks réellement fournis par ConnectedApp.
jest.mock('../ui/ExecutionScreen', () => ({ ExecutionScreen: (p: object) => require('react').createElement('Execution', p) }));
jest.mock('../ui/ResumeScreen', () => ({ ResumeScreen: (p: object) => require('react').createElement('Resume', p) }));
let mockRealSummary = false;
jest.mock('../ui/CompleteScreen', () => ({ CompleteScreen: (p: object) => mockRealSummary
  ? require('react').createElement(jest.requireActual('../ui/CompleteScreen').CompleteScreen, p)
  : require('react').createElement('Complete', p) }));
jest.mock('../ui/bodymap/BodyMapTriptych', () => ({ SessionBodyMap: () => null }));
jest.mock('../ui/MissionScreen', () => ({ MissionScreen: (p: object) => require('react').createElement('Mission', p) }));
jest.mock('../ui/QuietScreen', () => ({ QuietScreen: (p: object) => require('react').createElement('Quiet', p) }));
jest.mock('../ui/LoginScreen', () => ({ LoginScreen: (p: object) => require('react').createElement('Login', p) }));
jest.mock('../ui/LabSheet', () => ({ LabSheet: () => null }));
jest.mock('../ui/components', () => ({ ...jest.requireActual('../ui/components'),
  Sheet: ({ visible, children }: { visible: boolean; children: React.ReactNode }) => visible
    ? require('react').createElement('NativeSheetBoundary', null, children) : null,
}));

const fixture = rawFixture as unknown as LabFixture;
const plan = fixture.plans['push-a'];
const first = plan.sets[0];
let ConnectedApp: React.ComponentType;
let root: Root;

beforeAll(() => { ConnectedApp = require('../../ConnectedApp').default; });

beforeEach(async () => {
  mockRealSummary = false;
  mockOperationSequence = 0;
  jest.useFakeTimers();
  mockJournal = await openMemoryJournal();
  mockTransport.mockReset().mockImplementation(async (path: string) => {
    if (path === '/auth/refresh') return {
      access_token: 'test-access', refresh_token: 'test-next-refresh', access_expires_in: 900,
      token_type: 'Bearer', server_now: new Date().toISOString(),
    };
    throw new ApiFailure('network');
  });
  root = createRoot();
});

afterEach(async () => {
  await act(async () => root?.unmount());
  jest.restoreAllMocks();
  jest.clearAllTimers();
  jest.useRealTimers();
});

async function saved(state: 'acked' | 'failed', complete = false) {
  const now = Date.now();
  let snapshot = reduce(initialState, { type: 'START', plan, nowMs: now });
  snapshot = reduce(snapshot, { type: 'VALIDATED', setId: first.set_id, nowMs: now,
    performedAt: { epochMs: now, estimated: false } });
  if (complete) snapshot = reduce(snapshot, { type: 'FINISH_NOW', nowMs: now });
  const command = setCommand('persisted-op', plan.session_id, first.set_id, 40, 8, { epochMs: now, estimated: false });
  await mockJournal.commitValidation({
    set_id: first.set_id, session_id: plan.session_id, se_id: first.se_id, weight_kg: 40, reps: 8,
    performed_at_ms: now, performed_at_estimated: 0, local_state: 'saved_local', created_at_ms: now,
  }, command, snapshot);
  await mockJournal.markOutbox(command.op_id, state, 1);
  return snapshot;
}

async function boot() { await act(async () => root.render(React.createElement(ConnectedApp))); }
function screen(type: string) {
  const nodes = root.container.queryAll((n) => n.type === type);
  expect(nodes).toHaveLength(1);
  return nodes[0].props;
}

test('une série persistée acquittée est reçue dans le vrai chemin exécution après relance hors ligne', async () => {
  await saved('acked');
  await boot();
  await act(async () => screen('Resume').onResume());
  expect(screen('Execution').serverStateOf(first.set_id)).toBe('synced');
});

test('un refus persisté est relu au démarrage même lorsque le réseau ne répond plus', async () => {
  await saved('failed');
  await boot();
  await act(async () => screen('Resume').onResume());
  expect(screen('Execution').serverStateOf(first.set_id)).toBe('refused');
});

test('le vrai bilan reçoit également les accusés restaurés', async () => {
  await saved('acked', true);
  await boot();
  expect(screen('Complete').serverStateOf(first.set_id)).toBe('synced');
});

function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (reason: unknown) => void;
  const promise = new Promise<T>((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
}

function readyMission() { return { ...fixture.mission, executable: true, decision: { top: plan.template_slug } }; }

test('deux appuis avant réponse ne créent qu’une requête et le vrai écran reçoit busy', async () => {
  const pending = deferred<unknown>();
  const fallback = mockTransport.getMockImplementation()!;
  mockTransport.mockImplementation((path: string) => {
    if (path === '/mission') return Promise.resolve(readyMission());
    if (path === '/sessions') return pending.promise;
    return fallback(path);
  });
  await boot();
  const start = screen('Mission').onStart;
  let firstCall: Promise<void>;
  let secondCall: Promise<void>;
  await act(async () => {
    firstCall = start(plan.template_slug);
    secondCall = start(plan.template_slug);
  });
  expect(mockTransport.mock.calls.filter(([path]) => path === '/sessions')).toHaveLength(1);
  expect(screen('Mission').busy).toBe(true);
  await act(async () => { pending.resolve(plan); await firstCall!; await secondCall!; });
  expect(screen('Execution').state.plan.session_id).toBe(plan.session_id);
});

test('un démarrage échoué libère le verrou et permet une nouvelle tentative', async () => {
  const fallback = mockTransport.getMockImplementation()!;
  let attempts = 0;
  mockTransport.mockImplementation(async (path: string) => {
    if (path === '/mission') return readyMission();
    if (path === '/sessions') {
      attempts += 1;
      if (attempts === 1) throw new ApiFailure('network');
      return plan;
    }
    return fallback(path);
  });
  await boot();
  await act(async () => { await screen('Mission').onStart(plan.template_slug); });
  expect(screen('Mission').busy).toBe(false);
  await act(async () => { await screen('Mission').onStart(plan.template_slug); });
  expect(attempts).toBe(2);
  expect(screen('Execution').state.plan.session_id).toBe(plan.session_id);
});

test('la marque seule reste visible tant que le refresh du jeton n’a pas répondu', async () => {
  const refresh = deferred<unknown>();
  mockTransport.mockImplementation(() => refresh.promise);
  await boot();
  expect(root.container.queryAll((n) => n.props.testID === 'auren-mark')).toHaveLength(1);
  expect(root.container.queryAll((n) => ['Quiet', 'Mission', 'Resume'].includes(n.type))).toHaveLength(0);
  await act(async () => { refresh.reject(new ApiFailure('network')); });
});

test('Reprendre depuis le serveur attend une seule lecture et explique la reprise hors ligne', async () => {
  const pending = deferred<unknown>();
  const fallback = mockTransport.getMockImplementation()!;
  let reads = 0;
  mockTransport.mockImplementation(async (path: string) => {
    if (path === '/mission') return {
      state: 'RESUME', primary_action: 'RESUME', position: null,
      session: { id: plan.session_id, name: 'Push A', subtitle: null, template_slug: plan.template_slug,
        started_at: new Date().toISOString() },
    };
    if (path === `/sessions/${plan.session_id}/execution`) {
      reads += 1;
      if (reads === 1) throw new ApiFailure('network');
      return pending.promise;
    }
    return fallback(path);
  });
  await boot();
  expect(screen('Resume').note).toMatch(/Hors ligne/);
  const resume = screen('Resume').onResume;
  await act(async () => { resume(); resume(); });
  expect(reads).toBe(2); // une lecture initiale échouée, une seule nouvelle demande
  expect(screen('Resume').busy).toBe(true);
  await act(async () => { pending.resolve({ ...plan, done: {}, status: 'in_progress',
    started_at: new Date().toISOString(), ended_at: null, cursor_set_id: first.set_id,
    excluded_from_stats: false, allowed_actions: [] }); });
  expect(screen('Execution').state.plan.session_id).toBe(plan.session_id);
});

test('un refus réessayé puis acquitté met à jour le vrai consommateur à partir du journal', async () => {
  const kick = jest.spyOn(SyncEngine.prototype, 'kick');
  await saved('failed');
  await boot();
  await act(async () => screen('Resume').onResume());
  expect(screen('Execution').serverStateOf(first.set_id)).toBe('refused');
  const engine = kick.mock.contexts[0] as SyncEngine;
  const fallback = mockTransport.getMockImplementation()!;
  mockTransport.mockImplementation((path: string) => path.includes('/sets/')
    ? Promise.resolve({ state: 'ACKNOWLEDGED', applied: true }) : fallback(path));
  await act(async () => { await engine.retry('persisted-op'); });
  expect(screen('Execution').serverStateOf(first.set_id)).toBe('synced');
  expect((await mockJournal.restore()).outbox[0].state).toBe('acked');
});

test('une ancienne lecture tardive ne remplace pas un accusé déjà relu par le vrai consommateur', async () => {
  const kick = jest.spyOn(SyncEngine.prototype, 'kick');
  await saved('acked');
  await boot();
  await act(async () => screen('Resume').onResume());
  const current = await mockJournal.restore();
  const stale = deferred<Restored>();
  jest.spyOn(mockJournal, 'restore').mockImplementationOnce(() => stale.promise).mockResolvedValue(current);
  const engine = kick.mock.contexts[0] as SyncEngine;
  await act(async () => { await engine.kick(); await engine.kick(); });
  expect(screen('Execution').serverStateOf(first.set_id)).toBe('synced');
  await act(async () => { stale.resolve({ ...current, outbox: current.outbox.map((r) => ({ ...r, state: 'failed' })) }); });
  expect(screen('Execution').serverStateOf(first.set_id)).toBe('synced');
});

function bilanReads(preferences: unknown, history: unknown, failHistory = false) {
  const fallback = mockTransport.getMockImplementation()!;
  mockTransport.mockImplementation(async (path: string) => {
    if (path === '/me/training-preferences') return preferences;
    if (path.startsWith('/me/sessions?')) {
      if (failHistory) throw new ApiFailure('network');
      return history;
    }
    return fallback(path);
  });
}

test('le vrai bilan reçoit la fréquence déclarée et l’historique serveur sans compter deux fois la séance', async () => {
  await saved('acked', true);
  bilanReads({ sessions_per_week: 3 }, { has_more: false, sessions: [
    { id: plan.session_id, template_slug: plan.template_slug, started_at: '2026-11-04T09:00:00Z', ended_at: '2026-11-04T10:00:00Z' },
    { id: plan.session_id + 1, template_slug: 'old', started_at: '2026-11-02T09:00:00Z', ended_at: '2026-11-02T10:00:00Z' },
  ] });
  await boot();
  expect(screen('Complete').sessionsPerWeek).toBe(3);
  expect(screen('Complete').history).toEqual([{ slug: 'old', atMs: Date.parse('2026-11-02T10:00:00Z') }]);
  expect(screen('Complete').contextLine).toBe('Du 02/11/2026 à 00:00 au 04/11/2026 à 10:00 UTC : 2 séances terminées dans l’historique AUREN.');
});

test('une fréquence non déclarée reste absente et un historique vide reste réellement vide', async () => {
  await saved('acked', true);
  bilanReads({}, { has_more: false, sessions: [] });
  await boot();
  expect(screen('Complete').sessionsPerWeek).toBeNull();
  expect(screen('Complete').history).toEqual([]);
  expect(screen('Complete').contextLine).toBeNull();
});

test('une lecture historique en erreur n’efface pas la préférence déclarée et ne fabrique aucun historique', async () => {
  await saved('acked', true);
  bilanReads({ sessions_per_week: 4 }, null, true);
  await boot();
  expect(screen('Complete').sessionsPerWeek).toBe(4);
  expect(screen('Complete').history).toBeNull();
  expect(screen('Complete').contextLine).toBeNull();
});

test('un historique tronqué ne permet pas de prétendre connaître les semaines tenues', async () => {
  await saved('acked', true);
  bilanReads({ sessions_per_week: 3 }, { has_more: true, sessions: [] });
  await boot();
  expect(screen('Complete').sessionsPerWeek).toBe(3);
  expect(screen('Complete').history).toBeNull();
  expect(screen('Complete').contextLine).toBeNull();
});

async function freshWorkout() {
  await mockJournal.saveSnapshot(reduce(initialState, { type: 'START', plan, nowMs: Date.now() }));
  await boot();
  await act(async () => screen('Resume').onResume());
}

const replacement = 'Remplacement proposé';

test('une substitution hors ligne reste explicite sans prétendre avoir remplacé l’exercice', async () => {
  await freshWorkout();
  await act(async () => screen('Execution').onRequestSubstitute(first.se_id, replacement));
  const shown = screen('Execution');
  expect(shown.state.plan.exercises[0].executed_name).toBe(plan.exercises[0].executed_name);
  expect(shown.state.requiresSync[first.se_id].substitute).toBe(replacement);
  expect(shown.offline).toBe(true);
  await act(async () => shown.onValidate(first.set_id));
  expect(screen('Execution').state.done[first.set_id]).toBeUndefined();
});

test('après un refus persistant, l’origine est praticable et la demande cesse d’être en attente', async () => {
  let snapshot = reduce(initialState, { type: 'START', plan, nowMs: Date.now() });
  snapshot = reduce(snapshot, { type: 'REQUEST_SUBSTITUTE', seId: first.se_id, substitute: replacement });
  const command = substituteCommand('refused-substitute', plan.session_id, first.se_id, replacement);
  await mockJournal.enqueue(command, snapshot);
  await mockJournal.markOutbox(command.op_id, 'failed', 1);
  await boot();
  await act(async () => screen('Resume').onResume());
  const shown = screen('Execution');
  expect(shown.state.requiresSync[first.se_id]).toBeUndefined();
  expect(shown.state.plan.exercises[0].executed_name).toBe(plan.exercises[0].executed_name);
  expect(shown.statusNote.text).toMatch(/remplacement.*pas.*accepté/i);
  await act(async () => shown.onValidate(first.set_id));
  expect(screen('Execution').state.done[first.set_id].local).toBe('saved_local');
});

test('une demande non persistée ne laisse pas la séance bloquée', async () => {
  await freshWorkout();
  jest.spyOn(mockJournal, 'enqueue').mockRejectedValueOnce(new Error('disk'));
  await act(async () => screen('Execution').onRequestSubstitute(first.se_id, replacement));
  expect(screen('Execution').state.requiresSync[first.se_id]).toBeUndefined();
  expect(screen('Execution').statusNote.text).toMatch(/remplacement.*enregistré/i);
});

test('un accusé de substitution restauré est réconcilié avec le vrai plan serveur', async () => {
  let snapshot = reduce(initialState, { type: 'START', plan, nowMs: Date.now() });
  snapshot = reduce(snapshot, { type: 'REQUEST_SUBSTITUTE', seId: first.se_id, substitute: replacement });
  const command = substituteCommand('accepted-substitute', plan.session_id, first.se_id, replacement);
  await mockJournal.enqueue(command, snapshot);
  await mockJournal.markOutbox(command.op_id, 'acked', 1);
  const fallback = mockTransport.getMockImplementation()!;
  mockTransport.mockImplementation((path: string) => path.endsWith('/execution')
    ? Promise.resolve({ ...plan, exercises: plan.exercises.map((e) => e.se_id === first.se_id ? { ...e, executed_name: replacement } : e),
      status: 'in_progress', done: {}, started_at: new Date().toISOString(), ended_at: null,
      cursor_set_id: first.set_id, excluded_from_stats: false, allowed_actions: [] })
    : fallback(path));
  await boot();
  await act(async () => screen('Resume').onResume());
  expect(screen('Execution').state.requiresSync[first.se_id]).toBeUndefined();
  expect(screen('Execution').state.plan.exercises[0].executed_name).toBe(replacement);
});

test('une réponse sans garantie de complétude reste inconnue pour le bilan', async () => {
  await saved('acked', true);
  bilanReads({ sessions_per_week: 3 }, { sessions: [] });
  await boot();
  expect(screen('Complete').history).toBeNull();
  expect(screen('Complete').contextLine).toBeNull();
});

function acceptedPlan() {
  return { ...plan, exercises: plan.exercises.map((e) => e.se_id === first.se_id ? { ...e, executed_name: replacement } : e),
    status: 'in_progress', done: {}, started_at: new Date().toISOString(), ended_at: null,
    cursor_set_id: first.set_id, excluded_from_stats: false, allowed_actions: [] };
}

test('une commande durable reste verrouillée si le drain échoue après son enregistrement', async () => {
  await freshWorkout();
  const kick = jest.spyOn(SyncEngine.prototype, 'kick').mockRejectedValueOnce(new Error('journal read'));
  await act(async () => screen('Execution').onRequestSubstitute(first.se_id, replacement));
  const engine = kick.mock.contexts[0] as SyncEngine;
  expect((await mockJournal.restore()).outbox.some((r) => r.kind === 'SUBSTITUTE' && r.state === 'pending')).toBe(true);
  expect(screen('Execution').state.requiresSync[first.se_id]?.substitute).toBe(replacement);
  expect(screen('Execution').statusNote.text).not.toMatch(/non enregistré/);
  await act(async () => screen('Execution').onValidate(first.set_id));
  expect(screen('Execution').state.done[first.set_id]).toBeUndefined();
  kick.mockRestore();
  const fallback = mockTransport.getMockImplementation()!;
  mockTransport.mockImplementation((path: string) => path.endsWith('/substitute')
    ? Promise.resolve({ state: 'ACKNOWLEDGED', applied: true })
    : path.endsWith('/execution') ? Promise.resolve(acceptedPlan()) : fallback(path));
  await act(async () => { await engine.kick(); });
  expect(screen('Execution').state.plan.exercises[0].executed_name).toBe(replacement);
  expect(screen('Execution').state.requiresSync[first.se_id]).toBeUndefined();
});

test('le plan d’un remplacement acquitté est relu après coupure sans exiger de quitter l’app', async () => {
  await freshWorkout();
  const delayed = deferred<unknown>();
  let reads = 0;
  const fallback = mockTransport.getMockImplementation()!;
  mockTransport.mockImplementation((path: string) => {
    if (path.endsWith('/substitute')) return Promise.resolve({ state: 'ACKNOWLEDGED', applied: true });
    if (path.endsWith('/execution')) { reads += 1; return reads === 1 ? delayed.promise : Promise.resolve(acceptedPlan()); }
    return fallback(path);
  });
  await act(async () => screen('Execution').onRequestSubstitute(first.se_id, replacement));
  expect(reads).toBe(1);
  expect((await mockJournal.restore()).outbox.find((r) => r.kind === 'SUBSTITUTE')?.state).toBe('acked');
  await act(async () => { delayed.reject(new ApiFailure('network')); });
  await act(async () => { await jest.advanceTimersByTimeAsync(1000); });
  expect(reads).toBeGreaterThan(1);
  expect(screen('Execution').state.plan.exercises[0].executed_name).toBe(replacement);
  expect(screen('Execution').state.requiresSync[first.se_id]).toBeUndefined();
});

test('la ligne factuelle ne transforme pas une préférence absente en activité déclarée', async () => {
  await saved('acked', true);
  bilanReads({}, { has_more: false, sessions: [
    { id: plan.session_id, template_slug: plan.template_slug, started_at: '2026-11-04T09:00:00Z', ended_at: '2026-11-04T10:00:00Z' },
  ] });
  await boot();
  expect(screen('Complete').sessionsPerWeek).toBeNull();
  expect(screen('Complete').contextLine).toBe('Du 02/11/2026 à 00:00 au 04/11/2026 à 10:00 UTC : 1 séance terminée dans l’historique AUREN.');
});

const renderedText = (n: TestInstance | string): string => typeof n === 'string' ? n : n.children.map(renderedText).join(' ');
async function openRealSummaryDetails() {
  const button = root.container.queryAll((n) => n.props.accessibilityRole === 'button' && n.props.accessibilityLabel === 'Détails des séries');
  expect(button).toHaveLength(1);
  // RN Pressability exposes accessibility clicks on the actual host, not an onPress prop.
  await act(async () => button[0].props.onClick({ nativeEvent: {} }));
}

test.each([
  ['acked', 'Reçue par AUREN'],
  ['pending', 'En attente d’envoi ou de confirmation'],
  ['inflight', 'En attente d’envoi ou de confirmation'],
  ['failed', 'À vérifier — refusée par AUREN'],
] as const)('le vrai bilan expose après relance une série persistée %s', async (status, expected) => {
  mockRealSummary = true;
  await saved('acked', true);
  await mockJournal.markOutbox('persisted-op', status, 1);
  await boot();
  expect(renderedText(root.container)).not.toContain(expected);
  await openRealSummaryDetails();
  expect(renderedText(root.container)).toContain(expected);
  if (status !== 'acked') expect(renderedText(root.container)).not.toContain('Reçue par AUREN');
});

test('le vrai bilan ne déduit aucune confirmation d’une série locale sans commande vérifiable', async () => {
  mockRealSummary = true;
  const snapshot = await saved('acked', true);
  await mockJournal.reset();
  await mockJournal.saveSnapshot(snapshot);
  await boot();
  await openRealSummaryDetails();
  expect(renderedText(root.container)).toContain('État serveur inconnu');
  expect(renderedText(root.container)).not.toContain('Reçue par AUREN');
});

test('le vrai bilan remplace le refus par le retry confirmé sans doubler la série', async () => {
  mockRealSummary = true;
  const kick = jest.spyOn(SyncEngine.prototype, 'kick');
  await saved('failed', true);
  await boot();
  await openRealSummaryDetails();
  expect(renderedText(root.container)).toContain('À vérifier — refusée par AUREN');
  const engine = kick.mock.contexts[0] as SyncEngine;
  const fallback = mockTransport.getMockImplementation()!;
  mockTransport.mockImplementation((path: string) => path.includes('/sets/')
    ? Promise.resolve({ state: 'ACKNOWLEDGED', applied: false }) : fallback(path));
  await act(async () => { await engine.retry('persisted-op'); });
  expect(renderedText(root.container)).not.toContain('À vérifier — refusée par AUREN');
  expect(root.container.queryAll((n) => n.type === 'Text' && n.children.includes('Reçue par AUREN'))).toHaveLength(1);
});

test('le vrai bilan ne réutilise pas un ancien ACK pour une commande plus récente en attente', async () => {
  mockRealSummary = true;
  const snapshot = await saved('acked', true);
  jest.setSystemTime(Date.now() + 10);
  const newer = setCommand('newer-op', plan.session_id, first.set_id, 42, 9, { epochMs: Date.now(), estimated: false });
  await mockJournal.enqueue(newer, snapshot);
  await mockJournal.enqueue(newer, snapshot);
  await boot();
  await openRealSummaryDetails();
  expect(renderedText(root.container)).toContain('En attente d’envoi ou de confirmation');
  expect(renderedText(root.container)).not.toContain('Reçue par AUREN');
  expect(root.container.queryAll((n) => n.type === 'Text' && n.children.includes('Série 1'))).toHaveLength(1);
});

test('une ancienne lecture tardive ne recrée pas une confirmation du bilan après une source indisponible', async () => {
  mockRealSummary = true;
  const kick = jest.spyOn(SyncEngine.prototype, 'kick');
  await saved('acked', true);
  await boot();
  await openRealSummaryDetails();
  expect(renderedText(root.container)).toContain('Reçue par AUREN');
  const previous = await mockJournal.restore();
  const stale = deferred<Restored>();
  const read = jest.spyOn(mockJournal, 'restore').mockImplementationOnce(() => stale.promise)
    .mockRejectedValue(new Error('journal temporarily unavailable'));
  const engine = kick.mock.contexts[0] as SyncEngine;
  await act(async () => { await engine.kick(); await engine.kick(); });
  expect(renderedText(root.container)).toContain('État serveur inconnu');
  expect(renderedText(root.container)).not.toContain('Reçue par AUREN');
  await act(async () => { stale.resolve(previous); });
  expect(renderedText(root.container)).toContain('État serveur inconnu');
  read.mockRestore();
  await act(async () => { await engine.kick(); });
  expect(renderedText(root.container)).toContain('Reçue par AUREN');
});

test('le détail du bilan n’ajoute pas une série absente de la séance réalisée', async () => {
  mockRealSummary = true;
  const snapshot = await saved('acked', true);
  const other = plan.sets.find((set) => set.set_id !== first.set_id)!;
  const command = setCommand('other-op', plan.session_id, other.set_id, 40, 8, { epochMs: Date.now(), estimated: false });
  await mockJournal.enqueue(command, snapshot);
  await mockJournal.markOutbox(command.op_id, 'acked', 1);
  await boot();
  await openRealSummaryDetails();
  expect(root.container.queryAll((n) => n.type === 'Text' && n.children.includes('Reçue par AUREN'))).toHaveLength(1);
});

test('un ancien refus lu avant une nouvelle demande identique ne retire pas son verrou ni sa lecture canonique', async () => {
  const kick = jest.spyOn(SyncEngine.prototype, 'kick');
  await freshWorkout();
  const exercise = plan.exercises[0];
  const name = exercise.substitutes[0];
  const old = substituteCommand('old-refused', plan.session_id, exercise.se_id, name);
  await mockJournal.enqueue(old, screen('Execution').state);
  await mockJournal.markOutbox(old.op_id, 'failed', 1);
  const previous = await mockJournal.restore();
  const stale = deferred<Restored>();
  const actualRestore = mockJournal.restore.bind(mockJournal);
  jest.spyOn(mockJournal, 'restore').mockImplementationOnce(() => stale.promise).mockImplementation(actualRestore);
  const write = deferred<void>();
  const actualEnqueue = mockJournal.enqueue.bind(mockJournal);
  jest.spyOn(mockJournal, 'enqueue').mockImplementationOnce(async (command, snapshot) => {
    await write.promise;
    await actualEnqueue(command, snapshot);
  });
  const engine = kick.mock.contexts[0] as SyncEngine;
  await act(async () => { await engine.kick(); });
  await act(async () => screen('Execution').onRequestSubstitute(exercise.se_id, name));
  await act(async () => { stale.resolve(previous); });
  expect(screen('Execution').state.requiresSync[exercise.se_id]).toEqual({ substitute: name });
  const updated = { ...acceptedPlan(), exercises: plan.exercises.map((e) => e.se_id === exercise.se_id ? { ...e, executed_name: name } : e) };
  const fallback = mockTransport.getMockImplementation()!;
  mockTransport.mockImplementation(async (path: string) => {
    if (path.endsWith('/substitute')) return { state: 'ACKNOWLEDGED', applied: true };
    if (path.endsWith('/execution')) return updated;
    return fallback(path);
  });
  await act(async () => { write.resolve(); });
  expect(screen('Execution').state.plan.exercises[0].executed_name).toBe(name);
  expect(screen('Execution').state.requiresSync[exercise.se_id]).toBeUndefined();
});
