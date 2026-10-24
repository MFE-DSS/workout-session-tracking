/**
 * D9 §11 — on relaunch, ONE workout state from three sources:
 *
 *   the server plan  → the canonical session: its sets, its names (a
 *                      substitution acknowledged since is already applied)
 *   the local journal → the sets this device durably recorded (wins over the
 *                      snapshot, exactly as in N0)
 *   the snapshot     → where the instrument was: cursor, rest, drafts
 *
 * A set the server holds that the device does not (done on the web, or before a
 * reinstall) is shown as done. A set the device holds that the server does not
 * yet is a pending command in the outbox: shown as done, synced later.
 */
import type { ExecutionPlan } from '../api/types';
import { DoneSet, initialState, WorkoutState } from '../domain/workout';
import { JournalRow, restoreState } from '../storage/outbox';

function serverDone(plan: ExecutionPlan): Record<number, DoneSet> {
  const done: Record<number, DoneSet> = {};
  for (const [id, d] of Object.entries(plan.done)) {
    done[Number(id)] = {
      weight: d.weight_kg ?? 0,
      reps: d.reps,
      performedAt: { epochMs: d.performed_at ? Date.parse(d.performed_at) : 0, estimated: d.performed_at === null },
      local: 'saved_local',
    };
  }
  return done;
}

export function stateFromServer(
  plan: ExecutionPlan,
  snapshot: WorkoutState | null,
  rows: JournalRow[],
  nowMs: number,
): WorkoutState {
  const local = rows.filter((r) => r.session_id === plan.session_id);
  const sameSession = snapshot !== null && snapshot.phase !== 'MISSION' && snapshot.plan?.session_id === plan.session_id;
  if (sameSession) {
    const restored = restoreState({ ...snapshot, plan }, local);
    return { ...restored, done: { ...serverDone(plan), ...restored.done } };
  }
  const fresh: WorkoutState = {
    ...initialState,
    phase: 'SET',
    plan,
    cursorSetId: plan.cursor_set_id,
    startedMs: Date.parse(plan.started_at),
  };
  const restored = restoreState(fresh, local);
  const done = { ...serverDone(plan), ...restored.done };
  const cursor = plan.sets.find((s) => !done[s.set_id])?.set_id ?? null;
  if (cursor === null) {
    // every set is recorded but the session is still open: what is left is to close it
    return { ...restored, done, phase: 'COMPLETE', cursorSetId: null, completedMs: nowMs };
  }
  return { ...restored, done, cursorSetId: cursor };
}
