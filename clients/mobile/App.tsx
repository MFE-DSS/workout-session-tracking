/**
 * AUREN vNext — Sb_VNEXT_NATIVE_N0_EXPERIENCE_LAB.
 *
 * Lab only: no auth, no network, no production write. Fixtures come from the
 * canonical FastAPI services (scripts/generate_fixtures.py). The question this
 * app answers is the operator's: is this so much better that the legacy
 * workout UI can be abandoned?
 */
import * as Crypto from 'expo-crypto';
import { StatusBar } from 'expo-status-bar';
import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { AppState, StyleSheet, View } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import { performedAt, TimeAnchor } from './src/domain/performedAt';
import { sessionPerformance } from './src/domain/performance';
import { isElapsed, remainingMs } from './src/domain/timer';
import type { LabFixture } from './src/domain/types';
import { Event, exerciseById, initialState, reduce, setById, WorkoutState } from './src/domain/workout';
import rawFixture from './src/fixtures/lab_fixture.json';
import { LabSession, missionFor, nextAfter, planFor } from './src/lab/persona';
import type { Persona, Profile } from './src/lab/profile';
import { feedback } from './src/native/feedback';
import { keepAwake } from './src/native/keepAwake';
import { announce, useReducedMotion } from './src/native/motion';
import { restNotification } from './src/native/restNotification';
import { openJournal } from './src/storage/journal';
import type { Journal } from './src/storage/journalTypes';
import { restoreState, setCommand } from './src/storage/outbox';
import { CompleteScreen } from './src/ui/CompleteScreen';
import { ExecutionScreen } from './src/ui/ExecutionScreen';
import { LabSheet } from './src/ui/LabSheet';
import { MissionScreen } from './src/ui/MissionScreen';
import { OnboardingFlow } from './src/ui/OnboardingFlow';
import { color } from './src/ui/theme';
import { Tutorial } from './src/ui/Tutorial';

const fixture = rawFixture as unknown as LabFixture;
const PROCESS_ID = Crypto.randomUUID();

/** Lab time anchor: in N0 there is no server, so the anchor is taken at boot. */
const ANCHOR: TimeAnchor = { serverMs: Date.now(), monoMs: performance.now(), processId: PROCESS_ID };

function useNow(active: boolean): number {
  const [now, setNow] = useState(Date.now());
  useEffect(() => {
    if (!active) return;
    setNow(Date.now());
    const id = setInterval(() => setNow(Date.now()), 200);
    return () => clearInterval(id);
  }, [active]);
  // returning to the foreground recomputes from the deadline immediately
  useEffect(() => {
    const sub = AppState.addEventListener('change', (s) => s === 'active' && setNow(Date.now()));
    return () => sub.remove();
  }, []);
  return now;
}

