/** In-memory acquisition; the canonical source and historical slots stay separate. */
import type {BuilderProgram,BuilderSourceExercise} from '../../api/programBuilderDTO';
import {BUILDER_VERSION,builderCommandJSON,type BuilderSelection,type BuilderTreeSession} from '../../domain/programBuilderCommand';
export type ManualTarget={min:string;max:string;technique:string|null;is_warmup:boolean};
export type ManualMovement={kind:'manual';selection:BuilderSelection;sets:string;targets:ManualTarget[];notes:string|null};
export type HistoricalMovement={kind:'historical';source:BuilderSourceExercise};
export type DraftMovement=ManualMovement|HistoricalMovement;
export type DraftSession={name:string;kind:'strength'|'cardio';focus:string;duration_target_minutes:number|null;notes:string|null;movements:DraftMovement[]};
export type BuilderDraft={title:string;sessions:DraftSession[]};
export function draftFromProgram(p:BuilderProgram):BuilderDraft{return {title:p.title,sessions:p.sessions.map(s=>({name:s.name,kind:s.kind,focus:s.focus,duration_target_minutes:s.duration_target_minutes,notes:s.notes,movements:s.exercises.map(e=>({kind:'historical',source:JSON.parse(JSON.stringify(e)) as BuilderSourceExercise}))}))};}
export function manualMovement(selection:BuilderSelection):ManualMovement{return {kind:'manual',selection:{slug:selection.slug,name:selection.name,ekb_version:selection.ekb_version},sets:'',targets:[],notes:null};}
export function setCount(m:ManualMovement,value:string):void{m.sets=value;if(/^[1-6]$/.test(value))m.targets=Array.from({length:Number(value)},(_,i)=>m.targets[i]??{min:'',max:'',technique:null,is_warmup:false});}
export function moveItem<T>(rows:T[],index:number,delta:-1|1):number{const to=index+delta;if(index<0||index>=rows.length||to<0||to>=rows.length)return index;const [item]=rows.splice(index,1);rows.splice(to,0,item);return to;}
export const movementName=(m:DraftMovement)=>m.kind==='historical'?m.source.exercise_name:m.selection.name;
function integer(value:string):number{if(!/^[1-9][0-9]?$/.test(value)||Number(value)>50)throw Error('manual_targets_required');return Number(value);}
export function treePayload(d:BuilderDraft):{sessions:BuilderTreeSession[]}{
 const payload={sessions:d.sessions.map((s,i)=>({position:i+1,name:s.name,kind:s.kind,focus:s.focus,duration_target_minutes:s.duration_target_minutes,notes:s.notes,exercises:s.movements.map((m,j)=>{
  if(m.kind==='historical')return {position:j+1,selection:null,keep:{slot_id:m.source.slot_id,slot_digest:m.source.slot_digest},rep_targets:null,notes:null};
  if(!/^[1-6]$/.test(m.sets)||m.targets.length!==Number(m.sets))throw Error('manual_targets_required');
  return {position:j+1,selection:{...m.selection},keep:null,notes:m.notes,rep_targets:m.targets.map(t=>({min_reps:integer(t.min),max_reps:integer(t.max),technique:t.technique,is_warmup:t.is_warmup}))};
 })}))};
 // Reuse the frozen boundary, including min<=max, text lengths, counts and bytes.
 builderCommandJSON({contract_version:BUILDER_VERSION,command_id:'check',operation:'SAVE_TREE',program_id:1,expected_source_digest:'0'.repeat(64),payload});return payload;
}
