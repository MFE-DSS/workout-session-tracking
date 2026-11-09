import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { AuthSession } from '../auth/authSession';
import { ApiFailure, type Transport } from './http';
import { createV3Transport, RuntimeV3Client, decodeRecommendationV3, capabilityEnvelope, V3_VERSIONS } from './firstPlanV3';

const cases = JSON.parse(readFileSync(resolve(__dirname,'../../../../docs/science/sci-p02-initial-policy/stage2-v3/producer-fixtures.v3.json'),'utf8'));
const copy = (v:any) => JSON.parse(JSON.stringify(v));
const pair={ access_token:'synthetic-access',refresh_token:'rt1.test-only.secret',access_expires_in:900,server_now:'2026-11-08T12:00:00Z' };
async function setup(reply:unknown) {
  let owner=7,credential:string|null=null;
  const identity:Transport=async(path)=> (path==='/auth/me'?{id:owner,username:'synthetic'}:pair) as any;
  const auth=new AuthSession(identity,{read:async()=>credential,write:async(v)=>{credential=v;},clear:async()=>{credential=null;}});
  await auth.login('synthetic','test-only',null);
  const submitted:unknown[]=[];
  let source=async()=>reply;
  const client=new RuntimeV3Client(auth,identity,async(path,init)=>{submitted.push({path,init});return source();});
  return {auth,client,submitted,set:(value:()=>Promise<unknown>)=>{source=value;},owner:(id:number)=>{owner=id;}};
}
const envelope=(data={})=>({owner_id:7,contract_version:'first-session-runtime/3.0.0',versions:V3_VERSIONS,...data});

test('parallel transport negotiates V3 and calibration without touching V1',async()=>{
  const calls:any[]=[];
  const fetcher=async(url:any,init:any)=>{calls.push({url,init});return {ok:true,status:200,json:async()=>envelope()} as Response;};
  await createV3Transport('http://127.0.0.1:8990',fetcher as any)('/me/blueprint/declarations',{token:'test-only',ifMatch:3});
  expect(calls[0].url).toBe('http://127.0.0.1:8990/api/mobile/v3/me/blueprint/declarations');
  expect(calls[0].init.headers['X-Auren-Contract']).toBe('first-session-runtime/3.0.0');
  expect(calls[0].init.headers['X-Auren-Calibration']).toBe('first-calibration-encounter/1.0.0');
  expect(calls[0].init.headers['If-Match']).toBe('3');
  expect(calls[0].init.credentials).toBe('omit');
});

test.each([
  {...envelope(),owner_id:8}, {...envelope(),versions:{...V3_VERSIONS,result:'first-plan-recommendation/1.0.0'}},
  {...envelope(),contract_version:'first-session-runtime/4.0.0'},
])('wrong owner or negotiated contract never populates the consumer',async(raw)=>{
  const s=await setup(raw);
  expect((await s.client.request('/me/first-plan/capabilities')).state).toBe('unknown');
});

test('late success after changing account is discarded',async()=>{
  const s=await setup(null);let done!:(value:unknown)=>void;
  s.set(()=>new Promise(resolve=>{done=resolve;}));
  const loading=s.client.request('/me/first-plan/capabilities');
  for(let i=0;i<15;i++) await Promise.resolve();
  await s.auth.logout();s.owner(8);await s.auth.login('other','test-only',null);
  done(envelope());
  expect((await loading).state).toBe('cancelled');
});

test('lost mutation response is unknown and the mutation is not replayed',async()=>{
  const s=await setup(null);s.set(async()=>{throw new ApiFailure('network');});
  expect((await s.client.request('/me/blueprint/snapshots',{method:'POST',body:{request_id:'stable'}})).state).toBe('unknown');
  expect(s.submitted).toHaveLength(1);
});

test('published SCI V3 structure is decoded while scientific admission stays server-owned',()=>{
  for(const row of cases) expect(decodeRecommendationV3(row.response)).not.toBeNull();
  const positive=copy(cases.find((r:any)=>r.response.scientific_readiness==='SCIENTIFICALLY_READY').response);
  positive.candidate_plan.sessions[0].slots[0].prescription.dose.work_sets=true;
  expect(decodeRecommendationV3(positive)).toBeNull();
  positive.candidate_plan.sessions[0].slots[0].prescription.dose.work_sets=Number.NaN;
  expect(decodeRecommendationV3(positive)).toBeNull();
  expect(decodeRecommendationV3({...positive,scientific_readiness:'READY'})).toBeNull();
});

