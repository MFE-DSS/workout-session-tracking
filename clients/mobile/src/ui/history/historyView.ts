import type {HistoryWindow} from '../../api/trainingHistory';
import type {WeightEntry} from '../../api/weightHistory';
export const numeric=(n:number)=>String(n).replace('.',',');
export function dateLabel(instant:string,timeZone='UTC'){
 try{return new Intl.DateTimeFormat('fr-FR',{day:'numeric',month:'short',year:'numeric',timeZone}).format(new Date(instant));}catch{return instant;}
}
export function periodLabel(w:HistoryWindow){return `${w.from?`Du ${dateLabel(w.from,w.time_zone)} au`:'Tout l’historique jusqu’au'} ${dateLabel(w.until,w.time_zone)} · ${w.time_zone}`;}
export function sessionStatus(value:string){return({completed:'Terminée',abandoned:'Abandonnée',active:'En cours',in_progress:'En cours',paused:'En pause'} as Record<string,string>)[value]??value;}
export function setFact(s:{completed:boolean;reps:number|null;weight_kg?:number|null;raw_weight_repr?:string|null;raw_reps_repr?:string|null;observation?:{setting:{value:number|null}|null;context:{load_semantics:string}}|null}){
 if(!s.completed&&s.reps===null&&s.weight_kg==null&&s.observation==null&&s.raw_weight_repr==null&&s.raw_reps_repr==null)return 'Aucun fait enregistré';
 const unit=s.observation?.context.load_semantics;
 const load=s.raw_weight_repr!=null?`Valeur de charge invalide · source « ${s.raw_weight_repr} »`:s.observation?.setting?.value!=null?`${numeric(s.observation.setting.value)} ${unit==='PER_IMPLEMENT'?'kg par haltère':unit==='MACHINE_DISPLAY_KG'?'kg affichés':'kg externes totaux'}`:s.weight_kg!=null?`${numeric(s.weight_kg)} kg saisis · contexte inconnu`:'Charge inconnue';
 return `${load} · ${s.raw_reps_repr!=null?`répétitions invalides · source « ${s.raw_reps_repr} »`:s.reps===null?'répétitions inconnues':`${s.reps} rép.`}${s.completed?'':' · non complétée'}`;
}
const plottedWeight=(rows:WeightEntry[])=>rows.filter(e=>e.quality==='KNOWN'&&e.value!==null&&Number.isFinite(e.value)&&Number.isFinite(Date.parse(e.measured_at)));
export function weightExtent(rows:WeightEntry[]){
 const points=plottedWeight(rows);if(!points.length)return null;
 const dated=[...points].sort((a,b)=>Date.parse(a.measured_at)-Date.parse(b.measured_at));
 return{low:Math.min(...points.map(e=>e.value!)),high:Math.max(...points.map(e=>e.value!)),from:dated[0].measured_at,until:dated[dated.length-1].measured_at};
}
/** Raw measured points only. No line, smoothing, predicted value or zero imputation. */
export function weightGeometry(rows:WeightEntry[],width:number,height:number){
 const points=plottedWeight(rows);
 if(!points.length)return[];const times=points.map(e=>Date.parse(e.measured_at)),values=points.map(e=>e.value!);
 const loT=Math.min(...times),hiT=Math.max(...times),loV=Math.min(...values),hiV=Math.max(...values),pad=10;
 return points.map(e=>({id:e.measurement_id,x:hiT===loT?width/2:pad+(Date.parse(e.measured_at)-loT)/(hiT-loT)*(width-pad*2),y:hiV===loV?height/2:height-pad-(e.value!-loV)/(hiV-loV)*(height-pad*2)}));
}
