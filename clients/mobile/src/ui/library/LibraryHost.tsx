/** Native library consumer; parent retains owned journal and execution controllers. */
import React,{useCallback,useEffect,useMemo,useRef,useState} from 'react';
import {AppState,BackHandler} from 'react-native';
import {LibraryResource} from '../../api/libraryResource';
import type {LibraryQuery} from '../../api/library';
import {LibraryOpeningController,type LibraryOpeningPorts} from '../../sync/libraryOpening';
import type {LibrarySessionIdentity} from '../../storage/libraryPendingOpenings';
import {LibraryScreen} from './LibraryScreen';
import {ProgramBuilderHost,type ProgramBuilderPorts} from '../programs/ProgramBuilderHost';
export function LibraryHost(p:{onOpened?:()=>void;ports:LibraryOpeningPorts;existingSession?:LibrarySessionIdentity|null;onResumeExisting:()=>void;builderPorts?:ProgramBuilderPorts;active?:boolean}){
 const focused=useRef(p.active!==false);focused.current=p.active!==false;
 const alive=useRef(false),query=useRef<LibraryQuery>({section:'all',zone:null});
 const [builder,setBuilder]=useState(false),builderActive=useRef(false);
 const [hostFailed,setHostFailed]=useState(false),[,paint]=useState(0);
 const sources=useMemo(()=>({resource:new LibraryResource(p.ports.client),opening:new LibraryOpeningController(p.ports)}),[p.ports]);
 const run=useCallback(async(task:()=>Promise<unknown>)=>{
  const revision=p.ports.client.auth.revision,current=()=>alive.current&&revision===p.ports.client.auth.revision;
  try{const pending=task();if(current())paint(n=>n+1);await pending;}
  catch{if(current())setHostFailed(true);}
  finally{if(current())paint(n=>n+1);}
 },[p.ports]);
 const refresh=useCallback(async()=>{
  if(!focused.current||sources.opening.inFlight||builderActive.current)return;
  setHostFailed(false);await run(async()=>{await sources.opening.hydrate();if(alive.current)await sources.resource.refresh(query.current);});
 },[run,sources]);
 const back=useCallback(()=>{
  if(!focused.current||builderActive.current)return false;
  if(sources.resource.state.view==='INDEX')return false;
  void run(()=>sources.resource.back());return true;
 },[run,sources]);
 useEffect(()=>{
  alive.current=true;void refresh();
  const foreground=AppState.addEventListener('change',state=>{if(state==='active')void refresh();});
  const hardware=BackHandler.addEventListener('hardwareBackPress',back);
  return()=>{alive.current=false;sources.resource.invalidate();sources.opening.dispose();foreground.remove();hardware.remove();};
 },[sources,refresh,back]);
 const wasActive=useRef(p.active!==false);
 useEffect(()=>{const previous=wasActive.current;wasActive.current=p.active!==false;if(!previous&&wasActive.current)void refresh();},[p.active,refresh]);
 const phase=sources.opening.state.phase,notified=useRef<LibraryOpeningController|null>(null);
 useEffect(()=>{
  if(p.active===false)return;
  if(phase!=='created'&&phase!=='resumed'){notified.current=null;return;}
  if(notified.current!==sources.opening){notified.current=sources.opening;p.onOpened?.();}
 },[phase,p.onOpened,sources.opening,p.active]);
 if(builder&&p.builderPorts)return <ProgramBuilderHost active={p.active} ports={p.builderPorts} onBack={()=>{builderActive.current=false;setBuilder(false);void refresh();}}/>;
 return <LibraryScreen state={sources.resource.state} opening={hostFailed?{phase:'unavailable'}:sources.opening.state} query={query.current}
  onBuilder={p.builderPorts?()=>{builderActive.current=true;setBuilder(true);}:undefined}
  existingSession={p.existingSession} onResumeExisting={p.onResumeExisting}
  onFilter={section=>{query.current={section,zone:null};void refresh();}} onRefresh={()=>{void refresh();}}
  onMore={()=>{void run(()=>sources.resource.next());}} onSelect={ref=>{void run(()=>sources.resource.select(ref));}} onBack={back}
  onAskStart={()=>{sources.resource.confirm();paint(n=>n+1);}}
  onConfirm={()=>{const selected=sources.resource.selection();if(sources.resource.state.view==='CONFIRM'&&selected)void run(()=>sources.opening.submit(selected,()=>alive.current&&sources.resource.selectionCurrent(selected)));}}
  onVerify={()=>{void run(()=>sources.opening.verify());}} onResume={()=>{void run(()=>sources.opening.resume());}}
  onCancel={confirmed=>{void run(()=>sources.opening.cancel(confirmed));}}/>;
}
