/** Selection guard only. The original journals/controllers remain command owners. */
import type {MissionAction} from './missionAction';
import type {MissionResourceState} from './missionActionResource';
export type LocalOpening={kind:'START'|'CLOSE'|'SOURCE'}|null;
export function localOpeningState(input:{legacyStartUnknown:boolean;closePending:boolean;v3:{intent:{state:string}|null;source:{pending?:unknown}}|null}):LocalOpening{
 if(input.legacyStartUnknown||input.v3?.intent?.state==='submitted'||input.v3?.intent?.state==='unknown')return{kind:'START'};
 if(input.closePending)return{kind:'CLOSE'};
 if(input.v3?.source.pending)return{kind:'SOURCE'};
 return null;
}
export function missionActionCurrent(action:MissionAction,read:MissionResourceState,local:LocalOpening):boolean{
 return local===null&&read.state==='confirmed'&&JSON.stringify(action)===JSON.stringify(read.value);
}

/** Additive MOB04 metadata in the existing owner-bound MISSION JSON, never a replay command. */
import type {WorkoutState} from '../domain/workout';
type LegacyMarker={version:'legacy-start-uncertainty/1.0.0';template_slug:string;requested_at_ms:number};
export function hasLegacyStart(state:unknown):boolean{return !!state&&typeof state==='object'&&Object.prototype.hasOwnProperty.call(state,'mission_opening');}
export function legacyStartMarker(state:unknown):LegacyMarker|null{
 if(!hasLegacyStart(state))return null;
 const v=(state as {mission_opening:unknown}).mission_opening;
 if(!v||typeof v!=='object')return null;
 const m=v as Record<string,unknown>;
 return m.version==='legacy-start-uncertainty/1.0.0'&&typeof m.template_slug==='string'&&m.template_slug.length>0&&typeof m.requested_at_ms==='number'&&Number.isSafeInteger(m.requested_at_ms)&&m.requested_at_ms>=0?{version:m.version,template_slug:m.template_slug,requested_at_ms:m.requested_at_ms}:null;
}
export function markLegacyStart(state:WorkoutState,slug:string,at:number):WorkoutState&{mission_opening:LegacyMarker}{
 if(state.phase!=='MISSION'||hasLegacyStart(state)||!slug||!Number.isSafeInteger(at)||at<0)throw Error('invalid_legacy_opening');
 return{...state,mission_opening:{version:'legacy-start-uncertainty/1.0.0',template_slug:slug,requested_at_ms:at}};
}
export function clearLegacyStart(state:WorkoutState):WorkoutState{
 const {mission_opening:_,...rest}=state as WorkoutState&{mission_opening?:unknown};return rest;
}

/** Existing V3 state resumes; a new claim belongs to the explicit V3 entry action. */
export async function restoreExistingV3(controller:{restore:()=>Promise<void>},journal:{read:()=>Promise<unknown>}):Promise<void>{
 if(await journal.read())await controller.restore();
}

/** Negative current-server evidence is retained across offline refresh/restart. */
export function legacyResumeBlocked(state:unknown):boolean{return !!state&&typeof state==='object'&&Object.prototype.hasOwnProperty.call(state,'mission_resume_blocked');}
export function blockLegacyResume(state:WorkoutState):WorkoutState{
 if(!state.plan)return state;
 return{...state,mission_resume_blocked:{version:'mission-resume-exclusion/1.0.0',session_id:state.plan.session_id}} as WorkoutState;
}
export function clearLegacyResumeBlock(state:WorkoutState):WorkoutState{
 const {mission_resume_blocked:_,...rest}=state as WorkoutState&{mission_resume_blocked?:unknown};return rest;
}
