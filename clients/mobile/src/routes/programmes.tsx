/** Owned native library; the connected owner supplies journal and recovery. */
import React,{useCallback,useState} from 'react';
import {useRouter,useFocusEffect} from 'expo-router';
import {useShell} from '../shell/ShellContext';
import {PendingSpace} from '../shell/PendingSpace';
export default function Programs(){
 const shell=useShell(),router=useRouter(),[focused,setFocused]=useState(false);
 useFocusEffect(useCallback(()=>{setFocused(true);return()=>setFocused(false);},[]));
 return shell.programmes?focused?shell.programmes(()=>router.replace('/')):null:<PendingSpace eyebrow="AUREN · Programmes" title="Bibliothèque indisponible" text="Le journal propriétaire doit être connecté avant d’ouvrir les programmes." webPath="/library"/>;
}
