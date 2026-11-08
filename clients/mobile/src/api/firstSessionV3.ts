/** Handoff API only. The controller persists its stable intent before submit. */
import type {CapabilitiesV3,EvaluationV3,ExecutionV3,FirstSessionCommandV3,FirstSessionReceiptV3,OwnedEnvelopeV3,SetFactV3,SetReceiptV3} from '../domain/planV3Types';
import { RuntimeV3Client,hexDigest,isObject,positiveId,revision,runtimeSchemaMatches } from './firstPlanV3';
import schemas from './firstPlanV3.contract.json';
export function commandFromEvaluationV3(evaluation:EvaluationV3,capabilities:CapabilitiesV3):FirstSessionCommandV3|null {
  const r=evaluation.recommendation,a=capabilities.controlled_authority;
  if(!a||!capabilities.controlled_test_available||capabilities.owner_id!==evaluation.owner_id||a.generation!==evaluation.authority_generation
    ||r.scientific_readiness!=='SCIENTIFICALLY_READY'||r.start_permission!=='ELIGIBLE'||!r.candidate_plan||!r.acknowledgment)return null;
  if(!hexDigest(r.plan_time_fingerprint)||!hexDigest(r.binding_digest)||r.binding_digest!==a.pins.binding_digest||r.bundle_digest!==a.pins.bundle_digest
    ||r.effective_science_digest!==a.pins.effective_science_digest||!r.engine_version||!r.policy_version||!r.binding_ref)return null;
  const first=r.candidate_plan.sessions[0];
  if(!first||typeof first.session_id!=='string')return null;
  return {evaluation_ref:evaluation.evaluation_ref,snapshot_ref:evaluation.snapshot_ref,source_revision:evaluation.source_revision,
    request_fingerprint:r.request_fingerprint,observation_fingerprint:r.observation_fingerprint,full_evaluation_fingerprint:r.full_evaluation_fingerprint,
    plan_time_fingerprint:r.plan_time_fingerprint,binding_ref:r.binding_ref,binding_digest:r.binding_digest,bundle_digest:r.bundle_digest,
    effective_science_digest:r.effective_science_digest,engine_version:r.engine_version,policy_version:r.policy_version,
    registry_digest:a.pins.registry_digest,contract_version:r.contract_version,selected_scientific_session_id:first.session_id};
}
export function firstSessionReceipt(raw:OwnedEnvelopeV3):FirstSessionReceiptV3|null {
  const x=raw as unknown as Record<string,unknown>;
  if(typeof x.request_id!=='string'||!['CREATED','DENIED','CANCELLED'].includes(String(x.state)))return null;
  if(x.state==='CREATED'){
    if(!positiveId(x.session_id)||typeof x.scientific_session_id!=='string')return null;
  }else if(x.session_id!==null)return null;
  if(x.terminal_code!==null&&typeof x.terminal_code!=='string')return null;
  return raw as FirstSessionReceiptV3;
}
function typedContext(raw:unknown):boolean {
  return isObject(raw)&&raw.side==='BILATERAL'&&['TOTAL_EXTERNAL','PER_IMPLEMENT','MACHINE_DISPLAY_KG'].includes(String(raw.load_semantics))
    &&['canonical_exercise_id','context_ref','equipment_ref','realization_ref'].every(key=>typeof raw[key]==='string'&&Boolean(raw[key]));
}
export function executionEnvelope(raw:OwnedEnvelopeV3):ExecutionV3|null {
  const value=(raw as unknown as Record<string,unknown>).execution;
  if(!isObject(value)||value.contract_version!=='first-plan-execution/3.0.0'||!positiveId(value.session_id)
    ||!['in_progress','completed'].includes(String(value.status))||!Array.isArray(value.exercises)||!value.exercises.length
    ||!isObject(value.applicability)||!['CURRENT','UNKNOWN','BLOCKED'].includes(String(value.applicability.state))
    ||typeof value.observation_only!=='boolean'||!Array.isArray(value.allowed_actions)||!value.allowed_actions.every(x=>typeof x==='string')
    ||typeof value.evaluation_ref!=='string'||!hexDigest(value.binding_digest)||value.derived_metrics!=='NON_EVALUABLE')return null;
  const ids=new Set<number>();
  for(const exercise of value.exercises){
    if(!isObject(exercise)||!positiveId(exercise.se_id)||typeof exercise.canonical_exercise_id!=='string'||typeof exercise.intent_id!=='string'
      ||!runtimeSchemaMatches(exercise.prescription,{$ref:'#/$defs/ObservedSettingPrescription'},schemas.response)||!isObject(exercise.prescription)||exercise.prescription.mode!=='OBSERVED_SETTING'||!typedContext(exercise.prescription.context)
      ||!isObject(exercise.prescription.setting)||exercise.prescription.setting.kind!=='MASS_KG'||exercise.prescription.setting.unit!=='kg'
      ||typeof exercise.prescription.setting.value!=='number'||!Number.isFinite(exercise.prescription.setting.value)||exercise.prescription.setting.value<0
      ||!isObject(exercise.prescription.dose)||!positiveId(exercise.prescription.dose.work_sets)||!positiveId(exercise.prescription.dose.rest_seconds)
      ||!Array.isArray(exercise.sets)||exercise.sets.length!==exercise.prescription.dose.work_sets)return null;
    for(const set of exercise.sets){
      if(!isObject(set)||!positiveId(set.set_id)||ids.has(set.set_id)||set.kind!=='work'||!revision(set.revision)||typeof set.completed!=='boolean')return null;
      if(set.reps!==null&&(!revision(set.reps)))return null;
      ids.add(set.set_id);
      if(set.observation!==null&&(!isObject(set.observation)||!typedContext(set.observation.context)))return null;
    }
    if(!isObject(exercise.transition_after_exercise)||!['SETUP_NEXT_EXERCISE','BILAN'].includes(String(exercise.transition_after_exercise.kind))||exercise.transition_after_exercise.duration_seconds!==null)return null;
  }
  if(value.cursor!==null&&(!isObject(value.cursor)||!positiveId(value.cursor.set_id)||!ids.has(value.cursor.set_id)))return null;
  if(value.observation_only&&value.allowed_actions.includes('NEXT_WORK_SET'))return null;
  return value as ExecutionV3;
}
export class FirstSessionV3Client {
  constructor(private readonly runtime:RuntimeV3Client){}
  submit(requestId:string,command:FirstSessionCommandV3,current?:()=>boolean){
    return this.runtime.request('/me/first-session-requests',{method:'POST',body:{request_id:requestId,command}},raw=>{
      const result=firstSessionReceipt(raw);return result?.request_id===requestId?result:null;
    },current);
  }
  readRequest(requestId:string,current?:()=>boolean){
    return this.runtime.request(`/me/first-session-requests/${encodeURIComponent(requestId)}`,{},raw=>{
      const result=firstSessionReceipt(raw);return result?.request_id===requestId?result:null;
    },current);
  }
  handoff(current?:()=>boolean){return this.runtime.request('/me/first-session-handoff',{},raw=>{
    const h=(raw as unknown as Record<string,unknown>).handoff;
    if(h===null)return {handoff:null};
    if(!isObject(h)||h.owner_id!==raw.owner_id)return null;
    const parsed=firstSessionReceipt(h as OwnedEnvelopeV3);
    return parsed?.state==='CREATED'?{handoff:parsed}:null;
  },current);}
  cancel(requestId:string,command:FirstSessionCommandV3,current?:()=>boolean){
    return this.runtime.request(`/me/first-session-requests/${encodeURIComponent(requestId)}/cancel`,{method:'POST',body:{request_id:requestId,command}},raw=>{
      const result=firstSessionReceipt(raw);return result?.request_id===requestId?result:null;
    },current);
  }
  execution(sessionId:number,current?:()=>boolean){
    return this.runtime.request(`/sessions/${sessionId}/execution`,{},raw=>{
      const result=executionEnvelope(raw);return result?.session_id===sessionId?result:null;
    },current);
  }
  recordSet(sessionId:number,setId:number,opId:string,expectedRevision:number,observation:SetFactV3,current?:()=>boolean){
    return this.runtime.request(`/sessions/${sessionId}/sets/${setId}`,{method:'PUT',body:{op_id:opId,expected_set_revision:expectedRevision,observation}},raw=>{
      const receipt=(raw as unknown as Record<string,unknown>).receipt;
      if(!isObject(receipt)||receipt.state!=='APPLIED'||receipt.session_id!==sessionId||receipt.set_id!==setId||receipt.op_id!==opId||receipt.applied_revision!==expectedRevision+1)return null;
      return receipt as SetReceiptV3;
    },current);
  }
}
