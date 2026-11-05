/** Non-destructive deletion orchestration. No production deletion endpoint exists here. */
import { AuthSession } from '../auth/authSession';
import type { Transport } from './http';

export type DeletionIntent = {
  ownerId: number; requestId: string; previousRequestId?: string;
  phase: 'prepared' | 'submitted' | 'unknown' | 'pending' | 'confirmed' | 'rejected' | 'rejected_confirmed';
};
export type DeletionStore = {
  read(ownerId: number): Promise<DeletionIntent | null>;
  reserve(ownerId: number, requestId: string, current: () => boolean): Promise<DeletionIntent>;
  renewRejected(prior: DeletionIntent, newKey: string, current: () => boolean): Promise<DeletionIntent | null>;
  claim(intent: DeletionIntent, current: () => boolean): Promise<boolean>;
  write(intent: DeletionIntent, current: () => boolean): Promise<void>;
  retire(intent: DeletionIntent, current: () => boolean): Promise<void>;
};
/** Trusted adapter code, NOT fields from a JSON receipt. No production adapter is supplied.
 * verify must authenticate the authoritative result, applicable policy, revoked access,
 * completed data erasure and protection against restoration for DELETED, or an
 * authoritative terminal refusal for REJECTED. Shape alone proves none of it.
 */
export type DeletionProducer = {
  submit(token: string, intent: DeletionIntent, currentPassword: string): Promise<unknown>;
  read(token: string, intent: DeletionIntent): Promise<unknown>;
  verify(token: string, raw: unknown, intent: DeletionIntent): Promise<boolean>;
};
export type DeletionOutcome = { state: 'unavailable' | 'pending' | 'unknown' | 'rejected' | 'confirmed' | 'cancelled' };

const positiveId = (v: unknown): v is number => Number.isSafeInteger(v) && (v as number) > 0;
const nonempty = (v: unknown): v is string => typeof v === 'string' && v.trim().length > 0;

export class AccountDeletionClient {
  private busy = false;
  private confirmed: { result: DeletionOutcome; intent: DeletionIntent; revision: number } | null = null;
  constructor(
    private readonly auth: AuthSession,
    private readonly call: Transport,
    private readonly store: DeletionStore,
    private readonly producer: DeletionProducer | null = null,
    private readonly requestId: () => string = () => '',
  ) {}

  submit(currentPassword: string): Promise<DeletionOutcome> { return this.run(currentPassword); }
  retryRejected(currentPassword: string): Promise<DeletionOutcome> { return this.run(currentPassword, true); }
  reconcile(): Promise<DeletionOutcome> { return this.run(); }

