import {useEffect,useRef,useState} from 'react';
import {AppState} from 'react-native';
import {readContext,type ContextRead,type ContextReader} from './referenceRead';
import type {ContextTarget} from './referenceModel';
/** Ephemeral view resource. No lifecycle command, time anchor or durable cache. */
export function useContextRead(reader:ContextReader,target:ContextTarget,revision:number,current:()=>boolean){
 const key=JSON.stringify([revision,target]),latest=useRef({key,current});latest.current={key,current};
 const [foreground,setForeground]=useState(AppState.currentState!=='background'&&AppState.currentState!=='inactive');
 const [attempt,setAttempt]=useState(0),[result,setResult]=useState<{key:string;value:ContextRead}|null>(null);
 const generation=useRef(0);
 useEffect(()=>{const sub=AppState.addEventListener('change',state=>{generation.current++;setResult(null);setForeground(state==='active');if(state==='active')setAttempt(n=>n+1);});return()=>sub.remove();},[]);
 useEffect(()=>{let alive=true;const gen=++generation.current;setResult(null);
  const active=()=>alive&&foreground&&gen===generation.current&&latest.current.key===key&&latest.current.current();
  if(active())void readContext(reader,target,active).then(value=>{if(active())setResult({key,value});});
  return()=>{alive=false;};
 },[reader,key,attempt,foreground]);
 return{read:foreground&&current()&&result?.key===key?result.value:null,refresh:()=>{generation.current++;setResult(null);setAttempt(n=>n+1);}};
}
