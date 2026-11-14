import type {BodyEntry,BodyKey} from '../../api/bodyMeasurements';

/** Pure read projection. No permissions, write payloads or inferred observation time. */
export type BodyObservation={entry:BodyEntry;key:BodyKey;value:BodyEntry['fields'][BodyKey];day:string|null};
const exactDay=(e:BodyEntry)=>{
 if(e.date_precision!=='DAY_UTC_CONVENTION')return null;
 const day=e.measured_at.slice(0,10),instant=Date.parse(day+'T00:00:00Z');
 return Number.isFinite(instant)&&new Date(instant).toISOString().slice(0,10)===day?day:null;
};
export function bodyObservations(entries:BodyEntry[],key:BodyKey):BodyObservation[]{
 return entries.filter(e=>e.state==='CURRENT'&&e.fields[key]&&e.fields[key].quality!=='MISSING')
  .map(entry=>({entry,key,value:entry.fields[key],day:exactDay(entry)}));
}
const plottable=(o:BodyObservation)=>o.day!==null&&o.value.quality==='KNOWN'&&o.value.value!==null&&Number.isFinite(o.value.value);
export function defaultObservation(rows:BodyObservation[]):BodyObservation|null {
 if(!rows.length||rows.some(r=>r.day===null))return null;
 const latest=rows.reduce((day,r)=>r.day!>day?r.day!:day,''),matches=rows.filter(r=>r.day===latest);
 return matches.length===1?matches[0]:null;
}
export function compareObservations(a:BodyObservation,b:BodyObservation){
 if(!plottable(a)||!plottable(b)||a.key!==b.key||a.value.unit!==b.value.unit||a.day!>=b.day!)return null;
 return {difference:Number((b.value.value!-a.value.value!).toPrecision(12)),days:(Date.parse(b.day!+'T00:00:00Z')-Date.parse(a.day!+'T00:00:00Z'))/86400000,unit:a.value.unit,from:a.day!,through:b.day!};
}
/** An observation plot, never a smoothed curve or a clinical reference range. */
export function chronology(rows:BodyObservation[],width:number,height:number){
 const known=rows.filter(plottable),values=known.map(r=>r.value.value!),dates=known.map(r=>Date.parse(r.day!+'T00:00:00Z'));
 if(!known.length)return {points:[],ticks:[]};
 const lo=Math.min(...values),hi=Math.max(...values),span=hi-lo,pad=span?span*0.15:Math.max(Math.abs(lo)*0.005,0.1),min=lo-pad,max=hi+pad;
 const start=Math.min(...dates),end=Math.max(...dates);
 return {points:known.map(observation=>({observation,x:end===start?width/2:(Date.parse(observation.day!+'T00:00:00Z')-start)/(end-start)*width,y:height-(observation.value.value!-min)/(max-min)*height})),
  ticks:[min,(min+max)/2,max].map(value=>({value,y:height-(value-min)/(max-min)*height}))};
}
export const bodyNumber=(value:number)=>new Intl.NumberFormat('fr-FR',{maximumFractionDigits:12}).format(value);
export const bodyDay=(day:string|null)=>day?new Intl.DateTimeFormat('fr-FR',{day:'numeric',month:'short',timeZone:'UTC'}).format(new Date(day+'T00:00:00Z')):'Date inconnue';
