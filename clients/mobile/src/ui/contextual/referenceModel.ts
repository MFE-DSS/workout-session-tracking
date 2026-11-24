/** SAME_RECORDED_CONTEXT_V1: display only, never prescription or work permission. */
import type {ExecutionV3,ContextV3,PlanV3Stored} from '../../domain/planV3Types';
import type {HistoricalScienceExecution} from '../../api/trainingHistory';
export type ContextTarget={ownerId:number;sessionId:number;startedAt:string;binding:string;seId:number;setId:number;index:number;slotId:string;intentId:string;context:ContextV3;blocked:number[];readVersion:string};
export type RecordedSet={setId:number;index:number;value:number;reps:number;revision:number;unit:'kg';semantics:'MACHINE_DISPLAY_KG';performedAt:string;estimated:boolean|undefined;completedAt:string|null};
const keys=['canonical_exercise_id','context_ref','equipment_ref','realization_ref','side','load_semantics'] as const;
function known(c:ContextV3){return c?.canonical_exercise_id==='leg-extensions-assises'&&c.side==='BILATERAL'&&c.load_semantics==='MACHINE_DISPLAY_KG'&&keys.every(k=>typeof c[k]==='string'&&Boolean(c[k]?.trim()));}
function same(a:ContextV3,b:ContextV3){return known(a)&&known(b)&&keys.every(k=>a[k]===b[k]);}
export function contextTarget(state:PlanV3Stored,setId:number,blocked:number[]=[]):ContextTarget|null{
 const ex=state.execution,e=ex?.exercises.find(e=>e.sets.some(s=>s.set_id===setId)),s=e?.sets.find(s=>s.set_id===setId);
 if(state.profile!=='PLAN_V3'||!Number.isSafeInteger(state.owner_id)||state.owner_id<=0||!ex||!e||!s||!known(e.prescription.context)||e.canonical_exercise_id!==e.prescription.context.canonical_exercise_id)return null;
 return{ownerId:state.owner_id,sessionId:ex.session_id,startedAt:ex.started_at,binding:ex.binding_digest,seId:e.se_id,setId,index:s.set_index,slotId:e.slot_id,intentId:e.intent_id,context:{...e.prescription.context},blocked:[...blocked],readVersion:JSON.stringify([ex.server_now,ex.status,e.sets.map(s=>[s.set_id,s.revision,s.completed,s.observation])])};
}
export function matchingExercise(t:ContextTarget,read:HistoricalScienceExecution|ExecutionV3){
 if(read.session_id!==t.sessionId||read.binding_digest!==t.binding||Date.parse(read.started_at)!==Date.parse(t.startedAt))return null;
 const e=read.exercises.find(e=>e.se_id===t.seId);
 return e&&e.canonical_exercise_id===t.context.canonical_exercise_id&&e.slot_id===t.slotId&&e.intent_id===t.intentId&&same(e.prescription.context,t.context)&&e.sets.some(s=>s.set_id===t.setId&&s.set_index===t.index)?e:null;
}
export function recordedSet(t:ContextTarget,read:HistoricalScienceExecution|ExecutionV3,setId:number):RecordedSet|null{
 const e=matchingExercise(t,read),s=e?.sets.find(s=>s.set_id===setId),o=s?.observation,v=o?.setting;
 if(!s||s.kind!=='work'||!s.completed||!o?.completed||!same(o.context,t.context)||s.revision<1||!Number.isSafeInteger(s.revision)||s.reps!==o.reps||typeof o.reps!=='number'||!Number.isSafeInteger(o.reps)||o.reps<0||!v||v.kind!=='MASS_KG'||v.unit!=='kg'||typeof v.value!=='number'||!Number.isFinite(v.value)||v.value<0||!Number.isFinite(Date.parse(o.performed_at)))return null;
 return{setId:s.set_id,index:s.set_index,value:v.value,reps:o.reps,revision:s.revision,unit:'kg',semantics:'MACHINE_DISPLAY_KG',performedAt:o.performed_at,estimated:o.performed_at_estimated,completedAt:s.completed_at};
}
export function selectReference(t:ContextTarget,read:HistoricalScienceExecution|ExecutionV3):RecordedSet|null{
 const e=matchingExercise(t,read),previous=e?.sets.filter(s=>s.set_index===t.index-1);
 if(!previous||previous.length!==1||previous[0].set_id===t.setId||t.blocked.includes(previous[0].set_id))return null;
 return recordedSet(t,read,previous[0].set_id);
}
