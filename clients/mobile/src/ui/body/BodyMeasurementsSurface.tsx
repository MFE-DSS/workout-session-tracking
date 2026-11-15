/** One owned native family: current facts, correction, audit and exact recovery. */
import React,{useCallback,useEffect,useMemo,useRef,useState} from 'react';
import {AppState,BackHandler,Text,View} from 'react-native';
import type {AuthSession} from '../../auth/authSession';
import type {BodyConsent,BodyEntry,BodyErasureEntry,BodyKey,BodyMeasurementsClient,BodySpec} from '../../api/bodyMeasurements';
import {BodyMeasurementsResource,BodyErasureResource} from '../../api/bodyMeasurementsResource';
import type {BodyPendingCommands,PendingBodyCommand} from '../../storage/bodyPendingCommands';
import {BodyCommandRecovery} from '../../sync/bodyCommandRecovery';
import {BodyWorkspaceFrame} from './BodyWorkspaceFrame';
import {BodyCockpit} from './BodyCockpit';
import {CalibrationAction,CalibrationLink} from '../plan/calibrationControls';
import {CalibrationInstrument} from '../plan/calibrationInstrument';
import {NumericReadout} from '../instrument/NumericReadout';
import {type} from '../theme';
import {MeasurementSheet,measurementLabel,type BodyForm} from './MeasurementSheet';

