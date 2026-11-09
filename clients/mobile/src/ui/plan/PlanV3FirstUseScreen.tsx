/** G1 approved first-use composition. All actions pass through the owned controller. */
import React,{useState,useEffect} from 'react';
import {Text,View} from 'react-native';
import type {FirstUseV3Controller} from '../../api/firstUseV3';
import type {EvaluationV3,ContextV3} from '../../domain/planV3Types';
import {AccountFrame,AccountField,AccountLink,AccountMessage} from '../account/AccountFrame';
import {PrimaryAction} from '../components';
import {settingDescriptionV3} from './settingV3';
import {runtimeNoticeV3} from './PlanV3Messages';
import {PlanV3ObservedScreen} from './PlanV3ObservedScreen';
import {color,type} from '../theme';
import {CalibrationInstrument} from './calibrationInstrument';
import {CalibrationEncounterInstrument} from './calibrationEncounterInstrument';
import {calibrationStage,resumableCalibrationDraft,type CalibrationDraft} from './calibrationModel';
type Step='choose'|'entry'|'minimum'|'facts'|'context'|'pilot'|'proposal'|'ack'|'observed';
const requiredLabels:Record<string,string>={objective:'Objectif',population_scope:'Cadre déclaré',sessions_per_week:'Séances par semaine',session_budgets_minutes:'Temps disponible',limitations:'Limitations déclarées'};
const phases:Record<string,string>={PREPARE:'Préparer l’appareil',FAMILIARIZE:'Se familiariser',TRIAL:'Faire un essai',OBSERVE:'Noter ce qui s’est passé',DECIDE:'Examiner l’essai',STOP:'Faire une pause'};
export function PlanV3FirstUseScreen(p:{controller:FirstUseV3Controller;onExit:()=>void;onPreferences:()=>void}){
 const c=p.controller,s=c.state,draft=s?.source.calibration_draft as CalibrationDraft|undefined,[draftRef,setDraftRef]=useState(()=>draft?.draft_ref??c.newCalibrationDraftRef()),[candidate,setCandidate]=useState<string|null>(draft?.candidate??null),[available,setAvailable]=useState<'AVAILABLE'|'UNAVAILABLE'|'UNKNOWN'>('UNKNOWN'),[concern,setConcern]=useState<'CLEAR'|'REPORTED'|'UNKNOWN'>('UNKNOWN'),[stopReason,setStopReason]=useState<string|null>(draft?.stopReason??null),[step,setStep]=useState<Step>('entry'),[pilotStage,setPilotStage]=useState<'preparation'|'setting'|'familiar'|'trial'|'observation'|'decision'>('preparation'),[adult,setAdult]=useState(false),[noLimit,setNoLimit]=useState(false),
 [budget1,setBudget1]=useState(''),[budget2,setBudget2]=useState(''),[place,setPlace]=useState(draft?.place??''),[device,setDevice]=useState(draft?.device??''),
 [instruction,setInstruction]=useState(draft?.instruction??''),[setup,setSetup]=useState(draft?.setup??''),[load,setLoad]=useState(draft?.load??''),[observedLoad,setObservedLoad]=useState(draft?.observedLoad??''),[reps,setReps]=useState(draft?.reps??''),
 [expandedSlot,setExpandedSlot]=useState<string|null>(null),[notice,setNotice]=useState<string|null>(null),[trialAt,setTrialAt]=useState(draft?.trialAt??''),[trialDate,setTrialDate]=useState(draft?.trialDate??''),[trialTime,setTrialTime]=useState(draft?.trialTime??''),
 [successful,setSuccessful]=useState<boolean|null|undefined>(draft?.successful==='UNSET'?undefined:draft?.successful),[completed,setCompleted]=useState<boolean|null>(draft?.completed??null),[quality,setQuality]=useState<string|null>(draft?.quality??null),[discomfort,setDiscomfort]=useState<string|null>(draft?.discomfort??null);
 useEffect(()=>{void c.saveCalibrationDraft({draft_ref:draftRef,encounter_ref:step==='pilot'&&typeof s?.source.encounter_ref==='string'?s.source.encounter_ref:null,stage:pilotStage,candidate,place,device,instruction,setup,load,observedLoad,reps,completed,successful:successful===undefined?'UNSET':successful,quality,discomfort,stopReason,trialAt,trialDate,trialTime}).catch(()=>setNotice('Ton brouillon reste à vérifier sur cet appareil.'));},[draftRef,candidate,place,device,instruction,setup,load,observedLoad,reps,completed,successful,quality,discomfort,stopReason,trialAt,trialDate,trialTime,pilotStage,step,s?.source.encounter_ref,c]);
 useEffect(()=>{const confirmed=c.calibrationDraft(typeof s?.source.encounter_ref==='string'?s.source.encounter_ref:'') as CalibrationDraft|null;
  if(step==='pilot'&&pilotStage==='observation'&&confirmed?.draft_ref===draftRef&&confirmed?.committed_event_ref)setPilotStage('decision');
 },[s?.source.calibration_drafts,draftRef,pilotStage,step,c]);
 const run=(task:()=>Promise<unknown>)=>{setNotice(null);void task().catch(()=>setNotice('La réponse reste à vérifier. Tes faits sont conservés.'));};
 const action=(label:string,task:()=>Promise<unknown>,id?:string)=> <PrimaryAction label={label} busy={c.loading} testID={id} onPress={()=>run(task)}/>;
 const secondary=(label:string,fn:()=>void,id?:string)=> <AccountLink key={id??label} label={label} testID={id} disabled={c.loading} onPress={fn}/>;
 const footer= <>{!s?.source.pending?secondary('Relire mes informations',()=>run(()=>c.load()),'plan-v3-read-sources'):null}{s?.source.pending? <>{secondary('Relire mes informations',()=>run(()=>c.load()),'plan-v3-read-sources')}{secondary('Répéter explicitement la même action',()=>run(async()=>{await c.retryPendingExplicitly();await c.load();}))}</>:null}{c.notice||notice?<AccountMessage text={runtimeNoticeV3(notice??c.notice)!} alert/>:null}{secondary('Mes préférences',p.onPreferences)}{secondary('Voir Aujourd’hui',p.onExit)}</>;
 const frame=(title:string,children:React.ReactNode)=><AccountFrame key={`${step}:${pilotStage}`} title={title} onBack={()=>setStep('entry')} footer={footer}>{children}</AccountFrame>;
 if(s?.intent&&['submitted','unknown'].includes(s.intent.state))return frame('Démarrage à vérifier',<>
  <AccountMessage text="La création de ta séance n’a pas encore été confirmée."/>
  {action('Vérifier la même demande',()=>c.reconcileStart(),'plan-v3-reconcile')}
  {secondary('Renvoyer cette même demande',()=>run(()=>c.retryStartExplicitly()))}
 </>);
 if(!c.capabilities?.controlled_test_available)return frame('Ton premier entraînement',<>
  <AccountMessage text={c.loading?'Un instant.':'Ton premier plan n’est pas disponible pour le moment.'}/>
  {action('Vérifier à nouveau',()=>c.load())}
 </>);
 const resumeCalibration=async()=>{
  await c.readCalibration();const progress=c.encounter?.progress;
  const choice=progress?.setting_choice,prep=progress?.preparation;
  setCandidate(progress?.context?.canonical_exercise_id??null);
  const saved=resumableCalibrationDraft(c.calibrationDraft(c.encounter?.encounter_ref??''),c.encounter?.encounter_ref??'');
  const observation=saved?.stage==='observation';
  setDraftRef(saved?.draft_ref??c.newCalibrationDraftRef());
  setLoad(saved&&(observation||saved.stage==='setting')?saved.load:choice?.setting.value===null||choice?.setting.value===undefined?'':String(choice.setting.value));
  setInstruction(saved?.instruction??prep?.instruction_ref??'');setSetup(saved?.setup??prep?.setup_ref??'');
  if(saved){setObservedLoad(saved.observedLoad??'');setReps(saved.reps??'');setCompleted(saved.completed??null);setSuccessful(saved.successful==='UNSET'?undefined:saved.successful);setQuality(saved.quality??null);setDiscomfort(saved.discomfort??null);setStopReason(saved.stopReason??null);setTrialAt(saved.trialAt??'');setTrialDate(saved.trialDate??'');setTrialTime(saved.trialTime??'');}
  setPilotStage(observation?'observation':saved?.stage==='setting'?'setting':calibrationStage(c.encounter));setStep('pilot');
 };
 const minimum=async()=>{if(!adult||!noLimit)return;if(await c.saveDeclarations({population_scope:{state:'KNOWN',value:'ADULT_NON_CLINICAL'},limitations:{state:'KNOWN',value:[]}}))setStep('context');};
 const selected=c.capabilities?.supported_realizations?.find(x=>x.candidate_id===candidate);
 const currentName=selected?.display_name??c.capabilities?.supported_realizations?.find(x=>x.candidate_id===c.encounter?.progress.context?.canonical_exercise_id)?.display_name??'Mouvement à identifier';
 if(step==='choose')return frame('Ta préparation',<>
  <AccountMessage text="Une rencontre à la fois. Les observations conservées ne sont pas des permissions actuelles."/>
  {c.capabilities.supported_realizations?.filter(x=>x.initial_guidance_supported).map(x=>{
   const histories=(s?.source.declarations as any)?.observation_progress?.filter((e:any)=>e.kind==='CALIBRATION_ENCOUNTER_OPENED'&&e.context.canonical_exercise_id===x.candidate_id)??[];
   return <View key={x.candidate_id} style={{gap:4}}>
    {secondary((candidate===x.candidate_id?'✓ ':'')+x.display_name,()=>setCandidate(x.candidate_id))}
    <Text style={type.small}>{histories.length?'Observations conservées':'À préparer'}</Text>
    {candidate===x.candidate_id?histories.map((e:any)=><React.Fragment key={e.episode_ref}>{secondary('Reprendre · '+(e.context.equipment_ref??'Dispositif inconnu'),()=>run(async()=>{if(await c.selectCalibration(e.episode_ref))await resumeCalibration();}))}</React.Fragment>):null}
   </View>;
  })}
  {selected?action('Préparer ce mouvement',async()=>{
   setPlace('');setDevice('');setLoad('');setInstruction('');setSetup('');setAvailable('UNKNOWN');setConcern('UNKNOWN');setPilotStage('preparation');setObservedLoad('');setReps('');setCompleted(null);setSuccessful(undefined);setQuality(null);setDiscomfort(null);setStopReason(null);setTrialAt('');setTrialDate('');setTrialTime('');
   const facts=(s?.source.declarations as any)?.blueprint;
   setStep(facts?.population_scope?.value==='ADULT_NON_CLINICAL'&&facts?.limitations?.state==='KNOWN'&&facts.limitations.value?.length===0?'context':'minimum');
  }):null}
 </>);
 if(step==='observed')return <PlanV3ObservedScreen controller={c} onBack={()=>setStep('entry')}/>;
 if(step==='minimum')return frame('Avant de découvrir l’appareil',<>
  <AccountMessage text="Cette première exploration concerne un adulte, dans un cadre non clinique et sans limitation déclarée. Elle ne garantit pas la sécurité médicale."/>
  {secondary(adult?'✓ Adulte · cadre non clinique':'Je déclare être adulte, dans un cadre non clinique',()=>setAdult(!adult))}
  {secondary(noLimit?'✓ Aucune limitation déclarée':'Je ne déclare aucune limitation',()=>setNoLimit(!noLimit))}
  {adult&&noLimit?action('Continuer',minimum):<AccountMessage text="Si ce cadre ne te correspond pas, tu peux revenir à Aujourd’hui sans effectuer cet essai."/>}
 </>);
 if(step==='context')return frame('Ton contexte',<CalibrationInstrument name={currentName} status="Informations que tu déclares">
  <AccountMessage text="Identifie le dispositif réellement présent. Aucun réglage de départ n’est calculé."/>
  <AccountField editable={!c.loading} secureTextEntry={false} textContentType="none" autoComplete="off" label="Lieu ou contexte" value={place} onChangeText={setPlace}/>
  <AccountField editable={!c.loading} secureTextEntry={false} textContentType="none" autoComplete="off" label={selected?.load_semantics==='PER_IMPLEMENT'?'Paire d’haltères et dispositif précis':'Appareil précis'} value={device} onChangeText={setDevice}/>
  {(['AVAILABLE','UNAVAILABLE','UNKNOWN'] as const).map(v=>secondary((available===v?'✓ ':'')+({AVAILABLE:'Dispositif disponible',UNAVAILABLE:'Indisponible',UNKNOWN:'Disponibilité inconnue'}[v]),()=>setAvailable(v)))}
  {(['CLEAR','REPORTED','UNKNOWN'] as const).map(v=>secondary((concern===v?'✓ ':'')+({CLEAR:'Aucune préoccupation rapportée',REPORTED:'Je rapporte une préoccupation',UNKNOWN:'Je ne sais pas conclure'}[v]),()=>setConcern(v)))}
  {place.trim()&&device.trim()&&selected?action('Confirmer ce contexte',async()=>{
   const context:ContextV3={canonical_exercise_id:selected.candidate_id,realization_ref:selected.realization_ref,context_ref:place.trim(),equipment_ref:device.trim(),side:'BILATERAL',load_semantics:selected.load_semantics??'UNKNOWN'};
   await c.openCalibration(context,available,concern);if(c.encounter)setStep('pilot');
  }):null}
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
  const r=c.encounter?.result;
  const form:CalibrationDraft={draft_ref:draftRef,encounter_ref:typeof s?.source.encounter_ref==='string'?s.source.encounter_ref:null,stage:pilotStage,candidate,place,device,instruction,setup,load,observedLoad,reps,completed,successful:successful===undefined?'UNSET':successful,quality,discomfort,stopReason,trialAt,trialDate,trialTime};
  return frame(pilotStage==='observation'?'Noter ce qui s’est passé':pilotStage==='decision'?'Examiner l’essai':phases[r?.phase??'']??'Première rencontre',
   <CalibrationEncounterInstrument key={form.encounter_ref} controller={c} name={currentName} form={form} onChange={fields=>{
    if(fields.draft_ref!==undefined)setDraftRef(fields.draft_ref);if(fields.stage!==undefined)setPilotStage(fields.stage);
    if(fields.load!==undefined)setLoad(fields.load);if(fields.observedLoad!==undefined)setObservedLoad(fields.observedLoad);if(fields.reps!==undefined)setReps(fields.reps);if(fields.instruction!==undefined)setInstruction(fields.instruction);if(fields.setup!==undefined)setSetup(fields.setup);
    if(fields.completed!==undefined)setCompleted(fields.completed);if(fields.successful!==undefined)setSuccessful(fields.successful==='UNSET'?undefined:fields.successful);
    if(fields.quality!==undefined)setQuality(fields.quality);if(fields.discomfort!==undefined)setDiscomfort(fields.discomfort);if(fields.stopReason!==undefined)setStopReason(fields.stopReason);
    if(fields.trialAt!==undefined)setTrialAt(fields.trialAt);if(fields.trialDate!==undefined)setTrialDate(fields.trialDate);if(fields.trialTime!==undefined)setTrialTime(fields.trialTime);
   }} onPreparation={async()=>{await c.load();setStep('choose');}} onPause={async()=>{await c.pause();setStep('entry');}} onNotice={setNotice}/>);
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
 return frame('Ton premier entraînement',<>
  <AccountMessage text="Tu peux commencer par découvrir un appareil, même sans charge déjà connue. Tu gardes la possibilité de modifier tes préférences."/>
  {action('Découvrir un appareil',async()=>{setStep('choose');},'plan-v3-first-calibration')}
  {s?.source.encounter_ref?secondary('Reprendre ma rencontre',()=>run(resumeCalibration),'plan-v3-resume-calibration'):null}
  {secondary('Vérifier les réglages qualifiés · voir mon plan',()=>run(async()=>{await c.evaluate();setStep('proposal');}),'plan-v3-open-proposal')}
  {secondary('Ajouter un réglage déjà observé',()=>setStep('observed'))}
  {secondary('Compléter mes disponibilités',()=>setStep('facts'))}
 </>);
}
