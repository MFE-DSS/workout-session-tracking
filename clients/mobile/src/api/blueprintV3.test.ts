import { AuthSession } from '../auth/authSession';
import type { Transport } from './http';
import { RuntimeV3Client,V3_VERSIONS } from './firstPlanV3';
import { BlueprintV3Client } from './blueprintV3';

const envelope=(data={})=>({owner_id:7,contract_version:V3_VERSIONS.runtime,versions:V3_VERSIONS,...data});
async function setup(raw:unknown) {
  const identity:Transport=async(path)=> (path==='/auth/me'?{id:7}:{access_token:'test-only',refresh_token:'rt1.fixture.secret',access_expires_in:900,server_now:'2026-11-08T12:00:00Z'}) as any;
  const auth=new AuthSession(identity,{read:async()=>null,write:async()=>{},clear:async()=>{}});await auth.login('synthetic','test-only',null);
  const calls:any[]=[];
  const runtime=new RuntimeV3Client(auth,identity,async(path,init)=>{calls.push({path,init});return raw;});
  return {client:new BlueprintV3Client(runtime),calls};
}
test('declared input is sent as declarations with CAS, never a caller-owned Blueprint',async()=>{
  const s=await setup(envelope({source_revision:4,event_ref:'event-confirmed'}));
  const fields={sessions_per_week:{state:'KNOWN' as const,value:2}};
  expect((await s.client.saveDeclarations('stable-declaration',3,fields)).state).toBe('confirmed');
  expect(s.calls[0].init.ifMatch).toBe(3);
  expect(s.calls[0].init.body).toEqual({request_id:'stable-declaration',fields});
  expect(s.calls[0].init.body.owner_id).toBeUndefined();
});
test('foreign, malformed or mismatched snapshot cannot become authoritative input',async()=>{
  const s=await setup(envelope({snapshot_ref:'snapshot',source_revision:true,snapshot_digest:'x'.repeat(64),blueprint:{},subject_ref:'subject'}));
  expect((await s.client.capture('capture',0)).state).toBe('unknown');
  expect(s.calls[0].init.body).toEqual({request_id:'capture',expected_revision:0});
});
test('an observation operation retains its exact identity and context',async()=>{
  const s=await setup(envelope({source_revision:8,event_ref:'actual-observation',episode_ref:'episode'}));
  const event={kind:'CALIBRATION_EVENT',episode_ref:'episode',event:{kind:'ATTEMPT_OBSERVED',reps:9}};
  expect((await s.client.observe('observation-op',7,event)).state).toBe('confirmed');
  expect(s.calls[0].init.body).toEqual({request_id:'observation-op',expected_revision:7,event});
});
test('owned observation history rejects an event attributed to a different scientific subject',async()=>{
 const {readFileSync}=require('node:fs'),{resolve}=require('node:path');
 const cases=JSON.parse(readFileSync(resolve(__dirname,'../../../../docs/science/sci-p02-initial-policy/stage2-v3/producer-fixtures.v3.json'),'utf8'));
 const request=cases.find((row:any)=>row.request.episodes.length>0).request,episode=request.episodes[0];
 const history={episode_ref:episode.episode_id,kind:'CONTEXT_OPENED',context:episode.context,availability:episode.availability,events:episode.events,preparation:null,setting_choice:null};
 const raw=envelope({source_revision:0,subject_ref:request.subject_ref,blueprint:request.blueprint,observation_progress:[history]});
 expect((await (await setup(raw)).client.read()).state).toBe('confirmed');
 const changed=JSON.parse(JSON.stringify(raw));changed.observation_progress[0].events[0].subject_ref='foreign-subject';
 expect((await (await setup(changed)).client.read()).state).toBe('unknown');
});
