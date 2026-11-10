/** Owned historical reads. This adapter exposes no workout or measurement command. */
import {AuthSession} from '../auth/authSession';
import type {ExecutionV3} from '../domain/planV3Types';
import {ApiFailure,type Transport} from './http';
import {jsonCopy,positiveId,runtimeSchemaMatches} from './firstPlanV3';
import type {FirstSessionV3Client} from './firstSessionV3';

export type HistoryPeriod='4w'|'12w'|'all';
export type HistoryWindow={period:HistoryPeriod;time_zone:string;from:string|null;until:string};
export type HistoryContext={owner_id:number;read_id:string;read_context:string;window:HistoryWindow};
type LegacyDescriptor={execution_profile:'LEGACY_V1';prescription:'UNKNOWN_NOT_CAPTURED';equipment_context:'UNKNOWN_NOT_CAPTURED';mapping:{se_id:number;position:number;code:string;name:string}[]};
type ScienceDescriptor={execution_profile:'SCI_V3';binding_digest:string;execution_profile_version:'first-plan-execution/3.0.0';mapping:{se_id:number;slot_id:string;intent_id:string;canonical_exercise_id:string;set_ids:number[]}[]};
type UnknownDescriptor={execution_profile:'UNKNOWN';reason:'SCHEMA_UNAVAILABLE'|'BINDING_UNAVAILABLE'};
export type HistoryEntry={session_id:number;started_at:string;ended_at:string|null;status:string;excluded_from_stats:boolean;template_slug:string;name:string;entry_ref:string;execution_profile:'LEGACY_V1'|'SCI_V3'|'UNKNOWN';descriptor:LegacyDescriptor|ScienceDescriptor|UnknownDescriptor};
export type HistoryPage=HistoryContext&{contract_version:'training-history/1.0.0';state:'AVAILABLE'|'EMPTY';membership:'LIVE_BOUNDED_MEMBERSHIP';counts_read_at:string;rows_read_at:string;
 counts:{state:'AVAILABLE';recorded:number;completed:number;open:number;excluded:number;completed_with_work:number};weekly_counts:{week_from:string;week_until:string;completed_with_work:number;partial_current_week:boolean}[];
 planned_calendar:{state:'NOT_PERSISTED';count:null};completeness:'COMPLETE'|'MORE_AVAILABLE';next_cursor:string|null;entries:HistoryEntry[]};
type Identity={namespace:'LEGACY_EXERCISE'|'SCI_CANONICAL_EXERCISE';id:string};
export type ExerciseIndexEntry={exercise_ref:string;identity:Identity;name:string};
export type HistoryOccurrence=Omit<HistoryEntry,'ended_at'|'template_slug'>&{se_id:number;position:number;identity:Identity;occurrence_ref:string;comparison:'NON_COMPARABLE'};
export type ExercisePage<T>={contract_version:string;owner_id:number;read_id:string;window:HistoryWindow;rows_read_at:string;state:'AVAILABLE'|'EMPTY'|'SCANNING';entries:T[];scan:'EXHAUSTED'|'PARTIAL_SCAN';source_inspected:number;unresolved_count:number;coverage_complete:boolean;next_cursor:string|null};
type LegacySet={set_id:number;kind:string;set_index:number;completed:boolean;reps:number|null;raw_reps_repr?:string;weight_kg:number|null;raw_weight_repr:string|null;completed_at:string|null};
export type LegacySessionFacts={contract_version:'training-session-facts/1.0.0';owner_id:number;read_id:string;window:HistoryWindow;rows_read_at:string;execution_profile:'LEGACY_V1';prescription:'UNKNOWN_NOT_CAPTURED';timezone_basis:'DATABASE_UTC_CONVENTION';
 selected_se_id?:number;session:{session_id:number;name:string;template_slug:string;started_at:string;ended_at:string|null;status:string;excluded_from_stats:boolean};
 cardio:{duration_min:number|null;bpm_avg:number|null;machine_calories:number|null;machine_type:string|null};
 exercises:{se_id:number;position:number;code:string;prescribed_name:string;executed_name:string;substituted_name:string|null;prescription:'UNKNOWN_NOT_CAPTURED';equipment_context:'UNKNOWN_NOT_CAPTURED';load_semantics:'UNKNOWN';sets:LegacySet[]}[]};
