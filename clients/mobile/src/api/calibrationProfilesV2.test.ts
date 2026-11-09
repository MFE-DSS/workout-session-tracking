import {readFileSync} from 'fs';
import {resolve} from 'path';
import {capabilityEnvelope,CALIBRATION_INVENTORY,V3_VERSIONS,createV3Transport,RuntimeV3Client,FirstPlanV3Client} from './firstPlanV3';
import {bindCalibrationCapabilities} from './calibrationProfilesV2';
import {AuthSession} from '../auth/authSession';
import type {Transport} from './http';
import {CalibrationV1Client,calibrationEnvelope} from './calibrationV1';
const read=(name:string)=>JSON.parse(readFileSync(resolve(__dirname,'../../../../',name),'utf8'));
const base='docs/science/sci-p02-initial-policy/';
const selection=read(base+'stage2-v3/authority/registry.v1.json').selection;
const extensions=read(base+'calibration-six-extensions/authority/registry.v1.json');
const pilot=read(base+'first-use-calibration-bootstrap/authority/registry.v1.json');
const fixture=read(base+'calibration-six-extensions/exports/encounter-fixtures.v1.json');
function caps():any {const profiles=selection.map((p:any)=>({...p,load_semantics:p.candidate_id==='romanian-deadlift-halteres'?'PER_IMPLEMENT':'MACHINE_DISPLAY_KG',policy_ref:p.candidate_id===pilot.scope.candidate_id?pilot.policy_ref:extensions.policy_ref}));return {owner_id:7,contract_version:V3_VERSIONS.runtime,versions:V3_VERSIONS,runtime_availability:'NOT_SERVED',controlled_test_available:true,
 controlled_authority:{state:'ACTIVE',generation:1,pins:{registry_digest:'a'.repeat(64),binding_digest:'b'.repeat(64),bundle_digest:'c'.repeat(64),effective_science_digest:'d'.repeat(64)},engine_version:'e',policy_version:'p',binding_ref:'b',start_policy_ref:'s',encounter_bundle_digest:'e'.repeat(64)},
 supported_realizations:profiles.map((p:any)=>({candidate_id:p.candidate_id,intent_id:p.intent_id,realization_ref:p.realization_ref,load_semantics:p.load_semantics,display_name:p.candidate_id,initial_guidance_supported:true})),initial_calibration_pilot:{...selection[0],display_name:'pilot'},
 calibration_inventory:{version:CALIBRATION_INVENTORY,bundle_digest:fixture.authority_digest,profiles,protocol_material:{source_ref:'x',sha256:'a'.repeat(64),text:'x'}}};}
