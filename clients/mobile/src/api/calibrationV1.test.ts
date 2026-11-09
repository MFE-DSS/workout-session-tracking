import { AuthSession } from '../auth/authSession';
import type { Transport } from './http';
import { RuntimeV3Client,V3_VERSIONS } from './firstPlanV3';
import { CalibrationV1Client } from './calibrationV1';

async function setup(raw:unknown) {
 const legacy:Transport=async(path)=>(path==='/auth/me'?{id:7}:{access_token:'test-only',refresh_token:'rt1.fixture.secret',access_expires_in:900,server_now:'2026-11-08T12:00:00Z'}) as any;
 const auth=new AuthSession(legacy,{read:async()=>null,write:async()=>{},clear:async()=>{}});await auth.login('synthetic','test-only',null);
 const calls:any[]=[];const runtime=new RuntimeV3Client(auth,legacy,async(path,init)=>{calls.push({path,init});return raw;});
 return {client:new CalibrationV1Client(runtime),calls};
}
const envelope=(data={})=>({owner_id:7,contract_version:V3_VERSIONS.runtime,versions:V3_VERSIONS,...data});
test('opening the first encounter sends no seven-setting or anthropometry prerequisite',async()=>{
 const s=await setup(envelope({encounter_ref:'encounter',source_revision:1}));
 const context={canonical_exercise_id:'leg-extensions-assises',realization_ref:null,equipment_ref:null,context_ref:null,side:'BILATERAL' as const,load_semantics:'UNKNOWN' as const};
 expect((await s.client.open('stable-open',0,context,'UNKNOWN','UNKNOWN')).state).toBe('confirmed');
 expect(s.calls[0].init.body).toEqual({request_id:'stable-open',expected_revision:0,context,availability:'UNKNOWN',concern_state:'UNKNOWN'});
});
test('history remains visible without converting unavailable current permission into a fresh trial',async()=>{
 const history={encounter_ref:'encounter',source_revision:5,as_of:'2026-11-08T12:00:00Z',result:null,authority:null,runtime_availability:'NOT_SERVED',allowed_actions:[],
   progress:{ledger_complete:true,observed_attempt_count:1,observation_refs:['actual-trial'],acceptance_refs:[]}};
 const s=await setup(envelope({encounter:history}));
 const result=await s.client.read('encounter');
 expect(result.state).toBe('confirmed');
 if(result.state==='confirmed'){
  expect(result.value.progress.observation_refs).toEqual(['actual-trial']);
  expect(result.value.allowed_actions).toEqual([]);
 }
});
test('an incomplete ledger cannot be presented as zero actual observations',async()=>{
 const s=await setup(envelope({encounter:{encounter_ref:'encounter',source_revision:5,as_of:'2026-11-08T12:00:00Z',result:null,authority:null,allowed_actions:[],
   progress:{ledger_complete:false,observed_attempt_count:0,observation_refs:[],acceptance_refs:[]}}}));
 expect((await s.client.read('encounter')).state).toBe('unknown');
});

test('an unnegotiated client cannot expose inventory2 permission supplied by a valid-looking response',async()=>{
 const fixture=require('../../../../docs/science/sci-p02-initial-policy/calibration-six-extensions/exports/encounter-fixtures.v1.json');
 const f=fixture.cases[0],result={...f.result,source_revision:'blueprint-source/1'};
 const history={encounter_ref:result.encounter_ref,source_revision:1,as_of:f.request.as_of,result,selected:true,allowed_actions:result.allowed_actions,
 authority:{generation:1,encounter_bundle_digest:fixture.authority_digest,inventory_version:'plan-calibration-inventory/2.0.0',packaging_digest:'a'.repeat(64),inventory_bundle_digest:fixture.authority_digest,policy_ref:result.policy_ref,context_fingerprint:'b'.repeat(64),contract_version:V3_VERSIONS.calibration},
 progress:{context:f.request.context,ledger_complete:true,observed_attempt_count:0,observation_refs:[],acceptance_refs:[]}};
 const s=await setup(envelope({encounter:history}));const response=await s.client.read(result.encounter_ref);
 expect(response.state).toBe('confirmed');if(response.state==='confirmed'){expect(response.value.allowed_actions).toEqual([]);expect(response.value.progress.context).toEqual(f.request.context);}
});
