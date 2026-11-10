/** Owned, negotiated read projection. No command, journal or scientific decision here. */
import { AuthSession } from '../auth/authSession';
import { ApiFailure, type Transport } from './http';
import { isObject, jsonCopy, positiveId, runtimeSchemaMatches } from './firstPlanV3';
import { isStartable, type ReadyMission, type ResumeMission } from './types';

export const MISSION_ACTION_VERSION='mission-action/1.0.0';
export const MISSION_V3_HOST='first-session-runtime/3.0.0';
const V3_PROFILE='first-plan-execution/3.0.0';
export type MissionPath='FIRST_USE'|'HISTORICAL';
export type HistoricalMission=Omit<ReadyMission,'reason'>&{reason:Omit<ReadyMission['reason'],'horizon'|'provenance'>&{horizon:string|null;provenance:string|null}};
type Source='OPEN_SESSION'|'OWNED_FIRST_USE'|'HISTORICAL_MISSION'|'NONE';
type Base={contract_version:typeof MISSION_ACTION_VERSION;owner_id:number;requested_path:MissionPath;observed_at:string;reason:null};
type ResumePayload=ResumeMission&{execution_profile:'LEGACY_V1'|typeof V3_PROFILE};
export type MissionAction = Base & (
 |{state:'RESUME';source:'OPEN_SESSION';primary_action:{kind:'RESUME_LEGACY'|'RESUME_V3';session_id:number};payload:ResumePayload}
 |{state:'FIRST_SESSION_HISTORY';source:'OWNED_FIRST_USE';primary_action:{kind:'OPEN_FIRST_SESSION_HISTORY';session_id:number};payload:ResumePayload}
 |{state:'FIRST_USE';source:'OWNED_FIRST_USE';primary_action:{kind:'OPEN_FIRST_USE'};payload:{execution_profile:typeof V3_PROFILE;calibration_inventory:'plan-calibration-inventory/2.0.0';source_revision:string}}
 |{state:'HISTORICAL_READY';source:'HISTORICAL_MISSION';primary_action:{kind:'START_LEGACY';template_slug:string;decision:ReadyMission['decision']};payload:HistoricalMission}
 |{state:'NO_MISSION';source:'NONE';primary_action:null;payload:null}
) | Omit<Base,'reason'>&(
 |{state:'UNAVAILABLE';source:Source;primary_action:{kind:'REFRESH'}|null;payload:null;reason:string}
 |{state:'CONFLICT';source:'OPEN_SESSION';primary_action:null;payload:null;reason:'MULTIPLE_OPEN_SESSIONS'}
);
export type MissionOutcome={state:'confirmed';value:MissionAction}|{state:'cancelled'|'unknown'}|
 {state:'unavailable';reason:string}|{state:'rejected';status:number;code:string|null};
export type MissionActionTransport=(path:MissionPath,host:boolean,token:string)=>Promise<unknown>;

