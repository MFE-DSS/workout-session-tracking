/** BODY-01: source-aware facts and exact owned commands, parallel to weight v1. */
import {AuthSession} from '../auth/authSession';
import {ApiFailure,type CallInit,type Transport} from './http';

export const BODY_CONTRACT='body-measurements/1.0.0' as const;
export const BODY_KEYS=['weight_kg','waist_cm','neck_cm','chest_cm','shoulder_width_cm','arm_cm_left','arm_cm_right','thigh_cm_left','thigh_cm_right','hip_cm','calf_cm_left','calf_cm_right','wingspan_cm'] as const;
export type BodyKey=typeof BODY_KEYS[number];
export type BodyValue={value:number|null;raw_value_repr:string|null;quality:'MISSING'|'KNOWN'|'LEGACY_OUTSIDE_CURRENT_BOUNDS'|'INVALID_NONFINITE';unit:'kg'|'cm';provenance:{origin:'UNKNOWN'|'USER_DECLARED';acquisition:'UNKNOWN'|'MANUAL_ENTRY'|'MANUAL_CORRECTION';source_ref:string}};
export type BodyEntry={root_ref:number;measurement_id:number;revision:number;state:'CURRENT'|'SUPERSEDED';head_token:string|null;measured_at:string;recorded_at:string;date_precision:'UNKNOWN'|'DAY_UTC_CONVENTION'|'SERVER_CAPTURE_TIME';timezone_basis:'DATABASE_UTC_CONVENTION';fields:Record<BodyKey|'calf_cm',BodyValue>};
export type BodySpec={key:BodyKey;label:string;min:number;max:number;unit:'kg'|'cm'};
export type BodyPage={contract_version:typeof BODY_CONTRACT;owner_id:number;body_revision:number;state:'AVAILABLE'|'EMPTY';entries:BodyEntry[];next_cursor:string|null;window:{from:string|null;through:string|null};field_specs:BodySpec[]};
export type BodyErasureEntry=Pick<BodyEntry,'root_ref'|'measurement_id'|'revision'|'head_token'|'measured_at'|'date_precision'>&{head_token:string;version_count:number};
export type BodyErasurePage={contract_version:typeof BODY_CONTRACT;owner_id:number;body_revision:number;projection:'ERASURE_ONLY';state:'AVAILABLE'|'EMPTY';entries:BodyErasureEntry[];next_cursor:string|null;window:{from:string|null;through:string|null}};
export type BodyReceipt={contract_version:'body-operation/1.0.0';owner_id:number;command_digest:string;request_id:string;operation:'CREATE'|'CORRECT'|'ERASE';root_ref:number;measurement_id:number;applied_revision:number;recorded_at:string;state:'APPLIED'|'ERASED'};
export type BodyConsent={contract_version:typeof BODY_CONTRACT;owner_id:number;granted:boolean;consent_version:number;granted_at:string|null;withdrawn_at:string|null;consent_token:string};
export type BodyOutcome<T>={state:'confirmed';value:T}|{state:'unknown'|'cancelled'|'changed'|'unavailable'|'consent_required'}|{state:'rejected';code:string|null;status:number};
export type BodyTransport={scope:string;call:Transport};
export type PreparedBodyRequest={owner_id:number;backend_scope:string;request_id:string;method:'POST';path:string;payload_json:string;body_digest:string};
type PageMode='current'|'weight'|'versions'|'export';
export type BodyReadOptions={mode?:PageMode;root?:number;from?:string;through?:string;limit?:number;cursor?:string};
export type BodyErasureReadOptions=Pick<BodyReadOptions,'from'|'through'|'limit'|'cursor'>;
const root='/me/body';
const hash=(x:unknown):x is string=>typeof x==='string'&&/^[a-f0-9]{64}$/.test(x);
const id=(x:unknown):x is number=>Number.isSafeInteger(x)&&(x as number)>0;
const natural=(x:unknown):x is number=>Number.isSafeInteger(x)&&(x as number)>=0;
const record=(x:unknown):x is Record<string,unknown>=>typeof x==='object'&&x!==null&&!Array.isArray(x);
const exact=(x:unknown,keys:string[])=>record(x)&&Object.keys(x).length===keys.length&&keys.every(k=>Object.hasOwn(x,k));
const instant=(x:unknown):x is string=>typeof x==='string'&&x.length<=64&&/(?:Z|[+-]\d{2}:\d{2})$/.test(x)&&Number.isFinite(Date.parse(x));
const day=(x:unknown):x is string=>typeof x==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(x)&&Number.isFinite(Date.parse(x+'T00:00:00Z'))&&new Date(x+'T00:00:00Z').toISOString().slice(0,10)===x;
const copy=<T>(x:T):T=>JSON.parse(JSON.stringify(x));

