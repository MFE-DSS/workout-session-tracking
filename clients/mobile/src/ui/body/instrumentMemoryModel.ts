import {chronology,type BodyObservation} from './bodyCockpitModel';
export type DraftPoint={day:string;value:number};
const dayTime=(day:string)=>Date.parse(day+'T00:00:00Z');
export function memoryGeometry(rows:BodyObservation[],width:number,height:number,draft?:DraftPoint){
 const left=12,right=Math.max(12,width-52),top=12,bottom=Math.max(12,height-30);
 const base=chronology(rows,right-left,bottom-top),points=base.points.map(p=>({...p,x:p.x+left,y:p.y+top}));
 const dates=points.map(p=>p.observation.day!).sort(),from=dates[0]??null,through=dates.at(-1)??null;
 const ticks=base.ticks.map(t=>({...t,y:t.y+top}));let projected:null|{x:number;y:number;outside:boolean}=null;
 if(draft&&from&&through&&Number.isFinite(draft.value)&&Number.isFinite(dayTime(draft.day))){
  const min=ticks[0].value,max=ticks.at(-1)!.value,start=dayTime(from),end=dayTime(through),time=dayTime(draft.day);
  projected={x:start===end?(left+right)/2:left+(time-start)/(end-start)*(right-left),y:bottom-(draft.value-min)/(max-min)*(bottom-top),outside:time<start||time>end||draft.value<min||draft.value>max};
 }
 return {points,ticks,from,through,left,right,top,bottom,draft:projected};
}
export function sourceKind(o:BodyObservation):'manual'|'correction'|'unknown'{if(o.value.provenance?.origin!=='USER_DECLARED')return 'unknown';return o.value.provenance.acquisition==='MANUAL_CORRECTION'?'correction':o.value.provenance.acquisition==='MANUAL_ENTRY'?'manual':'unknown';}
export function sourceLabel(o:BodyObservation){return o.value.quality!=='KNOWN'?'Source non comparable':sourceKind(o)==='unknown'?(o.value.provenance?.origin==='USER_DECLARED'?'Déclaré · méthode inconnue':'Origine inconnue'):sourceKind(o)==='correction'?'Déclaré · corrigé':'Relevé déclaré';}
