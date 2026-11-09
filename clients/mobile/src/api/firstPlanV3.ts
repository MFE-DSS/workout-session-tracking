/** V3 transport and structural decoding. Scientific trust is the real server adapter. */
import { AuthSession } from '../auth/authSession';
import type { OwnedEnvelopeV3, RecommendationV3, RuntimeVersionsV3 } from '../domain/planV3Types';
import { ApiFailure, type Transport } from './http';
import schemas from './firstPlanV3.contract.json';

export const V3_VERSIONS:RuntimeVersionsV3 = Object.freeze({runtime:'first-session-runtime/3.0.0',request:'first-plan-request/3.0.0',
  result:'first-plan-recommendation/3.0.0',execution:'first-plan-execution/3.0.0',calibration:'first-calibration-encounter/1.0.0'});
export type V3CallInit={method?:'GET'|'POST'|'PUT';body?:unknown;token?:string;timeoutMs?:number;ifMatch?:number};
export type V3Transport=(path:string,init?:V3CallInit)=>Promise<unknown>;
export type V3Outcome<T>={state:'confirmed';value:T}|{state:'unknown'}|{state:'cancelled'}|{state:'unavailable';reason:string}|{state:'rejected';code:string|null;status:number};
export const isObject=(x:unknown):x is Record<string,unknown>=> x!==null&&typeof x==='object'&&!Array.isArray(x);
export const positiveId=(x:unknown):x is number=>typeof x==='number'&&Number.isSafeInteger(x)&&x>0;
export const revision=(x:unknown):x is number=>typeof x==='number'&&Number.isSafeInteger(x)&&x>=0;
export const hexDigest=(x:unknown):x is string=>typeof x==='string'&&/^[a-f0-9]{64}$/.test(x);
export function jsonCopy<T>(value:T):T {
  const check=(v:unknown):void=>{
    if(v===null||typeof v==='string'||typeof v==='boolean') return;
    if(typeof v==='number'&&Number.isFinite(v)) return;
    if(Array.isArray(v)){v.forEach(check);return;}
    if(isObject(v)&&Object.getPrototypeOf(v)===Object.prototype){Object.values(v).forEach(check);return;}
    throw Error('invalid_json_value');
  };
  check(value);return JSON.parse(JSON.stringify(value));
}
export const CALIBRATION_INVENTORY = "plan-calibration-inventory/2.0.0";
export function createV3Transport(baseUrl:string,fetchImpl:typeof fetch=fetch,options?:{calibrationInventory:typeof CALIBRATION_INVENTORY}):V3Transport {
  const base=baseUrl.replace(/\/+$/,'');
  return async(path,init={})=>{
    if(!path.startsWith('/')||path.includes('://')||path.includes('#')||path.includes('?')) throw new ApiFailure('http',422,'invalid_runtime_path');
    if(init.ifMatch!==undefined&&!revision(init.ifMatch))throw Error('invalid_source_revision');
    const controller=new AbortController();const timer=setTimeout(()=>controller.abort(),init.timeoutMs??10000);
    const headers:Record<string,string>={Accept:'application/json','X-Auren-Contract':V3_VERSIONS.runtime,'X-Auren-Calibration':V3_VERSIONS.calibration};
    if(options)headers["X-Auren-Calibration-Inventory"]=options.calibrationInventory;
    if(init.token)headers.Authorization=`Bearer ${init.token}`;
    if(init.ifMatch!==undefined){if(!revision(init.ifMatch))throw Error('invalid_source_revision');headers['If-Match']=String(init.ifMatch);}
    if(init.body!==undefined)headers['Content-Type']='application/json';
    try {
      const response=await fetchImpl(`${base}/api/mobile/v3${path}`,{method:init.method??'GET',headers,credentials:'omit',
        body:init.body===undefined?undefined:JSON.stringify(jsonCopy(init.body)),signal:controller.signal});
      let raw:unknown;try{raw=await response.json();}catch{throw new ApiFailure('network');}
      if(!response.ok){const detail=isObject(raw)?raw.detail:null;throw new ApiFailure('http',response.status,isObject(detail)&&typeof detail.error==='string'?detail.error:null);}
      if(options&&response.headers?.get("X-Auren-Calibration-Inventory")!==options.calibrationInventory)throw new ApiFailure("http",406,"calibration_inventory_not_supported");
      return raw;
    }catch(error){if(error instanceof ApiFailure)throw error;throw new ApiFailure('network');}
    finally{clearTimeout(timer);}
  };
}
export function ownedEnvelope(raw:unknown,owner:number):raw is OwnedEnvelopeV3 {
  if(!isObject(raw)||raw.owner_id!==owner||raw.contract_version!==V3_VERSIONS.runtime||!isObject(raw.versions))return false;
  return Object.entries(V3_VERSIONS).every(([key,value])=>raw.versions!==null&&isObject(raw.versions)&&raw.versions[key]===value);
}
export class RuntimeV3Client {
  constructor(readonly auth:AuthSession,private readonly identity:Transport,private readonly call:V3Transport){}
  async request<T=OwnedEnvelopeV3>(path:string,init:Omit<V3CallInit,'token'>={},parse?:(value:OwnedEnvelopeV3)=>T|null,
    current:()=>boolean=()=>true):Promise<V3Outcome<T>> {
    const generation=this.auth.revision;const active=()=>generation===this.auth.revision&&current();
    const mutation=init.method!==undefined&&init.method!=='GET';
    try {
      const captured={...init,...(init.body!==undefined?{body:jsonCopy(init.body)}:{})};
      const owner=await this.auth.authorized(token=>this.identity<{id:number}>('/auth/me',{token}));
      if(!active())return{state:'cancelled'};
      if(!positiveId(owner?.id))return{state:'unknown'};
      const raw=await this.auth.authorized(token=>{if(!active())throw new ApiFailure('http',401,'stale_identity');return this.call(path,{...captured,token});},
        {retryUnauthorized:!mutation});
      if(!active())return{state:'cancelled'};
      if(!ownedEnvelope(raw,owner.id))return{state:'unknown'};
      const result=parse?parse(raw):raw as T;
      if(!active())return{state:'cancelled'};
      return result===null?{state:'unknown'}:{state:'confirmed',value:jsonCopy(result)};
    }catch(error){
      if(!active())return{state:'cancelled'};
      if(error instanceof ApiFailure&&error.kind==='http'){
        if(error.status===406)return{state:'unavailable',reason:'CONTRACT_NOT_SUPPORTED'};
        if(error.status>=500&&!mutation)return{state:'unavailable',reason:error.code??'NOT_SERVED'};
        if(error.status>=400&&error.status<500&&![408,429].includes(error.status))return{state:'rejected',code:error.code,status:error.status};
      }
      return{state:'unknown'};
    }
  }
}

