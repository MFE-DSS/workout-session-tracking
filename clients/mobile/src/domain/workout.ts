/**
 * The training instrument's state machine (N0 §9).
 *
 *   MISSION → SET → REST → SET → REST(next exercise) → SET → … → COMPLETE
 *
 * Pure: no I/O, no clock reads (time comes in on the events). It FOLLOWS the
 * server's transition table (`plan.on_complete`); it never computes the next
 * set or the next exercise itself — that would be domain logic on the device.
 * A non-nominal mutation (substitution) does not mutate the plan: it marks the
 * exercise `REQUIRES_SYNC` and waits for the server.
 */
import { RestClock, shift } from './timer';
import type { PerformedAt } from './performedAt';
import type { PlanExercise, PlanSet, SessionPlan, Transition } from './types';

export type Draft = { weight: number | null; reps: number | null };

export type DoneSet = {
  weight: number;
  reps: number;
  performedAt: PerformedAt;
  /** Local durability: `pending_local` until the SQLite commit returns. */
  local: 'pending_local' | 'saved_local' | 'not_saved';
};

export type Phase = 'MISSION' | 'SET' | 'REST' | 'COMPLETE';

export type WorkoutState = {
  phase: Phase;
  plan: SessionPlan | null;
  cursorSetId: number | null;
  drafts: Record<number, Draft>;
  done: Record<number, DoneSet>;
  rest: (RestClock & { after: Transition; fromSetId: number }) | null;
  requiresSync: Record<number, { substitute: string }>;
  /**
   * R10 / R12 — sets the user chose NOT to do. A skipped set is simply not done
   * (the product's existing meaning of an unvalidated set): nothing is written.
   * Optional: snapshots written before this field existed restore without it.
   */
  skipped?: Record<number, true>;
  startedMs: number | null;
  completedMs: number | null;
};

export const initialState: WorkoutState = {
  phase: 'MISSION',
  plan: null,
  cursorSetId: null,
  drafts: {},
  done: {},
  rest: null,
  requiresSync: {},
  skipped: {},
  startedMs: null,
  completedMs: null,
};

export type Event =
  | { type: 'START'; plan: SessionPlan; nowMs: number }
  | { type: 'ADJUST'; setId: number; field: keyof Draft; delta: number }
  | { type: 'SET_VALUE'; setId: number; field: keyof Draft; value: number | null }
  | { type: 'VALIDATED'; setId: number; performedAt: PerformedAt; nowMs: number }
  | { type: 'LOCAL_COMMIT'; setId: number; ok: boolean }
  | { type: 'REST_SHIFT'; deltaMs: number; nowMs: number }
  | { type: 'REST_END'; nowMs: number }
  | { type: 'REQUEST_SUBSTITUTE'; seId: number; substitute: string }
  | { type: 'FINISH_NOW'; nowMs: number }
  | { type: 'SKIP_SET'; setId: number; nowMs: number }
  | { type: 'SKIP_EXERCISE'; nowMs: number }
  | { type: 'RESTORE'; state: WorkoutState }
  | { type: 'RESET' };

// ── read helpers (lookups into the plan, never derivations of it) ────────────

export function setById(plan: SessionPlan, setId: number): PlanSet | undefined {
  return plan.sets.find((s) => s.set_id === setId);
}

export function exerciseById(plan: SessionPlan, seId: number): PlanExercise | undefined {
  return plan.exercises.find((e) => e.se_id === seId);
}

export function setsOf(plan: SessionPlan, seId: number): PlanSet[] {
  return plan.sets.filter((s) => s.se_id === seId);
}

export function currentExercise(state: WorkoutState): PlanExercise | undefined {
  if (!state.plan || state.cursorSetId === null) return undefined;
  const set = setById(state.plan, state.cursorSetId);
  return set && exerciseById(state.plan, set.se_id);
}

