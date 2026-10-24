/**
 * Outbox and restore logic — pure, so it is unit-tested without a device.
 *
 * The SQLite layer (`journal.ts`) only persists what these functions build.
 */
import type { PerformedAt } from '../domain/performedAt';
import type { WorkoutState } from '../domain/workout';

export type SetCommand = {
  op_id: string;
  kind: 'SET_COMPLETION';
  /** `set/<set_id>` — one command per training fact (D3). */
  target: string;
  payload: {
    session_id: number;
    set_id: number;
    weight_kg: number;
    reps: number;
    performed_at: string;
    performed_at_estimated: boolean;
    /**
     * Engine V2 (ruling 7): reps in reserve, OPTIONAL in the contract. The N0
     * nominal flow never asks for it, so it is always `null` here; a reported
     * value is kept as reported, never corrected by a population mean.
     */
    rir: number | null;
  };
};

/**
 * D9 — the session-level commands of R16 (TERMINER / ABANDONNER) and the
 * REQUIRES_SYNC substitution. They travel through the SAME outbox as the sets,
 * in order: a session is never closed on the server before its sets arrive.
 */
export type CloseCommand = {
  op_id: string;
  kind: 'SESSION_FINISH' | 'SESSION_ABANDON';
  target: string;
  payload: { session_id: number; at: string };
};

export type SubstituteCommand = {
  op_id: string;
  kind: 'SUBSTITUTE';
  target: string;
  payload: { session_id: number; se_id: number; name: string };
};

export type Command = SetCommand | CloseCommand | SubstituteCommand;

export function closeCommand(
  opId: string,
  kind: CloseCommand['kind'],
  sessionId: number,
  atMs: number,
): CloseCommand {
  return {
    op_id: opId,
    kind,
    target: `session/${sessionId}`,
    payload: { session_id: sessionId, at: new Date(atMs).toISOString() },
  };
}

export function substituteCommand(opId: string, sessionId: number, seId: number, name: string): SubstituteCommand {
  return {
    op_id: opId,
    kind: 'SUBSTITUTE',
    target: `exercise/${seId}`,
    payload: { session_id: sessionId, se_id: seId, name },
  };
}

export type OutboxRow = {
  op_id: string;
  kind: string;
  target: string;
  payload: string;
  created_at_ms: number;
  attempts: number;
  state: 'pending' | 'inflight' | 'acked' | 'failed';
};

export type JournalRow = {
  set_id: number;
  session_id: number;
  se_id: number;
  weight_kg: number;
  reps: number;
  performed_at_ms: number;
  performed_at_estimated: number;
  local_state: string;
  created_at_ms: number;
};

export function setCommand(
  opId: string,
  sessionId: number,
  setId: number,
  weight: number,
  reps: number,
  at: PerformedAt,
): SetCommand {
  return {
    op_id: opId,
    kind: 'SET_COMPLETION',
    target: `set/${setId}`,
    payload: {
      session_id: sessionId,
      set_id: setId,
      weight_kg: weight,
      reps,
      performed_at: new Date(at.epochMs).toISOString(),
      performed_at_estimated: at.estimated,
      rir: null,
    },
  };
}

/**
 * Two PENDING commands on the same fact collapse: the latest wins. An
 * in-flight command is never rewritten (its outcome is not known yet).
 */
export function compactPending(rows: OutboxRow[]): OutboxRow[] {
  const latestPending = new Map<string, OutboxRow>();
  const kept: OutboxRow[] = [];
  for (const row of rows) {
    if (row.state !== 'pending') {
      kept.push(row);
      continue;
    }
    const seen = latestPending.get(row.target);
    if (!seen || row.created_at_ms >= seen.created_at_ms) latestPending.set(row.target, row);
  }
  return [...kept, ...latestPending.values()].sort((a, b) => a.created_at_ms - b.created_at_ms);
}

/** Exponential backoff for a retry, capped at 5 minutes. */
export function retryDelayMs(attempts: number): number {
  return Math.min(5 * 60_000, 1000 * 2 ** Math.max(0, attempts));
}

/**
 * After a restart: the snapshot says where the instrument was; the journal says
 * which sets are DURABLY recorded. A set present in the journal is shown as
 * saved on the device, whatever the snapshot said about it. The journal wins.
 */
export function restoreState(snapshot: WorkoutState, rows: JournalRow[]): WorkoutState {
  const done = { ...snapshot.done };
  for (const row of rows) {
    if (snapshot.plan && row.session_id !== snapshot.plan.session_id) continue;
    done[row.set_id] = {
      weight: row.weight_kg,
      reps: row.reps,
      performedAt: { epochMs: row.performed_at_ms, estimated: row.performed_at_estimated === 1 },
      local: 'saved_local',
    };
  }
  for (const [id, d] of Object.entries(done)) {
    if (d.local === 'pending_local' && !rows.some((r) => r.set_id === Number(id))) {
      done[Number(id)] = { ...d, local: 'not_saved' };
    }
  }
  return { ...snapshot, done };
}
