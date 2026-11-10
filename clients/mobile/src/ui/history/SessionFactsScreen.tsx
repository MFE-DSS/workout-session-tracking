import React,{useState} from 'react';
import {Text,View} from 'react-native';
import type {HistoricalDetail,HistoryExerciseLink} from '../../api/trainingHistory';
import {AccountFrame} from '../account/AccountFrame';
import {CalibrationLink} from '../plan/calibrationControls';
import {type} from '../theme';
import {dateLabel,sessionStatus,setFact} from './historyView';
export function SessionFactsScreen(p:{detail:HistoricalDetail;onBack:()=>void;timeZone:string;previous?:boolean;onExercise?:(link:HistoryExerciseLink)=>void}){
 const [prescription,setPrescription]=useState(false),d=p.detail;
 const selected=d.selected_se_id??(d.kind==='LEGACY'?d.facts.selected_se_id:undefined);
 const ordered=<T extends {se_id:number}>(xs:T[])=>selected===undefined?xs:[...xs].sort((a,b)=>Number(b.se_id===selected)-Number(a.se_id===selected));
 const historyLink=(seId:number)=>{const link=d.exercise_links?.find(l=>l.se_id===seId);return link?.exercise_ref&&p.onExercise?<CalibrationLink testID={`history-exercise-${seId}`} label="Historique du mouvement" disabled={p.previous} onPress={()=>p.onExercise?.(link)}/>:null;};
 const selectedMark=(seId:number)=>selected===seId?<Text testID={`history-selected-exercise-${seId}`} style={type.small}>Exercice sélectionné</Text>:null;
 if(d.kind==='LEGACY'){
  const f=d.facts,s=f.session;
  return <AccountFrame title={s.name||'Séance'} onBack={p.onBack}>
   {p.previous?<Text style={type.small}>Lecture précédente</Text>:null}
   <Text style={type.body}>{dateLabel(s.started_at,p.timeZone)} · {sessionStatus(s.status)}{s.excluded_from_stats?' · exclue des statistiques':''}</Text>
   {ordered(f.exercises).map(e=><View key={e.se_id} style={{gap:8}}>{selectedMark(e.se_id)}<Text accessibilityRole="header" style={type.bodyStrong}>{e.executed_name||e.prescribed_name||e.code}</Text>
    {e.substituted_name?<Text style={type.small}>Mouvement remplacé : {e.prescribed_name}</Text>:null}
    <Text testID={`history-context-${e.se_id}`} style={type.small}>Contexte matériel non capturé</Text>
    {historyLink(e.se_id)}
   {e.sets.map(s=><View testID={`history-set-${s.set_id}`} key={s.set_id}><Text style={type.body}>{s.kind==='work'?'Série':'Préparation'} {s.set_index} · {setFact(s)}</Text>{s.completed_at?<Text style={type.small}>{dateLabel(s.completed_at,p.timeZone)} · horodatage du journal</Text>:null}</View>)}
   </View>)}
   {f.cardio.duration_min!==null?<Text style={type.body}>Cardio · {f.cardio.duration_min} min{f.cardio.bpm_avg!==null?` · ${f.cardio.bpm_avg} bpm`:''}{f.cardio.machine_calories!==null?` · ${f.cardio.machine_calories} kcal machine`:''}</Text>:null}
   <Text style={type.small}>Prescription et contexte historiques non capturés. Les kilogrammes saisis ne prouvent pas une masse externe totale.</Text>
  </AccountFrame>;
 }
 const x=d.execution;
 return <AccountFrame title="Séance conservée" onBack={p.onBack}>
  {p.previous?<Text style={type.small}>Lecture précédente</Text>:null}
  <Text style={type.body}>{dateLabel(x.started_at,p.timeZone)} · {sessionStatus(x.status)}</Text>
  {ordered(x.exercises).map(e=><View key={e.se_id} style={{gap:8}}>{selectedMark(e.se_id)}<Text accessibilityRole="header" style={type.bodyStrong}>{e.canonical_exercise_id}</Text>
   <Text style={type.small}>{e.prescription.context.realization_ref} · {e.prescription.context.equipment_ref} · bilatéral</Text>
   {historyLink(e.se_id)}
   {e.sets.map(s=><View key={s.set_id} testID={`history-set-${s.set_id}`}><Text style={type.body}>Série {s.set_index} · {setFact(s)}</Text>{s.observation?<Text style={type.small}>{dateLabel(s.observation.performed_at,p.timeZone)} · {s.observation.performed_at_estimated?'heure déclarée approximative':'occurrence déclarée'}</Text>:null}</View>)}
   {prescription?<Text style={type.small}>Prescription capturée : {e.prescription.dose.work_sets} séries · {e.prescription.dose.min_reps}–{e.prescription.dose.max_reps} rép. · repos {e.prescription.dose.rest_seconds} s. Ce sont des cibles, pas des faits réalisés.</Text>:null}
  </View>)}
  <CalibrationLink label="Prescription capturée" expanded={prescription} onPress={()=>setPrescription(!prescription)}/>
  <Text style={type.small}>Journal historique. Aucune nouvelle permission de travail ni score de progression.</Text>
 </AccountFrame>;
}
