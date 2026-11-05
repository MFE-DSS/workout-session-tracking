import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { AuthSession } from '../auth/authSession';
import { ApiFailure, type Transport } from './http';
import { FirstPlanClient, type FirstPlanProducer } from './firstPlan';

const root = resolve(__dirname, '../../../../');
const cases: any[] = JSON.parse(readFileSync(resolve(root, 'docs/science/sci-p01-p02/v1/fixtures.json'), 'utf8'));
const pair = { access_token:'test-access',refresh_token:'rt1.test.secret',access_expires_in:900,server_now:'2026-11-05T12:00:00Z' };
const copy = (x:any) => JSON.parse(JSON.stringify(x));
async function setup(raw:any, verified=true) {
  let credential:string|null=null;
  const seen:string[]=[];
  const call:Transport=async(path)=>{
    seen.push(path);
    if(path==='/auth/me')return {id:7,username:'test-owner'} as any;
    if(path==='/auth/logout')return undefined as any;
    return pair as any;
  };
  const auth=new AuthSession(call,{read:async()=>credential,write:async(v)=>{credential=v;},clear:async()=>{credential=null;}});
  await auth.login('test-owner','test-only',null);
  const producer:FirstPlanProducer={read:async()=>({owner_id:7,kind:'result',result:raw}),verify:async()=>verified};
  return {auth,call,producer,seen,client:new FirstPlanClient(auth,call,producer)};
}
function input(c=cases[0]) { return {request:copy(c.request),fingerprint:c.response.request_fingerprint}; }

test('missing science producer is explicitly unavailable without calling a fictitious endpoint',async()=>{
  const s=await setup(null);s.seen.length=0;
  const client=new FirstPlanClient(s.auth,s.call);
  expect(await client.load(input())).toEqual({state:'unavailable',reason:'NOT_SERVED'});
  expect(s.seen).toEqual([]);
});
test.each(cases.map((c:any)=>[c.scenario,c] as [string,any]))('canonical fixture %s preserves its true status',async(_name,c:any)=>{
  const s=await setup(c.response), result=await s.client.load(input(c));
  const expected:any={CONFLICTING_DATA:'rejected',INSUFFICIENT_DATA:'insufficient_information',POLICY_UNAVAILABLE:'unavailable',CONSTRAINT_UNSATISFIABLE:'rejected',REVIEW_REQUIRED:'unavailable'};
  expect(result.state).toBe(expected[c.response.status]);
  expect((result as any).status).toBe(c.response.status);
  expect(result.state).not.toBe('available');
});
test.each(['fingerprint','version','engine','shape','owner','authority'])('invalid %s never becomes a recommendation',async(kind)=>{
  const c=copy(cases[0]),s=await setup(c.response,kind!=='authority');
  if(kind==='fingerprint')c.response.request_fingerprint='0'.repeat(64);
  if(kind==='version')c.response.contract_version='unknown';
  if(kind==='engine')c.response.engine_version='unexpected-engine';
  if(kind==='shape')c.response.assessment.missing_fields=42;
  if(kind==='owner')s.producer.read=async()=>({owner_id:8,kind:'result',result:c.response});
  expect((await s.client.load(input(cases[0]))).state).toBe('unknown');
});
test('pending is observable while a producer is running',async()=>{
  const s=await setup(null);let done!:(value:unknown)=>void;
  s.producer.read=()=>new Promise((r)=>{done=r;});
  const loading=s.client.load(input());
  expect(s.client.state.state).toBe('pending');
  for(let i=0;i<12;i++)await Promise.resolve();
  done({owner_id:7,kind:'pending'});expect((await loading).state).toBe('pending');
});
test('response after account change cannot populate the next account',async()=>{
  const s=await setup(null);let done!:(value:unknown)=>void;
  s.producer.read=()=>new Promise((r)=>{done=r;});
  const loading=s.client.load(input());
  for(let i=0;i<12;i++)await Promise.resolve();
  await s.auth.logout();await s.auth.login('other','test-only',null);
  done({owner_id:7,kind:'result',result:cases[0].response});
  expect((await loading).state).toBe('unknown');expect(s.client.state.state).toBe('unknown');
});
test('cached personal state disappears immediately when auth generation changes',async()=>{
  const c=cases.find((x:any)=>x.response.status==='INSUFFICIENT_DATA'),s=await setup(c.response);
  expect((await s.client.load(input(c))).state).toBe('insufficient_information');
  await s.auth.logout();expect(s.client.state).toEqual({state:'unknown'});
});
test.each([new ApiFailure('network'),new ApiFailure('http',401),new ApiFailure('http',503)])('transport failure remains explicit (%s)',async(error)=>{
  const s=await setup(null);s.producer.read=async()=>{throw error;};
  expect((await s.client.load(input())).state).toBe(error instanceof ApiFailure&&error.status===401?'rejected':'unknown');
});
test('consumer schema copies are pinned to published canonical exports',()=>{
  const schemas=require('./firstPlan.contract.json');
  for(const [key,name] of [['request','first_plan_request'],['response','first_plan_recommendation']]){
    expect(schemas[key]).toEqual(JSON.parse(readFileSync(resolve(root,`docs/science/sci-p01-p02/v1/${name}.v1.schema.json`),'utf8')));
  }
});

test('available is exercised only with a synthetic protocol fixture, never a served policy',async()=>{
  const c=JSON.parse(readFileSync(resolve(__dirname,'__fixtures__/firstPlan.protocol-test-only.json'),'utf8'));
  expect(c.authority).toBe('SYNTHETIC_TEST_ONLY_NOT_SERVED');
  const s=await setup(c.response);
  const result=await s.client.load(input(c));
  expect(result.state).toBe('available');
  const disabled=new FirstPlanClient(s.auth,s.call);
  expect((await disabled.load(input(c))).state).toBe('unavailable');
});

test('READY with no plan or engine cannot be exposed even by an incorrectly permissive adapter',async()=>{
  const c=copy(cases[0]); c.response.status='READY'; c.response.candidate_plan=null;
  const s=await setup(c.response);
  expect((await s.client.load(input(c))).state).toBe('unknown');
});
test('an older response cannot replace a newer input result',async()=>{
  const a=cases[0],b=cases.find((x:any)=>x.response.status==='INSUFFICIENT_DATA'),s=await setup(null);
  let old!:(value:unknown)=>void, fresh!:(value:unknown)=>void;let calls=0;
  s.producer.read=()=>new Promise((r)=>{if(calls++===0)old=r;else fresh=r;});
  const first=s.client.load(input(a));for(let i=0;i<12;i++)await Promise.resolve();
  const second=s.client.load(input(b));for(let i=0;i<12;i++)await Promise.resolve();
  fresh({owner_id:7,kind:'result',result:b.response});expect((await second).state).toBe('insufficient_information');
  old({owner_id:7,kind:'result',result:a.response});expect((await first).state).toBe('unknown');
  expect(s.client.state.state).toBe('insufficient_information');
});