/**
 * Presentation rule for the values shown in the dials (D6, LAB ONLY): the first
 * set of an exercise shows the server's prefill; a later set repeats the last
 * validated set of the same exercise. Nothing here is a training decision.
 */
export function draftFor(state: WorkoutState, setId: number): Draft {
  const existing = state.drafts[setId];
  if (existing) return existing;
  const plan = state.plan;
  const set = plan && setById(plan, setId);
  if (!plan || !set) return { weight: null, reps: null };
  const earlier = setsOf(plan, set.se_id)
    .filter((s) => s.index < set.index && state.done[s.set_id])
    .sort((a, b) => b.index - a.index)[0];
  if (earlier) {
    const d = state.done[earlier.set_id];
    return { weight: d.weight, reps: d.reps };
  }
  const ex = exerciseById(plan, set.se_id);
  return { weight: ex?.prefill.weight_kg ?? null, reps: ex?.prefill.reps ?? null };
}

/** Rest after a set of this exercise: the read model's value, else the plan default. */
export function restSecondsFor(plan: SessionPlan, seId: number | undefined): number {
  const ex = seId === undefined ? undefined : exerciseById(plan, seId);
  return ex?.rest_seconds ?? plan.rest_default_seconds;
}

export function canValidate(draft: Draft): boolean {
  return draft.weight !== null && draft.weight >= 0 && draft.reps !== null && draft.reps > 0;
}

const WEIGHT_STEP = 2.5;

function clampDraft(field: keyof Draft, value: number | null): number | null {
  if (value === null) return null;
  if (field === 'reps') return Math.max(1, Math.min(100, Math.round(value)));
  return Math.max(0, Math.min(1000, Math.round(value / 0.5) * 0.5));
}

/**
 * The not-done sets of the current exercise, from the cursor on — found by
 * following the SERVER's transitions while they stay in this exercise.
 */
export function remainingOfExercise(state: WorkoutState): number[] {
  const plan = state.plan;
  if (!plan || state.cursorSetId === null) return [];
  const seId = setById(plan, state.cursorSetId)?.se_id;
  const chain: number[] = [];
  let id: number | null = state.cursorSetId;
  while (id !== null && setById(plan, id)?.se_id === seId) {
    if (!state.done[id]) chain.push(id);
    const t: Transition = plan.on_complete[String(id)] ?? { kind: 'BILAN' };
    id = t.kind === 'BILAN' ? null : t.set_id;
  }
  return chain;
}

/**
 * Mark `setIds` as skipped and move the cursor where the server's table says
 * the LAST of them leads — no rest: nothing was performed, nothing to recover.
 */
function skipThrough(state: WorkoutState, setIds: number[], nowMs: number): WorkoutState {
  if (!state.plan || setIds.length === 0) return state;
  const skipped = { ...(state.skipped ?? {}) };
  for (const id of setIds) skipped[id] = true;
  const last = setIds[setIds.length - 1];
  const after: Transition = state.plan.on_complete[String(last)] ?? { kind: 'BILAN' };
  if (after.kind === 'BILAN') {
    return { ...state, skipped, phase: 'COMPLETE', rest: null, cursorSetId: null, completedMs: nowMs };
  }
  return { ...state, skipped, phase: 'SET', rest: null, cursorSetId: after.set_id };
}

// ── reducer ───────────────────────────────────────────────────────────────

