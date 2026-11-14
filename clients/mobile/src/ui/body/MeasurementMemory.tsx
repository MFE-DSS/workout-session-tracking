import React,{useState} from 'react';
import {Text,View,useWindowDimensions,Pressable} from 'react-native';
import Svg,{Circle,Line} from 'react-native-svg';
import {color,type} from '../theme';
import {bodyDay,bodyNumber,type BodyObservation} from './bodyCockpitModel';
import {memoryGeometry,sourceKind,type DraftPoint} from './instrumentMemoryModel';
export function MeasurementMemory(p:{rows:BodyObservation[];unit:string;selected:number|null;onChoose:(day:string|null)=>void;draft?:DraftPoint}){
 const {width,fontScale}=useWindowDimensions(),[measured,setMeasured]=useState<number|null>(null),w=Math.max(200,measured??width-40),h=fontScale>=1.25?180:154,g=memoryGeometry(p.rows,w,h,p.draft);
 return <View testID="body-memory" onLayout={e=>{const next=e.nativeEvent.layout.width;if(next>0)setMeasured(next);}} style={{gap:8}}><View style={{flexDirection:'row',flexWrap:'wrap',gap:8,justifyContent:'space-between'}}><Text style={type.eyebrow}>Mémoire</Text><Text style={type.small}>{p.unit} · jours déclarés</Text></View>
 {g.points.length?<><Pressable testID="body-plot-pick" accessibilityRole="button" accessibilityLabel="Choisir un jour et son relevé exact" accessibilityHint="Les observations du même jour restent distinctes" onPress={e=>{const point=g.points.reduce((a,b)=>Math.abs(a.x-e.nativeEvent.locationX)<Math.abs(b.x-e.nativeEvent.locationX)?a:b);p.onChoose(point.observation.day);}}><Svg testID="body-plot" width={w} height={h} accessible={false} importantForAccessibility="no-hide-descendants">
  {g.ticks.map((t,i)=><Line key={'axis'+i} x1={g.left} x2={g.right} y1={t.y} y2={t.y} stroke={color.line} strokeWidth={1}/>)}
  <Line x1={g.left} x2={g.right} y1={g.bottom} y2={g.bottom} stroke={color.ink3} strokeWidth={1}/>
  {g.points.map(point=>{const active=p.selected===point.observation.entry.measurement_id,kind=sourceKind(point.observation);return <React.Fragment key={point.observation.entry.measurement_id}><Line x1={point.x} x2={point.x} y1={g.bottom} y2={g.bottom+4} stroke={color.ink3}/>{active?<Line x1={point.x} x2={point.x} y1={g.top} y2={g.bottom} stroke={color.signal} strokeWidth={1} opacity={0.5}/>:null}<Circle cx={point.x} cy={point.y} r={active?5:3.5} fill={kind==='manual'?color.ink2:color.field} stroke={active?color.signal:color.ink2} strokeWidth={active?2:1} strokeDasharray={kind==='unknown'?'2 2':undefined}/></React.Fragment>;})}
  {g.draft&&!g.draft.outside?<Circle cx={g.draft.x} cy={g.draft.y} r={5} fill={color.field} stroke={color.signal} strokeDasharray="2 2" strokeWidth={2}/>:null}
 </Svg><View pointerEvents="none" style={{position:'absolute',right:0,top:0,bottom:30,justifyContent:'space-between'}}>{[...g.ticks].reverse().map((t,i)=><Text key={i} maxFontSizeMultiplier={1.25} style={type.small}>{bodyNumber(Number(t.value.toPrecision(3)))}</Text>)}</View></Pressable>
 <View style={{flexDirection:'row',justifyContent:'space-between',flexWrap:'wrap'}}><Text style={type.small}>{bodyDay(g.from)}</Text><Text style={type.small}>{bodyDay(g.through)}</Text></View>
 {g.points.some(p=>sourceKind(p.observation)!=='manual')?<Text style={type.small}>Plein : saisie · creux : correction · pointillé : origine inconnue</Text>:null}
 {g.draft?<Text style={[type.small,{color:color.signal}]}>{g.draft.outside?'Brouillon hors de cette échelle':'Brouillon non enregistré'}</Text>:null}
 </>:<Text style={type.small}>{p.rows.length?'Valeurs ou dates non comparables · sources disponibles':'Aucune observation de cette mesure'}</Text>}
 </View>;
}
