import type {AuthSession} from '../auth/authSession';
import type {BodyMeasurementsClient,BodyReadOptions,BodyPage,BodyEntry,BodyErasurePage,BodyErasureReadOptions} from './bodyMeasurements';
import type {HistoryWindow} from './trainingHistory';
import type {WeightWindowState,WeightPoint} from './trainingHistoryResource';
export type BodyReadState<P=BodyPage>={status:'idle'|'pending'|'confirmed'|'unknown'|'changed'|'unavailable'|'rejected'|'consent_required';previous:boolean;value?:P};
export class BodyMeasurementsResource{
 private value:BodyReadState={status:'idle',previous:false};private revision:number;private sequence=0;private options:BodyReadOptions={};private cursors=new Set<string>();
 constructor(private auth:AuthSession,private client:BodyMeasurementsClient){this.revision=auth.revision;}
 invalidate(){this.sequence++;this.value={status:'idle',previous:false};this.cursors.clear();}
 get state():BodyReadState{if(this.revision!==this.auth.revision){this.revision=this.auth.revision;this.invalidate();}return JSON.parse(JSON.stringify(this.value));}
 refresh(options:BodyReadOptions={}){void this.state;const same=JSON.stringify(options)===JSON.stringify(this.options);if(!same)this.invalidate();this.options={...options};this.cursors.clear();return this.read();}
 loadNext(){const s=this.state;return s.status==='confirmed'&&s.value?.next_cursor?this.read(s.value.next_cursor):Promise.resolve(s);}
 private async read(cursor?:string){
  const old=this.state,revision=this.auth.revision,sequence=++this.sequence;
  this.value={...old,status:'pending',previous:Boolean(old.value)};
  let outcome;try{outcome=await this.client.read({...this.options,...(cursor?{cursor}:{})});}catch{outcome={state:'unknown'} as const;}
  if(revision!==this.auth.revision||sequence!==this.sequence)return this.state;
  if(outcome.state==='confirmed'){
   const next=outcome.value,prior=cursor?old.value:undefined;
   if(prior&&(next.body_revision!==prior.body_revision||next.owner_id!==prior.owner_id||next.entries.some(e=>prior.entries.some(p=>p.measurement_id===e.measurement_id))||next.next_cursor!==null&&this.cursors.has(next.next_cursor))){this.value={status:'changed',previous:false};}
   else{if(cursor)this.cursors.add(cursor);this.value={status:'confirmed',previous:false,value:prior?{...next,state:'AVAILABLE',entries:[...prior.entries,...next.entries]}:next};}
  }else if(outcome.state==='unknown')this.value={...old,status:'unknown',previous:Boolean(old.value)};
  else this.value={status:outcome.state==='cancelled'?'idle':outcome.state,previous:false};
  return this.state;
 }
}
export type BodyWeightSource={date_precision:BodyEntry['date_precision'];origin:string;acquisition:string;source_ref:string;root_ref:number;revision:number};
export function bodyWeight(entry:BodyEntry):WeightPoint[]{const v=entry.fields.weight_kg;if(v.quality==='MISSING')return[];return[{measurement_id:entry.measurement_id,measured_at:entry.measured_at,recorded_at:entry.recorded_at,value:v.value,raw_value_repr:v.raw_value_repr,quality:v.quality,provenance:v.provenance,bodySource:{...v.provenance,date_precision:entry.date_precision,root_ref:entry.root_ref,revision:entry.revision}}];}
const calendar=(instant:string,zone:string)=>{const p=new Intl.DateTimeFormat('en-CA',{timeZone:zone,year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date(instant));return['year','month','day'].map(k=>p.find(x=>x.type===k)?.value).join('-');};
/** Separate erasure projection; it never fabricates BodyEntry fields or a grant. */
export class BodyErasureResource{
 private value:BodyReadState<BodyErasurePage>={status:'idle',previous:false};private revision:number;private sequence=0;private options:BodyErasureReadOptions={};private cursors=new Set<string>();
 constructor(private auth:AuthSession,private client:BodyMeasurementsClient){this.revision=auth.revision;}
 invalidate(){this.sequence++;this.value={status:'idle',previous:false};this.cursors.clear();}
 get state():BodyReadState<BodyErasurePage>{if(this.revision!==this.auth.revision){this.revision=this.auth.revision;this.invalidate();}return JSON.parse(JSON.stringify(this.value));}
 refresh(options:BodyErasureReadOptions={}){void this.state;if(JSON.stringify(options)!==JSON.stringify(this.options))this.invalidate();this.options={...options};this.cursors.clear();return this.read();}
 loadNext(){const state=this.state;return state.status==='confirmed'&&state.value?.next_cursor?this.read(state.value.next_cursor):Promise.resolve(state);}
 private async read(cursor?:string){
  const old=this.state,revision=this.auth.revision,sequence=++this.sequence;
  this.value={...old,status:'pending',previous:Boolean(old.value)};
  let result;try{result=await this.client.readErasure({...this.options,...(cursor?{cursor}:{})});}catch{result={state:'unknown'} as const;}
  if(revision!==this.auth.revision||sequence!==this.sequence)return this.state;
  if(result.state==='confirmed'){
   const next=result.value,prior=cursor?old.value:undefined;
   if(prior&&(next.owner_id!==prior.owner_id||next.body_revision!==prior.body_revision||next.window.from!==prior.window.from||next.window.through!==prior.window.through
    ||next.entries.some(e=>prior.entries.some(p=>p.root_ref===e.root_ref||p.measurement_id===e.measurement_id))
    ||next.next_cursor!==null&&this.cursors.has(next.next_cursor))){this.value={status:'changed',previous:false};}
   else{if(cursor)this.cursors.add(cursor);this.value={status:'confirmed',previous:false,value:prior?{...next,state:'AVAILABLE',entries:[...prior.entries,...next.entries]}:next};}
  }else if(result.state==='unknown')this.value={...old,status:'unknown',previous:Boolean(old.value)};
  else this.value={status:result.state==='cancelled'?'idle':result.state,previous:false};
  return this.state;
 }
}
export class BodyWeightWindowResource{
 private value:WeightWindowState={status:'idle',previous:false,coverage:'PARTIAL',canContinue:false,entries:[]};private revision:number;private sequence=0;
 constructor(private auth:AuthSession,private source:BodyMeasurementsResource){this.revision=auth.revision;}
 invalidate(){this.sequence++;this.value={status:'idle',previous:false,coverage:'PARTIAL',canContinue:false,entries:[]};this.source.invalidate();}
 get state(){if(this.revision!==this.auth.revision){this.revision=this.auth.revision;this.invalidate();}return JSON.parse(JSON.stringify(this.value));}
 refresh(window:HistoryWindow){const old=this.state;return this.read(window,false,JSON.stringify(window)===JSON.stringify(old.window)?old:undefined);}
 continue(){const s=this.state;return s.canContinue&&s.window?this.read(s.window,true,s):Promise.resolve(s);}
 private async read(window:HistoryWindow,more:boolean,old?:WeightWindowState){
  const revision=this.auth.revision,sequence=++this.sequence,current=()=>revision===this.auth.revision&&sequence===this.sequence;
  this.value={status:'pending',previous:Boolean(old?.entries.length),coverage:'PARTIAL',canContinue:false,entries:old?.entries??[],window};
  let result=await(more?this.source.loadNext():this.source.refresh({mode:'weight',limit:100}));let pages=0;
  while(current()){
   if(result.status!=='confirmed'||!result.value){this.value=result.status==='unknown'?{...this.value,status:'unknown',previous:Boolean(old?.entries.length)}:{status:result.status==='changed'?'unknown':result.status,previous:false,coverage:'PARTIAL',canContinue:false,entries:[],window};return this.state;}
   const rows=result.value.entries;
   const afterStart=(e:BodyEntry)=>window.from===null|| (e.date_precision==='DAY_UTC_CONVENTION'?e.measured_at.slice(0,10)>=calendar(window.from,window.time_zone):Date.parse(e.measured_at)>=Date.parse(window.from));
   const beforeEnd=(e:BodyEntry)=>e.date_precision==='DAY_UTC_CONVENTION'?e.measured_at.slice(0,10)<=calendar(window.until,window.time_zone):Date.parse(e.measured_at)<Date.parse(window.until);
   const done=result.value.next_cursor===null||rows.some(e=>!afterStart(e));
   this.value={status:'confirmed',previous:false,coverage:done?'COMPLETE':'PARTIAL',canContinue:!done,window,entries:rows.filter(e=>afterStart(e)&&beforeEnd(e)).flatMap(bodyWeight)};
   if(done||++pages>=10)return this.state;
   result=await this.source.loadNext();
  }
  return this.state;
 }
}
