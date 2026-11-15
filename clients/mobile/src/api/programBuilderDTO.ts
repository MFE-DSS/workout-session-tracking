/** Factual projections: current-name resolution does not prove original selection. */
import {BUILDER_VERSION,BUILDER_OPERATIONS,BUILDER_MAX_BYTES,builderExact,builderId,builderHash,builderKey,builderText,builderByteLength,type PreparedBuilderCommand,type BuilderSelection,type BuilderOperation,type BuilderCommand,type BuilderTreeSession} from '../domain/programBuilderCommand';
export type BuilderReceipt={contract_version:typeof BUILDER_VERSION;owner_id:number;command_id:string;request_sha256:string;operation:BuilderOperation;program_id:number;resulting_source_digest:string;resulting_version:number;publication_ids:number[];selections:(BuilderSelection&{slot_id:number})[];recorded_at:string};
export type BuilderProgramSummary={id:number;title:string;status:'draft'|'validated'|'published'|'archived';version:number;source_digest:string};
export type BuilderExerciseOption=BuilderSelection&{equipment_family:string|null;movement_pattern:string|null};
export type BuilderSourceTarget={set_index:number;min_reps:number;max_reps:number;technique:string|null;is_warmup:boolean};
export type BuilderSourceIdentity={state:'RESOLVED_CURRENT_NAME';slug:string;name:string;ekb_version:string}|{state:'UNRESOLVED';slug:null;name:null;ekb_version:null};
export type BuilderSourceExercise={slot_id:number;slot_digest:string;position:number;exercise_name:string;set_scheme:string;variant_key:string|null;variant_group:string|null;equipment_family:string|null;movement_pattern:string|null;notes:string|null;source_reason:string|null;rep_targets:BuilderSourceTarget[];identity:BuilderSourceIdentity};
export type BuilderSourceSession={position:number;name:string;kind:'strength'|'cardio';focus:string;duration_target_minutes:number|null;notes:string|null;exercises:BuilderSourceExercise[]};
export type BuilderProgram=BuilderProgramSummary&{slug_base:string;sessions:BuilderSourceSession[];publication_ids:number[]};
export type BuilderProgramRead={contract_version:typeof BUILDER_VERSION;owner_id:number;program:BuilderProgram};
export type BuilderPage<T>={contract_version:typeof BUILDER_VERSION;owner_id:number;items:T[];next_cursor:string|null};
export type BuilderProgramsPage=BuilderPage<BuilderProgramSummary>;
export type BuilderExercisesPage=BuilderPage<BuilderExerciseOption>;
const integer=(v:unknown):v is number=>typeof v==='number'&&Number.isSafeInteger(v);
const nullableText=(v:unknown,max:number)=>v===null||builderText(v,max,true);
const ids=(v:unknown,max=1000):v is number[]=>Array.isArray(v)&&v.length<=max&&v.every(builderId)&&new Set(v).size===v.length;
export function builderResponseBounded(value:unknown):boolean{try{const json=JSON.stringify(value);return typeof json==='string'&&builderByteLength(json)<=BUILDER_MAX_BYTES;}catch{return false;}}
const owned=(raw:Record<string,unknown>,owner:number)=>builderId(owner)&&raw.owner_id===owner&&raw.contract_version===BUILDER_VERSION;
function selected(v:unknown):v is BuilderSelection{return builderExact(v,['slug','name','ekb_version'])&&builderText(v.slug,96)&&builderText(v.name,255)&&builderText(v.ekb_version,128);}
export function builderInstant(v:unknown):v is string{
 if(typeof v!=='string'||v.length>64)return false;
 const m=/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.\d{1,6})?(Z|[+-](\d{2}):(\d{2}))$/.exec(v);
 if(!m||!Number.isFinite(Date.parse(v)))return false;
 const [y,mo,d,h,mi,s]=m.slice(1,7).map(Number),leap=y%4===0&&(y%100!==0||y%400===0),days=[31,leap?29:28,31,30,31,30,31,31,30,31,30,31];
 return mo>=1&&mo<=12&&d>=1&&d<=days[mo-1]&&h<24&&mi<60&&s<60&&(m[7]==='Z'||Number(m[8])<=23&&Number(m[9])<60);
}
export function decodeBuilderReceipt(raw:unknown,owner:number,expected:PreparedBuilderCommand):BuilderReceipt|null{
 if(!builderResponseBounded(raw)||!builderExact(raw,['contract_version','owner_id','command_id','request_sha256','operation','program_id','resulting_source_digest','resulting_version','publication_ids','selections','recorded_at'])||!owned(raw,owner)||expected.owner_id!==owner||raw.command_id!==expected.command_id||!builderKey(raw.command_id)||raw.request_sha256!==expected.request_sha256||!builderHash(raw.request_sha256)||raw.operation!==expected.operation||!BUILDER_OPERATIONS.includes(raw.operation as BuilderOperation)||!builderId(raw.program_id)||expected.program_id!==null&&raw.program_id!==expected.program_id||!builderHash(raw.resulting_source_digest)||!builderId(raw.resulting_version)||!ids(raw.publication_ids,7)||!Array.isArray(raw.selections)||raw.selections.length>70||!builderInstant(raw.recorded_at))return null;
 if(expected.operation==='CREATE'&&(raw.resulting_version!==1||raw.publication_ids.length!==0)||expected.operation==='NEW_CYCLE'&&(raw.resulting_version as number)<2||expected.operation==='PUBLISH'&&raw.publication_ids.length===0)return null;
 let selections:BuilderSelection[]=[];
 try{const body=JSON.parse(expected.payload_json) as BuilderCommand;if(body.operation==='SAVE_TREE')selections=(body.payload as {sessions:BuilderTreeSession[]}).sessions.flatMap(s=>s.exercises.flatMap(e=>e.selection?[e.selection]:[]));}catch{return null;}
 if(raw.selections.length!==selections.length)return null;
 const slots=new Set<number>();
 for(let i=0;i<selections.length;i++){const row=raw.selections[i],want=selections[i];
  if(!builderExact(row,['slot_id','slug','name','ekb_version'])||!builderId(row.slot_id)||slots.has(row.slot_id)||!selected({slug:row.slug,name:row.name,ekb_version:row.ekb_version})||row.slug!==want.slug||row.name!==want.name||row.ekb_version!==want.ekb_version)return null;slots.add(row.slot_id);}
 return raw as BuilderReceipt;
}
const summaryKeys=['id','title','status','version','source_digest'];
function summary(v:Record<string,unknown>):boolean{return builderId(v.id)&&builderText(v.title,128)&&typeof v.status==='string'&&['draft','validated','published','archived'].includes(v.status)&&builderId(v.version)&&builderHash(v.source_digest);}
function identity(v:unknown):v is BuilderSourceIdentity{if(!builderExact(v,['state','slug','name','ekb_version']))return false;return v.state==='UNRESOLVED'?v.slug===null&&v.name===null&&v.ekb_version===null:v.state==='RESOLVED_CURRENT_NAME'&&selected({slug:v.slug,name:v.name,ekb_version:v.ekb_version});}
function sourceExercise(v:unknown,slots:Set<number>):v is BuilderSourceExercise{
 if(!builderExact(v,['slot_id','slot_digest','position','exercise_name','set_scheme','variant_key','variant_group','equipment_family','movement_pattern','notes','source_reason','rep_targets','identity'])||!builderId(v.slot_id)||slots.has(v.slot_id)||!builderHash(v.slot_digest)||!builderId(v.position)||!builderText(v.exercise_name,255)||!builderText(v.set_scheme,255,true)||!nullableText(v.variant_key,128)||!nullableText(v.variant_group,128)||!nullableText(v.equipment_family,64)||!nullableText(v.movement_pattern,64)||!nullableText(v.notes,BUILDER_MAX_BYTES)||!nullableText(v.source_reason,255)||!identity(v.identity)||v.identity.state==='RESOLVED_CURRENT_NAME'&&v.identity.name!==v.exercise_name||!Array.isArray(v.rep_targets)||v.rep_targets.length>1000)return false;
 slots.add(v.slot_id);const keys=new Set<string>();let previous=-Infinity;
 for(const rt of v.rep_targets){if(!builderExact(rt,['set_index','min_reps','max_reps','technique','is_warmup'])||!integer(rt.set_index)||rt.set_index<previous||!integer(rt.min_reps)||!integer(rt.max_reps)||!nullableText(rt.technique,8)||typeof rt.is_warmup!=='boolean')return false;const key=`${rt.set_index}/${rt.is_warmup}`;if(keys.has(key))return false;keys.add(key);previous=rt.set_index;}
 return true;
}
export function decodeBuilderProgram(raw:unknown,owner:number,id:number):BuilderProgramRead|null{
 if(!builderResponseBounded(raw)||!builderExact(raw,['contract_version','owner_id','program'])||!owned(raw,owner)||!builderId(id)||!builderExact(raw.program,[...summaryKeys,'slug_base','sessions','publication_ids']))return null;
 const p=raw.program;if(p.id!==id||!summary(p)||!builderText(p.slug_base,64)||!ids(p.publication_ids,1000)||!Array.isArray(p.sessions)||p.sessions.length>1000)return null;
 const slots=new Set<number>();let sessionPosition=0;
 for(const s of p.sessions){if(!builderExact(s,['position','name','kind','focus','duration_target_minutes','notes','exercises'])||!builderId(s.position)||s.position<=sessionPosition||!builderText(s.name,128)||!['strength','cardio'].includes(s.kind as string)||!builderText(s.focus,128,true)||s.duration_target_minutes!==null&&!integer(s.duration_target_minutes)||!nullableText(s.notes,BUILDER_MAX_BYTES)||!Array.isArray(s.exercises)||s.exercises.length>1000)return null;
  sessionPosition=s.position;let position=0;for(const e of s.exercises){if(!sourceExercise(e,slots)||e.position<=position)return null;position=e.position;}}
 return raw as BuilderProgramRead;
}
export function builderReadQuery(kind:'programs'|'exercises',limit=25,cursor?:string):string{
 if(!builderId(limit)||limit>50||cursor!==undefined&&(!builderText(cursor,4096)||!/^[-A-Za-z0-9_]+=*$/.test(cursor)))throw Error('invalid_builder_query');
 return `/me/program-builder/${kind}?limit=${limit}`+(cursor===undefined?'':`&cursor=${encodeURIComponent(cursor)}`);
}
function page<T>(raw:unknown,owner:number,limit:number,cursor:string|undefined,item:(v:unknown)=>boolean,key:(v:any)=>string|number):BuilderPage<T>|null{
 if(!builderResponseBounded(raw)||!builderExact(raw,['contract_version','owner_id','items','next_cursor'])||!owned(raw,owner)||!builderId(limit)||limit>50||!Array.isArray(raw.items)||raw.items.length>limit||raw.next_cursor!==null&&(!builderText(raw.next_cursor,4096)||!/^[-A-Za-z0-9_]+=*$/.test(raw.next_cursor)||raw.next_cursor===cursor||raw.items.length!==limit))return null;
 const keys=new Set<string|number>();let previous:string|number|undefined;for(const row of raw.items){if(!item(row))return null;const k=key(row);if(keys.has(k)||previous!==undefined&&k<=previous)return null;keys.add(k);previous=k;}return raw as BuilderPage<T>;
}
export function decodeBuilderPrograms(raw:unknown,owner:number,limit=25,cursor?:string):BuilderProgramsPage|null{return page(raw,owner,limit,cursor,v=>builderExact(v,summaryKeys)&&summary(v),v=>v.id);}
export function decodeBuilderExercises(raw:unknown,owner:number,limit=25,cursor?:string):BuilderExercisesPage|null{return page(raw,owner,limit,cursor,v=>builderExact(v,['slug','name','ekb_version','equipment_family','movement_pattern'])&&selected({slug:v.slug,name:v.name,ekb_version:v.ekb_version})&&nullableText(v.equipment_family,64)&&nullableText(v.movement_pattern,64),v=>v.slug);}
