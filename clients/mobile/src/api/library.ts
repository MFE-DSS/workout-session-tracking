/** Owned source projection. No client recommendation or scientific admission. */
import {AuthSession} from '../auth/authSession';
import {ApiFailure,createTransport,type Transport} from './http';
import {isObject,jsonCopy,positiveId,runtimeSchemaMatches as matches} from './firstPlanV3';
import type {ExecutionPlan} from './types';
import vocabulary from './libraryVocabulary.json';
export const LIBRARY_VERSION='owned-library/1.0.0' as const;
export const LIBRARY_HEADER='X-Auren-Library-Contract';
export type LibrarySection='all'|'programs'|'core'|'utility'|'specialization';
export type LibraryQuery={section:LibrarySection;zone:string|null;limit?:number;cursor?:string|null};
export type LibrarySelection={domain_launchable:boolean;native_support:{state:'SUPPORTED'|'UNSUPPORTED'|'UNKNOWN';reason:null|'NATIVE_EXECUTION_UNSUPPORTED'};selection_ref:string|null};
export type LibraryEntry={kind:'CATALOG_SESSION'|'OWNED_PROGRAM';source_ref:string;name:string;source_status:'AVAILABLE'|'DRAFT'|'VALIDATED'|'PUBLISHED';section:Exclude<LibrarySection,'all'>;counts:{sessions:number|null;exercise_slots:number|null;prescribed_sets:number|null;count_state:'KNOWN'|'PARTIAL'|'UNKNOWN'};zones:{state:'MAPPED'|'NO_ZONES_DEFINED'|'ZONES_UNKNOWN';codes:string[]}};
export type LibraryPage={contract_version:typeof LIBRARY_VERSION;owner_id:number;read_revision:string;section:LibrarySection;requested_zone:string|null;applied_zone:string|null;groups:string[];entries:LibraryEntry[];next_cursor:string|null;collection_state:'PARTIAL'|'COMPLETE'};
export type LibraryExercise={id:number;position:number;name:string;code:string|null;set_scheme:string;notes:string|null;machine_slug:string|null;machine_family:string|null;equipment_context:'UNKNOWN';rep_targets:{set_index:number;min_reps:number;max_reps:number;technique:string|null;is_warmup:boolean}[]};
export type LibraryComposition={source_ref:string;name:string;kind:string;notes:string|null;exercises:LibraryExercise[];selection:LibrarySelection};
export type LibraryDetail={contract_version:typeof LIBRARY_VERSION;owner_id:number;read_revision:string;source:{kind:'CATALOG_SESSION'|'OWNED_PROGRAM'|'OWNED_SESSION';id:number;program_id:number|null;name:string;status:LibraryEntry['source_status'];version:number|null};composition:LibraryComposition[];selection:LibrarySelection|null;limitations:('SOURCE_CONTEXT_UNKNOWN'|'PRESCRIPTION_PARTIAL'|'NATIVE_EXECUTION_UNSUPPORTED')[]};
export type LibraryCreated={contract_version:typeof LIBRARY_VERSION;owner_id:number;request_sha256:string;source_ref:string;execution_profile:'LEGACY';execution:ExecutionPlan};
export type LibraryRefusal={contract_version:typeof LIBRARY_VERSION;owner_id:number;request_sha256:string;effect:'NOT_CREATED';code:string};
export type LibraryOutcome<T>={state:'confirmed';value:T}|{state:'unknown'|'cancelled'|'unavailable'|'changed'};
export type LibraryStartOutcome={state:'created';value:LibraryCreated}|{state:'refused';value:LibraryRefusal}|{state:'unknown'|'cancelled'};
export type LibraryWireReply={status:number;raw:unknown;negotiated:boolean};
export type LibraryPorts={backendScope:string;identity:Transport;sha256:(raw:string)=>Promise<string>;call:(path:string,init:{token:string;method:'GET'|'POST';body?:unknown})=>Promise<LibraryWireReply>};
const obj=(properties:Record<string,unknown>)=>({type:'object',properties,required:Object.keys(properties),additionalProperties:false});
const text={type:'string',maxLength:1024},note={type:'string',maxLength:8192},bool={type:'boolean'},nil={type:'null'};
const nat={type:'integer',minimum:0,maximum:Number.MAX_SAFE_INTEGER},id={...nat,minimum:1};
const ref={type:'string',minLength:1,maxLength:4096,pattern:'^[A-Za-z0-9_-]+\\.[a-f0-9]{64}$'},hash={type:'string',pattern:'^[a-f0-9]{64}$'};
const nullable=(s:unknown)=>({anyOf:[nil,s]}),arr=(items:unknown,maxItems=10000)=>({type:'array',items,maxItems});
const constant=(v:unknown)=>({const:v}),sections=['all','programs','core','utility','specialization'];
const status={enum:['AVAILABLE','DRAFT','VALIDATED','PUBLISHED']},base={contract_version:constant(LIBRARY_VERSION),owner_id:id};
const selection=obj({domain_launchable:bool,native_support:obj({state:{enum:['SUPPORTED','UNSUPPORTED','UNKNOWN']},reason:nullable(constant('NATIVE_EXECUTION_UNSUPPORTED'))}),selection_ref:nullable(ref)});
const entrySchema=obj({kind:{enum:['CATALOG_SESSION','OWNED_PROGRAM']},source_ref:ref,name:text,source_status:status,section:{enum:sections.slice(1)},counts:obj({sessions:nullable(nat),exercise_slots:nullable(nat),prescribed_sets:nullable(nat),count_state:{enum:['KNOWN','PARTIAL','UNKNOWN']}}),zones:obj({state:{enum:['MAPPED','NO_ZONES_DEFINED','ZONES_UNKNOWN']},codes:arr({enum:vocabulary.zones},100)})});
const pageSchema=obj({...base,read_revision:hash,section:{enum:sections},requested_zone:nullable(text),applied_zone:nullable({enum:vocabulary.zones}),groups:arr({enum:sections.slice(1)},4),entries:arr(entrySchema,100),next_cursor:nullable(ref),collection_state:{enum:['PARTIAL','COMPLETE']}});
const targetSchema=obj({set_index:id,min_reps:id,max_reps:id,technique:nullable(text),is_warmup:bool});
const exerciseSchema=obj({id,position:id,name:text,code:nullable(text),set_scheme:text,notes:nullable(note),machine_slug:nullable(text),machine_family:nullable(text),equipment_context:constant('UNKNOWN'),rep_targets:arr(targetSchema,100)});
const compositionSchema=obj({source_ref:ref,name:text,kind:text,notes:nullable(note),exercises:arr(exerciseSchema,200),selection});
const detailSchema=obj({...base,read_revision:hash,source:obj({kind:{enum:['CATALOG_SESSION','OWNED_PROGRAM','OWNED_SESSION']},id,program_id:nullable(id),name:text,status,version:nullable(id)}),composition:arr(compositionSchema,50),selection:nullable(selection),limitations:arr({enum:['SOURCE_CONTEXT_UNKNOWN','PRESCRIPTION_PARTIAL','NATIVE_EXECUTION_UNSUPPORTED']},3)});
const unique=(values:unknown[])=>new Set(values).size===values.length;
const copy=<T,>(raw:unknown,schema:unknown):T|null=>{try{const x=jsonCopy(raw);return matches(x,schema)?x as T:null;}catch{return null;}};
export function decodeLibraryPage(raw:unknown,owner:number,query:Pick<LibraryQuery,'section'|'zone'>):LibraryPage|null{
 const x=copy<LibraryPage>(raw,pageSchema);if(!x||!positiveId(owner)||x.owner_id!==owner||x.section!==query.section||x.requested_zone!==query.zone)return null;
 if(x.applied_zone!==null&&x.applied_zone!==query.zone)return null;
 if((x.next_cursor!==null)!==(x.collection_state==='PARTIAL')||!unique(x.entries.map(e=>e.source_ref))||!unique(x.groups))return null;
 const groups=query.section==='all'?sections.slice(1):[query.section];
 if(JSON.stringify(groups)!==JSON.stringify(x.groups)||x.entries.some(e=>!groups.includes(e.section)))return null;
 for(const e of x.entries){
  if((e.kind==='OWNED_PROGRAM')!==(e.section==='programs')||(e.kind==='CATALOG_SESSION')!==(e.source_status==='AVAILABLE'))return null;
  if(e.counts.count_state==='KNOWN'&&Object.entries(e.counts).some(([k,v])=>k!=='count_state'&&v===null))return null;
  if(!unique(e.zones.codes)||(e.zones.state==='MAPPED')!==(e.zones.codes.length>0))return null;
  if(x.applied_zone!==null&&!e.zones.codes.includes(x.applied_zone))return null;
 }
 return x;
}
function coherentSelection(s:LibrarySelection){
 if((s.native_support.state==='SUPPORTED')!==(s.native_support.reason===null))return false;
 return (s.selection_ref!==null)===(s.domain_launchable&&s.native_support.state==='SUPPORTED');
}
function referenceIdentity(reference:string,owner:number):{kind:string;id:number;program_id:number|null}|null{
 try{
  if(!matches(reference,ref))return null;
  const encoded=reference.split('.')[0].replace(/-/g,'+').replace(/_/g,'/');
  // Public reference payload is a coherence check only, never HMAC authority.
  const x=JSON.parse(atob(encoded+'='.repeat((4-encoded.length%4)%4)));
  if(!isObject(x)||x.kind!=='source'||!isObject(x.binding)||x.binding.owner!==owner||x.binding.contract!==LIBRARY_VERSION||!isObject(x.value))return null;
  const v=x.value;if(!['CATALOG_SESSION','OWNED_PROGRAM','OWNED_SESSION'].includes(String(v.kind))||!positiveId(v.id)||(v.program_id!==null&&!positiveId(v.program_id)))return null;
  return v as {kind:string;id:number;program_id:number|null};
 }catch{return null;}
}
export function decodeLibraryDetail(raw:unknown,owner:number,requestedRef:string):LibraryDetail|null{
 const x=copy<LibraryDetail>(raw,detailSchema);if(!x||!positiveId(owner)||x.owner_id!==owner||!unique(x.limitations)||!unique(x.composition.map(s=>s.source_ref)))return null;
 const requested=referenceIdentity(requestedRef,owner);
 if(!requested||requested.kind!==x.source.kind||requested.id!==x.source.id||requested.program_id!==x.source.program_id)return null;
 const p=x.source.kind==='OWNED_PROGRAM',personal=x.source.kind!=='CATALOG_SESSION';
 if(p!==(x.selection===null)||(!p&&x.composition.length!==1)||(personal===(x.source.status==='AVAILABLE'))||(personal!==(x.source.version!==null))||(x.source.kind==='OWNED_SESSION')!==(x.source.program_id!==null))return null;
 const ids:number[]=[];
 for(const s of x.composition){
  const actual=referenceIdentity(s.source_ref,owner),expectedProgram=p?x.source.id:x.source.program_id;
  if(!actual||actual.kind!==(personal?'OWNED_SESSION':'CATALOG_SESSION')||actual.program_id!==expectedProgram||(!p&&(actual.id!==x.source.id||s.source_ref!==requestedRef)))return null;
  if(!coherentSelection(s.selection)||!unique(s.exercises.map(e=>e.position)))return null;
  if(personal&&x.source.status!=='PUBLISHED'&&s.selection.domain_launchable)return null;
  if(s.selection.native_support.state==='SUPPORTED'&&(s.kind!=='strength'||!s.exercises.length||s.exercises.some(e=>!e.rep_targets.some(r=>!r.is_warmup))))return null;
  for(const e of s.exercises){ids.push(e.id);if(!unique(e.rep_targets.map(r=>`${r.set_index}/${r.is_warmup}`))||e.rep_targets.some(r=>r.max_reps<r.min_reps))return null;}
 }
 if(!unique(ids)||ids.length>200)return null;
 if(!p&&JSON.stringify(x.selection)!==JSON.stringify(x.composition[0].selection))return null;
 return x;
}
const instant={type:'string',format:'date-time'},number={type:'number',minimum:0},zoneSchema=obj({zone:text,label:text});
const executionExerciseSchema=obj({se_id:id,code:text,prescribed_name:text,executed_name:text,set_scheme:nullable(text),rep_range:nullable(obj({min:id,max:id})),guidance:nullable(obj({state:text,intent_label:text,target_summary:nullable(text),reasons:arr(text),is_silent:bool})),previous:nullable(obj({relative:nullable(text),weights:nullable(text),reps:nullable(text)})),prefill:obj({weight_kg:nullable(number),reps:nullable(nat),origin:{enum:['OVERLOAD_TARGET','LAST_SET','NONE']}}),substitutes:arr(text),substitute_options:arr(obj({name:text,level:{enum:['N1','N2','N3']},badge:text,rationale:nullable(text)})),zone:nullable(zoneSchema),secondary_zones:arr(zoneSchema),rest_seconds:nullable(nat),best:nullable(obj({weight_kg:number,reps:nat}))});
const transition={oneOf:[obj({kind:constant('BILAN')}),obj({kind:constant('REST_THEN_SET'),set_id:id}),obj({kind:constant('REST_THEN_EXERCISE'),set_id:id,se_id:id})]};
const executionSchema=obj({session_id:id,template_slug:text,template_name:text,status:constant('in_progress'),excluded_from_stats:constant(false),started_at:instant,ended_at:nil,server_now:instant,rest_default_seconds:nat,exercises:arr(executionExerciseSchema,200),sets:arr(obj({set_id:id,se_id:id,index:id}),10000),on_complete:{type:'object',additionalProperties:transition},done:obj({}),cursor_set_id:id,allowed_actions:arr({enum:['COMPLETE_SET','FINISH','PAUSE','ABANDON']},4)});
const createdSchema=obj({...base,request_sha256:hash,source_ref:ref,execution_profile:constant('LEGACY'),execution:executionSchema});
export function decodeLibraryCreated(raw:unknown,owner:number,digest:string,sourceRef:string):LibraryCreated|null{
 const x=copy<LibraryCreated>(raw,createdSchema);if(!x||x.owner_id!==owner||x.request_sha256!==digest||x.source_ref!==sourceRef)return null;
 const e=x.execution;
 if(e.template_slug==='science:v3:first-session'||!e.exercises.length||!e.sets.length||!unique(e.exercises.map(v=>v.se_id))||!unique(e.sets.map(s=>s.set_id))||e.cursor_set_id!==e.sets[0].set_id)return null;
 if(JSON.stringify(e.allowed_actions)!==JSON.stringify(['COMPLETE_SET','FINISH','PAUSE','ABANDON'])||Object.keys(e.on_complete).length!==e.sets.length)return null;
 for(let i=0;i<e.sets.length;i++){
  const s=e.sets[i],next=e.sets[i+1],t=e.on_complete[String(s.set_id)];if(!e.exercises.some(x=>x.se_id===s.se_id)||!t)return null;
  if(!next){if(t.kind!=='BILAN')return null;}
  else if(t.kind==='BILAN'||t.set_id!==next.set_id||(s.se_id===next.se_id?t.kind!=='REST_THEN_SET':t.kind!=='REST_THEN_EXERCISE'||t.se_id!==next.se_id))return null;
 }
 return x;
}
const refusalSchema=obj({...base,request_sha256:hash,effect:constant('NOT_CREATED'),code:text});
const definite:Record<number,string[]>={403:['acquisition_unavailable'],404:['foreign_or_missing'],406:['unsupported_contract'],409:['stale_selection','session_open','start_blocked'],413:['source_too_large'],422:['invalid_request']};
export function decodeLibraryRefusal(raw:unknown,status:number,owner:number,digest:string):LibraryRefusal|null{
 const x=copy<LibraryRefusal>(raw,refusalSchema);return x&&x.owner_id===owner&&x.request_sha256===digest&&definite[status]?.includes(x.code)?x:null;
}
export const libraryStartBody=(selectionRef:string)=>({contract_version:LIBRARY_VERSION,selection_ref:selectionRef});
export const libraryStartJSON=(selectionRef:string)=>JSON.stringify(libraryStartBody(selectionRef));
export function createLibraryPorts(baseUrl:string,fetchImpl:typeof fetch,sha256:LibraryPorts['sha256']):LibraryPorts{
 const url=new URL(baseUrl);if(url.username||url.password||url.search||url.hash||!['http:','https:'].includes(url.protocol))throw Error('invalid_library_backend');
 const base=baseUrl.replace(/\/+$/,'');
 return {backendScope:base,identity:createTransport(base,fetchImpl),sha256,
  call:async(path,init)=>{
   if(!path.startsWith('/me/library')||path.includes('://')||path.includes('#'))throw Error('invalid_library_path');
   const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),20000);
   try{
    const response=await fetchImpl(base+'/api/mobile/v1'+path,{method:init.method,credentials:'omit',signal:controller.signal,
     headers:{Accept:'application/json',Authorization:`Bearer ${init.token}`,[LIBRARY_HEADER]:LIBRARY_VERSION,...(init.body?{'Content-Type':'application/json'}:{})},body:init.body?JSON.stringify(init.body):undefined});
    return {status:response.status,raw:await response.json(),negotiated:response.headers?.get(LIBRARY_HEADER)===LIBRARY_VERSION};
   }finally{clearTimeout(timer);}
  }};
}
export class LibraryClient{
 constructor(readonly auth:AuthSession,readonly ports:LibraryPorts){}
 get backendScope(){return this.ports.backendScope;}
 async owner(current:()=>boolean=()=>true):Promise<number|null>{
  const revision=this.auth.revision;
  const x=await this.auth.authorized(token=>this.ports.identity<{id:number}>('/auth/me',{token}));
  return revision===this.auth.revision&&current()&&positiveId(x?.id)?x.id:null;
 }
 private async read<T>(path:string,parse:(raw:unknown,owner:number)=>T|null,current:()=>boolean):Promise<LibraryOutcome<T>>{
  const revision=this.auth.revision,active=()=>revision===this.auth.revision&&current();
  try{
   const owner=await this.owner(active);if(!active())return{state:'cancelled'};if(owner===null)return{state:'unknown'};
   const r=await this.auth.authorized(token=>{if(!active())throw new ApiFailure('http',401);return this.ports.call(path,{method:'GET',token});});
   if(!active())return{state:'cancelled'};if(!r.negotiated)return{state:'unknown'};
   if(r.status===409&&isObject(r.raw)&&isObject(r.raw.detail)&&r.raw.detail.error==='source_changed')return{state:'changed'};
   if(r.status!==200)return{state:'unavailable'};
   const value=parse(r.raw,owner);return value?{state:'confirmed',value}:{state:'unknown'};
  }catch{return active()?{state:'unknown'}:{state:'cancelled'};}
 }
 page(query:LibraryQuery,current:()=>boolean=()=>true):Promise<LibraryOutcome<LibraryPage>>{
  const limit=query.limit??30;if(!sections.includes(query.section)||!Number.isSafeInteger(limit)||limit<1||limit>100)return Promise.resolve({state:'unknown'});
  const q=new URLSearchParams({section:query.section,limit:String(limit)});if(query.zone!==null)q.set('zone',query.zone);if(query.cursor)q.set('cursor',query.cursor);
  return this.read('/me/library?'+q,(raw,owner)=>decodeLibraryPage(raw,owner,query),current);
 }
 detail(sourceRef:string,current:()=>boolean=()=>true):Promise<LibraryOutcome<LibraryDetail>>{
  if(!matches(sourceRef,ref))return Promise.resolve({state:'unknown'});
  return this.read('/me/library/items/'+encodeURIComponent(sourceRef),(raw,owner)=>decodeLibraryDetail(raw,owner,sourceRef),current);
 }
 async start(owner:number,selectionRef:string,sourceRef:string,digest:string,current:()=>boolean=()=>true):Promise<LibraryStartOutcome>{
  const revision=this.auth.revision,active=()=>revision===this.auth.revision&&current();
  try{
   if(!positiveId(owner)||!matches(selectionRef,ref)||!matches(sourceRef,ref)||!matches(digest,hash)||await this.ports.sha256(libraryStartJSON(selectionRef))!==digest)return{state:'unknown'};
   if(await this.owner(active)!==owner)return active()?{state:'unknown'}:{state:'cancelled'};
   const r=await this.auth.authorized(async token=>{
    if(!active())throw new ApiFailure('http',401);
    const identity=await this.ports.identity<{id:number}>('/auth/me',{token});
    if(!active()||identity?.id!==owner)throw new ApiFailure('http',401);
    return this.ports.call('/me/library/start',{method:'POST',token,body:libraryStartBody(selectionRef)});
   },{retryUnauthorized:false});
   if(!active())return{state:'cancelled'};if(!r.negotiated)return{state:'unknown'};
   if(r.status===201){const value=decodeLibraryCreated(r.raw,owner,digest,sourceRef);return value?{state:'created',value}:{state:'unknown'};}
   const value=decodeLibraryRefusal(r.raw,r.status,owner,digest);return value?{state:'refused',value}:{state:'unknown'};
  }catch{return active()?{state:'unknown'}:{state:'cancelled'};}
 }
}
