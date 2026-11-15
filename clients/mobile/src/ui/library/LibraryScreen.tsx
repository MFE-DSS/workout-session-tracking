/** Approved MOB06 G1, local composition using the existing AUREN primitives. */
import React,{useState} from 'react';
import {FlatList,Pressable,ScrollView,Text,View,useWindowDimensions} from 'react-native';
import {useSafeAreaInsets} from 'react-native-safe-area-context';
import type {LibraryDetail,LibraryEntry,LibraryQuery} from '../../api/library';
import type {LibraryState} from '../../api/libraryResource';
import type {LibraryOpeningState} from '../../sync/libraryOpening';
import type {LibrarySessionIdentity} from '../../storage/libraryPendingOpenings';
import {AurenMark} from '../brand/AurenMark';
import {CalibrationChoices,CalibrationLink} from '../plan/calibrationControls';
import {EmbeddedAction as CalibrationAction} from '../body/EmbeddedAction';
import {InstrumentSurface} from '../body/InstrumentSurface';
import {color,space,type} from '../theme';
export type LibraryScreenProps={state:LibraryState;opening:LibraryOpeningState;query:LibraryQuery;existingSession?:LibrarySessionIdentity|null;
 onFilter:(section:LibraryQuery['section'])=>void;onRefresh:()=>void;onMore:()=>void;onSelect:(ref:string)=>void;onBack:()=>void;
 onAskStart:()=>void;onConfirm:()=>void;onVerify:()=>void;onResume:()=>void;onCancel:(confirmed:boolean)=>void;onResumeExisting:()=>void;onBuilder?:()=>void};
