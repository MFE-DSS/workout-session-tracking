/** MOB-05A — focused owned history; retains the shell fallback without a consumer. */
import React,{useCallback,useState} from 'react';
import {useFocusEffect} from 'expo-router';
import {useShell} from '../shell/ShellContext';

import { PendingSpace } from '../shell/PendingSpace';

export default function Progress() {
  const shell=useShell(),[focused,setFocused]=useState(false);
  useFocusEffect(useCallback(()=>{setFocused(true);return()=>setFocused(false);},[]));
  if(shell.progress)return focused?<>{shell.progress}</>:null;
  return (
    <PendingSpace
      eyebrow="AUREN · Progrès"
      title="Sur le site, pour l’instant"
      text="L’historique de tes séances, celui de chaque exercice et tes progrès mesurés arriveront ici."
      webPath="/progress"
    />
  );
}
