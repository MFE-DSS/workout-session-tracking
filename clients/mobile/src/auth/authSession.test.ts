import { ApiFailure, CallInit } from '../api/http';
import { AuthSession, CredentialStore } from './authSession';

// No @types/node in this app: the two file-reading guards below use jest's own loader.
declare const __dirname: string;
type Fs = {
  readFileSync(p: string, enc: 'utf8'): string;
  readdirSync(p: string): string[];
  statSync(p: string): { isDirectory(): boolean };
};
const { readFileSync, readdirSync, statSync } = jest.requireActual<Fs>('fs');
const { join } = jest.requireActual<{ join(...parts: string[]): string }>('path');

function memoryStore(initial: string | null = null): CredentialStore & { value: string | null } {
  const s = {
    value: initial,
    read: async () => s.value,
    write: async (t: string) => {
      s.value = t;
    },
    clear: async () => {
      s.value = null;
    },
  };
  return s;
}

function pair(n: number) {
  return {
    token_type: 'Bearer', access_token: `access-${n}`, access_expires_in: 900,
    refresh_token: `rt1.dev.secret-${n}`, server_now: '2026-10-24T10:00:00+00:00',
  };
}

type Call = { path: string; init?: CallInit };

function fakeServer(handler: (c: Call) => unknown) {
  const calls: Call[] = [];
  const call = async <T>(path: string, init?: CallInit): Promise<T> => {
    calls.push({ path, init });
    return handler({ path, init }) as T;
  };
  return { call, calls };
}

test('login keeps the refresh token in the store and the access token in memory only', async () => {
  const store = memoryStore();
  const { call } = fakeServer(() => pair(1));
  const auth = new AuthSession(call, store);
  expect(await auth.login('u', 'p', 'iPhone')).toBe('ok');
  expect(store.value).toBe('rt1.dev.secret-1');
  expect(auth.signedIn).toBe(true);
});

test('a refused login is "invalid", an unreachable server is "network"', async () => {
  const refused = new AuthSession(fakeServer(() => { throw new ApiFailure('http', 401, 'invalid_credentials'); }).call, memoryStore());
  expect(await refused.login('u', 'bad', null)).toBe('invalid');
  const offline = new AuthSession(fakeServer(() => { throw new ApiFailure('network'); }).call, memoryStore());
  expect(await offline.login('u', 'p', null)).toBe('network');
});

test('refresh rotates the stored credential', async () => {
  const store = memoryStore('rt1.dev.secret-0');
  let n = 0;
  const { call, calls } = fakeServer(() => pair(++n));
  const auth = new AuthSession(call, store);
  expect(await auth.refresh()).toBe('ok');
  expect(calls[0].init?.body).toEqual({ refresh_token: 'rt1.dev.secret-0' });
  expect(store.value).toBe('rt1.dev.secret-1');
});

test('two parallel refreshes spend the refresh token ONCE', async () => {
  const store = memoryStore('rt1.dev.secret-0');
  const { call, calls } = fakeServer(() => pair(1));
  const auth = new AuthSession(call, store);
  await Promise.all([auth.refresh(), auth.refresh(), auth.refresh()]);
  expect(calls.filter((c) => c.path === '/auth/refresh')).toHaveLength(1);
});

test('a refused refresh clears the store; a network failure keeps it', async () => {
  const refused = memoryStore('rt1.dev.old');
  const a = new AuthSession(fakeServer(() => { throw new ApiFailure('http', 401, 'invalid_refresh'); }).call, refused);
  expect(await a.refresh()).toBe('invalid');
  expect(refused.value).toBeNull();

  const kept = memoryStore('rt1.dev.keep');
  const b = new AuthSession(fakeServer(() => { throw new ApiFailure('network'); }).call, kept);
  expect(await b.refresh()).toBe('network');
  expect(kept.value).toBe('rt1.dev.keep');
});

test('a 401 on a resource call refreshes once and retries once', async () => {
  const store = memoryStore();
  let n = 0;
  const { call } = fakeServer(() => pair(++n));
  const auth = new AuthSession(call, store);
  await auth.login('u', 'p', null);
  const seen: string[] = [];
  const result = await auth.authorized(async (token) => {
    seen.push(token);
    if (seen.length === 1) throw new ApiFailure('http', 401, 'unauthorized');
    return 'done';
  });
  expect(result).toBe('done');
  expect(seen).toEqual(['access-1', 'access-2']);
});

