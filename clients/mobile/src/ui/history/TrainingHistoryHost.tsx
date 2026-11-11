/** Focused, read-only native consumer. Canonical clients retain all validation. */
import React,{useCallback,useEffect,useMemo,useRef,useState} from 'react';
import {AppState,BackHandler} from 'react-native';
import type {AuthSession} from '../../auth/authSession';
import type {Transport} from '../../api/http';
import type {FirstSessionV3Client} from '../../api/firstSessionV3';
import {TrainingHistoryClient,type HistoryPeriod} from '../../api/trainingHistory';
import {TrainingHistoryResource,WeightWindowResource,type WeightWindowState} from '../../api/trainingHistoryResource';
import {WeightHistoryClient} from '../../api/weightHistory';
import {WeightHistoryResource} from '../../api/weightHistoryResource';
import {TrainingHistoryScreen} from './TrainingHistoryScreen';

type Props={auth:AuthSession;call:Transport;typed?:Pick<FirstSessionV3Client,'execution'>;timeZone?:string};
export function TrainingHistoryHost({auth,call,typed,timeZone}:Props){
 const zone=timeZone??Intl.DateTimeFormat().resolvedOptions().timeZone??'UTC';
 const sources=useMemo(()=>({history:new TrainingHistoryResource(auth,new TrainingHistoryClient(auth,call,typed)),
  weight:new WeightWindowResource(auth,new WeightHistoryResource(auth,new WeightHistoryClient(auth,call)))}),[auth,call,typed]);
 const alive=useRef(false),sequence=useRef(0),periodRef=useRef<HistoryPeriod>('4w');
 const [period,setPeriod]=useState<HistoryPeriod>('4w'),[,paint]=useState(0),[weightVisible,setWeightVisible]=useState(false),[weightFailed,setWeightFailed]=useState(false);
 const run=useCallback(async(send:()=>Promise<unknown>)=>{
  const revision=auth.revision,active=()=>alive.current&&auth.revision===revision;
  try{const task=send();if(active())paint(n=>n+1);await task;}finally{if(active())paint(n=>n+1);}
 },[auth]);
 const refresh=useCallback(async(next:HistoryPeriod=periodRef.current)=>{
  const revision=auth.revision,seq=++sequence.current,current=()=>alive.current&&auth.revision===revision&&sequence.current===seq;
  sources.weight.invalidate();periodRef.current=next;setPeriod(next);setWeightVisible(false);setWeightFailed(false);
  const reading=sources.history.refresh(next,zone);paint(n=>n+1);
  const result=await reading;if(!current())return;paint(n=>n+1);
  if(result.sessions.status!=='confirmed'||!result.sessions.value){setWeightFailed(true);return;}
  try{const task=sources.weight.refresh(result.sessions.value.window);setWeightVisible(true);paint(n=>n+1);await task;}
  catch{if(current())setWeightFailed(true);}
  finally{if(current())paint(n=>n+1);}
 },[auth,sources,zone]);
 const back=useCallback(()=>{
  const s=sources.history.state;if(s.selectedEntry===null&&s.selectedExercise===null)return false;
  sources.history.back();paint(n=>n+1);return true;
 },[sources]);
 useEffect(()=>{
  alive.current=true;void refresh();
  const foreground=AppState.addEventListener('change',state=>{if(state==='active')void refresh();});
  const hardware=BackHandler.addEventListener('hardwareBackPress',back);
  return()=>{alive.current=false;sequence.current++;sources.history.invalidate();sources.weight.invalidate();foreground.remove();hardware.remove();};
 },[refresh,back,sources]);
 const pending:WeightWindowState={status:weightFailed?'unknown':'pending',previous:false,coverage:'PARTIAL',canContinue:false,entries:[]};
 return <TrainingHistoryScreen state={sources.history.state} weight={weightVisible&&!weightFailed?sources.weight.state:pending} period={period}
  onPeriod={p=>{void refresh(p);}} onRefresh={()=>{void refresh();}} onBack={back}
  onMore={()=>{void run(()=>sources.history.nextSessions());}} onExercises={()=>{void run(()=>sources.history.loadExercises());}}
  onExercise={ref=>{void run(()=>sources.history.selectExercise(ref));}} onMoreExercises={()=>{void run(()=>sources.history.nextExercises());}}
  onOccurrence={entry=>{void run(()=>sources.history.selectOccurrence(entry));}} onMoreOccurrences={()=>{void run(()=>sources.history.nextOccurrences());}}
  onDetailExercise={(seId,ref)=>{void run(()=>sources.history.openExerciseFromDetail(seId,ref));}}
  onEntry={entry=>{void run(()=>sources.history.selectEntry(entry));}} onMoreWeight={()=>{void run(()=>sources.weight.continue());}}/>;
}
