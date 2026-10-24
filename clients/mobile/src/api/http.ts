/**
 * D9 — the one transport to `/api/mobile/v1`. JSON in, JSON out, a timeout,
 * and two kinds of failure the rest of the app can act on:
 *
 *   network → the server was not reached: retry later, keep working offline
 *   http    → the server answered and refused: `status` + the contract's `error`
 *
 * Nothing here logs: request bodies carry passwords and tokens.
 */

export class ApiFailure extends Error {
  constructor(
    readonly kind: 'network' | 'http',
    readonly status = 0,
    readonly code: string | null = null,
  ) {
    super(kind === 'network' ? 'network' : `http ${status}${code ? ` ${code}` : ''}`);
  }
}

export type CallInit = {
  method?: 'GET' | 'POST' | 'PUT';
  body?: unknown;
  token?: string | null;
  timeoutMs?: number;
};

export type Transport = <T>(path: string, init?: CallInit) => Promise<T>;

const DEFAULT_TIMEOUT_MS = 10_000;

function errorCode(body: unknown): string | null {
  const detail = (body as { detail?: unknown } | null)?.detail;
  if (detail && typeof detail === 'object' && typeof (detail as { error?: unknown }).error === 'string') {
    return (detail as { error: string }).error;
  }
  return typeof detail === 'string' ? detail : null;
}

export function createTransport(baseUrl: string, fetchImpl: typeof fetch = fetch): Transport {
  const base = baseUrl.replace(/\/+$/, '');
  return async function call<T>(path: string, init: CallInit = {}): Promise<T> {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), init.timeoutMs ?? DEFAULT_TIMEOUT_MS);
    const headers: Record<string, string> = { Accept: 'application/json' };
    if (init.body !== undefined) headers['Content-Type'] = 'application/json';
    if (init.token) headers.Authorization = `Bearer ${init.token}`;
    let res: Response;
    try {
      res = await fetchImpl(`${base}/api/mobile/v1${path}`, {
        method: init.method ?? 'GET',
        headers,
        body: init.body === undefined ? undefined : JSON.stringify(init.body),
        signal: controller.signal,
      });
    } catch {
      throw new ApiFailure('network');
    } finally {
      clearTimeout(timer);
    }
    if (res.status === 204) return undefined as T;
    let body: unknown = null;
    try {
      body = await res.json();
    } catch {
      body = null;
    }
    if (!res.ok) throw new ApiFailure('http', res.status, errorCode(body));
    return body as T;
  };
}