const annotations=new Set(['$schema','$id','$defs','title','description','default','discriminator']);
const supported=new Set(['$ref','type','anyOf','oneOf','const','enum','properties','required','additionalProperties','items','minItems','maxItems','minLength','maxLength','minimum','maximum','exclusiveMinimum','exclusiveMaximum','pattern','format']);
function dateTime(value:string):boolean {
  const m=/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/.exec(value);
  if(!m||!Number.isFinite(Date.parse(value)))return false;
  const [year,month,day,hour,minute,second]=m.slice(1).map(Number);
  return year>=1&&month>=1&&month<=12&&day>=1&&day<=new Date(Date.UTC(year,month,0)).getUTCDate()&&hour<24&&minute<60&&second<60;
}
function schemaMatches(value:unknown,node:any,root:any=schemas.response,depth=0):boolean {
  if(depth>80||!isObject(node)||Object.keys(node).some(k=>!annotations.has(k)&&!supported.has(k)))return false;
  if(typeof value==='number'&&!Number.isFinite(value))return false;
  if(typeof node.$ref==='string'){
    if(!node.$ref.startsWith('#/$defs/'))return false;
    const key=node.$ref.slice(8).replace(/~1/g,'/').replace(/~0/g,'~');
    return Boolean(root.$defs?.[key])&&schemaMatches(value,root.$defs[key],root,depth+1);
  }
  if(Array.isArray(node.oneOf)&&node.oneOf.filter(s=>schemaMatches(value,s,root,depth+1)).length!==1)return false;
  if(Array.isArray(node.anyOf)&&!node.anyOf.some(s=>schemaMatches(value,s,root,depth+1)))return false;
  if(Object.prototype.hasOwnProperty.call(node,'const')&&value!==node.const)return false;
  if(Array.isArray(node.enum)&&!node.enum.includes(value))return false;
  if(node.type==='null')return value===null;
  if(node.type==='boolean'&&typeof value!=='boolean')return false;
  if(node.type==='string'){
    if(typeof value!=='string'||(typeof node.minLength==='number'&&[...value].length<node.minLength)||(typeof node.maxLength==='number'&&[...value].length>node.maxLength))return false;
    if(typeof node.pattern==='string'&&!new RegExp(node.pattern).test(value))return false;
    if(node.format!==undefined&&(node.format!=='date-time'||!dateTime(value)))return false;
  }
  if(node.type==='number'||node.type==='integer'){
    if(typeof value!=='number'||!Number.isFinite(value)||(node.type==='integer'&&!Number.isSafeInteger(value)))return false;
    if(typeof node.minimum==='number'&&value<node.minimum||typeof node.maximum==='number'&&value>node.maximum||typeof node.exclusiveMinimum==='number'&&value<=node.exclusiveMinimum||typeof node.exclusiveMaximum==='number'&&value>=node.exclusiveMaximum)return false;
  }
  if(node.type==='array'){
    if(!Array.isArray(value)||(typeof node.minItems==='number'&&value.length<node.minItems)||(typeof node.maxItems==='number'&&value.length>node.maxItems))return false;
    if(node.items&&!value.every(v=>schemaMatches(v,node.items,root,depth+1)))return false;
  }
  if(node.type==='object'){
    if(!isObject(value))return false;
    if(Array.isArray(node.required)&&node.required.some(k=>typeof k!=='string'||!Object.prototype.hasOwnProperty.call(value,k)))return false;
    for(const [key,child] of Object.entries(value)){
      if(isObject(node.properties)&&Object.prototype.hasOwnProperty.call(node.properties,key)){
        if(!schemaMatches(child,node.properties[key],root,depth+1))return false;
      }else if(node.additionalProperties===false)return false;
      else if(isObject(node.additionalProperties)&&!schemaMatches(child,node.additionalProperties,root,depth+1))return false;
    }
  }
  return node.type===undefined||['null','boolean','string','number','integer','array','object'].includes(String(node.type));
}
export function decodeRecommendationV3(raw:unknown):RecommendationV3|null {
  return schemaMatches(raw,schemas.response)?raw as RecommendationV3:null;
}

