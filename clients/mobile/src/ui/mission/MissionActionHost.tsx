/** Today composition only. Commands and journals remain owned by ConnectedApp. */
import React,{useRef,useState} from 'react';
import {Text,View} from 'react-native';
import type {MissionAction,MissionPath} from '../../api/missionAction';
import type {MissionResourceState} from '../../api/missionActionResource';
import {AccountFrame} from '../account/AccountFrame';
import {CalibrationAction,CalibrationLink} from '../plan/calibrationControls';
import {type} from '../theme';

export type MissionActionHostProps={
 read:MissionResourceState;path:MissionPath;checking?:boolean;refusal?:string|null;offline?:boolean;onReadOwned?:()=>Promise<void>;
 local:{kind:'START'|'CLOSE'|'SOURCE'}|null;
 onAction:(action:MissionAction)=>Promise<void>;
 onVerify:()=>Promise<void>;onSelectPath:(path:MissionPath)=>void;onOpenJournal:()=>void;
 /** The unchanged MISSION consumer occupies its existing full layout. */
 historical:React.ReactNode;
};
type Orientation={title:string;fact:string;label:string;detail:string;action:MissionAction|null;pending?:boolean};
function orientation(p:MissionActionHostProps):Orientation {
 if(p.local)return{title:'Réception à vérifier',fact:p.local.kind==='START'?'La création de ta séance reste à vérifier.':p.local.kind==='CLOSE'?'La clôture de ta séance reste à vérifier.':'Une action de ton parcours attend sa confirmation.',
  label:'Vérifier',detail:'Les informations et la demande restent conservées sur cet appareil. Vérifier ne crée pas une nouvelle demande.',action:null};
 if(p.refusal)return{title:'Démarrage refusé',fact:p.refusal,label:'Actualiser',detail:'Aucune création n’est confirmée. Le journal reste disponible.',action:null};
 const r=p.read;
 if(r.state==='idle'&&p.offline)return{title:'À vérifier',fact:'Hors ligne. Ton parcours reste à relire.',label:'Actualiser',detail:'Aucune vérification n’est en cours. Réessaie lorsque la connexion revient.',action:null};
 if(r.state==='idle'||r.state==='pending')return{title:'Un instant',fact:'Vérification de ton parcours.',label:'Vérification…',detail:'Aucune nouvelle séance n’est lancée pendant cette lecture.',action:null,pending:true};
 if(r.state!=='confirmed')return{title:'À vérifier',fact:r.state==='rejected'&&r.status===401?'Reconnecte ton compte pour continuer.':'Le parcours n’a pas pu être confirmé.',
  label:'Actualiser',detail:'Une réponse manquante ne signifie pas qu’aucune séance existe. Ton journal reste disponible.',action:null};
 const x=r.value;
 if(x.state==='FIRST_USE')return{title:'Première séance',fact:'Retrouve ton parcours de préparation.',label:'Continuer',
  detail:'Le parcours existant recueille tes informations et tes observations. Son ouverture ne confirme ni un plan ni une charge.',action:x};
 if(x.state==='RESUME'){
  if(p.offline)return{title:'Reprise à vérifier',fact:'La lecture de ta séance attend une connexion.',label:'Reprendre',detail:'La séance enregistrée reste disponible dans ton compte. Sa position et ses conditions seront relues avant la reprise.',action:x};
  const pos=x.payload.position;
  return{title:'Séance en cours',fact:x.payload.session.name,label:'Reprendre',
   detail:pos?`${pos.sets_done} sur ${pos.sets_total} séries enregistrées. La reprise relit la séance et ses conditions actuelles.`:'La séance et ta position seront relues avant la reprise.',action:x};
 }
 if(x.state==='FIRST_SESSION_HISTORY')return{title:'Ta première séance',fact:x.payload.session.name,label:'Lire la séance',
  detail:'Cette séance est conservée dans ton compte. La consulter ne lance pas une autre première séance.',action:x};
 if(x.state==='CONFLICT')return{title:'Séances à vérifier',fact:'Plusieurs séances ouvertes sont enregistrées.',label:'Actualiser',
  detail:'Aucune séance n’est choisie automatiquement. Le journal reste accessible.',action:null};
 if(x.state==='NO_MISSION')return{title:'Rien à proposer',fact:'Aucune séance historique n’est disponible aujourd’hui.',label:'Actualiser',
  detail:'Aucun autre plan ou équipement n’est supposé disponible.',action:null};
 return{title:'Parcours indisponible',fact:x.state==='UNAVAILABLE'&&x.reason==='EXECUTION_PROFILE_REQUIRED'?'Cette séance demande un format d’exécution indisponible ici.':'La disponibilité de ce parcours reste à vérifier.',label:'Actualiser',
  detail:'Tu peux consulter ton journal. Une indisponibilité ne déclenche pas un autre parcours.',action:null};
}
export function MissionActionHost(p:MissionActionHostProps){
 // No wrapper changes the locked MISSION geometry, including its measured zones.
 if(!p.local&&!p.refusal&&p.read.state==='confirmed'&&p.read.value.state==='HISTORICAL_READY')return p.historical;
 return <MissionOrientation {...p}/>;
}
function MissionOrientation(p:MissionActionHostProps){
 const [details,setDetails]=useState(false),[busy,setBusy]=useState(false),flight=useRef(false),view=orientation(p);
 const submit=async()=>{
  if(flight.current||view.pending||p.checking)return;
  flight.current=true;setBusy(true);
  try{if(view.action)await p.onAction(view.action);else await p.onVerify();}
  finally{flight.current=false;setBusy(false);}
 };
 return <AccountFrame title={view.title} footer={<>
  <CalibrationAction testID="mission-action-primary" label={view.label} busy={busy||view.pending||p.checking} onPress={()=>void submit()}/>
  {!p.local?<CalibrationLink testID="mission-action-other" label={p.path==='FIRST_USE'?'Autres parcours':'Premier parcours'} onPress={()=>p.onSelectPath(p.path==='FIRST_USE'?'HISTORICAL':'FIRST_USE')} disabled={busy}/>:null}
  {p.onReadOwned?<CalibrationLink testID="mission-action-read-owned" label="Lire la séance enregistrée" onPress={()=>void p.onReadOwned?.()}/>:null}
  <CalibrationLink testID="mission-action-journal" label="Journal" onPress={p.onOpenJournal}/>
 </>}>
  <Text accessibilityLiveRegion="polite" style={type.bodyStrong}>{view.fact}</Text>
  <CalibrationLink testID="mission-action-details" label="Détails" expanded={details} onPress={()=>setDetails(!details)}/>
  {details?<View testID="mission-action-detail"><Text style={type.small}>{view.detail}</Text></View>:null}
 </AccountFrame>;
}
