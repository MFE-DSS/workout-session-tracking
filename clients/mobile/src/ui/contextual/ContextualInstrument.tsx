import React,{useEffect,useRef,useState} from 'react';
import {BackHandler,Keyboard,Pressable,KeyboardAvoidingView,ScrollView,Text,TextInput,View,useWindowDimensions} from 'react-native';
import {useSafeAreaInsets} from 'react-native-safe-area-context';
import type {FirstUseV3Controller} from '../../api/firstUseV3';
import {workPermissionV3} from '../../domain/planV3Workout';
import {keyboardAvoidance} from '../../native/platformUi';
import {IconButton} from '../components';
import {AurenMark} from '../brand/AurenMark';
import {NumericReadout} from '../instrument/NumericReadout';
import {color,space,type} from '../theme';
import {ContextCommand,ContextDisclosure,ContextFrame,ContextWindow} from './ContextualPrimitives';
import {useContextRead} from './useContextRead';
import type {ContextReader} from './referenceRead';
import type {ContextTarget} from './referenceModel';
type Props={controller:FirstUseV3Controller;target:ContextTarget;reader:ContextReader;revision:number;current:()=>boolean;serverNowMs:number;onSync:()=>Promise<void>;onExit:()=>void;onJournal:()=>void;onSubmitted:(id:number)=>void;onContinue:()=>void};
const num=(v:number)=>String(v).replace('.',',');
export function ContextualInstrument(p:Props){
 const c=p.controller,t=p.target,state=c.state!,exercise=state.execution!.exercises.find(e=>e.se_id===t.seId)!,insets=useSafeAreaInsets(),dimensions=useWindowDimensions(),large=dimensions.fontScale>=1.25;
 const [draft,setDraft]=useState({load:'',reps:''}),[editing,setEditing]=useState<'load'|'reps'|null>(null),[before,setBefore]=useState(draft),[ime,setIme]=useState(false),[busy,setBusy]=useState(false),[failedSave,setFailedSave]=useState(false),[failedVerify,setFailedVerify]=useState(false);
 const flight=useRef(false),scroll=useRef<React.ElementRef<typeof ScrollView>>(null),anchors=useRef({origin:0,load:0,reps:0}),invalidated=useRef<string|null>(null);
 const [sourceOpen,setSourceOpen]=useState(false);
 const {read,refresh}=useContextRead(p.reader,t,p.revision,p.current),reference=read?.state==='ready'?read.reference:null,serverFact=read?.state==='ready'?read.current:null;
 const rows=c.localOperations.filter(r=>r.owner_id===t.ownerId&&r.session_id===t.sessionId&&r.set_id===t.setId).sort((a,b)=>b.local_revision-a.local_revision),op=rows[0];
 const local=state.local_facts[String(t.setId)],resolved=op?.state==='resolved'||local?.sync==='resolved',saved=resolved?null:op?.fact??local?.fact,ack=op?.state==='acked'||(!op&&local?.sync==='acked'),refused=!resolved&&(op?.state==='failed'||local?.sync==='failed');
 const authoritative=read?.state==='ready'&&(resolved||read.currentRevision>=(op?.expected_server_revision??local?.expected_server_revision??-1)+1),verified=authoritative?serverFact:null,serverRemoved=authoritative&&read.currentState==='not_completed'&&(ack||resolved),serverUnqualified=authoritative&&read.currentState==='unqualified';
 const pending=op?.state==='pending'||op?.state==='inflight'||(!op&&local?.sync==='saved_local');
 const independent=!!verified&&!saved&&!pending&&!refused;
 const effective=(ack||resolved||independent)&&verified?{value:verified.value,reps:verified.reps,performedAt:verified.performedAt,estimated:verified.estimated,revision:verified.revision}:!serverRemoved&&!serverUnqualified&&saved?.setting?.kind==='MASS_KG'&&typeof saved.setting.value==='number'?{value:saved.setting.value,reps:saved.reps,performedAt:saved.performed_at,estimated:saved.performed_at_estimated,revision:null}:null;
 const recorded=!!effective&&(saved?.completed===true||((ack||resolved||independent)&&!!verified)),permission=workPermissionV3(state,p.serverNowMs);
 const n=Number(draft.load.replace(',','.')),r=Number(draft.reps),valid=!!draft.load.trim()&&!!draft.reps.trim()&&Number.isFinite(n)&&n>=0&&Number.isSafeInteger(r)&&r>=0;
 const allowed=permission.state==='WORK'&&state.phase==='ACTIVE',observeOnly=!allowed;
 const status=serverUnqualified?'Fait actuel à examiner':serverRemoved?'Aucune réalisation actuelle relue':resolved?'Version serveur retenue':refused?'Refusé · à examiner':recorded?ack||independent?(verified?'Fait relu · serveur':'Enregistré · reçu serveur'):'Envoi à vérifier':pending?'Envoi à vérifier':failedSave?'Non enregistré · saisie conservée':busy?'Enregistrement…':'À déclarer';
 const invalidation=authoritative&&(serverRemoved||serverUnqualified||resolved)&&read?.state==='ready'?`${t.setId}:${read.currentRevision}:${read.currentState}`:null;
 useEffect(()=>{if(invalidation&&invalidated.current!==invalidation){invalidated.current=invalidation;setDraft({load:'',reps:''});setBefore({load:'',reps:''});setEditing(null);Keyboard.dismiss();}},[invalidation]);
 function cancel(){setDraft(before);setEditing(null);Keyboard.dismiss();}
 useEffect(()=>{const a=Keyboard.addListener('keyboardDidShow',()=>setIme(true)),b=Keyboard.addListener('keyboardDidHide',()=>setIme(false));return()=>{a.remove();b.remove();};},[]);
 useEffect(()=>{const sub=BackHandler.addEventListener('hardwareBackPress',()=>{if(editing){cancel();return true;}return false;});return()=>sub.remove();},[editing,before]);
 async function sync(){if(flight.current)return;flight.current=true;setBusy(true);setFailedVerify(false);try{await p.onSync();await c.refreshExecution();}catch{setFailedVerify(true);}finally{refresh();setBusy(false);flight.current=false;}}
 async function submit(){if(!valid||recorded||pending||refused||serverUnqualified||flight.current||c.loading)return;flight.current=true;const at=c.eventTime();p.onSubmitted(t.setId);setBusy(true);setFailedSave(false);Keyboard.dismiss();setEditing(null);
  try{await c.recordFact(t.setId,n,r,new Date(at.epochMs).toISOString(),at.estimated);await p.onSync();await c.refreshExecution();}catch{setFailedSave(true);}finally{refresh();setBusy(false);flight.current=false;}
 }
 const split=!large&&Math.max(draft.load.length,String(effective?.value??'').length)<=5&&Math.max(draft.reps.length,String(effective?.reps??'').length)<=3;
 const readOnly=recorded||pending||refused||serverUnqualified;
 const value=(field:'load'|'reps')=>recorded&&effective?(field==='load'?num(effective.value):effective.reps===null?'—':num(effective.reps)):readOnly?'—':draft[field]||'—';
 const shortStatus=serverUnqualified?'À examiner':serverRemoved?'Non réalisé · relu':resolved?'Version serveur':refused?'Refusé · à examiner':recorded?ack||independent?(verified?'Relu · serveur':'Reçu confirmé'):'À vérifier':pending?'À vérifier':failedSave?'Saisie conservée':busy?'Enregistrement…':editing?'Saisie en cours':'À déclarer';
 function edit(field:'load'|'reps'){if(readOnly||busy)return;setBefore(draft);setSourceOpen(false);setEditing(field);}
 function focus(field:'load'|'reps'){const a=anchors.current;scroll.current?.scrollTo({y:Math.max(0,a.origin+a[field]-4),animated:false});}
 const referenceDetail=<>{reference?<><Text selectable style={type.small}>Séance {t.sessionId} · exercice {t.seId} · série {reference.setId} · révision {reference.revision}</Text><Text selectable style={type.small}>Heure déclarée : {reference.performedAt}{reference.estimated===true?' · approximative':reference.estimated===undefined?' · précision non qualifiée':''}</Text><Text style={type.small}>Appareil {t.context.equipment_ref} · côté bilatéral. Le contexte est enregistré, pas revérifié physiquement par cet affichage. Aucun réglage n’est conseillé.</Text></>:<Text style={type.small}>{read?.state==='ready'?'Aucune observation précédente qualifiée dans cette occurrence.':'Lecture indisponible · absence d’historique non établie.'}</Text>}{read?.state==='ready'?<Text selectable style={type.small}>Détail serveur : {read.detailServerNow} · index : {read.indexReadId}, {read.indexRowsReadAt}</Text>:null}</>;
 const continueReady=!refused&&(ack||resolved)&&(recorded||serverUnqualified);
 return <View testID="context-instrument" style={{flex:1,backgroundColor:color.field,paddingTop:insets.top}}><KeyboardAvoidingView {...keyboardAvoidance} style={{flex:1}}>
  <View style={{paddingHorizontal:space.gutter,paddingBottom:4,flexDirection:'row',gap:8,alignItems:'center'}}><View style={{minWidth:48,minHeight:48,justifyContent:'center'}}><IconButton icon="close" label="Quitter la séance" onPress={p.onExit}/></View><View style={{flex:1,gap:2}}><Text accessibilityRole="header" style={type.bodyStrong}>Extension de jambes</Text><Text style={type.small}>{exercise.prescription.dose.min_reps}–{exercise.prescription.dose.max_reps} rép. prévues</Text></View><AurenMark size={20} color={color.ink}/></View>
  <View testID="context-reference" style={{marginHorizontal:space.gutter,flexDirection:'row',alignItems:'center',gap:8,paddingVertical:4}}>
   <View style={{flex:1,gap:2}}>{reference?<Text accessibilityLabel={`Série ${reference.index} confirmée · ${num(reference.value)} kg affichés · ${reference.reps} répétitions · même contexte enregistré`} testID="context-reference-value" style={[type.small,{color:color.ink2}]}>S{reference.index} · {num(reference.value)} kg affichés × {reference.reps} rép.</Text>:<Text style={type.small}>{read?'Référence indisponible':'Lecture de la référence…'}</Text>}</View>
   <Pressable accessibilityRole="button" accessibilityLabel="Source de la référence" accessibilityState={{expanded:sourceOpen}} onPress={()=>setSourceOpen(!sourceOpen)} style={{minWidth:48,minHeight:48,justifyContent:'center',alignItems:'center'}}><Text style={[type.bodyStrong,{color:color.ink2}]}>ⓘ</Text></Pressable>
  </View>
  <View testID="context-current-set" style={{flexShrink:1,minHeight:0}} accessibilityLabel={`Série actuelle ${t.index} sur ${exercise.sets.length}`}>
   <View testID="context-current-identity" style={{paddingHorizontal:space.gutter,paddingVertical:8,flexDirection:'row',flexWrap:'wrap',justifyContent:'space-between',gap:4}}><Text style={type.bodyStrong}>S{t.index} / {exercise.sets.length}</Text><Text accessibilityLiveRegion="polite" accessibilityLabel={status} style={[type.small,{color:recorded&&!refused&&ack?color.ink2:color.signal}]}>{shortStatus}</Text></View>
   <ScrollView ref={scroll} keyboardShouldPersistTaps="handled" contentInsetAdjustmentBehavior="never" style={{flexGrow:0,flexShrink:1}} contentContainerStyle={{paddingHorizontal:space.gutter,gap:8,paddingBottom:4}}>
    <ContextFrame>{({width,u,originY})=>{anchors.current.origin=originY;return <>
     <View style={{flexDirection:split?'row':'column',gap:2*u}}>
      {(['load','reps'] as const).map(field=><ContextWindow key={field} width={split?(width-2*u)*(field==='load'?2/3:1/3):width} u={u} testID={field==='load'?'context-load-window':'context-reps-window'} onTop={y=>{anchors.current[field]=y;}}>
       <Text style={type.small}>{field==='load'?'Réglage':'Répétitions'}</Text>
       {!readOnly&&editing===field?<View style={{flexDirection:'row',alignItems:'baseline',gap:4}}><TextInput testID={field==='load'?'context-load':'context-reps'} accessibilityLabel={field==='load'?'Réglage fait en kg affichés':'Répétitions faites'} value={draft[field]} placeholder="—" placeholderTextColor={color.ink3} keyboardType={field==='load'?'decimal-pad':'number-pad'} autoFocus selectTextOnFocus onFocus={()=>focus(field)} onChangeText={v=>setDraft(d=>({...d,[field]:v}))} style={[type.figure,{flexShrink:1,minWidth:48,minHeight:56,padding:0,color:color.signal}]}/><Text style={[type.small,{color:color.ink2,flexShrink:0}]}>{field==='load'?'kg affichés':'rép.'}</Text></View>:<Pressable testID={`context-edit-${field}`} accessibilityRole={readOnly?undefined:'button'} accessibilityState={{disabled:readOnly||busy}} accessibilityLabel={`${field==='load'?'Réglage fait en kg affichés':'Répétitions faites'} · ${value(field)}${readOnly?' · '+shortStatus:' · modifier'}`} disabled={readOnly||busy} onPress={()=>edit(field)} style={{minHeight:56,justifyContent:'center'}}><NumericReadout testID={recorded&&field==='load'?'context-recorded-value':undefined} value={value(field)} unit={field==='load'?'kg affichés':'rép.'} role={type.figure}/></Pressable>}
      </ContextWindow>)}
     </View>
    </>;}}</ContextFrame>
   {sourceOpen?<View style={{gap:8}}>{referenceDetail}</View>:null}
  </ScrollView>
  </View>
  <View style={{paddingHorizontal:space.gutter,paddingBottom:ime?8:4}}>
   <View style={{flexDirection:large?'column':'row',gap:4,borderTopWidth:1,borderColor:color.line,paddingTop:4}}>
    {editing?<ContextCommand testID="context-cancel" label="Annuler la saisie" display="Annuler" onPress={cancel}/>:null}
    <View style={{flex:large?undefined:1}}>{continueReady?<ContextCommand label="Continuer la séance" display="Continuer" primary disabled={busy||c.loading} onPress={p.onContinue}/>:refused?<ContextCommand label="Examiner le refus dans le journal" display="Examiner le refus" primary onPress={p.onJournal}/>:!recorded&&!pending&&!serverUnqualified?<ContextCommand testID="context-submit" label={allowed?'Enregistrer cette série':'Enregistrer un fait déjà réalisé'} display={`Enregistrer S${t.index}`} primary={allowed} disabled={!valid||busy||c.loading||serverUnqualified} onPress={()=>void submit()}/>:<ContextCommand label="Vérifier l’enregistrement" display={`Vérifier S${t.index}`} primary={!refused} onPress={()=>void sync()} disabled={busy||c.loading||refused}/>}</View>
   </View>
  </View>
  {!ime?<ScrollView style={{flexGrow:0,flexShrink:1}} contentContainerStyle={{paddingHorizontal:space.gutter,paddingBottom:Math.max(8,insets.bottom),gap:4}}>
   <ContextDisclosure label={recorded?'Fait et enregistrement':'Contexte et options'}>
    {recorded&&effective?<><Text selectable style={type.small}>Série {t.setId} · commande {op?.op_id??local?.op_id} · révision locale {op?.local_revision??local?.local_revision}</Text><Text selectable style={type.small}>Heure déclarée : {effective.performedAt}{effective.estimated===true?' · approximative':effective.estimated===undefined?' · précision non qualifiée':''}</Text><Text style={type.small}>Le reçu de commande et la relecture du fait sont distincts.</Text>{effective.revision!==null?<Text selectable style={type.small}>Révision serveur relue : {effective.revision}</Text>:null}<ContextCommand label="Vérifier l’enregistrement" onPress={()=>void sync()} disabled={busy||c.loading}/></>:null}
    <Text style={type.small}>{permission.state==='REST'?'Repos prescrit en cours':permission.state==='WAIT_SYNC'?'La suite attend la vérification de l’envoi':permission.state==='SETUP'?'Installation suivante à confirmer':observeOnly?'Toute nouvelle consigne demande une vérification actuelle':'Renseigne uniquement le réglage et les répétitions effectivement réalisés.'}</Text>
    {!recorded&&!pending&&!refused&&!serverUnqualified?<ContextCommand label={permission.state==='SETUP'?'Installation prête · vérifier la suite':'Vérifier la consigne'} disabled={busy||c.loading} onPress={()=>void (permission.state==='SETUP'?c.confirmSetup():c.beginNext()).catch(()=>setFailedVerify(true))}/>:null}
   </ContextDisclosure>
   {permission.state==='REST'?<Text style={[type.bodyStrong,{color:color.system}]}>{Math.ceil((permission.remaining_ms??0)/1000)} s · repos restant</Text>:null}
   {failedVerify?<Text accessibilityLiveRegion="polite" style={type.small}>Vérification indisponible · fait conservé</Text>:null}{c.notice?<Text accessibilityLiveRegion="polite" style={type.small}>{c.notice}</Text>:null}
   <View style={{flexDirection:large?'column':'row',justifyContent:'space-between'}}><ContextCommand label="Journal et options" display="Journal" onPress={p.onJournal}/>{resolved&&!recorded?<ContextCommand label="Continuer la séance" display="Continuer" disabled={busy||c.loading} onPress={p.onContinue}/>:null}</View>
  </ScrollView>:null}
 </KeyboardAvoidingView></View>;
}
