/**
 * AUREN — D9 REAL BACKEND BRIDGE (`Sb_VNEXT_MOBILE_D9_01`).
 *
 * The N0 instrument, unchanged, wired to the real FastAPI backend:
 *
 *   LOGIN → MISSION (served engine) → START (web start composition)
 *     → SET confirmed LOCALLY (one SQLite transaction: fact + command)
 *     → REST at once → outbox drained to the server, in order
 *     → TERMINER / PAUSE / ABANDONNER (R16) → BILAN → next MISSION
 *
 * The device decides nothing about training: the plan, its transitions, the
 * mission and the start all come from the server. The device owns only what
 * must survive without a network: the set fact, its time claim (D11), and the
 * queue of commands that carries them.
 */
import * as Crypto from 'expo-crypto';
import { ExpoRoot } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { AppState, BackHandler, Linking, StyleSheet, View } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import { ApiFailure, createTransport } from './src/api/http';
import {RuntimeV3Client,FirstPlanV3Client,createV3Transport} from './src/api/firstPlanV3';
import {BlueprintV3Client} from './src/api/blueprintV3';
import {CalibrationV1Client} from './src/api/calibrationV1';
import {FirstSessionV3Client} from './src/api/firstSessionV3';
import {FirstUseV3Controller} from './src/api/firstUseV3';
import {sendPlanV3Outbox} from './src/sync/planV3Sync';
import {PlanV3Host} from './src/ui/plan/PlanV3Host';
import { FirstPlanClient } from './src/api/firstPlan';
import { FirstUseController } from './src/api/firstUse';
import { FirstUseScreen } from './src/ui/account/FirstUseScreen';
import { TrainingPreferencesClient } from './src/api/trainingPreferences';
import { ExecutionPlan, isStartable, ServerMission, SessionHistoryRead, TrainingPreferencesRead } from './src/api/types';
import { AuthSession, type AccountOutcome, type Registration, type PasswordChange } from './src/auth/authSession';
import { credentialStore } from './src/auth/credentialStore';
import { performedAt, TimeAnchor } from './src/domain/performedAt';
import type { DoneSession } from './src/domain/adherence';
import { sessionPerformance } from './src/domain/performance';
import type { Mission } from './src/domain/types';
import { isElapsed, remainingMs } from './src/domain/timer';
import { Event, exerciseById, initialState, progress, reduce, setById, WorkoutState } from './src/domain/workout';
import { backAction } from './src/native/backAction';
import { deviceIdentity } from './src/native/deviceInfo';
import { observeQADelivery } from './src/native/qaDelivery';
import { deviceLabel } from './src/native/deviceLabel';
import { exitMessage, ExitChoice, EXIT_OPTIONS, showNativeExitSheet } from './src/native/exitSheet';
import { feedback } from './src/native/feedback';
import { keepAwake } from './src/native/keepAwake';
import { announce, useReducedMotion } from './src/native/motion';
import { restNotification } from './src/native/restNotification';
import { initialSpace } from './src/native/shellNav';
import { ShellProvider } from './src/shell/ShellContext';
import { shellRoutes } from './src/shell/routeContext';
import { openJournal } from './src/storage/journal';
import { resolveJournal } from './src/storage/ownership';
import { openOwnershipBook } from './src/storage/ownershipStore';
import { inspectLegacyJournal } from './src/storage/legacyInspection';
import type { Journal } from './src/storage/journalTypes';
import { closeCommand, OutboxRow, restoreState, retryDelayMs, setCommand, substituteCommand } from './src/storage/outbox';
import { stateFromServer } from './src/sync/reconcile';
import { serverStateFromOutbox } from './src/sync/serverState';
import { summaryContext } from './src/sync/summaryContext';
import { reconcileSubstitutions, substitutionStates } from './src/sync/substitutionState';
import { routeFor } from './src/sync/routes';
import { IDLE, SyncEngine, SyncStatus } from './src/sync/syncEngine';
import { CompleteScreen } from './src/ui/CompleteScreen';
import { Sheet, SheetRow } from './src/ui/components';
import { ExecutionScreen } from './src/ui/ExecutionScreen';
import { LabSheet } from './src/ui/LabSheet';
import { LoginScreen } from './src/ui/LoginScreen';
import { SignupScreen, PasswordScreen } from './src/ui/account/AccountForms';
import { AccountResultScreen, AccountSettingsScreen, JournalOwnershipScreen } from './src/ui/account/AccountPages';
import { TrainingPreferencesScreen } from './src/ui/account/TrainingPreferencesScreen';
import { MissionScreen } from './src/ui/MissionScreen';
import { QuietScreen } from './src/ui/QuietScreen';
import { ResumePosition, ResumeScreen } from './src/ui/ResumeScreen';
import { color } from './src/ui/theme';
import { BootScreen } from './src/ui/BootScreen';

const API_URL = process.env.EXPO_PUBLIC_API_URL ?? '';
const PLAN_V3_CONTROLLED_TEST = process.env.EXPO_PUBLIC_PLAN_V3_CONTROLLED_TEST === '1';
const PRIVACY_URL = process.env.EXPO_PUBLIC_PRIVACY_URL;
const PROCESS_ID = Crypto.randomUUID();
const transport = createTransport(API_URL);
/** Before any server contact there is no anchor: every time claim is `estimated`. */
const NO_ANCHOR: TimeAnchor = { serverMs: 0, monoMs: 0, processId: 'none' };
const SUBSTITUTION_REFUSED = 'Le remplacement n’a pas été accepté.';

type Screen = 'BOOT' | 'LOGIN' | 'APP' | 'OWNERSHIP';

function useNow(active: boolean): number {
  const [now, setNow] = useState(Date.now());
  useEffect(() => {
    if (!active) return;
    setNow(Date.now());
    const id = setInterval(() => setNow(Date.now()), 200);
    return () => clearInterval(id);
  }, [active]);
  useEffect(() => {
    const sub = AppState.addEventListener('change', (s) => s === 'active' && setNow(Date.now()));
    return () => sub.remove();
  }, []);
  return now;
}

function localPosition(s: WorkoutState): ResumePosition | null {
  if (!s.plan) return null;
  const { exerciseIndex, exerciseCount } = progress(s);
  const cursor = s.cursorSetId === null ? undefined : setById(s.plan, s.cursorSetId);
  const ex = cursor ? exerciseById(s.plan, cursor.se_id) : undefined;
  return {
    exerciseIndex: exerciseIndex + 1,
    exerciseTotal: exerciseCount,
    setsDone: Object.keys(s.done).length,
    setsTotal: s.plan.sets.length,
    exerciseName: ex?.executed_name ?? null,
  };
}

function statusNote(sync: SyncStatus): { text: string; alert: boolean } | null {
  if (sync.attention > 0) {
    return { text: `${sync.attention} enregistrement${sync.attention > 1 ? 's' : ''} à vérifier — gardé${sync.attention > 1 ? 's' : ''} sur l’appareil`, alert: true };
  }
  if (sync.authRequired && sync.pending > 0) return { text: 'Reconnexion nécessaire pour envoyer les séries — elles sont gardées', alert: false };
  if (sync.offline && sync.pending > 0) return { text: `Hors ligne · ${sync.pending} en attente — tout est gardé sur l’appareil`, alert: false };
  return null;
}

