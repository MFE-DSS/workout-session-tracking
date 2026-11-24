import React,{useEffect,useState} from 'react';
import {AppState} from 'react-native';
import type {FirstUseV3Controller} from '../../api/firstUseV3';
import {PlanV3FirstUseScreen} from './PlanV3FirstUseScreen';
import {PlanV3ExecutionScreen,type ContextualPorts} from './PlanV3ExecutionScreen';
export function PlanV3Host(p:{controller:FirstUseV3Controller;contextual?:ContextualPorts;onExit:()=>void;onPreferences:()=>void;onSync:()=>Promise<void>}){
 const c=p.controller,hasExecution=Boolean(c.state?.execution);
 const [,paint]=useState(0);
 useEffect(()=>{if(!hasExecution)return;const timer=setInterval(()=>paint(n=>n+1),250);return()=>clearInterval(timer);},[hasExecution]);
 useEffect(()=>{
  c.setForeground(AppState.currentState==='active');
  const subscription=AppState.addEventListener('change',state=>{c.setForeground(state==='active');if(state!=='active')void c.pause();});
  return()=>subscription.remove();
 },[c]);
 return c.state?.execution?<PlanV3ExecutionScreen controller={c} contextual={p.contextual} serverNowMs={c.executionNowMs()} onExit={p.onExit} onSync={p.onSync}/>:<PlanV3FirstUseScreen controller={c} onExit={p.onExit} onPreferences={p.onPreferences}/>;
}