test('an expired access token is renewed before the call, by the monotonic clock', async () => {
  let mono = 0;
  let n = 0;
  const { call, calls } = fakeServer(() => pair(++n));
  const auth = new AuthSession(call, memoryStore(), () => mono);
  await auth.login('u', 'p', null);
  mono = 15 * 60_000; // past expiry
  const token = await auth.authorized(async (t) => t);
  expect(token).toBe('access-2');
  expect(calls.map((c) => c.path)).toEqual(['/auth/login', '/auth/refresh']);
});

test('the server time of every token pair anchors D11', async () => {
  const anchors: [string, number][] = [];
  const auth = new AuthSession(fakeServer(() => pair(1)).call, memoryStore(), () => 42, (s, m) => anchors.push([s, m]));
  await auth.login('u', 'p', null);
  expect(anchors).toEqual([['2026-10-24T10:00:00+00:00', 42]]);
});

test('logout revokes this device server-side and forgets the credential, even offline', async () => {
  const store = memoryStore();
  const { call, calls } = fakeServer((c) => (c.path === '/auth/logout' ? undefined : pair(1)));
  const auth = new AuthSession(call, store);
  await auth.login('u', 'p', null);
  await auth.logout();
  expect(calls.at(-1)).toEqual({ path: '/auth/logout', init: { method: 'POST', token: 'access-1' } });
  expect(store.value).toBeNull();
  expect(auth.signedIn).toBe(false);

  const offlineStore = memoryStore('rt1.dev.x');
  const offline = new AuthSession(fakeServer(() => { throw new ApiFailure('network'); }).call, offlineStore);
  await offline.logout();
  expect(offlineStore.value).toBeNull();
});

test('no auth or transport module writes to the console', () => {
  for (const f of ['authSession.ts', 'credentialStore.ts', '../api/http.ts']) {
    const src = readFileSync(join(__dirname, f), 'utf8');
    expect(src).not.toMatch(/console\./);
  }
});

