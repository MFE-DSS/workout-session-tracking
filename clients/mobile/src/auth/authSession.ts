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

export type AccountOutcome =
  | { state: 'confirmed' }
  | { state: 'rejected'; code: string | null }
  | { state: 'unknown' }
  | { state: 'cancelled' };
export type Registration = { username: string; password: string; password_confirm: string; email?: string };
export type PasswordChange = { current_password: string; new_password: string; new_password_confirm: string };

export class AuthSession {
  private access: string | null = null;
  private accessUntil = 0;
  private inflight: Promise<AuthOutcome> | null = null;
  private loginFlight: Promise<AuthOutcome> | null = null;
  private mutation: Promise<AccountOutcome> | null = null;
  private generation = 0;
  private storeTail: Promise<unknown> = Promise.resolve();

  constructor(
    private readonly call: Transport,
    private readonly store: CredentialStore,
    private readonly mono: () => number = () => performance.now(),
    private readonly onServerTime: (serverNowIso: string, monoAtReceipt: number) => void = () => undefined,
  ) {}

  /** Store operations stay ordered even if a SecureStore write finishes after logout. */
  private stored<T>(fn: () => Promise<T>): Promise<T> {
    const task = this.storeTail.then(fn, fn);
    this.storeTail = task.catch(() => undefined);
    return task;
  }

  get revision(): number { return this.generation; }
  get signedIn(): boolean { return this.access !== null; }

  private async adopt(pair: TokenPair, generation: number): Promise<boolean> {
    if (generation !== this.generation) return false;
    const written = await this.stored(async () => {
      if (generation !== this.generation) return false;
      await this.store.write(pair.refresh_token);
      return true;
    });
    if (!written || generation !== this.generation) return false;
    const at = this.mono();
    this.access = pair.access_token;
    this.accessUntil = at + pair.access_expires_in * 1000 - EARLY_RENEW_MS;
    this.onServerTime(pair.server_now, at);
    return true;
  }

  private beginIdentity(): number {
    this.generation += 1;
    this.access = null;
    this.accessUntil = 0;
    this.inflight = null;
    return this.generation;
  }

  login(username: string, password: string, deviceLabel: string | null): Promise<AuthOutcome> {
    if (this.loginFlight) return this.loginFlight;
    const generation = this.beginIdentity();
    const task = (async (): Promise<AuthOutcome> => {
      try {
        await this.stored(() => this.store.clear());
        if (generation !== this.generation) return 'network';
        const pair = await this.call<TokenPair>('/auth/login', {
          method: 'POST', body: { username, password, device_label: deviceLabel },
        });
        return await this.adopt(pair, generation) ? 'ok' : 'network';
      } catch (e) {
        return generation === this.generation && e instanceof ApiFailure && e.kind === 'http' ? 'invalid' : 'network';
      }
    })();
    this.loginFlight = task;
    void task.finally(() => { if (this.loginFlight === task) this.loginFlight = null; });
    return task;
  }

  register(input: Registration, deviceLabel: string | null): Promise<AccountOutcome> {
    if (this.mutation) return this.mutation;
    const generation = this.beginIdentity();
    return this.mutate('/auth/register', { ...input, device_label: deviceLabel }, generation, false);
  }

  changePassword(input: PasswordChange): Promise<AccountOutcome> {
    if (this.mutation) return this.mutation;
    return this.mutate('/auth/password', input, this.generation, true);
  }