function view(c:any):any {const f=fixture.cases[0];return {encounter_ref:f.result.encounter_ref,source_revision:1,as_of:f.request.as_of,selected:true,result:{...f.result,source_revision:'blueprint-source/1'},allowed_actions:f.result.allowed_actions,authority:{generation:1,encounter_bundle_digest:fixture.authority_digest,inventory_version:CALIBRATION_INVENTORY,packaging_digest:'f'.repeat(64),inventory_bundle_digest:c.calibration_inventory.bundle_digest,policy_ref:extensions.policy_ref,context_fingerprint:'a'.repeat(64),contract_version:V3_VERSIONS.calibration},progress:{context:f.request.context,ledger_complete:true,observed_attempt_count:0,observation_refs:[],acceptance_refs:[]}};}
test('all seven served tuples join without demanding intent/policy on carriers that do not serve them',()=>{expect(capabilityEnvelope(caps(),CALIBRATION_INVENTORY)).not.toBeNull();});
for(const row of selection){
 for(const key of ['intent_id','realization_ref','policy_ref','load_semantics'])test(`${row.candidate_id}: incompatible inventory ${key} closes decoding`,()=>{const c=caps();c.calibration_inventory.profiles.find((p:any)=>p.candidate_id===row.candidate_id)[key]='incompatible';expect(capabilityEnvelope(c,CALIBRATION_INVENTORY)).toBeNull();});
 for(const key of ['intent_id','realization_ref','load_semantics'])test(`${row.candidate_id}: incompatible realization ${key} closes decoding`,()=>{const c=caps();c.supported_realizations.find((p:any)=>p.candidate_id===row.candidate_id)[key]='incompatible';expect(capabilityEnvelope(c,CALIBRATION_INVENTORY)).toBeNull();});
 for(const carrier of ['profiles','supported_realizations'])test(`${row.candidate_id}: ${carrier} omission and duplicate are rejected`,()=>{for(const duplicate of [false,true]){const c=caps(),items=carrier==='profiles'?c.calibration_inventory.profiles:c.supported_realizations;const index=items.findIndex((p:any)=>p.candidate_id===row.candidate_id);if(duplicate)items[(index+1)%7]=items[index];else items.splice(index,1);expect(capabilityEnvelope(c,CALIBRATION_INVENTORY)).toBeNull();}});
}
test('unnegotiated inventory and incompatible pilot are rejected',()=>{const c=caps();expect(capabilityEnvelope(c)).toBeNull();c.initial_calibration_pilot.candidate_id=selection[1].candidate_id;expect(capabilityEnvelope(c,CALIBRATION_INVENTORY)).toBeNull();});
test('encounter authority joins same owner, generation, policy, bundles and current context',()=>{const c=caps(),v=view(c);expect(bindCalibrationCapabilities(v,c,7).allowed_actions).toEqual(v.allowed_actions);
 for(const change of [(x:any)=>x.authority.generation++, (x:any)=>x.authority.policy_ref='other',(x:any)=>x.authority.inventory_bundle_digest='0'.repeat(64),(x:any)=>x.authority.encounter_bundle_digest='0'.repeat(64),(x:any)=>x.progress.context.load_semantics='TOTAL_EXTERNAL',(x:any)=>x.progress.context.realization_ref=selection[0].realization_ref,(x:any)=>x.result.policy_ref='other']){const x=structuredClone(v);change(x);const result=bindCalibrationCapabilities(x,c,7);expect(result.allowed_actions).toEqual([]);expect(result.progress).toEqual(x.progress);expect(result.result).toBeNull();}
 expect(bindCalibrationCapabilities(v,{...c,owner_id:8},7).allowed_actions).toEqual([]);
});
test('UNKNOWN open context keeps help/collection; typed setting and portable context cannot acquire another semantics',()=>{const c=caps(),v=view(c);v.progress.context={...v.progress.context,load_semantics:'UNKNOWN'};expect(bindCalibrationCapabilities(v,c,7).allowed_actions).toEqual(v.allowed_actions);
 v.result.qualified_setting={kind:'ASSISTANCE_SETTING',value:10,unit:'setting'};expect(bindCalibrationCapabilities(v,c,7).allowed_actions).toEqual([]);
 const x=view(c);x.result.portable_episode={context:{...x.progress.context,load_semantics:'PER_IMPLEMENT'},events:[]};expect(bindCalibrationCapabilities(x,c,7).allowed_actions).toEqual([]);
});
test('historical settings keep their own context and value; absent authority adds no permission',()=>{const c=caps(),v=view(c);v.progress.events=[{setting:{kind:'MASS_KG',value:12,unit:'kg'}}];v.progress.setting_choice={setting:{kind:'MASS_KG',value:20,unit:'kg'}};expect(bindCalibrationCapabilities(v,c,7).progress).toEqual(v.progress);v.result=null;v.authority=null;v.allowed_actions=[];expect(bindCalibrationCapabilities(v,null,7)).toEqual(v);});
test('real transport negotiation is required by capabilities consumer, including header echo',async()=>{const c=caps(),headers:any[]=[];const legacy:Transport=async(path)=>(path==='/auth/me'?{id:7}:{access_token:'test',refresh_token:'rt1.fixture.secret',access_expires_in:900,server_now:'2026-11-08T12:00:00Z'}) as any;const auth=new AuthSession(legacy,{read:async()=>null,write:async()=>{},clear:async()=>{}});await auth.login('synthetic','test',null);
 const fetcher:any=async(_url:string,init:any)=>{headers.push(init.headers);return {ok:true,headers:{get:()=>CALIBRATION_INVENTORY},json:async()=>c};};
 const client=(negotiated:boolean)=>new FirstPlanV3Client(new RuntimeV3Client(auth,legacy,createV3Transport('http://localhost',fetcher,negotiated?{calibrationInventory:CALIBRATION_INVENTORY}:undefined)));
 expect((await client(true).capabilities()).state).toBe('confirmed');expect(headers[0]['X-Auren-Calibration-Inventory']).toBe(CALIBRATION_INVENTORY);expect((await client(false).capabilities()).state).toBe('unknown');
});