type HistoricalSet=Omit<ExecutionV3['exercises'][number]['sets'][number],'transition_after_set'>;
type HistoricalExercise=Omit<ExecutionV3['exercises'][number],'transition_after_exercise'|'sets'>&{sets:HistoricalSet[]};
export type HistoricalScienceExecution=Omit<ExecutionV3,'allowed_actions'|'applicability'|'observation_only'|'cursor'|'exercises'>&{exercises:HistoricalExercise[]};
export type HistoricalDetail={kind:'LEGACY';facts:LegacySessionFacts}|{kind:'SCI';execution:HistoricalScienceExecution};
export type HistoryOutcome<T>={state:'confirmed';value:T}|{state:'unknown'|'cancelled'|'changed'|'unavailable'}|{state:'rejected';status:number;code:string|null};

const root='/me/training-history';
const text={type:'string'},nonempty={type:'string',minLength:1},bool={type:'boolean'},nil={type:'null'};
const natural={type:'integer',minimum:0,maximum:Number.MAX_SAFE_INTEGER},id={...natural,minimum:1};
const signedInteger={type:'integer',minimum:-Number.MAX_SAFE_INTEGER,maximum:Number.MAX_SAFE_INTEGER};
const number={type:'number'},instant={type:'string',format:'date-time'};
const ref={type:'string',minLength:1,maxLength:16384,pattern:'^[A-Za-z0-9_-]+\\.[a-f0-9]{64}$'};
const hash={type:'string',pattern:'^[a-f0-9]{64}$'},readId={type:'string',pattern:'^[a-f0-9]{32}$'};
const constant=(value:unknown)=>({const:value});
const nullable=(schema:unknown)=>({anyOf:[nil,schema]});
const array=(items:unknown)=>({type:'array',items});
function object(properties:Record<string,unknown>,optional:string[]=[]){return{type:'object',properties,required:Object.keys(properties).filter(k=>!optional.includes(k)),additionalProperties:false};}
const windowSchema=object({period:{enum:['4w','12w','all']},time_zone:nonempty,from:nullable(instant),until:instant});
const legacyMapping=object({se_id:id,position:signedInteger,code:text,name:text});
const scienceMapping=object({se_id:id,slot_id:nonempty,intent_id:nonempty,canonical_exercise_id:nonempty,set_ids:{...array(id),minItems:1}});
const descriptorSchema={oneOf:[object({execution_profile:constant('LEGACY_V1'),prescription:constant('UNKNOWN_NOT_CAPTURED'),equipment_context:constant('UNKNOWN_NOT_CAPTURED'),mapping:array(legacyMapping)}),
 object({execution_profile:constant('SCI_V3'),binding_digest:hash,execution_profile_version:constant('first-plan-execution/3.0.0'),mapping:{...array(scienceMapping),minItems:1}}),
 object({execution_profile:constant('UNKNOWN'),reason:{enum:['SCHEMA_UNAVAILABLE','BINDING_UNAVAILABLE']}})]};
const entryProperties={session_id:id,started_at:instant,status:nonempty,excluded_from_stats:bool,name:text,entry_ref:ref,execution_profile:{enum:['LEGACY_V1','SCI_V3','UNKNOWN']},descriptor:descriptorSchema};
const entrySchema=object({...entryProperties,ended_at:nullable(instant),template_slug:text});
const identitySchema=object({namespace:{enum:['LEGACY_EXERCISE','SCI_CANONICAL_EXERCISE']},id:nonempty});
const occurrenceSchema=object({...entryProperties,se_id:id,position:signedInteger,identity:identitySchema,occurrence_ref:ref,comparison:constant('NON_COMPARABLE')});
const countsSchema=object({state:constant('AVAILABLE'),recorded:natural,completed:natural,open:natural,excluded:natural,completed_with_work:natural});
const weeklySchema=object({week_from:instant,week_until:instant,completed_with_work:natural,partial_current_week:bool});
const pageSchema=object({contract_version:constant('training-history/1.0.0'),owner_id:id,state:{enum:['AVAILABLE','EMPTY']},read_id:readId,read_context:ref,window:windowSchema,
 membership:constant('LIVE_BOUNDED_MEMBERSHIP'),counts_read_at:instant,rows_read_at:instant,counts:countsSchema,weekly_counts:array(weeklySchema),planned_calendar:object({state:constant('NOT_PERSISTED'),count:nil}),
 completeness:{enum:['COMPLETE','MORE_AVAILABLE']},next_cursor:nullable(ref),entries:array(entrySchema)});