export default function ConnectedApp() {
  useEffect(() => { observeQADelivery(); }, []);
  const [planV3,setPlanV3] = useState<FirstUseV3Controller|null>(null);
  const [planV3Open,setPlanV3Open] = useState(true);
  const [,setPlanV3Revision] = useState(0);
  const [state, setState] = useState<WorkoutState>(initialState);
  const stateRef = useRef(state);
  const journalRef = useRef<Journal | null>(null);
  const [journal, setJournal] = useState<Journal | null>(null);
  const engineRef = useRef<SyncEngine | null>(null);
  const anchorRef = useRef<TimeAnchor>(NO_ANCHOR);
  const notifRef = useRef<string | null>(null);
  const pressInRef = useRef<number | null>(null);
  const resumedRef = useRef(false);
  const closedRef = useRef<number | null>(null);
  const reducedMotion = useReducedMotion();

  const [screen, setScreen] = useState<Screen>('BOOT');
  const [account, setAccount] = useState<string | null>(null);
  const [loginError, setLoginError] = useState<'invalid' | 'network' | null>(null);
  const [busy, setBusy] = useState(false);
  const [accountView, setAccountView] = useState<'signup' | 'password' | 'created' | 'password-done' | 'preferences' | 'first-use' | 'first-use-preferences' | null>(null);
  const preferencesExit = useRef<(() => void) | null>(null);
  const registerPreferencesExit = useCallback((handler: (() => void) | null) => { preferencesExit.current = handler; }, []);
  const [accountOutcome, setAccountOutcome] = useState<AccountOutcome | null>(null);
  const accountFlight = useRef(false);
  const ownershipFlight = useRef<Promise<void> | null>(null);
  const [ownershipChecking, setOwnershipChecking] = useState(false);
  const sessionActionInFlight = useRef(false);
  const [mission, setMission] = useState<ServerMission | null>(null);
  const [offline, setOffline] = useState(false);
  const [paused, setPaused] = useState(false);
  const [sync, setSync] = useState<SyncStatus>(IDLE);
  const [next, setNext] = useState<Mission | null>(null);
  const [bilanContext, setBilanContext] = useState<{ sessionId: number; history: DoneSession[] | null; sessionsPerWeek: number | null; contextLine: string | null } | null>(null);
  const [exitOpen, setExitOpen] = useState(false);
  const [lab, setLab] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  /** §8.7 — per set, what the server said: acknowledged or refused (absent = not yet). */
  const [substitutions, setSubstitutions] = useState<ReturnType<typeof substitutionStates>>({});
  const [substitutionNotice, setSubstitutionNotice] = useState<string | null>(null);
  const substitutionRefreshInFlight = useRef(false);
  const substitutionRefreshAgain = useRef(false);
  const substitutionRetryTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const substitutionRetryAttempt = useRef(0);
  const appAlive = useRef(true);
  const refreshJournalRef = useRef<() => Promise<void>>(async () => undefined);
  const [serverSets, setServerSets] = useState<ReturnType<typeof serverStateFromOutbox>>({});
  const [signOutBlocked, setSignOutBlocked] = useState<number | null>(null);
  /** R10 / R12 — a skip can be taken back for a few seconds; nothing was written. */
  const [undo, setUndo] = useState<{ text: string; prev: WorkoutState; revision: number } | null>(null);
  const undoTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const auth = useMemo(
    () => new AuthSession(transport, credentialStore, () => performance.now(), (iso, mono) => {
      anchorRef.current = { serverMs: Date.parse(iso), monoMs: mono, processId: PROCESS_ID };
    }),
    [],
  );
  const preferencesClient = useMemo(() => new TrainingPreferencesClient(auth, transport), [auth]);
  const firstUse = useMemo(() => new FirstUseController(auth, transport, preferencesClient, new FirstPlanClient(auth, transport)), [auth, preferencesClient]);

  const apply = useCallback((event: Event): WorkoutState => {
    const n = reduce(stateRef.current, event);
    stateRef.current = n;
    setState(n);
    return n;
  }, []);

  const metric = useCallback((name: string, value = 1) => {
    void journalRef.current?.recordMetric(name, value).catch(() => undefined);
  }, []);

  /** D11 — every read model re-anchors the device on server time. */
  const anchorOn = useCallback((serverNowIso: string) => {
    anchorRef.current = { serverMs: Date.parse(serverNowIso), monoMs: performance.now(), processId: PROCESS_ID };
  }, []);

  const api = useCallback(<T,>(path: string, init: { method?: 'GET' | 'POST' | 'PUT'; body?: unknown } = {}) =>
    auth.authorized((token) => transport<T>(path, { ...init, token })), [auth]);

  const fetchExecution = useCallback(async (sessionId: number): Promise<ExecutionPlan> => {
    const plan = await api<ExecutionPlan>(`/sessions/${sessionId}/execution`);
    anchorOn(plan.server_now);
    return plan;
  }, [api, anchorOn]);

  const journalReadVersion = useRef(0);
  const substitutionWritesInFlight = useRef(0);
  const refreshServerSets = useCallback(async (): Promise<void> => {
    if (!appAlive.current) return;
    const current = journalRef.current;
    if (!current) return;
    const version = ++journalReadVersion.current;
    const restored = await current.restore().catch((error) => {
      if (appAlive.current && version === journalReadVersion.current) setServerSets({});
      throw error;
    });
    if (!appAlive.current || version !== journalReadVersion.current || substitutionWritesInFlight.current > 0) return;
    setServerSets(serverStateFromOutbox(restored.outbox));
    const local = stateRef.current;
    const statuses = substitutionStates(restored.outbox, local.plan?.session_id);
    setSubstitutions(statuses);
    const refused = Object.values(statuses).some((status) => status.state === 'failed');
    setSubstitutionNotice((previous) => refused ? SUBSTITUTION_REFUSED : previous === SUBSTITUTION_REFUSED ? null : previous);
    const resolved = reconcileSubstitutions(local, restored.outbox);
    if (resolved !== local) apply({ type: 'RESTORE', state: resolved });
    const acknowledged = Object.entries(statuses).filter(([key, status]) => status.state === 'acked'
      && resolved.requiresSync[Number(key)]?.substitute === status.name);
    if (!acknowledged.length || !resolved.plan) {
      if (substitutionRetryTimer.current) clearTimeout(substitutionRetryTimer.current);
      substitutionRetryTimer.current = null;
      substitutionRetryAttempt.current = 0;
      return;
    }
    if (substitutionRefreshInFlight.current) { substitutionRefreshAgain.current = true; return; }
    if (substitutionRetryTimer.current) clearTimeout(substitutionRetryTimer.current);
    substitutionRetryTimer.current = null;
    substitutionRefreshInFlight.current = true;
    const sessionId = resolved.plan.session_id;
    let failedRead = false;
    try {
      const plan = await fetchExecution(sessionId);
      const journal = await current.restore();
      const latest = stateRef.current;
      if (!appAlive.current || latest.plan?.session_id !== sessionId) return;
      let merged = reconcileSubstitutions(stateFromServer(plan, latest, journal.sets, Date.now()), journal.outbox);
      const latestStatuses = substitutionStates(journal.outbox, sessionId);
      // Ce GET a démarré APRÈS ces accusés précis : le plan canonique prévaut,
      // y compris si un autre appareil a depuis changé le nom exécuté.
      for (const [key, status] of acknowledged) {
        const id = Number(key);
        if (latestStatuses[id]?.opId === status.opId && merged.requiresSync[id]?.substitute === status.name) {
          const { [id]: _request, ...rest } = merged.requiresSync;
          merged = { ...merged, requiresSync: rest };
        }
      }
      apply({ type: 'RESTORE', state: merged });
      setOffline(false);
      substitutionRetryAttempt.current = 0;
    } catch (error) {
      failedRead = true;
      if (!appAlive.current) return;
      if (error instanceof ApiFailure && error.kind === 'http' && error.status === 401) {
        setScreen('LOGIN');
      } else if (error instanceof ApiFailure && (error.kind === 'network' || error.status >= 500 || error.status === 429 || error.status === 408)) {
        if (error.kind === 'network') setOffline(true);
        const delay = retryDelayMs(substitutionRetryAttempt.current++);
        substitutionRetryTimer.current = setTimeout(() => {
          substitutionRetryTimer.current = null;
          void refreshJournalRef.current().catch(() => undefined);
        }, delay);
      } else {
        setSubstitutionNotice('Plan indisponible ; données locales conservées.');
      }
    } finally {
      substitutionRefreshInFlight.current = false;
      const again = substitutionRefreshAgain.current;
      substitutionRefreshAgain.current = false;
      if (again && !failedRead && appAlive.current) void refreshJournalRef.current().catch(() => undefined);
    }
  }, [apply, fetchExecution]);
  refreshJournalRef.current = refreshServerSets;

  const onStatus = useCallback((s: SyncStatus) => {
    setSync(s);
    void refreshServerSets().catch(() => undefined);
  }, [refreshServerSets]);

  // ── canonical state: the mission, and the open session if there is one ────
  const loadMission = useCallback(async () => {
    const revision = auth.revision;
    try {
      const m = await api<ServerMission>('/mission');
      if (revision !== auth.revision || !journalRef.current) return;
      setOffline(false);
      setMission(m);
      const local = stateRef.current;
      if (m.state === 'RESUME' && m.session.template_slug === 'science:v3:first-session') {
        // Existing owned handoff, never a scientific recommendation fallback.
        setPaused(true);
        return;
      }
      if (m.state === 'RESUME') {
        const plan = await fetchExecution(m.session.id);
        const target=journalRef.current;
        const current=()=>appAlive.current&&revision===auth.revision&&target===journalRef.current;
        const restored = target ? await target.restore() : { sets: [], outbox: [] };
        if (!current()||plan.session_id!==m.session.id) return;
        const latest = stateRef.current;
        const next=reconcileSubstitutions(stateFromServer(plan, latest.phase === 'MISSION' ? null : latest, restored.sets, Date.now()), restored.outbox);
        await target?.beginLegacy?.(next,current);
        if(!current())return;
        setPlanV3Open(false);
        apply({ type: 'RESTORE', state: next });
        setPaused(true);
      } else if (local.phase === 'SET' || local.phase === 'REST') {
        // the server holds no open session: it was closed elsewhere (web) or by a
        // command already acknowledged. Pending commands stay visible in the journal.
        apply({ type: 'RESET' });
        setPaused(false);
      }
    } catch (e) {
      if (revision !== auth.revision) return;
      if (e instanceof ApiFailure && e.kind === 'http' && e.status === 401) {
        setScreen('LOGIN');
        return;
      }
      setOffline(true);
    }
  }, [api, apply, auth, fetchExecution]);

  const onAck = useCallback((row: OutboxRow, response: unknown) => {
    metric('SYNC-ACK');
    metric('G-SYNC', Date.now() - row.created_at_ms);
    if ((response as { applied?: boolean } | null)?.applied === false) metric('SYNC-ACK-DUPLICATE');
    setOffline(false);
    if (row.kind === 'SET_COMPLETION' || row.kind === 'SUBSTITUTE') {
      void refreshServerSets().catch(() => undefined);
    }
    if (row.kind === 'SESSION_FINISH' || row.kind === 'SESSION_ABANDON') {
      void api<ServerMission>('/mission').then((m) => {
        if (isStartable(m)) setNext(m as unknown as Mission);
        if (stateRef.current.phase === 'MISSION') setMission(m);
      }).catch(() => undefined);
    }
  }, [api, metric, refreshServerSets]);

  const attachJournal = useCallback(async (online: boolean): Promise<boolean> => {
    const revision = auth.revision;
    const current = () => appAlive.current && revision === auth.revision;
    const ownedApi = async <T,>(path: string): Promise<T> => {
      if (!current()) throw new ApiFailure('http', 401, 'stale_identity');
      const value = await api<T>(path);
      if (!current()) throw new ApiFailure('http', 401, 'stale_identity');
      return value;
    };
    const owned = await resolveJournal({
      isCurrent: current,
      book: await openOwnershipBook(), deviceId: await auth.deviceSessionId(), online,
      identity: async () => {
        const identity = await ownedApi<{ id: number; username: string }>('/auth/me');
        if (revision === auth.revision) setAccount(identity.username);
        return identity;
      },
      inspectLegacy: inspectLegacyJournal,
      verifySession: (id) => ownedApi<{ session_id: number }>(`/sessions/${id}/execution`),
    });
    if (!appAlive.current || revision !== auth.revision) return false;
    if (owned.state !== 'ready') { setScreen('OWNERSHIP'); return false; }
    const j = await openJournal(owned.name, PLAN_V3_CONTROLLED_TEST ? {planV3OwnerId:owned.userId} : {});
    if (!appAlive.current || revision !== auth.revision) return false;
    engineRef.current?.stop();
    journalRef.current = j;
    setJournal(j);
    const active = () => appAlive.current && revision === auth.revision && journalRef.current === j;
    const v3Runtime = new RuntimeV3Client(auth,transport,createV3Transport(API_URL,fetch,{calibrationInventory:"plan-calibration-inventory/2.0.0"}));
    const v3Sessions = new FirstSessionV3Client(v3Runtime);
    if(PLAN_V3_CONTROLLED_TEST && j.planV3){
      const controller = new FirstUseV3Controller({ownerId:owned.userId,journal:j.planV3,sessions:v3Sessions,
        plan:new FirstPlanV3Client(v3Runtime),blueprint:new BlueprintV3Client(v3Runtime),calibration:new CalibrationV1Client(v3Runtime),
        newId:()=>Crypto.randomUUID(),current:active},()=>{if(active())setPlanV3Revision(value=>value+1);});
      await controller.restore();if(!active())return false;
      if(controller.state){setPlanV3(controller);setPlanV3Open(true);void controller.load().catch(()=>undefined);}
    }else setPlanV3(null);
    engineRef.current = new SyncEngine(j, (row) => {
      if (!active()) return Promise.reject(new ApiFailure('http', 401, 'auth'));
      if(row.kind === 'PLAN_V3_SET'){
        if(!j.planV3)return Promise.reject(new ApiFailure('http',409,'typed_journal_unavailable'));
        return sendPlanV3Outbox(row,v3Sessions,j.planV3,active);
      }
      const r = routeFor(row);
      return api(r.path, { method: r.method, body: r.body });
    }, (status) => { if (active()) onStatus(status); }, (row, response) => { if (active()) onAck(row, response); });
    const r = await j.restore();
    if (!active()) return false;
    setServerSets(serverStateFromOutbox(r.outbox));
    const statuses = substitutionStates(r.outbox, r.snapshot?.plan?.session_id);
    setSubstitutions(statuses);
    setSubstitutionNotice(Object.values(statuses).some((status) => status.state === 'failed') ? SUBSTITUTION_REFUSED : null);
    if (r.snapshot && r.snapshot.phase !== 'MISSION') {
      const restored = reconcileSubstitutions(restoreState(r.snapshot, r.sets), r.outbox);
      apply({ type: 'RESTORE', state: restored });
      setPaused(restored.phase !== 'COMPLETE');
      await j.recordMetric('RELAUNCH-RESTORED-SETS', Object.values(restored.done).filter((d) => d.local === 'saved_local').length);
    } else { apply({ type: 'RESET' }); setPaused(false); }
    if (!active()) return false;
    if (owned.quarantined) setNotice('Un ancien journal reste conservé séparément, sans être attribué à ce compte.');
    setScreen('APP');
    setOffline(!online);
    return true;
  }, [api, apply, auth, onAck, onStatus]);

  const verifyOwnership = useCallback(() => {
    if (ownershipFlight.current) return ownershipFlight.current;
    const revision = auth.revision;
    setOwnershipChecking(true);
    const task = (async () => {
      try {
        const ready = await attachJournal(true);
        if (ready && revision === auth.revision && appAlive.current) {
          await engineRef.current?.kick(); await loadMission();
        }
      } catch {
        if (appAlive.current && revision === auth.revision) setScreen('LOGIN');
      }
    })();
    ownershipFlight.current = task;
    void task.finally(() => {
      if (ownershipFlight.current !== task) return;
      ownershipFlight.current = null;
      if (appAlive.current && revision === auth.revision) setOwnershipChecking(false);
    });
    return task;
  }, [attachJournal, auth, loadMission]);

  // Resolve identity BEFORE a journal can be restored, displayed or synchronized.
  useEffect(() => {
    appAlive.current = true;
    const boot = async () => {
      if (!(await auth.hasCredential())) { if (appAlive.current) setScreen('LOGIN'); return; }
      const outcome = await auth.refresh();
      if (!appAlive.current) return;
      if (outcome === 'invalid') { setScreen('LOGIN'); return; }
      if (!(await attachJournal(outcome === 'ok'))) return;
      if (outcome === 'network') return;
      await engineRef.current?.kick();
      await loadMission();
    };
    void boot().catch(() => { if (appAlive.current) setScreen('LOGIN'); });
    const stop = restNotification.onDelivery((late) => metric('NOTIF-LATENESS', late));
    return () => {
      appAlive.current = false;
      if (substitutionRetryTimer.current) clearTimeout(substitutionRetryTimer.current);
      substitutionRetryTimer.current = null;
      stop(); engineRef.current?.stop();
    };
  }, []);

  // back in the foreground: drain, and re-read the canonical state between workouts
  useEffect(() => {
    const sub = AppState.addEventListener('change', (s) => {
      if (s !== 'active') return;
      resumedRef.current = true;
      if (screen !== 'APP') return;
      void engineRef.current?.kick();
      if (stateRef.current.phase === 'MISSION') void loadMission();
    });
    return () => sub.remove();
  }, [auth, loadMission, screen]);

  useEffect(() => {
    const target = journalRef.current;
    const revision = auth.revision;
    const t = setTimeout(() => {
      if (target && target === journalRef.current && revision === auth.revision) void target.saveSnapshot(state).catch(() => undefined);
    }, 250);
    return () => clearTimeout(t);
  }, [auth, state]);

  useEffect(() => {
    if ((state.phase === 'SET' || state.phase === 'REST') && !paused) keepAwake.enable();
    else keepAwake.disable();
    if (state.phase === 'COMPLETE') metric('SESSION-COMPLETED');
  }, [state.phase, paused, metric]);

  // ── BILAN reached (last set, or TERMINER): close the session on the server, once ──
  useEffect(() => {
    const s = stateRef.current;
    // a skip that reached the bilan can still be undone: close only once the window has passed
    if (undo) return;
    if (s.phase !== 'COMPLETE' || !s.plan || closedRef.current === s.plan.session_id) return;
    closedRef.current = s.plan.session_id;
    const cmd = closeCommand(Crypto.randomUUID(), 'SESSION_FINISH', s.plan.session_id, performedAt(anchorRef.current, performance.now(), PROCESS_ID, Date.now()).epochMs);
    void journalRef.current?.enqueue(cmd, s).then(() => engineRef.current?.kick()).catch(() => undefined);
  }, [state.phase, undo]);

  // Les deux lectures sont indépendantes : une indisponibilité n’invente ni cadence ni historique.
  useEffect(() => {
    if (screen !== 'APP' || state.phase !== 'COMPLETE' || !state.plan) return;
    let active = true;
    const sessionId = state.plan.session_id;
    setBilanContext({ sessionId, history: null, sessionsPerWeek: null, contextLine: null });
    void api<TrainingPreferencesRead>('/me/training-preferences').then((value) => {
      const declared = value.sessions_per_week;
      if (active && Number.isInteger(declared) && declared! > 0) {
        setBilanContext((current) => current?.sessionId === sessionId ? { ...current, sessionsPerWeek: declared! } : current);
      }
    }).catch(() => undefined);
    void api<SessionHistoryRead>('/me/sessions?limit=500').then((value) => {
      // Une page tronquée ne prouve pas une suite de semaines tenues.
      if (!active || !Array.isArray(value.sessions) || value.has_more !== false || value.sessions.some((row) => !Number.isFinite(Date.parse(row.ended_at)))) return;
      const history = value.sessions.filter((row) => row.id !== sessionId)
        .map((row) => ({ slug: row.template_slug, atMs: Date.parse(row.ended_at) }));
      setBilanContext((current) => current?.sessionId === sessionId ? { ...current, history, contextLine: summaryContext(value, sessionId) } : current);
    }).catch(() => undefined);
    return () => { active = false; };
  }, [api, screen, state.phase, state.plan?.session_id]);

  // ── the deadline is the truth; the tick only redraws and detects the end ───
  const now = useNow(state.phase === 'REST' && !paused);
  useEffect(() => {
    const s = stateRef.current;
    if (paused || s.phase !== 'REST' || !s.rest || !isElapsed(s.rest, now)) return;
    const opening = s.rest.after.kind === 'REST_THEN_EXERCISE';
    metric(resumedRef.current ? 'REST-END-LATENESS-RESUME' : 'REST-END-LATENESS-FOREGROUND', now - s.rest.deadlineMs);
    resumedRef.current = false;
    metric(opening ? 'AUTO-NEXT-EXERCISE' : 'AUTO-NEXT-SET');
    const n = apply({ type: 'REST_END', nowMs: now });
    notifRef.current = null;
    if (AppState.currentState === 'active') {
      feedback.restDone();
      if (opening) setTimeout(feedback.nextExercise, 380);
    }
    const ex = n.plan && n.cursorSetId !== null ? exerciseById(n.plan, setById(n.plan, n.cursorSetId)!.se_id) : undefined;
    announce(opening && ex ? `Repos terminé. Exercice suivant : ${ex.executed_name}` : 'Repos terminé. Série suivante.');
  }, [now, paused, apply, metric]);

  const showed = useMemo(
    () => (state.phase === 'COMPLETE' && state.plan ? sessionPerformance(state.plan, state.done, state.requiresSync) : null),
    [state.phase, state.plan, state.done, state.requiresSync],
  );

  // ── handlers ───────────────────────────────────────────────────────────────
  const login = useCallback(async (username: string, password: string) => {
    if (busy || accountFlight.current) return;
    accountFlight.current = true;
    ownershipFlight.current = null; setOwnershipChecking(false);
    if (undoTimer.current) clearTimeout(undoTimer.current); undoTimer.current = null; setUndo(null);
    engineRef.current?.stop(); engineRef.current = null; journalRef.current = null; setJournal(null);
    apply({ type: 'RESET' }); setServerSets({}); setMission(null); setNext(null); setBilanContext(null);
    setBusy(true); setLoginError(null);
    const pending = auth.login(username, password, deviceLabel(deviceIdentity()));
    const revision = auth.revision;
    try {
      const outcome = await pending;
      if (revision !== auth.revision || !appAlive.current) return;
      if (outcome !== 'ok') { setLoginError(outcome); return; }
      setAccountView(null); setAccountOutcome(null);
      if (!(await attachJournal(true))) return;
      await (engineRef.current as SyncEngine | null)?.kick();
      await loadMission();
    } catch {
      if (revision === auth.revision && appAlive.current) setLoginError('network');
    } finally {
      if (revision === auth.revision && appAlive.current) { setBusy(false); accountFlight.current = false; }
    }
  }, [apply, attachJournal, auth, busy, loadMission]);

  const register = useCallback(async (input: Registration) => {
    if (accountFlight.current) return;
    accountFlight.current = true; setBusy(true); setAccountOutcome(null);
    const pending = auth.register(input, deviceLabel(deviceIdentity()));
    const revision = auth.revision;
    try {
      const outcome = await pending;
      if (revision !== auth.revision || !appAlive.current || outcome.state === 'cancelled') return;
      setAccountOutcome(outcome);
      if (outcome.state !== 'confirmed') return;
      const attached = await attachJournal(true);
      if (attached) await loadMission();
      if (revision === auth.revision && appAlive.current) setAccountView('created');
    } catch {
      if (revision === auth.revision && appAlive.current) { setScreen('OWNERSHIP'); setAccountView('created'); }
    } finally {
      if (revision === auth.revision && appAlive.current) { setBusy(false); accountFlight.current = false; }
    }
  }, [attachJournal, auth, loadMission]);

  const changePassword = useCallback(async (input: PasswordChange) => {
    if (accountFlight.current) return;
    accountFlight.current = true; setBusy(true); setAccountOutcome(null);
    const revision = auth.revision;
    try {
      const outcome = await auth.changePassword(input);
      if (revision !== auth.revision || !appAlive.current || outcome.state === 'cancelled') return;
      setAccountOutcome(outcome);
      if (outcome.state === 'confirmed') {
        // The new device session must be bound before its first offline restart.
        await attachJournal(true);
        if (revision === auth.revision && appAlive.current) setAccountView('password-done');
      }
    } catch {
      if (revision === auth.revision && appAlive.current) { setScreen('OWNERSHIP'); setAccountView('password-done'); }
    } finally {
      if (revision === auth.revision && appAlive.current) { setBusy(false); accountFlight.current = false; }
    }
  }, [attachJournal, auth]);

  const reschedule = useCallback((s: WorkoutState, nowMs: number) => {
    if (!s.rest || !s.plan) return;
    const after = s.rest.after;
    const nextEx = after.kind === 'BILAN' ? undefined : exerciseById(s.plan, setById(s.plan, after.set_id)!.se_id);
    const previous = notifRef.current;
    notifRef.current = null;
    const seconds = remainingMs(s.rest, nowMs) / 1000;
    void (async () => {
      await restNotification.cancel(previous);
      notifRef.current = await restNotification.schedule(seconds, nextEx ? nextEx.executed_name : 'Série suivante');
      if (notifRef.current) metric('NOTIF-REQUESTED', seconds);
    })();
  }, [metric]);

  const cancelRestNotification = useCallback(() => {
    void restNotification.cancel(notifRef.current);
    notifRef.current = null;
  }, []);

  const start = useCallback(async (slug: string) => {
    if (!mission || mission.state !== 'READY' || busy || sessionActionInFlight.current) return;
    const generation=auth.revision,ownedJournal=journalRef.current;
    const current=()=>appAlive.current&&auth.revision===generation&&journalRef.current===ownedJournal;
    sessionActionInFlight.current = true;
    setBusy(true);
    setNotice(null);
    try {
      const plan = await api<ExecutionPlan>('/sessions', {
        method: 'POST',
        body: {
          template_slug: slug,
          creation_source: slug === mission.template.slug ? 'reco_top' : 'reco_alt',
          decision: mission.decision,
        },
      });
      if(!current())return;
      const nowMs=Date.now();
      await ownedJournal?.beginLegacy?.(reduce(stateRef.current,{type:'START',plan,nowMs}),current);
      if(!current())return;
      setPlanV3Open(false);
      anchorOn(plan.server_now);
      closedRef.current = null;
      apply({ type: 'START', plan, nowMs });
      setPaused(false);
      void restNotification.prepare().catch(() => undefined);
    } catch (e) {
      feedback.refused();
      if (e instanceof ApiFailure && e.kind === 'http' && e.code === 'session_open') await loadMission();
      else if (e instanceof ApiFailure && e.code === 'start_blocked') setNotice('Cette séance n’est pas faisable avec l’équipement déclaré.');
      else setNotice('AUREN est injoignable : le démarrage attend la connexion.');
    } finally {
      sessionActionInFlight.current = false;
      setBusy(false);
    }
  }, [anchorOn, api, apply, auth, busy, loadMission, mission]);

  const validate = useCallback((setId: number) => {
    const before = stateRef.current;
    const currentSet = before.plan && setById(before.plan, setId);
    if (currentSet && before.requiresSync[currentSet.se_id]) { feedback.refused(); return; }
    const at = performedAt(anchorRef.current, performance.now(), PROCESS_ID, Date.now());
    const nowMs = Date.now();
    const n = apply({ type: 'VALIDATED', setId, performedAt: at, nowMs });
    if (n === before) {
      feedback.refused();
      return;
    }
    const plan = n.plan!;
    const done = n.done[setId];
    const set = setById(plan, setId)!;
    metric('SET-VALIDATED');
    if (n.phase === 'REST' && n.rest) reschedule(n, nowMs);
    const j = journalRef.current;
    if (!j) {
      apply({ type: 'LOCAL_COMMIT', setId, ok: false });
      feedback.failed();
      return;
    }
    const row = {
      set_id: setId, session_id: plan.session_id, se_id: set.se_id, weight_kg: done.weight, reps: done.reps,
      performed_at_ms: at.epochMs, performed_at_estimated: at.estimated ? 1 : 0,
      local_state: 'saved_local', created_at_ms: nowMs,
    };
    const cmd = setCommand(Crypto.randomUUID(), plan.session_id, setId, done.weight, done.reps, at);
    void (async () => {
      let ms: number;
      try {
        ms = await j.commitValidation(row, cmd, n);
      } catch {
        metric('COMMIT-FAILED');
        apply({ type: 'LOCAL_COMMIT', setId, ok: false });
        feedback.failed();
        return;
      }
      apply({ type: 'LOCAL_COMMIT', setId, ok: true });
      feedback.setSaved();
      await j.recordMetric('G-LOCAL', ms).catch(() => undefined);
      void engineRef.current?.kick();
    })();
  }, [apply, reschedule, metric]);

  const onRestPainted = useCallback(() => {
    const t0 = pressInRef.current;
    if (t0 === null) return;
    pressInRef.current = null;
    requestAnimationFrame(() => journalRef.current?.recordMetric('G-VAL', performance.now() - t0).catch(() => undefined));
  }, []);

  const shiftRest = useCallback((deltaMs: number) => {
    const nowMs = Date.now();
    const n = apply({ type: 'REST_SHIFT', deltaMs, nowMs });
    if (!n.rest) return;
    feedback.step();
    reschedule(n, nowMs);
  }, [apply, reschedule]);

  const skip = useCallback(() => {
    const opening = stateRef.current.rest?.after.kind === 'REST_THEN_EXERCISE';
    cancelRestNotification();
    metric('REST-SKIP');
    apply({ type: 'REST_END', nowMs: Date.now() });
    if (opening) feedback.nextExercise();
  }, [apply, cancelRestNotification, metric]);

  const requestSubstitute = useCallback((seId: number, name: string) => {
    const before = stateRef.current;
    if (!before.plan || before.requiresSync[seId]) return;
    // Invalidate snapshots read before this mutation, including reads during its durable write.
    substitutionWritesInFlight.current += 1;
    journalReadVersion.current += 1;
    const s = apply({ type: 'REQUEST_SUBSTITUTE', seId, substitute: name });
    feedback.step();
    setSubstitutionNotice(null);
    const sessionId = before.plan.session_id;
    const cmd = substituteCommand(Crypto.randomUUID(), sessionId, seId, name);
    const finishWrite = () => {
      substitutionWritesInFlight.current -= 1;
      journalReadVersion.current += 1;
      void refreshJournalRef.current().catch(() => undefined);
    };
    const failed = () => {
      finishWrite();
      const current = stateRef.current;
      if (current.plan?.session_id !== sessionId || current.requiresSync[seId]?.substitute !== name) return;
      const { [seId]: _request, ...rest } = current.requiresSync;
      apply({ type: 'RESTORE', state: { ...current, requiresSync: rest } });
      setSubstitutionNotice('Remplacement non enregistré sur l’appareil.');
    };
    const journal = journalRef.current;
    if (!journal) { failed(); return; }
    void journal.enqueue(cmd, s).then(() => {
      finishWrite();
      // Le fait est déjà durable : une panne du drain ne doit pas annuler sa demande.
      void engineRef.current?.kick().catch(() => {
        if (stateRef.current.plan?.session_id === sessionId) setSubstitutionNotice('Demande gardée, synchronisation en attente.');
      });
    }, failed);
  }, [apply]);

  // ── R10 / R12 — passer une série, passer un exercice (rien n'est écrit) ─────
  const UNDO_MS = 5000;
  const skipWith = useCallback((event: Event, text: string) => {
    const before = stateRef.current;
    const n = apply(event);
    if (n === before) return;
    feedback.step();
    metric(event.type);
    if (undoTimer.current) clearTimeout(undoTimer.current);
    setUndo({ text, prev: before, revision: auth.revision });
    undoTimer.current = setTimeout(() => setUndo(null), UNDO_MS);
  }, [apply, auth, metric]);

  const takeBack = useCallback(() => {
    if (!undo || undo.revision !== auth.revision || undo.prev.plan?.session_id !== stateRef.current.plan?.session_id) return;
    if (undoTimer.current) clearTimeout(undoTimer.current);
    apply({ type: 'RESTORE', state: undo.prev });
    setUndo(null);
    metric('SKIP-UNDONE');
  }, [apply, auth, metric, undo]);

  // ── R16 — TERMINER / PAUSE / ABANDONNER / ANNULER ─────────────────────────
  const onExitChoice = useCallback((choice: ExitChoice) => {
    setExitOpen(false);
    metric(`EXIT-${choice.toUpperCase()}`);
    const s = stateRef.current;
    if (!s.plan || choice === 'cancel') return;
    if (choice === 'finish') {
      cancelRestNotification();
      apply({ type: 'FINISH_NOW', nowMs: Date.now() });
      feedback.setSaved();
      return;
    }
    if (choice === 'pause') {
      cancelRestNotification();
      setPaused(true);
      return;
    }
    cancelRestNotification();
    const sid = s.plan.session_id;
    closedRef.current = sid;
    const at = performedAt(anchorRef.current, performance.now(), PROCESS_ID, Date.now()).epochMs;
    const cmd = closeCommand(Crypto.randomUUID(), 'SESSION_ABANDON', sid, at);
    const cleared = apply({ type: 'RESET' });
    setPaused(false);
    setMission(null);
    setNotice('Séance abandonnée. Les séries faites restent enregistrées ; la séance ne comptera pas.');
    void journalRef.current?.enqueue(cmd, cleared).then(() => engineRef.current?.kick()).catch(() => undefined);
  }, [apply, cancelRestNotification, metric]);

  const requestExit = useCallback(() => {
    const s = stateRef.current;
    const message = exitMessage(Object.keys(s.done).length, s.plan?.sets.length ?? 0);
    if (!showNativeExitSheet(message, onExitChoice)) setExitOpen(true);
  }, [onExitChoice]);

  // ── PLAT-01 — Android hardware back: never leaves the app during a workout ──
  useEffect(() => {
    const sub = BackHandler.addEventListener('hardwareBackPress', () => {
      if (accountView) {
        if (accountView === 'preferences' || accountView === 'first-use-preferences') { preferencesExit.current?.(); return true; }
        if (!accountFlight.current) { setAccountView(null); setAccountOutcome(null); }
        return true;
      }
      const s = stateRef.current;
      const action = backAction({
        screen: screen === 'OWNERSHIP' ? 'LOGIN' : screen,
        inWorkout: s.phase === 'SET' || s.phase === 'REST',
        paused,
        sheetOpen: exitOpen || lab || signOutBlocked !== null,
      });
      if (action === 'exit-sheet') requestExit();
      if (action === 'close-sheet') {
        if (exitOpen) onExitChoice('cancel');
        setLab(false);
        setSignOutBlocked(null);
      }
      return action !== 'system';
    });
    return () => sub.remove();
  }, [accountView, screen, paused, exitOpen, lab, signOutBlocked, requestExit, onExitChoice]);

  const resume = useCallback(() => {
    setPaused(false);
    const s = stateRef.current;
    if (s.phase === 'REST' && s.rest) reschedule(s, Date.now());
  }, [reschedule]);

  const resumeFromServer = useCallback(async () => {
    if (mission?.state !== 'RESUME' || sessionActionInFlight.current) return;
    if(mission.session.template_slug==='science:v3:first-session'){
      if(!planV3?.active){setNotice('Cette séance demande le contrat d’exécution V3.');return;}
      await planV3.load();
      if(planV3.active&&planV3.state?.execution?.session_id===mission.session.id)setPlanV3Open(true);
      else setNotice('La reprise de cette séance reste à vérifier.');
      return;
    }
    const generation=auth.revision,target=journalRef.current;
    const current=()=>appAlive.current&&generation===auth.revision&&target===journalRef.current;
    sessionActionInFlight.current = true;
    setBusy(true);
    try {
      const plan = await fetchExecution(mission.session.id);
      const restored = target ? await target.restore() : { sets: [], outbox: [] };
      if(!current()||plan.session_id!==mission.session.id)return;
      const local = stateRef.current;
      const next=reconcileSubstitutions(stateFromServer(plan, local.phase === 'MISSION' ? null : local, restored.sets, Date.now()), restored.outbox);
      await target?.beginLegacy?.(next,current);
      if(!current())return;
      setPlanV3Open(false);
      apply({ type: 'RESTORE', state: next });
      setPaused(false);
      setOffline(false);
    } catch {
      setOffline(true);
    } finally {
      sessionActionInFlight.current = false;
      setBusy(false);
    }
  }, [apply, auth, fetchExecution, mission, planV3]);

  const signOut = useCallback(async () => {
    // §8.4 — no set may disappear as a side effect of signing out: while a
    // command is still unsent, the sign-out waits. (A REFUSED command stays in
    // the journal, never sent again automatically, so it does not block.)
    const revision = auth.revision;
    const unsent = ((await journalRef.current?.outboxRows()) ?? []).filter((r) => r.state !== 'failed').length;
    if (revision !== auth.revision || !appAlive.current) return;
    if (unsent > 0) {
      setLab(false);
      setNotice(null);
      setSignOutBlocked(unsent);
      void engineRef.current?.kick();
      return;
    }
    setLab(false);
    cancelRestNotification();
    if (undoTimer.current) clearTimeout(undoTimer.current); undoTimer.current = null; setUndo(null);
    engineRef.current?.stop(); engineRef.current = null;
    journalRef.current = null; setJournal(null);
    apply({ type: 'RESET' }); setServerSets({}); setSubstitutions({}); setBilanContext(null); setNext(null);
    const signingOut = auth.logout();
    const logoutRevision = auth.revision;
    await signingOut;
    if (logoutRevision !== auth.revision || !appAlive.current) return;
    ownershipFlight.current = null; setOwnershipChecking(false);
    accountFlight.current = false; setBusy(false); setAccountView(null); setAccountOutcome(null);
    setAccount(null);
    setMission(null);
    setScreen('LOGIN');
  }, [apply, auth, cancelRestNotification]);

  const closeBilan = useCallback(() => {
    apply({ type: 'RESET' });
    setNext(null);
    if (!auth.signedIn) {
      setScreen('LOGIN');
      return;
    }
    void loadMission();
  }, [apply, auth, loadMission]);

  // ── screens ────────────────────────────────────────────────────────────────
  const openJournalSheet = () => setLab(true);
  const currentBilan = bilanContext && bilanContext.sessionId === state.plan?.session_id ? bilanContext : null;
  let body: React.ReactNode = null;
  // MOB-01 — login, resume priority and first space go through the tested rule (spec `mobile/navigation-shell`)
  const opening = initialSpace({ authPending: screen === 'BOOT', signedIn: screen === 'APP', openWorkout: mission?.state === 'RESUME' });
  const openWeb = (path: string) => { if (API_URL) void Linking.openURL(`${API_URL.replace(/\/+$/, '')}${path}`); };
  const privacy = PRIVACY_URL?.startsWith('https://') ? () => { void Linking.openURL(PRIVACY_URL); } : undefined;
  const leaveAccountView = () => { if (!accountFlight.current) { setAccountView(null); setAccountOutcome(null); } };
  const reconnectAccount = () => {
    if (accountFlight.current) return;
    // Keep owned pending workout facts in their partition during reauthentication.
    engineRef.current?.stop(); engineRef.current = null; journalRef.current = null; setJournal(null);
    apply({ type: 'RESET' }); setAccount(null); setMission(null); setNext(null); setBilanContext(null); setServerSets({});
    setAccountView(null); setAccountOutcome(null); setScreen('LOGIN');
  };
  const accountSettings = <AccountSettingsScreen username={account} onPassword={() => { setAccountOutcome(null); setAccountView('password'); }}
    onPreferences={() => setAccountView('preferences')}
    onExport={API_URL ? () => openWeb('/export') : undefined} onPrivacy={privacy}
    onWebProfile={API_URL ? () => openWeb('/profile') : undefined} onSignOut={() => void signOut()} />;
  const continueAfterCreated = () => {
    const resume = state.phase === 'SET' || state.phase === 'REST' || mission?.state === 'RESUME';
    if (!accountFlight.current) setAccountView(screen === 'APP' && !resume ? 'first-use' : null);
  };
  const accountOverlay = screen !== 'APP' ? null : accountView === 'first-use'
    ? planV3?.active ? <PlanV3Host controller={planV3} onExit={()=>{setPlanV3Open(false);leaveAccountView();}} onPreferences={()=>setAccountView('first-use-preferences')} onSync={async()=>{await engineRef.current?.kick();}}/> : <FirstUseScreen key={auth.revision} controller={firstUse} onPreferences={() => setAccountView('first-use-preferences')} onToday={leaveAccountView} onBack={leaveAccountView} />
    : accountView === 'preferences' || accountView === 'first-use-preferences'
    ? <TrainingPreferencesScreen key={auth.revision} client={preferencesClient} onClose={accountView === 'first-use-preferences' ? () => setAccountView('first-use') : leaveAccountView}
      onReconnect={reconnectAccount} registerExit={registerPreferencesExit} onWebProfile={API_URL ? () => openWeb('/profile') : undefined} />
    : accountView === 'password'
      ? <PasswordScreen busy={busy} outcome={accountOutcome} onSubmit={(input) => void changePassword(input)} onBack={leaveAccountView} onLogin={reconnectAccount} />
      : accountView === 'password-done'
        ? <AccountResultScreen kind="password" onContinue={leaveAccountView} /> : null;
  if (accountView === 'created') {
    body = <AccountResultScreen kind="created" onContinue={continueAfterCreated} />;
  } else if (accountView === 'signup' && screen === 'LOGIN') {
    body = <SignupScreen busy={busy} outcome={accountOutcome} onSubmit={(input) => void register(input)} onBack={leaveAccountView} onLogin={leaveAccountView} />;
  } else if (screen === 'BOOT') {
    body = <BootScreen />;
  } else if (screen === 'OWNERSHIP') {
    body = <JournalOwnershipScreen state={ownershipChecking ? 'checking' : 'offline'} onVerify={() => void verifyOwnership()} onChangeAccount={() => void signOut()} />;
  } else if (opening === 'login') {
    body = <LoginScreen error={loginError} busy={busy} onSubmit={(u, p) => void login(u, p)}
      onCreateAccount={() => { setAccountOutcome(null); setAccountView('signup'); }}
      onRecover={API_URL ? () => openWeb('/forgot-password') : undefined} onPrivacy={privacy} />;
  } else if (screen === 'APP' && planV3?.active && planV3Open && !accountView && state.phase!=='SET' && state.phase!=='REST') {
    body = <PlanV3Host controller={planV3} onExit={()=>setPlanV3Open(false)} onPreferences={()=>setAccountView('preferences')} onSync={async()=>{await engineRef.current?.kick();}}/>;
  } else if (screen === 'APP') {
    const inWorkout = state.phase === 'SET' || state.phase === 'REST';
    if (inWorkout && paused && state.plan) {
      const [name, subtitle] = state.plan.template_name.split(' — ');
      body = (
        <ResumeScreen
          name={name}
          subtitle={subtitle ?? null}
          position={localPosition(state)}
          note={offline ? 'Hors ligne : la séance continue sur l’appareil et se synchronise au retour du réseau.' : null}
          onResume={resume}
          onOpenJournal={openJournalSheet}
        />
      );
    } else if (inWorkout) {
      body = (
        <ExecutionScreen
          state={state}
          nowMs={now}
          reducedMotion={reducedMotion}
          onAdjust={(setId, field, delta) => {
            apply({ type: 'ADJUST', setId, field, delta });
            feedback.step();
          }}
          onSetValue={(setId, field, value) => apply({ type: 'SET_VALUE', setId, field, value })}
          onValidatePressIn={() => (pressInRef.current = performance.now())}
          onValidate={validate}
          onShift={shiftRest}
          onSkip={skip}
          onRequestSubstitute={requestSubstitute}
          onOpenLab={openJournalSheet}
          onRestPainted={onRestPainted}
          onSecondaryOpened={() => metric('SECONDARY-OPENED')}
          onExitRequested={requestExit}
          offline={sync.offline || offline}
          substitutionStateOf={(seId) => substitutions[seId]?.state==='resolved'?null:substitutions[seId]?.state ?? null}
          statusNote={substitutionNotice ? { text: substitutionNotice, alert: true } : statusNote({ ...sync, offline: sync.offline || offline })}
          serverStateOf={(setId) => serverSets[setId] === 'synced' || serverSets[setId] === 'refused' ? serverSets[setId] as 'synced' | 'refused' : null}
          onSkipSet={(setId) => skipWith({ type: 'SKIP_SET', setId, nowMs: Date.now() }, 'Série passée — elle ne sera pas comptée.')}
          onSkipExercise={() => skipWith({ type: 'SKIP_EXERCISE', nowMs: Date.now() }, 'Exercice passé — ses séries restantes ne seront pas comptées.')}
          undo={undo ? { text: undo.text, onUndo: takeBack } : null}
        />
      );
    } else if (state.phase === 'COMPLETE' && showed) {
      body = (
        <CompleteScreen
          state={state}
          performance={showed}
          serverStateOf={(setId) => serverSets[setId] ?? 'unknown'}
          history={currentBilan?.history ?? null}
          contextLine={currentBilan?.contextLine ?? null}
          sessionsPerWeek={currentBilan?.sessionsPerWeek ?? null}
          next={next}
          reducedMotion={reducedMotion}
          onClose={closeBilan}
          onOpenLab={openJournalSheet}
        />
      );
    } else if (opening === 'resume' && mission?.state === 'RESUME') {
      const p = mission.position;
      body = (
        <ResumeScreen
          name={mission.session.name}
          subtitle={mission.session.subtitle}
          position={p ? { exerciseIndex: p.exercise_index, exerciseTotal: p.exercise_total, setsDone: p.sets_done, setsTotal: p.sets_total, exerciseName: p.exercise_name } : null}
          note={offline ? 'Hors ligne : la reprise attend la connexion. Les séries gardées sur l’appareil restent conservées.' : null}
          busy={busy}
          onResume={() => void resumeFromServer()}
          onOpenJournal={openJournalSheet}
        />
      );
    } else {
      // MOB-01 — outside a workout the native shell is on screen; AUJOURD'HUI holds the MISSION or its quiet states
      let today: React.ReactNode;
      if (isStartable(mission)) {
        today = (
          <View style={{ flex: 1 }}>
            <MissionScreen
              mission={mission as unknown as Mission}
              busy={busy}
              onStart={(slug) => void start(slug)}
              onOpenLab={openJournalSheet}
              onSecondaryOpened={() => metric('SECONDARY-OPENED')}
            />
          </View>
        );
      } else if (mission?.state === 'READY') {
        today = (
          <QuietScreen
            title={mission.template.name}
            text={`${mission.reason.phrase} Cette séance ne se suit pas encore dans l’application.`}
            choices={mission.alternatives.filter((a) => a.executable).map((a) => ({
              key: a.slug, title: a.name, detail: a.phrase, onPress: () => void start(a.slug),
            }))}
            onOpenJournal={openJournalSheet}
          />
        );
      } else if (mission?.state === 'NO_MISSION') {
        today = (
          <QuietScreen
            title="Rien à proposer"
            text="Aucune séance n’est faisable avec l’environnement déclaré aujourd’hui."
            action={{ label: 'Actualiser', onPress: () => void loadMission() }}
            onOpenJournal={openJournalSheet}
          />
        );
      } else {
        today = (
          <QuietScreen
            title={offline ? 'Hors ligne' : 'Un instant'}
            text={notice ?? (offline ? 'La mission du jour arrive dès que la connexion revient. Rien de ce qui est enregistré ici n’est perdu.' : 'AUREN prépare la mission du jour.')}
            action={{ label: 'Réessayer', onPress: () => void loadMission() }}
            onOpenJournal={openJournalSheet}
          />
        );
      }
      body = (
        <ShellProvider value={{ today, openJournal: openJournalSheet, siteUrl: API_URL, account: accountSettings }}>
          <ExpoRoot context={shellRoutes} />
        </ShellProvider>
      );
    }
  }

  return (
    <SafeAreaProvider>
      <StatusBar style="light" />
      <View style={styles.root}>
        <View testID="connected-content" pointerEvents={accountOverlay ? 'none' : 'auto'}
          accessibilityElementsHidden={!!accountOverlay} importantForAccessibility={accountOverlay ? 'no-hide-descendants' : 'auto'}
          style={{ flex: 1, display: accountOverlay ? 'none' : 'flex' }}>
          {body}
        </View>
        {accountOverlay}
        <Sheet visible={signOutBlocked !== null} title="Déconnexion en attente" onClose={() => setSignOutBlocked(null)}>
          <SheetRow
            title={`${signOutBlocked ?? 0} enregistrement${(signOutBlocked ?? 0) > 1 ? 's' : ''} pas encore envoyé${(signOutBlocked ?? 0) > 1 ? 's' : ''} à AUREN`}
            detail="La déconnexion attend qu’ils soient envoyés : se déconnecter maintenant les laisserait sans compte. Ils partent dès que la connexion le permet."
          />
        </Sheet>
        <Sheet visible={exitOpen} title="Quitter la séance" onClose={() => onExitChoice('cancel')}>
          {EXIT_OPTIONS.map((o) => (
            <SheetRow key={o.choice} title={o.label} onPress={() => onExitChoice(o.choice)} />
          ))}
        </Sheet>
        <LabSheet
          visible={lab}
          journal={journal}
          plannedSets={state.plan?.sets.length ?? null}
          reduceMotionEnabled={reducedMotion}
          onClose={() => setLab(false)}
          account={account}
          attention={sync.attention}
          onSignOut={() => void signOut()}
        />
      </View>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: color.field },
});
