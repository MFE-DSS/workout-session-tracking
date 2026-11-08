/** G1 approved first-use composition. All actions pass through the owned controller. */
import React,{useState} from 'react';
import {Text,View} from 'react-native';
import type {FirstUseV3Controller} from '../../api/firstUseV3';
import type {EvaluationV3,ContextV3} from '../../domain/planV3Types';
import {AccountFrame,AccountField,AccountLink,AccountMessage} from '../account/AccountFrame';
import {PrimaryAction} from '../components';
import {settingDescriptionV3} from './settingV3';
import {runtimeNoticeV3} from './PlanV3Messages';
import {PlanV3ObservedScreen} from './PlanV3ObservedScreen';
import {color,type} from '../theme';
type Step='entry'|'minimum'|'facts'|'context'|'pilot'|'proposal'|'ack'|'observed';
const requiredLabels:Record<string,string>={objective:'Objectif',population_scope:'Cadre déclaré',sessions_per_week:'Séances par semaine',session_budgets_minutes:'Temps disponible',limitations:'Limitations déclarées'};
const phases:Record<string,string>={PREPARE:'Préparer l’appareil',FAMILIARIZE:'Se familiariser',TRIAL:'Faire un essai',OBSERVE:'Noter ce qui s’est passé',DECIDE:'Examiner l’essai',STOP:'Faire une pause'};
export function PlanV3FirstUseScreen(p:{controller:FirstUseV3Controller;onExit:()=>void;onPreferences:()=>void}){
 const c=p.controller,s=c.state,[step,setStep]=useState<Step>('entry'),[pilotStage,setPilotStage]=useState<'preparation'|'setting'|'familiar'|'trial'|'observation'|'decision'>('preparation'),[adult,setAdult]=useState(false),[noLimit,setNoLimit]=useState(false),
 [budget1,setBudget1]=useState(''),[budget2,setBudget2]=useState(''),[place,setPlace]=useState(''),[device,setDevice]=useState(''),
 [instruction,setInstruction]=useState(''),[setup,setSetup]=useState(''),[load,setLoad]=useState(''),[reps,setReps]=useState(''),
 [expandedSlot,setExpandedSlot]=useState<string|null>(null),[notice,setNotice]=useState<string|null>(null),[showProtocol,setShowProtocol]=useState(false),[trialAt,setTrialAt]=useState(''),
 [successful,setSuccessful]=useState<boolean|null|undefined>(undefined),[completed,setCompleted]=useState<boolean|null>(null),[quality,setQuality]=useState<string|null>(null),[discomfort,setDiscomfort]=useState<string|null>(null);
 const run=(task:()=>Promise<unknown>)=>{setNotice(null);void task().catch(()=>setNotice('La réponse reste à vérifier. Tes faits sont conservés.'));};
 const action=(label:string,task:()=>Promise<unknown>,id?:string)=> <PrimaryAction label={label} busy={c.loading} testID={id} onPress={()=>run(task)}/>;
 const secondary=(label:string,fn:()=>void,id?:string)=> <AccountLink label={label} testID={id} disabled={c.loading} onPress={fn}/>;
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
  setLoad(choice?.setting.value===null||choice?.setting.value===undefined?'':String(choice.setting.value));
  setInstruction(prep?.instruction_ref??'');setSetup(prep?.setup_ref??'');
  setPilotStage((progress?.observed_attempt_count??0)>0?'decision':prep?'setting':'preparation');setStep('pilot');
 };
 const minimum=async()=>{if(!adult||!noLimit)return;if(await c.saveDeclarations({population_scope:{state:'KNOWN',value:'ADULT_NON_CLINICAL'},limitations:{state:'KNOWN',value:[]}}))setStep('context');};
 if(step==='observed')return <PlanV3ObservedScreen controller={c} onBack={()=>setStep('entry')}/>;
 if(step==='minimum')return frame('Avant de découvrir l’appareil',<>
  <AccountMessage text="Cette première exploration concerne un adulte, dans un cadre non clinique et sans limitation déclarée. Elle ne garantit pas la sécurité médicale."/>
  {secondary(adult?'✓ Adulte · cadre non clinique':'Je déclare être adulte, dans un cadre non clinique',()=>setAdult(!adult))}
  {secondary(noLimit?'✓ Aucune limitation déclarée':'Je ne déclare aucune limitation',()=>setNoLimit(!noLimit))}
  {adult&&noLimit?action('Continuer',minimum):<AccountMessage text="Si ce cadre ne te correspond pas, tu peux revenir à Aujourd’hui sans effectuer cet essai."/>}
 </>);
 if(step==='context')return frame('Ton appareil',<>
  <Text style={type.bodyStrong}>{c.capabilities.initial_calibration_pilot?.display_name}</Text>
  <AccountMessage text="Identifie l’appareil réellement présent et son affichage. Aucun réglage de départ n’est calculé."/>
  <AccountField secureTextEntry={false} textContentType="none" autoComplete="off" label="Lieu ou contexte" value={place} onChangeText={setPlace}/>
  <AccountField secureTextEntry={false} textContentType="none" autoComplete="off" label="Appareil précis" value={device} onChangeText={setDevice}/>
  {place.trim()&&device.trim()?action('Appareil disponible · aucune préoccupation signalée',async()=>{
   const pilot=c.capabilities!.initial_calibration_pilot;if(!pilot)return;
   const context:ContextV3={canonical_exercise_id:pilot.candidate_id,realization_ref:pilot.realization_ref,context_ref:place.trim(),equipment_ref:device.trim(),side:'BILATERAL',load_semantics:'MACHINE_DISPLAY_KG'};
   await c.openCalibration(context,'AVAILABLE','CLEAR');setStep('pilot');
  }):null}
  <AccountMessage text="Si le dispositif, l’unité ou les commandes te sont inconnus : demande une aide sur place, fais une pause ou reviens plus tard."/>
 </>);
 if(step==='facts')return frame('Ton temps disponible',<>
  <AccountMessage text="Ce premier périmètre propose deux séances par semaine pour l’hypertrophie. Tu peux modifier tes préférences plus tard."/>
  <AccountField secureTextEntry={false} textContentType="none" autoComplete="off" label="Séance 1 · minutes disponibles" keyboardType="number-pad" value={budget1} onChangeText={setBudget1}/>
  <AccountField secureTextEntry={false} textContentType="none" autoComplete="off" label="Séance 2 · minutes disponibles" keyboardType="number-pad" value={budget2} onChangeText={setBudget2}/>
  {Number.isSafeInteger(Number(budget1))&&Number(budget1)>0&&Number.isSafeInteger(Number(budget2))&&Number(budget2)>0?action('Confirmer cet objectif et ces disponibilités',async()=>{
   const saved=await c.saveDeclarations({objective:{state:'KNOWN',value:'HYPERTROPHY'},sessions_per_week:{state:'KNOWN',value:2},session_budgets_minutes:{state:'KNOWN',value:[Number(budget1),Number(budget2)]}});
   if(saved){await c.evaluate();setStep('proposal');}
  }):null}
 </>);
 if(step==='pilot'){
  const encounter=c.encounter,r=encounter?.result,allowed=encounter?.allowed_actions??[],last=encounter?.progress.observations?.at(-1),factContext=encounter?.progress.context,setting={kind:'MASS_KG',value:Number(load.replace(',','.')),unit:'kg'};
  const emit=(observation:Record<string,unknown>)=>c.recordCalibration(observation);
  return frame(phases[r?.phase??'']??'Première rencontre',<>
   <Text style={type.bodyStrong}>{c.capabilities.initial_calibration_pilot?.display_name}</Text>
   <AccountMessage text={r===null?'Le guidage est indisponible. Les observations passées restent conservées.':'Tu peux t’arrêter à tout moment. Aucun essai n’est une série de travail du plan.'}/>
   {encounter?.progress.ledger_complete&&encounter.progress.observed_attempt_count!==null&&encounter.progress.observed_attempt_count>0?<AccountMessage text={`${encounter.progress.observed_attempt_count} essai observé conservé${encounter.progress.observed_attempt_count>1?'s':''}.`}/>:null}
   {last&&factContext?<View style={{gap:6}}>
    <Text selectable style={type.bodyStrong}>{last.setting?.kind==='MASS_KG'&&last.setting.value!==null?String(last.setting.value)+' kg '+(factContext.load_semantics==='PER_IMPLEMENT'?'par élément':factContext.load_semantics==='MACHINE_DISPLAY_KG'?'affichés par l’appareil':'au total'):'Réglage non massique ou inconnu'} · {last.reps===null?'Répétitions inconnues':String(last.reps)+' reps observées'}</Text>
    <Text selectable style={type.small}>{factContext.equipment_ref??'Appareil inconnu'} · {factContext.context_ref??'Contexte inconnu'}</Text>
   </View>:null}
   {r?.state==='QUALIFIED'?<AccountMessage text="Réglage provisoirement qualifié pour réessai, dans ce contexte. Cela ne termine pas à lui seul la préparation du plan."/>:null}
   {secondary(showProtocol?'Masquer les instructions':'Lire la procédure de cette rencontre',()=>setShowProtocol(!showProtocol))}
   {showProtocol?<Text selectable style={type.body}>{c.capabilities.calibration_protocol_material?.text??'Instructions indisponibles : aucune nouvelle consigne.'}</Text>:null}
   {r&&<>
    {pilotStage==='preparation'?<>
    <AccountField secureTextEntry={false} textContentType="none" autoComplete="off" label="Notice de l’appareil consultée" value={instruction} onChangeText={setInstruction} helper="Référence de la notice réellement disponible."/>
    <AccountField secureTextEntry={false} textContentType="none" autoComplete="off" label="Installation comprise" value={setup} onChangeText={setSetup} helper="Identifie tes réglages de siège, d’axe et de coussin selon cette notice."/>
    {instruction&&setup?secondary('Je comprends l’installation et peux contrôler les commandes',()=>run(async()=>{if(await emit({kind:'PREPARATION_REPORTED',instruction_ref:instruction,setup_ref:setup,understood:true,controlled:true}))setPilotStage('setting');})):null}
    </>:null}
    {pilotStage==='setting'?<>
    {allowed.includes('INITIATE_FAMILIARIZATION')?action('Découvrir l’installation sans essai chargé',()=>emit({kind:'CALIBRATION_ACTION_REQUESTED',action:'INITIATE_FAMILIARIZATION'}),'plan-v3-setup-discovery'):null}
    <AccountField secureTextEntry={false} textContentType="none" autoComplete="off" label="Réglage choisi · kg affichés par cet appareil" keyboardType="decimal-pad" value={load} onChangeText={setLoad} helper="Laisse vide tant que tu n’as pas choisi un réglage réellement présent. Ce n’est pas une masse totale calculée."/>
    {load.trim()&&Number.isFinite(setting.value)&&setting.value>=0?secondary('Confirmer ce réglage réellement disponible',()=>run(()=>emit({kind:'SETTING_CHOICE_REPORTED',setting,available:true}))):null}
    {allowed.includes('CONFIRM_CONTEXT')&&load.trim()?secondary('Appareil et réglage vérifiés',()=>run(async()=>{if(await emit({kind:'CALIBRATION_EVENT_REPORTED',event:{kind:'CONTEXT_CONFIRMED',setting}}))setPilotStage('familiar');})):null}
    </>:null}
    {pilotStage==='familiar'?<>
    {allowed.includes('INITIATE_FAMILIARIZATION')?action('Préparer et découvrir les commandes',()=>emit({kind:'CALIBRATION_ACTION_REQUESTED',action:'INITIATE_FAMILIARIZATION'})):null}
    {allowed.includes('CONFIRM_FAMILIARIZATION')?secondary('J’ai réellement terminé la familiarisation',()=>run(async()=>{if(await emit({kind:'CALIBRATION_EVENT_REPORTED',event:{kind:'FAMILIARIZATION_CONFIRMED'}}))setPilotStage('trial');})):null}
    </>:null}
    {pilotStage==='trial'&&allowed.includes('INITIATE_TRIAL')?<><AccountMessage text="Pour cet essai, viser 8–12 répétitions en gardant de la réserve selon ta compréhension. Arrête-toi plus tôt si nécessaire ; ne cherche pas l’échec."/>{action('Choisir de faire un essai',async()=>{if(await emit({kind:'CALIBRATION_ACTION_REQUESTED',action:'INITIATE_TRIAL'}))setPilotStage('observation');})}</>:null}
    {pilotStage==='observation'&&allowed.includes('RECORD_TRIAL')?<>
     <AccountMessage text="Note uniquement un essai réellement effectué. Ce formulaire ne donne pas la permission d’en refaire un. Aucun RIR n’est mesuré ici."/>
     <AccountField secureTextEntry={false} textContentType="none" autoComplete="off" label="Répétitions réellement faites" keyboardType="number-pad" value={reps} onChangeText={setReps}/>

     {secondary(completed===true?'✓ Essai terminé':'Je viens de terminer l’essai',()=>{setCompleted(true);setTrialAt(new Date().toISOString());})}
     {secondary(completed===false?'✓ Essai interrompu':'Je viens d’interrompre l’essai',()=>{setCompleted(false);setTrialAt(new Date().toISOString());})}
     {secondary(successful===true?'✓ Réussite rapportée':'Je rapporte un essai réussi',()=>setSuccessful(true))}
     {secondary(successful===false?'✓ Échec rapporté':'Je rapporte un échec',()=>setSuccessful(false))}
     {secondary(successful===null?'✓ Réussite inconnue':'Je ne peux pas conclure sur la réussite',()=>setSuccessful(null))}
     {secondary(quality==='ACCEPTABLE'?'✓ Contrôle acceptable rapporté':'Je rapporte un contrôle acceptable',()=>setQuality('ACCEPTABLE'))}
     {secondary(quality==='UNKNOWN'?'✓ Contrôle incertain':'Je ne sais pas juger le contrôle',()=>setQuality('UNKNOWN'))}
     {secondary(discomfort==='NO_CONCERN'?'✓ Aucune gêne préoccupante rapportée':'Je ne rapporte pas de gêne préoccupante',()=>setDiscomfort('NO_CONCERN'))}
     {secondary(discomfort==='CONCERN'?'✓ Préoccupation rapportée':'Je rapporte une préoccupation',()=>setDiscomfort('CONCERN'))}
     {completed!==null&&successful!==undefined&&quality&&discomfort&&reps.trim()&&Number.isSafeInteger(Number(reps))&&Number.isFinite(Date.parse(trialAt))?action('Enregistrer cet essai réel',async()=>{await emit({kind:'CALIBRATION_EVENT_REPORTED',stop_reason:discomfort==='CONCERN'?'CONCERN':successful===false?'FAILURE':completed?'COMPLETED':'USER_STOPPED',event:{kind:'ATTEMPT_OBSERVED',setting,reps:Number(reps),completed,successful,technique:quality,discomfort,occurred_at:trialAt}});setPilotStage('decision');}):null}
    </>:null}
    {pilotStage==='decision'?secondary('Vérifier le réglage actuellement choisi',()=>setPilotStage('setting')):null}
    {pilotStage!=='observation'&&allowed.includes('RECORD_TRIAL')?secondary('Noter un essai déjà réalisé',()=>setPilotStage('observation')):null}
    {allowed.includes('ACCEPT_EXACT_SETTING')&&last&&factContext&&last.event_id===encounter?.progress.observation_refs.at(-1)?action('Accepter ce réglage provisoire exact',()=>emit({kind:'CALIBRATION_EVENT_REPORTED',event:{kind:'SETTING_ACCEPTED',reference_event_id:last.event_id}})):null}
    {secondary('Signaler une préoccupation',()=>run(()=>emit({kind:'CALIBRATION_EVENT_REPORTED',event:{kind:'CONCERN_REPORTED'}})))}
    {secondary('Arrêter ce guidage',()=>run(()=>emit({kind:'ENCOUNTER_WITHDRAWN'})))}
   </>}
   {secondary('Relire la rencontre',()=>run(()=>c.readCalibration()))}
   {secondary('Poursuivre ma préparation',()=>setStep('facts'))}
  </>);
 }
 const evaluation=s?.source.evaluation as EvaluationV3|undefined,r=evaluation?.recommendation;
 if(step==='proposal'||step==='ack'){
  return frame(step==='ack'?'Ton temps, ton choix':'Ton premier plan',<>
   {!r?<AccountMessage text="La proposition reste à vérifier."/>:r.scientific_readiness!=='SCIENTIFICALLY_READY'?<>
    <AccountMessage text="Ton premier plan n’est pas encore disponible dans ce périmètre."/>
    {r.assessment.missing_fields.map(field=><Text key={field} style={type.body}>{requiredLabels[field]??'Information à vérifier'}</Text>)}
    <AccountMessage text="Le plan demande sept réalisations actuellement qualifiées. La rencontre proposée ici accompagne seulement l’extension de jambes ; aucune observation des autres exercices n’est inventée."/>
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
  {action('Découvrir un appareil',async()=>{setStep('minimum');},'plan-v3-first-calibration')}
  {s?.source.encounter_ref?secondary('Reprendre ma rencontre',()=>run(resumeCalibration),'plan-v3-resume-calibration'):null}
  {secondary('J’ai déjà des réglages qualifiés · voir mon plan',()=>run(async()=>{await c.evaluate();setStep('proposal');}),'plan-v3-open-proposal')}
  {secondary('Ajouter un réglage déjà observé',()=>setStep('observed'))}
  {secondary('Compléter mes disponibilités',()=>setStep('facts'))}
 </>);
}
