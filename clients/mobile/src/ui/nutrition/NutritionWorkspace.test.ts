import {NutritionWorkspace,applicableNutritionTargets} from './NutritionWorkspace';
import type {NutritionClient} from '../../api/nutrition';
import type {NutritionHead,NutritionEntry} from '../../api/nutritionDTO';

const token='a'.repeat(64);
const consent={contract_version:'nutrition-manual/1.0.0',owner_id:7,purpose:'nutrition_manual',state:'PRESENT',granted:true,wording_version:1,current_wording_version:1,granted_at:'2026-11-12T00:00:00Z',withdrawn_at:null,consent_token:token};
const entry=(changes:Partial<NutritionEntry>={}):NutritionEntry=>({id:1,revision:1,values:{kcal_milli:0,protein_milli:null,carbohydrate_milli:null,fat_milli:null},units:{},provenance:{},recorded_at:'2026-11-12T00:00:00Z',head_token:token,local_day:'2026-11-12',timezone:'Europe/Paris',state:'ACTIVE',declared_complete:false,target_ref:null,...changes});
const head=(day='2026-11-12'):NutritionHead=>({contract_version:'nutrition-manual/1.0.0',owner_id:7,key:{local_day:day},state:'PRESENT',head_token:token,entry:entry({local_day:day})});
function setup(){
 let current=true,sequence=0;const calls:any[]=[];
 const client={ownerId:7,backendScope:'https://qa.invalid',capabilities:async()=>({state:'confirmed',value:{contract_version:'nutrition-manual/1.0.0',owner_id:7,mode:'MANUAL_DAILY',state:'AVAILABLE',can_read:true,can_write:true,assisted_modes:[]}}),consent:async()=>({state:'confirmed',value:consent}),head:async(k:any)=>({state:'confirmed',value:head(k.local_day)}),
  read:async()=>({state:'unknown'}),setConsent:async()=>({state:'unknown'})} as unknown as NutritionClient;
 const recovery={send:async(input:any)=>{calls.push(input);return{state:'unknown'};},verify:async()=>({state:'unknown'}),replay:async()=>({state:'unknown'})};
 const pending={pending:async()=>[]} as any;
 const workspace=new NutritionWorkspace({client,pending,current:()=>current,newId:()=>`new-${++sequence}`,day:'2026-11-12',timezone:'Europe/Paris',notify:()=>{},recovery:recovery as any});
 return{workspace,client,calls,change:()=>{current=false;},recovery};
}
test('fresh consent is required; BODY grant cannot expose NUT values or open acquisition',async()=>{
 const x=setup();x.client.consent=async()=>({state:'confirmed',value:{...consent,granted:false} as any});
 await x.workspace.refresh();expect(x.workspace.state.status).toBe('consent_required');expect(x.workspace.state.head).toBeNull();
 expect(x.workspace.editDay('kcal_milli')).toBe(false);expect(x.calls).toEqual([]);
});
test('editing preserves zero, optional unknowns and frozen revision; blank alone never clears a field',async()=>{
 const x=setup();await x.workspace.refresh();expect(x.workspace.state.head?.entry?.values.kcal_milli).toBe(0);
 expect(x.workspace.editDay('protein_milli')).toBe(true);x.workspace.setDraft('');
 await x.workspace.saveDraft();expect(x.calls).toEqual([]);
 x.workspace.setDraft('1,25');x.workspace.state.head!.head_token='b'.repeat(64);
 await x.workspace.saveDraft();const body=JSON.parse(x.calls[0].payload_json);
 expect(body.values).toEqual({protein_milli:1250});expect(body.expected_head_token).toBe(token);
 expect(body.confirm_complete).toBeNull();expect(x.workspace.state.editor).toBeNull();expect(x.workspace.state.notice).toContain('vérifier');
});
test('completeness is a separate explicit command, never inferred from four values',async()=>{
 const x=setup();await x.workspace.refresh();await x.workspace.setComplete(true);
 expect(JSON.parse(x.calls[0].payload_json)).toMatchObject({operation:'COMPLETE',values:{},confirm_complete:true});
});
test('late read after account change clears numeric state and cannot open an editor',async()=>{
 const x=setup();let finish!:(v:any)=>void;x.client.head=()=>new Promise(r=>{finish=r;});
 const loading=x.workspace.refresh();await Promise.resolve();await Promise.resolve();x.change();finish({state:'confirmed',value:head()});await loading;
 expect(x.workspace.state.head).toBeNull();expect(x.workspace.editDay('kcal_milli')).toBe(false);expect(x.calls).toEqual([]);
});
test('target candidates use latest effective key, disabled does not fall back and future is excluded',()=>{
 const targets=[entry({id:3,variant:'STANDARD',effective_from:'2026-11-01',enabled:true}),entry({id:4,variant:'STANDARD',effective_from:'2026-11-10',enabled:false}),entry({id:5,variant:'TRAINING',effective_from:'2026-11-11',enabled:true}),entry({id:6,variant:'REST',effective_from:'2026-11-20',enabled:true})];
 expect(applicableNutritionTargets(targets,'2026-11-12').map(e=>e.id)).toEqual([5]);
});
test('a refused lookup never enables an unverified replay; recovery failure remains visible',async()=>{
 const x=setup();await x.workspace.refresh();const command={request_id:'pending'} as any;
 x.recovery.verify=async()=>({state:'rejected',status:406,code:'unsupported_contract'} as any);
 await x.workspace.verify(command);expect(x.workspace.state.verified).toBeNull();
 x.recovery.verify=async()=>{throw Error('storage_unavailable');};
 await expect(x.workspace.verify(command)).resolves.toBeUndefined();expect(x.workspace.state.notice).toContain('vérifier');
 expect(x.workspace.state.busy).toBe(false);
});
test('identity mismatch during a write removes all personal facts instead of leaving stale editable values',async()=>{
 const x=setup();await x.workspace.refresh();x.recovery.send=async()=>({state:'changed'} as any);
 x.workspace.editDay('protein_milli');x.workspace.setDraft('12');await x.workspace.saveDraft();
 expect(x.workspace.state.head).toBeNull();expect(x.workspace.state.consent).toBeNull();expect(x.workspace.state.status).toBe('unknown');
});
test('a read-only backend never opens a fresh acquisition even when consent and existing facts are confirmed',async()=>{
 const x=setup();(x.client as any).capabilities=async()=>({state:'confirmed',value:{contract_version:'nutrition-manual/1.0.0',owner_id:7,mode:'MANUAL_DAILY',state:'AVAILABLE',can_read:true,can_write:false,assisted_modes:[]}});
 await x.workspace.refresh();expect(x.workspace.state.head?.entry?.values.kcal_milli).toBe(0);expect(x.workspace.editDay('kcal_milli')).toBe(false);expect(x.calls).toEqual([]);
});
test.each(['consent_required','changed'] as const)('secondary history %s clears numeric facts and invalidates a competing late refresh',async state=>{
 const x=setup();await x.workspace.refresh();let finish!:(v:any)=>void;x.client.head=()=>new Promise(r=>{finish=r;});
 const loading=x.workspace.refresh();for(let i=0;i<8;i++)await Promise.resolve();
 x.client.read=async()=>({state});await x.workspace.history('DAY','2026-11-12');
 finish({state:'confirmed',value:head()});await loading;expect(x.workspace.state.head).toBeNull();expect(x.workspace.state.consent).toBeNull();expect(x.workspace.editDay('kcal_milli')).toBe(false);
});
test('target-head consent refusal removes previously loaded day facts',async()=>{
 const x=setup();await x.workspace.refresh();x.client.head=async()=>({state:'consent_required'});await x.workspace.editTarget('STANDARD','2026-11-12','kcal_milli');expect(x.workspace.state.head).toBeNull();expect(x.workspace.state.editor).toBeNull();
});
test.each(['consent_required','changed'] as const)('a standalone history %s clears all cached facts without a competing refresh',async state=>{
 const x=setup();await x.workspace.refresh();expect(x.workspace.state.head?.entry).not.toBeNull();x.client.read=async()=>({state});
 await x.workspace.history('DAY','2026-11-12');expect(x.workspace.state.head).toBeNull();expect(x.workspace.state.consent).toBeNull();expect(x.workspace.editDay('kcal_milli')).toBe(false);
});
test('bound historical target read refusal cannot leave cached day facts visible',async()=>{
 const x=setup();x.client.head=async()=>({state:'confirmed',value:{...head(),entry:entry({target_ref:99})}});x.client.read=async o=>o.kind==='versions'?{state:'consent_required'}:{state:'unknown'};
 await x.workspace.refresh();expect(x.workspace.state.head).toBeNull();expect(x.workspace.state.consent).toBeNull();
});
test('failed day B read never borrows day A values, while same-day offline retains labelled memory',async()=>{
 const x=setup();await x.workspace.refresh();x.client.head=async()=>({state:'unknown'});await x.workspace.refresh();expect(x.workspace.state.previousHead?.key.local_day).toBe('2026-11-12');
 await x.workspace.selectDay('2026-11-11');expect(x.workspace.state.day).toBe('2026-11-11');expect(x.workspace.state.previousHead).toBeNull();expect(x.workspace.state.head).toBeNull();
});
test('definitive conflict preserves the entered correction and requires explicit review before a new command',async()=>{
 const x=setup();await x.workspace.refresh();x.recovery.send=async(input:any)=>{x.calls.push(input);return{state:'rejected',status:409,code:'stale_head'} as any;};
 x.workspace.editDay('kcal_milli');x.workspace.setDraft('1500');await x.workspace.saveDraft();expect(x.workspace.state.editor?.value).toBe('1500');expect(x.workspace.state.notice).toContain('modifi');
 await x.workspace.saveDraft();expect(x.calls).toHaveLength(1);
 x.client.head=async()=>({state:'confirmed',value:{...head(),head_token:'b'.repeat(64)}});await x.workspace.reviewRefusal();expect(x.workspace.state.editor?.value).toBe('1500');
 await x.workspace.saveDraft();expect(x.calls).toHaveLength(2);expect(JSON.parse(x.calls[1].payload_json).expected_head_token).toBe('b'.repeat(64));
});
