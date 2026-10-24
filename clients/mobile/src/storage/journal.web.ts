/**
 * Web PREVIEW only — an in-memory journal so the screens can be rendered in a
 * browser for layout review. It proves nothing about durability: the N0
 * reliability proof (force-kill, restart) is a device test against `journal.ts`.
 */
import type { WorkoutState } from '../domain/workout';
import type { Journal, LabKey, Metric, Restored } from './journalTypes';
import type { JournalRow, OutboxRow, SetCommand } from './outbox';

export async function openJournal(): Promise<Journal> {
  let snapshot: WorkoutState | null = null;
  let sets: JournalRow[] = [];
  let outbox: OutboxRow[] = [];
  let metrics: Metric[] = [];
  let kv: Partial<Record<LabKey, string>> = {};

  return {
    kind: 'memory',
    async restore(): Promise<Restored> {
      return { snapshot, sets, outbox };
    },
    async commitValidation(r: JournalRow, c: SetCommand, s: WorkoutState): Promise<number> {
      sets = [...sets.filter((x) => x.set_id !== r.set_id), r];
      outbox = [...outbox, {
        op_id: c.op_id, kind: c.kind, target: c.target, payload: JSON.stringify(c.payload),
        created_at_ms: r.created_at_ms, attempts: 0, state: 'pending',
      }];
      snapshot = s;
      return 0;
    },
    async saveSnapshot(s: WorkoutState): Promise<void> {
      snapshot = s;
    },
    async recordMetric(name: string, value: number): Promise<void> {
      metrics = [...metrics, { name, value, at_ms: Date.now() }];
    },
    async metrics(): Promise<Metric[]> {
      return metrics;
    },
    async getLab<T>(key: LabKey): Promise<T | null> {
      return key in kv ? (JSON.parse(kv[key] as string) as T) : null;
    },
    async setLab(key: LabKey, value: unknown): Promise<void> {
      kv[key] = JSON.stringify(value);
    },
    async reset(): Promise<void> {
      snapshot = null;
      sets = [];
      outbox = [];
      metrics = [];
      kv = {};
    },
  };
}
