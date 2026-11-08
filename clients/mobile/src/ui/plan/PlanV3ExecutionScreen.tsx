/** Same AUREN instrument roles; typed settings never enter the V1 numeric journal. */
import React,{useEffect,useState} from 'react';
import {ScrollView,Text,View} from 'react-native';
import {useSafeAreaInsets} from 'react-native-safe-area-context';
import type {FirstUseV3Controller} from '../../api/firstUseV3';
import {PlanV3JournalScreen} from './PlanV3JournalScreen';
import {runtimeNoticeV3} from './PlanV3Messages';
import {workPositionV3,workPermissionV3,currentSetFactV3} from '../../domain/planV3Workout';
import {AccountField,AccountLink,AccountMessage} from '../account/AccountFrame';
import {ExerciseRail,IconButton,PrimaryAction,RestRing,ValueDial,Sheet} from '../components';
import {color,space,type} from '../theme';
export function PlanV3ExecutionScreen(p:{controller:FirstUseV3Controller;serverNowMs:number;onSync:()=>Promise<void>;onExit:()=>void}){
 const c=p.controller,state=c.state!,ex=state.execution!,position=workPositionV3(state),insets=useSafeAreaInsets();
 const [history,setHistory]=useState(false),[load,setLoad]=useState(''),[reps,setReps]=useState(''),[menu,setMenu]=useState(false),[edit,setEdit]=useState<'load'|'reps'|null>(null),[message,setMessage]=useState<string|null>(null);
 useEffect(()=>{setLoad('');setReps('');},[position?.set.set_id]);
 const run=(task:()=>Promise<unknown>)=>{void task().catch(()=>setMessage('Enregistrement à vérifier. Le journal reste conservé.'));};
 const permission=workPermissionV3(state,p.serverNowMs),resting=permission.state==='REST';
 const action=(label:string,task:()=>Promise<unknown>,id?:string,prominent=true)=>prominent?<PrimaryAction busy={c.loading} testID={id} label={label} onPress={()=>run(task)}/>:<AccountLink disabled={c.loading} testID={id} label={label} onPress={()=>run(task)}/>;
 const link=(label:string,task:()=>void)=><AccountLink label={label} onPress={task} disabled={c.loading}/>;
 const exercise=position?.exercise,unit=exercise?.prescription.context.load_semantics==='PER_IMPLEMENT'?'kg par élément':exercise?.prescription.context.load_semantics==='MACHINE_DISPLAY_KG'?'kg affichés par l’appareil':'kg au total';
 const name=c.capabilities?.supported_realizations?.find(x=>x.candidate_id===exercise?.canonical_exercise_id)?.display_name??exercise?.canonical_exercise_id;
 if(history)return <PlanV3JournalScreen controller={c} onBack={()=>setHistory(false)} onSync={p.onSync}/>;
 if(state.phase==='COMPLETE'||ex.status==='completed')return <ScrollView style={{flex:1,backgroundColor:color.field}} contentContainerStyle={{padding:space.gutter,paddingTop:insets.top+30,gap:24}}>
  <Text style={type.title}>{ex.status==='completed'?'Séance terminée':'Fin enregistrée sur l’appareil'}</Text>
  <AccountMessage text={`${ex.exercises.flatMap(e=>e.sets).filter(s=>currentSetFactV3(state,s).completed).length} séries réellement faites conservées. Aucun score de réussite n’est calculé pour cette séance.`}/>
  <AccountLink testID="plan-v3-read-journal" label="Lire le journal de cette séance" onPress={()=>setHistory(true)}/>
  {action('Vérifier la synchronisation',async()=>{await p.onSync();await c.refreshExecution();})}
  {link('Voir Aujourd’hui',p.onExit)}
 </ScrollView>;
 return <ScrollView style={{flex:1,backgroundColor:resting?color.fieldRest:color.field}} contentContainerStyle={{flexGrow:1,paddingHorizontal:space.gutter,paddingTop:insets.top+10,paddingBottom:insets.bottom+12,gap:16}} keyboardShouldPersistTaps="handled">
  <ExerciseRail count={ex.exercises.length} index={position?.exerciseIndex??ex.exercises.length-1} resting={resting}/>
  <View style={{flexDirection:'row',justifyContent:'space-between',alignItems:'center'}}>
   <IconButton icon="close" label="Quitter la séance" onPress={()=>setMenu(!menu)}/>
   <Text style={type.eyebrow}>{position?`Exercice ${position.exerciseIndex+1} / ${ex.exercises.length}`:'Bilan'}</Text>
   <IconButton icon="more" label="Journal et options" onPress={()=>setMenu(!menu)}/>
  </View>
  {message||c.notice?<AccountMessage text={runtimeNoticeV3(message??c.notice)!} alert/>:null}
  {menu?<View style={{gap:8}}>
   <AccountLink testID="plan-v3-read-journal" label="Lire le journal de cette séance" onPress={()=>setHistory(true)}/>
   {link('Pause',()=>run(()=>c.pause()))}
   {link('Synchroniser et relire',()=>run(async()=>{await p.onSync();await c.refreshExecution();}))}
   {link('Terminer cette séance',()=>run(async()=>{await c.close('SESSION_FINISH');await p.onSync();await c.refreshExecution();}))}
   {link('Abandonner sans effacer les faits',()=>run(async()=>{await c.close('SESSION_ABANDON');await p.onSync();await c.refreshExecution();}))}
   {link('Fermer les options',()=>setMenu(false))}
  </View>:null}
  <Text accessibilityRole="header" style={type.exercise}>{name??'Séance'}</Text>
  {position?<><Text style={type.body}>Série {position.setIndex+1} sur {exercise!.sets.length} · objectif {exercise!.prescription.dose.min_reps}–{exercise!.prescription.dose.max_reps} reps</Text>
   <View style={{flexDirection:'row',gap:8,marginTop:16}}>{exercise!.sets.map(set=><View key={set.set_id} style={{flex:1,borderRadius:14,borderWidth:set.set_id===position.set.set_id?2:1,borderColor:set.set_id===position.set.set_id?color.signal:color.line,paddingVertical:8,paddingHorizontal:10,minHeight:54,backgroundColor:color.plate}}>
    <Text style={[type.eyebrow,{fontSize:11}]}>S{set.set_index}</Text><Text style={type.bodyStrong}>{currentSetFactV3(state,set).completed?'✓':'—'}</Text>
   </View>)}</View></>:null}
  {resting?<View style={{alignItems:'center',gap:16,paddingVertical:30}}>
   <Text style={type.eyebrow}>Repos entre les séries</Text>
   <RestRing size={260} fraction={Math.min(1,(permission.remaining_ms??0)/(exercise?.prescription.dose.rest_seconds??1)/1000)}>
    <Text style={type.clock}>{`${Math.floor(Math.ceil((permission.remaining_ms??0)/1000)/60)}:${String(Math.ceil((permission.remaining_ms??0)/1000)%60).padStart(2,'0')}`}</Text>
   </RestRing>
   <AccountMessage text="Le repos prescrit reste entier. Le temps d’installation suivant n’a pas de durée établie."/>
  </View>:permission.state==='SETUP'?<View style={{flex:1,justifyContent:'center',gap:16,paddingVertical:30}}>
   <Text style={type.title}>Installe le prochain exercice</Text>
   <AccountMessage text="Suis les instructions propres à cet appareil et à sa réalisation qualifiée. La durée d’installation n’est pas établie."/>
   {action('Installation prête · vérifier la suite',()=>c.confirmSetup())}
  </View>:permission.state==='WAIT_SYNC'?<AccountMessage text="Tes faits sont enregistrés sur l’appareil. Leur envoi doit être confirmé avant une nouvelle consigne."/>:state.phase!=='ACTIVE'||permission.state==='OBSERVATION_ONLY'?<View style={{gap:16,paddingVertical:24}}>
   <AccountMessage text="La prescription capturée reste lisible. Une nouvelle consigne demande une vérification actuelle ; hors ligne, tu peux noter un fait déjà réalisé ou sortir."/>
   {action('Vérifier avant de reprendre',()=>c.beginNext(),'plan-v3-resume')}
  </View>:exercise?<View style={{paddingVertical:24,gap:12}}>
   <Text style={type.eyebrow}>Réglage observé · provisoire</Text>
   <Text style={type.figure}>{exercise.prescription.setting.value} <Text style={type.body}>{unit}</Text></Text>
   <AccountMessage text={`Cible subjective : ${exercise.prescription.dose.rir_target} répétitions en réserve. Ce n’est pas un RIR mesuré.`}/>
  </View>:null}
  <View style={{flexGrow:1}}/>
  {position?<View style={{gap:12}}>
   <View style={{flexDirection:'row',gap:10}}>
    <ValueDial testID="plan-v3-dial-setting" label={exercise?.prescription.context.load_semantics==='PER_IMPLEMENT'?'Par élément':exercise?.prescription.context.load_semantics==='MACHINE_DISPLAY_KG'?'Appareil':'Au total'} value={load||'—'} unit="kg" stepLabel="réglage" stepAvailable={false} onMinus={()=>setMessage('Saisis le réglage effectivement utilisé.')} onPlus={()=>setMessage('Saisis le réglage effectivement utilisé.')} onEdit={()=>setEdit('load')}/>
    <ValueDial testID="plan-v3-dial-reps" label="Reps" value={reps||'—'} stepLabel="une rep" onMinus={()=>setReps(String(Math.max(0,Number(reps||0)-1)))} onPlus={()=>setReps(String(Number(reps||0)+1))} onEdit={()=>setEdit('reps')}/>
   </View>
   <Sheet visible={edit!==null} title={edit==='load'?`Réglage fait · ${unit}`:'Répétitions faites'} onClose={()=>setEdit(null)}>
    <AccountField secureTextEntry={false} textContentType="none" autoComplete="off" label={edit==='load'?`Réglage fait · ${unit}`:'Reps faites'} keyboardType={edit==='load'?'decimal-pad':'number-pad'} value={edit==='load'?load:reps} onChangeText={edit==='load'?setLoad:setReps}/>
    <PrimaryAction label="Garder cette saisie" onPress={()=>setEdit(null)}/>
   </Sheet>
   {load.trim()&&reps.trim()&&Number.isFinite(Number(load.replace(',','.')))&&Number(load.replace(',','.'))>=0&&Number.isSafeInteger(Number(reps))&&Number(reps)>=0?action(state.phase==='ACTIVE'&&permission.state==='WORK'?'Valider la série':'Enregistrer un fait déjà réalisé',async()=>{
    await c.recordFact(position.set.set_id,Number(load.replace(',','.')),Number(reps),new Date(p.serverNowMs||Date.now()).toISOString(),!Number.isFinite(p.serverNowMs));
    await p.onSync();await c.refreshExecution();
   },'plan-v3-record-set',state.phase==='ACTIVE'&&permission.state==='WORK'):null}
  </View>:action('Terminer la séance',async()=>{await c.close('SESSION_FINISH');await p.onSync();await c.refreshExecution();})}
  {(c.localOperations??[]).some(f=>f.state==='failed')?<AccountMessage alert text="Un fait a été refusé. Ouvre Journal et options pour le relire et résoudre le refus."/>:null}
  {Object.values(state.local_facts).some(f=>f.sync!=='acked'&&f.sync!=='resolved')?<AccountMessage text="Enregistré sur l’appareil · synchronisation à vérifier"/>:null}
  {link('Synchroniser',()=>run(async()=>{await p.onSync();await c.refreshExecution();}))}
 </ScrollView>;
}
