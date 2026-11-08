import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { AuthSession } from '../auth/authSession';
import { ApiFailure,type Transport } from './http';
import { RuntimeV3Client,V3_VERSIONS } from './firstPlanV3';
import { FirstSessionV3Client,commandFromEvaluationV3,executionEnvelope } from './firstSessionV3';

const cases=JSON.parse(readFileSync(resolve(__dirname,'../../../../docs/science/sci-p02-initial-policy/stage2-v3/producer-fixtures.v3.json'),'utf8'));
const owned=(data={})=>({owner_id:7,contract_version:V3_VERSIONS.runtime,versions:V3_VERSIONS,...data});
async function setup(reply:unknown){
 const legacy:Transport=async(path)=>(path==='/auth/me'?{id:7}:{access_token:'test-only',refresh_token:'rt1.fixture.secret',access_expires_in:900,server_now:'2026-11-08T12:00:00Z'}) as any;
 const auth=new AuthSession(legacy,{read:async()=>null,write:async()=>{},clear:async()=>{}});await auth.login('synthetic','test-only',null);
 const calls:any[]=[];let answer=reply;
 const runtime=new RuntimeV3Client(auth,legacy,async(path,init)=>{calls.push({path,init});if(answer instanceof Error)throw answer;return answer;});
 return {client:new FirstSessionV3Client(runtime),calls,answer:(x:unknown)=>{answer=x;}};
}
test('the first session command pins the first ordered scientific session only',()=>{
 const row=cases.find((x:any)=>x.response.start_permission==='ELIGIBLE'),r=row.response;
 const evaluation:any=owned({evaluation_ref:'evaluation',snapshot_ref:r.snapshot_ref,source_revision:4,authority_generation:1,recommendation:r});
 const authority:any=owned({controlled_test_available:true,controlled_authority:{state:'ACTIVE',generation:1,pins:{registry_digest:'a'.repeat(64),binding_digest:r.binding_digest,bundle_digest:r.bundle_digest,effective_science_digest:r.effective_science_digest}}});
 const body=commandFromEvaluationV3(evaluation,authority);
 expect(body?.selected_scientific_session_id).toBe(r.candidate_plan.sessions[0].session_id);
 expect(body).not.toHaveProperty('owner_id');
 expect(body).not.toHaveProperty('exercises');
 expect(commandFromEvaluationV3({...evaluation,recommendation:{...r,start_permission:'REQUIRES_TIME_ACK'}},authority)).toBeNull();
});
test('lost start response remains unknown; reconciliation reads the same key',async()=>{
 const s=await setup(new ApiFailure('network'));
 const body:any={evaluation_ref:'evaluation',selected_scientific_session_id:'session-1'};
 expect((await s.client.submit('stable',body)).state).toBe('unknown');
 expect(s.calls).toHaveLength(1);
 s.answer(owned({request_id:'stable',state:'CREATED',session_id:42,terminal_code:null,scientific_session_id:'session-1',existing_handoff:null}));
 expect((await s.client.readRequest('stable')).state).toBe('confirmed');
 expect(s.calls[1].path).toBe('/me/first-session-requests/stable');
 expect(s.calls[1].init?.method).not.toBe('POST');
});
test('CREATED without a real owned session id is never successful handoff',async()=>{
 const s=await setup(owned({request_id:'stable',state:'CREATED',session_id:null,terminal_code:null,scientific_session_id:'session-1',existing_handoff:null}));
 expect((await s.client.readRequest('stable')).state).toBe('unknown');
});
test('execution refuses an incomplete or malformed prescription before showing work guidance',()=>{
 const r=cases.find((x:any)=>x.response.start_permission==='ELIGIBLE').response;
 const slot=r.candidate_plan.sessions[0].slots[0],prescription=slot.prescription;
 const envelope:any=owned({execution:{contract_version:'first-plan-execution/3.0.0',session_id:1,status:'in_progress',
  exercises:[{se_id:1,canonical_exercise_id:slot.selected.canonical_exercise_id,intent_id:slot.intent_id,prescription,
   sets:Array.from({length:prescription.dose.work_sets},(_,i)=>({set_id:i+1,kind:'work',revision:0,completed:false,reps:null,observation:null})),
   transition_after_exercise:{kind:'BILAN',duration_seconds:null}}],
  applicability:{state:'CURRENT'},observation_only:false,allowed_actions:['NEXT_WORK_SET'],evaluation_ref:'e',binding_digest:'a'.repeat(64),derived_metrics:'NON_EVALUABLE',cursor:{set_id:1}}});
 expect(executionEnvelope(envelope)).not.toBeNull();
 const bad=JSON.parse(JSON.stringify(envelope));bad.execution.exercises[0].prescription.dose.min_reps=true;
 expect(executionEnvelope(bad)).toBeNull();
 delete bad.execution.exercises[0].prescription.dose.min_reps;
 expect(executionEnvelope(bad)).toBeNull();
});