test('legacy negotiation preserves only the actual pilot path with its own authority',()=>{
 const c=caps();delete c.calibration_inventory;const f=read(base+'first-use-calibration-bootstrap/exports/encounter-fixtures.v1.json');const sample=f.cases[0];
 c.controlled_authority.encounter_bundle_digest=f.authority_digest;
 const v:any={...view(caps()),encounter_ref:sample.result.encounter_ref,result:{...sample.result},progress:{...view(caps()).progress,context:sample.request.context},authority:{...view(caps()).authority,policy_ref:pilot.policy_ref,encounter_bundle_digest:f.authority_digest}};
 delete v.authority.inventory_version;delete v.authority.inventory_bundle_digest;delete v.authority.packaging_digest;
 expect(bindCalibrationCapabilities(v,c,7).allowed_actions).toEqual(v.allowed_actions);
 expect(bindCalibrationCapabilities(view(caps()),c,7).allowed_actions).toEqual([]);
});
for(const row of selection)test(`${row.candidate_id} encounter uses its own tuple and refuses exchanged semantics`,()=>{const candidate=row.candidate_id;
 const c=caps(),v=view(c),p=c.calibration_inventory.profiles.find((row:any)=>row.candidate_id===candidate);
 v.progress.context={...v.progress.context,canonical_exercise_id:candidate,realization_ref:p.realization_ref,load_semantics:p.load_semantics};
 v.authority.policy_ref=p.policy_ref;v.result.policy_ref=p.policy_ref;
 if(candidate===pilot.scope.candidate_id){v.authority.encounter_bundle_digest=c.controlled_authority.encounter_bundle_digest;v.result.authority_digest=c.controlled_authority.encounter_bundle_digest;}
 expect(bindCalibrationCapabilities(v,c,7).allowed_actions).toEqual(v.allowed_actions);
 v.progress.context.load_semantics=p.load_semantics==='PER_IMPLEMENT'?'MACHINE_DISPLAY_KG':'PER_IMPLEMENT';
 expect(bindCalibrationCapabilities(v,c,7).allowed_actions).toEqual([]);
});

test('available optional tuple fields on pilot and realization carriers cannot contradict their compatible tuple',()=>{
 for(const carrier of ['initial_calibration_pilot','supported_realizations'])for(const key of ['intent_id','policy_ref','load_semantics']){
  const c=caps(),row=carrier==='initial_calibration_pilot'?c.initial_calibration_pilot:c.supported_realizations[0];row[key]='incompatible';expect(capabilityEnvelope(c,CALIBRATION_INVENTORY)).toBeNull();
 }
});


test('an inventory2-shaped test port cannot grant read permission without transport negotiation',async()=>{
 const c=caps(),v=view(c);const legacy:Transport=async(path)=>(path==='/auth/me'?{id:7}:{access_token:'test',refresh_token:'rt1.fixture.secret',access_expires_in:900,server_now:'2026-11-08T12:00:00Z'}) as any;
 const auth=new AuthSession(legacy,{read:async()=>null,write:async()=>{},clear:async()=>{}});await auth.login('synthetic','test',null);
 const runtime=new RuntimeV3Client(auth,legacy,async()=>({owner_id:7,contract_version:V3_VERSIONS.runtime,versions:V3_VERSIONS,encounter:v}));
 const result=await new CalibrationV1Client(runtime).read(v.encounter_ref,undefined,c);
 expect(result.state).toBe('confirmed');if(result.state==='confirmed'){expect(result.value.allowed_actions).toEqual([]);expect(result.value.progress).toEqual(v.progress);}
});