  private async run(password?: string, renewRejected = false): Promise<DeletionOutcome> {
    if (!this.producer) return { state: 'unavailable' };
    if (this.busy) return { state: 'pending' };
    this.busy = true;
    this.confirmed = null;
    const revision = this.auth.revision;
    const current = () => revision === this.auth.revision;
    let intent: DeletionIntent | null = null;
    try {
      const owner = await this.auth.authorized((token) => this.call<{ id: number }>('/auth/me', { token }));
      if (!current()) return { state: 'cancelled' };
      if (!positiveId(owner?.id)) return { state: 'unknown' };
      if (renewRejected) {
        const previous = await this.store.read(owner.id);
        if (!previous || !['rejected', 'rejected_confirmed'].includes(previous.phase)) return { state: 'unknown' };
        const terminal = await this.auth.authorized(async (token) => {
          const raw = await this.producer!.read(token, previous) as any;
          return raw?.contract_version === 'account-deletion/1.0.0' && raw.owner_id === owner.id
            && raw.request_id === previous.requestId && raw.state === 'REJECTED'
            && await this.producer!.verify(token, raw, previous);
        }, { retryUnauthorized: false });
        if (!current()) return { state: 'cancelled' };
        if (!terminal) return { state: 'unknown' };
        await this.store.write({ ...previous, phase: 'rejected_confirmed' }, current);
        intent = await this.store.renewRejected(previous, this.requestId(), current);
        if (!intent) return { state: 'unknown' };
      } else if (password !== undefined) {
        const key = this.requestId();
        if (!nonempty(key)) return { state: 'unknown' };
        intent = await this.store.reserve(owner.id, key, current);
      } else intent = await this.store.read(owner.id);
      if (!current()) return { state: 'cancelled' };
      if (!intent || intent.ownerId !== owner.id) return { state: 'unavailable' };
      if (password !== undefined && !(await this.store.claim(intent, current))) {
        return { state: intent.phase === 'rejected_confirmed' ? 'rejected' : 'unknown' };
      }
      if (!current()) return { state: 'cancelled' };
      const captured = { ...intent };
      // A request is sent once. Neither expiry nor loss replays a mutation.
      const result = await this.auth.authorized(async (token) => {
        const raw = password === undefined
          ? await this.producer!.read(token, captured)
          : await this.producer!.submit(token, captured, password);
        if (!current()) return { state: 'cancelled' } as DeletionOutcome;
        return this.accept(token, raw, captured, revision, current);
      }, { retryUnauthorized: false });
      return current() ? result : { state: 'cancelled' };
    } catch {
      if (!current()) return { state: 'cancelled' };
      if (intent) {
        try { await this.store.write({ ...intent, phase: 'unknown' }, current); } catch { /* keep existing durable intent */ }
      }
      // 401/404 after revocation or account disappearance are NOT deletion proof.
      return { state: 'unknown' };
    } finally { this.busy = false; }
  }

  private async accept(token: string, raw: unknown, intent: DeletionIntent, revision: number, current: () => boolean): Promise<DeletionOutcome> {
    const value = raw as Record<string, unknown> | null;
    let state: DeletionOutcome['state'] = 'unknown';
    let phase: DeletionIntent['phase'] = 'unknown';
    if (value && value.contract_version === 'account-deletion/1.0.0'
      && value.owner_id === intent.ownerId && value.request_id === intent.requestId) {
      if (value.state === 'PENDING') { state = 'pending'; phase = 'pending'; }
      if (value.state === 'POLICY_REQUIRED') { state = 'unavailable'; phase = 'pending'; }
      if (value.state === 'REJECTED' && await this.producer!.verify(token, raw, intent)) { state = 'rejected'; phase = 'rejected_confirmed'; }
      if (value.state === 'DELETED' && nonempty(value.policy_ref)
        && typeof value.confirmed_at === 'string' && /(?:Z|[+-]\d{2}:\d{2})$/.test(value.confirmed_at)
        && Number.isFinite(Date.parse(value.confirmed_at))
        && value.revocation === 'CONFIRMED' && value.data_erasure === 'CONFIRMED'
        && value.restore_protection === 'CONFIRMED'
        && await this.producer!.verify(token, raw, intent)) { state = 'confirmed'; phase = 'confirmed'; }
    }
    if (!current()) return { state: 'cancelled' };
    const saved = { ...intent, phase };
    await this.store.write(saved, current);
    if (!current()) return { state: 'cancelled' };
    const result: DeletionOutcome = { state };
    if (state === 'confirmed') this.confirmed = { result, intent: saved, revision };
    return result;
  }

  /** No purge implementation here. Only this verified in-memory result can unlock
   * an explicitly owner-scoped future cleanup; a copy/JSON object cannot authorize it.
   */
  async complete(result: DeletionOutcome, cleanupOwner: (ownerId: number) => Promise<void>): Promise<boolean> {
    const confirmation = this.confirmed;
    if (!confirmation || confirmation.result !== result || confirmation.revision !== this.auth.revision) return false;
    this.confirmed = null;
    const current = () => confirmation.revision === this.auth.revision;
    await this.store.retire(confirmation.intent, current);
    if (!current()) return false;
    // Persistent retirement prevents reopen; synchronous generation change neutralizes late replies.
    await this.auth.logout();
    if (this.auth.revision !== confirmation.revision + 1) return false;
    await cleanupOwner(confirmation.intent.ownerId);
    return true;
  }
}