export function decodeBlueprintV3(raw:unknown):Record<string,unknown>|null {
  return schemaMatches(raw,schemas.request.properties.blueprint,schemas.request)&&isObject(raw)?raw:null;
}
export function capabilityEnvelope(raw:OwnedEnvelopeV3):import('../domain/planV3Types').CapabilitiesV3|null {
  const x=raw as unknown as Record<string,unknown>;
  if(x.runtime_availability!=='NOT_SERVED'||typeof x.controlled_test_available!=='boolean')return null;
  const authority=x.controlled_authority;
  if(authority!==null){
    if(!isObject(authority)||!positiveId(authority.generation)||authority.state!=='ACTIVE'||!isObject(authority.pins))return null;
    if(!['registry_digest','binding_digest','bundle_digest','effective_science_digest'].every(key=>isObject(authority.pins)&&hexDigest(authority.pins[key])))return null;
    if(!['engine_version','policy_version','binding_ref','start_policy_ref'].every(key=>typeof authority[key]==='string'))return null;
  }
  const realization=(item:unknown)=>isObject(item)&&['candidate_id','realization_ref','display_name'].every(key=>typeof item[key]==='string'&&Boolean(item[key]));
  if(x.supported_realizations!==undefined&&(!Array.isArray(x.supported_realizations)||x.supported_realizations.some(item=>!realization(item)||!isObject(item)||typeof item.intent_id!=='string'||typeof item.initial_guidance_supported!=='boolean')))return null;
  if(x.initial_calibration_pilot!==undefined&&x.initial_calibration_pilot!==null&&!realization(x.initial_calibration_pilot))return null;
  if(x.calibration_protocol_material!==undefined&&x.calibration_protocol_material!==null){
   const material=x.calibration_protocol_material;
   if(!isObject(material)||typeof material.source_ref!=='string'||!hexDigest(material.sha256)||typeof material.text!=='string')return null;
  }
  if(x.controlled_guidance_available!==undefined&&typeof x.controlled_guidance_available!=='boolean')return null;
  if(x.calibration_inventory!==undefined&&x.calibration_inventory!==null){
   const inv=x.calibration_inventory;
   if(!isObject(inv)||inv.version!==CALIBRATION_INVENTORY||!hexDigest(inv.bundle_digest)||!Array.isArray(inv.profiles)||inv.profiles.length!==7)return null;
   const ids=new Set<string>();
   for(const p of inv.profiles){
    if(!isObject(p)||typeof p.candidate_id!=='string'||typeof p.realization_ref!=='string'||typeof p.policy_ref!=='string'||ids.has(p.candidate_id))return null;
    if(p.load_semantics!==(p.candidate_id==='romanian-deadlift-halteres'?'PER_IMPLEMENT':'MACHINE_DISPLAY_KG'))return null;
    ids.add(p.candidate_id);
   }
   const m=inv.protocol_material;if(!isObject(m)||typeof m.source_ref!=='string'||!hexDigest(m.sha256)||typeof m.text!=='string')return null;
  }
  return raw as import('../domain/planV3Types').CapabilitiesV3;
}
export class FirstPlanV3Client {
  constructor(private readonly runtime:RuntimeV3Client){}
  capabilities(){return this.runtime.request('/me/first-plan/capabilities',{},capabilityEnvelope);}
  evaluate(snapshot:import('../domain/planV3Types').BlueprintSnapshotV3,capabilities:import('../domain/planV3Types').CapabilitiesV3,
    requestId:string,current:()=>boolean=()=>true):Promise<V3Outcome<import('../domain/planV3Types').EvaluationV3>> {
    const authority=capabilities.controlled_authority;
    if(!capabilities.controlled_test_available||!authority)return Promise.resolve({state:'unavailable',reason:'NOT_SERVED'});
    const captured=jsonCopy({snapshot_ref:snapshot.snapshot_ref,subject_ref:snapshot.subject_ref,source_revision:snapshot.source_revision,
      owner_id:snapshot.owner_id,authority,capability_owner:capabilities.owner_id});
    if(captured.capability_owner!==captured.owner_id)return Promise.resolve({state:'unknown'});
    return this.runtime.request('/me/first-plan/evaluations',{method:'POST',body:{request_id:requestId,snapshot_ref:captured.snapshot_ref,expected_pins:captured.authority.pins}},
      raw=>this.parseEvaluation(raw,captured),current);
  }
  private parseEvaluation(raw:OwnedEnvelopeV3,expected:{owner_id:number;snapshot_ref:string;subject_ref:string;source_revision:number;authority:NonNullable<import('../domain/planV3Types').CapabilitiesV3['controlled_authority']>}):import('../domain/planV3Types').EvaluationV3|null {
    const x=raw as unknown as Record<string,unknown>,result=decodeRecommendationV3(x.recommendation);
    if(!result||x.owner_id!==expected.owner_id||x.snapshot_ref!==expected.snapshot_ref||x.source_revision!==expected.source_revision||x.authority_generation!==expected.authority.generation)return null;
    if(typeof x.evaluation_ref!=='string'||!['EVALUATE','TIME_ACK'].includes(String(x.operation_kind))||typeof x.historical!=='boolean')return null;
    if(result.snapshot_ref!==expected.snapshot_ref||result.subject_ref!==expected.subject_ref||result.source_revision!==`blueprint-source/${expected.source_revision}`)return null;
    if(result.bundle_digest!==expected.authority.pins.bundle_digest||result.effective_science_digest!==expected.authority.pins.effective_science_digest)return null;
    if(result.scientific_readiness==='SCIENTIFICALLY_READY'&&(result.binding_digest!==expected.authority.pins.binding_digest||result.binding_ref!==expected.authority.binding_ref
      ||result.engine_version!==expected.authority.engine_version||result.policy_version!==expected.authority.policy_version||result.start_policy_ref!==expected.authority.start_policy_ref))return null;
    return raw as import('../domain/planV3Types').EvaluationV3;
  }
  readEvaluation(evaluationRef:string,snapshot:import('../domain/planV3Types').BlueprintSnapshotV3,capabilities:import('../domain/planV3Types').CapabilitiesV3,current:()=>boolean=()=>true){
    const authority=capabilities.controlled_authority?jsonCopy(capabilities.controlled_authority):null;
    if(!authority)return Promise.resolve({state:'unavailable',reason:'NOT_SERVED'} as V3Outcome<import('../domain/planV3Types').EvaluationV3>);
    const expected=jsonCopy({owner_id:snapshot.owner_id,snapshot_ref:snapshot.snapshot_ref,subject_ref:snapshot.subject_ref,source_revision:snapshot.source_revision,authority});
    return this.runtime.request(`/me/first-plan/evaluations/${encodeURIComponent(evaluationRef)}`,{},raw=>{
      const parsed=this.parseEvaluation(raw,expected);return parsed?.evaluation_ref===evaluationRef?parsed:null;
    },current);
  }
  acknowledge(evaluation:import('../domain/planV3Types').EvaluationV3,capabilities:import('../domain/planV3Types').CapabilitiesV3,requestId:string,
    current:()=>boolean=()=>true):Promise<V3Outcome<import('../domain/planV3Types').EvaluationV3>> {
    const captured=jsonCopy(evaluation),authority=capabilities.controlled_authority?jsonCopy(capabilities.controlled_authority):null;
    if(!authority||capabilities.owner_id!==evaluation.owner_id)return Promise.resolve({state:'unavailable',reason:'NOT_SERVED'});
    if(captured.recommendation.start_permission!=='REQUIRES_TIME_ACK')return Promise.resolve({state:'rejected',status:409,code:'time_ack_not_applicable'});
    const r=captured.recommendation;
    const expectedContext={request_fingerprint:r.request_fingerprint,observation_fingerprint:r.observation_fingerprint,
      plan_time_fingerprint:r.plan_time_fingerprint,start_policy_ref:r.start_policy_ref};
    return this.runtime.request(`/me/first-plan/evaluations/${encodeURIComponent(captured.evaluation_ref)}/time-acknowledgments`,{
      method:'POST',body:{request_id:requestId,expected_context:expectedContext}},raw=>{
        const parsed=this.parseEvaluation(raw,{owner_id:captured.owner_id,snapshot_ref:captured.snapshot_ref,subject_ref:r.subject_ref,source_revision:captured.source_revision,authority:jsonCopy(authority)});
        if(!parsed||parsed.operation_kind!=='TIME_ACK'||parsed.parent_evaluation_ref!==captured.evaluation_ref)return null;
        const next=parsed.recommendation;
        if(next.request_fingerprint!==r.request_fingerprint||next.observation_fingerprint!==r.observation_fingerprint||next.plan_time_fingerprint!==r.plan_time_fingerprint
          ||next.full_evaluation_fingerprint===r.full_evaluation_fingerprint||next.start_permission!=='ELIGIBLE')return null;
        return parsed;
      },current);
  }
}

export { schemaMatches as runtimeSchemaMatches };