test('current qualification matches the selected setting and exact accepted observation, without rewriting earlier settings',()=>{
 const c=caps(),v=view(c),f=fixture.cases.find((row:any)=>row.result.state==='QUALIFIED');
 v.result=structuredClone({...f.result,source_revision:'blueprint-source/1'});v.result.portable_episode.episode_id=v.encounter_ref;
 v.progress.setting_choice=structuredClone(f.request.setting_choice);v.authority.context_fingerprint=f.request.setting_choice.context_fingerprint;
 const old=structuredClone(v.result.portable_episode.events[0]);old.event_id='older';old.setting.value=15;v.result.portable_episode.events.unshift(old);
 expect(bindCalibrationCapabilities(v,c,7).result).not.toBeNull();
 v.result.qualified_setting.value=42;expect(bindCalibrationCapabilities(v,c,7).allowed_actions).toEqual([]);
 v.result.qualified_setting.value=40;v.result.portable_episode.events.find((e:any)=>e.event_id===v.result.reference_event_id).setting.value=41;
 expect(bindCalibrationCapabilities(v,c,7).allowed_actions).toEqual([]);
});
test('current choice fingerprint and explicit capability guidance restriction cannot contradict supplied permission',()=>{
 const c=caps(),v=view(c);v.progress.setting_choice={setting:{kind:'MASS_KG',unit:'kg',value:20},context_fingerprint:'different'};
 expect(bindCalibrationCapabilities(v,c,7).allowed_actions).toEqual([]);
 const x=view(c);x.allowed_actions=['INITIATE_TRIAL'];c.controlled_guidance_available=false;expect(bindCalibrationCapabilities(x,c,7).allowed_actions).toEqual([]);
});


