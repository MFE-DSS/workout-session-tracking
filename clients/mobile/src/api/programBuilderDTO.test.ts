import {prepareBuilderCommand,BUILDER_VERSION} from '../domain/programBuilderCommand';
import {decodeBuilderReceipt,decodeBuilderProgram,decodeBuilderPrograms,decodeBuilderExercises} from './programBuilderDTO';
const sha=async(s:string)=>require('node:crypto').createHash('sha256').update(s).digest('hex');
const hash='a'.repeat(64);
const envelope=(value:object)=>({contract_version:BUILDER_VERSION,owner_id:7,...value});
const root=()=>({id:3,title:'Programme',slug_base:'programme',status:'draft',version:1,source_digest:hash,publication_ids:[],sessions:[]});
const historical=()=>({...root(),sessions:[{position:1,name:'Ancienne',kind:'strength',focus:'',duration_target_minutes:null,notes:null,exercises:[{slot_id:8,slot_digest:hash,position:1,exercise_name:'Ancien mouvement',set_scheme:'8x100',variant_key:null,variant_group:null,equipment_family:null,movement_pattern:null,notes:null,source_reason:null,rep_targets:Array.from({length:8},(_,i)=>({set_index:i+1,min_reps:100,max_reps:101,technique:null,is_warmup:false})),identity:{state:'UNRESOLVED',slug:null,name:null,ekb_version:null}}]}]});
const command=()=>prepareBuilderCommand(7,'https://qa.invalid',{contract_version:BUILDER_VERSION,command_id:'one',operation:'CREATE',program_id:null,expected_source_digest:null,payload:{title:'Programme'}},sha);
const receipt=async()=>{const p=await command();return {contract_version:BUILDER_VERSION,owner_id:7,command_id:'one',request_sha256:p.request_sha256,operation:'CREATE',program_id:3,resulting_source_digest:hash,resulting_version:1,publication_ids:[],selections:[],recorded_at:'2026-11-15T12:30:00Z'};};
test('exact owned bare receipt acknowledges the prepared command',async()=>{
 expect(decodeBuilderReceipt(await receipt(),7,await command())).toEqual(await receipt());
});
test('receipt rejects changed identity, bytes, root, shape, integers and malformed instants',async()=>{
 const p=await command(),r=await receipt();
 for(const change of [{owner_id:8},{command_id:'two'},{request_sha256:'b'.repeat(64)},{operation:'RENAME'},{program_id:3.5},{resulting_version:0},{resulting_source_digest:'A'.repeat(64)},{publication_ids:[1,1]},{recorded_at:'2026-02-30T00:00:00Z'},{selections:[{slot_id:4,slug:'x',name:'x',ekb_version:'1'}]},{extra:true}])expect(decodeBuilderReceipt({...r,...change},7,p)).toBeNull();
 expect(decodeBuilderReceipt({receipt:r},7,p)).toBeNull();
 expect(decodeBuilderReceipt(r,8,p)).toBeNull();
});
test('owned historical tree preserves old targets and unresolved metadata independently of new input bounds',()=>{
 const raw=envelope({program:historical()});expect(decodeBuilderProgram(raw,7,3)).toEqual(raw);
});
test('tree rejects unknown fields, contradictory identity, duplicate slot ids and malformed prescription scalars',()=>{
 const raw:any=envelope({program:historical()});
 const slot=()=>raw.program.sessions[0].exercises[0];
 slot().identity.slug='made-up';expect(decodeBuilderProgram(raw,7,3)).toBeNull();slot().identity.slug=null;
 slot().rep_targets[0].min_reps=1.5;expect(decodeBuilderProgram(raw,7,3)).toBeNull();slot().rep_targets[0].min_reps=100;
 raw.program.sessions[0].exercises.push({...slot(),position:2});expect(decodeBuilderProgram(raw,7,3)).toBeNull();raw.program.sessions[0].exercises.pop();
 slot().unreviewed=true;expect(decodeBuilderProgram(raw,7,3)).toBeNull();
 expect(decodeBuilderProgram(envelope({program:root()}),7,4)).toBeNull();
});
test('empty owned page is confirmed while foreign, oversized, duplicate and nonprogressing pages are unknown',()=>{
 const empty=envelope({items:[],next_cursor:null});expect(decodeBuilderPrograms(empty,7)).toEqual(empty);
 expect(decodeBuilderExercises(empty,7)).toEqual(empty);
 expect(decodeBuilderPrograms({...empty,owner_id:8},7)).toBeNull();
 expect(decodeBuilderPrograms({...empty,next_cursor:'same'},7)).toBeNull();
 const {sessions:_,slug_base:__,publication_ids:___,...summary}=root();
 expect(decodeBuilderPrograms(envelope({items:[summary,summary],next_cursor:null}),7)).toBeNull();
 expect(decodeBuilderPrograms(envelope({items:[summary],next_cursor:'same'}),7,1,'same')).toBeNull();
 const option={slug:'press',name:'Press',ekb_version:'1',equipment_family:'machine',movement_pattern:'push'};
 expect(decodeBuilderExercises(envelope({items:[option],next_cursor:null}),7,1)).toEqual(envelope({items:[option],next_cursor:null}));
 expect(decodeBuilderExercises(envelope({items:[option,option],next_cursor:null}),7,1)).toBeNull();
});
test('nullable picker facts remain unknown and current-name resolution is factual rather than selection proof',()=>{
 const option={slug:'press',name:'Press',ekb_version:'1',equipment_family:null,movement_pattern:null},raw=envelope({items:[option],next_cursor:null});expect(decodeBuilderExercises(raw,7)).toEqual(raw);
 const source:any=envelope({program:historical()});source.program.sessions[0].exercises[0].exercise_name='Press';source.program.sessions[0].exercises[0].identity={state:'RESOLVED_CURRENT_NAME',slug:'press',name:'Press',ekb_version:'1'};expect(decodeBuilderProgram(source,7,3)).toEqual(source);
});
test('SAVE receipt proves each explicit selection in order and cannot attribute a preserved slot',async()=>{
 const selection={slug:'press',name:'Press',ekb_version:'1'};
 const p=await prepareBuilderCommand(7,'https://qa.invalid',{contract_version:BUILDER_VERSION,command_id:'save',operation:'SAVE_TREE',program_id:3,expected_source_digest:hash,payload:{sessions:[{position:1,name:'S',kind:'strength',focus:'',duration_target_minutes:null,notes:null,exercises:[{position:1,selection,keep:null,notes:null,rep_targets:[{min_reps:1,max_reps:2,technique:null,is_warmup:false}]},{position:2,selection:null,keep:{slot_id:9,slot_digest:hash},rep_targets:null,notes:null}]}]}},sha);
 const r={...await receipt(),command_id:'save',operation:'SAVE_TREE',request_sha256:p.request_sha256,selections:[{slot_id:8,...selection}]};expect(decodeBuilderReceipt(r,7,p)).toEqual(r);
 for(const change of [{program_id:4},{selections:[]},{selections:[{slot_id:8,...selection,name:'Other'}]},{selections:[...r.selections,{slot_id:9,...selection}]}])expect(decodeBuilderReceipt({...r,...change},7,p)).toBeNull();
});
test('resolved identity must name the actual slot and oversized sources remain unknown',()=>{
 const raw:any=envelope({program:historical()});raw.program.sessions[0].exercises[0].identity={state:'RESOLVED_CURRENT_NAME',slug:'press',name:'Press',ekb_version:'1'};expect(decodeBuilderProgram(raw,7,3)).toBeNull();
 raw.program.sessions[0].exercises[0].identity={state:'UNRESOLVED',slug:null,name:null,ekb_version:null};raw.program.sessions[0].notes='é'.repeat(70000);expect(decodeBuilderProgram(raw,7,3)).toBeNull();
});
