/** One native instrument, reused for every actual calibration context. */
import React,{useState} from 'react';
import {InputAccessoryView,Keyboard,Platform,Text,TextInput,View,useWindowDimensions} from 'react-native';
import {InstrumentFrameC} from '../instrument/InstrumentFrame';
import {RecessedWindow} from '../instrument/RecessedWindow';
import {NumericReadout} from '../instrument/NumericReadout';
import {frameGeometry} from '../instrument/frameGeometry';
import {recessedWindowGeometry} from '../instrument/recessedWindowGeometry';
import {densityFor,UNIT} from '../calibration/layout';
import {color,type} from '../theme';
import {parseCalibrationMass,calibrationUnit} from './calibrationModel';
import {CalibrationLink} from './calibrationControls';

export function CalibrationInstrument(p:{name:string;status:string;children:React.ReactNode}){
 const {width}=useWindowDimensions(),w=width-40,u=UNIT[densityFor(w)],[h,setH]=useState(240);
 return <InstrumentFrameC width={w} height={h} testID="calibration-instrument">
  <View onLayout={e=>{const needed=Math.ceil(e.nativeEvent.layout.height)+7*u;if(Math.abs(h-needed)>1)setH(needed);}} style={{gap:16}}>
   <Text style={type.bodyStrong}>{p.name}</Text>
   <Text accessibilityLiveRegion="polite" style={type.small}>{p.status}</Text>
   {p.children}
  </View>
 </InstrumentFrameC>;
}
export function CalibrationSetting(p:{value:string;onChange:(v:string)=>void;semantics:string|undefined;editing:boolean;label?:string;disabled?:boolean;onDone:()=>void}){
 const {width}=useWindowDimensions(),outer=width-40,u=UNIT[densityFor(outer)],[contentHeight,setContentHeight]=useState(0);
 const w=frameGeometry('rail',outer,240,u).content.w,h=Math.max(112,contentHeight+4.5*u);
 const inner=recessedWindowGeometry(w,h,u).content.w,entered=parseCalibrationMass(p.value);
 return <RecessedWindow width={w} height={h} u={u} testID="calibration-setting-window">
  <View style={{flex:1,justifyContent:'center'}}><View onLayout={e=>setContentHeight(Math.ceil(e.nativeEvent.layout.height))} style={{gap:4}}>
   <Text style={type.eyebrow}>{p.label??(p.editing?'Ton choix de réglage':'Réglage saisi')}</Text>
   {p.editing?<TextInput accessibilityLabel={(p.label??'Réglage réellement choisi')+' · '+calibrationUnit(p.semantics)} testID="calibration-setting-input" editable={!p.disabled} value={p.value} onChangeText={p.onChange}
    keyboardType="decimal-pad" returnKeyType="done" inputAccessoryViewID={Platform.OS==='ios'?'calibration-decimal-done':undefined} onSubmitEditing={()=>{Keyboard.dismiss();p.onDone();}} autoCorrect={false} placeholder="—" placeholderTextColor={color.ink3}
    style={[type.figure,{color:color.ink,minHeight:44,paddingVertical:0,width:inner}]} />:
    <NumericReadout testID="calibration-setting-value" value={entered===null?'—':String(entered.value)} role={type.figure} />}
   <Text style={type.small}>{calibrationUnit(p.semantics)}</Text>
  </View></View>
  {p.editing&&Platform.OS==='ios'?<InputAccessoryView nativeID="calibration-decimal-done"><View style={{backgroundColor:color.field,paddingHorizontal:20,alignItems:'flex-end'}}><CalibrationLink label="Terminé" onPress={()=>{Keyboard.dismiss();p.onDone();}}/></View></InputAccessoryView>:null}
 </RecessedWindow>;
}