export default function App() {
  const [state, setState] = useState<WorkoutState>(initialState);
  const stateRef = useRef(state);
  const journalRef = useRef<Journal | null>(null);
  const [journal, setJournal] = useState<Journal | null>(null);
  const [lab, setLab] = useState(false);
  const notifRef = useRef<string | null>(null);
  const pressInRef = useRef<number | null>(null);
  /** true from a return to the foreground until the next rest-end detection */
  const resumedRef = useRef(false);
  const reducedMotion = useReducedMotion();
  // ── lab user (D13): who holds the phone decides which canonical fixture applies
  const [booted, setBooted] = useState(false);
  const [persona, setPersona] = useState<Persona | null>(null);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [sessions, setSessions] = useState<LabSession[]>([]);

  const apply = useCallback((event: Event): WorkoutState => {
    const next = reduce(stateRef.current, event);
    stateRef.current = next;
    setState(next);
    return next;
  }, []);

  /** PHYSICAL_DEVICE_GATE evidence: every lab metric goes through here. */
  const metric = useCallback((name: string, value = 1) => {
    void journalRef.current?.recordMetric(name, value).catch(() => undefined);
  }, []);

  useEffect(() => {
    const sub = AppState.addEventListener('change', (s) => {
      if (s === 'active') resumedRef.current = true;
    });
    return () => sub.remove();
  }, []);

  // ── boot: open the journal, restore whatever survived the last process ────
  useEffect(() => {
    let alive = true;
    const boot = async () => {
      const j = await openJournal();
      if (!alive) return;
      journalRef.current = j;
      setJournal(j);
      setPersona(await j.getLab<Persona>('persona'));
      setProfile(await j.getLab<Profile>('profile'));
      setSessions((await j.getLab<LabSession[]>('sessions')) ?? []);
      setBooted(true);
      const r = await j.restore();
      if (r.snapshot && r.snapshot.phase !== 'MISSION') {
        const restored = restoreState(r.snapshot, r.sets);
        apply({ type: 'RESTORE', state: restored });
        // force-kill proof: how many validated sets came back from the journal
        await j.recordMetric('RELAUNCH-RESTORED-SETS', Object.values(restored.done).filter((d) => d.local === 'saved_local').length);
      }
    };
    boot().catch(() => {
      setJournal(null);
      setBooted(true);
    });
    const stop = restNotification.onDelivery((late) => metric('NOTIF-LATENESS', late));
    return () => {
      alive = false;
      stop();
    };
  }, [apply, metric]);

  // ── persist the instrument (validation snapshots ride their own transaction) ─
  useEffect(() => {
    const t = setTimeout(() => journalRef.current?.saveSnapshot(state).catch(() => undefined), 250);
    return () => clearTimeout(t);
  }, [state.phase, state.cursorSetId, state.rest?.deadlineMs, state.requiresSync, state]);

  // ── keep the screen awake during the workout only ─────────────────────────
  useEffect(() => {
    if (state.phase === 'SET' || state.phase === 'REST') keepAwake.enable();
    else keepAwake.disable();
    if (state.phase === 'COMPLETE') metric('SESSION-COMPLETED');
  }, [state.phase, metric]);

  // ── the deadline is the truth; the tick only redraws and detects the end ───
  const now = useNow(state.phase === 'REST');
  useEffect(() => {
    const s = stateRef.current;
    if (s.phase !== 'REST' || !s.rest || !isElapsed(s.rest, now)) return;
    const opening = s.rest.after.kind === 'REST_THEN_EXERCISE';
    // timer evidence: how late the END was detected after the deadline, split
    // between an app that stayed in front and one that came back to it
    metric(resumedRef.current ? 'REST-END-LATENESS-RESUME' : 'REST-END-LATENESS-FOREGROUND', now - s.rest.deadlineMs);
    resumedRef.current = false;
    metric(opening ? 'AUTO-NEXT-EXERCISE' : 'AUTO-NEXT-SET');
    const next = apply({ type: 'REST_END', nowMs: now });
    notifRef.current = null; // delivered (or about to be) by the OS — never cancel a past one
    if (AppState.currentState === 'active') {
      feedback.restDone();
      if (opening) setTimeout(feedback.nextExercise, 380);
    }
    const ex = next.plan && next.cursorSetId !== null ? exerciseById(next.plan, setById(next.plan, next.cursorSetId)!.se_id) : undefined;
    announce(opening && ex ? `Repos terminé. Exercice suivant : ${ex.executed_name}` : 'Repos terminé. Série suivante.');
  }, [now, apply, metric]);

  // ── engine V2, ruling 11: what the session showed (no score), and its place in the history ─
  const showed = useMemo(
    () => (state.phase === 'COMPLETE' && state.plan ? sessionPerformance(state.plan, state.done, state.requiresSync) : null),
    [state.phase, state.plan, state.done, state.requiresSync],
  );
  const sessionId = state.startedMs ?? 0;
  const before = useMemo(() => sessions.filter((s) => s.id !== sessionId), [sessions, sessionId]);
  useEffect(() => {
    if (!showed || !state.plan || sessions.some((s) => s.id === sessionId)) return;
    const next = [...sessions, { id: sessionId, atMs: state.completedMs ?? Date.now(), slug: state.plan.template_slug }];
    setSessions(next);
    void journalRef.current?.setLab('sessions', next).catch(() => undefined);
    metric('SESSION-RECORDS', showed.records.length);
  }, [showed, sessions, sessionId, state.plan, state.completedMs, metric]);

  // ── handlers ───────────────────────────────────────────────────────────────
  const start = useCallback((slug: string, as: Persona | null = persona) => {
    const plan = planFor(fixture, as, sessions, slug);
    if (!plan) return feedback.refused();
    apply({ type: 'START', plan, nowMs: Date.now() });
    void restNotification.prepare().catch(() => undefined);
  }, [apply, persona, sessions]);

  const finishOnboarding = useCallback((p: Profile) => {
    if (!p.slug) return feedback.refused();
    const as: Persona = { kind: 'newcomer', family: p.family, slug: p.slug };
    setProfile(p);
    setPersona(as);
    void journalRef.current?.setLab('profile', p).catch(() => undefined);
    void journalRef.current?.setLab('persona', as).catch(() => undefined);
    metric('ONBOARDING-DONE');
    start(p.slug, as);
  }, [metric, start]);

  const finishTutorial = useCallback(() => {
    if (!profile) return;
    const p = { ...profile, tutorialDone: true };
    setProfile(p);
    void journalRef.current?.setLab('profile', p).catch(() => undefined);
  }, [profile]);

  const switchToSeeded = useCallback(() => {
    const as: Persona = { kind: 'seeded' };
    void restNotification.cancel(notifRef.current);
    notifRef.current = null;
    setPersona(as);
    void journalRef.current?.setLab('persona', as).catch(() => undefined);
    apply({ type: 'RESET' });
    setLab(false);
  }, [apply]);

  /** One pending "rest over" notification at a time, always matching the deadline. */
  const reschedule = useCallback((s: WorkoutState, nowMs: number) => {
    if (!s.rest || !s.plan) return;
    const after = s.rest.after;
    const nextEx = after.kind === 'BILAN' ? undefined : exerciseById(s.plan, setById(s.plan, after.set_id)!.se_id);
    const previous = notifRef.current;
    notifRef.current = null;
    const seconds = remainingMs(s.rest, nowMs) / 1000;
    const run = async () => {
      await restNotification.cancel(previous);
      notifRef.current = await restNotification.schedule(seconds, nextEx ? nextEx.executed_name : 'Série suivante');
      if (notifRef.current) metric('NOTIF-REQUESTED', seconds);
    };
    void run();
  }, [metric]);

  const validate = useCallback((setId: number) => {
    const before = stateRef.current;
    const at = performedAt(ANCHOR, performance.now(), PROCESS_ID, Date.now());
    const nowMs = Date.now();
    const next = apply({ type: 'VALIDATED', setId, performedAt: at, nowMs });
    if (next === before) {
      feedback.refused();
      return;
    }
    const plan = next.plan!;
    const done = next.done[setId];
    const set = setById(plan, setId)!;
    metric('SET-VALIDATED');
    if (next.phase === 'REST' && next.rest) reschedule(next, nowMs);
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
    const commit = async () => {
      let ms: number;
      try {
        ms = await j.commitValidation(row, cmd, next);
      } catch (e) {
        // the lab must say WHY a set was not saved, not only that it was not
        console.warn('[N0] set commit failed', setId, e instanceof Error ? e.message : String(e));
        metric('COMMIT-FAILED');
        apply({ type: 'LOCAL_COMMIT', setId, ok: false });
        feedback.failed();
        return;
      }
      apply({ type: 'LOCAL_COMMIT', setId, ok: true });
      feedback.setSaved();
      await j.recordMetric('G-LOCAL', ms).catch(() => undefined);
    };
    void commit();
  }, [apply, reschedule, metric]);

  const onRestPainted = useCallback(() => {
    const t0 = pressInRef.current;
    if (t0 === null) return;
    pressInRef.current = null;
    requestAnimationFrame(() => journalRef.current?.recordMetric('G-VAL', performance.now() - t0).catch(() => undefined));
  }, []);

  const shiftRest = useCallback((deltaMs: number) => {
    const nowMs = Date.now();
    const next = apply({ type: 'REST_SHIFT', deltaMs, nowMs });
    if (!next.rest) return;
    feedback.step();
    reschedule(next, nowMs);
  }, [apply, reschedule]);

  const skip = useCallback(() => {
    const opening = stateRef.current.rest?.after.kind === 'REST_THEN_EXERCISE';
    void restNotification.cancel(notifRef.current);
    notifRef.current = null;
    metric('REST-SKIP');
    apply({ type: 'REST_END', nowMs: Date.now() });
    if (opening) feedback.nextExercise();
  }, [apply, metric]);

  /** A secondary sheet opened = a navigation decision the operator had to make. */
  const secondaryOpened = useCallback(() => metric('SECONDARY-OPENED'), [metric]);

  const reset = useCallback(() => {
    void restNotification.cancel(notifRef.current);
    notifRef.current = null;
    void journalRef.current?.reset().catch(() => undefined);
    setPersona(null);
    setProfile(null);
    setSessions([]);
    apply({ type: 'RESET' });
    setLab(false);
  }, [apply]);

  const mission = missionFor(fixture, persona, sessions);
  const showTutorial = state.phase === 'SET' && persona?.kind === 'newcomer' && profile !== null && !profile.tutorialDone;

  let screen: React.ReactNode;
  if (!booted) {
    screen = null;
  } else if (state.phase === 'MISSION' && !mission) {
    screen = <OnboardingFlow families={fixture.onboarding.families} onDone={finishOnboarding} />;
  } else if (state.phase === 'MISSION' && mission) {
    screen = <MissionScreen mission={mission} onStart={(slug) => start(slug)} onOpenLab={() => setLab(true)} onSecondaryOpened={secondaryOpened} />;
  } else if (state.phase === 'COMPLETE' && showed) {
    screen = (
      <CompleteScreen
        state={state}
        performance={showed}
        history={before}
        sessionsPerWeek={persona?.kind === 'newcomer' ? profile?.sessionsPerWeek ?? null : null}
        next={nextAfter(fixture, persona, before)}
        reducedMotion={reducedMotion}
        onClose={() => apply({ type: 'RESET' })}
        onOpenLab={() => setLab(true)}
      />
    );
  } else {
    screen = (
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
        onRequestSubstitute={(seId, name) => {
          // REQUIRES_SYNC: recorded as a request, never applied on the device.
          apply({ type: 'REQUEST_SUBSTITUTE', seId, substitute: name });
          feedback.step();
        }}
        onOpenLab={() => setLab(true)}
        onRestPainted={onRestPainted}
        onSecondaryOpened={secondaryOpened}
      />
    );
  }

  return (
    <SafeAreaProvider>
      <StatusBar style="light" />
      <View style={styles.root}>
        {screen}
        {showTutorial ? <Tutorial onDone={finishTutorial} /> : null}
        <LabSheet
          visible={lab}
          journal={journal}
          plannedSets={state.plan?.sets.length ?? null}
          reduceMotionEnabled={reducedMotion}
          onClose={() => setLab(false)}
          onReset={reset}
          onSeeded={switchToSeeded}
        />
      </View>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: color.field },
});