test('only the matching owned snapshot and authority can be displayed as a proposal',async()=>{
  const {FirstPlanV3Client}=require('./firstPlanV3');
  const row=cases.find((r:any)=>r.response.scientific_readiness==='SCIENTIFICALLY_READY');
  const result=copy(row.response),request=row.request;
  const capabilities:any=envelope({runtime_availability:'NOT_SERVED',controlled_test_available:true,controlled_authority:{state:'ACTIVE',generation:1,
    pins:{registry_digest:'602ff0d32ebc625b4c9474660b5b36ee9983c4c598f16ae9b1269e67e5cea50f',binding_digest:result.binding_digest,bundle_digest:result.bundle_digest,effective_science_digest:result.effective_science_digest},
    engine_version:result.engine_version,policy_version:result.policy_version,binding_ref:result.binding_ref,start_policy_ref:result.start_policy_ref}});
  const snapshot:any=envelope({snapshot_ref:request.snapshot_ref,subject_ref:request.subject_ref,source_revision:Number(request.source_revision.split('/').pop())||0});
  result.source_revision=`blueprint-source/${snapshot.source_revision}`;
  const evaluation=envelope({evaluation_ref:'test-evaluation',snapshot_ref:snapshot.snapshot_ref,source_revision:snapshot.source_revision,authority_generation:1,
    operation_kind:'EVALUATE',parent_evaluation_ref:null,recommendation:result,historical:true});
  const s=await setup(evaluation),client=new FirstPlanV3Client(s.client);
  expect((await client.evaluate(snapshot,capabilities,'stable-evaluation')).state).toBe('confirmed');
  s.set(async()=>({...evaluation,recommendation:{...result,binding_digest:'0'.repeat(64)}}));
  expect((await client.evaluate(snapshot,capabilities,'different-evaluation')).state).toBe('unknown');
  s.set(async()=>({...evaluation,source_revision:snapshot.source_revision+1}));
  expect((await client.evaluate(snapshot,capabilities,'stale-evaluation')).state).toBe('unknown');
  const unavailable={...capabilities,controlled_authority:null};s.submitted.length=0;
  expect((await client.evaluate(snapshot,unavailable,'not-served')).state).toBe('unavailable');
  expect(s.submitted).toHaveLength(0);
});

test('parallel client schemas are exact consumer copies of the published V3 exports',()=>{
  const local=require('./firstPlanV3.contract.json');
  for(const [key,file] of [['request','FirstPlanRequest'],['response','FirstPlanRecommendation']]){
    expect(local[key]).toEqual(JSON.parse(readFileSync(resolve(__dirname,`../../../../docs/science/sci-p01-p02/v3/${file}.v3.schema.json`),'utf8')));
  }
});
test.each([
 {supported_realizations:{}},
 {supported_realizations:[{candidate_id:'x'}]},
 {calibration_protocol_material:{source_ref:'x',sha256:'not-a-digest',text:'procedure'}},
 {initial_calibration_pilot:{candidate_id:'x',realization_ref:'r',display_name:1}}
])('malformed optional capability content is not exposed to the consumer: %j',extra=>{
 expect(capabilityEnvelope({owner_id:7,contract_version:'first-session-runtime/3.0.0',versions:V3_VERSIONS,
  runtime_availability:'NOT_SERVED',controlled_test_available:false,controlled_authority:null,...extra} as any)).toBeNull();
});

test('inventory2 is explicitly negotiated and missing echo never downgrades to pilot',async()=>{
 const calls:any[]=[];
 const fetcher=async(_url:any,init:any)=>{calls.push(init);return {ok:true,status:200,headers:new Headers(),json:async()=>envelope()} as Response;};
 const call=createV3Transport('http://127.0.0.1:8990',fetcher as any,{calibrationInventory:'plan-calibration-inventory/2.0.0'});
 await expect(call('/me/first-plan/capabilities')).rejects.toBeInstanceOf(ApiFailure);
 expect(calls[0].headers['X-Auren-Calibration-Inventory']).toBe('plan-calibration-inventory/2.0.0');
});

test('I3 legacy capabilities check contradictory pilot fields on each served carrier without requiring six profiles',()=>{
 const pilot=JSON.parse(readFileSync(resolve(__dirname,'../../../../docs/science/sci-p02-initial-policy/stage2-v3/authority/registry.v1.json'),'utf8')).selection[0];
 const legacy=()=>envelope({runtime_availability:'NOT_SERVED',controlled_test_available:true,controlled_authority:null,
  initial_calibration_pilot:{...pilot,display_name:'pilot'},supported_realizations:[{...pilot,display_name:'pilot',initial_guidance_supported:true}]}) as any;
 expect(capabilityEnvelope(legacy())).not.toBeNull();
 for(const carrier of ['initial_calibration_pilot','supported_realizations'])for(const field of ['intent_id','realization_ref','load_semantics','policy_ref']){
  const c=legacy(),row=carrier==='initial_calibration_pilot'?c.initial_calibration_pilot:c.supported_realizations[0];row[field]='contradictory';expect(capabilityEnvelope(c)).toBeNull();
 }
 const minimal=legacy();delete minimal.initial_calibration_pilot.intent_id;expect(capabilityEnvelope(minimal)).not.toBeNull();
});
