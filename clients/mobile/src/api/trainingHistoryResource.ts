/** Memory-only historical consumers. No commands, permission or persistent copy. */
import {AuthSession} from '../auth/authSession';
import {jsonCopy} from './firstPlanV3';
import {TrainingHistoryClient,type HistoryPage,type HistoryPeriod,type HistoryWindow,type HistoryEntry,type HistoryOccurrence,type ExercisePage,type ExerciseIndexEntry,type HistoricalDetail,type HistoryOutcome} from './trainingHistory';
import {WeightHistoryResource} from './weightHistoryResource';
import type {WeightEntry} from './weightHistory';
export type ReadSlot<T>={status:'idle'|'pending'|'confirmed'|'unknown'|'changed'|'unavailable'|'rejected';value?:T;previous:boolean};
type Slots={sessions:ReadSlot<HistoryPage>;exercises:ReadSlot<ExercisePage<ExerciseIndexEntry>>;occurrences:ReadSlot<ExercisePage<HistoryOccurrence>>;detail:ReadSlot<HistoricalDetail>};
export type TrainingHistoryState=Slots&{selectedExercise:string|null;selectedEntry:number|null;selectedExerciseLabel?:string};
const idle=<T>():ReadSlot<T>=>({status:'idle',previous:false});
const initial=():TrainingHistoryState=>({sessions:idle(),exercises:idle(),occurrences:idle(),detail:idle(),selectedExercise:null,selectedEntry:null});
const equal=(a:unknown,b:unknown)=>JSON.stringify(a)===JSON.stringify(b);
export class TrainingHistoryResource{
 private value=initial();private revision:number;private epoch=0;
 private seq={sessions:0,exercises:0,occurrences:0,detail:0};
 private cursors={sessions:new Set<string>(),exercises:new Set<string>(),occurrences:new Set<string>()};
 constructor(private readonly auth:AuthSession,private readonly client:TrainingHistoryClient){this.revision=auth.revision;}
 get state():TrainingHistoryState{if(this.revision!==this.auth.revision){this.revision=this.auth.revision;this.invalidate();}return jsonCopy(this.value);}
 invalidate(){this.epoch++;this.value=initial();this.cursors={sessions:new Set(),exercises:new Set(),occurrences:new Set()};}
 private async run<K extends keyof Slots,T>(key:K,send:(current:()=>boolean)=>Promise<HistoryOutcome<T>>,merge?:(next:T,old:T)=>T):Promise<TrainingHistoryState>{
  void this.state;const revision=this.revision,epoch=this.epoch,seq=++this.seq[key],before=this.value[key] as ReadSlot<T>;
  const current=()=>revision===this.auth.revision&&epoch===this.epoch&&seq===this.seq[key];
  (this.value[key] as ReadSlot<T>)={status:'pending',previous:before.value!==undefined,...(before.value===undefined?{}:{value:before.value})};
  let outcome:HistoryOutcome<T>;try{outcome=await send(current);}catch{outcome={state:'unknown'};}
  if(!current())return this.state;
  if(outcome.state==='confirmed'){
   try{const next=merge&&before.value?merge(outcome.value,before.value):outcome.value;(this.value[key] as ReadSlot<T>)={status:'confirmed',previous:false,value:jsonCopy(next)};}
   catch{(this.value[key] as ReadSlot<T>)={status:'unknown',previous:before.value!==undefined,...(before.value===undefined?{}:{value:before.value})};}
  }else if(outcome.state==='unknown'){
   (this.value[key] as ReadSlot<T>)={status:'unknown',previous:before.value!==undefined,...(before.value===undefined?{}:{value:before.value})};
  }else (this.value[key] as ReadSlot<T>)={status:outcome.state==='cancelled'?'idle':outcome.state,previous:false};
  return this.state;
 }
 refresh(period:HistoryPeriod,timeZone:string){void this.state;const old=this.value.sessions;this.invalidate();if(old.value?.window.period===period&&old.value.window.time_zone===timeZone)this.value.sessions=old;
  return this.run('sessions',current=>this.client.sessions({period,timeZone},current));}
 nextSessions(){const p=this.state.sessions;if(p.status!=='confirmed'||!p.value?.next_cursor)return Promise.resolve(this.state);const old=p.value,cursor=old.next_cursor!;this.cursors.sessions.add(cursor);
  return this.run('sessions',current=>this.client.sessions({period:old.window.period,timeZone:old.window.time_zone,cursor},current),(n:HistoryPage,o:HistoryPage)=>{
   if(n.read_id!==o.read_id||n.read_context!==o.read_context||!equal(n.window,o.window)||!equal(n.counts,o.counts)||!equal(n.weekly_counts,o.weekly_counts)||n.counts_read_at!==o.counts_read_at||n.entries.some(e=>o.entries.some(x=>x.session_id===e.session_id))||n.next_cursor!==null&&this.cursors.sessions.has(n.next_cursor))throw Error('history_page_changed');
   return{...n,state:'AVAILABLE' as const,entries:[...o.entries,...n.entries]};});}
 private context(){const p=this.state.sessions;return p.status==='confirmed'?p.value:undefined;}
 loadExercises(){const p=this.context();if(!p)return Promise.resolve(this.state);this.seq.occurrences++;this.seq.detail++;this.value.exercises=idle();this.value.occurrences=idle();this.value.detail=idle();this.value.selectedExercise=null;this.value.selectedEntry=null;this.cursors.exercises.clear();return this.run('exercises',current=>this.client.exercises(p,{},current));}
 nextExercises(){const p=this.context(),x=this.state.exercises;if(!p||x.status!=='confirmed'||!x.value?.next_cursor)return Promise.resolve(this.state);const cursor=x.value.next_cursor;this.cursors.exercises.add(cursor);
  return this.run('exercises',current=>this.client.exercises(p,{cursor},current),(n:ExercisePage<ExerciseIndexEntry>,o:ExercisePage<ExerciseIndexEntry>)=>this.mergeScan(n,o,'exercises',e=>e.exercise_ref));}
 selectExercise(exerciseRef:string){const p=this.context(),x=this.state.exercises;if(!p||x.status!=='confirmed'||!x.value?.entries.some(e=>e.exercise_ref===exerciseRef))return Promise.resolve(this.state);
  this.seq.detail++;this.value.detail=idle();this.value.selectedEntry=null;this.value.occurrences=idle();this.value.selectedExercise=exerciseRef;this.value.selectedExerciseLabel=x.value!.entries.find(e=>e.exercise_ref===exerciseRef)!.name;this.cursors.occurrences.clear();return this.run('occurrences',current=>this.client.occurrences(p,exerciseRef,{},current));}
 nextOccurrences(){const p=this.context(),x=this.state.occurrences,selection=this.value.selectedExercise;if(!p||!selection||x.status!=='confirmed'||!x.value?.next_cursor)return Promise.resolve(this.state);const cursor=x.value.next_cursor;this.cursors.occurrences.add(cursor);
  return this.run('occurrences',current=>this.client.occurrences(p,selection,{cursor},current),(n:ExercisePage<HistoryOccurrence>,o:ExercisePage<HistoryOccurrence>)=>this.mergeScan(n,o,'occurrences',e=>e.occurrence_ref));}
 private mergeScan<T>(n:ExercisePage<T>,o:ExercisePage<T>,key:'exercises'|'occurrences',identity:(row:T)=>string):ExercisePage<T>{
  if(n.read_id!==o.read_id||!equal(n.window,o.window)||n.next_cursor!==null&&this.cursors[key].has(n.next_cursor))throw Error('history_scan_changed');
  const rows=new Map(o.entries.map(e=>[identity(e),e]));for(const e of n.entries)rows.set(identity(e),e);return{...n,state:rows.size?'AVAILABLE':n.state,entries:[...rows.values()]};
 }
 selectEntry(entry:HistoryEntry){const p=this.context();if(!p)return Promise.resolve(this.state);const owned=p.entries.find(e=>e.session_id===entry.session_id&&e.entry_ref===entry.entry_ref);if(!owned)return Promise.resolve(this.state);
  this.value.selectedEntry=owned.session_id;this.value.detail=idle();return this.run('detail',current=>this.client.detail(p,owned,current));}
 selectOccurrence(entry:HistoryOccurrence){const p=this.context(),o=this.state.occurrences;if(!p||!this.value.selectedExercise||o.status!=='confirmed')return Promise.resolve(this.state);const owned=o.value?.entries.find(e=>e.occurrence_ref===entry.occurrence_ref&&e.session_id===entry.session_id);if(!owned)return Promise.resolve(this.state);
  this.value.selectedEntry=owned.session_id;this.value.detail=idle();return this.run('detail',current=>this.client.detail(p,owned,current));}
 openExerciseFromDetail(seId:number,exerciseRef:string){
  const p=this.context(),detail=this.state.detail;if(!p||detail.status!=='confirmed'||!detail.value)return Promise.resolve(this.state);
  const link=detail.value.exercise_links?.find(l=>l.se_id===seId&&l.exercise_ref===exerciseRef);if(!link||link.exercise_ref===null)return Promise.resolve(this.state);
  this.seq.detail++;this.value.selectedEntry=null;this.value.detail=idle();this.value.selectedExercise=link.exercise_ref;this.value.selectedExerciseLabel=link.name;this.value.occurrences=idle();this.cursors.occurrences.clear();
  return this.run('occurrences',current=>this.client.occurrences(p,link.exercise_ref!,{},current));
 }
 back(){void this.state;this.seq.detail++;if(this.value.selectedEntry!==null){this.value.selectedEntry=null;this.value.detail=idle();}else{this.seq.occurrences++;this.value.selectedExercise=null;this.value.occurrences=idle();}return this.state;}
}
export type WeightPoint=Omit<WeightEntry,'provenance'>&{provenance:WeightEntry['provenance']|import('./bodyMeasurements').BodyValue['provenance'];bodySource?:import('./bodyMeasurementsResource').BodyWeightSource};
export type WeightWindowState={status:'idle'|'pending'|'confirmed'|'unknown'|'consent_required'|'unavailable'|'rejected';previous:boolean;coverage:'COMPLETE'|'PARTIAL';canContinue:boolean;entries:WeightPoint[];window?:HistoryWindow};
const emptyWeight=():WeightWindowState=>({status:'idle',previous:false,coverage:'PARTIAL',canContinue:false,entries:[]});
export class WeightWindowResource{
 private value=emptyWeight();private revision:number;private sequence=0;private consumed=0;
 constructor(private readonly auth:AuthSession,private readonly source:WeightHistoryResource){this.revision=auth.revision;}
 invalidate(){this.sequence++;this.consumed=0;this.value=emptyWeight();}
 get state(){if(this.revision!==this.auth.revision){this.revision=this.auth.revision;this.invalidate();void this.source.state;}return jsonCopy(this.value);}
 refresh(window:HistoryWindow){void this.state;const old=equal(this.value.window,window)?this.value:emptyWeight();this.consumed=0;return this.read(jsonCopy(window),false,old);}
 continue(){const s=this.state;return s.status==='confirmed'&&s.canContinue&&s.window?this.read(s.window,true,s):Promise.resolve(s);}
 private async read(window:HistoryWindow,continuation:boolean,old:WeightWindowState):Promise<WeightWindowState>{
  const revision=this.auth.revision,sequence=++this.sequence,current=()=>revision===this.auth.revision&&sequence===this.sequence;
  this.value={...old,status:'pending',previous:old.entries.length>0,coverage:'PARTIAL',canContinue:false,window};
  let result=await(continuation?this.source.loadNext():this.source.refresh()),used=0;
  while(current()){
   if(result.state!=='confirmed'){
    this.value=result.state==='unknown'?{...this.value,status:'unknown',previous:this.value.entries.length>0,coverage:'PARTIAL',canContinue:false,window}:{...emptyWeight(),status:result.state==='cancelled'?'idle':result.state==='pending'||result.state==='idle'?'unknown':result.state,window};return this.state;
   }
   const rows=result.value.entries;
   if(rows.some((e,i)=>i>0&&(Date.parse(rows[i-1].measured_at)<Date.parse(e.measured_at)||(Date.parse(rows[i-1].measured_at)===Date.parse(e.measured_at)&&rows[i-1].measurement_id<=e.measurement_id)))){
    this.value={...old,status:'unknown',previous:old.entries.length>0,coverage:'PARTIAL',canContinue:false,window};return this.state;
   }
   used+=rows.length-this.consumed;this.consumed=rows.length;
   const lower=window.from===null?-Infinity:Date.parse(window.from),until=Date.parse(window.until);
   const reached=rows.some(e=>Date.parse(e.measured_at)<lower),done=reached||result.value.next_cursor===null;
   this.value={status:'confirmed',previous:false,coverage:done?'COMPLETE':'PARTIAL',canContinue:!done,window,entries:rows.filter(e=>Date.parse(e.measured_at)>=lower&&Date.parse(e.measured_at)<until)};
   if(done||used>=1000)return this.state;
   result=await this.source.loadNext();
  }
  return this.state;
 }
}