/** BODY command bytes only; distinct from all SCI fingerprints. */
export function bodyCommandCanonical(command:Pick<PreparedBodyRequest,'method'|'path'|'request_id'|'payload_json'>):string{
 const match=command.path.match(/^\/me\/body\/measurements(?:\/([1-9]\d*)\/(corrections|erase))?$/);
 const value:unknown=JSON.parse(command.payload_json);
 if(command.method!=='POST'||!match||!record(value)||value.request_id!==command.request_id||!/^[A-Za-z0-9][A-Za-z0-9_.:-]{0,63}$/.test(command.request_id))throw Error('invalid_body_command');
 const operation=match[2]==='erase'?'ERASE':match[2]==='corrections'?'CORRECT':'CREATE';
 const allowed=operation==='ERASE'?['request_id','expected_head_token','confirm_all_versions']:['request_id','values','measured_on',...(operation==='CORRECT'?['expected_head_token']:[])];
 if(Object.keys(value).some(k=>!allowed.includes(k))||operation!=='CREATE'&&(!id(Number(match[1]))||!hash(value.expected_head_token)))throw Error('invalid_body_command');
 if(operation==='ERASE'){
  if(value.confirm_all_versions!==true)throw Error('erase_confirmation_required');
 }else{
  if(value.values!==undefined&&(!record(value.values)||Object.entries(value.values).some(([k,v])=>!BODY_KEYS.includes(k as BodyKey)||v!==null&&(typeof v!=='number'||!Number.isFinite(v)))))throw Error('invalid_body_value');
  if(value.measured_on!==undefined&&!day(value.measured_on)||operation==='CREATE'&&value.measured_on===undefined)throw Error('invalid_body_day');
 }
 const canonical=(x:unknown):unknown=>record(x)?Object.fromEntries(Object.keys(x).sort().map(k=>[k,canonical(x[k])])):x;
 return JSON.stringify(canonical({...value,operation,...(operation==='CREATE'?{}:{root_ref:Number(match[1])})}));
}

export function createBodyTransport(baseUrl:string,fetchImpl:typeof fetch=fetch):BodyTransport{
 const url=new URL(baseUrl);
 if(!['http:','https:'].includes(url.protocol)||url.username||url.password||url.search||url.hash)throw Error('invalid_body_backend');
 const scope=url.toString().replace(/\/+$/,'');
 const call:Transport=async<T>(path:string,init:CallInit={}):Promise<T>=>{
  if(!path.startsWith('/me/body/'))throw Error('invalid_body_path');
  const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),init.timeoutMs??10000);
  try{
   const headers:Record<string,string>={Accept:'application/json','X-Auren-Body-Contract':BODY_CONTRACT};
   if(init.token)headers.Authorization=`Bearer ${init.token}`;
   if(init.body!==undefined)headers['Content-Type']='application/json';
   const response=await fetchImpl(`${scope}/api/mobile/v1${path}`,{method:init.method??'GET',headers,
    body:init.body===undefined?undefined:JSON.stringify(init.body),signal:controller.signal});
   let body:unknown;try{body=await response.json();}catch{throw new ApiFailure('http',502,'body_response_unknown');}
   if(response.status!==401&&response.headers.get('X-Auren-Body-Contract')!==BODY_CONTRACT)throw new ApiFailure('http',502,'body_contract_echo_mismatch');
   if(!response.ok){const detail=record(body)?body.detail:null;throw new ApiFailure('http',response.status,record(detail)&&typeof detail.error==='string'?detail.error:null);}
   return body as T;
  }catch(error){if(error instanceof ApiFailure)throw error;throw new ApiFailure('network');}
  finally{clearTimeout(timer);}
 };
 return {scope,call};
}