class NegotiationFailure extends Error {}
export function createMissionActionTransport(baseUrl:string,fetchImpl:typeof fetch=fetch):MissionActionTransport {
 const base=baseUrl.replace(/\/+$/,'');
 return async(path,host,token)=>{
  if(!validPath(path)||typeof host!=='boolean')throw Error('invalid_mission_query');
  const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),10000);
  const headers:Record<string,string>={Accept:'application/json',Authorization:`Bearer ${token}`,'X-Auren-Mission-Action':MISSION_ACTION_VERSION};
  if(host)headers['X-Auren-Mission-V3-Host']=MISSION_V3_HOST;
  try {
   const response=await fetchImpl(`${base}/api/mobile/v1/mission-action?requested_path=${path}`,{method:'GET',headers,credentials:'omit',signal:controller.signal});
   const raw:unknown=await response.json();
   if(!response.ok){const detail=isObject(raw)?raw.detail:null;throw new ApiFailure('http',response.status,isObject(detail)&&typeof detail.error==='string'?detail.error:null);}
   if(response.headers?.get('X-Auren-Mission-Action')!==MISSION_ACTION_VERSION||
      (response.headers?.get('X-Auren-Mission-V3-Host')??null)!==(host?MISSION_V3_HOST:null))throw new NegotiationFailure();
   return raw;
  }catch(error){if(error instanceof ApiFailure||error instanceof NegotiationFailure)throw error;throw new ApiFailure('network');}
  finally{clearTimeout(timer);}
 };
}
function validPath(path:unknown):path is MissionPath{return path==='FIRST_USE'||path==='HISTORICAL';}
const text=(x:unknown):x is string=>typeof x==='string';
const nullableText=(x:unknown)=>x===null||text(x);
const texts=(x:unknown)=>Array.isArray(x)&&x.every(text);
const integer=(x:unknown):x is number=>typeof x==='number'&&Number.isSafeInteger(x)&&x>=0;
const date=(x:unknown)=>runtimeSchemaMatches(x,{type:'string',format:'date-time'});
function exact(x:Record<string,unknown>,keys:string[]){return Object.keys(x).length===keys.length&&keys.every(k=>Object.prototype.hasOwnProperty.call(x,k));}
function decision(x:unknown):x is ReadyMission['decision']{
 return isObject(x)&&exact(x,['fingerprint','policy','top','alternatives'])&&nullableText(x.fingerprint)&&nullableText(x.policy)&&text(x.top)&&texts(x.alternatives);
}
function sameDecision(a:unknown,b:unknown){
 return decision(a)&&decision(b)&&a.fingerprint===b.fingerprint&&a.policy===b.policy&&a.top===b.top&&
  a.alternatives.length===b.alternatives.length&&a.alternatives.every((v,i)=>v===b.alternatives[i]);
}
function historical(x:unknown):x is HistoricalMission {
 if(!isObject(x)||x.state!=='READY'||x.primary_action!=='START'||x.executable!==true||x.duration_estimate!==null)return false;
 const t=x.template,r=x.reason,s=x.scope;
 if(!isObject(t)||!text(t.slug)||!text(t.name)||!nullableText(t.subtitle)||!isObject(r)||!text(r.phrase)||
   !texts(r.reasons)||!texts(r.winning)||!texts(r.limiting)||!nullableText(r.horizon)||!nullableText(r.provenance))return false;
 if(!isObject(s)||!positiveId(s.exercise_count)||!integer(s.work_set_count)||!isObject(s.first_exercise)||
   !text(s.first_exercise.name)||!nullableText(s.first_exercise.set_scheme))return false;
 if(!Array.isArray(x.alternatives)||!x.alternatives.every(a=>isObject(a)&&text(a.slug)&&text(a.name)&&text(a.phrase)&&typeof a.executable==='boolean'))return false;
 if(x.zones!==undefined&&(!Array.isArray(x.zones)||!x.zones.every(z=>isObject(z)&&text(z.zone)&&text(z.label))))return false;
 const alternatives=x.alternatives;
 if(!decision(x.decision)||x.decision.top!==t.slug||!x.decision.alternatives.every((slug,i)=>isObject(alternatives[i])&&slug===alternatives[i].slug)||x.decision.alternatives.length!==alternatives.length)return false;
 // isStartable is the existing canonical structural permission; nullable historical
 // explanation metadata is carried intact rather than fabricated for the old TS type.
 return isStartable(x as unknown as ReadyMission);
}
function resume(x:unknown,id:number):x is ResumePayload {
 if(!isObject(x)||x.state!=='RESUME'||x.primary_action!=='RESUME'||!isObject(x.session))return false;
 const s=x.session,p=x.position;
 if(s.id!==id||!text(s.template_slug)||!text(s.name)||!nullableText(s.subtitle)||!date(s.started_at))return false;
 return p===null||(isObject(p)&&integer(p.exercise_index)&&positiveId(p.exercise_total)&&p.exercise_index<=p.exercise_total&&
  integer(p.sets_done)&&integer(p.sets_total)&&p.sets_done<=p.sets_total&&nullableText(p.exercise_name)&&(p.set_index===null||integer(p.set_index)));
}
export function decodeMissionAction(raw:unknown,owner:number,path:MissionPath,host:boolean):MissionAction|null {
 try {
  const x:unknown=jsonCopy(raw);
  if(!isObject(x)||!exact(x,['contract_version','owner_id','requested_path','observed_at','state','source','primary_action','payload','reason'])||
   x.contract_version!==MISSION_ACTION_VERSION||x.owner_id!==owner||!positiveId(owner)||x.requested_path!==path||!date(x.observed_at))return null;
  const a=x.primary_action,p=x.payload;
  if(x.state==='UNAVAILABLE'){
   const reasons=['SCHEMA_UNAVAILABLE','RUNTIME_NOT_SERVED','AUTHORITY_UNAVAILABLE','EXECUTION_PROFILE_REQUIRED','HISTORICAL_NOT_EXECUTABLE'];
   const source=x.source==='OPEN_SESSION'||x.source===(path==='FIRST_USE'?'OWNED_FIRST_USE':'HISTORICAL_MISSION');
   return source&&p===null&&text(x.reason)&&reasons.includes(x.reason)&&(a===null||(isObject(a)&&exact(a,['kind'])&&a.kind==='REFRESH'))?x as MissionAction:null;
  }
  if(x.state==='CONFLICT')return x.source==='OPEN_SESSION'&&x.reason==='MULTIPLE_OPEN_SESSIONS'&&a===null&&p===null?x as MissionAction:null;
  if(x.reason!==null)return null;
  if(x.state==='NO_MISSION')return path==='HISTORICAL'&&x.source==='NONE'&&a===null&&p===null?x as MissionAction:null;
  if(!isObject(a)||!isObject(p))return null;
  if(x.state==='FIRST_USE')return path==='FIRST_USE'&&host&&x.source==='OWNED_FIRST_USE'&&exact(a,['kind'])&&a.kind==='OPEN_FIRST_USE'&&
   exact(p,['execution_profile','calibration_inventory','source_revision'])&&p.execution_profile===V3_PROFILE&&p.calibration_inventory==='plan-calibration-inventory/2.0.0'&&
   text(p.source_revision)&&/^blueprint-source\/(0|[1-9]\d*)$/.test(p.source_revision)&&Number.isSafeInteger(Number(p.source_revision.slice(17)))?x as MissionAction:null;
  if(x.state==='RESUME'||x.state==='FIRST_SESSION_HISTORY'){
   if(!exact(a,['kind','session_id'])||!positiveId(a.session_id)||!resume(p,a.session_id))return null;
   if(x.state==='FIRST_SESSION_HISTORY')return path==='FIRST_USE'&&host&&x.source==='OWNED_FIRST_USE'&&a.kind==='OPEN_FIRST_SESSION_HISTORY'&&p.execution_profile===V3_PROFILE?x as MissionAction:null;
   if(x.source!=='OPEN_SESSION')return null;
   return (a.kind==='RESUME_LEGACY'&&p.execution_profile==='LEGACY_V1')||(host&&a.kind==='RESUME_V3'&&p.execution_profile===V3_PROFILE)?x as MissionAction:null;
  }
  if(x.state==='HISTORICAL_READY')return path==='HISTORICAL'&&x.source==='HISTORICAL_MISSION'&&exact(a,['kind','template_slug','decision'])&&a.kind==='START_LEGACY'&&
   historical(p)&&a.template_slug===p.template.slug&&sameDecision(a.decision,p.decision)?x as MissionAction:null;
  return null;
 }catch{return null;}
}
export class MissionActionClient {
 constructor(readonly auth:AuthSession,private readonly identity:Transport,private readonly call:MissionActionTransport){}
 async read(path:MissionPath,host:boolean,current:()=>boolean=()=>true):Promise<MissionOutcome>{
  if(!validPath(path)||typeof host!=='boolean')return{state:'unknown'};
  const revision=this.auth.revision,active=()=>revision===this.auth.revision&&current();
  try {
   const owner=await this.auth.authorized(token=>this.identity<{id:number}>('/auth/me',{token}));
   if(!active())return{state:'cancelled'};if(!positiveId(owner?.id))return{state:'unknown'};
   const raw=await this.auth.authorized(token=>{if(!active())throw new ApiFailure('http',401,'stale_identity');return this.call(path,host,token);});
   if(!active())return{state:'cancelled'};
   const parsed=decodeMissionAction(raw,owner.id,path,host);
   return parsed?{state:'confirmed',value:parsed}:{state:'unknown'};
  }catch(error){
   if(!active())return{state:'cancelled'};
   if(error instanceof NegotiationFailure||(error instanceof ApiFailure&&error.kind==='http'&&error.status===406))return{state:'unavailable',reason:'CONTRACT_NOT_SUPPORTED'};
   if(error instanceof ApiFailure&&error.kind==='http'){
    if(error.status>=500)return{state:'unavailable',reason:error.code??'NOT_SERVED'};
    if(error.status>=400&&error.status<500&&![408,429].includes(error.status))return{state:'rejected',status:error.status,code:error.code};
   }
   return{state:'unknown'};
  }
 }
}
