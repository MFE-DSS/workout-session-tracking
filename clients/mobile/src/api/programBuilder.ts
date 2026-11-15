/** Exact owned command bytes, bounded reads, and no implicit mutation replay. */
import {CryptoDigestAlgorithm,digestStringAsync} from 'expo-crypto';
import {AuthSession} from '../auth/authSession';
import {BUILDER_VERSION,BUILDER_MAX_BYTES,builderBackendScope,builderByteLength,builderCommandJSON,builderExact,builderId,builderKey,type PreparedBuilderCommand,verifyPreparedBuilderCommand,type BuilderCommand} from '../domain/programBuilderCommand';
import {ApiFailure,type Transport} from './http';
import {builderReadQuery,decodeBuilderReceipt,decodeBuilderPrograms,decodeBuilderExercises,decodeBuilderProgram,type BuilderReceipt,type BuilderProgramsPage,type BuilderExercisesPage,type BuilderProgramRead} from './programBuilderDTO';
export {decodeBuilderReceipt,type BuilderReceipt} from './programBuilderDTO';
export type BuilderOutcome<T>={state:'confirmed';value:T}|{state:'unknown'|'cancelled'|'changed'}|{state:'rejected';status:number;code:string|null};
export type BuilderTransport={scope:string;call:(path:string,token:string,body?:string)=>Promise<unknown>};
export type BuilderIdentityTransport={scope:string;call:Transport};
const prefix='/me/program-builder/';
function validPath(path:string,body?:string):boolean{
 if(body!==undefined)return path===prefix+'commands';
 if(path.startsWith(prefix+'programs/')){const id=path.slice((prefix+'programs/').length);return /^[1-9][0-9]*$/.test(id)&&builderId(Number(id));}
 if(path.startsWith(prefix+'operations/'))return builderKey(path.slice((prefix+'operations/').length));
 try{const parsed=new URL(path,'https://builder.invalid'),kind=parsed.pathname.slice(prefix.length);
  if(!['programs','exercises'].includes(kind)||parsed.pathname!==prefix+kind||parsed.hash)return false;
  const limit=parsed.searchParams.get('limit'),cursor=parsed.searchParams.get('cursor')??undefined;
  return path===builderReadQuery(kind as 'programs'|'exercises',limit===null?25:Number(limit),cursor)||path===prefix+kind;
 }catch{return false;}
}
export function createProgramBuilderTransport(baseUrl:string,fetchImpl:typeof fetch=fetch):BuilderTransport{
 const url=new URL(baseUrl);if(!['https:','http:'].includes(url.protocol)||url.username||url.password||url.hash||url.search)throw Error('invalid_builder_backend');
 const scope=url.toString().replace(/\/+$/,'');if(!builderBackendScope(scope))throw Error('invalid_builder_backend');
 return {scope,async call(path,token,body){
  if(!validPath(path,body)||typeof token!=='string'||!token||/[\r\n]/.test(token))throw Error('invalid_builder_request');
  const headers:Record<string,string>={Accept:'application/json',Authorization:`Bearer ${token}`,'X-Auren-Program-Builder':BUILDER_VERSION};
  if(body!==undefined){
   if(builderByteLength(body)>BUILDER_MAX_BYTES)throw Error('invalid_builder_request');
   const command=JSON.parse(body) as BuilderCommand;if(builderCommandJSON(command)!==body)throw Error('invalid_builder_request');
   headers['Content-Type']='application/json';if(command.operation==='CREATE')headers['If-None-Match']='*';else headers['If-Match']=command.expected_source_digest!;
  }
  const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),10000);
  try{
   const response=await fetchImpl(scope+'/api/mobile/v1'+path,{method:body===undefined?'GET':'POST',headers,body,signal:controller.signal,redirect:'error'});
   if(response.headers.get('X-Auren-Program-Builder')!==BUILDER_VERSION||response.headers.get('Cache-Control')?.toLowerCase()!=='no-store'||!/^application\/json(?:\s*;|$)/i.test(response.headers.get('Content-Type')??''))throw new ApiFailure('http',502,'builder_response_unknown');
   const length=response.headers.get('Content-Length');if(length!==null&&(!/^[0-9]+$/.test(length)||Number(length)>BUILDER_MAX_BYTES))throw new ApiFailure('http',502,'builder_response_unknown');
   const text=await response.text();if(builderByteLength(text)>BUILDER_MAX_BYTES)throw new ApiFailure('http',502,'builder_response_unknown');
   let value:unknown;try{value=JSON.parse(text);}catch{throw new ApiFailure('http',502,'builder_response_unknown');}
   if(!response.ok){const detail=builderExact(value,['detail'])?value.detail:null;throw new ApiFailure('http',response.status,builderExact(detail,['error'])&&typeof detail.error==='string'&&detail.error.length<=128?detail.error:null);}
   return value;
  }catch(error){if(error instanceof ApiFailure)throw error;throw new ApiFailure('network');}finally{clearTimeout(timer);}
 }};
}
class Changed extends Error{}
class Cancelled extends Error{}
const refusals:Record<number,readonly string[]>={400:['invalid_request','invalid_precondition'],403:['acquisition_unavailable'],406:['unsupported_contract'],409:['command_conflict','stale_source','stale_slot','stale_selection','domain_refused'],413:['source_too_large'],422:['invalid_request','invalid_cursor'],428:['precondition_required']};
const invalid=<T>():BuilderOutcome<T>=>({state:'rejected',status:422,code:'invalid_builder_request'});
export class ProgramBuilderClient{
 readonly backendScope:string;
 constructor(private auth:AuthSession,private identity:BuilderIdentityTransport,private transport:BuilderTransport,readonly ownerId:number,private sha:(s:string)=>Promise<string>=s=>digestStringAsync(CryptoDigestAlgorithm.SHA256,s)){
  if(!builderId(ownerId))throw Error('invalid_builder_owner');if(!builderBackendScope(transport.scope)||identity.scope!==transport.scope)throw Error('builder_backend_mismatch');this.backendScope=transport.scope;
 }
 private async request<T>(path:string,decode:(raw:unknown)=>T|null,body?:string,revision=this.auth.revision):Promise<BuilderOutcome<T>>{
  try{
   if(revision!==this.auth.revision)return {state:'cancelled'};
   const raw=await this.auth.authorized(async token=>{
    if(revision!==this.auth.revision)throw new Cancelled();const who=await this.identity.call<unknown>('/auth/me',{token});
    if(revision!==this.auth.revision)throw new Cancelled();
    if(typeof who!=='object'||who===null||!('id' in who)||who.id!==this.ownerId)throw new Changed();
    return this.transport.call(path,token,body);
   },{retryUnauthorized:false});
   if(revision!==this.auth.revision)return {state:'cancelled'};
   const value=decode(raw);return value===null?{state:'unknown'}:{state:'confirmed',value:JSON.parse(JSON.stringify(value)) as T};
  }catch(error){if(revision!==this.auth.revision||error instanceof Cancelled)return {state:'cancelled'};if(error instanceof Changed)return {state:'changed'};
   if(error instanceof ApiFailure&&error.kind==='http'&&error.code!==null&&refusals[error.status]?.includes(error.code))return {state:'rejected',status:error.status,code:error.code};return {state:'unknown'};}
 }
 private async command(input:PreparedBuilderCommand,send:boolean):Promise<BuilderOutcome<BuilderReceipt>>{
  const revision=this.auth.revision;
  if(!input||input.owner_id!==this.ownerId||input.backend_scope!==this.backendScope)return {state:'changed'};
  let prepared:PreparedBuilderCommand;
  try{prepared=await verifyPreparedBuilderCommand({...input},this.sha);}catch{return revision!==this.auth.revision?{state:'cancelled'}:invalid();}
  if(revision!==this.auth.revision)return {state:'cancelled'};
  const outcome=await this.request(prefix+(send?'commands':'operations/'+prepared.command_id),raw=>decodeBuilderReceipt(raw,this.ownerId,prepared),send?prepared.payload_json:undefined,revision);
  return !send&&outcome.state==='rejected'?{state:'unknown'}:outcome;
 }
 submit(p:PreparedBuilderCommand):Promise<BuilderOutcome<BuilderReceipt>>{return this.command(p,true);}
 status(p:PreparedBuilderCommand):Promise<BuilderOutcome<BuilderReceipt>>{return this.command(p,false);}
 programs(limit=25,cursor?:string):Promise<BuilderOutcome<BuilderProgramsPage>>{let path:string;try{path=builderReadQuery('programs',limit,cursor);}catch{return Promise.resolve(invalid());}return this.request(path,raw=>decodeBuilderPrograms(raw,this.ownerId,limit,cursor));}
 exercises(limit=25,cursor?:string):Promise<BuilderOutcome<BuilderExercisesPage>>{let path:string;try{path=builderReadQuery('exercises',limit,cursor);}catch{return Promise.resolve(invalid());}return this.request(path,raw=>decodeBuilderExercises(raw,this.ownerId,limit,cursor));}
 program(id:number):Promise<BuilderOutcome<BuilderProgramRead>>{if(!builderId(id))return Promise.resolve(invalid());return this.request(prefix+'programs/'+id,raw=>decodeBuilderProgram(raw,this.ownerId,id));}
}
