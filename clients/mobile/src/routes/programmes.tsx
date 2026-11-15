/** Keep the visited owned workspace alive across tabs; inactive controls do not capture Back. */
import React,{useCallback,useState} from 'react';
import {View} from 'react-native';
import {useRouter,useFocusEffect} from 'expo-router';
import {useShell} from '../shell/ShellContext';
import {PendingSpace} from '../shell/PendingSpace';
export default function Programs(){
 const shell=useShell(),router=useRouter(),[focused,setFocused]=useState(false),[visited,setVisited]=useState(false);
 useFocusEffect(useCallback(()=>{setVisited(true);setFocused(true);return()=>setFocused(false);},[]));
 return shell.programmes?visited?<View style={{flex:1,display:focused?'flex':'none'}} accessibilityElementsHidden={!focused} importantForAccessibility={focused?'auto':'no-hide-descendants'}>{shell.programmes(()=>router.replace('/'),focused)}</View>:null:<PendingSpace eyebrow="AUREN · Programmes" title="Bibliothèque indisponible" text="Le journal propriétaire doit être connecté avant d’ouvrir les programmes." webPath="/library"/>;
}
