import { accountHarness, deferred, reply } from '../../test/accountDataHarness';
import { FirstUseController, type BlueprintSource } from './firstUse';
import { FirstPlanClient } from './firstPlan';
import { TrainingPreferencesClient } from './trainingPreferences';
import prefs from '../ui/account/review/trainingDeclarations.fixture.json';
import protocol from './__fixtures__/firstPlan.protocol-test-only.json';

async function setup(source: BlueprintSource | null = null) {
  const s = await accountHarness();
  s.handle(async(path) => path === '/me/training-preferences/declarations' ? reply(prefs) : reply(null,404));
  const firstPlan = new FirstPlanClient(s.auth,s.call);
  const controller = new FirstUseController(s.auth,s.call,new TrainingPreferencesClient(s.auth,s.call),firstPlan,source);
  return {...s,controller,firstPlan};
}
test('new user with no anthropometry or cadence is not sent to an invented plan or inventory',async()=>{
 const s=await setup();s.handle(async()=>reply({...prefs,declarations:{sessions_per_week:null,focus_priorities:null,available_equipment:null}}));
 expect(await s.controller.load()).toEqual({state:'no_plan_producer'});
 expect(s.calls.filter(x=>x.path.includes('mission')||x.path.includes('body')||x.body)).toHaveLength(1); // login only
});
test('loading is separate from unknown and rereading never writes declarations',async()=>{
 const s=await setup(),wait=deferred<Response>(),seen:string[]=[];s.handle(async()=>wait.promise);
 const stop=s.controller.subscribe(()=>seen.push(s.controller.state.state));const pending=s.controller.load();
 expect(s.controller.state.state).toBe('loading');wait.resolve(reply(null,503));
 expect(await pending).toEqual({state:'unknown'});stop();
 expect(seen).toEqual(['loading','unknown']);expect(s.calls.filter(x=>x.path.includes('declarations')&&x.body)).toEqual([]);
});
test('a departed account cannot restore the old state or expose its declarations',async()=>{
 const s=await setup(),wait=deferred<Response>();s.handle(async()=>wait.promise);const pending=s.controller.load();
 await s.auth.logout();s.setOwner(8);await s.auth.login('other','fixture-only',null);
 wait.resolve(reply(prefs));expect(await pending).toEqual({state:'unknown'});expect(s.controller.state.state).toBe('unknown');
});
test('later reads and explicit invalidation suppress abandoned results',async()=>{
 const s=await setup(),wait=deferred<Response>();s.handle(async()=>wait.promise);const old=s.controller.load();
 s.handle(async()=>reply(prefs));expect(await s.controller.load()).toEqual({state:'no_plan_producer'});
 wait.resolve(reply(null,503));expect(await old).toEqual({state:'unknown'});expect(s.controller.state.state).toBe('no_plan_producer');
 s.controller.invalidate();expect(s.controller.state.state).toBe('unknown');
});
test.each(['owner','consent','network'])('snapshot %s failure cannot expose a recommendation',async(kind)=>{
 const s=await setup({read:async()=>{throw Error('replaced');}});
 const source:BlueprintSource={read:async(token)=>{
  if(kind==='network')throw Error('network');
  if(kind==='consent')return s.call('/__test-only__/snapshot',{token});
  return {owner_id:8,input:{request:protocol.request,fingerprint:protocol.response.request_fingerprint}};
 }};
 const controller=new FirstUseController(s.auth,s.call,new TrainingPreferencesClient(s.auth,s.call),s.firstPlan,source);
 s.handle(async(path)=>path.includes('declarations')?reply(prefs):reply({detail:{error:'body_consent_required'}},403));
 expect((await controller.load()).state).toBe(kind==='consent'?'required_consent':'unknown');
});
test('the real SCI consumer maps insufficiency and never promotes a READY protocol example to a usable session',async()=>{
 const s=await setup();let response:any=JSON.parse(JSON.stringify(protocol.response));
 const first=new FirstPlanClient(s.auth,s.call,{read:async()=>({owner_id:7,kind:'result',result:response}),verify:async()=>true});
 const source:BlueprintSource={read:async()=>({owner_id:7,input:{request:protocol.request,fingerprint:protocol.response.request_fingerprint}})};
 const controller=new FirstUseController(s.auth,s.call,new TrainingPreferencesClient(s.auth,s.call),first,source);
 expect(await controller.load()).toEqual({state:'unavailable',reason:'SESSION_HANDOFF_NOT_SERVED'});
 response.status='INSUFFICIENT_DATA';response.candidate_plan=null;response.assessment.state='INSUFFICIENT';response.assessment.missing_fields=['sessions_per_week'];
 expect(await controller.load()).toEqual({state:'missing_information',missing:['sessions_per_week']});
});