function erasureEntry(raw:unknown):BodyErasureEntry|null{
 if(!exact(raw,['root_ref','measurement_id','revision','head_token','measured_at','date_precision','version_count']))return null;
 const x=raw as BodyErasureEntry;
 return id(x.root_ref)&&id(x.measurement_id)&&x.measurement_id>=x.root_ref&&natural(x.revision)
  &&hash(x.head_token)&&instant(x.measured_at)&&['UNKNOWN','DAY_UTC_CONVENTION','SERVER_CAPTURE_TIME'].includes(x.date_precision)
  &&id(x.version_count)&&(x.version_count===x.revision||x.version_count===x.revision+1)?x:null;
}
function erasurePage(raw:unknown,owner:number,options:BodyErasureReadOptions):BodyErasurePage|null{
 if(!exact(raw,['contract_version','owner_id','body_revision','projection','state','entries','next_cursor','window']))return null;
 const x=raw as BodyErasurePage;
 if(x.contract_version!==BODY_CONTRACT||x.owner_id!==owner||!natural(x.body_revision)||x.projection!=='ERASURE_ONLY'
  ||!['AVAILABLE','EMPTY'].includes(x.state)||!Array.isArray(x.entries)||x.entries.length>(options.limit??50)
  ||(x.state==='EMPTY')!==(x.entries.length===0)||!exact(x.window,['from','through']))return null;
 if(x.window.from!==null&&!day(x.window.from)||x.window.through!==null&&!day(x.window.through)
  ||options.from!==undefined&&options.from!==x.window.from||options.through!==undefined&&options.through!==x.window.through)return null;
 if(options.from===undefined&&options.through===undefined&&(x.window.from!==null||x.window.through!==null))return null;
 if(x.next_cursor!==null&&(typeof x.next_cursor!=='string'||!x.next_cursor.length||x.next_cursor.length>4096)||x.state==='EMPTY'&&x.next_cursor!==null)return null;
 const roots=new Set<number>(),ids=new Set<number>();
 for(const row of x.entries){if(!erasureEntry(row)||roots.has(row.root_ref)||ids.has(row.measurement_id))return null;roots.add(row.root_ref);ids.add(row.measurement_id);}
 return x;
}
function entry(raw:unknown):BodyEntry|null{
 if(!exact(raw,['root_ref','measurement_id','revision','state','head_token','measured_at','recorded_at','date_precision','timezone_basis','fields']))return null;
 const x=raw as BodyEntry;
 if(!id(x.root_ref)||!id(x.measurement_id)||x.measurement_id<x.root_ref||!natural(x.revision)||!['CURRENT','SUPERSEDED'].includes(x.state)
  ||!instant(x.measured_at)||!instant(x.recorded_at)||!['UNKNOWN','DAY_UTC_CONVENTION','SERVER_CAPTURE_TIME'].includes(x.date_precision)
  ||x.timezone_basis!=='DATABASE_UTC_CONVENTION'||(x.state==='CURRENT'?!hash(x.head_token):x.head_token!==null)||!exact(x.fields,[...BODY_KEYS,'calf_cm']))return null;
 for(const key of [...BODY_KEYS,'calf_cm'] as const){
  const v=x.fields[key];
  if(!exact(v,['value','raw_value_repr','quality','unit','provenance'])||v.unit!==(key==='weight_kg'?'kg':'cm')||!exact(v.provenance,['origin','acquisition','source_ref']))return null;
  const source=v.provenance;
  if(source.origin==='UNKNOWN'?source.acquisition!=='UNKNOWN':source.origin!=='USER_DECLARED'||!['MANUAL_ENTRY','MANUAL_CORRECTION'].includes(source.acquisition))return null;
  const match=typeof source.source_ref==='string'?source.source_ref.match(/^body_measurements\/(\d+)\/([a-z_]+)$/):null;
  if(!match||match[2]!==key||!id(Number(match[1]))||Number(match[1])<x.root_ref||Number(match[1])>x.measurement_id)return null;
  if(v.quality==='MISSING'){if(v.value!==null||v.raw_value_repr!==null)return null;}
  else if(v.quality==='INVALID_NONFINITE'){if(v.value!==null||typeof v.raw_value_repr!=='string'||!v.raw_value_repr.length||v.raw_value_repr.length>64)return null;}
  else if(['KNOWN','LEGACY_OUTSIDE_CURRENT_BOUNDS'].includes(v.quality)){if(typeof v.value!=='number'||!Number.isFinite(v.value)||v.raw_value_repr!==null)return null;}
  else return null;
 }
 return x;
}
function page(raw:unknown,owner:number,options:BodyReadOptions):BodyPage|null{
 if(!exact(raw,['contract_version','owner_id','body_revision','state','entries','next_cursor','window','field_specs']))return null;
 const x=raw as BodyPage;
 if(x.contract_version!==BODY_CONTRACT||x.owner_id!==owner||!natural(x.body_revision)||!Array.isArray(x.entries)||x.entries.length>100||!['AVAILABLE','EMPTY'].includes(x.state)
  ||(x.state==='EMPTY')!==(x.entries.length===0)||!exact(x.window,['from','through'])||!Array.isArray(x.field_specs)||x.field_specs.length!==BODY_KEYS.length)return null;
 if((x.window.from!==null&&!day(x.window.from))||(x.window.through!==null&&!day(x.window.through))||options.from!==undefined&&options.from!==x.window.from||options.through!==undefined&&options.through!==x.window.through)return null;
 if(x.next_cursor!==null&&(typeof x.next_cursor!=='string'||!x.next_cursor.length||x.next_cursor.length>4096)||x.state==='EMPTY'&&x.next_cursor!==null)return null;
 const specs=new Set<string>();
 for(const spec of x.field_specs){
  if(!exact(spec,['key','label','min','max','unit'])||!BODY_KEYS.includes(spec.key)||specs.has(spec.key)||typeof spec.label!=='string'||!spec.label.length||spec.label.length>256
    ||typeof spec.min!=='number'||typeof spec.max!=='number'||!Number.isFinite(spec.min)||!Number.isFinite(spec.max)||spec.min>=spec.max||spec.unit!==(spec.key==='weight_kg'?'kg':'cm'))return null;
  specs.add(spec.key);
 }
 const ids=new Set<number>(),roots=new Set<number>();let currentCount=0;
 for(const item of x.entries){
  if(!entry(item)||ids.has(item.measurement_id))return null;ids.add(item.measurement_id);
  if((options.mode??'current')==='current'||options.mode==='weight'){
   if(item.state!=='CURRENT'||roots.has(item.root_ref))return null;roots.add(item.root_ref);
  }
  if(options.mode==='versions'&&item.root_ref!==options.root)return null;
  if(item.state==='CURRENT')currentCount++;
  for(const spec of x.field_specs){const v=item.fields[spec.key];if(v.quality==='KNOWN'&&(v.value!<spec.min||v.value!>spec.max))return null;}
 }
 if(options.mode==='versions'&&currentCount>1)return null;
 return x;
}
export function decodeBodyReceipt(raw:unknown,owner:number,expected?:PreparedBodyRequest):BodyReceipt|null{
 if(!exact(raw,['contract_version','owner_id','command_digest','request_id','operation','root_ref','measurement_id','applied_revision','recorded_at','state']))return null;
 const x=raw as BodyReceipt;
 if(x.contract_version!=='body-operation/1.0.0'||x.owner_id!==owner||!hash(x.command_digest)||typeof x.request_id!=='string'||!/^[A-Za-z0-9][A-Za-z0-9_.:-]{0,63}$/.test(x.request_id)
  ||!['CREATE','CORRECT','ERASE'].includes(x.operation)||!id(x.root_ref)||!id(x.measurement_id)||x.measurement_id<x.root_ref||!id(x.applied_revision)||!instant(x.recorded_at)
  ||x.state!==(x.operation==='ERASE'?'ERASED':'APPLIED')||x.operation==='CREATE'&&(x.root_ref!==x.measurement_id||x.applied_revision!==1))return null;
 if(expected){
  const match=expected.path.match(/^\/me\/body\/measurements(?:\/(\d+)\/(corrections|erase))?$/);
  if(!match||x.command_digest!==expected.body_digest||x.request_id!==expected.request_id||x.operation!==(match[2]==='erase'?'ERASE':match[2]==='corrections'?'CORRECT':'CREATE')||(match[1]!==undefined&&Number(match[1])!==x.root_ref))return null;
 }
 return x;
}
function consent(raw:unknown,owner:number):BodyConsent|null{
 if(!exact(raw,['contract_version','owner_id','granted','consent_version','granted_at','withdrawn_at','consent_token']))return null;
 const x=raw as BodyConsent;
 return x.contract_version===BODY_CONTRACT&&x.owner_id===owner&&typeof x.granted==='boolean'&&x.consent_version===1
  &&(x.granted_at===null||instant(x.granted_at))&&(x.withdrawn_at===null||instant(x.withdrawn_at))&&hash(x.consent_token)?x:null;
}
class IdentityChanged extends Error{}
class Cancelled extends Error{}
export class BodyMeasurementsClient{
 readonly backendScope:string;
 constructor(private readonly auth:AuthSession,private readonly call:Transport,private readonly body:BodyTransport,readonly ownerId:number){
  if(!id(ownerId))throw Error('invalid_body_owner');this.backendScope=body.scope;
 }
 private async request<T>(path:string,init:CallInit,parse:(raw:unknown)=>T|null,unknown404=false):Promise<BodyOutcome<T>>{
  const revision=this.auth.revision;
  try{
   const raw=await this.auth.authorized(async token=>{
    if(revision!==this.auth.revision)throw new Cancelled();
    // Re-run this proof inside the callback: automatic token refresh must
    // never replay an A command with B's token, even at the same generation.
    const owner=await this.call<{id:number}>('/auth/me',{token});
    if(revision!==this.auth.revision)throw new Cancelled();
    if(owner?.id!==this.ownerId)throw new IdentityChanged();
    return this.body.call<unknown>(path,{...init,token});
   });
   if(revision!==this.auth.revision)return {state:'cancelled'};
   const value=parse(raw);return value===null?{state:'unknown'}:{state:'confirmed',value:copy(value)};
  }catch(error){
   if(revision!==this.auth.revision||error instanceof Cancelled)return {state:'cancelled'};
   if(error instanceof IdentityChanged)return {state:'changed'};
   if(error instanceof ApiFailure&&error.kind==='http'){
    if(error.status===403&&error.code==='body_consent_required')return {state:'consent_required'};
    if(error.status===404)return {state:unknown404?'unknown':'unavailable'};
   if(error.status===409)return init.method==='POST'&&error.code==='head_conflict'?{state:'rejected',status:409,code:error.code}:{state:'changed'};
    if(error.status>=400&&error.status<500&&![401,408,429].includes(error.status))return {state:'rejected',status:error.status,code:error.code};
   }
   return {state:'unknown'};
  }
 }
 read(options:BodyReadOptions={}):Promise<BodyOutcome<BodyPage>>{
  const mode=options.mode??'current';
  if(options.limit!==undefined&&(!id(options.limit)||options.limit>100)||options.from!==undefined&&!day(options.from)||options.through!==undefined&&!day(options.through)||options.cursor!==undefined&&(typeof options.cursor!=='string'||options.cursor.length>4096))return Promise.resolve({state:'rejected',status:422,code:'invalid_body_query'});
  if(mode==='versions'&&!id(options.root))return Promise.resolve({state:'rejected',status:422,code:'invalid_body_root'});
  const path=mode==='weight'?'/measurements/weight-history':mode==='export'?'/measurements/export':mode==='versions'?`/measurements/${options.root}/versions`:'/measurements';
  const query=[`limit=${options.limit??50}`];
  if(options.from!==undefined)query.push(`from=${encodeURIComponent(options.from)}`);
  if(options.through!==undefined)query.push(`through=${encodeURIComponent(options.through)}`);
  if(options.cursor!==undefined)query.push(`cursor=${encodeURIComponent(options.cursor)}`);
  return this.request(root+path+'?'+query.join('&'),{},raw=>page(raw,this.ownerId,options));
 }
 head(rootRef:number):Promise<BodyOutcome<BodyEntry>>{
  if(!id(rootRef))return Promise.resolve({state:'rejected',status:422,code:'invalid_body_root'});
  return this.request(`${root}/measurements/${rootRef}`,{},raw=>{
   if(!record(raw)||!exact(raw,['contract_version','owner_id','entry'])||raw.contract_version!==BODY_CONTRACT||raw.owner_id!==this.ownerId)return null;
   const value=entry(raw.entry);return value?.state==='CURRENT'&&value.root_ref===rootRef?value:null;
  });
 }
 readErasure(options:BodyErasureReadOptions={}):Promise<BodyOutcome<BodyErasurePage>>{
  if(options.limit!==undefined&&(!id(options.limit)||options.limit>100)||options.from!==undefined&&!day(options.from)||options.through!==undefined&&!day(options.through)||options.cursor!==undefined&&(typeof options.cursor!=='string'||!options.cursor.length||options.cursor.length>4096))return Promise.resolve({state:'rejected',status:422,code:'invalid_body_query'});
  const query=['purpose=erasure',`limit=${options.limit??50}`];
  if(options.from!==undefined)query.push(`from=${encodeURIComponent(options.from)}`);
  if(options.through!==undefined)query.push(`through=${encodeURIComponent(options.through)}`);
  if(options.cursor!==undefined)query.push(`cursor=${encodeURIComponent(options.cursor)}`);
  return this.request(root+'/measurements?'+query.join('&'),{},raw=>erasurePage(raw,this.ownerId,options));
 }
 erasureHead(rootRef:number):Promise<BodyOutcome<BodyErasureEntry>>{
  if(!id(rootRef))return Promise.resolve({state:'rejected',status:422,code:'invalid_body_root'});
  return this.request(`${root}/measurements/${rootRef}?purpose=erasure`,{},raw=>{
   if(!exact(raw,['contract_version','owner_id','projection','entry']))return null;
   const envelope=raw as {contract_version:string;owner_id:number;projection:string;entry:unknown};
   if(envelope.contract_version!==BODY_CONTRACT||envelope.owner_id!==this.ownerId||envelope.projection!=='ERASURE_ONLY')return null;
   const value=erasureEntry(envelope.entry);return value?.root_ref===rootRef?value:null;
  });
 }
 consent(){return this.request(root+'/consent',{},raw=>consent(raw,this.ownerId));}
 setConsent(granted:boolean,expected:BodyConsent){
  return this.request(root+'/consent',{method:'POST',body:{granted,consent_version:expected.consent_version,expected_consent_token:expected.consent_token}},raw=>consent(raw,this.ownerId));
 }
 status(command:PreparedBodyRequest){
  if(command.owner_id!==this.ownerId||command.backend_scope!==this.backendScope)return Promise.resolve<BodyOutcome<BodyReceipt>>({state:'changed'});
  return this.request(`${root}/operations/${encodeURIComponent(command.request_id)}`,{},raw=>decodeBodyReceipt(raw,this.ownerId,command),true);
 }
 submit(command:PreparedBodyRequest):Promise<BodyOutcome<BodyReceipt>>{
  if(command.owner_id!==this.ownerId||command.backend_scope!==this.backendScope)return Promise.resolve({state:'changed'});
  if(command.method!=='POST'||!/^\/me\/body\/measurements(?:\/[1-9]\d*\/(?:corrections|erase))?$/.test(command.path)||!hash(command.body_digest))return Promise.resolve({state:'rejected',status:422,code:'invalid_body_command'});
  let body:unknown;try{body=JSON.parse(command.payload_json);}catch{return Promise.resolve({state:'rejected',status:422,code:'invalid_body_command'});}
  if(!record(body)||body.request_id!==command.request_id)return Promise.resolve({state:'rejected',status:422,code:'invalid_body_command'});
  return this.request(command.path,{method:'POST',body},raw=>decodeBodyReceipt(raw,this.ownerId,command));
 }
}
