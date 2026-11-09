/** Current pilot permissions and historical facts have separate carriers. */
import type {CalibrationReadV1,ContextV3,OwnedEnvelopeV3,CapabilitiesV3} from '../domain/planV3Types';
import { CALIBRATION_INVENTORY,RuntimeV3Client,isObject,revision,positiveId,hexDigest,runtimeSchemaMatches } from './firstPlanV3';
import { BlueprintV3Client,type SourceReceiptV3 } from './blueprintV3';
import {observationProgressV3} from './observationFactsV3';
import schemas from './calibrationV1.contract.json';
import {bindCalibrationCapabilities} from './calibrationProfilesV2';
const strings=(value:unknown):value is string[]=>Array.isArray(value)&&value.every(x=>typeof x==='string');
export function calibrationEnvelope(raw:OwnedEnvelopeV3,capabilities?:CapabilitiesV3|null):CalibrationReadV1|null {
  const value=(raw as unknown as Record<string,unknown>).encounter;
  if(!isObject(value)||typeof value.encounter_ref!=='string'||!revision(value.source_revision)||typeof value.as_of!=='string'
    ||!Number.isFinite(Date.parse(value.as_of))||!strings(value.allowed_actions)||!isObject(value.progress))return null;
  const progress=value.progress;
  if(typeof progress.ledger_complete!=='boolean'||!strings(progress.observation_refs)||!strings(progress.acceptance_refs))return null;
  if(progress.ledger_complete){
    if(!revision(progress.observed_attempt_count)||progress.observed_attempt_count!==progress.observation_refs.length)return null;
  }else if(progress.observed_attempt_count!==null)return null;
  if(progress.observations!==undefined){
    const entry=observationProgressV3({...progress,episode_ref:value.encounter_ref,kind:'CALIBRATION_ENCOUNTER_OPENED',availability:'UNKNOWN'});
    if(!entry||!Array.isArray(progress.observations)||progress.observations.length!==progress.observation_refs.length)return null;
    const expected=entry.events.filter(event=>event.kind==='ATTEMPT_OBSERVED');
    if(JSON.stringify(expected)!==JSON.stringify(progress.observations)||expected.some((event,index)=>event.event_id!==(progress.observation_refs as string[])[index]))return null;
  }
  if(value.result===null){
    if(value.authority!==null||value.allowed_actions.length!==0)return null;
  }else{
    if(!runtimeSchemaMatches(value.result,schemas.response,schemas.response)||!isObject(value.result)||!isObject(value.authority))return null;
    if(value.result.encounter_ref!==value.encounter_ref||value.result.source_revision!==`blueprint-source/${value.source_revision}`)return null;
    if(value.authority.inventory_version!==undefined&&(value.authority.inventory_version!==CALIBRATION_INVENTORY||!hexDigest(value.authority.packaging_digest)||!hexDigest(value.authority.inventory_bundle_digest)||typeof value.selected!=='boolean'))return null;
    if(!positiveId(value.authority.generation)||!hexDigest(value.authority.encounter_bundle_digest)||!hexDigest(value.authority.context_fingerprint))return null;
    if(value.authority.contract_version!=='first-calibration-encounter/1.0.0'||!strings(value.result.allowed_actions)
      ||value.allowed_actions.some(action=>!value.result||!isObject(value.result)||!Array.isArray(value.result.allowed_actions)||!value.result.allowed_actions.includes(action)))return null;
  }
  const view=value as CalibrationReadV1;
  return capabilities!==undefined||view.authority?.inventory_version!==undefined?bindCalibrationCapabilities(view,capabilities??null,raw.owner_id):view;
}
export class CalibrationV1Client {
  private readonly blueprint:BlueprintV3Client;
  constructor(private readonly runtime:RuntimeV3Client){this.blueprint=new BlueprintV3Client(runtime);}
  open(requestId:string,expectedRevision:number,context:ContextV3,availability:'AVAILABLE'|'UNAVAILABLE'|'UNKNOWN',concernState:'CLEAR'|'REPORTED'|'UNKNOWN',current?:()=>boolean){
    return this.runtime.request('/me/blueprint/calibration-encounters',{method:'POST',body:{request_id:requestId,expected_revision:expectedRevision,
      context,availability,concern_state:concernState}},raw=>{
      const x=raw as unknown as Record<string,unknown>;
      return typeof x.encounter_ref==='string'&&revision(x.source_revision)?raw as OwnedEnvelopeV3&{encounter_ref:string;source_revision:number}:null;
    },current);
  }
  read(encounterRef:string,current?:()=>boolean,capabilities?:CapabilitiesV3|null){
    return this.runtime.request(`/me/blueprint/calibration-encounters/${encodeURIComponent(encounterRef)}`,{},raw=>{
      const value=calibrationEnvelope(raw,capabilities?.calibration_inventory&&this.runtime.calibrationInventory!==CALIBRATION_INVENTORY?null:capabilities);return value?.encounter_ref===encounterRef?value:null;
    },current);
  }
  select(requestId:string,expectedRevision:number,encounterRef:string,current?:()=>boolean){
    return this.blueprint.observe(requestId,expectedRevision,{kind:"CALIBRATION_ENCOUNTER_SELECTED",encounter_ref:encounterRef},current);
  }
  record(requestId:string,view:CalibrationReadV1,observation:Record<string,unknown>,current?:()=>boolean){
    return this.blueprint.observe(requestId,view.source_revision,{kind:'ENCOUNTER_OBSERVATION',encounter_ref:view.encounter_ref,
      expected_authority:view.authority,observation},current);
  }
}
