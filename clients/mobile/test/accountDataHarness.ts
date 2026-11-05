/** Test-only HTTP boundary; actual transport and AuthSession, no served fixture endpoint. */
import { AuthSession } from '../src/auth/authSession';
import { createTransport } from '../src/api/http';
export const reply = (body: unknown, status = 200) => ({ status, ok: status >= 200 && status < 300, json: async () => body }) as Response;
export function deferred<T>() { let resolve!: (v: T) => void; const promise = new Promise<T>((r) => { resolve = r; }); return { resolve, promise }; }
export async function accountHarness() {
  let owner = 7, clock = 0, credential: string | null = null, token = 0;
  const owners = new Map<string, number>(), calls: {path: string; token: string | null; body: any}[] = [];
  let handler: (path: string, id: number, body: any) => Promise<Response> = async () => reply(null, 404);
  let refreshAllowed = true;
  const pair = (id: number) => {
    const access = `fixture-access-${++token}`; owners.set(access, id);
    return { access_token: access, refresh_token: `fixture-refresh-${id}`, access_expires_in: 900,
      token_type: 'Bearer', server_now: '2026-11-05T12:00:00Z' };
  };
  const fetcher = async (url: string, init?: RequestInit) => {
    const parsed = new URL(url), path = parsed.pathname.replace('/api/mobile/v1', '') + parsed.search;
    const access = ((init?.headers as Record<string, string>)?.Authorization ?? '').replace('Bearer ', '');
    const body = init?.body ? JSON.parse(init.body as string) : null;
    calls.push({ path, token: access || null, body });
    if (path === '/auth/login') return reply(pair(owner));
    if (path === '/auth/refresh') return refreshAllowed ? reply(pair(Number(body.refresh_token.split('-').at(-1)))) : reply({detail:{error:'invalid_refresh'}},401);
    const id = owners.get(access);
    if (!id) return reply({detail:{error:'unauthorized'}},401);
    if (path === '/auth/me') return reply({id});
    if (path === '/auth/logout') return reply(null,204);
    return handler(path, id, body);
  };
  const call = createTransport('http://test-only.invalid', fetcher as typeof fetch);
  const store={read:async()=>credential,write:async(v:string)=>{credential=v;},clear:async()=>{credential=null;}};
  const newAuth=()=>new AuthSession(call,store,()=>clock);
  const auth = newAuth();
  await auth.login('fixture','fixture-only',null);
  return { auth, call, calls, newAuth, handle:(fn:typeof handler)=>{handler=fn;}, setOwner:(id:number)=>{owner=id;},
    expire:()=>{clock+=1_000_000;}, denyRefresh:()=>{refreshAllowed=false;} };
}
export function weightPage(id=11, owner=7, cursor:string|null=null) {
  return {contract_version:'weight-history/1.0.0' as const,owner_id:owner,unit:'kg' as const,legacy_profile_included:false as const,
    timezone_basis:'DATABASE_UTC_CONVENTION' as const,state:'AVAILABLE' as const,next_cursor:cursor,
    entries:[{measurement_id:id,value:72,raw_value_repr:null,measured_at:'2025-01-02T00:00:00Z',recorded_at:null,
      quality:'KNOWN' as const,provenance:{origin:'UNKNOWN' as const,acquisition:'UNKNOWN' as const,source_ref:`body_measurements/${id}/weight_kg`}}]};
}
