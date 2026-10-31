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
import { StatusBar } from 'expo-status-bar';
import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { AppState, BackHandler, StyleSheet, View } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import { ApiFailure, createTransport } from './src/api/http';
import { ExecutionPlan, isStartable, ServerMission } from './src/api/types';
import { AuthSession } from './src/auth/authSession';
import { credentialStore } from './src/auth/credentialStore';
import { performedAt, TimeAnchor } from './src/domain/performedAt';
import { sessionPerformance } from './src/domain/performance';
import type { Mission } from './src/domain/types';
import { isElapsed, remainingMs } from './src/domain/timer';
import { Event, exerciseById, initialState, progress, reduce, setById, WorkoutState } from './src/domain/workout';
import { backAction } from './src/native/backAction';
import { deviceIdentity } from './src/native/deviceInfo';
import { deviceLabel } from './src/native/deviceLabel';
import { exitMessage, ExitChoice, EXIT_OPTIONS, showNativeExitSheet } from './src/native/exitSheet';
import { feedback } from './src/native/feedback';
import { keepAwake } from './src/native/keepAwake';
import { announce, useReducedMotion } from './src/native/motion';
import { restNotification } from './src/native/restNotification';
import { openJournal } from './src/storage/journal';
import type { Journal } from './src/storage/journalTypes';
import { closeCommand, OutboxRow, restoreState, setCommand, substituteCommand } from './src/storage/outbox';
import { stateFromServer } from './src/sync/reconcile';
import { routeFor } from './src/sync/routes';
import { IDLE, SyncEngine, SyncStatus } from './src/sync/syncEngine';
import { CompleteScreen } from './src/ui/CompleteScreen';
import { Sheet, SheetRow } from './src/ui/components';
import { ExecutionScreen } from './src/ui/ExecutionScreen';
import { LabSheet } from './src/ui/LabSheet';
import { LoginScreen } from './src/ui/LoginScreen';
import { MissionScreen } from './src/ui/MissionScreen';
import { QuietScreen } from './src/ui/QuietScreen';
import { ResumePosition, ResumeScreen } from './src/ui/ResumeScreen';
import { color } from './src/ui/theme';

const API_URL = process.env.EXPO_PUBLIC_API_URL ?? '';
const PROCESS_ID = Crypto.randomUUID();
const transport = createTransport(API_URL);
/** Before any server contact there is no anchor: every time claim is `estimated`. */
const NO_ANCHOR: TimeAnchor = { serverMs: 0, monoMs: 0, processId: 'none' };

