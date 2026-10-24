import type { WorkoutState } from '../domain/workout';
import type { Command, JournalRow, OutboxRow, SetCommand } from './outbox';

export type Metric = { name: string; value: number; at_ms: number };

export type Restored = {
  snapshot: WorkoutState | null;
  sets: JournalRow[];
  outbox: OutboxRow[];
};

export interface Journal {
  readonly kind: 'sqlite' | 'memory';
  restore(): Promise<Restored>;
  /**
   * ONE transaction: the set fact + its outbox command + the instrument
   * snapshot. Either all three are durable, or none is. Resolves with the
   * measured commit time (G-LOCAL).
   */
  commitValidation(row: JournalRow, command: SetCommand, snapshot: WorkoutState): Promise<number>;
  saveSnapshot(snapshot: WorkoutState): Promise<void>;
  /**
   * D9 — a session-level command (R16, substitution) and the snapshot that
   * reflects it, in ONE transaction: the decision and its command survive a
   * force-kill together, or not at all.
   */
  enqueue(command: Command, snapshot: WorkoutState): Promise<void>;
  /** D9 — every command not yet acknowledged, in the order it was decided. */
  outboxRows(): Promise<OutboxRow[]>;
  markOutbox(opId: string, state: OutboxRow['state'], attempts: number): Promise<void>;
  recordMetric(name: string, value: number): Promise<void>;
  metrics(): Promise<Metric[]>;
  /** Lab-only device state (profile, persona, sessions done) — JSON by key. */
  getLab<T>(key: LabKey): Promise<T | null>;
  setLab(key: LabKey, value: unknown): Promise<void>;
  reset(): Promise<void>;
}

export type LabKey = 'profile' | 'persona' | 'sessions';