  private mutate(path: string, body: unknown, generation: number, authenticated: boolean): Promise<AccountOutcome> {
    const task = (async (): Promise<AccountOutcome> => {
      try {
        if (!authenticated) await this.stored(() => this.store.clear());
        if (authenticated && this.inflight) await this.inflight;
        if (authenticated && (!this.access || this.mono() >= this.accessUntil)) await this.ensureRefreshed(true);
        if (generation !== this.generation) return { state: 'cancelled' };
        // Mutations are sent ONCE: a 401 or unknown reply never replays an account operation.
        const pair = await this.call<TokenPair>(path, {
          method: 'POST', body, ...(authenticated ? { token: this.access } : {}),
        });
        return await this.adopt(pair, generation) ? { state: 'confirmed' } : { state: 'cancelled' };
      } catch (e) {
        if (generation !== this.generation) return { state: 'cancelled' };
        if (e instanceof ApiFailure && e.kind === 'http' && e.status >= 400 && e.status < 500 && e.status !== 408) {
          return { state: 'rejected', code: e.code };
        }
        return { state: 'unknown' };
      }
    })();
    this.mutation = task;
    void task.finally(() => { if (this.mutation === task) this.mutation = null; });
    return task;
  }

  async hasCredential(): Promise<boolean> { return (await this.stored(() => this.store.read())) !== null; }

  /** Only the non-secret stable device-session identifier leaves the auth layer. */
  async deviceSessionId(): Promise<string | null> {
    const value = await this.stored(() => this.store.read());
    return /^rt1\.([A-Za-z0-9_-]+)\.[A-Za-z0-9_-]+$/.exec(value ?? '')?.[1] ?? null;
  }

  refresh(): Promise<AuthOutcome> {
    if (this.mutation) return this.mutation.then(() => this.refresh());
    return this.refreshNow();
  }

  private refreshNow(): Promise<AuthOutcome> {
    if (!this.inflight) {
      const task = this.doRefresh(this.generation);
      this.inflight = task;
      void task.finally(() => { if (this.inflight === task) this.inflight = null; });
    }
    return this.inflight;
  }

  private async doRefresh(generation: number): Promise<AuthOutcome> {
    const stored = await this.stored(() => this.store.read());
    if (generation !== this.generation) return 'network';
    if (!stored) return 'invalid';
    try {
      const pair = await this.call<TokenPair>('/auth/refresh', { method: 'POST', body: { refresh_token: stored } });
      return await this.adopt(pair, generation) ? 'ok' : 'network';
    } catch (e) {
      if (generation !== this.generation) return 'network';
      if (e instanceof ApiFailure && e.kind === 'http' && (e.status === 401 || e.status === 422)) {
        this.access = null;
        await this.stored(async () => { if (generation === this.generation) await this.store.clear(); });
        return 'invalid';
      }
      return 'network';
    }
  }

  async authorized<T>(fn: (token: string) => Promise<T>, options: { retryUnauthorized?: boolean } = {}): Promise<T> {
    const generation = this.generation;
    if (!this.access || this.mono() >= this.accessUntil) await this.ensureRefreshed();
    const check = () => { if (generation !== this.generation || !this.access) throw new ApiFailure('http', 401, 'auth'); };
    check();
    try {
      const value = await fn(this.access as string);
      check();
      return value;
    } catch (e) {
      check();
      if (options.retryUnauthorized === false || !(e instanceof ApiFailure && e.kind === 'http' && e.status === 401)) throw e;
      await this.ensureRefreshed();
      check();
      const value = await fn(this.access as string);
      check();
      return value;
    }
  }

  private async ensureRefreshed(insideMutation = false): Promise<void> {
    const outcome = await (insideMutation ? this.refreshNow() : this.refresh());
    if (outcome === 'network') throw new ApiFailure('network');
    if (outcome === 'invalid') throw new ApiFailure('http', 401, 'auth');
  }

  async logout(): Promise<void> {
    const token = this.access;
    this.beginIdentity();
    this.loginFlight = null;
    this.mutation = null;
    // Queue the clear immediately, before any later login can write its own credential.
    const clearing = this.stored(() => this.store.clear());
    try {
      if (token) await this.call<void>('/auth/logout', { method: 'POST', token });
    } catch {
      // Best effort for this captured device token only. Never revoke a later login.
    }
    await clearing;
  }
}
