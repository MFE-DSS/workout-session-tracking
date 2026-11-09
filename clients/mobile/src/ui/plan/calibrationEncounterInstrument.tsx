/** The single owned calibration instrument; production and native review share this renderer. */
import React,{useState} from 'react';
import {Text,View} from 'react-native';
import type {FirstUseV3Controller} from '../../api/firstUseV3';
import {AccountField,AccountMessage} from '../account/AccountFrame';
import {type} from '../theme';
import {CalibrationInstrument,CalibrationSetting} from './calibrationInstrument';
import {CalibrationAction,CalibrationChoices,CalibrationLink} from './calibrationControls';
import {CalibrationHelp} from './calibrationLayout';
import {parseCalibrationMass,parseCalibrationOccurrence,calibrationStage,calibrationTrialComplete,calibrationObservationSection,type CalibrationDraft} from './calibrationModel';

export function CalibrationEncounterInstrument(p:{controller:FirstUseV3Controller;name:string;form:CalibrationDraft;management?:React.ReactNode;onChange:(patch:Partial<CalibrationDraft>)=>void;onPreparation:()=>Promise<void>;onPause:()=>Promise<void>;onNotice:(message:string)=>void}){
 const c=p.controller,f=p.form,stage=f.stage,encounter=c.encounter,r=encounter?.result,allowed=encounter?.allowed_actions??[],ctx=encounter?.progress.context,last=encounter?.progress.observations?.at(-1);
 const [details,setDetails]=useState(false),[history,setHistory]=useState(false),[withdrawConfirm,setWithdrawConfirm]=useState(false),[pastTime,setPastTime]=useState(Boolean(f.trialDate||f.trialTime));
 const section=calibrationObservationSection(f),setting=parseCalibrationMass(f.load),observedSetting=parseCalibrationMass(f.observedLoad??'');
 const run=(task:()=>Promise<unknown>)=>{void task().catch(()=>p.onNotice('La réponse reste à vérifier. Tes faits sont conservés.'));};
 const action=(label:string,task:()=>Promise<unknown>,id?:string,reason?:string)=><CalibrationAction label={label} busy={c.loading} disabled={Boolean(reason)} reason={reason} testID={id} onPress={()=>run(task)}/>;
 const secondary=(label:string,fn:()=>void,id?:string)=><CalibrationLink key={id??label} label={label} testID={id} disabled={c.loading} onPress={fn}/>;
 const emit=(o:Record<string,unknown>)=>c.recordCalibration(o),event=async(e:Record<string,unknown>)=>emit({kind:'CALIBRATION_EVENT_REPORTED',event:e});
 const status=!r?'Guidage à vérifier':({CALIBRATION_REQUIRED:'Préparation requise',SUPPORTED_INITIAL_EXPLORATION:'Exploration disponible',OBSERVED:'Observation à examiner',QUALIFIED:'Réglage provisoire',CONCERN_REVIEW:'Revue nécessaire',WITHDRAWN:'Guidage retiré',UNAVAILABLE:'Dispositif indisponible',INSUFFICIENT_EVIDENCE:'Informations insuffisantes'}[r.state]??'Confirmation serveur reçue');
 const stopped=!r||['WITHDRAWN','CONCERN_REVIEW','UNAVAILABLE','INSUFFICIENT_EVIDENCE'].includes(r.state);
 const observationReset=()=>p.onChange({draft_ref:c.newCalibrationDraftRef(),observedLoad:'',reps:'',completed:null,successful:'UNSET',quality:null,discomfort:null,stopReason:null,trialAt:'',trialDate:'',trialTime:'',observationSection:'trial',stage:'observation'});
 const choices=(label:string,key:'quality'|'discomfort'|'stopReason',labels:Record<string,string>)=><CalibrationChoices label={label} value={f[key]} disabled={c.loading} options={Object.entries(labels).map(([value,label])=>({value,label}))} onChange={v=>p.onChange({[key]:v})}/>;
 const stopLabels={COMPLETED:'Terminé',USER_STOPPED:'Arrêt volontaire',TIME_LIMIT:'Limite de temps',CONCERN:'Préoccupation',FAILURE:'Échec',UNKNOWN:'Motif inconnu'};
 const ready=calibrationTrialComplete(f)&&Boolean(f.quality&&f.discomfort&&f.stopReason&&f.trialAt);
 return <CalibrationInstrument name={p.name} status={status}>
  <Text style={type.small}>{ctx?.equipment_ref??'Dispositif inconnu'} · {ctx?.context_ref??'Contexte inconnu'}</Text>
  {r?.state==='QUALIFIED'?<AccountMessage text="Réglage observé provisoirement accepté, à réessayer dans ce contexte. Il ne représente pas un poids optimal."/>:null}
  {r?.state==='CONCERN_REVIEW'?<AccountMessage text="Une préoccupation ou une information de contrôle ou de gêne reste à examiner dans l’historique. Aucune nouvelle consigne physique n’est donnée."/>:null}
  {stopped&&r?.state!=='CONCERN_REVIEW'?<AccountMessage text="Aucune nouvelle consigne. Les faits passés restent lisibles et enregistrables."/>:null}
  {stage==='decision'&&last?.setting?.kind==='MASS_KG'&&last.setting.value!==null?<CalibrationSetting value={String(last.setting.value)} onChange={()=>undefined} semantics={ctx?.load_semantics} editing={false} label="Réglage observé" onDone={()=>undefined}/>:null}
  {r&&!stopped&&stage==='preparation'?<>
   <AccountField editable={!c.loading} secureTextEntry={false} textContentType="none" autoComplete="off" label="Notice réellement consultée" value={f.instruction} onChangeText={instruction=>p.onChange({instruction})}/>
   <AccountField editable={!c.loading} secureTextEntry={false} textContentType="none" autoComplete="off" label="Installation comprise et contrôlée" value={f.setup} onChangeText={setup=>p.onChange({setup})} helper="Décris ton installation selon la notice réellement applicable."/>
   {action('Confirmer cette préparation',async()=>{if(await emit({kind:'PREPARATION_REPORTED',instruction_ref:f.instruction.trim(),setup_ref:f.setup.trim(),understood:true,controlled:true}))p.onChange({stage:'setting'});},undefined,f.instruction.trim()&&f.setup.trim()?undefined:'Indique la notice consultée et ton installation.')}
  </>:null}
  {r&&!stopped&&['setting','familiar','trial'].includes(stage)?<CalibrationSetting disabled={c.loading} value={f.load} onChange={load=>p.onChange({load})} semantics={ctx?.load_semantics} editing={stage==='setting'} onDone={()=>undefined}/>:null}
  {r&&!stopped&&stage==='setting'?<>
   <AccountMessage text="Choisis toi-même un réglage effectivement disponible. Aucun premier kilogramme ni incrément n’est recommandé."/>
   {action('Confirmer ce réglage disponible',async()=>{if(setting&&await emit({kind:'SETTING_CHOICE_REPORTED',setting,available:true}))p.onChange({stage:'familiar'});},undefined,setting?undefined:'Saisis le réglage réellement disponible.')}
   {!setting&&allowed.includes('INITIATE_FAMILIARIZATION')?secondary('Découvrir l’installation sans essai chargé',()=>run(()=>emit({kind:'CALIBRATION_ACTION_REQUESTED',action:'INITIATE_FAMILIARIZATION'})),'plan-v3-setup-discovery'):null}
  </>:null}
  {r&&!stopped&&stage==='familiar'&&allowed.includes('CONFIRM_FAMILIARIZATION')?<>
   <AccountMessage text="Vérifie le contexte et familiarise-toi réellement à ce réglage exact, selon les instructions applicables. Si tu ne peux pas contrôler le dispositif, fais une pause ou demande une aide sur place."/>
   {allowed.includes('CONFIRM_CONTEXT')&&!encounter?.progress.events?.some(e=>e.kind==='CONTEXT_CONFIRMED'&&e.setting?.kind===setting?.kind&&e.setting?.unit===setting?.unit&&e.setting?.value===setting?.value&&Date.parse(String(e.provenance.recorded_at))>=Date.parse(String(encounter?.progress.setting_choice?.provenance?.recorded_at)))?action('Confirmer contexte et réglage',()=>event({kind:'CONTEXT_CONFIRMED',setting}),undefined,setting?undefined:'Indique le réglage exact.'):action('Familiarisation réellement effectuée',async()=>{if(setting&&await event({kind:'FAMILIARIZATION_CONFIRMED',setting}))p.onChange({stage:'trial'});},undefined,setting?undefined:'Indique le réglage exact.')}
   {secondary('Choisir un autre réglage',()=>p.onChange({stage:'setting'}))}
  </>:null}
  {r&&!stopped&&stage==='trial'&&allowed.includes('INITIATE_TRIAL')?<>
   <AccountMessage text="Viser 8–12 répétitions en gardant de la réserve selon ta compréhension, sans obligation d’atteindre cette plage ni de chercher l’échec. L’effort ressenti n’est pas un RIR mesuré."/>
   {action('Choisir de faire un essai',async()=>{if(await emit({kind:'CALIBRATION_ACTION_REQUESTED',action:'INITIATE_TRIAL'}))observationReset();},'plan-v3-loaded-trial')}
  </>:null}
  {stage==='observation'&&(allowed.includes('RECORD_TRIAL')||!r)?<>
   <AccountMessage text="Note uniquement un essai réellement effectué. Ce formulaire n’autorise pas un nouvel essai."/>
   {section==='trial'?<>
    <CalibrationSetting disabled={c.loading} value={f.observedLoad??''} onChange={observedLoad=>p.onChange({observedLoad})} semantics={ctx?.load_semantics} editing label="Réglage réellement utilisé" onDone={()=>undefined}/>
    {encounter?.progress.setting_choice?.setting.kind==='MASS_KG'?secondary('Je confirme avoir utilisé le réglage choisi',()=>p.onChange({observedLoad:String(encounter.progress.setting_choice!.setting.value)})):null}
    <AccountField editable={!c.loading} secureTextEntry={false} textContentType="none" autoComplete="off" label="Répétitions réellement faites" keyboardType="number-pad" value={f.reps} onChangeText={reps=>p.onChange({reps})}/>
    <CalibrationChoices label="Complétion" value={f.completed} disabled={c.loading} options={[{value:true,label:'Essai terminé'},{value:false,label:'Essai interrompu'}]} onChange={completed=>p.onChange({completed})}/>
    <CalibrationChoices label="Réussite" value={f.successful==='UNSET'?undefined:f.successful} disabled={c.loading} options={[{value:true,label:'Réussite rapportée'},{value:false,label:'Échec rapporté'},{value:null,label:'Réussite inconnue'}]} onChange={successful=>p.onChange({successful})}/>
    {action('Continuer',async()=>p.onChange({observationSection:'feeling'}),'calibration-observation-continue',calibrationTrialComplete(f)?undefined:'Indique le réglage utilisé, les répétitions, la complétion et la réussite.')}
   </>:<>
    {choices('Contrôle rapporté','quality',{ACCEPTABLE:'Contrôle acceptable rapporté',CONCERN:'Contrôle préoccupant',UNKNOWN:'Contrôle inconnu'})}
    {choices('Gêne rapportée','discomfort',{NO_CONCERN:'Pas de gêne préoccupante rapportée',CONCERN:'Préoccupation rapportée',UNKNOWN:'Gêne inconnue'})}
    {choices('Motif réel d’arrêt','stopReason',stopLabels)}
    <Text style={type.eyebrow}>Quand l’essai a eu lieu</Text>
    {secondary('L’essai vient de se terminer',()=>{p.onChange({trialAt:new Date().toISOString(),trialDate:'',trialTime:''});setPastTime(false);})}
    {secondary(pastTime?'Masquer la date et l’heure':'Indiquer une date et une heure',()=>setPastTime(!pastTime))}
    {pastTime?<>
     <AccountField editable={!c.loading} secureTextEntry={false} textContentType="none" autoComplete="off" label="Date de l’essai" helper="AAAA-MM-JJ · selon ton heure locale" value={f.trialDate} onChangeText={trialDate=>p.onChange({trialDate,trialAt:parseCalibrationOccurrence(trialDate,f.trialTime)??''})}/>
     <AccountField editable={!c.loading} secureTextEntry={false} textContentType="none" autoComplete="off" label="Heure de l’essai" helper="HH:MM · pour un essai passé" value={f.trialTime} onChangeText={trialTime=>p.onChange({trialTime,trialAt:parseCalibrationOccurrence(f.trialDate,trialTime)??''})}/>
    </>:null}
    {f.trialAt?<Text testID="calibration-occurrence" style={type.small}>Heure indiquée : {new Date(f.trialAt).toLocaleString()}</Text>:null}
    {action('Enregistrer ces faits',async()=>{if(ready&&await emit({kind:'CALIBRATION_EVENT_REPORTED',stop_reason:f.stopReason,event:{kind:'ATTEMPT_OBSERVED',setting:observedSetting,reps:Number(f.reps),completed:f.completed,successful:f.successful,technique:f.quality,discomfort:f.discomfort,occurred_at:f.trialAt}}))p.onChange({stage:'decision'});},undefined,ready?undefined:'Complète les faits de l’essai, le contrôle, la gêne, le motif et l’heure réelle.')}
    {secondary('Corriger mon essai',()=>p.onChange({observationSection:'trial'}))}
   </>}
  </>:null}
  {stage==='decision'&&allowed.includes('ACCEPT_EXACT_SETTING')&&last?action('Accepter ce réglage provisoire exact',()=>event({kind:'SETTING_ACCEPTED',reference_event_id:last.event_id})):null}
  {stage==='decision'&&r?.state==='OBSERVED'&&!allowed.includes('ACCEPT_EXACT_SETTING')?action('Demander un réessai',async()=>{if(await emit({kind:'CALIBRATION_RETRY_REQUESTED'}))p.onChange({stage:calibrationStage(c.encounter)});}):null}
  {stage==='decision'&&r?.state==='QUALIFIED'?action('Revenir à ma préparation',()=>p.onPreparation()):null}
  {stopped&&stage!=='observation'?action('Relire la rencontre',async()=>{await c.readCalibration();p.onChange({stage:calibrationStage(c.encounter)});}):null}
  {(allowed.includes('RECORD_TRIAL')||!r)&&stage!=='observation'?secondary('Noter un essai déjà réalisé',observationReset):null}
  {allowed.includes('RECORD_TRIAL')?secondary('Signaler une préoccupation',()=>run(()=>event({kind:'CONCERN_REPORTED'}))):null}
  {secondary('Pause · conserver mes observations',()=>run(()=>p.onPause()))}
  <CalibrationLink label="Historique" expanded={history} onPress={()=>setHistory(!history)}/>
  {history?<View style={{gap:8}}>{last?<>
   <Text style={type.body}>{last.reps===null?'Répétitions inconnues':`${last.reps} répétitions rapportées`}</Text>
   <Text style={type.small}>Contrôle rapporté : {({ACCEPTABLE:'acceptable',CONCERN:'préoccupant',UNKNOWN:'inconnu'} as Record<string,string>)[last.technique]??'non renseigné'} · Gêne : {({NO_CONCERN:'aucune préoccupation rapportée',CONCERN:'préoccupation rapportée',UNKNOWN:'inconnue'} as Record<string,string>)[last.discomfort]??'non renseignée'}</Text>
   <Text style={type.small}>Motif : {(stopLabels as Record<string,string>)[encounter?.progress.reported_stop_reasons?.[last.event_id]?.value??'']??'non renseigné'}</Text>
  </>:<AccountMessage text="Aucun essai conservé à afficher."/>}</View>:null}
  <CalibrationLink label="Détails" expanded={details} onPress={()=>setDetails(!details)}/>
  {details?<>
   <AccountMessage text="Ce calibrage est une observation, pas une série de travail. Tu peux t’arrêter."/>
   {!stopped?secondary('Relire la rencontre',()=>run(async()=>{await c.readCalibration();p.onChange({stage:calibrationStage(c.encounter)});})):null}
   {p.management}
  </>:null}
  {details||stopped?withdrawConfirm?<><AccountMessage text="Le retrait arrête le guidage de cette préparation. Tes faits sont conservés. Aucune reprise après préoccupation n’est admise ici."/>{secondary('Confirmer le retrait du guidage',()=>run(()=>emit({kind:'ENCOUNTER_WITHDRAWN'})))}</>:secondary('Retirer le guidage',()=>setWithdrawConfirm(true)):null}
  <CalibrationHelp controller={c} candidate={ctx?.canonical_exercise_id??f.candidate} stage={stopped?'concern':stage==='familiar'?'familiarization':stage==='preparation'?'identify':stage} scopeKey={`${f.encounter_ref}:${stage}:${section}`}/>
 </CalibrationInstrument>;
}
