/**
 * D9 — the outbox drain (spec §10): PENDING → ACKNOWLEDGED | FAILED_REQUIRES_ATTENTION.
 *
 *  - FIFO, one command at a time: a session is never closed on the server
 *    before its sets, and a set never lands before the substitution it was
 *    performed under.
 *  - A transient failure (network, 5xx, 429, expired auth) keeps the row
 *    PENDING, stops the drain to preserve the order, and retries itself with
 *    backoff. Nothing is ever discarded.
 *  - A refusal the server will repeat (404, 409, 422) marks the row FAILED —
 *    visible, kept, retryable by hand — and the drain moves on.
 *  - The server answers an already-applied command with ACKNOWLEDGED: replaying
 *    an `inflight` row after a crash is safe.
 */
import { ApiFailure } from '../api/http';
import { OutboxRow, retryDelayMs } from '../storage/outbox';

export type SyncJournal = {
  outboxRows(): Promise<OutboxRow[]>;
  markOutbox(opId: string, state: OutboxRow['state'], attempts: number): Promise<void>;
};

export type SyncStatus = {
  pending: number;
  attention: number;
  syncing: boolean;
  offline: boolean;
  authRequired: boolean;
};

export type Outcome = 'retry' | 'auth' | 'attention';

export function classify(e: unknown): Outcome {
  if (!(e instanceof ApiFailure)) return 'attention';
  if (e.kind === 'network') return 'retry';
  if (e.status === 401) return 'auth';
  if (e.status >= 500 || e.status === 429 || e.status === 408) return 'retry';
  return 'attention';
}

export const IDLE: SyncStatus = { pending: 0, attention: 0, syncing: false, offline: false, authRequired: false };

export class SyncEngine {
  private running: Promise<void> | null = null;
  private again = false;
  private timer: ReturnType<typeof setTimeout> | null = null;
  private offline = false;
  private authRequired = false;

  constructor(
    private readonly journal: SyncJournal,
    private readonly send: (row: OutboxRow) => Promise<unknown>,
    private readonly onStatus: (s: SyncStatus) => void,
    private readonly onAck: (row: OutboxRow, response: unknown) => void = () => undefined,
  ) {}

  /** Drain now. Concurrent kicks coalesce into one more pass, never a parallel one. */
  kick(): Promise<void> {
    if (this.running) {
      this.again = true;
      return this.running;
    }
    this.running = this.loop().finally(() => {
      this.running = null;
    });
    return this.running;
  }

  stop(): void {
    if (this.timer) clearTimeout(this.timer);
    this.timer = null;
  }

  /** A FAILED row the user asked to send again. */
  async retry(opId: string): Promise<void> {
    const row = (await this.journal.outboxRows()).find((r) => r.op_id === opId);
    if (row?.state === 'failed') await this.journal.markOutbox(opId, 'pending', row.attempts);
    await this.kick();
  }

  private async loop(): Promise<void> {
    do {
      this.again = false;
      await this.drainOnce();
    } while (this.again);
  }

  private async drainOnce(): Promise<void> {
    const rows = await this.journal.outboxRows();
    for (const row of rows) {
      if (row.state === 'failed' || row.state === 'acked') continue;
      await this.publish(true);
      await this.journal.markOutbox(row.op_id, 'inflight', row.attempts);
      try {
        const response = await this.send(row);
        await this.journal.markOutbox(row.op_id, 'acked', row.attempts + 1);
        this.offline = false;
        this.authRequired = false;
        this.onAck(row, response);
      } catch (e) {
        const outcome = classify(e);
        if (outcome === 'attention') {
          await this.journal.markOutbox(row.op_id, 'failed', row.attempts + 1);
          continue;
        }
        await this.journal.markOutbox(row.op_id, 'pending', row.attempts + 1);
        this.offline = e instanceof ApiFailure && e.kind === 'network';
        this.authRequired = outcome === 'auth';
        this.schedule(retryDelayMs(row.attempts));
        break;
      }
    }
    await this.publish(false);
  }

  private schedule(ms: number): void {
    if (this.timer) clearTimeout(this.timer);
    this.timer = setTimeout(() => {
      this.timer = null;
      void this.kick();
    }, ms);
  }

  private async publish(syncing: boolean): Promise<void> {
    const rows = await this.journal.outboxRows();
    this.onStatus({
      pending: rows.filter((r) => r.state === 'pending' || r.state === 'inflight').length,
      attention: rows.filter((r) => r.state === 'failed').length,
      syncing,
      offline: this.offline,
      authRequired: this.authRequired,
    });
  }
}
