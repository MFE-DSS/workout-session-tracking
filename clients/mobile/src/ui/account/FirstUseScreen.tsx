import React, { useEffect, useState } from 'react';
import { FirstUseController, type FirstUseState } from '../../api/firstUse';
import { PrimaryAction } from '../components';
import { AccountFrame, AccountLink, AccountMessage } from './AccountFrame';

type Actions={onPreferences:()=>void;onToday:()=>void;onBack:()=>void};
export function FirstUseContent(p:Actions&{state:FirstUseState;onReload:()=>void}){
 const state=p.state;
 const message=state.state==='loading'?'Un instant.'
  :state.state==='no_plan_producer'?'Ton premier plan personnalisé n’est pas encore disponible.'
  :state.state==='missing_information'?'Quelques informations sont encore nécessaires.'
  :state.state==='required_consent'?'Ton accord est nécessaire pour ce traitement. Il n’est pas activé ici.'
  :state.state==='unknown'?'La réponse n’a pas pu être confirmée.'
  :'Ton premier plan n’est pas disponible pour le moment.';
 const editable=state.state==='no_plan_producer'||state.state==='missing_information'&&state.missing.includes('sessions_per_week');
 return <AccountFrame title="Ton premier entraînement" onBack={p.onBack} footer={<>
   {state.state==='loading'?<PrimaryAction label="Vérification…" busy onPress={()=>{}}/>
    :editable?<PrimaryAction testID="first-use-preferences" label="Mes préférences" onPress={p.onPreferences}/>
    :state.state!=='required_consent'?<PrimaryAction testID="first-use-reload" label="Vérifier à nouveau" onPress={p.onReload}/>:null}
   <AccountLink testID="first-use-today" label="Voir Aujourd’hui" onPress={p.onToday}/>
  </>}>
  <AccountMessage text={message}/>
 </AccountFrame>;
}
export function FirstUseScreen(p:Actions&{controller:Pick<FirstUseController,'state'|'subscribe'|'load'|'invalidate'>}){
 const [view,setView]=useState({source:p.controller,state:p.controller.state});
 useEffect(()=>{
  let active=true;const update=()=>{if(active)setView({source:p.controller,state:p.controller.state});};
  const stop=p.controller.subscribe(update);update();void p.controller.load();
  return()=>{active=false;stop();p.controller.invalidate();};
 },[p.controller]);
 return <FirstUseContent {...p} state={view.source===p.controller?view.state:p.controller.state} onReload={()=>{void p.controller.load();}}/>;
}