const legacySetSchema=object({set_id:id,kind:nonempty,set_index:signedInteger,completed:bool,reps:nullable(signedInteger),raw_reps_repr:nonempty,weight_kg:nullable(number),raw_weight_repr:nullable(nonempty),completed_at:nullable(instant)},['raw_reps_repr']);
const legacyExerciseSchema=object({se_id:id,position:signedInteger,code:text,prescribed_name:text,executed_name:text,substituted_name:nullable(text),prescription:constant('UNKNOWN_NOT_CAPTURED'),equipment_context:constant('UNKNOWN_NOT_CAPTURED'),load_semantics:constant('UNKNOWN'),sets:array(legacySetSchema)});
const factsSchema=object({contract_version:constant('training-session-facts/1.0.0'),owner_id:id,read_id:readId,window:windowSchema,rows_read_at:instant,execution_profile:constant('LEGACY_V1'),prescription:constant('UNKNOWN_NOT_CAPTURED'),timezone_basis:constant('DATABASE_UTC_CONVENTION'),selected_se_id:id,
 session:object({session_id:id,name:text,template_slug:text,started_at:instant,ended_at:nullable(instant),status:nonempty,excluded_from_stats:bool}),
 cardio:object({duration_min:nullable(signedInteger),bpm_avg:nullable(signedInteger),machine_calories:nullable(signedInteger),machine_type:nullable(text)}),exercises:array(legacyExerciseSchema)},['selected_se_id']);
