import React, { act } from 'react';
import { createRoot, Root, TestInstance } from 'test-renderer';

import rawFixture from '../fixtures/lab_fixture.json';
import type { LabFixture } from '../domain/types';
import { initialState, reduce } from '../domain/workout';
import { openJournal as openMemoryJournal } from '../storage/journal.web';
import type { Journal } from '../storage/journalTypes';
import { setCommand, substituteCommand } from '../storage/outbox';
import { ApiFailure } from '../api/http';
import {firstUse as mockFirstUse,negotiatedReply} from '../../test/missionActionHarness';
import { SyncEngine } from './syncEngine';
import type { Restored } from '../storage/journalTypes';

// Réseau et SQLite sont les frontières externes ; AuthSession, SyncEngine et le reducer restent réels.
const mockTransport = jest.fn();
let mockMissionOwner=7;
let mockJournal: Journal;
let mockCredential: string | null = 'rt1.test-device.secret';
const mockOwners = new Map<string, number>();
const mockJournalNames = new Map<number, string>();
let mockLegacyOwner: number | null = 7;
const mockOpened: string[] = [];
const mockInspectLegacy = jest.fn();
jest.mock('../storage/ownershipStore', () => ({ openOwnershipBook: async () => ({
  isRetiredOwner: async () => false,
  ownerOfDevice: async (d: string) => mockOwners.get(d) ?? null,
  journalOf: async (u: number) => mockJournalNames.get(u) ?? null,
  legacyOwner: async () => mockLegacyOwner,
  claimLegacy: async (u: number) => { if (mockLegacyOwner !== null && mockLegacyOwner !== u) return false; mockLegacyOwner = u; mockJournalNames.set(u, 'auren.db'); return true; },
  assignJournal: async (u: number, n: string) => { mockJournalNames.set(u, n); },
  bindDevice: async (d: string, u: number) => { mockOwners.set(d, u); },
}) }));
jest.mock('../storage/legacyInspection', () => ({ inspectLegacyJournal: () => mockInspectLegacy() }));
jest.mock('../api/http', () => ({ ...jest.requireActual('../api/http'), createTransport: () => async(path:string,init:unknown)=>{const value=await mockTransport(path,init);if(path==='/auth/me'&&value?.id)mockMissionOwner=value.id;return value;} }));
jest.mock('../storage/journal', () => ({ openJournal: async (name: string) => {
  mockOpened.push(name);
  return name === 'auren.db' ? mockJournal : jest.requireActual('../storage/journal.web').openJournal(name);
} }));
jest.mock('../auth/credentialStore', () => ({ credentialStore: {
  read: async () => mockCredential, write: async (v: string) => { mockCredential = v; }, clear: async () => { mockCredential = null; },
} }));
let mockOperationSequence = 0;
jest.mock('expo-crypto', () => ({ randomUUID: () => `test-op-${++mockOperationSequence}` }));
jest.mock('../shell/routeContext', () => ({ shellRoutes: {} }));
let mockShellMounts = 0;
let mockProgressTab=false;
jest.mock('expo-router', () => ({ useFocusEffect:(callback:()=>void)=>require('react').useEffect(callback,[callback]), ExpoRoot: () => { require('react').useEffect(() => { mockShellMounts++; }, []); const s = require('../shell/ShellContext').useShell(); if(mockProgressTab)return require('react').createElement(require('../routes/progres').default); return require('react').createElement(require('react').Fragment, null, s.today, s.account); } }));
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
jest.mock('../ui/account/AccountForms', () => ({
  SignupScreen: (p: object) => require('react').createElement('Signup', p),
  PasswordScreen: (p: object) => require('react').createElement('Password', p),
}));
jest.mock('../ui/account/FirstUseScreen', () => ({ FirstUseScreen: (p: object) => require('react').createElement('FirstUse', p) }));
jest.mock('../ui/account/AccountPages', () => ({
  AccountResultScreen: (p: object) => require('react').createElement('AccountResult', p),
  AccountSettingsScreen: (p: object) => require('react').createElement('AccountSettings', p),
  JournalOwnershipScreen: (p: object) => require('react').createElement('JournalOwnership', p),
}));
jest.mock('../ui/LabSheet', () => ({ LabSheet: (p: object) => require('react').createElement('JournalControls', p) }));
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
  mockRealSummary = false; mockShellMounts = 0;mockMissionOwner=7;mockProgressTab=false;
  mockCredential = 'rt1.test-device.secret';
  mockOwners.clear(); mockOwners.set('test-device', 7);
  mockJournalNames.clear(); mockJournalNames.set(7, 'auren.db');
  mockLegacyOwner = 7; mockOpened.length = 0;
  mockOperationSequence = 0;
  jest.useFakeTimers();
  mockJournal = await openMemoryJournal();
  mockInspectLegacy.mockReset().mockImplementation(() => mockJournal.restore());
  mockTransport.mockReset().mockImplementation(async (path: string) => {
    if(path==='/auth/me')return{id:7,username:'Synthetic owner'};
    if (path === '/auth/refresh') return {
      access_token: 'test-access', refresh_token: 'rt1.test-device.next-secret', access_expires_in: 900,
      token_type: 'Bearer', server_now: new Date().toISOString(),
    };
    throw new ApiFailure('network');
  });
  // Compatibility testimony for the old workout-mechanics tests only. The
  // production client still negotiates/decodes its exact DTO. New MOB04 cases
  // override this RPC boundary and assert no automatic historical request.
  jest.spyOn(global,'fetch').mockImplementation(async(url,init)=>{
    const u=new URL(String(url),'http://test-only.invalid'),path=u.searchParams.get('requested_path')??'FIRST_USE';
    const host=Boolean((init?.headers as Record<string,string>)?.['X-Auren-Mission-V3-Host']);
    const m=await mockTransport('/mission'),base={...mockFirstUse(mockMissionOwner),requested_path:path,observed_at:new Date().toISOString()};
    let raw:unknown;
    if(m?.state==='RESUME')raw={...base,state:'RESUME',source:'OPEN_SESSION',primary_action:{kind:'RESUME_LEGACY',session_id:m.session.id},payload:{...m,execution_profile:'LEGACY_V1'}};
    else if(path==='FIRST_USE')raw={...base,state:'UNAVAILABLE',source:'OWNED_FIRST_USE',primary_action:{kind:'REFRESH'},payload:null,reason:'RUNTIME_NOT_SERVED'};
    else if(m?.state==='READY'&&m.executable&&m.primary_action==='START')raw={...base,state:'HISTORICAL_READY',source:'HISTORICAL_MISSION',primary_action:{kind:'START_LEGACY',template_slug:m.template.slug,decision:m.decision},payload:m};
    else if(m?.state==='NO_MISSION')raw={...base,state:'NO_MISSION',source:'NONE',primary_action:null,payload:null};
    else raw={...base,state:'UNAVAILABLE',source:'HISTORICAL_MISSION',primary_action:{kind:'REFRESH'},payload:null,reason:'HISTORICAL_NOT_EXECUTABLE'};
    return negotiatedReply(raw,200,host);
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

async function pressMissionPrimary(){
 const button=root.container.queryAll(n=>n.props.testID==='mission-action-primary')[0];expect(button).toBeDefined();
 await act(async()=>button.props.onClick({nativeEvent:{},stopPropagation(){},currentTarget:1,target:1}));
}
async function chooseHistorical(){
 const button=root.container.queryAll(n=>n.props.testID==='mission-action-other')[0];
 if(button)await act(async()=>button.props.onClick({nativeEvent:{},stopPropagation:()=>{},currentTarget:1,target:1}));
}
// Old workout cases explicitly take the secondary source after boot, as a user.
async function boot(historical=true) { await act(async () => root.render(React.createElement(ConnectedApp)));if(historical)await chooseHistorical(); }
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

function readyMission() { return { ...fixture.mission,template:{...fixture.mission.template,slug:plan.template_slug},executable:true,primary_action:'START',duration_estimate:null,
 alternatives:fixture.mission.alternatives.map(a=>({...a,executable:true})),decision:{fingerprint:null,policy:'synthetic-legacy-test',top:plan.template_slug,alternatives:fixture.mission.alternatives.map(a=>a.slug)}}; }

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
  expect(root.container.queryAll(n=>n.props.testID==='mission-action-primary')[0].props.accessibilityState.disabled).toBe(true);
  await act(async () => { pending.resolve(plan); await firstCall!; await secondCall!; });
  expect(screen('Execution').state.plan.session_id).toBe(plan.session_id);
});

