/** MOB07 G1: ordered source structure around one active DA08 instrument. */
import React,{useState} from 'react';
import {InputAccessoryView,Keyboard,KeyboardAvoidingView,Platform,ScrollView,Text,TextInput,View,useWindowDimensions} from 'react-native';
import {useSafeAreaInsets} from 'react-native-safe-area-context';
import {keyboardAvoidance} from '../../native/platformUi';
import {AurenMark} from '../brand/AurenMark';
import {InstrumentSurface} from '../body/InstrumentSurface';
import {EmbeddedAction} from '../body/EmbeddedAction';
import {CalibrationChoices,CalibrationLink} from '../plan/calibrationControls';
import {color,space,type} from '../theme';
import type {BuilderOperation} from '../../domain/programBuilderCommand';
import {movementName} from './programBuilderModel';
import type {ProgramBuilderController} from './ProgramBuilderController';
const status={draft:'Brouillon',validated:'Structure validée · non publié',published:'Publié · lecture seule',archived:'Archivé · lecture seule'};
const operationName:Record<BuilderOperation,string>={CREATE:'Création',RENAME:'Renommage',SAVE_TREE:'Enregistrement',VALIDATE:'Validation de structure',PUBLISH:'Publication',NEW_CYCLE:'Nouveau cycle',ARCHIVE:'Archivage'};
function Input(p:{id:string;label:string;value:string;onChange:(v:string)=>void;editable:boolean;numeric?:boolean;prominent?:boolean}){
 return <View style={{gap:4,flexShrink:1}}><Text style={type.eyebrow}>{p.label}</Text><TextInput testID={p.id} accessibilityLabel={p.label} value={p.value} onChangeText={p.onChange} editable={p.editable} keyboardType={p.numeric?'number-pad':'default'} inputMode={p.numeric?'numeric':'text'} inputAccessoryViewID={Platform.OS==='ios'?'program-builder-done':undefined} placeholder="—" placeholderTextColor={color.ink3} selectionColor={color.signal} autoCorrect={!p.numeric} returnKeyType="done" onSubmitEditing={()=>Keyboard.dismiss()} style={[p.prominent?type.figure:type.bodyStrong,{minHeight:p.prominent?64:48,minWidth:48,paddingVertical:8,borderBottomWidth:1,borderColor:color.line}]}/></View>;
}
export function ProgramBuilderScreen(p:{controller:ProgramBuilderController;onBack:()=>void}){
 const c=p.controller,s=c.state,insets=useSafeAreaInsets(),large=useWindowDimensions().fontScale>=1.25;
 const [rename,setRename]=useState(false),[details,setDetails]=useState(false),[sources,setSources]=useState(false),[search,setSearch]=useState('');
 const session=c.activeSession(),movement=c.activeMovement(),editable=c.editable(),program=s.source;
 const row={flexDirection:large?'column':'row',flexWrap:'wrap',gap:8} as const;
 const command=(operation:BuilderOperation,confirmed=false)=>{Keyboard.dismiss();void c.command(operation,confirmed);};
 return <KeyboardAvoidingView testID="builder-workspace" behavior={keyboardAvoidance.behavior} style={{flex:1,backgroundColor:color.field}}><ScrollView contentInsetAdjustmentBehavior="never" keyboardShouldPersistTaps="handled" keyboardDismissMode="interactive" contentContainerStyle={{paddingHorizontal:space.gutter,paddingTop:insets.top+8,paddingBottom:insets.bottom+12,gap:16}}>
  <View style={[row,{justifyContent:'space-between',alignItems:large?'stretch':'center'}]}><CalibrationLink testID="builder-back" label="Retour" disabled={s.busy} onPress={p.onBack}/><View style={{flexDirection:'row',alignItems:'center',gap:8}}><AurenMark size={20} color={color.ink}/><Text style={type.eyebrow}>AUREN</Text></View></View>
  {s.busy?<Text accessibilityLiveRegion="polite" style={type.small}>Vérification en cours…</Text>:null}
  {s.message?<Text testID="builder-message" accessibilityLiveRegion="polite" selectable style={type.small}>{s.message}</Text>:null}
  {s.pending.map(pending=><View key={pending.command_id} testID={'builder-pending-'+pending.command_id} style={{gap:4,borderBottomWidth:1,borderColor:color.line,paddingBottom:8}}>
   <Text accessibilityRole="header" style={type.bodyStrong}>{operationName[pending.operation]} à vérifier</Text><Text selectable style={type.small}>{pending.program_id===null?'Création de programme':`Programme #${pending.program_id}`} · commande {pending.command_id}</Text>
   <EmbeddedAction testID={'builder-verify-'+pending.command_id} label="Vérifier le résultat" disabled={s.busy} onPress={()=>{void c.verify(pending);}}/>
   {s.replayKeys.includes(pending.command_id)?<><Text style={type.small}>Le résultat reste inconnu. La même commande sera envoyée avec les mêmes valeurs et la même clé.</Text><EmbeddedAction testID={'builder-replay-'+pending.command_id} label="Renvoyer exactement cette commande" disabled={s.busy} onPress={()=>{void c.replay(pending);}}/></>:null}
  </View>)}
  {s.view==='index'?<>
   <Text accessibilityRole="header" style={type.bodyStrong}>Mes brouillons et programmes</Text>
   <EmbeddedAction testID="builder-create" label="Créer un programme" disabled={s.busy||s.pending.some(r=>r.program_id===null)} onPress={()=>{setRename(false);c.create();}}/>
   {!s.programs.length&&!s.busy&&!s.message?<Text style={type.small}>Aucun programme personnel.</Text>:null}
   {s.programs.map(program=><View key={program.id} style={{borderBottomWidth:1,borderColor:color.line,paddingBottom:8,gap:4}}><CalibrationLink testID={'builder-program-'+program.id} label={program.title} disabled={s.busy} onPress={()=>{setRename(false);setDetails(false);void c.select(program.id);}}/><Text style={type.small}>{status[program.status]} · version {program.version}</Text></View>)}
   {s.programCursor?<CalibrationLink label="Suite de mes programmes" disabled={s.busy} onPress={()=>{void c.morePrograms();}}/>:null}
   <CalibrationLink testID="builder-refresh" label="Actualiser" disabled={s.busy} onPress={()=>{void c.refresh();}}/>
  </>:s.view==='create'?<>
   <InstrumentSurface label="Nouveau programme" state="Nom choisi" editing><Input id="builder-title" label="Nom du programme" value={s.draft?.title??''} onChange={v=>c.title(v)} editable={editable}/></InstrumentSurface>
   <EmbeddedAction testID="builder-create-confirm" label="Créer le brouillon →" active disabled={!c.can('CREATE')} onPress={()=>command('CREATE')}/>
  </>:<>
   {program&&s.draft?<>
    <View style={{gap:4}}><Text selectable accessibilityRole="header" style={type.title}>{s.draft.title}</Text>
     <Text style={type.small}>{s.fresh?status[program.status]:'Lecture précédente · à vérifier'}</Text>
     {editable?<CalibrationLink testID="builder-rename-toggle" label="Renommer" expanded={rename} onPress={()=>setRename(!rename)}/>:null}
     {rename&&editable?<><Input id="builder-title" label="Nom du programme" value={s.draft.title} onChange={v=>c.title(v)} editable={editable}/><EmbeddedAction testID="builder-rename" label="Enregistrer le nom" disabled={!c.dirtyTitle()||!c.can('RENAME')} onPress={()=>command('RENAME')}/></>:null}
    </View>
    {s.conflict?<View style={{gap:4}}><Text style={type.bodyStrong}>Conflit de contenu · brouillon conservé</Text><Text style={type.small}>Source relue : {program.title}, version {program.version}. Remplacer le brouillon abandonne les modifications non envoyées.</Text><EmbeddedAction testID="builder-discard" label="Remplacer par la source relue" disabled={s.busy||!s.fresh} onPress={()=>c.discard()}/></View>:null}
    <View testID="builder-session-sequence" style={row}>{s.draft.sessions.map((item,i)=><CalibrationLink key={i} testID={'builder-session-'+i} label={`${String(i+1).padStart(2,'0')} ${item.name||'Séance à nommer'}`} selected={s.activeSession===i} disabled={s.busy} onPress={()=>c.selectSession(i)}/>)}{editable?<EmbeddedAction testID="builder-add-session" label="Ajouter une séance" disabled={s.draft.sessions.length>=7} onPress={()=>{setDetails(true);c.addSession();}}/>:null}</View>
    {session?<InstrumentSurface label={session.name||'Nommer cette séance'} state={`${s.activeSession+1} / ${s.draft.sessions.length}`} editing={editable}>
     <View style={{gap:12}}>
      {editable?<><CalibrationLink testID="builder-session-details" label="Détails de la séance" expanded={details||!session.name} onPress={()=>setDetails(!details)}/>{details||!session.name?<><Input id="builder-session-name" label="Nom de la séance" value={session.name} editable={editable} onChange={v=>c.sessionName(v)}/><CalibrationChoices label="Type de séance" value={session.kind} options={[{value:'strength',label:'Musculation'},{value:'cardio',label:'Cardio'}]} onChange={v=>c.sessionKind(v)}/><View style={row}><EmbeddedAction testID="builder-session-up" label="Avancer la séance" disabled={s.activeSession===0} onPress={()=>c.moveSession(-1)}/><EmbeddedAction testID="builder-session-down" label="Reculer la séance" disabled={s.activeSession===s.draft!.sessions.length-1} onPress={()=>c.moveSession(1)}/><EmbeddedAction testID="builder-session-remove" label="Retirer la séance" onPress={()=>c.removeSession()}/></View></>:null}</>:null}
      <View testID="builder-movement-sequence" style={{gap:4}}>{session.movements.map((item,i)=><CalibrationLink key={i} testID={'builder-movement-'+i} label={`${i+1}. ${movementName(item)}`} selected={s.activeMovement===i} disabled={s.busy} onPress={()=>c.selectMovement(i)}/>)}</View>
      {movement?<View testID="builder-active-movement" style={{gap:12}}>
       {movement.kind==='historical'?<><Text style={type.small}>{movement.source.identity.state==='UNRESOLVED'?'Identité non cartographiée · contenu historique conservé':'Nom résolu dans le catalogue actuel · contenu historique conservé'}</Text>
        {movement.source.rep_targets.map((target,i)=><Text selectable key={i} style={type.bodyStrong}>{target.is_warmup?'Préparation':'Série'} {target.set_index} · {target.min_reps===target.max_reps?target.min_reps:`${target.min_reps}–${target.max_reps}`} rép.{target.technique?` · ${target.technique}`:''}</Text>)}{!movement.source.rep_targets.length?<Text selectable style={type.small}>{movement.source.set_scheme||'Plage historique non renseignée'}</Text>:null}
       </>:<><Input id="builder-sets" label="Nombre de séries" prominent numeric value={movement.sets} onChange={v=>c.movementSets(v)} editable={editable}/>
        {movement.targets.map((target,i)=><View key={i} style={{gap:4}}><Text style={type.eyebrow}>Série {i+1} · répétitions</Text><View style={row}><Input id={'builder-reps-min-'+i} label="Minimum" numeric value={target.min} onChange={v=>c.target(i,'min',v)} editable={editable}/><Input id={'builder-reps-max-'+i} label="Maximum" numeric value={target.max} onChange={v=>c.target(i,'max',v)} editable={editable}/></View></View>)}
       </>}
       {editable?<View style={row}><EmbeddedAction testID="builder-movement-up" label="Avancer le mouvement" disabled={s.activeMovement===0} onPress={()=>c.moveMovement(-1)}/><EmbeddedAction testID="builder-movement-down" label="Reculer le mouvement" disabled={s.activeMovement===session.movements.length-1} onPress={()=>c.moveMovement(1)}/><EmbeddedAction testID="builder-movement-remove" label="Retirer le mouvement" onPress={()=>c.removeMovement()}/></View>:null}
      </View>:<Text style={type.small}>Aucun mouvement dans cette séance.</Text>}
      {editable?<EmbeddedAction testID="builder-picker" label="Choisir un mouvement" disabled={session.movements.length>=10} onPress={()=>{setSearch('');void c.loadExercises();}}/>:null}
      {s.picker?<View style={{gap:4}}><Input id="builder-search" label="Rechercher dans les noms reçus" value={search} onChange={setSearch} editable={!s.busy}/>{s.pickerFresh?s.exercises.filter(e=>e.name.toLocaleLowerCase('fr').includes(search.toLocaleLowerCase('fr'))).map(e=><CalibrationLink key={e.slug} testID={'builder-exercise-'+e.slug} label={e.name} disabled={!editable} onPress={()=>c.chooseExercise(e)}/>):<Text style={type.small}>Catalogue non confirmé · actualiser la lecture.</Text>}{s.exerciseCursor&&s.pickerFresh?<CalibrationLink testID="builder-more-exercises" label="Suite des mouvements" disabled={s.busy} onPress={()=>{void c.loadExercises(true);}}/>:null}<CalibrationLink label="Fermer le choix" disabled={s.busy} onPress={()=>c.closePicker()}/></View>:null}
     </View>
    </InstrumentSurface>:<Text style={type.small}>Aucune séance composée.</Text>}
    {['draft','validated'].includes(program.status)?<>
     {c.dirtyTree()&&!c.can('SAVE_TREE')&&editable?<Text style={type.small}>Renseignez les noms, le nombre de séries et chaque plage de répétitions. Aucun nombre n’est prérempli.</Text>:null}
     <EmbeddedAction testID="builder-save" label="Enregistrer le brouillon →" active disabled={!c.dirtyTree()||!c.can('SAVE_TREE')} onPress={()=>command('SAVE_TREE')}/>
     {program.status==='draft'?<EmbeddedAction testID="builder-validate" label="Valider la structure" disabled={!c.can('VALIDATE')} onPress={()=>command('VALIDATE')}/>:<><Text style={type.small}>La structure est validée. Cela ne certifie ni efficacité ni sécurité scientifique et ne permet pas le départ.</Text><EmbeddedAction testID="builder-publish" label="Publier" disabled={!c.can('PUBLISH')} onPress={()=>command('PUBLISH')}/></>}
    </>:program.status==='published'?<><Text style={type.small}>Pour démarrer, revenez à la bibliothèque et examinez la séance publiée.</Text><EmbeddedAction testID="builder-new-cycle" label="Modifier dans un nouveau cycle" disabled={!c.can('NEW_CYCLE')} onPress={()=>command('NEW_CYCLE')}/></>:null}
    {program.status!=='archived'?<CalibrationLink testID="builder-archive" label="Archiver le programme" disabled={!c.can('ARCHIVE')} onPress={()=>command('ARCHIVE')}/>:null}
    {s.confirm?<View testID="builder-confirmation" style={{gap:8,borderTopWidth:1,borderColor:color.line,paddingTop:12}}><Text accessibilityRole="header" style={type.bodyStrong}>{s.confirm==='PUBLISH'?'Publier cette composition ?':s.confirm==='NEW_CYCLE'?'Ouvrir un nouveau cycle ?':'Archiver ce programme ?'}</Text><Text style={type.small}>{s.confirm==='PUBLISH'?'La publication rend cette composition disponible dans la bibliothèque. Les conditions de départ seront vérifiées là-bas.':s.confirm==='NEW_CYCLE'?'Les publications et séances précédentes sont conservées.':'Le programme sera archivé sans supprimer les séances ni les faits historiques.'}</Text><EmbeddedAction testID={'builder-confirm-'+s.confirm.toLowerCase().replace('_','-')} label={s.confirm==='PUBLISH'?'Confirmer la publication':s.confirm==='NEW_CYCLE'?'Confirmer le nouveau cycle':'Confirmer l’archivage'} active disabled={s.busy} onPress={()=>command(s.confirm!,true)}/><CalibrationLink label="Annuler" disabled={s.busy} onPress={()=>c.cancelConfirmation()}/></View>:null}
    <CalibrationLink testID="builder-source" label="Source et contenu conservé" expanded={sources} onPress={()=>setSources(!sources)}/>
    {sources?<View style={{gap:6}}><Text selectable style={type.small}>Programme #{program.id} · version {program.version} · {program.source_digest}</Text>{session?.focus?<Text selectable style={type.small}>{session.focus}</Text>:null}{session?.notes?<Text selectable style={type.small}>{session.notes}</Text>:null}{session?.duration_target_minutes!==null&&session?.duration_target_minutes!==undefined?<Text style={type.small}>{session.duration_target_minutes} min déclarées</Text>:null}{movement?.kind==='historical'&&movement.source.notes?<Text selectable style={type.small}>{movement.source.notes}</Text>:null}<Text style={type.small}>Les mouvements historiques conservent leurs valeurs d’origine. Les noms résolus aujourd’hui ne prouvent pas le choix initial.</Text></View>:null}
   </>:<Text style={type.small}>Lecture du programme non confirmée.</Text>}
   <CalibrationLink testID="builder-refresh" label="Relire la source" disabled={s.busy} onPress={()=>{void c.refresh();}}/>
  </>}
 </ScrollView>{Platform.OS==='ios'?<InputAccessoryView nativeID="program-builder-done"><View style={{backgroundColor:color.field,alignItems:'flex-end',paddingHorizontal:space.gutter}}><EmbeddedAction label="Terminé" onPress={()=>Keyboard.dismiss()}/></View></InputAccessoryView>:null}</KeyboardAvoidingView>;
}