const matches=(value:unknown,schema:unknown)=>runtimeSchemaMatches(value,schema);
const sameWindow=(a:HistoryWindow,b:HistoryWindow)=>a.period===b.period&&a.time_zone===b.time_zone&&a.from===b.from&&a.until===b.until;
const sameTime=(a:string,b:string)=>a.replace(/\+00:00$/,'Z')===b.replace(/\+00:00$/,'Z');
const unique=(values:unknown[])=>new Set(values).size===values.length;
function coherentEntry(entry:HistoryEntry|HistoryOccurrence){
 if(entry.execution_profile!==entry.descriptor.execution_profile)return false;
 const d=entry.descriptor;if(d.execution_profile==='UNKNOWN')return true;
 if(!unique(d.mapping.map(m=>m.se_id)))return false;
 if(d.execution_profile==='SCI_V3')return unique(d.mapping.map(m=>m.slot_id))&&unique(d.mapping.flatMap(m=>m.set_ids));
 return unique(d.mapping.map(m=>m.position));
}
function parsePage(raw:unknown,owner:number,period:HistoryPeriod,timeZone:string):HistoryPage|null{
 if(!matches(raw,pageSchema))return null;const x=raw as HistoryPage;
 if(x.owner_id!==owner||x.window.period!==period||x.window.time_zone!==timeZone||(period==='all')!==(x.window.from===null)||Date.parse(x.window.until)<=Date.parse(x.window.from??'0001-01-01T00:00:00Z'))return null;
 if((x.state==='EMPTY')!==(x.entries.length===0)||(x.completeness==='MORE_AVAILABLE')!==(x.next_cursor!==null)||(!x.entries.length&&x.next_cursor!==null))return null;
 if(!unique(x.entries.map(e=>e.session_id))||x.entries.some(e=>!coherentEntry(e)))return null;
 if(period==='all'&&x.weekly_counts.length)return null;
 if(period!=='all'&&x.weekly_counts.length!==(period==='4w'?4:12))return null;
 return x;
}
function parseExercisePage<T>(raw:unknown,owner:number,context:HistoryContext,occurrences:boolean):ExercisePage<T>|null{
 const row=occurrences?occurrenceSchema:object({exercise_ref:ref,identity:identitySchema,name:text});
 const schema=object({contract_version:constant(occurrences?'training-exercise-occurrences/1.0.0':'training-exercise-index/1.0.0'),owner_id:id,read_id:readId,window:windowSchema,rows_read_at:instant,state:{enum:['AVAILABLE','EMPTY','SCANNING']},entries:array(row),scan:{enum:['EXHAUSTED','PARTIAL_SCAN']},source_inspected:{...natural,maximum:1000},unresolved_count:{...natural,maximum:1000},coverage_complete:bool,next_cursor:nullable(ref)});
 if(!matches(raw,schema))return null;const x=raw as ExercisePage<T>;
 if(x.owner_id!==owner||x.read_id!==context.read_id||!sameWindow(x.window,context.window)||x.coverage_complete!==(x.scan==='EXHAUSTED')||x.coverage_complete!==(x.next_cursor===null))return null;
 if(x.state!==(x.entries.length?'AVAILABLE':x.coverage_complete?'EMPTY':'SCANNING')||x.unresolved_count>x.source_inspected)return null;
 if(occurrences&&x.entries.some(e=>!coherentEntry(e as HistoryOccurrence)))return null;
 return x;
}
function parseLegacy(raw:unknown,owner:number,context:HistoryContext,entry:HistoryEntry|HistoryOccurrence):LegacySessionFacts|null{
 if(!matches(raw,factsSchema))return null;const x=raw as LegacySessionFacts;
 if(x.owner_id!==owner||x.read_id!==context.read_id||!sameWindow(x.window,context.window)||x.session.session_id!==entry.session_id||!sameTime(x.session.started_at,entry.started_at))return null;
 if('occurrence_ref' in entry&&x.selected_se_id!==entry.se_id)return null;
 const descriptor=entry.descriptor;if(descriptor.execution_profile!=='LEGACY_V1'||x.exercises.length!==descriptor.mapping.length)return null;
 const ids:number[]=[];
 for(let i=0;i<x.exercises.length;i++){
  const exercise=x.exercises[i],m=descriptor.mapping[i];
  if(exercise.se_id!==m.se_id||exercise.position!==m.position||exercise.code!==m.code||exercise.prescribed_name!==m.name)return null;
  for(const set of exercise.sets){if((set.raw_weight_repr!==null&&set.weight_kg!==null)||(set.raw_reps_repr!==undefined&&set.reps!==null))return null;ids.push(set.set_id);}
 }
 return unique(ids)?x:null;
}
const typedContextSchema=object({canonical_exercise_id:nonempty,context_ref:nonempty,realization_ref:nonempty,equipment_ref:nonempty,side:constant('BILATERAL'),load_semantics:{enum:['TOTAL_EXTERNAL','PER_IMPLEMENT','MACHINE_DISPLAY_KG']}});
const typedSettingSchema=object({kind:constant('MASS_KG'),value:{type:'number',minimum:0},unit:constant('kg')});
const observationSchema=object({setting:nullable(typedSettingSchema),context:typedContextSchema,reps:nullable(natural),completed:bool,performed_at:instant,performed_at_estimated:bool},['performed_at_estimated']);
function contextKnown(raw:unknown):boolean{return matches(raw,typedContextSchema);}
const contextKeys=['canonical_exercise_id','context_ref','realization_ref','equipment_ref','side','load_semantics'] as const;
const sameContext=(a:unknown,b:unknown)=>contextKnown(a)&&contextKnown(b)&&contextKeys.every(k=>(a as any)[k]===(b as any)[k]);
function historicalScience(value:ExecutionV3,entry:HistoryEntry|HistoryOccurrence):HistoricalScienceExecution|null{
 const descriptor=entry.descriptor;
 if(descriptor.execution_profile!=='SCI_V3'||value.session_id!==entry.session_id||value.binding_digest!==descriptor.binding_digest||!matches(value.started_at,instant)||!sameTime(value.started_at,entry.started_at)||!matches(value.server_now,instant)||!matches(value.ended_at,nullable(instant))||value.exercises.length!==descriptor.mapping.length)return null;
 for(let i=0;i<value.exercises.length;i++){
  const e=value.exercises[i],m=descriptor.mapping[i];
  if(e.se_id!==m.se_id||e.slot_id!==m.slot_id||e.intent_id!==m.intent_id||e.canonical_exercise_id!==m.canonical_exercise_id||e.prescription.context.canonical_exercise_id!==e.canonical_exercise_id||e.sets.length!==m.set_ids.length)return null;
  for(let j=0;j<e.sets.length;j++){
   const s=e.sets[j],o=s.observation;
   if(s.set_id!==m.set_ids[j]||s.set_index!==j+1||!matches(s.completed_at,nullable(instant)))return null;
   if(o!==null){
    if(!matches(o,observationSchema)||s.revision<1||o.reps!==s.reps||o.completed!==s.completed||(o.completed&&o.reps===null)||!sameContext(o.context,e.prescription.context))return null;
   }else if(s.revision!==0)return null;
  }
 }
 const {allowed_actions:_actions,applicability:_applicability,observation_only:_observation,cursor:_cursor,exercises,...facts}=value;
 return{...facts,exercises:exercises.map(({transition_after_exercise:_transition,sets,...e})=>({...e,sets:sets.map(({transition_after_set:_rest,...s})=>s)}))};
}
/** Equality of observed typed context only; never a score, conversion or progression rule. */
export function comparisonKey(input:{profile:string;exercise?:HistoricalExercise}):string|null{
 const e=input.exercise;if(input.profile!=='SCI_V3'||!e)return null;
 const observation=e.sets.find(s=>s.observation?.setting!==null&&s.observation?.setting!==undefined)?.observation;
 if(!observation?.setting||!sameContext(observation.context,e.prescription.context)||observation.setting.kind!=='MASS_KG'||observation.setting.unit!=='kg')return null;
 return JSON.stringify([e.canonical_exercise_id,e.intent_id,...contextKeys.slice(1).map(k=>observation.context[k]),observation.setting.kind,observation.setting.unit]);
}
export class TrainingHistoryClient{
 constructor(private readonly auth:AuthSession,private readonly call:Transport,private readonly typed?:Pick<FirstSessionV3Client,'execution'>){}
 private async owned<T>(send:(owner:number)=>Promise<HistoryOutcome<T>>,current:()=>boolean=()=>true):Promise<HistoryOutcome<T>>{
  const revision=this.auth.revision,active=()=>revision===this.auth.revision&&current();
  try{
   const owner=await this.auth.authorized(token=>this.call<{id:number}>('/auth/me',{token}));
   if(!active())return{state:'cancelled'};if(!positiveId(owner?.id))return{state:'unknown'};
   const result=await send(owner.id);return active()?jsonCopy(result):{state:'cancelled'};
  }catch(error){
   if(!active())return{state:'cancelled'};
   if(error instanceof ApiFailure&&error.kind==='http'){
    if(error.status===409&&error.code==='READ_CHANGED'||error.status===404&&error.code==='history_entry_not_found')return{state:'changed'};
    if(error.status===404||error.status===406||error.status>=500)return{state:'unavailable'};
    if(error.status>=400&&error.status<500&&![408,429].includes(error.status))return{state:'rejected',status:error.status,code:error.code};
   }
   return{state:'unknown'};
  }
 }
 private get(path:string){return this.auth.authorized(token=>this.call<unknown>(path,{token}));}
 sessions(options:{period:HistoryPeriod;timeZone:string;limit?:number;cursor?:string},current?:()=>boolean):Promise<HistoryOutcome<HistoryPage>>{
  let o:typeof options;try{o=jsonCopy(options);}catch{return Promise.resolve({state:'unknown'});}
  const limit=o.limit??50;if(!['4w','12w','all'].includes(o.period)||typeof o.timeZone!=='string'||!o.timeZone||!matches(limit,{...natural,minimum:1,maximum:100})||(o.cursor!==undefined&&!matches(o.cursor,ref)))return Promise.resolve({state:'unknown'});
  return this.owned<HistoryPage>(async owner=>{const raw=await this.get(`${root}?period=${o.period}&time_zone=${encodeURIComponent(o.timeZone)}&limit=${limit}${o.cursor===undefined?'':`&cursor=${encodeURIComponent(o.cursor)}`}`);
   const value=parsePage(raw,owner,o.period,o.timeZone);return value?{state:'confirmed',value}:{state:'unknown'};},current);
 }
 private scan<T>(context:HistoryContext,exerciseRef:string|undefined,options:{limit?:number;cursor?:string},current?:()=>boolean):Promise<HistoryOutcome<ExercisePage<T>>>{
  let c:HistoryContext,o:typeof options;try{c=jsonCopy(context);o=jsonCopy(options);}catch{return Promise.resolve({state:'unknown'});}
  const limit=o.limit??50;if(!matches(c.read_context,ref)||!matches(limit,{...natural,minimum:1,maximum:100})||(o.cursor!==undefined&&!matches(o.cursor,ref))||(exerciseRef!==undefined&&!matches(exerciseRef,ref)))return Promise.resolve({state:'unknown'});
  return this.owned<ExercisePage<T>>(async owner=>{if(owner!==c.owner_id)return{state:'unknown'};
   const raw=await this.get(`${root}/exercises${exerciseRef===undefined?'':`/${encodeURIComponent(exerciseRef)}`}?read_context=${encodeURIComponent(c.read_context)}&limit=${limit}${o.cursor===undefined?'':`&cursor=${encodeURIComponent(o.cursor)}`}`);
   const value=parseExercisePage<T>(raw,owner,c,exerciseRef!==undefined);return value?{state:'confirmed',value}:{state:'unknown'};},current);
 }
 exercises(context:HistoryContext,options:{limit?:number;cursor?:string}={},current?:()=>boolean){return this.scan<ExerciseIndexEntry>(context,undefined,options,current);}
 occurrences(context:HistoryContext,exerciseRef:string,options:{limit?:number;cursor?:string}={},current?:()=>boolean){return this.scan<HistoryOccurrence>(context,exerciseRef,options,current);}
 detail(context:HistoryContext,entry:HistoryEntry|HistoryOccurrence,current?:()=>boolean):Promise<HistoryOutcome<HistoricalDetail>>{
  let c:HistoryContext,e:HistoryEntry|HistoryOccurrence;try{c=jsonCopy(context);e=jsonCopy(entry);}catch{return Promise.resolve({state:'unknown'});}
  if(!matches(e,'occurrence_ref' in e?occurrenceSchema:entrySchema)||!coherentEntry(e))return Promise.resolve({state:'unknown'});
  return this.owned<HistoricalDetail>(async owner=>{
   if(owner!==c.owner_id)return{state:'unknown'};
   try{
    const raw=await this.get(`${root}/sessions/${e.session_id}?entry_ref=${encodeURIComponent(e.entry_ref)}${'occurrence_ref' in e?`&occurrence_ref=${encodeURIComponent(e.occurrence_ref)}`:''}`);
    if(e.execution_profile!=='LEGACY_V1')return{state:'unknown'};
    const facts=parseLegacy(raw,owner,c,e);return facts?{state:'confirmed',value:{kind:'LEGACY',facts}}:{state:'unknown'};
   }catch(error){
    if(!(error instanceof ApiFailure&&error.kind==='http'&&error.status===409&&error.code==='execution_profile_required'))throw error;
    if(e.execution_profile!=='SCI_V3'||!this.typed)return{state:'unknown'};
    const result=await this.typed.execution(e.session_id,current);
    if(result.state!=='confirmed')return result.state==='cancelled'?{state:'cancelled'}:{state:'unknown'};
    const execution=historicalScience(result.value,e);return execution?{state:'confirmed',value:{kind:'SCI',execution}}:{state:'unknown'};
   }
  },current);
 }
}
