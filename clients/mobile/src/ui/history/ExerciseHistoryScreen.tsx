import React from 'react';
import {Text,View} from 'react-native';
import type {HistoryOccurrence,ExercisePage} from '../../api/trainingHistory';
import type {ReadSlot} from '../../api/trainingHistoryResource';
import {AccountFrame} from '../account/AccountFrame';
import {CalibrationLink} from '../plan/calibrationControls';
import {type} from '../theme';
import {dateLabel,sessionStatus} from './historyView';
export function ExerciseHistoryScreen(p:{name:string;read:ReadSlot<ExercisePage<HistoryOccurrence>>;timeZone:string;onSelect:(entry:HistoryOccurrence)=>void;onBack:()=>void;onMore:()=>void}){
 const r=p.read,v=r.value;
 return <AccountFrame title={p.name} onBack={p.onBack}>
  {r.previous?<Text style={type.small}>Lecture précédente · à actualiser</Text>:null}
  {r.status==='pending'?<Text style={type.small}>Lecture des occurrences…</Text>:null}
  {!v&&r.status!=='pending'?<Text style={type.small}>Historique à actualiser.</Text>:null}
  {v?.entries.map(e=><View key={e.occurrence_ref}><CalibrationLink label={`${dateLabel(e.started_at,p.timeZone)} · ${sessionStatus(e.status)}`} disabled={r.status!=='confirmed'} onPress={()=>p.onSelect(e)}/><Text style={type.small}>Faits, unité et appareil au détail.</Text></View>)}
  {v&&!v.entries.length?<Text style={type.small}>{v.coverage_complete?'Aucune occurrence dans cette période.':'Lecture partielle · des occurrences peuvent rester à retrouver.'}</Text>:null}
  {v?.next_cursor&&r.status==='confirmed'?<CalibrationLink label="Continuer la lecture" onPress={p.onMore}/>:null}
  <Text style={type.small}>Les faits restent séparés par contexte. Aucune charge n’est additionnée entre appareils ou haltères.</Text>
 </AccountFrame>;
}
