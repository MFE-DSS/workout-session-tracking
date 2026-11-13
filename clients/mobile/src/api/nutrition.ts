/** Owned manual nutrition transport. Exact bytes, no hidden mutation retry. */
import {AuthSession} from '../auth/authSession';
import {ApiFailure,type Transport} from './http';
import {nutritionCanonical,nutritionSorted,nutExact,nutHash,nutId,nutRequestId,nutDay,nutVariant,type PreparedNutritionRequest,type NutritionVariant,type NutritionNamespace} from '../domain/nutritionCommand';
import {decodeNutritionConsent,decodeNutritionHead,decodeNutritionPage,nutritionReadQuery,type NutritionRead,type NutritionConsent,type NutritionHead,type NutritionPage} from './nutritionDTO';

export const NUT_CONTRACT='nutrition-manual/1.0.0' as const;
export type NutritionOutcome<T>={state:'confirmed';value:T}|{state:'unknown'|'cancelled'|'changed'|'unavailable'|'consent_required'}|{state:'rejected';code:string|null;status:number};
export type NutritionReceipt={contract_version:'nutrition-operation/1.0.0';owner_id:number;namespace:NutritionNamespace;request_id:string;command_digest:string;state:'APPLIED';entity_ref:number;applied_revision:number;recorded_at:string};
export type NutritionTransport={scope:string;call:(path:string,token:string,body?:string)=>Promise<unknown>};
export type NutritionIdentityTransport={scope:string;call:Transport};
export type NutritionHeadKey={local_day:string}|{variant:NutritionVariant;effective_from:string};
export const nutInstant=(x:unknown):x is string=>typeof x==='string'&&x.length<=64&&/(?:Z|[+-][0-9]{2}:[0-9]{2})$/.test(x)&&Number.isFinite(Date.parse(x));
export function decodeNutritionReceipt(raw:unknown,owner:number,expected:PreparedNutritionRequest):NutritionReceipt|null{
 if(!nutExact(raw,['contract_version','owner_id','namespace','request_id','command_digest','state','entity_ref','applied_revision','recorded_at']))return null;
 if(raw.contract_version!=='nutrition-operation/1.0.0'||raw.owner_id!==owner||raw.namespace!==expected.namespace||raw.request_id!==expected.request_id||raw.command_digest!==expected.body_digest||!nutRequestId(raw.request_id)||!nutHash(raw.command_digest)||raw.state!=='APPLIED'||!nutId(raw.entity_ref)||!nutId(raw.applied_revision)||!nutInstant(raw.recorded_at))return null;
 return raw as NutritionReceipt;
}
export function createNutritionTransport(baseUrl:string,fetchImpl:typeof fetch=fetch):NutritionTransport{
 const url=new URL(baseUrl);
 if(!['http:','https:'].includes(url.protocol)||url.username||url.password||url.search||url.hash)throw Error('invalid_nutrition_backend');
 const scope=url.toString().replace(/\/+$/,'');
 return {scope,async call(path,token,body){
  if(!path.startsWith('/me/nutrition/')||path.includes('#')||/[\r\n]/.test(path))throw Error('invalid_nutrition_path');
  const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),10000);
  try{
   const headers:Record<string,string>={Accept:'application/json','X-Auren-Nutrition-Contract':NUT_CONTRACT,Authorization:`Bearer ${token}`};
   if(body!==undefined)headers['Content-Type']='application/json';
   const response=await fetchImpl(scope+'/api/mobile/v1'+path,{method:body===undefined?'GET':'POST',headers,body,signal:controller.signal});
   let value:unknown;try{value=await response.json();}catch{throw new ApiFailure('http',502,'nutrition_response_unknown');}
   if(response.status!==401&&response.headers.get('X-Auren-Nutrition-Contract')!==NUT_CONTRACT)throw new ApiFailure('http',502,'nutrition_contract_echo_mismatch');
   if(!response.ok){const detail=nutExact(value,['detail'])?value.detail:null;throw new ApiFailure('http',response.status,nutExact(detail,['error'])&&typeof detail.error==='string'?detail.error:null);}
   return value;
  }catch(error){if(error instanceof ApiFailure)throw error;throw new ApiFailure('network');}
  finally{clearTimeout(timer);}
 }};
}
class IdentityChanged extends Error{}
class Cancelled extends Error{}
const refusals:Record<number,readonly string[]>={403:['consent_required','acquisition_unavailable'],406:['unsupported_contract'],409:['stale_head','stale_target','stale_consent','idempotency_mismatch'],422:['invalid_command']};
export class NutritionClient{
 readonly backendScope:string;
 constructor(private auth:AuthSession,private identity:NutritionIdentityTransport,private transport:NutritionTransport,readonly ownerId:number){
  if(!nutId(ownerId))throw Error('invalid_nutrition_owner');
  if(identity.scope!==transport.scope)throw Error('nutrition_backend_mismatch');this.backendScope=transport.scope;
 }
 private async request<T>(path:string,parse:(raw:unknown)=>T|null,body?:string):Promise<NutritionOutcome<T>>{
  const revision=this.auth.revision;
  try{
   const raw=await this.auth.authorized(async token=>{
    if(revision!==this.auth.revision)throw new Cancelled();
    const who=await this.identity.call<{id:number}>('/auth/me',{token});
    if(revision!==this.auth.revision)throw new Cancelled();
    if(who?.id!==this.ownerId)throw new IdentityChanged();
    return this.transport.call(path,token,body);
   },{retryUnauthorized:false});
   if(revision!==this.auth.revision)return{state:'cancelled'};
   const value=parse(raw);return value===null?{state:'unknown'}:{state:'confirmed',value:JSON.parse(JSON.stringify(value))};
  }catch(error){
   if(revision!==this.auth.revision||error instanceof Cancelled)return{state:'cancelled'};
   if(error instanceof IdentityChanged)return{state:'changed'};
   if(error instanceof ApiFailure&&error.kind==='http'){
    if(error.status===403&&error.code==='consent_required')return{state:'consent_required'};
    if(error.code!==null&&refusals[error.status]?.includes(error.code))return{state:'rejected',status:error.status,code:error.code};
   }
   return{state:'unknown'};
  }
 }
 private owned(command:PreparedNutritionRequest){return command.owner_id===this.ownerId&&command.backend_scope===this.backendScope;}
 submit(command:PreparedNutritionRequest):Promise<NutritionOutcome<NutritionReceipt>>{
  if(!this.owned(command))return Promise.resolve({state:'changed'});
  try{nutritionCanonical(command);if(!nutHash(command.body_digest))throw Error();}catch{return Promise.resolve({state:'rejected',status:422,code:'invalid_nutrition_command'});}
  return this.request(command.path,raw=>decodeNutritionReceipt(raw,this.ownerId,command),command.payload_json);
 }
 status(command:PreparedNutritionRequest):Promise<NutritionOutcome<NutritionReceipt>>{
  if(!this.owned(command))return Promise.resolve({state:'changed'});
  try{nutritionCanonical(command);if(!nutHash(command.body_digest))throw Error();}catch{return Promise.resolve({state:'rejected',status:422,code:'invalid_nutrition_command'});}
  return this.request(`/me/nutrition/operations/${command.namespace}/${command.request_id}`,raw=>decodeNutritionReceipt(raw,this.ownerId,command));
 }
 consent(){return this.request('/me/nutrition/consent',raw=>decodeNutritionConsent(raw,this.ownerId));}
 setConsent(granted:boolean,expected:NutritionConsent){
  if(typeof granted!=='boolean'||!decodeNutritionConsent(expected,this.ownerId))return Promise.resolve<NutritionOutcome<NutritionConsent>>({state:'rejected',status:422,code:'invalid_nutrition_consent'});
  return this.request('/me/nutrition/consent',raw=>decodeNutritionConsent(raw,this.ownerId),nutritionSorted({contract_version:NUT_CONTRACT,expected_token:expected.consent_token,granted,wording_version:expected.current_wording_version}));
 }
 head(input:NutritionHeadKey):Promise<NutritionOutcome<NutritionHead>>{
  let namespace:NutritionNamespace,path:string,key:Record<string,string>;
  if('local_day' in input&&nutExact(input,['local_day'])&&nutDay(input.local_day)){
   namespace='DAY';key={local_day:input.local_day};path='/me/nutrition/days/'+input.local_day;
  }else if('variant' in input&&nutExact(input,['variant','effective_from'])&&nutVariant(input.variant)&&nutDay(input.effective_from)){
   namespace='TARGET';key={variant:input.variant,effective_from:input.effective_from};path=`/me/nutrition/targets/head?variant=${input.variant}&effective_from=${input.effective_from}`;
  }else return Promise.resolve({state:'rejected',status:422,code:'invalid_nutrition_query'});
  return this.request(path,raw=>decodeNutritionHead(raw,this.ownerId,namespace,key));
 }
 read(options:NutritionRead):Promise<NutritionOutcome<NutritionPage>>{
  let path:string;try{path=nutritionReadQuery(options);}catch{return Promise.resolve({state:'rejected',status:422,code:'invalid_nutrition_query'});}
  return this.request('/me/nutrition/'+path,raw=>decodeNutritionPage(raw,this.ownerId,options));
 }
}