// Complete, read-only published examples adapted only to the owned runtime envelope.
function runtimeView(sample:any,c:any,inventory=true):any {
 const q=structuredClone(sample.request),r=structuredClone(sample.result),events=q.episode?.events??[];
 r.source_revision='blueprint-source/1';if(r.portable_episode)r.portable_episode.episode_id=r.encounter_ref;
 return {encounter_ref:r.encounter_ref,source_revision:1,as_of:q.as_of,selected:true,result:r,allowed_actions:r.allowed_actions,
  authority:{generation:1,encounter_bundle_digest:r.authority_digest,...(inventory?{inventory_version:CALIBRATION_INVENTORY,packaging_digest:'f'.repeat(64),inventory_bundle_digest:c.calibration_inventory.bundle_digest}:{}),policy_ref:r.policy_ref,context_fingerprint:q.setting_choice?.context_fingerprint??'a'.repeat(64),contract_version:V3_VERSIONS.calibration},
  progress:{context:q.context,ledger_complete:true,observed_attempt_count:events.filter((e:any)=>e.kind==='ATTEMPT_OBSERVED').length,observation_refs:events.filter((e:any)=>e.kind==='ATTEMPT_OBSERVED').map((e:any)=>e.event_id),acceptance_refs:events.filter((e:any)=>e.kind==='SETTING_ACCEPTED').map((e:any)=>e.event_id),events,observations:events.filter((e:any)=>e.kind==='ATTEMPT_OBSERVED'),setting_choice:q.setting_choice,preparation:q.preparation}};
}
const decodeView=(v:any,c:any)=>calibrationEnvelope({...c,encounter:v},c);
for(const action of ['INITIATE_TRIAL','ACCEPT_EXACT_SETTING'])for(const change of ['missing','unavailable'])test(`I1 ${action} cannot survive ${change} current choice`,()=>{
 const c=caps(),f=fixture.cases.find((row:any)=>row.result.allowed_actions.includes('INITIATE_TRIAL')),v=runtimeView(f,c);
 if(action==='ACCEPT_EXACT_SETTING'){v.allowed_actions=[action];v.result.allowed_actions=[action];}
 expect(decodeView(v,c)?.allowed_actions).toContain(action);
 if(change==='missing')v.progress.setting_choice=null;else v.progress.setting_choice.available=false;
 const decoded=decodeView(v,c);expect(decoded).not.toBeNull();expect(decoded?.allowed_actions).toEqual([]);expect(decoded?.result).toBeNull();expect(decoded?.progress).toEqual(v.progress);
});
for(const proof of ['trial','acceptance'])for(const field of ['context_fingerprint','subject_ref'])test(`I2 portable ${proof} ${field} must match current owned proof`,()=>{
 const c=caps(),v=runtimeView(fixture.cases.find((row:any)=>row.result.state==='QUALIFIED'),c);
 expect(decodeView(v,c)?.result?.state).toBe('QUALIFIED');
 const eventId=proof==='trial'?v.result.reference_event_id:v.result.acceptance_event_id;
 v.result.portable_episode.events.find((e:any)=>e.event_id===eventId)[field]=field==='context_fingerprint'?'0'.repeat(64):'another-subject';
 const decoded=decodeView(v,c);expect(decoded?.allowed_actions).toEqual([]);expect(decoded?.result).toBeNull();expect(decoded?.progress).toEqual(v.progress);
});
for(const carrier of ['observations','events'])test(`I2 portable qualification must match ${carrier} evidence actually served`,()=>{
 const c=caps(),v=runtimeView(fixture.cases.find((row:any)=>row.result.state==='QUALIFIED'),c);
 v.progress[carrier].find((e:any)=>e.event_id===v.result.reference_event_id).reps=11;
 if(carrier==='events')v.progress.observations=v.progress.events.filter((e:any)=>e.kind==='ATTEMPT_OBSERVED');
 const decoded=decodeView(v,c);expect(decoded?.result).toBeNull();expect(decoded?.allowed_actions).toEqual([]);expect(decoded?.progress).toEqual(v.progress);
});
test('I3 legacy contradictory pilot intent is rejected even on a directly supplied capabilities port',()=>{
 const c=caps(),f=read(base+'first-use-calibration-bootstrap/exports/encounter-fixtures.v1.json');delete c.calibration_inventory;c.controlled_authority.encounter_bundle_digest=f.authority_digest;
 const v=runtimeView(f.cases.find((row:any)=>row.result.allowed_actions.includes('INITIATE_TRIAL')),c,false);
 expect(decodeView(v,c)?.allowed_actions).toContain('INITIATE_TRIAL');
 c.initial_calibration_pilot.intent_id='initial_press_v1';c.supported_realizations[0].intent_id='initial_press_v1';
 expect(capabilityEnvelope(c)).toBeNull();const decoded=decodeView(v,c);expect(decoded?.result).toBeNull();expect(decoded?.allowed_actions).toEqual([]);expect(decoded?.progress).toEqual(v.progress);
});
test('fix1 positive controls preserve UNKNOWN without choice, historical settings and minimal legacy pilot fields',()=>{
 const c=caps(),unknown=runtimeView(fixture.cases[0],c);unknown.progress.context.load_semantics='UNKNOWN';unknown.progress.setting_choice=null;
 expect(decodeView(unknown,c)?.allowed_actions).toEqual(unknown.allowed_actions);
 const qualified=runtimeView(fixture.cases.find((row:any)=>row.result.state==='QUALIFIED'),c);
 const past=structuredClone(qualified.result.portable_episode.events[0]);past.event_id='past-setting';past.setting.value=15;past.sequence=1;
 for(const event of qualified.result.portable_episode.events)event.sequence++;for(const event of qualified.progress.events)event.sequence++;
 qualified.result.portable_episode.events.unshift(past);qualified.progress.events.unshift(structuredClone(past));
 expect(decodeView(qualified,c)?.result?.state).toBe('QUALIFIED');expect(qualified.progress.events[0].setting.value).toBe(15);
 const f=read(base+'first-use-calibration-bootstrap/exports/encounter-fixtures.v1.json');delete c.calibration_inventory;c.controlled_authority.encounter_bundle_digest=f.authority_digest;
 delete c.initial_calibration_pilot.intent_id;delete c.supported_realizations;
 const legacy=runtimeView(f.cases.find((row:any)=>row.result.allowed_actions.includes('INITIATE_TRIAL')),c,false);
 expect(capabilityEnvelope(c)).not.toBeNull();expect(decodeView(legacy,c)?.allowed_actions).toContain('INITIATE_TRIAL');
});
