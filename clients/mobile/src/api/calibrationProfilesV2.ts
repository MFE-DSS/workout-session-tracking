/** Client representation compatibility only; SCI and the current owned authority decide permission.
 * Mirrors stage2-v3/authority/registry.v1.json and the pilot/six-extension registries.
 */
import type {CalibrationProfileV2,CapabilitiesV3,CalibrationReadV1,ContextV3} from '../domain/planV3Types';
export const CALIBRATION_INVENTORY_V2='plan-calibration-inventory/2.0.0' as const;
export const COMPATIBLE_CALIBRATION_PROFILES:readonly Readonly<CalibrationProfileV2>[] = Object.freeze([
  {
    "candidate_id": "leg-extensions-assises",
    "intent_id": "initial_quad_v1",
    "realization_ref": "initial-candidate-realisation/1.0.0@c05c6596f8f5578bad0b322db8644ebd8f37e319e733d8099a1f4ea18934bdda",
    "load_semantics": "MACHINE_DISPLAY_KG",
    "policy_ref": "initial-calibration-encounter/1.0.0"
  },
  {
    "candidate_id": "chest-press-machine",
    "intent_id": "initial_press_v1",
    "realization_ref": "initial-candidate-realisation/1.0.0@477c8e570e9260cdf20a3b6502490d68c7243059d526d0734ae68568f5ef9642",
    "load_semantics": "MACHINE_DISPLAY_KG",
    "policy_ref": "initial-calibration-extension/1.0.0"
  },
  {
    "candidate_id": "rowing-chest-supported",
    "intent_id": "initial_row_v1",
    "realization_ref": "initial-candidate-realisation/1.0.0@f65ee15f870e8d6c57dafa5bc9afa359ec2d774272f704a2cfd6884c61a6f773",
    "load_semantics": "MACHINE_DISPLAY_KG",
    "policy_ref": "initial-calibration-extension/1.0.0"
  },
  {
    "candidate_id": "romanian-deadlift-halteres",
    "intent_id": "initial_hinge_v1",
    "realization_ref": "initial-candidate-realisation/1.0.0@b857f3bdb563e90e2a84f17403d407d3eb4936fa183bddf05c2d7cd7f15d29f1",
    "load_semantics": "PER_IMPLEMENT",
    "policy_ref": "initial-calibration-extension/1.0.0"
  },
  {
    "candidate_id": "tirage-poulie-haute-prise-neutre",
    "intent_id": "initial_vertical_pull_v1",
    "realization_ref": "initial-candidate-realisation/1.0.0@0e07dc7086decdddf1411bc1821ef3a1dc987b227fa43ef43396c1dd4c50a234",
    "load_semantics": "MACHINE_DISPLAY_KG",
    "policy_ref": "initial-calibration-extension/1.0.0"
  },
  {
    "candidate_id": "elevations-laterales-machine",
    "intent_id": "initial_lateral_delt_v1",
    "realization_ref": "initial-candidate-realisation/1.0.0@07e1300036de7f302e8b2c76303f731a9cd050f11658487f215659e0ec8eb5cf",
    "load_semantics": "MACHINE_DISPLAY_KG",
    "policy_ref": "initial-calibration-extension/1.0.0"
  },
  {
    "candidate_id": "releves-mollets-debout-machine",
    "intent_id": "initial_calf_v1",
    "realization_ref": "initial-candidate-realisation/1.0.0@650be74db4ab9e31eb4fabdf21e99637159e345ebd8be40bd89287dcb94da1cc",
    "load_semantics": "MACHINE_DISPLAY_KG",
    "policy_ref": "initial-calibration-extension/1.0.0"
  }
].map(row=>Object.freeze(row as CalibrationProfileV2)));
export const PILOT_CANDIDATE='leg-extensions-assises';
const object=(x:unknown):x is Record<string,unknown>=>!!x&&typeof x==='object'&&!Array.isArray(x);
export function compatibleCalibrationProfile(candidate:unknown):Readonly<CalibrationProfileV2>|null {
 return COMPATIBLE_CALIBRATION_PROFILES.find(p=>p.candidate_id===candidate)??null;
}
/** Join only fields actually served on each carrier. Never infer admission from this mirror. */
export function compatibleCalibrationInventory(value:unknown,realizations:unknown,pilot:unknown):boolean {
 if(!object(value)||value.version!==CALIBRATION_INVENTORY_V2||!Array.isArray(value.profiles)||!Array.isArray(realizations)
  ||value.profiles.length!==7||realizations.length!==7||!object(pilot)||pilot.candidate_id!==PILOT_CANDIDATE)return false;
 const ids=new Set(),realizationIds=new Set();
 for(const row of value.profiles){
  if(!object(row))return false;const expected=compatibleCalibrationProfile(row.candidate_id);
  if(!expected||ids.has(row.candidate_id)||!Object.entries(expected).every(([key,v])=>row[key]===v))return false;
  ids.add(row.candidate_id);
 }
 for(const row of realizations){
  if(!object(row))return false;const expected=compatibleCalibrationProfile(row.candidate_id);
  if(!expected||realizationIds.has(row.candidate_id)||!['candidate_id','intent_id','realization_ref','load_semantics'].every(key=>row[key]===expected[key as keyof CalibrationProfileV2]))return false;
  if('policy_ref' in row&&row.policy_ref!==expected.policy_ref)return false;
  realizationIds.add(row.candidate_id);
 }
 const expected=compatibleCalibrationProfile(PILOT_CANDIDATE)!;
 return pilot.realization_ref===expected.realization_ref&&['intent_id','load_semantics','policy_ref'].every(key=>!(key in pilot)||pilot[key]===expected[key as keyof CalibrationProfileV2]);
}
/** Legacy pilot uses only its own served tuple fields; no six-profile prerequisite. */
export function compatibleLegacyCalibrationPilot(pilot:unknown,realizations:unknown):boolean {
 const expected=compatibleCalibrationProfile(PILOT_CANDIDATE)!;
 const matches=(row:unknown)=>object(row)&&row.candidate_id===expected.candidate_id&&row.realization_ref===expected.realization_ref
  &&['intent_id','load_semantics','policy_ref'].every(key=>!(key in row)||row[key]===expected[key as keyof CalibrationProfileV2]);
 if(!matches(pilot))return false;
 if(realizations===undefined)return true;
 if(!Array.isArray(realizations))return false;
 const rows=realizations.filter(row=>object(row)&&row.candidate_id===PILOT_CANDIDATE);
 return rows.length===1&&matches(rows[0]);
}
export function compatibleCalibrationContext(context:unknown,profile:Readonly<CalibrationProfileV2>,allowUnknown=true):context is ContextV3 {
 return object(context)&&context.canonical_exercise_id===profile.candidate_id&&context.realization_ref===profile.realization_ref
  &&context.side==='BILATERAL'&&(context.load_semantics===profile.load_semantics||(allowUnknown&&context.load_semantics==='UNKNOWN'));
}
function massSetting(setting:unknown):boolean {
 return setting===null||setting===undefined||(object(setting)&&setting.kind==='MASS_KG'&&setting.unit==='kg'&&typeof setting.value==='number'&&Number.isFinite(setting.value)&&setting.value>=0);
}
function sameSetting(a:unknown,b:unknown):boolean {return object(a)&&object(b)&&a.kind===b.kind&&a.unit===b.unit&&a.value===b.value;}
/** JSON facts may use different object key ordering; their contents must still agree. */
function sameFact(a:unknown,b:unknown):boolean {
 if(a===b)return true;
 if(Array.isArray(a)&&Array.isArray(b))return a.length===b.length&&a.every((v,i)=>sameFact(v,b[i]));
 return object(a)&&object(b)&&Object.keys(a).length===Object.keys(b).length&&Object.keys(a).every(key=>Object.prototype.hasOwnProperty.call(b,key)&&sameFact(a[key],b[key]));
}
function matchesServedFact(events:unknown,event:Record<string,unknown>):boolean {
 if(events===undefined)return true; // Older projections may omit this carrier.
 if(!Array.isArray(events))return false;
 const matching=events.filter(candidate=>object(candidate)&&candidate.event_id===event.event_id);
 // SCI serializes optional event defaults; compare every fact actually served in the ledger.
 return matching.length===1&&object(matching[0])&&Object.keys(matching[0]).every(key=>sameFact(matching[0][key],event[key]));
}
function sameContext(a:ContextV3,b:ContextV3):boolean {return Object.keys(a).every(k=>a[k as keyof ContextV3]===b[k as keyof ContextV3]);}
export function withoutCalibrationGuidance(view:CalibrationReadV1):CalibrationReadV1 {
 return {...view,result:null,authority:null,allowed_actions:[],unavailable_reason:'REVALIDATION_REQUIRED'};
}
/** Facts are kept unchanged on mismatch, including old settings and explicit UNKNOWN values. */
export function bindCalibrationCapabilities(view:CalibrationReadV1,caps:CapabilitiesV3|null,owner:number):CalibrationReadV1 {
 if(!view.authority&&!view.result&&view.allowed_actions.length===0)return view;
 const close=()=>withoutCalibrationGuidance(view),a=view.authority,r=view.result,c=caps?.controlled_authority;
 if(!caps||caps.owner_id!==owner||!caps.controlled_test_available||!a||!r||!c||a.generation!==c.generation)return close();
 const context=view.progress.context,profile=compatibleCalibrationProfile(context?.canonical_exercise_id);
 if(!profile||!compatibleCalibrationContext(context,profile)||a.policy_ref!==profile.policy_ref||r.policy_ref!==profile.policy_ref)return close();
 const inventory=caps.calibration_inventory;
 if(inventory){
  if(!compatibleCalibrationInventory(inventory,caps.supported_realizations,caps.initial_calibration_pilot)||a.inventory_version!==CALIBRATION_INVENTORY_V2||a.inventory_bundle_digest!==inventory.bundle_digest)return close();
 }else if(a.inventory_version!==undefined||profile.candidate_id!==PILOT_CANDIDATE
  ||!compatibleLegacyCalibrationPilot(caps.initial_calibration_pilot,caps.supported_realizations))return close();
 const expectedBundle=profile.candidate_id===PILOT_CANDIDATE?c.encounter_bundle_digest:inventory?.bundle_digest;
 if(!expectedBundle||a.encounter_bundle_digest!==expectedBundle||r.authority_digest!==expectedBundle)return close();
 const choice=view.progress.setting_choice;
 if(!massSetting(choice?.setting)||!massSetting(r.qualified_setting))return close();
 if(choice&&choice.context_fingerprint!==undefined&&choice.context_fingerprint!==a.context_fingerprint)return close();
 const needsChosenSetting=Boolean(r.qualified_setting)||view.allowed_actions.some(action=>['INITIATE_TRIAL','ACCEPT_EXACT_SETTING'].includes(action));
 if(needsChosenSetting&&(!choice||choice.available!==true||!object(choice.setting)))return close();
 if(r.qualified_setting&&(!choice||!sameSetting(r.qualified_setting,choice.setting)))return close();
 const physical=view.allowed_actions.some(action=>['INITIATE_FAMILIARIZATION','CONFIRM_FAMILIARIZATION','INITIATE_TRIAL','ACCEPT_EXACT_SETTING'].includes(action));
 if(physical&&(caps.controlled_guidance_available===false||caps.supported_realizations?.find(p=>p.candidate_id===profile.candidate_id)?.initial_guidance_supported===false||view.selected===false))return close();
 if(context.load_semantics==='UNKNOWN'&&(view.progress.setting_choice||r.qualified_setting||view.allowed_actions.some(x=>['INITIATE_TRIAL','ACCEPT_EXACT_SETTING'].includes(x))))return close();
 if(r.portable_episode!==null&&r.portable_episode!==undefined){
  const ep=r.portable_episode;
  if(!object(ep)||!compatibleCalibrationContext(ep.context,profile,false)||!sameContext(context,ep.context)||ep.episode_id!==view.encounter_ref||!Array.isArray(ep.events)
   ||ep.events.some(event=>!object(event)||!massSetting(event.setting)))return close();
  if(r.qualified_setting){
   const trial=ep.events.find(event=>object(event)&&event.event_id===r.reference_event_id);
   const acceptance=ep.events.find(event=>object(event)&&event.event_id===r.acceptance_event_id);
   if(!object(trial)||trial.kind!=='ATTEMPT_OBSERVED'||!sameSetting(trial.setting,r.qualified_setting)
    ||!object(acceptance)||acceptance.kind!=='SETTING_ACCEPTED'||acceptance.reference_event_id!==trial.event_id)return close();
   if(ep.subject_ref!==r.subject_ref||[trial,acceptance].some(event=>event.subject_ref!==r.subject_ref||event.context_fingerprint!==a.context_fingerprint)
    ||!matchesServedFact(view.progress.events,trial)||!matchesServedFact(view.progress.events,acceptance)
    ||!matchesServedFact(view.progress.observations,trial))return close();
  }
 }
 return view;
}
