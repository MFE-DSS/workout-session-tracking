/** No persistence or mutation: fresh, bounded, owned authoritative read only. */
import type {TrainingHistoryClient} from '../../api/trainingHistory';
import {matchingExercise,recordedSet,selectReference,type ContextTarget,type RecordedSet} from './referenceModel';
export type ContextReader=Pick<TrainingHistoryClient,'sessions'|'detail'>;
export type ContextRead={state:'ready';reference:RecordedSet|null;current:RecordedSet|null;currentRevision:number;currentState:'recorded'|'not_completed'|'unqualified';indexReadId:string;indexRowsReadAt:string;detailServerNow:string}|{state:'unknown'|'cancelled'|'unavailable'|'changed'};
export async function readContext(reader:ContextReader,t:ContextTarget,current:()=>boolean):Promise<ContextRead>{
 let cursor:string|undefined;const seen=new Set<string>();
 try{for(let i=0;i<5;i++){
  if(!current())return{state:'cancelled'};
  const r=await reader.sessions({period:'all',timeZone:'UTC',limit:100,...(cursor?{cursor}:{})},current);
  if(!current()||r.state==='cancelled')return{state:'cancelled'};
  if(r.state!=='confirmed')return{state:r.state==='changed'?'changed':'unknown'};
  const page=r.value;if(page.owner_id!==t.ownerId)return{state:'unknown'};
  const entry=page.entries.find(e=>e.session_id===t.sessionId);
  if(entry){
   if(entry.execution_profile!=='SCI_V3'||entry.descriptor.execution_profile!=='SCI_V3'||entry.descriptor.binding_digest!==t.binding)return{state:'unavailable'};
   const detail=await reader.detail(page,entry,current);
   if(!current()||detail.state==='cancelled')return{state:'cancelled'};
   if(detail.state!=='confirmed')return{state:detail.state==='changed'?'changed':'unknown'};
   if(detail.value.kind!=='SCI'||!matchingExercise(t,detail.value.execution))return{state:'unavailable'};
   const execution=detail.value.execution,currentSet=matchingExercise(t,execution)!.sets.find(s=>s.set_id===t.setId)!,fact=recordedSet(t,execution,t.setId);
   return{state:'ready',reference:selectReference(t,execution),current:fact,currentRevision:currentSet.revision,currentState:fact?'recorded':currentSet.completed?'unqualified':'not_completed',indexReadId:page.read_id,indexRowsReadAt:page.rows_read_at,detailServerNow:detail.value.execution.server_now};
  }
  if(!page.next_cursor)return{state:page.completeness==='COMPLETE'?'unavailable':'unknown'};
  if(seen.has(page.next_cursor))return{state:'unknown'};seen.add(page.next_cursor);cursor=page.next_cursor;
 }}catch{return{state:current()?'unknown':'cancelled'};}
 return{state:'unknown'};
}
