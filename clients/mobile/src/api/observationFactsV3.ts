/** Decodes owned historical facts; shape is never an admission or permission. */
import {isObject,runtimeSchemaMatches} from './firstPlanV3';
import type {ObservationProgressV3} from '../domain/planV3Types';
import schemas from './calibrationV1.contract.json';
export function observationProgressV3(raw:unknown,subjectRef?:string):ObservationProgressV3|null{
 if(!isObject(raw)||typeof raw.episode_ref!=='string'||!raw.episode_ref||!['CONTEXT_OPENED','CALIBRATION_ENCOUNTER_OPENED'].includes(String(raw.kind))
  ||!runtimeSchemaMatches(raw.context,schemas.request.properties.context,schemas.request)
  ||!runtimeSchemaMatches(raw.availability,schemas.request.properties.availability,schemas.request)
  ||!runtimeSchemaMatches(raw.preparation,schemas.request.properties.preparation,schemas.request)
  ||!runtimeSchemaMatches(raw.setting_choice,schemas.request.properties.setting_choice,schemas.request)
  ||!Array.isArray(raw.events))return null;
 const ids=new Set<string>();let sequence=0;
 for(const event of raw.events){
  if(!runtimeSchemaMatches(event,{$ref:'#/$defs/CalibrationEvent'},schemas.request)||!isObject(event)
   ||typeof event.event_id!=='string'||typeof event.sequence!=='number'||ids.has(event.event_id)||event.sequence<=sequence
   ||subjectRef!==undefined&&event.subject_ref!==subjectRef)return null;
  ids.add(event.event_id);sequence=event.sequence;
 }
 return raw as ObservationProgressV3;
}
