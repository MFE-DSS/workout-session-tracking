/** The single owned calibration instrument; production and native review share this renderer. */
import React,{useState} from 'react';
import {Text,View} from 'react-native';
import type {FirstUseV3Controller} from '../../api/firstUseV3';
import {AccountField,AccountLink,AccountMessage} from '../account/AccountFrame';
import {PrimaryAction} from '../components';
import {type} from '../theme';
import {CalibrationInstrument,CalibrationSetting} from './calibrationInstrument';
import {parseCalibrationMass,parseCalibrationOccurrence,calibrationStage,type CalibrationDraft} from './calibrationModel';

export function CalibrationEncounterInstrument(p:{controller:FirstUseV3Controller;name:string;form:CalibrationDraft;onChange:(patch:Partial<CalibrationDraft>)=>void;onPreparation:()=>Promise<void>;onPause:()=>Promise<void>;onNotice:(message:string)=>void}){
 const c=p.controller,currentName=p.name,{load,observedLoad,reps,completed,quality,discomfort,stopReason,trialAt,trialDate,trialTime,instruction,setup}=p.form;
 const successful=p.form.successful==='UNSET'?undefined:p.form.successful,pilotStage=p.form.stage;
 const [showProtocol,setShowProtocol]=useState(false),[withdrawConfirm,setWithdrawConfirm]=useState(false);
 const setLoad=(v:string)=>p.onChange({load:v}),setObservedLoad=(v:string)=>p.onChange({observedLoad:v}),setReps=(v:string)=>p.onChange({reps:v}),setCompleted=(v:boolean|null)=>p.onChange({completed:v}),
  setSuccessful=(v:boolean|null|undefined)=>p.onChange({successful:v===undefined?'UNSET':v}),setQuality=(v:string|null)=>p.onChange({quality:v}),setDiscomfort=(v:string|null)=>p.onChange({discomfort:v}),
  setStopReason=(v:string|null)=>p.onChange({stopReason:v}),setTrialAt=(v:string)=>p.onChange({trialAt:v}),setTrialDate=(v:string)=>p.onChange({trialDate:v}),setTrialTime=(v:string)=>p.onChange({trialTime:v}),
  setInstruction=(v:string)=>p.onChange({instruction:v}),setSetup=(v:string)=>p.onChange({setup:v}),setPilotStage=(v:CalibrationDraft['stage'])=>p.onChange({stage:v}),setDraftRef=(v:string)=>p.onChange({draft_ref:v});
 const run=(task:()=>Promise<unknown>)=>{void task().catch(()=>p.onNotice('La réponse reste à vérifier. Tes faits sont conservés.'));};
 const action=(label:string,task:()=>Promise<unknown>,id?:string)=><PrimaryAction label={label} busy={c.loading} testID={id} onPress={()=>run(task)}/>;
 const secondary=(label:string,fn:()=>void,id?:string)=><AccountLink key={id??label} label={label} testID={id} disabled={c.loading} onPress={fn}/>;
  const encounter=c.encounter,r=encounter?.result,allowed=encounter?.allowed_actions??[],last=encounter?.progress.observations?.at(-1),ctx=encounter?.progress.context,setting=parseCalibrationMass(load),observedSetting=parseCalibrationMass(observedLoad??'');
  const emit=(o:Record<string,unknown>)=>c.recordCalibration(o);
  const event=async(e:Record<string,unknown>)=>emit({kind:'CALIBRATION_EVENT_REPORTED',event:e});
  const status=!r?'Guidage à vérifier':({CALIBRATION_REQUIRED:'Préparation requise',SUPPORTED_INITIAL_EXPLORATION:'Exploration disponible',OBSERVED:'Observation à examiner',QUALIFIED:'Réglage provisoire',CONCERN_REVIEW:'Revue nécessaire',WITHDRAWN:'Guidage retiré',UNAVAILABLE:'Dispositif indisponible',INSUFFICIENT_EVIDENCE:'Informations insuffisantes'}[r.state]??'Confirmation serveur reçue');
  const material=ctx?.canonical_exercise_id==='leg-extensions-assises'?c.capabilities?.calibration_protocol_material:c.capabilities?.calibration_inventory?.protocol_material;
  return <CalibrationInstrument name={currentName} status={status}>
   <AccountMessage text="Ce calibrage est une observation, pas une série de travail. Tu peux t’arrêter."/>
   {r?.state==='QUALIFIED'?<AccountMessage text="Réglage observé provisoirement accepté, à réessayer dans ce contexte. Il ne représente pas un poids optimal."/>:null}
   {r?.state==='CONCERN_REVIEW'?<AccountMessage text="Une préoccupation ou une information de contrôle ou de gêne reste à examiner dans l’historique. Aucune nouvelle consigne physique n’est donnée."/>:null}
   {!r?<AccountMessage text="Aucune nouvelle consigne. Les faits passés restent lisibles et enregistrables."/>:null}
   {last?<View style={{gap:6}}><Text style={type.eyebrow}>Dernier essai conservé</Text>{pilotStage==='decision'&&last.setting?.kind==='MASS_KG'&&last.setting.value!==null?<CalibrationSetting value={String(last.setting.value)} onChange={()=>undefined} semantics={ctx?.load_semantics} editing={false} label="Réglage observé" onDone={()=>undefined}/>:null}<Text style={type.body}>{last.reps===null?'Répétitions inconnues':`${last.reps} répétitions rapportées`}</Text><Text style={type.small}>Contrôle rapporté : {({ACCEPTABLE:'acceptable',CONCERN:'préoccupant',UNKNOWN:'inconnu'} as Record<string,string>)[last.technique]??'non renseigné'} · Gêne : {({NO_CONCERN:'aucune préoccupation rapportée',CONCERN:'préoccupation rapportée',UNKNOWN:'inconnue'} as Record<string,string>)[last.discomfort]??'non renseignée'}</Text>
    <Text style={type.small}>Motif : {({COMPLETED:'terminé',USER_STOPPED:'arrêt volontaire',TIME_LIMIT:'limite de temps',CONCERN:'préoccupation',FAILURE:'échec',UNKNOWN:'inconnu déclaré'} as Record<string,string>)[encounter?.progress.reported_stop_reasons?.[last.event_id]?.value??'']??'non renseigné'}</Text><Text style={type.small}>{ctx?.equipment_ref??'Dispositif inconnu'} · {ctx?.context_ref??'Contexte inconnu'}</Text></View>:null}
   {secondary(showProtocol?'Masquer la procédure':'Lire la procédure applicable',()=>setShowProtocol(!showProtocol))}
   {showProtocol?<Text selectable style={type.body}>{material?.text??'Procédure indisponible : aucune nouvelle consigne.'}</Text>:null}
   {r&&pilotStage==='preparation'?<>
    <AccountField editable={!c.loading} secureTextEntry={false} textContentType="none" autoComplete="off" label="Notice réellement consultée" value={instruction} onChangeText={setInstruction}/>
    <AccountField editable={!c.loading} secureTextEntry={false} textContentType="none" autoComplete="off" label="Installation comprise et contrôlée" value={setup} onChangeText={setSetup} helper="Décris ton installation selon la notice réellement applicable."/>
    {instruction.trim()&&setup.trim()?action('Confirmer cette préparation',async()=>{if(await emit({kind:'PREPARATION_REPORTED',instruction_ref:instruction.trim(),setup_ref:setup.trim(),understood:true,controlled:true}))setPilotStage('setting');}):null}
   </>:null}
   {r&&['setting','familiar','trial'].includes(pilotStage)?<CalibrationSetting disabled={c.loading} value={load} onChange={setLoad} semantics={ctx?.load_semantics} editing={pilotStage==='setting'} onDone={()=>undefined}/>:null}
   {r&&pilotStage==='setting'?<>
    <AccountMessage text="Choisis toi-même un réglage effectivement disponible. Aucun premier kilogramme ni incrément n’est recommandé."/>
    {!setting&&allowed.includes('INITIATE_FAMILIARIZATION')?action('Découvrir l’installation sans essai chargé',()=>emit({kind:'CALIBRATION_ACTION_REQUESTED',action:'INITIATE_FAMILIARIZATION'}),'plan-v3-setup-discovery'):null}
    {setting?action('Confirmer ce réglage disponible',async()=>{if(await emit({kind:'SETTING_CHOICE_REPORTED',setting,available:true}))setPilotStage('familiar');}):null}
   </>:null}
   {r&&pilotStage==='familiar'&&allowed.includes('CONFIRM_FAMILIARIZATION')?<>
    <AccountMessage text="Vérifie le contexte et familiarise-toi réellement à ce réglage exact, selon les instructions applicables. Si tu ne peux pas contrôler le dispositif, fais une pause ou demande une aide sur place."/>
    {allowed.includes('CONFIRM_CONTEXT')&&setting&&!encounter?.progress.events?.some(e=>e.kind==='CONTEXT_CONFIRMED'&&e.setting?.kind===setting?.kind&&e.setting?.unit===setting?.unit&&e.setting?.value===setting?.value&&Date.parse(String(e.provenance.recorded_at))>=Date.parse(String(encounter?.progress.setting_choice?.provenance?.recorded_at)))?action('Confirmer contexte et réglage',()=>event({kind:'CONTEXT_CONFIRMED',setting})):allowed.includes('CONFIRM_FAMILIARIZATION')&&setting?action('Familiarisation réellement effectuée',async()=>{if(await event({kind:'FAMILIARIZATION_CONFIRMED',setting}))setPilotStage('trial');}):null}
    {secondary('Choisir un autre réglage',()=>setPilotStage('setting'))}
   </>:null}
   {r&&pilotStage==='trial'&&allowed.includes('INITIATE_TRIAL')?<>
    <AccountMessage text="Viser 8–12 répétitions en gardant de la réserve selon ta compréhension, sans obligation d’atteindre cette plage ni de chercher l’échec. L’effort ressenti n’est pas un RIR mesuré."/>
    {action('Choisir de faire un essai',async()=>{if(await emit({kind:'CALIBRATION_ACTION_REQUESTED',action:'INITIATE_TRIAL'})){setObservedLoad('');setStopReason(null);setCompleted(null);setSuccessful(undefined);setQuality(null);setDiscomfort(null);setReps('');setTrialAt('');setTrialDate('');setTrialTime('');setDraftRef(c.newCalibrationDraftRef());setPilotStage('observation');}})}
   </>:null}
   {pilotStage==='observation'&&(allowed.includes('RECORD_TRIAL')||!r)?<>
    <AccountMessage text="Note uniquement un essai réellement effectué. Ce formulaire n’autorise pas un nouvel essai."/>
    <CalibrationSetting disabled={c.loading} value={observedLoad??''} onChange={setObservedLoad} semantics={ctx?.load_semantics} editing label="Réglage réellement utilisé" onDone={()=>undefined}/>
    {encounter?.progress.setting_choice?.setting.kind==='MASS_KG'?secondary('Je confirme avoir utilisé le réglage choisi',()=>setObservedLoad(String(encounter.progress.setting_choice!.setting.value))):null}
    <Text style={type.small}>{ctx?.equipment_ref??'Dispositif inconnu'} · {ctx?.context_ref??'Contexte inconnu'}</Text>
    <AccountField editable={!c.loading} secureTextEntry={false} textContentType="none" autoComplete="off" label="Répétitions réellement faites" keyboardType="number-pad" value={reps} onChangeText={setReps}/>
    {([true,false] as const).map(v=>secondary((completed===v?'✓ ':'')+(v?'Essai terminé':'Essai interrompu'),()=>setCompleted(v)))}
    {([true,false,null] as const).map(v=>secondary((successful===v?'✓ ':'')+(v===null?'Réussite inconnue':v?'Réussite rapportée':'Échec rapporté'),()=>setSuccessful(v)))}
    {['ACCEPTABLE','CONCERN','UNKNOWN'].map(v=>secondary((quality===v?'✓ ':'')+({ACCEPTABLE:'Contrôle acceptable rapporté',CONCERN:'Contrôle préoccupant',UNKNOWN:'Contrôle inconnu'}[v]),()=>setQuality(v)))}
    {['NO_CONCERN','CONCERN','UNKNOWN'].map(v=>secondary((discomfort===v?'✓ ':'')+({NO_CONCERN:'Pas de gêne préoccupante rapportée',CONCERN:'Préoccupation rapportée',UNKNOWN:'Gêne inconnue'}[v]),()=>setDiscomfort(v)))}
    <Text style={type.eyebrow}>Quand l’essai a eu lieu</Text>
    {secondary('L’essai vient de se terminer',()=>{const now=new Date();setTrialAt(now.toISOString());setTrialDate('');setTrialTime('');})}
    <AccountField editable={!c.loading} secureTextEntry={false} textContentType="none" autoComplete="off" label="Date de l’essai" helper="AAAA-MM-JJ · selon ton heure locale" value={trialDate} onChangeText={v=>{setTrialDate(v);setTrialAt(parseCalibrationOccurrence(v,trialTime)??'');}}/>
    <AccountField editable={!c.loading} secureTextEntry={false} textContentType="none" autoComplete="off" label="Heure de l’essai" helper="HH:MM · pour un essai passé" value={trialTime} onChangeText={v=>{setTrialTime(v);setTrialAt(parseCalibrationOccurrence(trialDate,v)??'');}}/>
    {trialAt?<Text style={type.small}>Heure indiquée : {new Date(trialAt).toLocaleString()}</Text>:null}
    <Text style={type.eyebrow}>Motif réel d’arrêt</Text>
    {['COMPLETED','USER_STOPPED','TIME_LIMIT','CONCERN','FAILURE','UNKNOWN'].map(v=>secondary((stopReason===v?'✓ ':'')+({COMPLETED:'Terminé',USER_STOPPED:'Arrêt volontaire',TIME_LIMIT:'Limite de temps',CONCERN:'Préoccupation',FAILURE:'Échec',UNKNOWN:'Motif inconnu'}[v]),()=>setStopReason(v)))}
    {observedSetting&&completed!==null&&successful!==undefined&&quality&&discomfort&&stopReason&&/^\d+$/.test(reps)&&Number.isSafeInteger(Number(reps))&&trialAt?action('Enregistrer ces faits',async()=>{if(await emit({kind:'CALIBRATION_EVENT_REPORTED',stop_reason:stopReason,event:{kind:'ATTEMPT_OBSERVED',setting:observedSetting,reps:Number(reps),completed,successful,technique:quality,discomfort,occurred_at:trialAt}}))setPilotStage('decision');}):null}
   </>:null}
   {pilotStage==='decision'&&allowed.includes('ACCEPT_EXACT_SETTING')&&last?action('Accepter ce réglage provisoire exact',()=>event({kind:'SETTING_ACCEPTED',reference_event_id:last.event_id})):null}
   {pilotStage==='decision'&&r?.state==='OBSERVED'&&!allowed.includes('ACCEPT_EXACT_SETTING')?action('Demander un réessai',async()=>{if(await emit({kind:'CALIBRATION_RETRY_REQUESTED'}))setPilotStage(calibrationStage(c.encounter));}):null}
   {pilotStage==='decision'&&r?.state==='QUALIFIED'?action('Revenir à ma préparation',()=>p.onPreparation()):null}
   {(allowed.includes('RECORD_TRIAL')||!r)&&pilotStage!=='observation'?secondary('Noter un essai déjà réalisé',()=>{setDraftRef(c.newCalibrationDraftRef());setObservedLoad('');setReps('');setCompleted(null);setSuccessful(undefined);setQuality(null);setDiscomfort(null);setStopReason(null);setTrialAt('');setTrialDate('');setTrialTime('');setPilotStage('observation');}):null}
   {allowed.includes('RECORD_TRIAL')?secondary('Signaler une préoccupation',()=>run(()=>event({kind:'CONCERN_REPORTED'}))):null}
   {secondary('Pause · conserver mes observations',()=>run(()=>p.onPause()))}
   {withdrawConfirm?<><AccountMessage text="Le retrait arrête le guidage de cette préparation. Tes faits sont conservés. Aucune reprise après préoccupation n’est admise ici."/>{secondary('Confirmer le retrait du guidage',()=>run(()=>emit({kind:'ENCOUNTER_WITHDRAWN'})))}</>:secondary('Retirer le guidage',()=>setWithdrawConfirm(true))}
   {(!r||['WITHDRAWN','CONCERN_REVIEW','UNAVAILABLE','INSUFFICIENT_EVIDENCE'].includes(r.state))&&pilotStage!=='observation'?action('Relire la rencontre',async()=>{await c.readCalibration();setPilotStage(calibrationStage(c.encounter));}):secondary('Relire la rencontre',()=>run(async()=>{await c.readCalibration();setPilotStage(calibrationStage(c.encounter));}))}
  </CalibrationInstrument>;
}