const labels={programs:'Mes programmes',core:'Catalogue',utility:'Compléments',specialization:'Spécialisation'};
const statuses={AVAILABLE:'Catalogue',DRAFT:'Brouillon',VALIDATED:'Validé · non publié',PUBLISHED:'Publié'};
const previousLabel=(at?:number)=>at===undefined?'Lecture précédente · à actualiser':`Lecture précédente · reçue le ${new Date(at).toLocaleString('fr-FR',{year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',timeZoneName:'short'})}`;
const readStatus=(status:string)=>status==='pending'||status==='idle'?'Lecture de la bibliothèque…':status==='changed'?'La source a changé · actualise la lecture.':status==='unavailable'?'Bibliothèque indisponible.':'Lecture non confirmée.';
function loadLabel(entry:LibraryEntry){
 const c=entry.counts;if(c.count_state!=='KNOWN')return 'Composition partiellement connue';
 if(entry.kind==='OWNED_PROGRAM')return `${c.sessions} séance${c.sessions===1?'':'s'} · ${c.exercise_slots} exercice${c.exercise_slots===1?'':'s'}`;
 return c.prescribed_sets===0?'Sans série prescrite':`${c.prescribed_sets} séries prévues · ${c.exercise_slots} exercice${c.exercise_slots===1?'':'s'}`;
}
/** Structure glyphs encode supplied counts only, never readiness or muscle activation. */
function Structure(p:{entry:LibraryEntry}){
 const c=p.entry.counts;if(c.count_state!=='KNOWN'||c.exercise_slots===null||c.prescribed_sets===null)return null;
 const n=Math.min(c.exercise_slots,12);
 return <View testID={'library-structure-'+p.entry.source_ref} accessible accessibilityLabel={`${c.exercise_slots} exercices · ${c.prescribed_sets} séries prévues`} style={{gap:6,paddingHorizontal:12}}>
  <View importantForAccessibility="no-hide-descendants" accessibilityElementsHidden style={{flexDirection:'row',gap:6,flexWrap:'wrap'}}>{Array.from({length:n},(_,i)=><View key={i} style={{width:18,height:3,backgroundColor:color.ink3}}/>)}</View>
  <Text style={type.small}>{loadLabel(p.entry)}</Text>
 </View>;
}
function ProgramSequence(p:{detail:LibraryDetail;disabled:boolean;onSelect:(ref:string)=>void}){
 const large=useWindowDimensions().fontScale>=1.25;
 return <View testID="library-sequence" style={{flexDirection:large?'column':'row',flexWrap:'wrap',gap:12}}>
  {p.detail.composition.map((row,i)=>{
   const sets=row.exercises.flatMap(e=>e.rep_targets.filter(r=>!r.is_warmup));
   return <Pressable key={row.source_ref} testID={'library-session-'+row.source_ref} accessibilityRole="button" accessibilityLabel={`${i+1}. ${row.name}, ${sets.length} séries prévues`} accessibilityState={{disabled:p.disabled}} disabled={p.disabled} onPress={()=>p.onSelect(row.source_ref)} style={{minHeight:48,minWidth:48,flexBasis:large?'100%':'46%',flexGrow:1,paddingVertical:12,paddingHorizontal:12,borderLeftWidth:2,borderColor:color.line,gap:8,opacity:p.disabled?0.4:1}}>
    <Text style={type.eyebrow}>{String(i+1).padStart(2,'0')}</Text><Text selectable style={type.bodyStrong}>{row.name}</Text>
    <View importantForAccessibility="no-hide-descendants" accessibilityElementsHidden style={{flexDirection:'row',gap:4,flexWrap:'wrap'}}>{sets.slice(0,12).map((r,j)=><View key={j} style={{width:14,height:3,backgroundColor:color.ink2}}/>)}</View>
    <Text style={type.small}>{sets.length} séries prévues</Text><Text style={type.small}>Examiner ›</Text>
   </Pressable>;
  })}
 </View>;
}
export function LibraryScreen(p:LibraryScreenProps){
 const insets=useSafeAreaInsets(),[filters,setFilters]=useState(false),[sources,setSources]=useState(false),[cancel,setCancel]=useState(false);
 const s=p.state,index=s.index,v=index.value,d=s.detail.value,opening=p.opening;
 const canStart=s.detail.status==='confirmed'&&!s.detail.previous&&Boolean(d?.selection?.selection_ref)&&!p.existingSession&&['idle','refused'].includes(opening.phase)&&opening.code!=='session_open';
 const controls=<View style={{gap:4}}>
  {['hydrating','submitting'].includes(opening.phase)?<Text accessibilityLiveRegion="polite" style={type.small}>{opening.phase==='hydrating'?'Vérification locale…':'Départ en cours…'}</Text>:null}
  {opening.phase==='unavailable'?<View><Text style={type.small}>Vérification indisponible · aucun nouveau départ.</Text><CalibrationAction testID="library-verify" label="Vérifier la séance ouverte" onPress={p.onVerify}/></View>:null}
  {opening.phase==='unknown'||opening.phase==='owned_found'?<View style={{gap:8}}>
   <Text accessibilityRole="header" style={type.bodyStrong}>{opening.pending||opening.phase==='unknown'?'Départ à vérifier':'Séance déjà ouverte'}</Text>{opening.pending||opening.phase==='unknown'?<Text selectable style={type.small}>Création initiale inconnue</Text>:null}
   {opening.phase==='owned_found'?<CalibrationAction testID="library-resume-found" label="Reprendre cette séance" onPress={p.onResume}/>:<CalibrationAction testID="library-verify" label="Vérifier" onPress={p.onVerify}/>}
   {opening.owned?<Text style={type.small}>Séance possédée #{opening.owned.session_id} · {opening.owned.session_profile==='PLAN_V3'?'PLAN':'journal'}</Text>:null}
   {opening.pending||opening.phase==='unknown'?<CalibrationLink testID="library-cancel-options" label="Options de l’intention" expanded={cancel} onPress={()=>setCancel(!cancel)}/>:null}
   {cancel&&(opening.pending||opening.phase==='unknown')?<View><Text selectable style={type.small}>Cela n’annule aucune séance sur le serveur.</Text><CalibrationLink testID="library-cancel-confirm" label="Annuler l’intention sur cet appareil" onPress={()=>p.onCancel(true)}/></View>:null}
  </View>:p.existingSession?<View style={{gap:4}}><Text style={type.small}>Séance #{p.existingSession.session_id} déjà ouverte</Text><CalibrationAction testID="library-resume-existing" label="Reprendre" onPress={p.onResumeExisting}/></View>:null}
  {opening.phase==='refused'&&opening.code==='session_open'?<CalibrationAction testID="library-verify" label="Vérifier la séance ouverte" onPress={p.onVerify}/>:null}
  {opening.phase==='refused'?<Text selectable accessibilityLiveRegion="polite" style={type.small}>Départ refusé · {opening.code==='session_open'?'une séance est déjà ouverte':opening.code==='stale_selection'?'la sélection a changé':'conditions de départ non réunies'}</Text>:null}
  {opening.phase==='created'||opening.phase==='resumed'?<Text accessibilityLiveRegion="polite" style={type.small}>Séance ouverte dans le journal possédé</Text>:null}
 </View>;
 const header=<View style={{gap:12}}>
  <View style={{flexDirection:'row',justifyContent:'space-between',alignItems:'center',gap:8,flexWrap:'wrap'}}>
   {s.view!=='INDEX'?<CalibrationLink testID="library-back" label="Retour" onPress={p.onBack}/>:<Text accessibilityRole="header" style={type.bodyStrong}>Programmes</Text>}
   <View style={{flexDirection:'row',alignItems:'center',gap:8}}><AurenMark size={20} color={color.ink}/><Text style={type.eyebrow}>AUREN</Text></View>
   {s.view==='INDEX'?<CalibrationLink testID="library-filter" label="Filtrer" expanded={filters} onPress={()=>setFilters(!filters)}/>:null}
  </View>
  {controls}
 </View>;
 const padding={paddingHorizontal:space.gutter,paddingTop:insets.top+8,paddingBottom:insets.bottom+12,gap:16};
 if(s.view==='INDEX')return <FlatList<LibraryEntry> style={{flex:1,backgroundColor:color.field}} contentInsetAdjustmentBehavior="never" contentContainerStyle={padding} keyboardShouldPersistTaps="handled"
  data={v?.entries??[]} keyExtractor={e=>e.source_ref} initialNumToRender={8}
  ListHeaderComponent={<View style={{gap:8}}>{header}
   {p.onBuilder?<CalibrationLink testID="library-builder" label="Mes brouillons · Créer un programme" onPress={p.onBuilder}/>:null}
   {filters?<CalibrationChoices label="Sources" value={p.query.section} options={[{value:'all',label:'Tout'},{value:'programs',label:'Mes programmes'},{value:'core',label:'Catalogue'},{value:'utility',label:'Compléments'},{value:'specialization',label:'Spécialisation'}]} onChange={p.onFilter}/>:null}
   {index.previous?<Text testID="library-previous" style={type.small}>{previousLabel(index.receivedAtMs)}</Text>:null}
   {index.status!=='confirmed'?<Text accessibilityLiveRegion="polite" style={type.small}>{readStatus(index.status)}</Text>:null}
   {p.query.section==='all'&&index.status==='confirmed'&&!v?.entries.some(e=>e.kind==='OWNED_PROGRAM')?<Text style={type.small}>Aucun programme personnel.</Text>:null}
  </View>}
  renderItem={({item,index:i})=><View style={{gap:2,paddingBottom:8,borderBottomWidth:1,borderBottomColor:color.line}}>
   {i===0||v?.entries[i-1]?.section!==item.section?<Text accessibilityRole="header" style={[type.eyebrow,{paddingTop:12}]}>{labels[item.section]}</Text>:null}
   <CalibrationLink testID={'library-entry-'+item.source_ref} label={item.name} disabled={index.status!=='confirmed'||index.previous} onPress={()=>p.onSelect(item.source_ref)}/>
   {item.kind==='CATALOG_SESSION'&&item.counts.count_state==='KNOWN'?<Structure entry={item}/>:<Text selectable style={type.small}>{loadLabel(item)}{item.kind==='OWNED_PROGRAM'?` · ${statuses[item.source_status]}`:''}</Text>}
  </View>}
  ListEmptyComponent={index.status==='confirmed'?<Text style={type.body}>{p.query.section==='programs'?'Aucun programme personnel.':'Aucune séance dans cette sélection.'}</Text>:undefined}
  ListFooterComponent={<View style={{gap:4}}>{v?.next_cursor&&index.status==='confirmed'?<CalibrationLink label="Suite de la bibliothèque" onPress={p.onMore}/>:null}<CalibrationLink testID="library-refresh" label="Actualiser" disabled={index.status==='pending'} onPress={p.onRefresh}/></View>}/>;
 return <ScrollView style={{flex:1,backgroundColor:color.field}} contentInsetAdjustmentBehavior="never" keyboardShouldPersistTaps="handled" contentContainerStyle={padding}>
  {header}
  {s.detail.previous?<Text style={type.small}>{previousLabel(s.detail.receivedAtMs)}</Text>:null}
  {s.detail.status!=='confirmed'?<Text accessibilityLiveRegion="polite" style={type.small}>{readStatus(s.detail.status)}</Text>:null}
  {d?<>
   <Text selectable accessibilityRole="header" style={type.bodyStrong}>{d.source.name}</Text>
   <Text style={type.small}>{statuses[d.source.status]}</Text>
   <InstrumentSurface label={d.source.kind==='OWNED_PROGRAM'?'Séances prévues':'Prescription de la séance'} state={d.source.kind==='OWNED_PROGRAM'?'Ordre du programme':'Faits planifiés'}>
    {d.source.kind==='OWNED_PROGRAM'?<ProgramSequence detail={d} disabled={s.detail.status!=='confirmed'||s.detail.previous} onSelect={p.onSelect}/>:<>
     <Text testID="library-context" style={type.small}>Matériel non confirmé</Text>
     {d.composition[0].exercises.map(e=><View key={e.id} style={{gap:8,paddingVertical:12,borderBottomWidth:1,borderColor:color.line}}>
      <Text selectable style={type.bodyStrong}>{e.name}</Text>
      <View style={{gap:4}}>{e.rep_targets.map(r=><View key={`${r.set_index}/${r.is_warmup}`} style={{flexDirection:'row',alignItems:'baseline',gap:12,flexWrap:'wrap'}}>
       <Text style={type.eyebrow}>{r.is_warmup?'Préparation':'Série'} {r.set_index}</Text><Text selectable style={type.bodyStrong}>{r.min_reps===r.max_reps?r.min_reps:`${r.min_reps}–${r.max_reps}`} rép. prévues</Text>
      </View>)}</View>
     </View>)}
    </>}
   </InstrumentSurface>
   <CalibrationLink testID="library-sources" label="Sources et limites" expanded={sources} onPress={()=>setSources(!sources)}/>
   {sources?<View style={{gap:6}}>{d.composition.filter(row=>row.notes).map(row=><Text selectable key={row.source_ref} style={type.small}>{row.name} · {row.notes}</Text>)}{d.composition.flatMap(row=>row.exercises).flatMap(e=>e.rep_targets.filter(r=>r.technique).map(r=><Text selectable key={`${e.id}/${r.set_index}/${r.is_warmup}`} style={type.small}>{e.name} · série {r.set_index} · méthode déclarée : {r.technique}</Text>))}<Text selectable style={type.small}>Composition prévue · {d.source.kind==='CATALOG_SESSION'?'catalogue':`programme personnel, version ${d.source.version}`} · source #{d.source.id}</Text><Text selectable style={type.small}>Ces prescriptions ne sont pas des séries effectuées. Aucune charge ni masse externe totale n’est déduite du catalogue.</Text>{d.composition.flatMap(row=>row.exercises).filter(e=>e.notes).map(e=><Text selectable key={e.id} style={type.small}>{e.name} · {e.notes}</Text>)}</View>:null}
   {d.selection?.native_support.state!=='SUPPORTED'&&d.selection!==null?<Text style={type.small}>Exécution native indisponible pour cette séance.</Text>:null}
   {d.selection&&!d.selection.domain_launchable?<Text style={type.small}>Cette séance n’est pas publiée pour le départ.</Text>:null}
   {s.view==='CONFIRM'?<View style={{gap:8}}><Text accessibilityRole="header" style={type.bodyStrong}>Confirmer le départ</Text><Text style={type.small}>Les conditions actuelles seront vérifiées avant création.</Text><CalibrationAction testID="library-confirm-start" label="Confirmer le départ" disabled={!canStart} onPress={p.onConfirm}/><CalibrationLink label="Annuler" onPress={p.onBack}/></View>:d.selection?.selection_ref?<CalibrationAction testID="library-ask-start" label="Démarrer la séance" disabled={!canStart} onPress={p.onAskStart}/>:null}
  </>:null}
 </ScrollView>;
}