function importsOf(src: string): string[] {
  return [...src.matchAll(/^import[^'"]*['"]([^'"]+)['"]/gm)].map((m) => m[1]);
}

function sourcesUnder(dir: string): string[] {
  return readdirSync(dir).flatMap((f: string) => {
    const p = join(dir, f);
    return statSync(p).isDirectory() ? sourcesUnder(p) : /\.tsx?$/.test(f) && !/\.test\./.test(f) ? [p] : [];
  });
}

test('the refresh credential is stored through expo-secure-store and nothing else', () => {
  // imports, not prose: a comment that NAMES AsyncStorage is not a use of it
  expect(importsOf(readFileSync(join(__dirname, 'credentialStore.ts'), 'utf8'))).toEqual([
    'expo-secure-store', './authSession',
  ]);
});

test('only the auth layer ever touches the refresh token', () => {
  const root = join(__dirname, '..', '..');
  const touching = [...sourcesUnder(join(root, 'src')), join(root, 'App.tsx'), join(root, 'ConnectedApp.tsx')]
    .filter((p) => { try { return /refresh_token/.test(readFileSync(p, 'utf8')); } catch { return false; } })
    .map((p) => p.slice(root.length + 1))
    .sort();
  expect(touching).toEqual(['src/api/types.ts', 'src/auth/authSession.ts']);
});

function deferredValue<T>() {
  let resolve!: (value: T) => void;
  let reject!: (error: unknown) => void;
  const promise = new Promise<T>((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
}

test('register sends canonical fields once for concurrent submits and adopts the confirmed pair', async () => {
  const pending = deferredValue<ReturnType<typeof pair>>();
  const server = fakeServer(() => pending.promise);
  const store = memoryStore();
  const auth = new AuthSession(server.call, store);
  const input = { username: 'athlete', password: 'test-only-password', password_confirm: 'test-only-password', email: '' };
  const first = auth.register(input, 'iPhone');
  const duplicate = auth.register(input, 'iPhone');
  await Promise.resolve();
  pending.resolve(pair(2));
  expect(await first).toEqual({ state: 'confirmed' });
  expect(await duplicate).toEqual({ state: 'confirmed' });
  expect(server.calls).toEqual([{ path: '/auth/register', init: { method: 'POST', body: { ...input, device_label: 'iPhone' } } }]);
  expect(store.value).toBe(pair(2).refresh_token);
});

test('lost registration result stays unknown, is not retried, and does not claim authentication', async () => {
  const server = fakeServer(() => { throw new ApiFailure('network'); });
  const auth = new AuthSession(server.call, memoryStore());
  expect(await auth.register({ username: 'athlete', password: 'p', password_confirm: 'p' }, null)).toEqual({ state: 'unknown' });
  expect(server.calls).toHaveLength(1);
  expect(auth.signedIn).toBe(false);
});

test('registration returns only the canonical rejection code', async () => {
  const auth = new AuthSession(fakeServer(() => { throw new ApiFailure('http', 409, 'username_taken'); }).call, memoryStore());
  expect(await auth.register({ username: 'athlete', password: 'p', password_confirm: 'p' }, null)).toEqual({ state: 'rejected', code: 'username_taken' });
});

test('password mutation adopts its pair but never retries the mutation after a refusal', async () => {
  const store = memoryStore();
  const server = fakeServer(({ path }) => path === '/auth/password' ? pair(2) : pair(1));
  const auth = new AuthSession(server.call, store);
  await auth.login('u', 'p', null);
  const input = { current_password: 'old', new_password: 'new-test-only', new_password_confirm: 'new-test-only' };
  expect(await auth.changePassword(input)).toEqual({ state: 'confirmed' });
  expect(server.calls.at(-1)).toEqual({ path: '/auth/password', init: { method: 'POST', token: 'access-1', body: input } });
  expect(store.value).toBe(pair(2).refresh_token);
  const refused = fakeServer(({ path }) => { if (path === '/auth/password') throw new ApiFailure('http', 401, 'invalid_current_password'); return pair(1); });
  const b = new AuthSession(refused.call, memoryStore());
  await b.login('u', 'p', null);
  expect(await b.changePassword(input)).toEqual({ state: 'rejected', code: 'invalid_current_password' });
  expect(refused.calls.filter((x) => x.path === '/auth/password')).toHaveLength(1);
});

test('logout fences a late login response and prevents credential resurrection', async () => {
  const pending = deferredValue<ReturnType<typeof pair>>();
  const store = memoryStore();
  const auth = new AuthSession(fakeServer(() => pending.promise).call, store);
  const login = auth.login('u', 'p', null);
  await auth.logout();
  pending.resolve(pair(1));
  expect(await login).not.toBe('ok');
  expect(store.value).toBeNull();
  expect(auth.signedIn).toBe(false);
});

test('a late refused refresh cannot erase a newer login credential', async () => {
  const pending = deferredValue<ReturnType<typeof pair>>();
  const store = memoryStore('rt1.dev.old');
  const started = deferredValue<void>();
  const auth = new AuthSession(fakeServer(({ path }) => {
    if (path === '/auth/refresh') { started.resolve(); return pending.promise; }
    return pair(2);
  }).call, store);
  const refreshing = auth.refresh();
  await started.promise;
  await auth.login('new-user', 'p', null);
  pending.reject(new ApiFailure('http', 401, 'invalid_refresh'));
  await refreshing;
  expect(store.value).toBe(pair(2).refresh_token);
  expect(await auth.authorized(async (token) => token)).toBe('access-2');
});

test('logout queues behind an already started credential write', async () => {
  const gate = deferredValue<void>();
  const started = deferredValue<void>();
  const store = memoryStore();
  const originalWrite = store.write;
  store.write = async (value) => { started.resolve(); await gate.promise; await originalWrite(value); };
  const auth = new AuthSession(fakeServer(() => pair(1)).call, store);
  const login = auth.login('u', 'p', null);
  await started.promise;
  const logout = auth.logout();
  gate.resolve();
  await Promise.all([login, logout]);
  expect(store.value).toBeNull();
  expect(auth.signedIn).toBe(false);
});

test('device session identity is read inside auth without exposing the credential', async () => {
  const auth = new AuthSession(fakeServer(() => pair(1)).call, memoryStore('rt1.known-device.private-secret'));
  expect(await auth.deviceSessionId()).toBe('known-device');
  const malformed = new AuthSession(fakeServer(() => pair(1)).call, memoryStore('not-a-refresh'));
  expect(await malformed.deviceSessionId()).toBeNull();
});

test('refresh during password change waits for its new credential rather than overwriting it', async () => {
  const pending = deferredValue<ReturnType<typeof pair>>();
  const started = deferredValue<void>();
  const store = memoryStore();
  const server = fakeServer(({ path, init }) => {
    if (path === '/auth/password') { started.resolve(); return pending.promise; }
    if (path === '/auth/refresh') {
      expect(init?.body).toEqual({ refresh_token: pair(2).refresh_token }); return pair(3);
    }
    return pair(1);
  });
  const auth = new AuthSession(server.call, store);
  await auth.login('u', 'p', null);
  const updating = auth.changePassword({ current_password: 'old', new_password: 'new', new_password_confirm: 'new' });
  await started.promise;
  const renewing = auth.refresh();
  await Promise.resolve();
  expect(server.calls.filter((x) => x.path === '/auth/refresh')).toHaveLength(0);
  pending.resolve(pair(2));
  await updating; await renewing;
  expect(store.value).toBe(pair(3).refresh_token);
});
