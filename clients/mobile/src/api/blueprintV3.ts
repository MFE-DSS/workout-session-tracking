/** Only server-owned captures become scientific input. Forms send declarations. */
import type { BlueprintSnapshotV3, FactV3, OwnedEnvelopeV3 } from '../domain/planV3Types';
import {observationProgressV3} from './observationFactsV3';
import { RuntimeV3Client,decodeBlueprintV3,hexDigest,isObject,revision } from './firstPlanV3';
export type DeclarationNameV3='objective'|'population_scope'|'sessions_per_week'|'session_budgets_minutes'|'limitations'|'experience'|'declared_priorities'|'excluded_exercise_ids';
export type DeclarationPatchV3=Partial<Record<DeclarationNameV3,{state:'KNOWN'|'UNKNOWN'|'WITHHELD';value:unknown}>>;
export type DeclarationsV3=OwnedEnvelopeV3 & {source_revision:number;blueprint:Record<string,unknown>;
 subject_ref?:string;observation_progress?:import('../domain/planV3Types').ObservationProgressV3[];
 receipts?:{sources:{request_id:string;event_ref:string;source_revision:number;kind:string}[];snapshots:{request_id:string;snapshot_ref:string;source_revision:number}[];
 evaluations:{request_id:string;evaluation_ref:string;snapshot_ref:string;operation_kind:'EVALUATE'|'TIME_ACK'}[]}};
export type SourceReceiptV3=OwnedEnvelopeV3 & {source_revision:number;event_ref:string;episode_ref?:string};
function sourceReceipt(raw:OwnedEnvelopeV3):SourceReceiptV3|null {
  const x=raw as unknown as Record<string,unknown>;
  return revision(x.source_revision)&&typeof x.event_ref==='string'?raw as SourceReceiptV3:null;
}
export function snapshotEnvelope(raw:OwnedEnvelopeV3):BlueprintSnapshotV3|null {
  const x=raw as unknown as Record<string,unknown>;
  if(typeof x.snapshot_ref!=='string'||typeof x.subject_ref!=='string'||!revision(x.source_revision)||!hexDigest(x.snapshot_digest)
    ||typeof x.as_of!=='string'||!Number.isFinite(Date.parse(x.as_of))||!decodeBlueprintV3(x.blueprint)||!isObject(x.consent_assessment))return null;
  if(!['NOT_REQUIRED','SATISFIED','REQUIRED','UNAVAILABLE'].includes(String(x.consent_assessment.state)))return null;
  if(!isObject(x.blueprint)||x.blueprint.snapshot_id!==x.snapshot_ref)return null;
  return raw as BlueprintSnapshotV3;
}
export class BlueprintV3Client {
  constructor(private readonly runtime:RuntimeV3Client){}
  read(current?:()=>boolean){return this.runtime.request('/me/blueprint/declarations',{},raw=>{
    const x=raw as unknown as Record<string,unknown>;
    if(!revision(x.source_revision)||!decodeBlueprintV3(x.blueprint))return null;
    if(x.observation_progress!==undefined&&(!Array.isArray(x.observation_progress)||typeof x.subject_ref!=='string'
      ||x.observation_progress.some(entry=>!observationProgressV3(entry,x.subject_ref as string))))return null;
    return raw as DeclarationsV3;
  },current);}
  saveDeclarations(requestId:string,expectedRevision:number,fields:DeclarationPatchV3,current?:()=>boolean){
    return this.runtime.request('/me/blueprint/declarations',{method:'PUT',ifMatch:expectedRevision,
      body:{request_id:requestId,fields}},sourceReceipt,current);
  }
  capture(requestId:string,expectedRevision:number,current?:()=>boolean){
    return this.runtime.request('/me/blueprint/snapshots',{method:'POST',body:{request_id:requestId,expected_revision:expectedRevision}},
      raw=>{const parsed=snapshotEnvelope(raw);return parsed?.source_revision===expectedRevision?parsed:null;},current);
  }
  readSnapshot(snapshotRef:string,current?:()=>boolean){
    return this.runtime.request(`/me/blueprint/snapshots/${encodeURIComponent(snapshotRef)}`,{},
      raw=>{const parsed=snapshotEnvelope(raw);return parsed?.snapshot_ref===snapshotRef?parsed:null;},current);
  }
  observe(requestId:string,expectedRevision:number,event:Record<string,unknown>,current?:()=>boolean){
    return this.runtime.request('/me/blueprint/observations',{method:'POST',body:{request_id:requestId,expected_revision:expectedRevision,event}},sourceReceipt,current);
  }
}
export function declaredFact(blueprint:Record<string,unknown>,field:DeclarationNameV3):FactV3|null {
  const value=blueprint[field];
  return isObject(value)&&['KNOWN','UNKNOWN','CONFLICT','WITHHELD'].includes(String(value.state))&&isObject(value.provenance)?value as FactV3:null;
}
