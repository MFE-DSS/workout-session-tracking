import { deferred } from '../../test/accountDataHarness';
import { firstUse, historical, missionHarness, negotiatedReply, resumed, HOST, CONTRACT } from '../../test/missionActionHarness';
import { createMissionActionTransport, MissionActionClient } from './missionAction';
async function setup(){const s=await missionHarness();return {...s,client:new MissionActionClient(s.auth,s.call,createMissionActionTransport('https://qa.test.invalid',s.fetcher))};}
test('real AuthSession sends only negotiated GET, preserves authority source, owner and revision',async()=>{
 const s=await setup();let captured:RequestInit|undefined;
 s.respond(async(url,init)=>{expect(url).toBe('https://qa.test.invalid/api/mobile/v1/mission-action?requested_path=FIRST_USE');captured=init;return negotiatedReply(firstUse());});
 expect(await s.client.read('FIRST_USE',true)).toEqual({state:'confirmed',value:firstUse()});
 expect(captured).toMatchObject({method:'GET',credentials:'omit',headers:{Authorization:expect.stringContaining('Bearer '),'X-Auren-Mission-Action':CONTRACT,'X-Auren-Mission-V3-Host':HOST}});
 expect(captured?.body).toBeUndefined();
});
test.each(['owner','path','version','date','action','profile','revision','source','invented','reason'])('incoherent first-use %s cannot authorize a path',async(kind)=>{
 const s=await setup(),raw:any=firstUse();
 if(kind==='owner')raw.owner_id=8;if(kind==='path')raw.requested_path='HISTORICAL';if(kind==='version')raw.contract_version='future';
 if(kind==='date')raw.observed_at='2026-02-30T12:00:00Z';if(kind==='action')raw.primary_action={kind:'START_LEGACY'};
 if(kind==='profile')raw.payload.execution_profile='LEGACY_V1';if(kind==='revision')raw.payload.source_revision='blueprint-source/NaN';
 if(kind==='source')raw.source='HISTORICAL_MISSION';if(kind==='invented')raw.state='READY';if(kind==='reason')raw.reason='fake-success';
 s.respond(async()=>negotiatedReply(raw));expect(await s.client.read('FIRST_USE',true)).toEqual({state:'unknown'});
});
test.each(['wrong_session','wrong_profile','negative_position','missing_session','v3_without_host','closed_legacy'])('incoherent resume %s is refused',async(kind)=>{
 const s=await setup(),raw:any=resumed();let host=true;
 if(kind==='wrong_session')raw.primary_action.session_id=20;if(kind==='wrong_profile')raw.payload.execution_profile='first-plan-execution/3.0.0';
 if(kind==='negative_position')raw.payload.position={exercise_index:-1,exercise_total:1,sets_done:0,sets_total:2,exercise_name:null,set_index:null};
 if(kind==='missing_session')delete raw.payload.session;if(kind==='v3_without_host'){Object.assign(raw,resumed('first-plan-execution/3.0.0'));host=false;}
 if(kind==='closed_legacy')Object.assign(raw,resumed('LEGACY_V1',true));
 s.respond(async()=>negotiatedReply(raw,200,host));expect(await s.client.read('FIRST_USE',host)).toEqual({state:'unknown'});
});
test.each([resumed(),resumed('first-plan-execution/3.0.0'),resumed('first-plan-execution/3.0.0',true)])('valid owned action $state / $primary_action.kind retains the same session',async(raw)=>{
 const s=await setup();s.respond(async()=>negotiatedReply(raw));expect(await s.client.read('FIRST_USE',true)).toEqual({state:'confirmed',value:raw});
});
test('historical READY is explicit, structurally complete and tied to its exact decision',async()=>{
 const s=await setup(),raw:any=historical();s.respond(async()=>negotiatedReply(raw));
 expect(await s.client.read('HISTORICAL',true)).toEqual({state:'confirmed',value:raw});
 raw.primary_action.decision={...raw.primary_action.decision,top:'different'};
 expect(await s.client.read('HISTORICAL',true)).toEqual({state:'unknown'});
});
test.each(['first_exercise','phrase','scope','executable','alternative','zones'])('invalid historical %s is not startable',async(kind)=>{
 const s=await setup(),raw:any=historical();
 if(kind==='first_exercise')raw.payload.scope.first_exercise=null;if(kind==='phrase')raw.payload.reason.phrase=7;
 if(kind==='scope')raw.payload.scope.exercise_count=-1;if(kind==='executable')raw.payload.executable=false;
 if(kind==='alternative')raw.payload.alternatives=[{slug:'x',name:'x',phrase:'x'}];if(kind==='zones')raw.payload.zones=[{zone:'x',label:7}];
 s.respond(async()=>negotiatedReply(raw));expect(await s.client.read('HISTORICAL',true)).toEqual({state:'unknown'});
});
test.each(['contract','host'])('missing or wrong negotiated %s echo stays unavailable',async(kind)=>{
 const s=await setup();s.respond(async()=>negotiatedReply(firstUse(),200,kind!=='host',kind==='contract'?'future':CONTRACT));
 expect(await s.client.read('FIRST_USE',true)).toEqual({state:'unavailable',reason:'CONTRACT_NOT_SUPPORTED'});
});
test('honest absence, transport loss and HTTP refusal remain distinct',async()=>{
 const s=await setup(),raw={...historical(),state:'NO_MISSION',source:'NONE',primary_action:null,payload:null};
 s.respond(async()=>negotiatedReply(raw));expect(await s.client.read('HISTORICAL',true)).toEqual({state:'confirmed',value:raw});
 s.respond(async()=>{throw Error('offline');});expect(await s.client.read('HISTORICAL',true)).toEqual({state:'unknown'});
 s.respond(async()=>negotiatedReply({detail:{error:'not_served'}},503));expect(await s.client.read('HISTORICAL',true)).toEqual({state:'unavailable',reason:'not_served'});
});
test('late identity response cannot launch or return the old owner data after logout',async()=>{
 const s=await setup(),late=deferred<Response>();s.respond(async()=>late.promise);const reading=s.client.read('FIRST_USE',true);
 for(let i=0;i<25;i++)await Promise.resolve();await s.auth.logout();late.resolve(negotiatedReply(firstUse()));
 expect(await reading).toEqual({state:'cancelled'});
});
test('malformed caller source or host never reaches the network',async()=>{
 const s=await setup();let calls=0;s.respond(async()=>{calls++;return negotiatedReply(firstUse());});
 expect(await s.client.read('FIRST_USE?owner=8' as any,true)).toEqual({state:'unknown'});
 expect(await s.client.read('FIRST_USE','yes' as any)).toEqual({state:'unknown'});expect(calls).toBe(0);
});
test.each([
 {state:'CONFLICT',source:'OPEN_SESSION',primary_action:null,payload:null,reason:'MULTIPLE_OPEN_SESSIONS'},
 {state:'UNAVAILABLE',source:'OWNED_FIRST_USE',primary_action:{kind:'REFRESH'},payload:null,reason:'AUTHORITY_UNAVAILABLE'},
 {state:'UNAVAILABLE',source:'OPEN_SESSION',primary_action:null,payload:null,reason:'EXECUTION_PROFILE_REQUIRED'},
])('confirmed $state retains its reason without a manufactured start',async(status)=>{
 const s=await setup(),raw={...firstUse(),...status};s.respond(async()=>negotiatedReply(raw));
 expect(await s.client.read('FIRST_USE',true)).toEqual({state:'confirmed',value:raw});
});
test.each(['action','reason','payload'])('incoherent conflict %s cannot turn into a confirmation',async(kind)=>{
 const s=await setup(),raw:any={...firstUse(),state:'CONFLICT',source:'OPEN_SESSION',primary_action:null,payload:null,reason:'MULTIPLE_OPEN_SESSIONS'};
 if(kind==='action')raw.primary_action={kind:'REFRESH'};if(kind==='reason')raw.reason=null;if(kind==='payload')raw.payload={session_id:9};
 s.respond(async()=>negotiatedReply(raw));expect(await s.client.read('FIRST_USE',true)).toEqual({state:'unknown'});
});
test('without V3 host a legacy resume remains readable and no V3 header is sent',async()=>{
 const s=await setup();s.respond(async(_url,init)=>{expect((init?.headers as any)['X-Auren-Mission-V3-Host']).toBeUndefined();return negotiatedReply(resumed(),200,false);});
 expect(await s.client.read('FIRST_USE',false)).toEqual({state:'confirmed',value:resumed()});
});
test('timeout covers JSON-body download, aborts the GET and preserves unknown transport status',async()=>{
 jest.useFakeTimers();
 try {
  const s=await setup();s.respond(async(_url,init)=>({...negotiatedReply(firstUse()),json:()=>new Promise((_resolve,reject)=>init?.signal?.addEventListener('abort',()=>reject(Error('aborted'))))} as Response));
  const read=s.client.read('FIRST_USE',true);for(let i=0;i<30;i++)await Promise.resolve();
  await jest.advanceTimersByTimeAsync(10001);expect(await read).toEqual({state:'unknown'});
 } finally {jest.useRealTimers();}
});
