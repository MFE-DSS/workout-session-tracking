/** G1 approved first-use composition. All actions pass through the owned controller. */
import React,{useState,useEffect,useRef} from 'react';
import {AccessibilityInfo,BackHandler,Keyboard,Text,View} from 'react-native';
import type {FirstUseV3Controller} from '../../api/firstUseV3';
import type {EvaluationV3,ContextV3} from '../../domain/planV3Types';
import {AccountFrame,AccountField,AccountLink,AccountMessage} from '../account/AccountFrame';
import {PrimaryAction} from '../components';
import {settingDescriptionV3} from './settingV3';
import {runtimeNoticeV3} from './PlanV3Messages';
import {PlanV3ObservedScreen} from './PlanV3ObservedScreen';
import {type} from '../theme';
import {CalibrationInstrument} from './calibrationInstrument';
import {CalibrationEncounterInstrument} from './calibrationEncounterInstrument';
import {CalibrationAction,CalibrationChoices,CalibrationLink} from './calibrationControls';
import {CalibrationHelp} from './calibrationLayout';
import {calibrationStage,calibrationObservationSection,resumableCalibrationDraft,type CalibrationDraft} from './calibrationModel';
type Step='choose'|'entry'|'minimum'|'facts'|'context'|'pilot'|'proposal'|'ack'|'observed';
const requiredLabels:Record<string,string>={objective:'Objectif',population_scope:'Cadre déclaré',sessions_per_week:'Séances par semaine',session_budgets_minutes:'Temps disponible',limitations:'Limitations déclarées'};
const stageTitles:Record<string,string>={preparation:'Ta préparation',setting:'Ton réglage',familiar:'Ta familiarisation',trial:'Ton essai',decision:'Examiner l’essai'};
export function PlanV3FirstUseScreen(p:{controller:FirstUseV3Controller;onExit:()=>void;onPreferences:()=>void}){
 const c=p.controller,s=c.state,draft=s?.source.calibration_draft as CalibrationDraft|undefined,[draftRef,setDraftRef]=useState(()=>draft?.draft_ref??c.newCalibrationDraftRef()),[candidate,setCandidate]=useState<string|null>(draft?.candidate??null),[available,setAvailable]=useState<'AVAILABLE'|'UNAVAILABLE'|'UNKNOWN'>('UNKNOWN'),[concern,setConcern]=useState<'CLEAR'|'REPORTED'|'UNKNOWN'>('UNKNOWN'),[stopReason,setStopReason]=useState<string|null>(draft?.stopReason??null),[step,setCurrentStep]=useState<Step>('entry'),[pilotStage,setPilotStage]=useState<'preparation'|'setting'|'familiar'|'trial'|'observation'|'decision'>('preparation'),[adult,setAdult]=useState(false),[noLimit,setNoLimit]=useState(false),
 [budget1,setBudget1]=useState(''),[budget2,setBudget2]=useState(''),[place,setPlace]=useState(draft?.place??''),[device,setDevice]=useState(draft?.device??''),
 [instruction,setInstruction]=useState(draft?.instruction??''),[setup,setSetup]=useState(draft?.setup??''),[load,setLoad]=useState(draft?.load??''),[observedLoad,setObservedLoad]=useState(draft?.observedLoad??''),[reps,setReps]=useState(draft?.reps??''),
 [expandedSlot,setExpandedSlot]=useState<string|null>(null),[notice,setNotice]=useState<string|null>(null),[trialAt,setTrialAt]=useState(draft?.trialAt??''),[trialDate,setTrialDate]=useState(draft?.trialDate??''),[trialTime,setTrialTime]=useState(draft?.trialTime??''),
 [entryDetails,setEntryDetails]=useState(false),[observationSection,setObservationSection]=useState<CalibrationDraft['observationSection']>(draft?.observationSection),[successful,setSuccessful]=useState<boolean|null|undefined>(draft?.successful==='UNSET'?undefined:draft?.successful),[completed,setCompleted]=useState<boolean|null>(draft?.completed??null),[quality,setQuality]=useState<string|null>(draft?.quality??null),[discomfort,setDiscomfort]=useState<string|null>(draft?.discomfort??null);
 const interaction=useRef(0);
 const setStep=(next:Step)=>{interaction.current+=1;setCurrentStep(next);};
 const captureInteraction=()=>({token:interaction.current,owner:c.state?.owner_id});
 const currentInteraction=(ticket:ReturnType<typeof captureInteraction>)=>c.active!==false&&interaction.current===ticket.token&&c.state?.owner_id===ticket.owner;
 useEffect(()=>()=>{interaction.current+=1;},[c]);
 useEffect(()=>{void c.saveCalibrationDraft({draft_ref:draftRef,encounter_ref:step==='pilot'&&typeof s?.source.encounter_ref==='string'?s.source.encounter_ref:null,stage:pilotStage,candidate,place,device,instruction,setup,load,observedLoad,reps,completed,successful:successful===undefined?'UNSET':successful,quality,discomfort,stopReason,trialAt,trialDate,trialTime,...(observationSection===undefined?{}:{observationSection})}).catch(()=>setNotice('Ton brouillon reste à vérifier sur cet appareil.'));},[observationSection,draftRef,candidate,place,device,instruction,setup,load,observedLoad,reps,completed,successful,quality,discomfort,stopReason,trialAt,trialDate,trialTime,pilotStage,step,s?.source.encounter_ref,c]);
 useEffect(()=>{const confirmed=c.calibrationDraft(typeof s?.source.encounter_ref==='string'?s.source.encounter_ref:'') as CalibrationDraft|null;
  if(step==='pilot'&&pilotStage==='observation'&&confirmed?.draft_ref===draftRef&&confirmed?.committed_event_ref)setPilotStage('decision');
 },[s?.source.calibration_drafts,draftRef,pilotStage,step,c]);
 const run=(task:()=>Promise<unknown>)=>{setNotice(null);void task().catch(()=>setNotice('La réponse reste à vérifier. Tes faits sont conservés.'));};
 const action=(label:string,task:()=>Promise<unknown>,id?:string)=> <PrimaryAction label={label} busy={c.loading} testID={id} onPress={()=>run(task)}/>;
 const secondary=(label:string,fn:()=>void,id?:string)=> <AccountLink key={id??label} label={label} testID={id} disabled={c.loading} onPress={fn}/>;
 const calibrationSurface=['entry','choose','minimum','context','pilot'].includes(step);
 const pendingCalibration=calibrationSurface&&Boolean(s?.source.pending);
 const compactAction=(label:string,task:()=>Promise<unknown>,id?:string,reason?:string)=><CalibrationAction label={label} busy={c.loading} disabled={Boolean(reason)} reason={reason} testID={id} onPress={()=>run(task)}/>;
 const compactSecondary=(label:string,fn:()=>void,id?:string)=><CalibrationLink key={id??label} label={label} testID={id} disabled={c.loading} onPress={fn}/>;
 const localSecondary=calibrationSurface?compactSecondary:secondary;
 const keyboardVisible=useRef(false);
 const onBack=()=>{
  if(calibrationSurface&&keyboardVisible.current){Keyboard.dismiss();return true;}
  if(step==='pilot'&&pilotStage==='observation'&&(observationSection??calibrationObservationSection({observedLoad,reps,completed,successful:successful===undefined?'UNSET':successful} as CalibrationDraft))==='feeling'){setObservationSection('trial');return true;}
  if(step==='context'){setStep('choose');return true;}
  if(step==='minimum'){setStep('choose');return true;}
  if(step==='entry'){interaction.current+=1;return false;}
  setStep('entry');return true;
 };
 useEffect(()=>{const show=Keyboard.addListener('keyboardDidShow',()=>{keyboardVisible.current=true;}),hide=Keyboard.addListener('keyboardDidHide',()=>{keyboardVisible.current=false;});return ()=>{show.remove();hide.remove();};},[]);
 useEffect(()=>{if(!calibrationSurface)return;const sub=BackHandler.addEventListener('hardwareBackPress',onBack);return ()=>sub.remove();},[step,pilotStage,observationSection,observedLoad,reps,completed,successful]);
 useEffect(()=>{if(step==='pilot'&&pilotStage==='observation')AccessibilityInfo.announceForAccessibility(observationSection==='feeling'?'Ton ressenti':'Ton essai');},[step,pilotStage,observationSection]);
 useEffect(()=>{const message=runtimeNoticeV3(notice??c.notice);if(message)AccessibilityInfo.announceForAccessibility(message);},[notice,c.notice]);
 const management=<>{!s?.source.pending&&!c.notice&&!notice?localSecondary('Relire mes informations',()=>run(()=>c.load()),'plan-v3-read-sources'):null}{localSecondary('Mes préférences',p.onPreferences)}{localSecondary('Voir Aujourd’hui',p.onExit)}</>;
 const footer=<>{s?.source.pending&&!pendingCalibration?<>{localSecondary('Relire mes informations',()=>run(()=>c.load()),'plan-v3-read-sources')}{localSecondary('Répéter explicitement la même action',()=>run(async()=>{await c.retryPendingExplicitly();await c.load();}))}</>:null}
  {c.notice||notice?<><AccountMessage text={runtimeNoticeV3(notice??c.notice)!} alert/>{!s?.source.pending?localSecondary('Relire mes informations',()=>run(()=>c.load()),'plan-v3-read-sources'):null}</>:null}
  {calibrationSurface?<>{step!=='entry'&&step!=='pilot'?<CalibrationLink testID="calibration-entry-details" label="Détails" expanded={entryDetails} onPress={()=>setEntryDetails(!entryDetails)}/>:null}{step!=='pilot'&&entryDetails?management:null}</>:s?.source.pending?<>{secondary('Mes préférences',p.onPreferences)}{secondary('Voir Aujourd’hui',p.onExit)}</>:management}
  {calibrationSurface&&step!=='pilot'&&!pendingCalibration&&c.capabilities?.controlled_test_available&&!['submitted','unknown'].includes(s?.intent?.state??'')?<CalibrationHelp controller={c} candidate={step==='entry'?null:candidate} stage="identify" scopeKey={step}/>:null}</>;
 const frame=(title:string,children:React.ReactNode)=><AccountFrame key={`${step}:${pilotStage}:${observationSection??''}`} title={title} onBack={()=>{if(!onBack())p.onExit();}} footer={footer}>{children}</AccountFrame>;
 if(s?.intent&&['submitted','unknown'].includes(s.intent.state))return frame('Démarrage à vérifier',<>
  <AccountMessage text="La création de ta séance n’a pas encore été confirmée."/>
  {action('Vérifier la même demande',()=>c.reconcileStart(),'plan-v3-reconcile')}
  {secondary('Renvoyer cette même demande',()=>run(()=>c.retryStartExplicitly()))}
 </>);
 if(pendingCalibration)return frame('Réponse à vérifier',<>
  <AccountMessage text="La réponse reste à vérifier. Tes faits sont conservés."/>
  {compactAction('Relire mes informations',()=>c.load(),'plan-v3-read-sources')}
  {compactSecondary('Répéter explicitement la même action',()=>run(async()=>{await c.retryPendingExplicitly();await c.load();}))}
 </>);
 if(!c.capabilities?.controlled_test_available)return frame('Ton premier entraînement',<>
  <AccountMessage text={c.loading?'Un instant.':'Ton premier plan n’est pas disponible pour le moment.'}/>
  {action('Vérifier à nouveau',()=>c.load())}
 </>);
 const resumeCalibration=async(ticket=captureInteraction())=>{
  if(!currentInteraction(ticket))return;
  await c.readCalibration();if(!currentInteraction(ticket))return;
  const progress=c.encounter?.progress;
  const choice=progress?.setting_choice,prep=progress?.preparation;
  setCandidate(progress?.context?.canonical_exercise_id??null);
  const saved=resumableCalibrationDraft(c.calibrationDraft(c.encounter?.encounter_ref??''),c.encounter?.encounter_ref??'');
  setPlace(saved?.place??progress?.context?.context_ref??'');setDevice(saved?.device??progress?.context?.equipment_ref??'');
  const observation=saved?.stage==='observation'&&!saved.committed_event_ref;
  setObservationSection(saved?calibrationObservationSection(saved):'trial');
  setDraftRef(saved?.draft_ref??c.newCalibrationDraftRef());
  setLoad(saved&&(observation||saved.stage==='setting')?saved.load:choice?.setting.value===null||choice?.setting.value===undefined?'':String(choice.setting.value));
  setInstruction(saved?.instruction??prep?.instruction_ref??'');setSetup(saved?.setup??prep?.setup_ref??'');
  {setObservedLoad(saved?.observedLoad??'');setReps(saved?.reps??'');setCompleted(saved?.completed??null);setSuccessful(saved?.successful==='UNSET'?undefined:saved?.successful);setQuality(saved?.quality??null);setDiscomfort(saved?.discomfort??null);setStopReason(saved?.stopReason??null);setTrialAt(saved?.trialAt??'');setTrialDate(saved?.trialDate??'');setTrialTime(saved?.trialTime??'');}
  setPilotStage(saved?.committed_event_ref?'decision':observation?'observation':saved?.stage==='setting'?'setting':calibrationStage(c.encounter));setStep('pilot');
 };
 const resumeHistory=async(ref:string)=>{const ticket=captureInteraction();if(await c.selectCalibration(ref)&&currentInteraction(ticket))await resumeCalibration(ticket);};
 const minimum=async()=>{if(!adult||!noLimit)return;const ticket=captureInteraction();if(await c.saveDeclarations({population_scope:{state:'KNOWN',value:'ADULT_NON_CLINICAL'},limitations:{state:'KNOWN',value:[]}})&&currentInteraction(ticket))setStep('context');};
 const selected=c.capabilities?.supported_realizations?.find(x=>x.candidate_id===candidate);
 const encounterName=c.capabilities?.supported_realizations?.find(x=>x.candidate_id===c.encounter?.progress.context?.canonical_exercise_id)?.display_name;
 const currentName=(step==='entry'||step==='pilot'?encounterName:selected?.display_name)??'Mouvement à identifier';
 if(step==='choose')return frame('Choisir un mouvement',<>
  <AccountMessage text="Une rencontre à la fois. Les observations conservées ne sont pas des permissions actuelles."/>
  {c.capabilities.supported_realizations?.filter(x=>x.initial_guidance_supported).map(x=>{
   const histories=(s?.source.declarations as any)?.observation_progress?.filter((e:any)=>e.kind==='CALIBRATION_ENCOUNTER_OPENED'&&e.context.canonical_exercise_id===x.candidate_id)??[];
   return <View key={x.candidate_id} style={{gap:4}}>
    {<CalibrationLink label={x.display_name} selected={candidate===x.candidate_id} disabled={c.loading} onPress={()=>{interaction.current+=1;setCandidate(x.candidate_id);}}/>}
    <Text style={type.small}>{histories.some((e:any)=>e.events?.some((event:any)=>event.kind==='ATTEMPT_OBSERVED'))?'Observations conservées':histories.length?'Rencontre conservée':'À préparer'}</Text>
    {candidate===x.candidate_id?histories.map((e:any)=><React.Fragment key={e.episode_ref}>{compactSecondary('Reprendre · '+(e.context.equipment_ref??'Dispositif inconnu'),()=>run(()=>resumeHistory(e.episode_ref)))}</React.Fragment>):null}
   </View>;
  })}
  {compactAction('Préparer ce mouvement',async()=>{
   setPlace('');setDevice('');setLoad('');setInstruction('');setSetup('');setAvailable('UNKNOWN');setConcern('UNKNOWN');setPilotStage('preparation');setObservedLoad('');setReps('');setCompleted(null);setSuccessful(undefined);setQuality(null);setDiscomfort(null);setStopReason(null);setTrialAt('');setTrialDate('');setTrialTime('');
   const facts=(s?.source.declarations as any)?.blueprint;
   setStep(facts?.population_scope?.value==='ADULT_NON_CLINICAL'&&facts?.limitations?.state==='KNOWN'&&facts.limitations.value?.length===0?'context':'minimum');
  },undefined,selected?undefined:'Choisis un mouvement.')}
 </>);
 if(step==='observed')return <PlanV3ObservedScreen controller={c} onBack={()=>setStep('entry')}/>;
 if(step==='minimum')return frame('Avant de commencer',<>
  <AccountMessage text="Cette première exploration concerne un adulte, dans un cadre non clinique et sans limitation déclarée. Elle ne garantit pas la sécurité médicale."/>
  {compactSecondary(adult?'✓ Adulte · cadre non clinique':'Je déclare être adulte, dans un cadre non clinique',()=>setAdult(!adult))}
  {compactSecondary(noLimit?'✓ Aucune limitation déclarée':'Je ne déclare aucune limitation',()=>setNoLimit(!noLimit))}
  {compactAction('Continuer',minimum,undefined,adult&&noLimit?undefined:'Confirme ton cadre déclaré pour continuer.')}
  <AccountMessage text="Si ce cadre ne te correspond pas, tu peux revenir à Aujourd’hui sans effectuer cet essai."/>
 </>);
 if(step==='context')return frame('Ton contexte',<CalibrationInstrument name={currentName} status="Informations que tu déclares">
  <AccountMessage text="Identifie le dispositif réellement présent. Aucun réglage de départ n’est calculé."/>
  <AccountField editable={!c.loading} secureTextEntry={false} textContentType="none" autoComplete="off" label="Lieu ou contexte" value={place} onChangeText={setPlace}/>
  <AccountField editable={!c.loading} secureTextEntry={false} textContentType="none" autoComplete="off" label={selected?.load_semantics==='PER_IMPLEMENT'?'Paire d’haltères et dispositif précis':'Appareil précis'} value={device} onChangeText={setDevice}/>
  <CalibrationChoices label="Disponibilité du dispositif" value={available} disabled={c.loading} options={[{value:'AVAILABLE',label:'Dispositif disponible'},{value:'UNAVAILABLE',label:'Indisponible'},{value:'UNKNOWN',label:'Disponibilité inconnue'}]} onChange={setAvailable}/>
  <CalibrationChoices label="Préoccupation déclarée" value={concern} disabled={c.loading} options={[{value:'CLEAR',label:'Aucune préoccupation rapportée'},{value:'REPORTED',label:'Je rapporte une préoccupation'},{value:'UNKNOWN',label:'Je ne sais pas conclure'}]} onChange={setConcern}/>
  {compactAction('Confirmer ce contexte',async()=>{
   if(!selected||!place.trim()||!device.trim())return;
   const ticket=captureInteraction();
   const context:ContextV3={canonical_exercise_id:selected.candidate_id,realization_ref:selected.realization_ref,context_ref:place.trim(),equipment_ref:device.trim(),side:'BILATERAL',load_semantics:selected.load_semantics??'UNKNOWN'};
   await c.openCalibration(context,available,concern);if(currentInteraction(ticket)&&c.encounter)setStep('pilot');
  },undefined,place.trim()&&device.trim()&&selected?undefined:'Indique le lieu et le dispositif réellement présents.')}
 </CalibrationInstrument>);
 if(step==='facts')return frame('Ton temps disponible',<>
  <AccountMessage text="Ce premier périmètre propose deux séances par semaine pour l’hypertrophie. Tu peux modifier tes préférences plus tard."/>
  <AccountField editable={!c.loading} secureTextEntry={false} textContentType="none" autoComplete="off" label="Séance 1 · minutes disponibles" keyboardType="number-pad" value={budget1} onChangeText={setBudget1}/>
  <AccountField editable={!c.loading} secureTextEntry={false} textContentType="none" autoComplete="off" label="Séance 2 · minutes disponibles" keyboardType="number-pad" value={budget2} onChangeText={setBudget2}/>
  {Number.isSafeInteger(Number(budget1))&&Number(budget1)>0&&Number.isSafeInteger(Number(budget2))&&Number(budget2)>0?action('Confirmer cet objectif et ces disponibilités',async()=>{
   const saved=await c.saveDeclarations({objective:{state:'KNOWN',value:'HYPERTROPHY'},sessions_per_week:{state:'KNOWN',value:2},session_budgets_minutes:{state:'KNOWN',value:[Number(budget1),Number(budget2)]}});
   if(saved){await c.evaluate();setStep('proposal');}
  }):null}
 </>);
 if(step==='pilot'){
  const form:CalibrationDraft={draft_ref:draftRef,encounter_ref:typeof s?.source.encounter_ref==='string'?s.source.encounter_ref:null,stage:pilotStage,candidate,place,device,instruction,setup,load,observedLoad,reps,completed,successful:successful===undefined?'UNSET':successful,quality,discomfort,stopReason,trialAt,trialDate,trialTime,observationSection};
  return frame(pilotStage==='observation'?(calibrationObservationSection(form)==='trial'?'Ton essai':'Ton ressenti'):stageTitles[pilotStage],
   <CalibrationEncounterInstrument key={form.encounter_ref} controller={c} name={currentName} form={form} onChange={fields=>{
    if(fields.observationSection!==undefined)setObservationSection(fields.observationSection);
    if(fields.draft_ref!==undefined)setDraftRef(fields.draft_ref);if(fields.stage!==undefined)setPilotStage(fields.stage);
    if(fields.load!==undefined)setLoad(fields.load);if(fields.observedLoad!==undefined)setObservedLoad(fields.observedLoad);if(fields.reps!==undefined)setReps(fields.reps);if(fields.instruction!==undefined)setInstruction(fields.instruction);if(fields.setup!==undefined)setSetup(fields.setup);
    if(fields.completed!==undefined)setCompleted(fields.completed);if(fields.successful!==undefined)setSuccessful(fields.successful==='UNSET'?undefined:fields.successful);
    if(fields.quality!==undefined)setQuality(fields.quality);if(fields.discomfort!==undefined)setDiscomfort(fields.discomfort);if(fields.stopReason!==undefined)setStopReason(fields.stopReason);
    if(fields.trialAt!==undefined)setTrialAt(fields.trialAt);if(fields.trialDate!==undefined)setTrialDate(fields.trialDate);if(fields.trialTime!==undefined)setTrialTime(fields.trialTime);
   }} management={management} onPreparation={async()=>{const ticket=captureInteraction();await c.load();if(currentInteraction(ticket))setStep('choose');}} onPause={async()=>{const ticket=captureInteraction();await c.pause();if(currentInteraction(ticket))setStep('entry');}} onNotice={setNotice}/>);
 }
 const evaluation=s?.source.evaluation as EvaluationV3|undefined,r=evaluation?.recommendation;
 if(step==='proposal'||step==='ack'){
  return frame(step==='ack'?'Ton temps, ton choix':'Ton premier plan',<>
   {!r?<AccountMessage text="La proposition reste à vérifier."/>:r.scientific_readiness!=='SCIENTIFICALLY_READY'?<>
    <AccountMessage text="Ton premier plan n’est pas encore disponible dans ce périmètre."/>
    {r.assessment.missing_fields.map(field=><Text key={field} style={type.body}>{requiredLabels[field]??'Information à vérifier'}</Text>)}
    <AccountMessage text="Le plan demande sept réalisations actuellement qualifiées. Chaque rencontre conserve ses propres conditions ; aucune observation manquante n’est inventée."/>
    {secondary('Compléter les informations',()=>setStep('facts'))}
   </>:<>
    <AccountMessage text="La durée totale n’est pas établie. Ton temps disponible n’est pas une estimation de la séance."/>
    {step==='proposal'?r.candidate_plan?.sessions.slice(0,1).map((session,index)=><View key={session.session_id} style={{gap:8}}>
     <Text style={type.bodyStrong}>Séance {index+1} · {session.duration.budget_minutes} min disponibles</Text>
     {session.slots.map(slot=>{if(slot.prescription.mode!=='OBSERVED_SETTING')return <AccountMessage key={slot.slot_id} text="Cette prescription demande un consommateur distinct. Aucun démarrage depuis ce détail."/>;const key=session.session_id+':'+slot.slot_id,prescription=slot.prescription,dose=prescription.dose,context=prescription.context;
      return <View key={slot.slot_id} style={{gap:6}}>
       {secondary(c.capabilities?.supported_realizations?.find(x=>x.candidate_id===slot.selected?.canonical_exercise_id)?.display_name??slot.selected?.canonical_exercise_id??'Exercice',()=>setExpandedSlot(expandedSlot===key?null:key),'plan-v3-slot-'+key)}
       {expandedSlot===key?<><Text style={type.body}>{dose.work_sets} séries · {dose.min_reps}–{dose.max_reps} reps · {dose.rest_seconds} s de repos entre les séries</Text>
        <Text style={type.body}>{settingDescriptionV3(prescription.setting,context)} · réglage observé provisoire</Text>
        <Text style={type.small}>{context.equipment_ref} · {context.context_ref}</Text>
        <Text style={type.small}>Cible subjective : {dose.rir_target} répétitions en réserve, sans mesure du RIR.</Text></>:null}
      </View>;
     })}
    </View>):<AccountMessage text="La séance peut dépasser mon temps disponible. Je peux m’arrêter ; je ne compresse pas les repos pour la terminer."/>}
    {r.start_permission==='REQUIRES_TIME_ACK'?(step==='ack'?action('Je reconnais cette incertitude pour ce plan',()=>c.acknowledgeTime(),'plan-v3-time-ack'):secondary('Lire et reconnaître l’incertitude',()=>setStep('ack'))):null}
    {r.start_permission==='ELIGIBLE'?action(s?.intent?.state==='denied'||s?.intent?.state==='cancelled'?'Faire une nouvelle demande':'Commencer',()=>c.start(),'plan-v3-start'):null}
   </>}
   {secondary('Vérifier la proposition',()=>run(()=>c.evaluate()))}
  </>);
 }
 return frame('Ton calibrage',<>
  <AccountMessage text="Une rencontre à la fois."/>
  {s?.source.encounter_ref?<>
   <Text style={type.bodyStrong}>{currentName}</Text>
   <Text style={type.small}>{(c.encounter?.progress.observed_attempt_count??0)>0||c.encounter?.progress.observation_refs?.length?'Observations conservées':'Rencontre conservée'}</Text>
   {compactAction('Reprendre',resumeCalibration,'plan-v3-resume-calibration')}
   {compactSecondary('Choisir un mouvement',()=>setStep('choose'),'plan-v3-first-calibration')}
  </>:compactAction('Commencer le calibrage',async()=>setStep('choose'),'plan-v3-first-calibration')}
  <CalibrationLink testID="calibration-entry-details" label="Détails" expanded={entryDetails} onPress={()=>setEntryDetails(!entryDetails)}/>
  {entryDetails?<>
   {compactSecondary('Vérifier les réglages qualifiés · voir mon plan',()=>run(async()=>{await c.evaluate();setStep('proposal');}),'plan-v3-open-proposal')}
   {compactSecondary('Ajouter un réglage déjà observé',()=>setStep('observed'))}
   {compactSecondary('Compléter mes disponibilités',()=>setStep('facts'))}
  </>:null}
 </>);
}
