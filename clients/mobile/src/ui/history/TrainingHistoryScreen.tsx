import React,{useState} from 'react';
import {Text,View} from 'react-native';
import type {HistoryPeriod,HistoryEntry,HistoryOccurrence} from '../../api/trainingHistory';
import type {TrainingHistoryState,WeightWindowState} from '../../api/trainingHistoryResource';
import {AccountFrame} from '../account/AccountFrame';
import {CalibrationChoices,CalibrationLink} from '../plan/calibrationControls';
import {type} from '../theme';
import {dateLabel,periodLabel,sessionStatus} from './historyView';
import {WeightTrend} from './WeightTrend';
import {SessionFactsScreen} from './SessionFactsScreen';
import {ExerciseHistoryScreen} from './ExerciseHistoryScreen';
export type ProgressProps={state:TrainingHistoryState;weight:WeightWindowState;period:HistoryPeriod;onPeriod:(period:HistoryPeriod)=>void;onRefresh:()=>void;onMore:()=>void;onExercises:()=>void;onExercise:(ref:string)=>void;onMoreExercises:()=>void;onOccurrence:(entry:HistoryOccurrence)=>void;onMoreOccurrences:()=>void;onEntry:(entry:HistoryEntry)=>void;onBack:()=>void;onMoreWeight:()=>void;onDetailExercise?:(seId:number,ref:string)=>void};
export function TrainingHistoryScreen(p:ProgressProps){
 const [help,setHelp]=useState(false),[sessionsExpanded,setSessionsExpanded]=useState<string|null>(null),[weeksExpanded,setWeeksExpanded]=useState<string|null>(null),s=p.state,r=s.sessions,v=r.value,timeZone=v?.window.time_zone??'UTC';
 if(s.selectedEntry!==null){
  if(s.detail.value)return <SessionFactsScreen detail={s.detail.value} timeZone={timeZone} previous={s.detail.previous} onBack={p.onBack} onExercise={link=>{if(link.exercise_ref)p.onDetailExercise?.(link.se_id,link.exercise_ref);}}/>;
  return <AccountFrame title="Séance" onBack={p.onBack}><Text style={type.body}>{s.detail.status==='pending'?'Lecture des faits…':s.detail.status==='changed'?'La séance a changé. Actualise Progrès.':'Les faits n’ont pas pu être confirmés.'}</Text><CalibrationLink label="Retour à Progrès" onPress={p.onRefresh}/></AccountFrame>;
 }
 if(s.selectedExercise){const name=s.selectedExerciseLabel??s.exercises.value?.entries.find(e=>e.exercise_ref===s.selectedExercise)?.name??'Exercice';return <ExerciseHistoryScreen name={name} read={s.occurrences} timeZone={timeZone} onSelect={p.onOccurrence} onMore={p.onMoreOccurrences} onBack={p.onBack}/>;}
 return <AccountFrame title="Progrès">
  <View testID="progress-period"><CalibrationChoices label="Période" value={p.period} options={[{value:'4w',label:'4 sem.'},{value:'12w',label:'12 sem.'},{value:'all',label:'Tout'}]} onChange={p.onPeriod}/></View>
  {v?<Text style={type.small}>{periodLabel(v.window)}</Text>:null}
  {r.previous?<Text testID="progress-previous" accessibilityLiveRegion="polite" style={type.small}>Lecture précédente · à actualiser</Text>:null}
  {r.status==='pending'?<Text accessibilityLiveRegion="polite" style={type.small}>Actualisation…</Text>:null}
  {r.status!=='confirmed'&&r.status!=='pending'?<Text style={type.small}>La lecture n’a pas pu être confirmée.</Text>:null}
  {v?<View style={{gap:6}}><Text testID="progress-frequency" style={type.figure}>{String(v.counts.completed_with_work)}</Text><Text style={type.body}>séances terminées avec séries enregistrées</Text>
   {v.weekly_counts.length>4&&weeksExpanded!==v.read_id?<Text style={type.small}>Quatre dernières semaines de la période</Text>:null}
   {v.weekly_counts.length?<View style={{flexDirection:'row',flexWrap:'wrap',gap:16}}>{(weeksExpanded===v.read_id?v.weekly_counts:v.weekly_counts.slice(-4)).map(w=><View testID={`progress-week-${w.week_from}`} key={w.week_from} accessible accessibilityLabel={`Semaine du ${dateLabel(w.week_from,timeZone)}, ${w.completed_with_work} séances${w.partial_current_week?', semaine en cours':''}`}><Text style={type.bodyStrong}>{w.completed_with_work}</Text><Text style={type.small}>{dateLabel(w.week_from,timeZone)}{w.partial_current_week?' · en cours':''}</Text></View>)}</View>:null}
   {v.weekly_counts.length>4?<CalibrationLink testID="progress-expand-weeks" label={weeksExpanded===v.read_id?'Réduire les semaines':'Toutes les semaines de la période'} expanded={weeksExpanded===v.read_id} onPress={()=>setWeeksExpanded(weeksExpanded===v.read_id?null:v.read_id)}/>:null}
  </View>:null}
  <View style={{gap:8}}><Text accessibilityRole="header" style={type.bodyStrong}>Séances récentes</Text>
   {(sessionsExpanded===v?.read_id?v?.entries:v?.entries.slice(0,5))?.map(e=><View key={e.session_id}><CalibrationLink testID={`progress-session-${e.session_id}`} label={`${dateLabel(e.started_at,timeZone)} · ${e.name||'Séance'}`} disabled={r.status!=='confirmed'} onPress={()=>p.onEntry(e)}/><Text style={type.small}>{sessionStatus(e.status)}{e.excluded_from_stats?' · exclue des statistiques':''}</Text></View>)}
   {v&&v.entries.length>5?<CalibrationLink testID="progress-expand-sessions" label={sessionsExpanded===v.read_id?'Réduire la liste':`Voir les ${v.entries.length-5} autres séances reçues`} expanded={sessionsExpanded===v.read_id} onPress={()=>setSessionsExpanded(sessionsExpanded===v.read_id?null:v.read_id)}/>:null}
   {v?.state==='EMPTY'?<Text style={type.small}>Aucune séance enregistrée dans cette période.</Text>:null}
   {v?.next_cursor&&r.status==='confirmed'?<CalibrationLink label="Séances suivantes" onPress={p.onMore}/>:null}
  </View>
  <View style={{gap:8}}><Text accessibilityRole="header" style={type.bodyStrong}>Exercice</Text>
   {s.exercises.status==='idle'?<CalibrationLink label="Choisir un exercice" onPress={p.onExercises} disabled={r.status!=='confirmed'}/>:null}
   {s.exercises.status==='pending'?<Text style={type.small}>Recherche des exercices…</Text>:null}
   {s.exercises.previous?<Text style={type.small}>Résultat précédent · à actualiser</Text>:null}
   {s.exercises.value?.entries.map(e=><CalibrationLink key={e.exercise_ref} label={e.name} disabled={s.exercises.status!=='confirmed'||r.status!=='confirmed'} onPress={()=>p.onExercise(e.exercise_ref)}/>)}
   {s.exercises.value?.state==='SCANNING'?<Text testID="progress-exercises-partial" style={type.small}>Recherche partielle · aucun résultat trouvé à ce stade.</Text>:null}
   {s.exercises.value?.state==='EMPTY'?<Text testID="progress-empty-exercises" style={type.small}>Aucun exercice regroupable dans cette période.</Text>:null}
   {s.exercises.value?.next_cursor&&s.exercises.status==='confirmed'?<CalibrationLink label="Continuer la recherche" onPress={p.onMoreExercises}/>:null}
  </View>
  <View style={{gap:8}}><Text accessibilityRole="header" style={type.bodyStrong}>Poids</Text><WeightTrend state={p.weight} onMore={p.onMoreWeight}/></View>
  <CalibrationLink label="Actualiser" onPress={p.onRefresh} disabled={r.status==='pending'}/>
  <CalibrationLink testID="progress-help" label="Aide" expanded={help} onPress={()=>setHelp(!help)}/>
  {help?<View testID="progress-help-body" style={{gap:8}}><Text style={type.small}>Les comptes couvrent la période entière : séances terminées, non exclues, avec au moins une série de travail complétée et un fait de répétitions ou de charge. Un statut terminé seul ne prouve pas un entraînement effectué.</Text>
   <Text style={type.small}>Le planning daté n’est pas conservé : aucun objectif ni taux d’adhérence n’est déduit. Les pages relisent les faits actuels ; leurs comptes datent de la première lecture.</Text>
   <Text style={type.small}>Le poids vient uniquement de mesures datées, sous accord applicable. Les points ne sont ni une recommandation ni une prédiction. Les prescriptions et les faits réalisés sont distincts.</Text></View>:null}
 </AccountFrame>;
}
