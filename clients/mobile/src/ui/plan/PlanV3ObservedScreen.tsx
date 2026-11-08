/** Recording existing facts is distinct from a permission to perform an exercise. */
import React,{useState} from 'react';
import {Text} from 'react-native';
import type {FirstUseV3Controller} from '../../api/firstUseV3';
import type {ContextV3,ObservationProgressV3} from '../../domain/planV3Types';
import {AccountFrame,AccountField,AccountLink,AccountMessage} from '../account/AccountFrame';
import {PrimaryAction} from '../components';
import type {DeclarationsV3} from '../../api/blueprintV3';
import {runtimeNoticeV3} from './PlanV3Messages';
import {type} from '../theme';
export function PlanV3ObservedScreen(p:{controller:FirstUseV3Controller;onBack:()=>void}){
 const c=p.controller,[selected,setSelected]=useState<NonNullable<typeof c.capabilities>['supported_realizations'] extends (infer T)[]|undefined?T|null:never>(null),
 [place,setPlace]=useState(''),[device,setDevice]=useState(''),[meaning,setMeaning]=useState<ContextV3['load_semantics']|null>(null),[load,setLoad]=useState(''),[reps,setReps]=useState(''),
 [phase,setPhase]=useState<'CONTEXT'|'SETTING'|'FAMILIAR'|'OBSERVATION'|'ACCEPT'>('CONTEXT'),[completed,setCompleted]=useState<boolean|null>(null),
 [successful,setSuccessful]=useState<boolean|null|undefined>(undefined),[quality,setQuality]=useState<string|null>(null),[discomfort,setDiscomfort]=useState<string|null>(null),[occurredAt,setOccurredAt]=useState<string|null>(null),[error,setError]=useState<string|null>(null);
 const run=(task:()=>Promise<unknown>)=>{void task().catch(()=>setError('La réponse reste à vérifier.'))};
 const link=(label:string,fn:()=>void)=><AccountLink disabled={c.loading} label={label} onPress={fn}/>;
 const field=(label:string,value:string,change:(value:string)=>void,numeric=false)=><AccountField label={label} value={value} onChangeText={change} secureTextEntry={false} textContentType="none" autoComplete="off" keyboardType={numeric?'decimal-pad':'default'}/>;
 const action=(label:string,task:()=>Promise<unknown>)=><PrimaryAction label={label} busy={c.loading} onPress={()=>run(task)}/>;
 const episodes=(c.state?.source.declarations as DeclarationsV3|undefined)?.observation_progress??[];
 const episode=episodes.find(e=>e.episode_ref===c.state?.source.observed_episode_ref);
 const last=episode?.events.filter(e=>e.kind==='ATTEMPT_OBSERVED').at(-1);
 const resume=async(e:ObservationProgressV3)=>{
  if(!await c.selectObservedEpisode(e.episode_ref))return;
  setSelected(c.capabilities?.supported_realizations?.find(x=>x.candidate_id===e.context.canonical_exercise_id)??null);
  const attempt=e.events.filter(x=>x.kind==='ATTEMPT_OBSERVED').at(-1),confirmed=e.events.filter(x=>x.kind==='CONTEXT_CONFIRMED').at(-1);
  const setting=attempt?.setting??confirmed?.setting;
  setLoad(setting?.value===null||setting?.value===undefined?'':String(setting.value));
  setMeaning(e.context.load_semantics);setPlace(e.context.context_ref??'');setDevice(e.context.equipment_ref??'');
  setPhase(attempt?'ACCEPT':e.events.some(x=>x.kind==='FAMILIARIZATION_CONFIRMED')?'OBSERVATION':confirmed?'FAMILIAR':'SETTING');
 };
 const setting={kind:'MASS_KG',unit:'kg',value:Number(load.replace(',','.'))};
 return <AccountFrame key={phase} title="Mes observations" onBack={p.onBack} footer={<>{error||c.notice?<AccountMessage alert text={runtimeNoticeV3(error??c.notice)!}/>:null}{link('Relire mes informations',()=>run(()=>c.load()))}{link('Retour à ma préparation',p.onBack)}</>}>
  <AccountMessage text="Consigne seulement des faits réellement observés dans le contexte indiqué. Cet écran n’accompagne pas un nouvel essai et ne propose aucune charge."/>
  {phase==='CONTEXT'?<>
   {episodes.filter(e=>e.kind==='CONTEXT_OPENED').map(e=><AccountLink key={e.episode_ref} testID={'plan-v3-resume-observed-'+e.episode_ref} disabled={c.loading}
    label={'Reprendre : '+(c.capabilities?.supported_realizations?.find(x=>x.candidate_id===e.context.canonical_exercise_id)?.display_name??'Observation')+' · '+e.context.context_ref}
    onPress={()=>run(()=>resume(e))}/>)}
   {c.capabilities?.supported_realizations?.map(item=><AccountLink key={item.candidate_id} disabled={c.loading} label={(selected?.candidate_id===item.candidate_id?'✓ ':'')+item.display_name} onPress={()=>setSelected(item)}/>)}
   {field('Lieu ou contexte',place,setPlace)}{field('Appareil ou éléments précis',device,setDevice)}
   {link(meaning==='MACHINE_DISPLAY_KG'?'✓ kg affichés par l’appareil':'kg affichés par l’appareil',()=>setMeaning('MACHINE_DISPLAY_KG'))}
   {link(meaning==='PER_IMPLEMENT'?'✓ kg par élément':'kg par élément',()=>setMeaning('PER_IMPLEMENT'))}
   {link(meaning==='TOTAL_EXTERNAL'?'✓ kg au total':'kg au total',()=>setMeaning('TOTAL_EXTERNAL'))}
   {selected&&place.trim()&&device.trim()&&meaning?action('Confirmer ce contexte disponible',async()=>{
    if(await c.openObservedContext({canonical_exercise_id:selected.candidate_id,realization_ref:selected.realization_ref,context_ref:place.trim(),equipment_ref:device.trim(),side:'BILATERAL',load_semantics:meaning}))setPhase('SETTING');
   }):null}
  </>:<><Text style={type.bodyStrong}>{selected?.display_name??'Contexte enregistré'}</Text>
   {episode?<Text selectable style={type.small}>{episode.context.equipment_ref} · {episode.context.context_ref}</Text>:null}
   {phase==='SETTING'?<>
    {field('Réglage réellement observé · kg',load,setLoad,true)}
    {load.trim()&&Number.isFinite(setting.value)&&setting.value>=0?action('Confirmer ce réglage dans ce contexte',async()=>{if(await c.recordObservedEvent({kind:'CONTEXT_CONFIRMED',setting}))setPhase('FAMILIAR');}):null}
   </>:phase==='FAMILIAR'?<>
    <AccountMessage text="La familiarisation doit réellement précéder l’essai. Une confirmation saisie après un ancien essai ne reconstruit pas sa chronologie."/>
    {action('Je confirme la familiarisation réellement faite',async()=>{if(await c.recordObservedEvent({kind:'FAMILIARIZATION_CONFIRMED'}))setPhase('OBSERVATION');})}
   </>:phase==='OBSERVATION'?<>
    {field('Répétitions réellement faites',reps,setReps,true)}
    {link(completed===true?'✓ Essai terminé maintenant':'Je viens de terminer l’essai',()=>{setCompleted(true);setOccurredAt(new Date().toISOString());})}
    {link(completed===false?'✓ Essai interrompu maintenant':'Je viens d’interrompre l’essai',()=>{setCompleted(false);setOccurredAt(new Date().toISOString());})}
    {link(successful===true?'✓ Réussite rapportée':'Je rapporte une réussite',()=>setSuccessful(true))}
    {link(successful===false?'✓ Échec rapporté':'Je rapporte un échec',()=>setSuccessful(false))}
    {link(successful===null?'✓ Réussite inconnue':'Je ne peux pas conclure sur la réussite',()=>setSuccessful(null))}
    {link(quality==='ACCEPTABLE'?'✓ Contrôle acceptable rapporté':'Je rapporte un contrôle acceptable',()=>setQuality('ACCEPTABLE'))}
    {link(quality==='UNKNOWN'?'✓ Contrôle incertain':'Je ne sais pas juger le contrôle',()=>setQuality('UNKNOWN'))}
    {link(discomfort==='NO_CONCERN'?'✓ Aucune gêne préoccupante rapportée':'Je ne rapporte pas de gêne préoccupante',()=>setDiscomfort('NO_CONCERN'))}
    {link(discomfort==='CONCERN'?'✓ Préoccupation rapportée':'Je rapporte une préoccupation',()=>setDiscomfort('CONCERN'))}
    {occurredAt&&completed!==null&&successful!==undefined&&quality&&discomfort&&reps.trim()&&Number.isSafeInteger(Number(reps))&&Number(reps)>=0?action('Enregistrer cet essai réel',async()=>{
      if(await c.recordObservedEvent({kind:'ATTEMPT_OBSERVED',setting,reps:Number(reps),completed,successful,technique:quality,discomfort,occurred_at:occurredAt}))setPhase('ACCEPT');
    }):null}
   </>:<>
    {last?.setting?.kind==='MASS_KG'&&episode?<Text selectable style={type.bodyStrong}>{last.setting.value} kg {episode.context.load_semantics==='PER_IMPLEMENT'?'par élément':episode.context.load_semantics==='MACHINE_DISPLAY_KG'?'affichés par l’appareil':'au total'} · {last.reps} reps observées</Text>:null}
    <AccountMessage text="L’enregistrement d’un essai ne le qualifie pas. L’autorité scientifique vérifiera les observations, leur chronologie et leur contexte."/>
    {last&&episode?action('Accepter ce réglage provisoire exact pour réessai',async()=>{if(await c.recordObservedEvent({kind:'SETTING_ACCEPTED',reference_event_id:last.event_id}))p.onBack();}):null}
   </>}
  </>}
 </AccountFrame>;
}
