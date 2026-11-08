/** Owned factual history. A refusal remains evidence; choosing server state is explicit. */
import React,{useState} from 'react';
import {Text,View} from 'react-native';
import type {FirstUseV3Controller} from '../../api/firstUseV3';
import {currentSetFactV3} from '../../domain/planV3Workout';
import {AccountFrame,AccountField,AccountLink,AccountMessage} from '../account/AccountFrame';
import {PrimaryAction} from '../components';
import {type} from '../theme';
import {settingDescriptionV3} from './settingV3';
import {runtimeNoticeV3} from './PlanV3Messages';
const states:Record<string,string>={server:'Confirmé par le serveur',acked:'Acquitté',saved_local:'Conservé sur cet appareil · envoi à vérifier',pending:'En attente',inflight:'Résultat inconnu',failed:'Refusé · résolution nécessaire',resolved:'Refus conservé · version serveur retenue'};
export function PlanV3JournalScreen(p:{controller:FirstUseV3Controller;onBack:()=>void;onSync:()=>Promise<void>}){
 const c=p.controller,[editing,setEditing]=useState<number|null>(null),[load,setLoad]=useState(''),[reps,setReps]=useState(''),[completed,setCompleted]=useState(true),[notice,setNotice]=useState<string|null>(null);
 const state=c.state!,ex=state.execution!;
 const run=(task:()=>Promise<unknown>)=>{setNotice(null);void task().catch(()=>setNotice('La réponse reste à vérifier. Les faits locaux sont conservés.'));};
 return <AccountFrame title="Journal de cette séance" onBack={p.onBack} footer={<>
  {notice||c.notice?<AccountMessage alert text={runtimeNoticeV3(notice??c.notice)!}/>:null}
  <AccountLink label="Synchroniser et relire" disabled={c.loading} onPress={()=>run(async()=>{await p.onSync();await c.refreshExecution();})}/>
 </>}>
  <AccountMessage text="Les faits réalisés sont distincts du réglage prescrit. Les anciennes opérations et leurs refus restent conservés ; une correction crée une nouvelle version."/>
  {ex.exercises.map(exercise=><View key={exercise.se_id} style={{gap:12}}>
   <Text style={type.bodyStrong}>{c.capabilities?.supported_realizations?.find(x=>x.candidate_id===exercise.canonical_exercise_id)?.display_name??exercise.canonical_exercise_id}</Text>
   {exercise.sets.map(set=>{
    const actual=currentSetFactV3(state,set),fact=actual.observation;
    const operations=(c.localOperations??[]).filter(row=>row.set_id===set.set_id),refused=operations.some(row=>row.state==='failed');
    return <View key={set.set_id} style={{gap:6,paddingVertical:8}}>
     <Text style={type.bodyStrong}>Série {set.set_index} · {actual.completed?'Réalisation confirmée':'Réalisation non confirmée'}</Text>
     {fact?<><Text selectable style={type.body}>{settingDescriptionV3(fact.setting,fact.context)} · {fact.reps===null?'Répétitions inconnues':fact.reps+' reps faites'}</Text>
      <Text selectable style={type.small}>{fact.context.equipment_ref} · {fact.context.context_ref}</Text>
      <Text style={type.small}>{fact.performed_at_estimated?'Date estimée · ':actual.completed_at&&Date.parse(actual.completed_at)!==Date.parse(fact.performed_at)?'Date ajustée par le serveur · ':''}{actual.completed_at??fact.performed_at} · {states[actual.sync]} · version serveur {set.revision}</Text></>:<AccountMessage text="Aucun fait actuel confirmé pour cette série."/>}
     {operations.filter(row=>['failed','resolved'].includes(row.state)).map(row=><View key={row.op_id} style={{gap:4}}>
      <Text style={type.small}>{states[row.state]} · opération locale {row.local_revision}</Text>
      <Text selectable style={type.small}>{settingDescriptionV3(row.fact.setting,row.fact.context)} · {row.fact.reps===null?'Répétitions inconnues':row.fact.reps+' reps rapportées'}</Text>
     </View>)}
     {refused?<><AccountMessage alert text="Une écriture a été refusée. Relis les faits du serveur avant de choisir. Son ancien contenu ne sera ni renvoyé automatiquement ni marqué acquitté."/>
      <AccountLink testID={'plan-v3-resolve-'+set.set_id} disabled={c.loading} label="Conserver la version serveur et résoudre ce refus" onPress={()=>run(async()=>{await c.resolveRefusal(set.set_id);await p.onSync();await c.refreshExecution();})}/>
     </>:<AccountLink testID={'plan-v3-correct-'+set.set_id} disabled={c.loading||Object.values(state.local_facts).some(f=>f.sync==='saved_local'||f.sync==='failed')} label="Corriger ce fait" onPress={()=>run(async()=>{await c.refreshExecution();if(c.active){setLoad('');setReps('');setCompleted(true);setEditing(set.set_id);}})}/>}
     {editing===set.set_id?<View style={{gap:8}}>
      <AccountMessage text="Vérifie la version affichée puis saisis seulement ce que tu souhaites corriger. Cette action ne donne aucune consigne de travail."/>
      <AccountField label={exercise.prescription.context.load_semantics==='PER_IMPLEMENT'?'Réglage fait · kg par élément':exercise.prescription.context.load_semantics==='MACHINE_DISPLAY_KG'?'Réglage fait · kg affichés par l’appareil':'Réglage fait · kg au total'} value={load} onChangeText={setLoad} keyboardType="decimal-pad" autoComplete="off" secureTextEntry={false}/>
      <AccountField label="Répétitions faites" value={reps} onChangeText={setReps} keyboardType="number-pad" autoComplete="off" secureTextEntry={false}/>
      <AccountLink label={completed?'✓ Série réellement terminée':'Confirmer la réalisation'} onPress={()=>setCompleted(true)}/>
      <AccountLink label={!completed?'✓ Réalisation non confirmée':'Retirer la confirmation de réalisation'} onPress={()=>setCompleted(false)}/>
      {load.trim()&&Number.isFinite(Number(load.replace(',','.')))&&Number(load.replace(',','.'))>=0&&(!completed&&!reps.trim()||reps.trim()&&Number.isSafeInteger(Number(reps))&&Number(reps)>=0)?
       <PrimaryAction label="Confirmer cette correction" busy={c.loading} onPress={()=>run(async()=>{await c.recordFact(set.set_id,Number(load.replace(',','.')),reps.trim()?Number(reps):null,set.completed_at??new Date().toISOString(),!set.completed_at,completed);await p.onSync();await c.refreshExecution();setEditing(null);})}/>:null}
      <AccountLink label="Annuler cette saisie" onPress={()=>setEditing(null)}/>
     </View>:null}
    </View>;
   })}
  </View>)}
 </AccountFrame>;
}
