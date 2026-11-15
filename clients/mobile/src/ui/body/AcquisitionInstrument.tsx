import React,{useState,useRef} from 'react';
import {Modal,KeyboardAvoidingView,ScrollView,View,Text,TextInput,Keyboard,Platform,InputAccessoryView,useWindowDimensions} from 'react-native';
import {SafeAreaProvider,SafeAreaView} from 'react-native-safe-area-context';
import type {BodyEntry,BodySpec} from '../../api/bodyMeasurements';
import {measurementValues,measurementLabel,type BodyForm} from './measurementInputModel';
import {bodyNumber,bodyDay} from './bodyCockpitModel';
import {color,type} from '../theme';
import {keyboardAvoidance} from '../../native/platformUi';
import {InstrumentSurface} from './InstrumentSurface';
import {EmbeddedAction} from './EmbeddedAction';
export type AcquisitionProps={specs:BodySpec[];initial?:BodyEntry;reference?:BodyEntry;busy:boolean;onSave:(f:BodyForm)=>void;onClose:()=>void};
export function AcquisitionInstrument(p:AcquisitionProps){
 const spec=p.specs[0],{fontScale}=useWindowDimensions(),large=fontScale>=1.25;
 const [value,setValue]=useState(''),[day,setDay]=useState(''),[leave,setLeave]=useState(false),[help,setHelp]=useState(false),input=useRef<React.ComponentRef<typeof TextInput>>(null);
 let values:BodyForm['values']={},valid=true;try{values=measurementValues(p.specs,{[spec.key]:value},{},undefined);}catch{valid=false;}
 const validDay=/^\d{4}-\d{2}-\d{2}$/.test(day)&&Number.isFinite(Date.parse(day+'T00:00:00Z'))&&new Date(day+'T00:00:00Z').toISOString().slice(0,10)===day&&day<=new Date().toISOString().slice(0,10),save=valid&&validDay&&Object.keys(values).length>0;
 const close=()=>{if(p.busy)return;if(value||day)setLeave(true);else p.onClose();};
 return <Modal visible transparent presentationStyle="overFullScreen" animationType="none" onRequestClose={close} accessibilityViewIsModal><SafeAreaProvider style={{backgroundColor:color.field}}><SafeAreaView testID="body-acquisition-safe-surface" edges={['top','bottom','left','right']} style={{flex:1}}><KeyboardAvoidingView style={{flex:1,backgroundColor:color.field}} behavior={keyboardAvoidance.behavior}><ScrollView keyboardShouldPersistTaps="handled" contentInsetAdjustmentBehavior="never" contentContainerStyle={{paddingTop:16,paddingHorizontal:20,paddingBottom:12,gap:20}}>
 <View style={{flexDirection:large?'column':'row',justifyContent:'space-between',alignItems:large?'stretch':'center',gap:8}}><Text style={type.eyebrow}>BODY / acquisition</Text><EmbeddedAction label="Fermer" onPress={close} disabled={p.busy}/></View>
 {leave?<View style={{gap:12}}><Text style={type.bodyStrong}>Quitter sans enregistrer ?</Text><Text style={type.small}>Ce brouillon n’a pas été envoyé.</Text><EmbeddedAction testID="body-keep-draft" label="Garder le brouillon" onPress={()=>setLeave(false)}/><EmbeddedAction label="Quitter sans enregistrer" onPress={p.onClose}/></View>:<>
 <InstrumentSurface label={measurementLabel(spec.label)} state="Brouillon" editing action={<Text style={[type.bodyStrong,{color:color.ink2}]}>{spec.unit}</Text>}><TextInput ref={input} testID={`body-value-${spec.key}`} accessibilityLabel={`${measurementLabel(spec.label)}, ${spec.unit}`} value={value} onChangeText={setValue} keyboardType="decimal-pad" inputMode="decimal" placeholder="—" placeholderTextColor={color.ink3} editable={!p.busy} selectionColor={color.signal} returnKeyType="done" inputAccessoryViewID={Platform.OS==='ios'?'body-acquisition-done':undefined} onSubmitEditing={()=>Keyboard.dismiss()} maxFontSizeMultiplier={1.25} style={[type.figure,{minHeight:64,paddingVertical:0,fontSize:value.length>9?30:40}]}/></InstrumentSurface>
 <View style={{gap:8}}><Text style={type.eyebrow}>Jour déclaré</Text><View style={{flexDirection:large?'column':'row',alignItems:large?'stretch':'center',gap:12}}><TextInput testID="body-day" accessibilityLabel="Jour de mesure, année mois jour" value={day} onChangeText={setDay} placeholder="AAAA-MM-JJ" placeholderTextColor={color.ink3} autoCapitalize="none" autoCorrect={false} editable={!p.busy} onSubmitEditing={()=>input.current?.focus()} style={[type.bodyStrong,{minHeight:48,flex:large?undefined:1,borderBottomWidth:1,borderColor:color.line}]}/><EmbeddedAction label="Aujourd’hui" disabled={p.busy} onPress={()=>setDay(new Date().toISOString().slice(0,10))}/></View></View>
 {p.reference?<Text testID="body-acquisition-reference" style={type.small}>Référence · {p.reference.fields[spec.key].value==null?'inconnue':bodyNumber(p.reference.fields[spec.key].value!)} {spec.unit} · {bodyDay(p.reference.date_precision==='DAY_UTC_CONVENTION'?p.reference.measured_at.slice(0,10):null)}</Text>:null}
 {!valid?<Text accessibilityLiveRegion="polite" style={[type.small,{color:color.alert}]}>Vérifier la valeur et son unité</Text>:null}
 <View style={{flexDirection:large?'column':'row',justifyContent:'space-between',borderTopWidth:1,borderColor:color.line,paddingTop:8}}><EmbeddedAction label="Annuler" testID="body-cancel" onPress={close} disabled={p.busy}/><EmbeddedAction label={p.busy?'Confirmation…':'Enregistrer →'} testID="body-save" active disabled={!save||p.busy} onPress={()=>{Keyboard.dismiss();p.onSave({values,measured_on:day});}}/></View>
 <EmbeddedAction label="Source / aide" onPress={()=>setHelp(!help)}/>{help?<Text style={type.small}>Saisie personnelle · jour déclaré selon le calendrier UTC. Une confirmation serveur enregistre le relevé ; elle ne valide pas scientifiquement la mesure.</Text>:null}
 </>}
 </ScrollView></KeyboardAvoidingView>{Platform.OS==='ios'?<InputAccessoryView nativeID="body-acquisition-done"><View style={{backgroundColor:color.field,alignItems:'flex-end',paddingHorizontal:20}}><EmbeddedAction label="Terminé" onPress={()=>Keyboard.dismiss()}/></View></InputAccessoryView>:null}</SafeAreaView></SafeAreaProvider></Modal>;
}
