/** Runtime-boundary tests only: no test producer or READY fixture is served by the app. */
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { accountHarness, deferred, reply } from '../../test/accountDataHarness';
import { FirstPlanClient, type FirstPlanInput, type FirstPlanProducer } from './firstPlan';
const root=resolve(__dirname,'../../../../');
const realCases:any[]=JSON.parse(readFileSync(resolve(root,'docs/science/sci-p02-initial-policy/v1/producer-fixtures.json'),'utf8'));
const protocol=JSON.parse(readFileSync(resolve(__dirname,'__fixtures__/firstPlan.protocol-test-only.json'),'utf8'));
const clone=(x:any)=>JSON.parse(JSON.stringify(x));
function ready(){return clone({request:protocol.request,response:protocol.response});}
async function setup(){
 const s=await accountHarness();let current=ready(),owner=7,status=200,verified=true;
 s.handle(async(path)=>{if(path!=='/__protocol_test_only__/first-plan')throw Error('unexpected-path');
  return status===200?reply({owner_id:owner,kind:'result',result:current.response}):reply({detail:{error:'body_consent_required'}},status);});
 const producer:FirstPlanProducer={read:async(token)=>s.call('/__protocol_test_only__/first-plan',{token}),verify:async()=>verified};
 const client=new FirstPlanClient(s.auth,s.call,producer);
 const input=():FirstPlanInput=>({request:current.request,fingerprint:current.response.request_fingerprint});
 return {...s,client,input,setCase:(c:any)=>{current=clone(c);},current:()=>current,setOwnerReply:(id:number)=>{owner=id;},revoke:()=>{status=403;},unverified:()=>{verified=false;}};
}
test('READY decoder is exercised with a labelled test-only protocol example, never a runtime scientific policy',async()=>{
 expect(protocol.authority).toBe('SYNTHETIC_TEST_ONLY_NOT_SERVED');
 const s=await setup();expect((await s.client.load(s.input())).state).toBe('available');
 const absent=new FirstPlanClient(s.auth,s.call);const n=s.calls.length;
 expect(await absent.load(s.input())).toEqual({state:'unavailable',reason:'NOT_SERVED'});expect(s.calls).toHaveLength(n);
});
test.each(['insufficient','unknown_gym','sufficient'])('real isolated producer case %s preserves its non-READY runtime outcome',async(name)=>{
 const s=await setup(),c=realCases.find(x=>x.scenario===name);expect(c.availability).toBe('NOT_SERVED');s.setCase(c);
 const out=await s.client.load(s.input());expect(out.state).toBe(name==='insufficient'?'insufficient_information':'unavailable');expect(out.state).not.toBe('available');
});
test.each(['version','owner','fingerprint','unverified'])('failure %s clears a previously available recommendation',async(kind)=>{
 const s=await setup();expect((await s.client.load(s.input())).state).toBe('available');
 const input=s.input();if(kind==='version')s.current().response.contract_version='stale-version';
 if(kind==='owner')s.setOwnerReply(8);if(kind==='fingerprint')s.current().response.request_fingerprint='0'.repeat(64);if(kind==='unverified')s.unverified();
 expect((await s.client.load(input)).state).toBe('unknown');expect(s.client.state.state).not.toBe('available');
});
test('revoked body consent from the authoritative adapter clears the previous result',async()=>{
 const s=await setup();await s.client.load(s.input());s.revoke();
 expect(await s.client.load(s.input())).toEqual({state:'rejected',code:'body_consent_required'});expect(s.client.state.state).toBe('rejected');
});
test('late HTTP recommendation cannot populate a new account',async()=>{
 const s=await setup(),late=deferred<Response>();s.handle(async()=>late.promise);const input=s.input(),running=s.client.load(input);
 for(let i=0;i<30;i++)await Promise.resolve();await s.auth.logout();s.setOwner(8);await s.auth.login('other','fixture-only',null);
 late.resolve(reply({owner_id:7,kind:'result',result:s.current().response}));expect((await running).state).toBe('unknown');expect(s.client.state.state).toBe('unknown');
});
test('a caller cannot mutate the verified cached recommendation',async()=>{
 const s=await setup(),out=await s.client.load(s.input());if(out.state==='available')out.recommendation.status='tampered';
 const state=s.client.state;expect(state).toMatchObject({state:'available',recommendation:{status:'READY'}});
 if(state.state==='available')state.recommendation.status='tampered-again';
 expect(s.client.state).toMatchObject({state:'available',recommendation:{status:'READY'}});
});
