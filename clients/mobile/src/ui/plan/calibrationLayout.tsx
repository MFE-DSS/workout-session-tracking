/** Integrity checked, read-only help for the actual selected owner/context. */
import React,{useEffect,useRef,useState} from 'react';
import {AccessibilityInfo,BackHandler,findNodeHandle,Modal,ScrollView,Text,View} from 'react-native';
import {useSafeAreaInsets} from 'react-native-safe-area-context';
import type {FirstUseV3Controller} from '../../api/firstUseV3';
import {type,color} from '../theme';
import {CalibrationLink} from './calibrationControls';
import {projectCalibrationHelp,type CalibrationHelpProjection,type CalibrationHelpStage} from './calibrationHelp';
function focus(target:any){target?.focus?.();const handle=target&&findNodeHandle(target);if(handle)AccessibilityInfo.setAccessibilityFocus(handle);}
export function CalibrationHelp(p:{controller:FirstUseV3Controller;candidate:string|null;stage?:CalibrationHelpStage;scopeKey:string}){
 const c=p.controller,insets=useSafeAreaInsets(),[open,setOpen]=useState(false),[help,setHelp]=useState<CalibrationHelpProjection|null>(null),trigger=useRef<any>(null),heading=useRef<any>(null);
 const caps=c.capabilities,owner=c.state?.owner_id,encounter=c.encounter?.encounter_ref,authority=c.encounter?.authority,revision=c.encounter?.source_revision;
 const context=JSON.stringify(c.encounter?.progress.context);
 const identity=JSON.stringify([owner,encounter,revision,context,p.candidate,p.stage,p.scopeKey]);
 const [displayIdentity,setDisplayIdentity]=useState('');
 const resolved=useRef<{caps:typeof caps;authority:typeof authority;identity:string}|null>(null);
 const close=()=>{setOpen(false);setHelp(null);focus(trigger.current);};
 useEffect(()=>{setOpen(false);setHelp(null);},[identity,caps,authority]);
 useEffect(()=>{
  if(!open)return;
  let current=true;setHelp(null);setDisplayIdentity(identity);
  void projectCalibrationHelp(caps,p.candidate,p.stage).then(value=>{
   if(current&&c.active!==false&&c.capabilities===caps&&c.state?.owner_id===owner&&c.encounter?.encounter_ref===encounter&&c.encounter?.authority===authority&&c.encounter?.source_revision===revision&&JSON.stringify(c.encounter?.progress.context)===context){resolved.current={caps,authority,identity};setHelp(value);}
  });
  return ()=>{current=false;};
 },[open,identity,caps,authority,c,p.candidate,p.stage,owner,encounter,revision,context]);
 useEffect(()=>{if(!open)return;const sub=BackHandler.addEventListener('hardwareBackPress',()=>{close();return true;});return ()=>sub.remove();},[open]);
 const visible=open&&displayIdentity===identity&&c.active!==false;
 const currentHelp=resolved.current?.caps===caps&&resolved.current?.authority===authority&&resolved.current?.identity===identity?help:null;
 const sections=currentHelp?.state==='available'?[...currentHelp.sections.filter(s=>currentHelp.primarySectionIds.includes(s.id)),...currentHelp.sections.filter(s=>!currentHelp.primarySectionIds.includes(s.id))]:[];
 return <>
  <CalibrationLink inputRef={trigger} testID="calibration-help-open" label="Aide" expanded={visible} onPress={()=>setOpen(true)}/>
  <Modal visible={visible} animationType="none" onRequestClose={close} onShow={()=>focus(heading.current)} onDismiss={()=>focus(trigger.current)}>
   <ScrollView contentContainerStyle={{paddingHorizontal:20,paddingTop:insets.top+12,paddingBottom:insets.bottom+12,gap:16,backgroundColor:color.field}} accessibilityViewIsModal>
    <Text ref={heading} accessibilityRole="header" style={type.title}>Procédure applicable</Text>
    <CalibrationLink testID="calibration-help-close" label="Fermer l’aide" onPress={close}/>
    {!currentHelp?<Text accessibilityLiveRegion="polite" style={type.body}>Vérification de la procédure…</Text>:currentHelp.state==='unavailable'?<Text accessibilityLiveRegion="polite" style={type.body}>Procédure indisponible. Aucune nouvelle consigne ; tes faits sont conservés.</Text>:<>
     {sections.map(section=><Text key={section.id} testID="calibration-help-section" selectable style={type.body}>{section.text}</Text>)}
     <View><Text selectable style={type.small}>{currentHelp.source_ref}</Text></View>
    </>}
   </ScrollView>
  </Modal>
 </>;
}
