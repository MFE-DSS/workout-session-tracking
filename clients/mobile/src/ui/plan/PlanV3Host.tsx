import React,{useEffect,useRef,useState} from 'react';
import {AppState} from 'react-native';
import type {FirstUseV3Controller} from '../../api/firstUseV3';
import {PlanV3FirstUseScreen} from './PlanV3FirstUseScreen';
import {PlanV3ExecutionScreen} from './PlanV3ExecutionScreen';
export function PlanV3Host(p:{controller:FirstUseV3Controller;onExit:()=>void;onPreferences:()=>void;onSync:()=>Promise<void>}){
 const c=p.controller,serverTime=c.state?.execution?.server_now;
 const anchor=useRef({server:NaN,mono:0}),[now,setNow]=useState(NaN);
 useEffect(()=>{if(!serverTime)return;anchor.current={server:Date.parse(serverTime),mono:performance.now()};setNow(anchor.current.server);},[serverTime]);
 useEffect(()=>{const timer=setInterval(()=>setNow(anchor.current.server+performance.now()-anchor.current.mono),250);return()=>clearInterval(timer);},[]);
 useEffect(()=>{const subscription=AppState.addEventListener('change',state=>{if(state!=='active')void c.pause();});return()=>subscription.remove();},[c]);
 return c.state?.execution?<PlanV3ExecutionScreen controller={c} serverNowMs={now} onExit={p.onExit} onSync={p.onSync}/>:<PlanV3FirstUseScreen controller={c} onExit={p.onExit} onPreferences={p.onPreferences}/>;
}
