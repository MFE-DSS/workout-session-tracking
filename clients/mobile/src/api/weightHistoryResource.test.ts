import { accountHarness, deferred, reply, weightPage } from '../../test/accountDataHarness';
import { WeightHistoryClient } from './weightHistory';
import { WeightHistoryResource } from './weightHistoryResource';
async function setup() { const s=await accountHarness(); return {...s,resource:new WeightHistoryResource(s.auth,new WeightHistoryClient(s.auth,s.call))}; }

test('headless consumer requires explicit consent and clears history when consent is revoked',async()=>{
 const s=await setup(); let allowed=false;
 s.handle(async()=>allowed?reply(weightPage()):reply({detail:{error:'body_consent_required'}},403));
 expect(await s.resource.refresh()).toEqual({state:'consent_required'});
 allowed=true;expect((await s.resource.refresh()).state).toBe('confirmed');
 allowed=false;expect(await s.resource.refresh()).toEqual({state:'consent_required'});
 expect('value' in s.resource.state).toBe(false);
});
test('empty history stays empty, never turns the undated profile weight into a row',async()=>{
 const s=await setup();s.handle(async()=>reply({...weightPage(),state:'EMPTY',entries:[]}));
 const r=await s.resource.refresh();expect(r).toMatchObject({state:'confirmed',value:{state:'EMPTY',entries:[]}});
 const count=s.calls.length;await s.resource.loadNext();expect(s.calls).toHaveLength(count);
});
test('real client pages through canonical entries once and double next shares one request',async()=>{
 const s=await setup(), page=deferred<Response>();let sends=0;
 s.handle(async(path)=>{sends++;return path.includes('cursor=')?page.promise:reply(weightPage(12,7,'opaque+cursor'));});
 await s.resource.refresh();const first=s.resource.loadNext(),second=s.resource.loadNext();
 page.resolve(reply(weightPage(11)));await Promise.all([first,second]);
 expect(sends).toBe(2);expect(s.resource.state).toMatchObject({state:'confirmed',value:{entries:[{measurement_id:12},{measurement_id:11}],next_cursor:null}});
 expect(s.calls.at(-1)?.path).toContain('cursor=opaque%2Bcursor');
});
test.each(['invalid_cursor','duplicate','repeated_cursor','wrong_owner','network'])('page failure %s cannot claim a complete chronology or retain readable stale state',async(kind)=>{
 const s=await setup();let page=false;
 s.handle(async()=>{if(!page)return reply(weightPage(12,7,'next'));if(kind==='network')throw Error('offline');if(kind==='invalid_cursor')return reply({detail:{error:'invalid_weight_history_cursor'}},400);
 return reply(weightPage(kind==='duplicate'?12:11,kind==='wrong_owner'?8:7,kind==='repeated_cursor'?'next':null));});
 await s.resource.refresh();page=true;const r=await s.resource.loadNext();
 expect(['unknown','rejected']).toContain(r.state);expect('value' in s.resource.state).toBe(false);
});
test('token expiry refreshes through real AuthSession without changing measurement owner',async()=>{
 const s=await setup();s.handle(async(_path,id)=>reply(weightPage(11,id)));s.expire();
 expect((await s.resource.refresh()).state).toBe('confirmed');expect(s.calls.filter(c=>c.path==='/auth/refresh')).toHaveLength(1);
});
test('refresh refusal does not retain previously readable data',async()=>{
 const s=await setup();s.handle(async()=>reply(weightPage()));await s.resource.refresh();s.expire();s.denyRefresh();
 expect((await s.resource.refresh()).state).not.toBe('confirmed');expect('value' in s.resource.state).toBe(false);
});
test('account switch hides cached data immediately and rejects an old in-flight page',async()=>{
 const s=await setup(), late=deferred<Response>();s.handle(async(path)=>path.includes('cursor=')?late.promise:reply(weightPage(12,7,'next')));
 await s.resource.refresh();const page=s.resource.loadNext();for(let i=0;i<20;i++)await Promise.resolve();
 await s.auth.logout();s.setOwner(8);await s.auth.login('other','fixture-only',null);
 expect(s.resource.state).toEqual({state:'idle'});late.resolve(reply(weightPage(11)));await page;
 expect('value' in s.resource.state).toBe(false);
 s.handle(async(_p,id)=>reply(weightPage(99,id)));expect(await s.resource.refresh()).toMatchObject({state:'confirmed',value:{owner_id:8}});
});
test('an older request cannot overwrite a newer refresh and callers cannot mutate cached facts',async()=>{
 const s=await setup(), older=deferred<Response>();let n=0;s.handle(async()=>++n===1?older.promise:reply(weightPage(21)));
 const first=s.resource.refresh();for(let i=0;i<20;i++)await Promise.resolve();await s.resource.refresh();older.resolve(reply(weightPage(11)));await first;
 const state=s.resource.state;if(state.state==='confirmed')state.value.entries.length=0;
 expect(s.resource.state).toMatchObject({state:'confirmed',value:{entries:[{measurement_id:21}]}});
});

test('a longer cursor cycle cannot keep paging a fabricated chronology',async()=>{
 const s=await setup();let n=0;s.handle(async()=>{n++;return reply(weightPage(20-n,7,n===2?'cursor-b':'cursor-a'));});
 await s.resource.refresh();await s.resource.loadNext();
 expect((await s.resource.loadNext()).state).toBe('unknown');expect('value' in s.resource.state).toBe(false);
});

test('the abandoned owner promise cannot return the newly signed-in owner history',async()=>{
 const s=await setup(),old=deferred<Response>();s.handle(async()=>old.promise);const abandoned=s.resource.refresh();for(let i=0;i<25;i++)await Promise.resolve();
 await s.auth.logout();s.setOwner(8);await s.auth.login('other','fixture-only',null);s.handle(async()=>reply(weightPage(88,8)));
 await s.resource.refresh();old.resolve(reply(weightPage(11,7)));
 expect(await abandoned).toEqual({state:'cancelled'});expect(s.resource.state).toMatchObject({state:'confirmed',value:{owner_id:8}});
});
