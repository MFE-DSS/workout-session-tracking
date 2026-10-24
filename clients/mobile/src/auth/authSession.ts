/**
 * D9 — the device's authenticated session. Pure orchestration: the transport
 * and the credential store are injected, so every rule below is unit-tested.
 *
 *   access token  → memory only, ~15 min, sent as `Bearer`
 *   refresh token → secure store only, ROTATED on every use
 *
 * Rules:
 *  - one refresh in flight at a time: two parallel 401s must not spend the same
 *    refresh token twice (the server would read the second use as a theft and
 *    revoke the device);
 *  - the rotated refresh token is written to the secure store BEFORE the new
 *    access token is used;
 *  - a refused refresh clears the store: the user signs in again;
 *  - a network failure clears nothing: the workout continues offline.
 *
 * Nothing here logs — tokens and passwords pass through.
 */
import { ApiFailure, Transport } from '../api/http';
import type { TokenPair } from '../api/types';

export type CredentialStore = {
  read(): Promise<string | null>;
  write(refreshToken: string): Promise<void>;
  clear(): Promise<void>;
};

export type AuthOutcome = 'ok' | 'invalid' | 'network';

/** Renew the access token a little before the server would refuse it. */
const EARLY_RENEW_MS = 30_000;

export class AuthSession {
  private access: string | null = null;
  private accessUntil = 0;
  private inflight: Promise<AuthOutcome> | null = null;

  constructor(
    private readonly call: Transport,
    private readonly store: CredentialStore,
    private readonly mono: () => number = () => performance.now(),
    /** server time as seen at receipt — the D11 anchor */
    private readonly onServerTime: (serverNowIso: string, monoAtReceipt: number) => void = () => undefined,
  ) {}

  private async adopt(pair: TokenPair): Promise<void> {
    await this.store.write(pair.refresh_token);
    const at = this.mono();
    this.access = pair.access_token;
    this.accessUntil = at + pair.access_expires_in * 1000 - EARLY_RENEW_MS;
    this.onServerTime(pair.server_now, at);
  }

  get signedIn(): boolean {
    return this.access !== null;
  }

  async login(username: string, password: string, deviceLabel: string | null): Promise<AuthOutcome> {
    try {
      const pair = await this.call<TokenPair>('/auth/login', {
        method: 'POST',
        body: { username, password, device_label: deviceLabel },
      });
      await this.adopt(pair);
      return 'ok';
    } catch (e) {
      return e instanceof ApiFailure && e.kind === 'http' ? 'invalid' : 'network';
    }
  }

  /** Is there a stored credential at all? (boot: login screen or not) */
  async hasCredential(): Promise<boolean> {
    return (await this.store.read()) !== null;
  }

  refresh(): Promise<AuthOutcome> {
    if (!this.inflight) {
      this.inflight = this.doRefresh().finally(() => {
        this.inflight = null;
      });
    }
    return this.inflight;
  }

  private async doRefresh(): Promise<AuthOutcome> {
    const stored = await this.store.read();
    if (!stored) return 'invalid';
    try {
      const pair = await this.call<TokenPair>('/auth/refresh', {
        method: 'POST',
        body: { refresh_token: stored },
      });
      await this.adopt(pair);
      return 'ok';
    } catch (e) {
      if (e instanceof ApiFailure && e.kind === 'http' && (e.status === 401 || e.status === 422)) {
        this.access = null;
        await this.store.clear();
        return 'invalid';
      }
      return 'network';
    }
  }

  /**
   * Run an API call with a valid access token. One 401 triggers one refresh and
   * one retry; a second refusal surfaces as `ApiFailure(http, 401, 'auth')`.
   */
  async authorized<T>(fn: (token: string) => Promise<T>): Promise<T> {
    if (!this.access || this.mono() >= this.accessUntil) await this.ensureRefreshed();
    try {
      return await fn(this.access as string);
    } catch (e) {
      if (!(e instanceof ApiFailure && e.kind === 'http' && e.status === 401)) throw e;
      await this.ensureRefreshed();
      return fn(this.access as string);
    }
  }

  private async ensureRefreshed(): Promise<void> {
    const outcome = await this.refresh();
    if (outcome === 'network') throw new ApiFailure('network');
    if (outcome === 'invalid') throw new ApiFailure('http', 401, 'auth');
  }

  /** Revoke THIS device server-side (best effort), then forget everything locally. */
  async logout(): Promise<void> {
    try {
      await this.authorized((token) => this.call<void>('/auth/logout', { method: 'POST', token }));
    } catch {
      // offline or already revoked: the local credential is erased all the same
    }
    this.access = null;
    this.accessUntil = 0;
    await this.store.clear();
  }
}