type Props={inTab?:boolean;auth:AuthSession;client:BodyMeasurementsClient;pending?:BodyPendingCommands;current:()=>boolean;newId:()=>string;onClose:()=>void;registerExit?:(handler:(()=>boolean)|null)=>void};
export const BODY_GROUPS:readonly {label:string;keys:readonly BodyKey[]}[]=[{label:'Poids',keys:['weight_kg']},{label:'Tour de taille',keys:['waist_cm']},{label:'Cou',keys:['neck_cm']},{label:'Poitrine',keys:['chest_cm']},{label:'Épaules',keys:['shoulder_width_cm']},{label:'Bras · gauche / droit',keys:['arm_cm_left','arm_cm_right']},{label:'Cuisses · gauche / droit',keys:['thigh_cm_left','thigh_cm_right']},{label:'Hanches',keys:['hip_cm']},{label:'Mollets · gauche / droit',keys:['calf_cm_left','calf_cm_right']},{label:'Envergure',keys:['wingspan_cm']}];
const labelFor=(key:string,specs:BodySpec[])=>measurementLabel(specs.find(s=>s.key===key)?.label??(key==='calf_cm'?'Mollet · ancien champ non latéralisé':key));
export function BodyEntryFacts(p:{entry:BodyEntry;specs:BodySpec[]}){
 const [sources,setSources]=useState(false),e=p.entry,fields=Object.entries(e.fields).filter(([,v])=>v.quality!=='MISSING');
 return <View style={{gap:12}}>
  <Text style={type.small}>{e.date_precision==='DAY_UTC_CONVENTION'?'Jour déclaré':'Date source · précision inconnue'} · {e.measured_at.slice(0,10)}{e.state==='SUPERSEDED'?' · version remplacée':''}</Text>
  {fields.map(([key,v])=><View key={key} accessible accessibilityLabel={`${labelFor(key,p.specs)}, ${v.value??v.raw_value_repr??'inconnu'} ${v.unit}, ${v.provenance.origin==='UNKNOWN'?'origine inconnue':'saisie personnelle'}${v.quality!=='KNOWN'?', valeur non comparable':''}`} style={{gap:4}}><Text style={type.eyebrow}>{labelFor(key,p.specs)}</Text><NumericReadout value={v.value===null?v.raw_value_repr??'—':String(v.value).replace('.',',')} unit={v.unit} role={type.figure}/>{v.quality!=='KNOWN'?<Text style={type.small}>Valeur source · non comparable</Text>:null}<Text style={type.small}>{v.provenance.origin==='UNKNOWN'?'Origine inconnue':'Saisie personnelle'}</Text></View>)}
  {!fields.length?<Text style={type.small}>Aucun fait numérique dans cette version.</Text>:null}
  <CalibrationLink label="Sources et versions" expanded={sources} onPress={()=>setSources(!sources)}/>
  {sources?<View style={{gap:8}}><Text selectable style={type.small}>Relevé {e.root_ref} · version {e.revision} · mesure {e.measurement_id}. Enregistrement : {e.recorded_at}. Convention de calendrier UTC ; aucune heure de mesure déduite.</Text>{fields.map(([key,v])=><Text selectable key={key} style={type.small}>{labelFor(key,p.specs)} : {v.provenance.source_ref} · {v.provenance.acquisition}</Text>)}</View>:null}
 </View>;
}
export function BodyMeasurementsSurface(p:Props){
 const alive=useRef(false),loadSequence=useRef(0),revision=p.auth.revision,current=useCallback(()=>alive.current&&p.current()&&p.auth.revision===revision,[p.current,p.auth,revision]);
 const source=useMemo(()=>new BodyMeasurementsResource(p.auth,p.client),[p.auth,p.client]);
 const versions=useMemo(()=>new BodyMeasurementsResource(p.auth,p.client),[p.auth,p.client]);
 const erasureSource=useMemo(()=>new BodyErasureResource(p.auth,p.client),[p.auth,p.client]);
 const numericAllowed=useRef(false);
 const erasureMode=useRef(false),[manageErasure,setManageErasure]=useState(false),[erasureSelected,setErasureSelected]=useState<BodyErasureEntry|null>(null);
 const recovery=useMemo(()=>p.pending?new BodyCommandRecovery(p.client,p.pending,current):null,[p.client,p.pending,current]);
 const [,paint]=useState(0),[busy,setBusy]=useState(false),[consent,setConsent]=useState<BodyConsent|null>(null),[notice,setNotice]=useState(''),[pending,setPending]=useState<PendingBodyCommand[]>([]),[verified,setVerified]=useState<string|null>(null);
 const [selected,setSelected]=useState<BodyEntry|null>(null),[detailConfirmed,setDetailConfirmed]=useState(false),[showVersions,setShowVersions]=useState(false),[erase,setErase]=useState(false),[pick,setPick]=useState(false),[sheet,setSheet]=useState<BodySpec[]|null>(null),[correcting,setCorrecting]=useState(false),[help,setHelp]=useState(false),[rootIndex,setRootIndex]=useState(false),[acquisitionReference,setAcquisitionReference]=useState<BodyEntry|null>(null),[year,setYear]=useState(new Date().getUTCFullYear());
 const specs=source.state.value?.field_specs??[],active=selected&&detailConfirmed&&selected.state==='CURRENT',locked=busy||!p.pending||!consent?.granted;
 const updatePending=useCallback(async()=>{const rows=await p.pending?.pending()??[];if(current())setPending(rows);},[p.pending,current]);
 const load=useCallback(async()=>{
  const sequence=++loadSequence.current,latest=()=>current()&&sequence===loadSequence.current;
  const now=new Date(),end=year===now.getUTCFullYear()?now.toISOString().slice(0,10):`${year}-12-31`,start=`${year}-01-01`;
  const reading=source.refresh({from:start,through:end});if(current())paint(n=>n+1);
  const c=await p.client.consent();if(!latest())return;
  setConsent(c.state==='confirmed'?c.value:null);numericAllowed.current=c.state==='confirmed'&&c.value.granted;if(!numericAllowed.current){source.invalidate();versions.invalidate();setShowVersions(false);setSelected(null);setDetailConfirmed(false);setSheet(null);setAcquisitionReference(null);setPick(false);setErase(false);setRootIndex(false);}
  await reading;if(!latest())return;
  if(erasureMode.current){setErasureSelected(null);await erasureSource.refresh();if(!latest())return;}
  await updatePending();if(latest())paint(n=>n+1);
 },[p.client,source,erasureSource,year,current,updatePending]);
 const run=async(task:()=>Promise<void>)=>{if(!current()||busy)return;setBusy(true);setNotice('');try{await task();}catch(error){if(current())setNotice(error instanceof Error&&error.message==='body_pending_conflict'?'Une demande doit d’abord être vérifiée.':'Action non confirmée. Vérifie la demande avant de recommencer.');}finally{if(current()){setBusy(false);paint(n=>n+1);}}};
 const back=useCallback(()=>{if(sheet)return true;if(busy)return true;if(erase){setErase(false);return true;}if(erasureSelected){setErasureSelected(null);return true;}if(manageErasure){erasureMode.current=false;setManageErasure(false);erasureSource.invalidate();return true;}if(showVersions){setShowVersions(false);return true;}if(pick){setPick(false);return true;}if(selected){setSelected(null);return true;}p.onClose();return true;},[sheet,busy,erase,erasureSelected,manageErasure,erasureSource,showVersions,pick,selected,p.onClose]);
 useEffect(()=>{alive.current=true;void load();const foreground=AppState.addEventListener('change',s=>{if(s==='active')void load();});return()=>{alive.current=false;source.invalidate();versions.invalidate();erasureSource.invalidate();foreground.remove();};},[load,source,versions,erasureSource]);
 useEffect(()=>{const sub=BackHandler.addEventListener('hardwareBackPress',back);return()=>sub.remove();},[back]);
 useEffect(()=>{p.registerExit?.(back);return()=>p.registerExit?.(null);},[p.registerExit,back]);
 const select=async(root:number)=>{setDetailConfirmed(false);const result=await p.client.head(root);if(!current()||!numericAllowed.current)return;if(result.state==='confirmed'){setSelected(result.value);setDetailConfirmed(true);}else setNotice('Relevé non confirmé. Actualise avant une modification.');};
 const selectErasure=async(root:number)=>{setErasureSelected(null);const result=await p.client.erasureHead(root);if(!current())return;if(result.state==='confirmed')setErasureSelected(result.value);else setNotice('Portée de suppression non confirmée. Actualise avant de confirmer.');};
 const mutate=async(path:string,payload:Record<string,unknown>)=>{
  if(!recovery)return;const key=p.newId(),outcome=await recovery.send({request_id:key,method:'POST',path,payload_json:JSON.stringify({...payload,request_id:key})});if(!current())return;
  // A durable command closes its matching in-memory form even on response loss.
  setSheet(null);setErase(false);setPick(false);setVerified(null);setErasureSelected(null);await updatePending();
  if(outcome.state==='confirmed'){setNotice(outcome.value.state==='ERASED'?'Relevé et versions supprimés du registre numérique.':'Enregistrement confirmé.');setSelected(null);setDetailConfirmed(false);await load();}
  else if(outcome.state==='rejected'){setNotice(outcome.code==='head_conflict'?'Une autre version existe. Actualise le relevé.':'Demande refusée. Les faits précédents restent inchangés.');setDetailConfirmed(false);}
  else setNotice('Résultat à vérifier · aucun succès supposé.');
 };
 const save=(form:BodyForm)=>void run(()=>mutate(correcting&&selected?`/me/body/measurements/${selected.root_ref}/corrections`:'/me/body/measurements',{...form,...(correcting&&selected?{expected_head_token:selected.head_token}:{})}));
 const read=source.state,erasureRead=erasureSource.state;
 return <BodyWorkspaceFrame onBack={back} disabled={busy} inTab={p.inTab}>{manageErasure||showVersions||selected?<Text accessibilityRole="header" style={type.bodyStrong}>{manageErasure?'Suppression des relevés':showVersions?'Versions':'Source et mémoire'}</Text>:null}
  {notice?<Text testID="body-notice" accessibilityLiveRegion="polite" style={type.small}>{notice}</Text>:null}
  {pending.map(command=><View key={command.request_id} style={{gap:6}}><Text style={type.bodyStrong}>Résultat à vérifier</Text><Text selectable style={type.small}>Demande {command.request_id} · {command.state==='PREPARED'?'préparée sur cet appareil':'confirmation serveur manquante'}</Text><CalibrationAction label="Vérifier" disabled={busy||!recovery} onPress={()=>void run(async()=>{const result=await recovery!.verify(command);if(!current())return;setVerified(result.state==='unknown'?command.request_id:null);setNotice(result.state==='confirmed'?'Reçu serveur confirmé.':'Statut non confirmé. Tu peux rejouer exactement cette demande.');await updatePending();if(result.state==='confirmed')await load();})}/>{verified===command.request_id?<CalibrationLink label="Rejouer la même demande" disabled={busy} onPress={()=>void run(async()=>{const result=await recovery!.replay(command);if(!current())return;setVerified(null);setNotice(result.state==='confirmed'?'Reçu serveur confirmé.':'Résultat encore à vérifier.');await updatePending();if(result.state==='confirmed')await load();})}/>:null}</View>)}
  {!manageErasure&&consent&&!consent.granted?<View style={{gap:12}}><Text style={type.bodyStrong}>Accord pour les mesures</Text><Text style={type.body}>Autoriser l’enregistrement et la consultation de tes mesures corporelles saisies manuellement. Tu peux retirer cet accord ici ; ce retrait n’efface pas les faits déjà conservés.</Text><CalibrationAction testID="body-consent-grant" label="Autoriser les mesures" disabled={busy} onPress={()=>void run(async()=>{const result=await p.client.setConsent(true,consent);if(current()){setNotice(result.state==='confirmed'?'Accord confirmé.':'Accord non confirmé. Actualise pour vérifier.');await load();}})}/></View>:null}
  {!consent&&read.status!=='pending'?<Text style={type.small}>Accord et données non confirmés. Aucune autorisation n’est déduite.</Text>:null}
  {read.status==='pending'?<Text style={type.small}>Lecture des mesures…</Text>:null}
  {read.previous?<Text style={type.small}>Lecture précédente · à actualiser</Text>:null}
  {['unknown','changed','unavailable','rejected'].includes(read.status)?<Text style={type.small}>Lecture non confirmée. Les données manquantes restent inconnues.</Text>:null}
  {manageErasure?<View style={{gap:12}}>
   <Text style={type.small}>Gestion sans nouvel accord de collecte. Aucune valeur corporelle n’est affichée.</Text>
   {erasureRead.status!=='confirmed'?<Text style={type.small}>Liste de suppression non confirmée. Actualise pour vérifier.</Text>:null}
   {erasureSelected?<>
    <CalibrationInstrument name={`Relevé ${erasureSelected.root_ref}`} status="Portée relue sur le serveur"><Text style={type.small}>{erasureSelected.date_precision==='DAY_UTC_CONVENTION'?'Jour déclaré':'Date source · précision inconnue'} · {erasureSelected.measured_at.slice(0,10)} · révision {erasureSelected.revision} · {erasureSelected.version_count} versions conservées</Text></CalibrationInstrument>
    {erase?<><Text style={type.bodyStrong}>Supprimer ce relevé et toutes ses versions ?</Text><Text style={type.small}>Les nombres seront effacés du registre. Les reçus techniques restent conservés ; ce geste ne supprime pas les copies, sauvegardes ou données du compte.</Text><CalibrationAction label="Confirmer la suppression" disabled={busy||!p.pending||pending.some(c=>c.path.includes(`/${erasureSelected.root_ref}/`))} onPress={()=>void run(()=>mutate(`/me/body/measurements/${erasureSelected.root_ref}/erase`,{expected_head_token:erasureSelected.head_token,confirm_all_versions:true}))}/><CalibrationLink label="Annuler" onPress={()=>setErase(false)}/></>:<CalibrationLink label="Supprimer le relevé" disabled={busy||!p.pending||pending.some(c=>c.path.includes(`/${erasureSelected.root_ref}/`))} onPress={()=>setErase(true)}/>}
   </>:<>
    {erasureRead.status==='confirmed'&&erasureRead.value?.state==='EMPTY'?<Text style={type.small}>Aucun relevé conservé à supprimer.</Text>:null}
    {erasureRead.value?.entries.map(e=><CalibrationLink key={e.root_ref} testID={`body-erase-entry-${e.root_ref}`} label={`Relevé ${e.root_ref} · ${e.measured_at.slice(0,10)} · ${e.version_count} versions`} disabled={busy||erasureRead.status!=='confirmed'||pending.some(c=>c.path.includes(`/${e.root_ref}/`))} onPress={()=>void run(()=>selectErasure(e.root_ref))}/>)}
    {erasureRead.value?.next_cursor?<CalibrationLink label="Relevés suivants" disabled={busy||erasureRead.status!=='confirmed'} onPress={()=>void run(async()=>{await erasureSource.loadNext();})}/>:null}
   </>}
  </View>:pick&&!sheet?null:showVersions&&consent?.granted?<View style={{gap:16}}>{versions.state.status!=='confirmed'?<Text style={type.small}>Versions non confirmées.</Text>:null}{versions.state.value?.entries.map(e=><CalibrationInstrument key={e.measurement_id} name={e.state==='CURRENT'?'Courante':'Précédente'} status={`Version ${e.revision}`}><BodyEntryFacts entry={e} specs={specs}/></CalibrationInstrument>)}{versions.state.value?.next_cursor?<CalibrationLink label="Versions suivantes" disabled={busy} onPress={()=>void run(async()=>{await versions.loadNext();})}/>:null}</View>:
   selected&&consent?.granted?<View style={{gap:12}}><CalibrationInstrument name={`Relevé ${selected.root_ref}`} status={detailConfirmed?'Lecture confirmée':'Lecture précédente · à actualiser'}><BodyEntryFacts entry={selected} specs={specs}/></CalibrationInstrument>
    {erase?<View style={{gap:8}}><Text style={type.bodyStrong}>Supprimer ce relevé et toutes ses versions ?</Text><Text style={type.small}>Les nombres seront effacés du registre. Les reçus techniques restent conservés ; ce geste ne supprime pas les copies, sauvegardes ou données du compte.</Text><CalibrationAction label="Confirmer la suppression" disabled={busy||!active} onPress={()=>void run(()=>mutate(`/me/body/measurements/${selected.root_ref}/erase`,{expected_head_token:selected.head_token,confirm_all_versions:true}))}/><CalibrationLink label="Annuler" onPress={()=>setErase(false)}/></View>:
     <><CalibrationAction label="Corriger" disabled={locked||!active||pending.some(c=>c.path.includes(`/${selected.root_ref}/`))} onPress={()=>{setCorrecting(true);setPick(true);}}/><CalibrationLink label="Voir les versions" disabled={busy} onPress={()=>void run(async()=>{await versions.refresh({mode:'versions',root:selected.root_ref});if(current()&&numericAllowed.current)setShowVersions(true);else versions.invalidate();})}/><CalibrationLink label="Supprimer le relevé" disabled={busy||!active||!p.pending} onPress={()=>setErase(true)}/></>}
   </View>:
   consent?.granted?<View style={{gap:12}}>
    <BodyCockpit key={`cockpit-${revision}-${year}`} entries={read.value?.entries??[]} specs={specs} previous={read.previous} partial={Boolean(read.value?.next_cursor)} locked={locked||read.status!=='confirmed'||pending.some(c=>c.path==='/me/body/measurements')}
     onAcquire={(key,reference)=>{setAcquisitionReference(reference??null);setCorrecting(false);setPick(true);const group=BODY_GROUPS.find(g=>g.keys.includes(key));setSheet([...specs.filter(s=>s.key===key),...specs.filter(s=>s.key!==key&&group?.keys.includes(s.key))]);}}
     onInspect={root=>void run(()=>select(root))}/>
    <CalibrationLink testID="body-roots-open" label="Tous les relevés et sources" expanded={rootIndex} onPress={()=>setRootIndex(!rootIndex)}/>
    {rootIndex?read.value?.entries.map(e=><CalibrationLink key={e.root_ref} testID={`body-entry-${e.root_ref}`} label={`${e.measured_at.slice(0,10)} · relevé ${e.root_ref}`} disabled={busy||read.status!=='confirmed'} onPress={()=>void run(()=>select(e.root_ref))}/>):null}
    {read.value?.state==='EMPTY'?<Text testID="body-empty" style={type.small}>Aucun relevé confirmé dans cette période.</Text>:null}
    <View style={{flexDirection:'row',flexWrap:'wrap',gap:12,alignItems:'center'}}><Text style={type.small}>{year}</Text><CalibrationLink label="Année précédente" disabled={busy||year<=1900} onPress={()=>setYear(y=>y-1)}/>{year<new Date().getUTCFullYear()?<CalibrationLink label="Année suivante" disabled={busy} onPress={()=>setYear(y=>y+1)}/>:null}</View>
    {read.value?.next_cursor?<CalibrationLink label="Relevés suivants" disabled={busy||read.status!=='confirmed'} onPress={()=>void run(async()=>{await source.loadNext();})}/>:null}
   </View>:null}
  {pick&&!sheet?<View style={{gap:6}}><Text style={type.eyebrow}>{correcting?'Champ à corriger':'Mesure à saisir'}</Text><View style={{flexDirection:'row',flexWrap:'wrap',gap:8}}>{BODY_GROUPS.map(g=><View key={g.label} style={{width:'48%'}}><CalibrationLink label={g.label} disabled={busy||!g.keys.some(k=>specs.some(s=>s.key===k))} onPress={()=>setSheet(specs.filter(s=>g.keys.includes(s.key)))}/></View>)}</View><CalibrationLink label="Annuler" onPress={()=>setPick(false)}/></View>:null}
  <CalibrationLink label="Actualiser" disabled={busy} onPress={()=>void run(async()=>{await load();if(selected)await select(selected.root_ref);})}/>
  {!manageErasure?<CalibrationLink testID="body-manage-erasure" label="Gérer la suppression des relevés" disabled={busy||!p.pending} onPress={()=>void run(async()=>{setSelected(null);setShowVersions(false);setPick(false);setErase(false);erasureMode.current=true;setManageErasure(true);await erasureSource.refresh();})}/>:null}
  <CalibrationLink label="Aide et accord" expanded={help} onPress={()=>setHelp(!help)}/>
  {help?<View style={{gap:8}}><Text style={type.small}>Les valeurs proviennent de tes saisies et des sources historiques. Aucune graisse corporelle, recommandation ou note de force n’est déduite. Un brouillon non envoyé reste en mémoire ; seule une demande confirmée pour envoi est conservée sur cet appareil.</Text>{consent?.granted?<CalibrationLink label="Retirer l’accord des mesures" disabled={busy} onPress={()=>void run(async()=>{const result=await p.client.setConsent(false,consent);if(current()){source.invalidate();versions.invalidate();setSelected(null);setSheet(null);setNotice(result.state==='confirmed'?'Accord retiré. Les faits ne sont pas effacés.':'Retrait non confirmé. Actualise pour vérifier.');await load();}})}/>:null}</View>:null}
  {sheet?<MeasurementSheet specs={sheet} reference={correcting?undefined:acquisitionReference??undefined} initial={correcting?selected??undefined:undefined} busy={busy} onSave={save} onClose={()=>{setSheet(null);setPick(false);}}/>:null}
 </BodyWorkspaceFrame>;
}