export function reduce(state: WorkoutState, event: Event): WorkoutState {
  switch (event.type) {
    case 'START':
      return {
        ...initialState,
        phase: 'SET',
        plan: event.plan,
        cursorSetId: event.plan.sets[0]?.set_id ?? null,
        startedMs: event.nowMs,
      };

    case 'ADJUST': {
      const d = draftFor(state, event.setId);
      const step = event.field === 'weight' ? WEIGHT_STEP : 1;
      const base = d[event.field] ?? 0;
      const value = clampDraft(event.field, base + event.delta * step);
      return { ...state, drafts: { ...state.drafts, [event.setId]: { ...d, [event.field]: value } } };
    }

    case 'SET_VALUE': {
      const d = draftFor(state, event.setId);
      const value = clampDraft(event.field, event.value);
      return { ...state, drafts: { ...state.drafts, [event.setId]: { ...d, [event.field]: value } } };
    }

    case 'VALIDATED': {
      if (!state.plan || state.phase !== 'SET' || state.cursorSetId !== event.setId) return state;
      const d = draftFor(state, event.setId);
      if (!canValidate(d)) return state;
      const done: DoneSet = {
        weight: d.weight as number,
        reps: d.reps as number,
        performedAt: event.performedAt,
        local: 'pending_local',
      };
      const after = state.plan.on_complete[String(event.setId)] ?? { kind: 'BILAN' };
      const next = { ...state, done: { ...state.done, [event.setId]: done } };
      if (after.kind === 'BILAN') {
        return { ...next, phase: 'COMPLETE', rest: null, cursorSetId: null, completedMs: event.nowMs };
      }
      const seId = setById(state.plan, event.setId)?.se_id;
      const durationMs = restSecondsFor(state.plan, seId) * 1000;
      return {
        ...next,
        phase: 'REST',
        rest: {
          startedMs: event.nowMs,
          deadlineMs: event.nowMs + durationMs,
          after,
          fromSetId: event.setId,
        },
      };
    }

    case 'LOCAL_COMMIT': {
      const d = state.done[event.setId];
      if (!d) return state;
      const local = event.ok ? 'saved_local' : 'not_saved';
      return { ...state, done: { ...state.done, [event.setId]: { ...d, local } } };
    }

    case 'REST_SHIFT':
      if (state.phase !== 'REST' || !state.rest) return state;
      return { ...state, rest: { ...state.rest, ...shift(state.rest, event.deltaMs, event.nowMs) } };

    case 'REST_END': {
      if (state.phase !== 'REST' || !state.rest) return state;
      const after = state.rest.after;
      if (after.kind === 'BILAN') return state;
      return { ...state, phase: 'SET', rest: null, cursorSetId: after.set_id };
    }

    case 'REQUEST_SUBSTITUTE':
      return {
        ...state,
        requiresSync: { ...state.requiresSync, [event.seId]: { substitute: event.substitute } },
      };

    case 'SKIP_SET':
      if (!state.plan || state.phase !== 'SET' || state.cursorSetId !== event.setId) return state;
      return skipThrough(state, [event.setId], event.nowMs);

    case 'SKIP_EXERCISE':
      if (state.phase !== 'SET') return state;
      return skipThrough(state, remainingOfExercise(state), event.nowMs);

    case 'FINISH_NOW':
      // R16 TERMINER MAINTENANT — what is done stays done, nothing is added:
      // the drafts of the sets not performed are dropped, never validated.
      if (state.phase !== 'SET' && state.phase !== 'REST') return state;
      return { ...state, phase: 'COMPLETE', rest: null, cursorSetId: null, drafts: {}, completedMs: event.nowMs };

    case 'RESTORE':
      return event.state;

    case 'RESET':
      return initialState;
  }
}

/** Did this REST_END open a new exercise? (drives the light haptic + announcement) */
export function opensNewExercise(state: WorkoutState): boolean {
  return state.phase === 'REST' && state.rest?.after.kind === 'REST_THEN_EXERCISE';
}

export function progress(state: WorkoutState): { exerciseIndex: number; exerciseCount: number } {
  const plan = state.plan;
  const ex = currentExercise(state);
  if (!plan) return { exerciseIndex: 0, exerciseCount: 0 };
  const restEx =
    state.phase === 'REST' && state.rest
      ? setById(plan, state.rest.fromSetId)?.se_id
      : undefined;
  const seId = ex?.se_id ?? restEx;
  const idx = plan.exercises.findIndex((e) => e.se_id === seId);
  return { exerciseIndex: Math.max(0, idx), exerciseCount: plan.exercises.length };
}