type Screen = 'BOOT' | 'LOGIN' | 'APP';

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
  const [mission, setMission] = useState<ServerMission | null>(null);
  const [offline, setOffline] = useState(false);
  const [paused, setPaused] = useState(false);
  const [sync, setSync] = useState<SyncStatus>(IDLE);
  const [next, setNext] = useState<Mission | null>(null);
  const [exitOpen, setExitOpen] = useState(false);
  const [lab, setLab] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  /** §8.7 — per set, what the server said: acknowledged or refused (absent = not yet). */
  const [serverSets, setServerSets] = useState<Record<number, 'synced' | 'refused'>>({});
  const [signOutBlocked, setSignOutBlocked] = useState<number | null>(null);
  /** R10 / R12 — a skip can be taken back for a few seconds; nothing was written. */
  const [undo, setUndo] = useState<{ text: string; prev: WorkoutState } | null>(null);
  const undoTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const onStatus = useCallback((s: SyncStatus) => {
    setSync(s);
    void journalRef.current?.outboxRows().then((rows) => {
      const refused = rows.filter((r) => r.state === 'failed' && r.kind === 'SET_COMPLETION');
      if (!refused.length) return;
      setServerSets((prev) => {
        const next = { ...prev };
        for (const r of refused) next[Number(r.target.split('/')[1])] = 'refused';
        return next;
      });
    }).catch(() => undefined);
  }, []);

  const auth = useMemo(
    () => new AuthSession(transport, credentialStore, () => performance.now(), (iso, mono) => {
      anchorRef.current = { serverMs: Date.parse(iso), monoMs: mono, processId: PROCESS_ID };
    }),
    [],
  );

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

  // ── canonical state: the mission, and the open session if there is one ────
  const loadMission = useCallback(async () => {
    try {
      const m = await api<ServerMission>('/mission');
      setOffline(false);
      setMission(m);
      const local = stateRef.current;
      if (m.state === 'RESUME') {
        const plan = await fetchExecution(m.session.id);
        const rows = journalRef.current ? (await journalRef.current.restore()).sets : [];
        apply({ type: 'RESTORE', state: stateFromServer(plan, local.phase === 'MISSION' ? null : local, rows, Date.now()) });
        setPaused(true);
      } else if (local.phase === 'SET' || local.phase === 'REST') {
        // the server holds no open session: it was closed elsewhere (web) or by a
        // command already acknowledged. Pending commands stay visible in the journal.
        apply({ type: 'RESET' });
        setPaused(false);
      }
    } catch (e) {
      if (e instanceof ApiFailure && e.kind === 'http' && e.status === 401) {
        setScreen('LOGIN');
        return;
      }
      setOffline(true);
    }
  }, [api, apply, fetchExecution]);

  const onAck = useCallback((row: OutboxRow, response: unknown) => {
    metric('SYNC-ACK');
    metric('G-SYNC', Date.now() - row.created_at_ms);
    if ((response as { applied?: boolean } | null)?.applied === false) metric('SYNC-ACK-DUPLICATE');
    if (row.kind === 'SET_COMPLETION') {
      const setId = Number(row.target.split('/')[1]);
      setServerSets((prev) => ({ ...prev, [setId]: 'synced' }));
    }
    if (row.kind === 'SESSION_FINISH' || row.kind === 'SESSION_ABANDON') {
      void api<ServerMission>('/mission').then((m) => {
        if (isStartable(m)) setNext(m as unknown as Mission);
        if (stateRef.current.phase === 'MISSION') setMission(m);
      }).catch(() => undefined);
    }
    if (row.kind === 'SUBSTITUTE') {
      const p = JSON.parse(row.payload) as { session_id: number; se_id: number };
      const s = stateRef.current;
      if (s.plan?.session_id !== p.session_id) return;
      void fetchExecution(p.session_id).then(async (plan) => {
        const rows = journalRef.current ? (await journalRef.current.restore()).sets : [];
        const cur = stateRef.current;
        const merged = stateFromServer(plan, cur, rows, Date.now());
        const { [p.se_id]: _done, ...rest } = merged.requiresSync;
        apply({ type: 'RESTORE', state: { ...merged, requiresSync: rest } });
      }).catch(() => undefined);
    }
  }, [api, apply, fetchExecution, metric]);

  // ── boot: journal first (the workout survives anything), then the server ──
  useEffect(() => {
    let alive = true;
    const boot = async () => {
      const j = await openJournal('auren.db');
      if (!alive) return;
      journalRef.current = j;
      setJournal(j);
      const send = (row: OutboxRow) => {
        const r = routeFor(row);
        return api(r.path, { method: r.method, body: r.body });
      };
      engineRef.current = new SyncEngine(j, send, onStatus, onAck);
      const r = await j.restore();
      if (r.snapshot && r.snapshot.phase !== 'MISSION') {
        const restored = restoreState(r.snapshot, r.sets);
        apply({ type: 'RESTORE', state: restored });
        if (restored.phase !== 'COMPLETE') setPaused(true);
        await j.recordMetric('RELAUNCH-RESTORED-SETS', Object.values(restored.done).filter((d) => d.local === 'saved_local').length);
      }
      if (!(await auth.hasCredential())) {
        setScreen('LOGIN');
        return;
      }
      setScreen('APP');
      const outcome = await auth.refresh();
      if (outcome === 'invalid') {
        setScreen('LOGIN');
        return;
      }
      if (outcome === 'network') {
        setOffline(true);
        return;
      }
      await engineRef.current.kick();
      await loadMission();
    };
    boot().catch(() => setScreen('LOGIN'));
    const stop = restNotification.onDelivery((late) => metric('NOTIF-LATENESS', late));
    return () => {
      alive = false;
      stop();
      engineRef.current?.stop();
    };
    // boot runs once; the callbacks it captures are stable
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // back in the foreground: drain, and re-read the canonical state between workouts
  useEffect(() => {
    const sub = AppState.addEventListener('change', (s) => {
      if (s !== 'active') return;
      resumedRef.current = true;
      if (!auth.signedIn && screen !== 'APP') return;
      void engineRef.current?.kick();
      if (stateRef.current.phase === 'MISSION') void loadMission();
    });
    return () => sub.remove();
  }, [auth, loadMission, screen]);

  useEffect(() => {
    const t = setTimeout(() => journalRef.current?.saveSnapshot(state).catch(() => undefined), 250);
    return () => clearTimeout(t);
  }, [state]);

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
    setBusy(true);
    setLoginError(null);
    const outcome = await auth.login(username, password, deviceLabel(deviceIdentity()));
    setBusy(false);
    if (outcome !== 'ok') {
      setLoginError(outcome);
      return;
    }
    setAccount(username);
    setScreen('APP');
    await engineRef.current?.kick();
    await loadMission();
  }, [auth, loadMission]);

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
    if (!mission || mission.state !== 'READY' || busy) return;
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
      anchorOn(plan.server_now);
      closedRef.current = null;
      apply({ type: 'START', plan, nowMs: Date.now() });
      setPaused(false);
      void restNotification.prepare().catch(() => undefined);
    } catch (e) {
      feedback.refused();
      if (e instanceof ApiFailure && e.kind === 'http' && e.code === 'session_open') await loadMission();
      else if (e instanceof ApiFailure && e.code === 'start_blocked') setNotice('Cette séance n’est pas faisable avec l’équipement déclaré.');
      else setNotice('AUREN est injoignable : le démarrage attend la connexion.');
    } finally {
      setBusy(false);
    }
  }, [anchorOn, api, apply, busy, loadMission, mission]);

  const validate = useCallback((setId: number) => {
    const before = stateRef.current;
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
    const s = apply({ type: 'REQUEST_SUBSTITUTE', seId, substitute: name });
    feedback.step();
    if (!s.plan) return;
    const cmd = substituteCommand(Crypto.randomUUID(), s.plan.session_id, seId, name);
    void journalRef.current?.enqueue(cmd, s).then(() => engineRef.current?.kick()).catch(() => undefined);
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
    setUndo({ text, prev: before });
    undoTimer.current = setTimeout(() => setUndo(null), UNDO_MS);
  }, [apply, metric]);

  const takeBack = useCallback(() => {
    if (!undo) return;
    if (undoTimer.current) clearTimeout(undoTimer.current);
    apply({ type: 'RESTORE', state: undo.prev });
    setUndo(null);
    metric('SKIP-UNDONE');
  }, [apply, metric, undo]);

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
      const s = stateRef.current;
      const action = backAction({
        screen,
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
  }, [screen, paused, exitOpen, lab, signOutBlocked, requestExit, onExitChoice]);

  const resume = useCallback(() => {
    setPaused(false);
    const s = stateRef.current;
    if (s.phase === 'REST' && s.rest) reschedule(s, Date.now());
  }, [reschedule]);

  const resumeFromServer = useCallback(async () => {
    if (mission?.state !== 'RESUME') return;
    try {
      const plan = await fetchExecution(mission.session.id);
      const rows = journalRef.current ? (await journalRef.current.restore()).sets : [];
      const local = stateRef.current;
      apply({ type: 'RESTORE', state: stateFromServer(plan, local.phase === 'MISSION' ? null : local, rows, Date.now()) });
      setPaused(false);
    } catch {
      setOffline(true);
    }
  }, [apply, fetchExecution, mission]);

  const signOut = useCallback(async () => {
    // §8.4 — no set may disappear as a side effect of signing out: while a
    // command is still unsent, the sign-out waits. (A REFUSED command stays in
    // the journal, never sent again automatically, so it does not block.)
    const unsent = ((await journalRef.current?.outboxRows()) ?? []).filter((r) => r.state !== 'failed').length;
    if (unsent > 0) {
      setLab(false);
      setNotice(null);
      setSignOutBlocked(unsent);
      void engineRef.current?.kick();
      return;
    }
    setLab(false);
    cancelRestNotification();
    await auth.logout();
    setAccount(null);
    setMission(null);
    setScreen('LOGIN');
  }, [auth, cancelRestNotification]);

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
  let body: React.ReactNode = null;
  if (screen === 'LOGIN') {
    body = <LoginScreen error={loginError} busy={busy} onSubmit={(u, p) => void login(u, p)} />;
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
          statusNote={statusNote({ ...sync, offline: sync.offline || offline })}
          serverStateOf={(setId) => serverSets[setId] ?? null}
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
          history={null}
          sessionsPerWeek={null}
          next={next}
          reducedMotion={reducedMotion}
          onClose={closeBilan}
          onOpenLab={openJournalSheet}
        />
      );
    } else if (mission?.state === 'RESUME') {
      const p = mission.position;
      body = (
        <ResumeScreen
          name={mission.session.name}
          subtitle={mission.session.subtitle}
          position={p ? { exerciseIndex: p.exercise_index, exerciseTotal: p.exercise_total, setsDone: p.sets_done, setsTotal: p.sets_total, exerciseName: p.exercise_name } : null}
          note={null}
          onResume={() => void resumeFromServer()}
          onOpenJournal={openJournalSheet}
        />
      );
    } else if (isStartable(mission)) {
      body = (
        <View style={{ flex: 1 }}>
          <MissionScreen
            mission={mission as unknown as Mission}
            onStart={(slug) => void start(slug)}
            onOpenLab={openJournalSheet}
            onSecondaryOpened={() => metric('SECONDARY-OPENED')}
          />
        </View>
      );
    } else if (mission?.state === 'READY') {
      body = (
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
      body = (
        <QuietScreen
          title="Rien à proposer"
          text="Aucune séance n’est faisable avec l’environnement déclaré aujourd’hui."
          action={{ label: 'Actualiser', onPress: () => void loadMission() }}
          onOpenJournal={openJournalSheet}
        />
      );
    } else {
      body = (
        <QuietScreen
          title={offline ? 'Hors ligne' : 'Un instant'}
          text={notice ?? (offline ? 'La mission du jour arrive dès que la connexion revient. Rien de ce qui est enregistré ici n’est perdu.' : 'AUREN prépare la mission du jour.')}
          action={{ label: 'Réessayer', onPress: () => void loadMission() }}
          onOpenJournal={openJournalSheet}
        />
      );
    }
  }

  return (
    <SafeAreaProvider>
      <StatusBar style="light" />
      <View style={styles.root}>
        {body}
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
