import React,{useCallback,useState} from 'react';
import {useFocusEffect} from 'expo-router';

/** Native tabs retain screens. Only the focused route may own BODY listeners. */
export function BodyTabConsumer(p:{children:React.ReactNode}){
 const [focused,setFocused]=useState(false);
 useFocusEffect(useCallback(()=>{setFocused(true);return()=>setFocused(false);},[]));
 return focused?<>{p.children}</>:null;
}
