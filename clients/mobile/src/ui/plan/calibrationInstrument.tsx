/** One native instrument, reused for every actual calibration context. */
import React,{useState} from 'react';
import {Text,TextInput,View,useWindowDimensions} from 'react-native';
import {InstrumentFrameC} from '../instrument/InstrumentFrame';
import {RecessedWindow} from '../instrument/RecessedWindow';
import {NumericReadout} from '../instrument/NumericReadout';
import {frameGeometry} from '../instrument/frameGeometry';
import {recessedWindowGeometry} from '../instrument/recessedWindowGeometry';
import {densityFor,UNIT} from '../calibration/layout';
import {color,type} from '../theme';
import {parseCalibrationMass,calibrationUnit} from './calibrationModel';

export function CalibrationInstrument(p:{name:string;status:string;children:React.ReactNode}){
 const {width}=useWindowDimensions(),w=width-40,u=UNIT[densityFor(w)],[h,setH]=useState(240);
 return <InstrumentFrameC width={w} height={h} testID="calibration-instrument">
  <View onLayout={e=>{const needed=Math.ceil(e.nativeEvent.layout.height)+7*u;if(Math.abs(h-needed)>1)setH(needed);}} style={{gap:16}}>
   <Text accessibilityRole="header" style={type.exercise}>{p.name}</Text>
   <Text accessibilityLiveRegion="polite" style={type.small}>{p.status}</Text>
   {p.children}
  </View>
 </InstrumentFrameC>;
}
export function CalibrationSetting(p:{value:string;onChange:(v:string)=>void;semantics:string|undefined;editing:boolean;label?:string;disabled?:boolean;onDone:()=>void}){
 const {width,fontScale}=useWindowDimensions(),outer=width-40,u=UNIT[densityFor(outer)];
 const w=frameGeometry('rail',outer,240,u).content.w,h=168*Math.max(1,Math.min(fontScale,1.8));
 const inner=recessedWindowGeometry(w,h,u).content.w,entered=parseCalibrationMass(p.value);
 return <RecessedWindow width={w} height={h} u={u} testID="calibration-setting-window">
  <View style={{flex:1,justifyContent:'center',gap:8}}>
   <Text style={type.eyebrow}>{p.label??(p.editing?'Ton choix de réglage':'Réglage saisi')}</Text>
   {p.editing?<TextInput accessibilityLabel={(p.label??'Réglage réellement choisi')+' · '+calibrationUnit(p.semantics)} testID="calibration-setting-input" editable={!p.disabled} value={p.value} onChangeText={p.onChange}
    keyboardType="decimal-pad" returnKeyType="done" onSubmitEditing={p.onDone} autoCorrect={false} placeholder="—" placeholderTextColor={color.ink3}
    style={[type.figure,{color:color.ink,minHeight:54,width:inner}]} />:
    <NumericReadout testID="calibration-setting-value" value={entered===null?'—':String(entered.value)} role={type.figure} />}
   <Text style={type.small}>{calibrationUnit(p.semantics)}</Text>
  </View>
 </RecessedWindow>;
}
