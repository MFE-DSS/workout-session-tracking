/** Local historical composition; locked instruments and tokens remain unchanged. */
import React,{useState} from 'react';
import {ScrollView,Text,View,useWindowDimensions} from 'react-native';
import {useSafeAreaInsets} from 'react-native-safe-area-context';
import {AurenMark} from '../brand/AurenMark';
import {CalibrationLink} from '../plan/calibrationControls';
import {InstrumentFrameC} from '../instrument/InstrumentFrame';
import {RecessedWindow} from '../instrument/RecessedWindow';
import {NumericReadout} from '../instrument/NumericReadout';
import {frameGeometry} from '../instrument/frameGeometry';
import {densityFor,UNIT} from '../calibration/layout';
import {color,space,type} from '../theme';
import {numeric} from './historyView';

export function HistoricalFactsFrame(p:{name:string;status:string;onBack:()=>void;previous?:boolean;children:React.ReactNode}){
 const insets=useSafeAreaInsets();
 return <ScrollView style={{flex:1,backgroundColor:color.field}} contentInsetAdjustmentBehavior="never" contentContainerStyle={{paddingHorizontal:space.gutter,paddingTop:insets.top+12,paddingBottom:insets.bottom+12,gap:12}}>
  <View style={{flexDirection:'row',justifyContent:'space-between',alignItems:'center',gap:8,flexWrap:'wrap'}}>
   <CalibrationLink testID="account-back" label="Retour" onPress={p.onBack}/>
   <View style={{flexDirection:'row',alignItems:'center',gap:8}}><AurenMark size={20} color={color.ink}/><Text style={type.eyebrow}>AUREN</Text></View>
   <Text style={type.small}>Historique</Text>
  </View>
  <View style={{gap:4}}><Text testID="history-session-title" selectable accessibilityRole="header" style={type.bodyStrong}>{p.name}</Text><Text selectable style={type.small}>{p.status}</Text>{p.previous?<Text accessibilityLiveRegion="polite" style={type.small}>Lecture précédente</Text>:null}</View>
  {p.children}
 </ScrollView>;
}
export function HistoricalExerciseInstrument(p:{name:string;context:string;seId:number;selected:boolean;children:(width:number,u:number)=>React.ReactNode}){
 const {width}=useWindowDimensions(),w=width-2*space.gutter,u=UNIT[densityFor(w)],[height,setHeight]=useState(180),contentWidth=frameGeometry('rail',w,height,u).content.w;
 return <InstrumentFrameC width={w} height={height} u={u} testID={`history-instrument-${p.seId}`}>
  <View onLayout={e=>{const next=Math.ceil(e.nativeEvent.layout.height)+7*u;if(Math.abs(next-height)>1)setHeight(next);}} style={{gap:8}}>
   {p.selected?<Text testID={`history-selected-exercise-${p.seId}`} style={type.small}>Exercice sélectionné</Text>:null}
   <Text selectable accessibilityRole="header" style={type.bodyStrong}>{p.name}</Text>
   <Text testID={`history-context-${p.seId}`} style={type.small}>{p.context}</Text>
   {p.children(contentWidth,u)}
  </View>
 </InstrumentFrameC>;
}
export function HistoricalSetWindow(p:{width:number;u:number;set:{set_id:number;kind:string;set_index:number;completed:boolean;reps:number|null;raw_reps_repr?:string|null};load:number|null;unit:string;rawLoad?:string|null;hasObservation?:boolean}){
 const [contentHeight,setContentHeight]=useState(0),s=p.set,h=Math.max(92,contentHeight+4.5*p.u);
 const empty=!p.hasObservation&&!s.completed&&s.reps===null&&p.load===null&&p.rawLoad==null&&s.raw_reps_repr==null;
 return <RecessedWindow width={p.width} height={h} u={p.u} testID={`history-set-${s.set_id}`}>
  <View onLayout={e=>setContentHeight(Math.ceil(e.nativeEvent.layout.height))} style={{gap:6}}>
   <Text style={type.small}>{s.kind==='work'?'Série':'Préparation'} {s.set_index} · {empty?'Aucun fait enregistré':s.completed?'Complétée':'Non complétée'}</Text>
   <View style={{flexDirection:'row',flexWrap:'wrap',alignItems:'flex-start',gap:8}}>
    <View style={{minWidth:146,maxWidth:'100%'}}>{p.rawLoad!=null?<Text style={type.bodyStrong}>Charge invalide</Text>:p.load===null?<Text style={type.body}>Charge inconnue</Text>:<NumericReadout testID={`history-load-${s.set_id}`} role={type.figure} value={numeric(p.load)} unit={p.unit}/>}</View>
    <View style={{minWidth:80,maxWidth:'100%'}}>{s.raw_reps_repr!=null?<Text style={type.bodyStrong}>Répétitions invalides</Text>:s.reps===null?<Text style={type.body}>Répétitions inconnues</Text>:<NumericReadout testID={`history-reps-${s.set_id}`} role={type.figure} value={String(s.reps)} unit="rép."/>}</View>
   </View>
  </View>
 </RecessedWindow>;
}
