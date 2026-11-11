import React,{useState} from 'react';
import {Text,View} from 'react-native';
import type {HistoricalDetail,HistoryExerciseLink} from '../../api/trainingHistory';
import {CalibrationLink} from '../plan/calibrationControls';
import {type} from '../theme';
import {dateLabel,sessionStatus} from './historyView';
import {HistoricalFactsFrame,HistoricalExerciseInstrument,HistoricalSetWindow} from './HistoricalFactsInstrument';
export function SessionFactsScreen(p:{detail:HistoricalDetail;onBack:()=>void;timeZone:string;previous?:boolean;onExercise?:(link:HistoryExerciseLink)=>void}){
 const [prescription,setPrescription]=useState(false),[sources,setSources]=useState<Set<number>>(()=>new Set()),d=p.detail;
 const selected=d.selected_se_id??(d.kind==='LEGACY'?d.facts.selected_se_id:undefined);
 const ordered=<T extends {se_id:number}>(xs:T[])=>selected===undefined?xs:[...xs].sort((a,b)=>Number(b.se_id===selected)-Number(a.se_id===selected));
 const historyLink=(seId:number)=>{const link=d.exercise_links?.find(l=>l.se_id===seId);return link?.exercise_ref&&p.onExercise?<CalibrationLink testID={`history-exercise-${seId}`} label="Historique du mouvement" disabled={p.previous} onPress={()=>p.onExercise?.(link)}/>:null;};
 const sourceLink=(seId:number)=><CalibrationLink testID={`history-provenance-${seId}`} label="Sources et limites" expanded={sources.has(seId)} onPress={()=>setSources(old=>{const next=new Set(old);if(next.has(seId))next.delete(seId);else next.add(seId);return next;})}/>;
 if(d.kind==='LEGACY'){
  const f=d.facts,s=f.session;
  return <HistoricalFactsFrame name={s.name||'Séance'} onBack={p.onBack} previous={p.previous} status={`${dateLabel(s.started_at,p.timeZone)} · ${sessionStatus(s.status)}${s.excluded_from_stats?' · exclue des statistiques':''}`}>
   {ordered(f.exercises).map(e=><HistoricalExerciseInstrument key={e.se_id} name={e.executed_name||e.prescribed_name||e.code} seId={e.se_id} context="Matériel non capturé" selected={selected===e.se_id}>
    {(width,u)=><>
     {e.sets.map(s=><HistoricalSetWindow key={s.set_id} width={width} u={u} set={s} load={s.weight_kg} rawLoad={s.raw_weight_repr} unit="kg saisis"/>)}
     {historyLink(e.se_id)}{sourceLink(e.se_id)}
     {sources.has(e.se_id)?<View style={{gap:8}}>
      <Text selectable style={type.small}>Journal historique · début {s.started_at}{s.ended_at?` · fin ${s.ended_at}`:''}</Text>
      {e.substituted_name?<Text selectable style={type.small}>Mouvement remplacé : {e.prescribed_name}</Text>:null}
      {e.sets.map(s=><View key={s.set_id} style={{gap:4}}><Text selectable style={type.small}>{s.kind==='work'?'Série':'Préparation'} {s.set_index} · horodatage du journal : {s.completed_at??'non renseigné'}</Text>{s.raw_weight_repr!=null?<Text selectable style={type.small}>Valeur de charge source : {s.raw_weight_repr}</Text>:null}{s.raw_reps_repr!=null?<Text selectable style={type.small}>Répétitions source : {s.raw_reps_repr}</Text>:null}</View>)}
      <Text style={type.small}>Prescription et matériel non capturés. Les kilogrammes saisis n'établissent pas une masse externe totale.</Text>
     </View>:null}
    </>}
   </HistoricalExerciseInstrument>)}
   {f.cardio.duration_min!==null?<Text selectable style={type.body}>Cardio · {f.cardio.duration_min} min{f.cardio.bpm_avg!==null?` · ${f.cardio.bpm_avg} bpm`:''}{f.cardio.machine_calories!==null?` · ${f.cardio.machine_calories} kcal machine`:''}</Text>:null}
  </HistoricalFactsFrame>;
 }
 const x=d.execution;
 return <HistoricalFactsFrame name="Séance conservée" onBack={p.onBack} previous={p.previous} status={`${dateLabel(x.started_at,p.timeZone)} · ${sessionStatus(x.status)}${x.excluded_from_stats?' · exclue des statistiques':''}`}>
  {ordered(x.exercises).map(e=><HistoricalExerciseInstrument key={e.se_id} name={e.canonical_exercise_id} seId={e.se_id} context="Contexte enregistré" selected={selected===e.se_id}>
   {(width,u)=><>
    {e.sets.map(s=><HistoricalSetWindow key={s.set_id} width={width} u={u} set={s} hasObservation={s.observation!==null} load={s.observation?.setting?.value??null} unit={s.observation?.context.load_semantics==='PER_IMPLEMENT'?'kg par haltère':s.observation?.context.load_semantics==='MACHINE_DISPLAY_KG'?'kg affichés':'kg externes totaux'}/>)}
    {historyLink(e.se_id)}{sourceLink(e.se_id)}
    {sources.has(e.se_id)?<View style={{gap:8}}>
     <Text selectable style={type.small}>Journal historique · début {x.started_at}{x.ended_at?` · fin ${x.ended_at}`:''}</Text>
     <Text selectable style={type.small}>{e.prescription.context.realization_ref} · {e.prescription.context.equipment_ref} · bilatéral</Text>
     {e.sets.map(s=><View key={s.set_id} style={{gap:4}}><Text selectable style={type.small}>Série {s.set_index} · journal : {s.completed_at??'non renseigné'}</Text>{s.observation?<Text selectable style={type.small}>Occurrence déclarée : {s.observation.performed_at}{s.observation.performed_at_estimated?' · heure approximative':''}</Text>:null}</View>)}
     <Text style={type.small}>Lecture historique ; aucune nouvelle permission de travail ou mesure de progression.</Text>
    </View>:null}
    {prescription?<Text style={type.small}>Prescription capturée : {e.prescription.dose.work_sets} séries · {e.prescription.dose.min_reps}–{e.prescription.dose.max_reps} rép. · repos {e.prescription.dose.rest_seconds} s. Ce sont des cibles, pas des faits réalisés.</Text>:null}
   </>}
  </HistoricalExerciseInstrument>)}
  <CalibrationLink label="Prescription capturée" expanded={prescription} onPress={()=>setPrescription(!prescription)}/>
 </HistoricalFactsFrame>;
}
