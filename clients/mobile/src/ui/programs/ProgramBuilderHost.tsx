/** Ports are borrowed from the owned journal; this host creates no account or database. */
import React,{useCallback,useEffect,useMemo,useRef,useState} from 'react';
import {AppState,BackHandler,Keyboard,Text,View} from 'react-native';
import {ProgramBuilderController,type ProgramBuilderPorts} from './ProgramBuilderController';
import {ProgramBuilderScreen} from './ProgramBuilderScreen';
import {EmbeddedAction} from '../body/EmbeddedAction';
import {color,space,type} from '../theme';
export type {ProgramBuilderPorts} from './ProgramBuilderController';
export function ProgramBuilderHost(p:{ports:ProgramBuilderPorts;onBack:()=>void;active?:boolean}){
 const focused=useRef(p.active!==false);focused.current=p.active!==false;
 const alive=useRef(false),keyboard=useRef(false),onBack=useRef(p.onBack);onBack.current=p.onBack;
 const [,paint]=useState(0),[leave,setLeave]=useState(false),leaveRef=useRef(false);
 const c=useMemo(()=>new ProgramBuilderController({...p.ports,current:()=>alive.current&&p.ports.current()},()=>{if(alive.current)paint(n=>n+1);}),[p.ports]);
 const exit=useCallback(()=>{if(c.state.view==='index')onBack.current();else{c.index();void c.refresh();}},[c]);
 const back=useCallback(()=>{
  if(!focused.current)return false;
  if(keyboard.current){keyboard.current=false;Keyboard.dismiss();return true;}
  if(c.state.busy)return true;
  if(leaveRef.current){leaveRef.current=false;setLeave(false);return true;}
  if(c.state.confirm){c.cancelConfirmation();return true;}
  if(c.state.picker){c.closePicker();return true;}
  if(c.dirty()){leaveRef.current=true;setLeave(true);return true;}
  exit();return true;
 },[c,exit]);
 useEffect(()=>{
  alive.current=true;void c.refresh();
  const foreground=AppState.addEventListener('change',state=>{if(state==='active'&&focused.current)void c.refresh();});
  const hardware=BackHandler.addEventListener('hardwareBackPress',back);
  const shown=Keyboard.addListener('keyboardDidShow',()=>{keyboard.current=true;}),hidden=Keyboard.addListener('keyboardDidHide',()=>{keyboard.current=false;});
  return()=>{alive.current=false;c.dispose();foreground.remove();hardware.remove();shown.remove();hidden.remove();};
 },[c,back]);
 const wasActive=useRef(p.active!==false);
 useEffect(()=>{const previous=wasActive.current;wasActive.current=p.active!==false;if(!previous&&wasActive.current)void c.refresh();},[p.active,c]);
 if(leave)return <View testID="builder-leave" style={{flex:1,backgroundColor:color.field,padding:space.gutter,justifyContent:'center',gap:12}}><Text accessibilityRole="header" style={type.bodyStrong}>Quitter ce brouillon ?</Text><Text style={type.small}>Les modifications non envoyées seront perdues. Une commande à vérifier reste conservée sur cet appareil ; quitter ne l’annule pas sur le serveur.</Text><EmbeddedAction testID="builder-stay" label="Garder le brouillon" onPress={()=>{leaveRef.current=false;setLeave(false);}}/><EmbeddedAction testID="builder-leave-confirm" label="Quitter les modifications non envoyées" onPress={()=>{leaveRef.current=false;setLeave(false);exit();}}/></View>;
 return <ProgramBuilderScreen controller={c} onBack={back}/>;
}
