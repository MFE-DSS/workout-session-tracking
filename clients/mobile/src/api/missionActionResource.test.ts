import { deferred } from '../../test/accountDataHarness';
import { firstUse, historical, missionHarness, negotiatedReply } from '../../test/missionActionHarness';
import { createMissionActionTransport, MissionActionClient } from './missionAction';
import { MissionActionResource } from './missionActionResource';
async function setup(){const s=await missionHarness(),client=new MissionActionClient(s.auth,s.call,createMissionActionTransport('https://qa.test.invalid',s.fetcher));return {...s,resource:new MissionActionResource(s.auth,client,true)};}
const flush=async()=>{for(let i=0;i<35;i++)await Promise.resolve();};
test('first use is default, read pending is distinct and caller cannot mutate confirmed facts',async()=>{
 const s=await setup(),late=deferred<Response>();s.respond(async()=>late.promise);
 expect(s.resource.path).toBe('FIRST_USE');expect(s.resource.state).toEqual({state:'idle'});
 const reading=s.resource.refresh();expect(s.resource.state).toEqual({state:'pending'});
 late.resolve(negotiatedReply(firstUse()));await reading;
 const state=s.resource.state;if(state.state==='confirmed')state.value.owner_id=99;
 expect(s.resource.state).toMatchObject({state:'confirmed',value:{owner_id:7}});
});
test('a failed refresh keeps display-only previous facts, never confirmed action permission',async()=>{
 const s=await setup();await s.resource.refresh();s.respond(async()=>{throw Error('offline');});
 expect(await s.resource.refresh()).toMatchObject({state:'unknown',previous:firstUse()});
 expect(s.resource.state.state).not.toBe('confirmed');
 s.respond(async()=>negotiatedReply(firstUse()));expect((await s.resource.refresh()).state).toBe('confirmed');
});
test('explicit historical choice cancels a delayed first-use response without fallback',async()=>{
 const s=await setup(),late=deferred<Response>();s.respond(async()=>late.promise);
 const first=s.resource.refresh();await flush();s.resource.selectPath('HISTORICAL');
 expect(s.resource.state).toEqual({state:'idle'});s.respond(async()=>negotiatedReply(historical()));await s.resource.refresh();
 late.resolve(negotiatedReply(firstUse()));expect(await first).toEqual({state:'cancelled'});
 expect(s.resource.state).toMatchObject({state:'confirmed',value:{requested_path:'HISTORICAL'}});
});
test('mutation invalidation rejects a delayed read and removes all cached actions',async()=>{
 const s=await setup(),late=deferred<Response>();await s.resource.refresh();s.respond(async()=>late.promise);
 const read=s.resource.refresh();await flush();s.resource.invalidate();late.resolve(negotiatedReply(firstUse()));
 expect(await read).toEqual({state:'cancelled'});expect(s.resource.state).toEqual({state:'idle'});
});
test('host change cancels its old read; unavailable never falls back to the legacy source',async()=>{
 const s=await setup(),late=deferred<Response>();s.respond(async()=>late.promise);const read=s.resource.refresh();await flush();
 s.resource.setHost(false);late.resolve(negotiatedReply(firstUse()));expect(await read).toEqual({state:'cancelled'});
 const unavailable={...firstUse(),state:'UNAVAILABLE',primary_action:null,payload:null,reason:'EXECUTION_PROFILE_REQUIRED'};
 s.respond(async(url)=>{expect(url).toContain('requested_path=FIRST_USE');return negotiatedReply(unavailable,200,false);});
 expect(await s.resource.refresh()).toMatchObject({state:'confirmed',value:{state:'UNAVAILABLE'}});
});
test('newer refresh wins over an older response even on the same owner and source',async()=>{
 const s=await setup(),late=deferred<Response>();let n=0;s.respond(async()=>++n===1?late.promise:negotiatedReply({...firstUse(),payload:{...firstUse().payload,source_revision:'blueprint-source/2'}}));
 const first=s.resource.refresh();await flush();await s.resource.refresh();late.resolve(negotiatedReply(firstUse()));
 expect(await first).toEqual({state:'cancelled'});expect(s.resource.state).toMatchObject({state:'confirmed',value:{payload:{source_revision:'blueprint-source/2'}}});
});
test('A/B switching clears cached path/data immediately and old promises never return B facts',async()=>{
 const s=await setup();s.resource.selectPath('HISTORICAL');s.respond(async()=>negotiatedReply(historical()));await s.resource.refresh();
 const late=deferred<Response>();s.respond(async()=>late.promise);const old=s.resource.refresh();await flush();
 await s.auth.logout();s.setOwner(8);await s.auth.login('b','test-only',null);
 expect(s.resource.state).toEqual({state:'idle'});expect(s.resource.path).toBe('FIRST_USE');
 s.respond(async()=>negotiatedReply(firstUse(8)));await s.resource.refresh();late.resolve(negotiatedReply(historical()));
 expect(await old).toEqual({state:'cancelled'});expect(s.resource.state).toMatchObject({state:'confirmed',value:{owner_id:8}});
});
test('no missing data or cancelled read becomes an empty recommendation',async()=>{
 const s=await setup();s.respond(async()=>negotiatedReply(null));expect(await s.resource.refresh()).toEqual({state:'unknown'});
 s.resource.invalidate();expect(s.resource.state).toEqual({state:'idle'});
});
