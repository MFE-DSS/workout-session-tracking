/** Presentation only. Permissions and qualification always come from the server. */
import type {CalibrationReadV1,SettingV3} from '../../domain/planV3Types';
export type CalibrationStage='preparation'|'setting'|'familiar'|'trial'|'observation'|'decision';
export function parseCalibrationMass(raw:string):SettingV3|null {
 const value=raw.trim();if(!/^\d+(?:[.,]\d+)?$/.test(value))return null;
 const n=Number(value.replace(',','.'));return Number.isFinite(n)&&n>=0?{kind:'MASS_KG',unit:'kg',value:n}:null;
}
export const calibrationUnit=(semantics:string|undefined)=>semantics==='PER_IMPLEMENT'?'kg par haltère':semantics==='MACHINE_DISPLAY_KG'?'kg affichés':'Unité inconnue';
export function calibrationStage(view:CalibrationReadV1|null):CalibrationStage {
 if(!view?.result||['QUALIFIED','CONCERN_REVIEW','WITHDRAWN','UNAVAILABLE','INSUFFICIENT_EVIDENCE'].includes(view.result.state))return 'decision';
 if(view.allowed_actions.includes('INITIATE_TRIAL'))return 'trial';
 if(view.result.state==='OBSERVED')return 'decision';
 if(!view.progress.preparation)return 'preparation';
 if(!view.progress.setting_choice)return 'setting';
 if(view.allowed_actions.includes('ACCEPT_EXACT_SETTING'))return 'decision';
 if(view.allowed_actions.includes('INITIATE_TRIAL'))return 'trial';
 if(view.progress.observed_attempt_count)return 'setting';
 return 'familiar';
}

export function parseCalibrationOccurrence(day:string,time:string):string|null {
 const d=/^(\d{4})-(\d{2})-(\d{2})$/.exec(day),t=/^(\d{2}):(\d{2})$/.exec(time);
 if(!d||!t)return null;
 const [year,month,date]=d.slice(1).map(Number),[hours,minutes]=t.slice(1).map(Number);
 const value=new Date(year,month-1,date,hours,minutes,0,0);
 if(value.getFullYear()!==year||value.getMonth()!==month-1||value.getDate()!==date||value.getHours()!==hours||value.getMinutes()!==minutes)return null;
 return value.toISOString();
}
export type CalibrationDraft={draft_ref?:string;committed_event_ref?:string;encounter_ref:string|null;stage:CalibrationStage;candidate:string|null;place:string;device:string;instruction:string;setup:string;load:string;observedLoad:string;reps:string;completed:boolean|null;successful:boolean|null|'UNSET';quality:string|null;discomfort:string|null;stopReason:string|null;trialAt:string;trialDate:string;trialTime:string};
export function resumableCalibrationDraft(raw:unknown,encounter:string):CalibrationDraft|null {
 if(!raw||typeof raw!=='object'||(raw as CalibrationDraft).encounter_ref!==encounter)return null;
 return raw as CalibrationDraft;
}