test('une lecture négative ne résout pas une réponse de démarrage perdue', async () => {
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
  expect(attempts).toBe(1);
  await pressMissionPrimary();
  expect(root.container.queryAll(n=>n.type==='Mission')).toHaveLength(0);
  expect(attempts).toBe(1);expect(renderedText(root.container)).toContain('Réception à vérifier');
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
  await boot(false);
  expect(reads).toBe(0);
  await pressMissionPrimary();
  expect(renderedText(root.container)).toContain('connexion');
  const resume = root.container.queryAll(n=>n.props.testID==='mission-action-primary')[0].props.onClick;
  await act(async () => { const event={nativeEvent:{},stopPropagation(){},currentTarget:1,target:1};resume(event);resume(event); });
  expect(reads).toBe(2); // une lecture initiale échouée, une seule nouvelle demande
  expect(root.container.queryAll(n=>n.props.testID==='mission-action-primary')[0].props.accessibilityState.disabled).toBe(true);
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


test('an unbound device cannot restore or sync the old journal while identity is unreachable', async () => {
  await saved('acked');
  mockOwners.clear(); mockJournalNames.clear(); mockLegacyOwner = null;
  await boot();
  expect(root.container.queryAll((n) => n.type === 'Resume' || n.type === 'Execution')).toHaveLength(0);
  expect(mockOpened).toEqual([]);
  expect(screen('JournalOwnership').state).toBe('offline');
});

test('server identity B selects a new partition without exposing the previous account A sets', async () => {
  await saved('acked');
  const fallback = mockTransport.getMockImplementation()!;
  mockTransport.mockImplementation((path: string) => path === '/auth/me'
    ? Promise.resolve({ id: 8, username: 'account-b' }) : fallback(path));
  await boot();
  expect(mockOpened).toEqual(['auren-user-8.db']);
  expect(root.container.queryAll((n) => n.type === 'Resume' || n.type === 'Execution')).toHaveLength(0);
  expect((await mockJournal.restore()).sets).toHaveLength(1);
  expect(mockTransport.mock.calls.filter(([path]) => String(path).includes('/sets/'))).toHaveLength(0);
});

test('legacy attachment waits for ownership proof of every recorded session', async () => {
  await saved('acked');
  mockOwners.clear(); mockJournalNames.clear(); mockLegacyOwner = null;
  const proof = deferred<unknown>();
  const fallback = mockTransport.getMockImplementation()!;
  mockTransport.mockImplementation((path: string) => {
    if (path === '/auth/me') return Promise.resolve({ id: 7, username: 'verified-a' });
    if (path === `/sessions/${plan.session_id}/execution`) return proof.promise;
    return fallback(path);
  });
  await boot();
  expect(mockOpened).toEqual([]);
  await act(async () => proof.resolve({ ...plan, session_id: plan.session_id }));
  expect(mockOpened).toEqual(['auren.db']);
  expect(screen('Resume').position.setsDone).toBe(1);
});


test('account B cannot restore account A through an undo button or its retained callback', async () => {
  await saved('acked'); await boot();
  await act(async () => screen('Resume').onResume());
  await act(async () => screen('Execution').onSkip());
  await act(async () => screen('Execution').onSkipSet(screen('Execution').state.cursorSetId));
  const oldUndo = screen('Execution').undo.onUndo;
  await act(async () => screen('JournalControls').onSignOut());
  const fallback = mockTransport.getMockImplementation()!;
  mockTransport.mockImplementation((path: string) => {
    if (path === '/auth/login') return Promise.resolve({ access_token: 'access-b', refresh_token: 'rt1.device-b.secret', access_expires_in: 900, token_type: 'Bearer', server_now: new Date().toISOString() });
    if (path === '/auth/me') return Promise.resolve({ id: 8, username: 'b' });
    if (path === '/mission') return Promise.resolve(readyMission());
    if (path === '/sessions') return Promise.resolve({ ...plan, session_id: 999 });
    return fallback(path);
  });
  await act(async () => screen('Login').onSubmit('b', 'test-only'));
  await chooseHistorical();
  await act(async () => screen('Mission').onStart(plan.template_slug));
  expect(screen('Execution').state.plan.session_id).toBe(999);
  expect(screen('Execution').undo).toBeNull();
  await act(async () => oldUndo());
  expect(screen('Execution').state.plan.session_id).toBe(999);
});


test('logout during a deferred ownership resolution cannot bind A from B proofs or replace B screen', async () => {
  await saved('acked');
  mockOwners.clear(); mockJournalNames.clear(); mockLegacyOwner = null;
  await boot();
  const delayed = deferred<Restored>();
  const legacy = await mockJournal.restore();
  mockInspectLegacy.mockImplementationOnce(() => delayed.promise);
  const fallback = mockTransport.getMockImplementation()!;
  let user = 7;
  mockTransport.mockImplementation((path: string) => {
    if (path === '/auth/me') return Promise.resolve({ id: user, username: `u${user}` });
    if (path === '/auth/login') return Promise.resolve({ access_token: 'access-b', refresh_token: 'rt1.device-b.secret', access_expires_in: 900, token_type: 'Bearer', server_now: new Date().toISOString() });
    if (path === `/sessions/${plan.session_id}/execution`) return user === 7 ? Promise.resolve(plan) : Promise.reject(new ApiFailure('http', 404));
    if (path === '/mission') return Promise.resolve(readyMission());
    return fallback(path);
  });
  await act(async () => screen('JournalOwnership').onVerify());
  await act(async () => screen('JournalOwnership').onChangeAccount());
  user = 8;
  await act(async () => screen('Login').onSubmit('u8', 'test-only'));
  await chooseHistorical();
  expect(screen('Mission')).toBeDefined();
  await act(async () => delayed.resolve(legacy));
  expect(mockLegacyOwner).toBeNull();
  expect(mockJournalNames.get(7)).toBeUndefined();
  expect(mockJournalNames.get(8)).toBe('auren-user-8.db');
  expect(screen('Mission')).toBeDefined();
});

test('malformed legacy snapshot is preserved apart before a renderable journal is opened', async () => {
  mockOwners.clear(); mockJournalNames.clear(); mockLegacyOwner = null;
  await mockJournal.saveSnapshot({ phase: 'SET', plan: { session_id: 11 } } as never);
  const fallback = mockTransport.getMockImplementation()!;
  mockTransport.mockImplementation((path: string) => path === '/auth/me' ? Promise.resolve({ id: 7, username: 'a' }) : fallback(path));
  await boot();
  expect(mockLegacyOwner).toBeNull();
  expect(mockOpened).toEqual(['auren-user-7.db']);
  expect((await mockJournal.restore()).snapshot).toEqual({ phase: 'SET', plan: { session_id: 11 } });
});


test('native signup uses the account API once, verifies identity, and reaches the real MISSION after confirmation', async () => {
  mockCredential = null; mockOwners.clear(); mockJournalNames.clear();
  await boot();
  await act(async () => screen('Login').onCreateAccount());
  const created = deferred<unknown>();
  const fallback = mockTransport.getMockImplementation()!;
  mockTransport.mockImplementation((path: string) => {
    if (path === '/auth/register') return created.promise;
    if (path === '/auth/me') return Promise.resolve({ id: 8, username: 'new-athlete' });
    if (path === '/mission') return Promise.resolve(readyMission());
    return fallback(path);
  });
  const input = { username: 'new-athlete', password: 'test-only-password', password_confirm: 'test-only-password', email: '' };
  await act(async () => { screen('Signup').onSubmit(input); screen('Signup').onSubmit(input); });
  expect(screen('Signup').busy).toBe(true);
  await act(async () => created.resolve({ access_token: 'new-access', refresh_token: 'rt1.new-device.secret', access_expires_in: 900, token_type: 'Bearer', server_now: new Date().toISOString() }));
  expect(mockTransport.mock.calls.filter(([p]) => p === '/auth/register')).toHaveLength(1);
  expect(mockOpened).toEqual(['auren-user-8.db']);
  expect(screen('AccountResult').kind).toBe('created');
  await act(async () => screen('AccountResult').onContinue());
  expect(screen('FirstUse')).toBeDefined();
  const mounts = mockShellMounts;
  await act(async () => screen('FirstUse').onToday());
  await chooseHistorical();
  expect(screen('Mission')).toBeDefined();
  expect(mockShellMounts).toBe(mounts);
});

test('lost native signup stays on an explicit unknown result without an invented profile or retry', async () => {
  mockCredential = null; await boot();
  await act(async () => screen('Login').onCreateAccount());
  await act(async () => screen('Signup').onSubmit({ username: 'new-athlete', password: 'test-only', password_confirm: 'test-only' }));
  expect(screen('Signup').outcome).toEqual({ state: 'unknown' });
  expect(mockOpened).toEqual([]);
  expect(mockTransport.mock.calls.filter(([p]) => p === '/auth/register')).toHaveLength(1);
  await act(async () => screen('Signup').onLogin());
  expect(screen('Login')).toBeDefined();
});

test('native password page submits the authenticated canonical mutation and confirms its result', async () => {
  const fallback = mockTransport.getMockImplementation()!;
  mockTransport.mockImplementation((path: string) => {
    if (path === '/auth/me') return Promise.resolve({ id: 7, username: 'a' });
    if (path === '/mission') return Promise.resolve(readyMission());
    if (path === '/auth/password') return Promise.resolve({ access_token: 'changed-access', refresh_token: 'rt1.changed-device.secret', access_expires_in: 900, token_type: 'Bearer', server_now: new Date().toISOString() });
    return fallback(path);
  });
  await boot();
  await act(async () => screen('AccountSettings').onPassword());
  const input = { current_password: 'old-test', new_password: 'new-test-password', new_password_confirm: 'new-test-password' };
  await act(async () => screen('Password').onSubmit(input));
  const calls = mockTransport.mock.calls.filter(([p]) => p === '/auth/password');
  expect(calls).toHaveLength(1); expect(calls[0][1].body).toEqual(input);
  expect(screen('AccountResult').kind).toBe('password');
  await act(async () => screen('AccountResult').onContinue());
  expect(mockShellMounts).toBe(1); expect(screen('AccountSettings')).toBeDefined();
  expect(mockCredential).toBe('rt1.changed-device.secret');
});

test('Profile opens the real native preferences editor and saves one canonical replacement without touching the workout journal', async () => {
  const fallback = mockTransport.getMockImplementation()!;
  const projection = require('../ui/account/review/trainingDeclarations.fixture.json');
  mockTransport.mockImplementation(async (path: string, init: any) => {
    if (path === '/mission') return readyMission();
    if (path === '/me/training-preferences/declarations') return init?.method === 'PUT'
      ? { ...projection, declarations: init.body } : projection;
    return fallback(path, init);
  });
  await boot(); const before = await mockJournal.restore();
  await act(async () => screen('AccountSettings').onPreferences());
  const hidden = root.container.queryAll((n) => n.props.testID === 'connected-content')[0].props;
  expect(hidden.accessibilityElementsHidden).toBe(true); expect(hidden.pointerEvents).toBe('none');
  const click = async (id: string) => { await act(async () => {
    const target = root.container.queryAll((n) => n.props.testID === id)[0];
    expect(target).toBeDefined(); target.props.onClick({ nativeEvent: {}, stopPropagation() {}, currentTarget: 1, target: 1 });
  }); };
  await click('preferences-frequency-4'); await click('preferences-next'); await click('preferences-focus-arms');
  await click('preferences-save');
  const calls = mockTransport.mock.calls.filter(([p, i]) => p === '/me/training-preferences/declarations' && i?.method === 'PUT');
  expect(calls).toHaveLength(1);
  expect(calls[0][1].body).toEqual({ sessions_per_week: 4, focus_priorities: ['arms'], available_equipment: null });
  expect(await mockJournal.restore()).toEqual(before);
  await click('preferences-done'); expect(screen('AccountSettings')).toBeDefined();
  expect(mockShellMounts).toBe(1);
});

test('Android back delegates to the preference page before closing the account route', async () => {
  const { BackHandler } = jest.requireActual('react-native');
  let back: (() => boolean) | null = null;
  jest.spyOn(BackHandler, 'addEventListener').mockImplementation((_event: unknown, handler: unknown) => {
    back = handler as () => boolean; return { remove() {} };
  });
  const fallback = mockTransport.getMockImplementation()!;
  mockTransport.mockImplementation(async (path: string, init: any) => {
    if (path === '/mission') return readyMission();
    if (path === '/me/training-preferences/declarations') return require('../ui/account/review/trainingDeclarations.fixture.json');
    return fallback(path, init);
  });
  await boot(); await act(async () => screen('AccountSettings').onPreferences());
  const press = async (id: string) => { await act(async () => root.container.queryAll((n) => n.props.testID === id)[0].props.onClick({ nativeEvent: {}, stopPropagation() {}, currentTarget: 1, target: 1 })); };
  await press('preferences-frequency-4'); await press('preferences-next');
  act(() => { expect(back?.()).toBe(true); });
  expect(root.container.queryAll((n) => n.props.testID === 'preferences-frequency-4')[0].props.accessibilityState.selected).toBe(true);
  expect(root.container.queryAll((n) => n.props.testID === 'connected-content')[0].props.accessibilityElementsHidden).toBe(true);
});

test('Android back closes signup through the current account route, rather than leaving the app', async () => {
  const { BackHandler } = jest.requireActual('react-native');
  let back: (() => boolean) | null = null;
  jest.spyOn(BackHandler, 'addEventListener').mockImplementation((_event: unknown, handler: unknown) => {
    back = handler as () => boolean; return { remove: () => undefined };
  });
  mockCredential = null; await boot();
  await act(async () => screen('Login').onCreateAccount());
  expect(screen('Signup')).toBeDefined();
  let handled = false;
  await act(async () => { handled = back!(); });
  expect(handled).toBe(true);
  expect(screen('Login')).toBeDefined();
});

test('uncertain password result can reauthenticate while owned commands remain pending', async () => {
  await mockJournal.enqueue({ op_id: 'kept-finish', kind: 'SESSION_FINISH', target: `session/${plan.session_id}`,
    payload: { session_id: plan.session_id, at: new Date().toISOString() } }, initialState);
  const fallback = mockTransport.getMockImplementation()!;
  mockTransport.mockImplementation((path: string) => {
    if (path === '/auth/me') return Promise.resolve({ id: 7, username: 'a' });
    if (path === '/mission') return Promise.resolve(readyMission());
    return fallback(path);
  });
  await boot(); await act(async () => screen('AccountSettings').onPassword());
  await act(async () => screen('Password').onSubmit({ current_password: 'old', new_password: 'new-test-only', new_password_confirm: 'new-test-only' }));
  expect(screen('Password').outcome.state).toBe('unknown');
  await act(async () => screen('Password').onLogin());
  expect(screen('Login')).toBeDefined();
  expect((await mockJournal.outboxRows()).map((r) => r.op_id)).toContain('kept-finish');
});

test('two immediate ownership checks share one verification and a late attempt cannot replace success', async () => {
  mockOwners.clear(); mockJournalNames.clear(); mockLegacyOwner = 7;
  const initialTransport=mockTransport.getMockImplementation()!;
  mockTransport.mockImplementation((path:string)=>path==='/auth/me'?Promise.reject(new ApiFailure('network')):initialTransport(path));
  await boot(false);
  const slow = deferred<unknown>(); const fast = deferred<unknown>();
  let verifications = 0;
  const fallback = mockTransport.getMockImplementation()!;
  mockTransport.mockImplementation((path: string) => {
    if (path === '/auth/me') return ++verifications === 1 ? slow.promise : fast.promise;
    if (path === '/mission') return Promise.resolve(readyMission());
    return fallback(path);
  });
  const verify = screen('JournalOwnership').onVerify;
  await act(async () => { verify(); verify(); });
  expect(screen('JournalOwnership').state).toBe('checking');
  expect(verifications).toBe(1);
  await act(async () => fast.resolve({ id: 8, username: 'b' }));
  await act(async () => slow.resolve({ id: 8, username: 'b' }));
  expect(mockOpened).toEqual(['auren-user-8.db']);
  await chooseHistorical();
  expect(screen('Mission')).toBeDefined();
});


test('first-use preferences return to the same journey, preserve the shell, and remain editable later', async () => {
  mockCredential = null; mockOwners.clear(); mockJournalNames.clear(); await boot();
  await act(async () => screen('Login').onCreateAccount());
  const projection = require('../ui/account/review/trainingDeclarations.fixture.json');
  const fallback = mockTransport.getMockImplementation()!;
  mockTransport.mockImplementation(async (path: string, init: any) => {
    if (path === '/auth/register') return { access_token:'new-access', refresh_token:'rt1.new-device.secret',access_expires_in:900,token_type:'Bearer',server_now:new Date().toISOString() };
    if (path === '/auth/me') return {id:8,username:'new-athlete'};
    if (path === '/mission') return readyMission();
    if (path === '/me/training-preferences/declarations') return projection;
    return fallback(path,init);
  });
  await act(async () => screen('Signup').onSubmit({username:'new-athlete',password:'test-only',password_confirm:'test-only'}));
  await act(async () => screen('AccountResult').onContinue());
  const mounts=mockShellMounts;
  expect(await screen('FirstUse').controller.load()).toEqual({state:'no_plan_producer'});
  await act(async () => screen('FirstUse').onPreferences());
  await act(async () => root.container.queryAll((n) => n.props.testID === 'account-back')[0].props.onClick({nativeEvent:{},stopPropagation(){}}));
  expect(screen('FirstUse')).toBeDefined();expect(mockShellMounts).toBe(mounts);
  await act(async () => screen('FirstUse').onToday());
  await act(async () => screen('AccountSettings').onPreferences());
  expect(root.container.queryAll((n) => n.props.testID === 'preferences-frequency-4').length).toBeGreaterThan(0);
  expect(mockTransport.mock.calls.filter(([p,i])=>p==='/me/training-preferences/declarations'&&i?.method==='PUT')).toHaveLength(0);
});

test('an existing server resume remains prior to first-use after registration confirmation', async () => {
  mockCredential=null;mockOwners.clear();mockJournalNames.clear();await boot();
  await act(async()=>screen('Login').onCreateAccount());
  const fallback=mockTransport.getMockImplementation()!;
  mockTransport.mockImplementation(async(path:string,init:any)=>{
    if(path==='/auth/register')return{access_token:'new-access',refresh_token:'rt1.new-device.secret',access_expires_in:900,token_type:'Bearer',server_now:new Date().toISOString()};
    if(path==='/auth/me')return{id:8,username:'new-athlete'};
    if(path==='/mission')return{state:'RESUME',primary_action:'RESUME',position:null,session:{id:plan.session_id,name:'Push A',subtitle:null,template_slug:plan.template_slug,started_at:new Date().toISOString()}};
    return fallback(path,init);
  });
  await act(async()=>screen('Signup').onSubmit({username:'new-athlete',password:'test-only',password_confirm:'test-only'}));
  await act(async()=>screen('AccountResult').onContinue());
  expect(root.container.queryAll(n=>n.type==='FirstUse')).toHaveLength(0);
  expect(mockTransport.mock.calls.filter(([p])=>String(p).includes('first-plan'))).toHaveLength(0);
});

test('ordinary ConnectedApp never reads QA native modules or emits QA observation', async () => {
  const previous=process.env.EXPO_PUBLIC_QA_DELIVERY;
  delete process.env.EXPO_PUBLIC_QA_DELIVERY;
  const output=jest.spyOn(console,'info').mockImplementation(()=>{});
  try {
    await boot();
    expect(output.mock.calls.filter(args=>args[0]==='AUREN_QA_DELIVERY')).toHaveLength(0);
  } finally {
    if(previous===undefined) delete process.env.EXPO_PUBLIC_QA_DELIVERY;
    else process.env.EXPO_PUBLIC_QA_DELIVERY=previous;
  }
});

test('real ConnectedApp mounts the QA provenance observer without exposing training data', async () => {
  const prior={selector:process.env.EXPO_PUBLIC_QA_DELIVERY,native:process.env.EXPO_PUBLIC_QA_NATIVE_SHA,js:process.env.EXPO_PUBLIC_QA_JS_SHA};
  process.env.EXPO_PUBLIC_QA_DELIVERY='1';process.env.EXPO_PUBLIC_QA_NATIVE_SHA='a'.repeat(40);
  process.env.EXPO_PUBLIC_QA_JS_SHA='b'.repeat(40);
  // Native bridges are I/O boundaries; actual ConnectedApp effect and observer remain real.
  jest.doMock('expo-application',()=>({nativeApplicationVersion:'0.0.2',nativeBuildVersion:'3'}));
  jest.doMock('expo-updates',()=>({runtimeVersion:'runtime-A',updateId:'update-B',isEmbeddedLaunch:false}));
  const output=jest.spyOn(console,'info').mockImplementation(()=>{});
  try {
    await boot();
    const events=output.mock.calls.filter(args=>args[0]==='AUREN_QA_DELIVERY');
    expect(events).toHaveLength(1);
    expect(JSON.parse(events[0][1])).toEqual({schemaVersion:'qa-client-observation/1.0.0',
      nativeApplicationVersion:'0.0.2',nativeBuildVersion:'3',runtimeVersion:'runtime-A',
      updateId:'update-B',isEmbeddedLaunch:false,nativeSourceSHA:'a'.repeat(40),currentJSSHA:'b'.repeat(40)});
  } finally {
    for(const [key,value] of Object.entries({EXPO_PUBLIC_QA_DELIVERY:prior.selector,EXPO_PUBLIC_QA_NATIVE_SHA:prior.native,EXPO_PUBLIC_QA_JS_SHA:prior.js})) {
      if(value===undefined) delete process.env[key];else process.env[key]=value;
    }
  }
});

test('MOB04 opens Today on explicit first-use orientation, never automatically fetches legacy execution',async()=>{
 const fallback=mockTransport.getMockImplementation()!;
 mockTransport.mockImplementation(async(path:string)=>path==='/auth/me'?{id:7,username:'Synthetic owner'}:path==='/mission'?readyMission():fallback(path));
 await boot(false);
 expect(root.container.queryAll(n=>n.props.testID==='mission-action-primary')).toHaveLength(1);
 expect(mockTransport.mock.calls.some(([path])=>String(path).includes('/execution'))).toBe(false);
});

function exactMissionRPC(raw:(path:string)=>unknown){
 (global.fetch as jest.Mock).mockImplementation(async(url:any,init:any)=>{
  const path=new URL(String(url),'http://test.invalid').searchParams.get('requested_path')??'FIRST_USE';
  return negotiatedReply(raw(path),200,Boolean(init?.headers?.['X-Auren-Mission-V3-Host']));
 });
}
function exactResume(){return{...mockFirstUse(),state:'RESUME',source:'OPEN_SESSION',primary_action:{kind:'RESUME_LEGACY',session_id:plan.session_id},payload:{state:'RESUME',primary_action:'RESUME',execution_profile:'LEGACY_V1',position:null,session:{id:plan.session_id,name:'Owned synthetic session',subtitle:null,template_slug:plan.template_slug,started_at:new Date().toISOString()}}};}
test('MOB04 exact unavailable DTO does not fetch historical recommendation until the user chooses it',async()=>{
 exactMissionRPC(path=>path==='FIRST_USE'?{...mockFirstUse(),state:'UNAVAILABLE',source:'OWNED_FIRST_USE',primary_action:{kind:'REFRESH'},payload:null,reason:'RUNTIME_NOT_SERVED'}:{...mockFirstUse(),requested_path:path,state:'HISTORICAL_READY',source:'HISTORICAL_MISSION',primary_action:{kind:'START_LEGACY',template_slug:plan.template_slug,decision:readyMission().decision},payload:readyMission()});
 await boot(false);
 expect(mockTransport.mock.calls.filter(([p])=>p==='/mission'||String(p).includes('/execution'))).toHaveLength(0);
 expect(root.container.queryAll(n=>n.type==='Mission')).toHaveLength(0);
 await chooseHistorical();expect(screen('Mission').mission.template.slug).toBe(plan.template_slug);
 expect(mockTransport.mock.calls.filter(([p])=>p==='/sessions')).toHaveLength(0);
});
test('MOB04 exact owned resume reads execution only after explicit action and recovers the same session',async()=>{
 exactMissionRPC(()=>exactResume());const fallback=mockTransport.getMockImplementation()!;
 mockTransport.mockImplementation(async(p:string)=>p===`/sessions/${plan.session_id}/execution`?{...plan,status:'in_progress',done:{},started_at:new Date().toISOString(),ended_at:null,cursor_set_id:first.set_id,excluded_from_stats:false,allowed_actions:[]}:fallback(p));
 await boot(false);expect(mockTransport.mock.calls.filter(([p])=>String(p).includes('/execution'))).toHaveLength(0);
 await pressMissionPrimary();expect(screen('Execution').state.plan.session_id).toBe(plan.session_id);
 expect(mockTransport.mock.calls.filter(([p])=>p==='/sessions')).toHaveLength(0);
});
test('MOB04 exact conflict never chooses an open session or sends a start',async()=>{
 exactMissionRPC(()=>({...mockFirstUse(),state:'CONFLICT',source:'OPEN_SESSION',primary_action:null,payload:null,reason:'MULTIPLE_OPEN_SESSIONS'}));
 await boot(false);await pressMissionPrimary();
 expect(mockTransport.mock.calls.filter(([p])=>p==='/sessions'||p==='/mission'||String(p).includes('/execution'))).toHaveLength(0);
 expect(renderedText(root.container)).toContain('Plusieurs séances');
});
test('MOB04 a lost start response reconciles the existing owned session without another POST',async()=>{
 let created=false;exactMissionRPC(path=>created?{...exactResume(),requested_path:path}:path==='FIRST_USE'?{...mockFirstUse(),state:'UNAVAILABLE',source:'OWNED_FIRST_USE',primary_action:{kind:'REFRESH'},payload:null,reason:'RUNTIME_NOT_SERVED'}:{...mockFirstUse(),requested_path:path,state:'HISTORICAL_READY',source:'HISTORICAL_MISSION',primary_action:{kind:'START_LEGACY',template_slug:plan.template_slug,decision:readyMission().decision},payload:readyMission()});
 const fallback=mockTransport.getMockImplementation()!;
 mockTransport.mockImplementation(async(p:string)=>{if(p==='/sessions'){created=true;throw new ApiFailure('network');}if(p===`/sessions/${plan.session_id}/execution`)return{...plan,status:'in_progress',done:{},started_at:new Date().toISOString(),ended_at:null,cursor_set_id:first.set_id,excluded_from_stats:false,allowed_actions:[]};return fallback(p);});
 await boot(false);await chooseHistorical();const oldStart=screen('Mission').onStart;
 await act(async()=>oldStart(plan.template_slug));await act(async()=>oldStart(plan.template_slug));
 expect(mockTransport.mock.calls.filter(([p])=>p==='/sessions')).toHaveLength(1);
 await pressMissionPrimary();expect(renderedText(root.container)).toContain('Owned synthetic session');
 await pressMissionPrimary();expect(screen('Execution').state.plan.session_id).toBe(plan.session_id);
 expect(mockTransport.mock.calls.filter(([p])=>p==='/sessions')).toHaveLength(1);
});
test('REVIEW lost start stays unresolved when server still reports no open session',async()=>{
 exactMissionRPC(path=>path==='FIRST_USE'?{...mockFirstUse(),state:'UNAVAILABLE',source:'OWNED_FIRST_USE',primary_action:{kind:'REFRESH'},payload:null,reason:'RUNTIME_NOT_SERVED'}:{...mockFirstUse(),requested_path:path,state:'HISTORICAL_READY',source:'HISTORICAL_MISSION',primary_action:{kind:'START_LEGACY',template_slug:plan.template_slug,decision:readyMission().decision},payload:readyMission()});
 const fallback=mockTransport.getMockImplementation()!;
 mockTransport.mockImplementation(async(p:string)=>{if(p==='/sessions')throw new ApiFailure('network');return fallback(p);});
 await boot(false);await chooseHistorical();
 const oldStart=screen('Mission').onStart;
 await act(async()=>oldStart(plan.template_slug));await pressMissionPrimary();
 const newStart=root.container.queryAll(n=>n.type==='Mission')[0]?.props.onStart;
 if(newStart)await act(async()=>newStart(plan.template_slug));
 expect(mockTransport.mock.calls.filter(([p])=>p==='/sessions')).toHaveLength(1);
 expect(renderedText(root.container)).toContain('Réception à vérifier');
});
test('REVIEW cold offline boot offers usable refresh instead of permanent loading',async()=>{
 const fallback=mockTransport.getMockImplementation()!;
 mockTransport.mockImplementation(async(p:string)=>{if(p==='/auth/refresh')throw new ApiFailure('network');return fallback(p);});
 await boot(false);
 const primary=root.container.queryAll(n=>n.props.testID==='mission-action-primary')[0];
 expect(primary).toBeDefined();
 expect(primary.props.accessibilityState.disabled).toBe(false);
});
test('REVIEW current owned remote session replaces a stale local session at explicit resume',async()=>{
 await saved('acked');
 exactMissionRPC(()=>{const x=exactResume();x.primary_action.session_id=999;x.payload.session.id=999;x.payload.session.name='Current owned session';return x;});
 const fallback=mockTransport.getMockImplementation()!;
 mockTransport.mockImplementation(async(p:string)=>p==='/sessions/999/execution'?{...plan,session_id:999,status:'in_progress',done:{},started_at:new Date().toISOString(),ended_at:null,cursor_set_id:first.set_id,excluded_from_stats:false,allowed_actions:[]}:fallback(p));
 await boot(false);
 const oldResume=root.container.queryAll(n=>n.type==='Resume')[0];
 if(oldResume)await act(async()=>oldResume.props.onResume());else await pressMissionPrimary();
 expect(screen('Execution').state.plan.session_id).toBe(999);
});

test('REVIEW a late legacy execution cannot replace a newer owned projection',async()=>{
 const {AppState}=require('react-native');let foreground:(state:string)=>void=()=>{};
 jest.spyOn(AppState,'addEventListener').mockImplementation((_event:any,handler:any)=>{foreground=handler;return{remove(){}};});
 let remoteId=plan.session_id;
 exactMissionRPC(()=>{const x=exactResume();x.primary_action.session_id=remoteId;x.payload.session.id=remoteId;return x;});
 const late=deferred<unknown>(),fallback=mockTransport.getMockImplementation()!;
 mockTransport.mockImplementation(async(p:string)=>p===`/sessions/${plan.session_id}/execution`?late.promise:fallback(p));
 await boot(false);await pressMissionPrimary();
 remoteId=999;await act(async()=>foreground('active'));
 await act(async()=>late.resolve({...plan,status:'in_progress',done:{},started_at:new Date().toISOString(),ended_at:null,cursor_set_id:first.set_id,excluded_from_stats:false,allowed_actions:[]}));
 expect(root.container.queryAll(n=>n.type==='Execution')).toHaveLength(0);
 expect(root.container.queryAll(n=>n.props.testID==='mission-action-primary')[0]).toBeDefined();
});
test('MOB04 lost legacy start remains durably blocked after cold restart and a negative read',async()=>{
 exactMissionRPC(path=>path==='FIRST_USE'?{...mockFirstUse(),state:'UNAVAILABLE',source:'OWNED_FIRST_USE',primary_action:{kind:'REFRESH'},payload:null,reason:'RUNTIME_NOT_SERVED'}:{...mockFirstUse(),requested_path:path,state:'HISTORICAL_READY',source:'HISTORICAL_MISSION',primary_action:{kind:'START_LEGACY',template_slug:plan.template_slug,decision:readyMission().decision},payload:readyMission()});
 const fallback=mockTransport.getMockImplementation()!;mockTransport.mockImplementation(async(p:string)=>{if(p==='/sessions')throw new ApiFailure('network');return fallback(p);});
 await boot(false);await chooseHistorical();await act(async()=>screen('Mission').onStart(plan.template_slug));
 expect((await mockJournal.restore()).snapshot).toMatchObject({mission_opening:{version:'legacy-start-uncertainty/1.0.0',template_slug:plan.template_slug}});
 await act(async()=>root.unmount());root=createRoot();await boot(false);await pressMissionPrimary();
 expect(renderedText(root.container)).toContain('Réception à vérifier');expect(mockTransport.mock.calls.filter(([p])=>p==='/sessions')).toHaveLength(1);
});
test('REREVIEW a delayed A refusal cleanup cannot replace B orientation',async()=>{
 let owner=7,postRefused=false;const release=deferred<void>(),originalSave=mockJournal.saveSnapshot.bind(mockJournal);let cleanupStarted=false;
 mockJournal.saveSnapshot=async(s:any)=>{if(postRefused&&!s.mission_opening){cleanupStarted=true;await release.promise;}return originalSave(s);};
 exactMissionRPC(path=>path==='FIRST_USE'?{...mockFirstUse(owner),state:'UNAVAILABLE',source:'OWNED_FIRST_USE',primary_action:{kind:'REFRESH'},payload:null,reason:'RUNTIME_NOT_SERVED'}:{...mockFirstUse(owner),requested_path:path,state:'HISTORICAL_READY',source:'HISTORICAL_MISSION',primary_action:{kind:'START_LEGACY',template_slug:plan.template_slug,decision:readyMission().decision},payload:readyMission()});
 const fallback=mockTransport.getMockImplementation()!;
 mockTransport.mockImplementation(async(p:string)=>{if(p==='/sessions'){postRefused=true;throw new ApiFailure('http',400,'start_blocked');}if(p==='/auth/me')return{id:owner,username:`u${owner}`};if(p==='/auth/login')return{access_token:'access-b',refresh_token:'rt1.device-b.secret',access_expires_in:900,token_type:'Bearer',server_now:new Date().toISOString()};return fallback(p);});
 await boot(false);await chooseHistorical();await act(async()=>screen('Mission').onStart(plan.template_slug));expect(cleanupStarted).toBe(true);
 await act(async()=>screen('JournalControls').onSignOut());owner=8;await act(async()=>screen('Login').onSubmit('b','test-only'));
 expect(renderedText(root.container)).not.toContain('Démarrage refusé');
 await act(async()=>release.resolve());
 expect(renderedText(root.container)).not.toContain('Démarrage refusé');
});
test('REREVIEW confirmed no open session cannot be forgotten by failed refresh before local resume',async()=>{
 await saved('acked');
 exactMissionRPC(()=>({...mockFirstUse(),state:'UNAVAILABLE',source:'OWNED_FIRST_USE',primary_action:{kind:'REFRESH'},payload:null,reason:'RUNTIME_NOT_SERVED'}));
 await boot(false);
 (global.fetch as jest.Mock).mockImplementation(async()=>{throw new ApiFailure('network');});
 await act(async()=>screen('Resume').onResume());
 await act(async()=>screen('Resume').onResume());
 expect(root.container.queryAll(n=>n.type==='Execution')).toHaveLength(0);
});
test('MOB04 a confirmed closed local session remains excluded after offline cold restart',async()=>{
 await saved('acked');exactMissionRPC(()=>({...mockFirstUse(),state:'UNAVAILABLE',source:'OWNED_FIRST_USE',primary_action:{kind:'REFRESH'},payload:null,reason:'RUNTIME_NOT_SERVED'}));await boot(false);
 await act(async()=>root.unmount());root=createRoot();const fallback=mockTransport.getMockImplementation()!;mockTransport.mockImplementation(async(p:string)=>p==='/auth/refresh'?Promise.reject(new ApiFailure('network')):fallback(p));
 await boot(false);await act(async()=>screen('Resume').onResume());expect(root.container.queryAll(n=>n.type==='Execution')).toHaveLength(0);
});


test('MOB05 real ConnectedApp Progress route consumes owned history and BodyMeasurement reads',async()=>{
 const {historyPage}=require('../../test/trainingHistoryHarness'),{weightPage}=require('../../test/accountDataHarness');mockProgressTab=true;
 mockTransport.mockImplementation(async(path:string)=>{
  if(path==='/auth/refresh')return{access_token:'test-access',refresh_token:'rt1.test-device.next-secret',access_expires_in:900,token_type:'Bearer',server_now:new Date().toISOString()};
  if(path==='/auth/me')return{id:7};
  if(path==='/mission')return{state:'NO_MISSION'};
  if(path.startsWith('/me/training-history?')){const p=historyPage();p.window.time_zone=new URL('https://qa.invalid'+path).searchParams.get('time_zone');return p;}
  if(path.startsWith('/me/body/weight-history')){const p=weightPage();p.entries[0].measured_at='2026-11-05T00:00:00Z';return p;}
  throw new ApiFailure('network');
 });
 await boot(false);await act(async()=>{for(let i=0;i<80;i++)await Promise.resolve();});
 expect(root.container.queryAll(n=>n.props.testID==='progress-frequency')[0]?.props.children).toBe('1');
 expect(mockTransport.mock.calls.some(([p])=>String(p).startsWith('/me/body/weight-history'))).toBe(true);
 expect(mockTransport.mock.calls.some(([p,init])=>String(p).startsWith('/sessions')&&init?.method==='POST')).toBe(false);
});
