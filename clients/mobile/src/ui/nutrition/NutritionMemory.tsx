/** Factual current-head memory; no smoothing, extrapolation or dietary judgement. */
import React,{useState} from 'react';
import {Text,View,useWindowDimensions} from 'react-native';
import Svg,{Circle,Line,Text as SvgText} from 'react-native-svg';
import type {NutritionEntry} from '../../api/nutritionDTO';
import type {NutritionCollectionState} from '../../api/nutritionResource';
import type {NutritionField} from '../../domain/nutritionCommand';
import {EmbeddedAction} from '../body/EmbeddedAction';
import {color,type} from '../theme';
import {nutritionNumber} from './NutritionWorkspace';
const labels:Record<NutritionField,string>={kcal_milli:'Énergie',protein_milli:'Protéines',carbohydrate_milli:'Glucides',fat_milli:'Lipides'};
const units=(field:NutritionField)=>field==='kcal_milli'?'kcal':'g';
export function NutritionComparisonReadout(p:{entry:Pick<NutritionEntry,'state'|'target_ref'|'values'>|null;target:Pick<NutritionEntry,'id'|'values'>|null;field:NutritionField}){
 const {entry,target,field}=p,observed=entry?.values[field],reference=target?.values[field];
 if(!target||entry?.state!=='ACTIVE'||entry.target_ref!==target.id||observed==null||reference==null)return null;
 const delta=observed-reference,unit=units(field),difference=(delta<0?'−':delta>0?'+':'')+nutritionNumber(Math.abs(delta)),ratio=reference>0?observed/reference:null;
 return <View style={{gap:4}}><Text testID={`nutrition-target-reference-${field}`} style={type.small}>Cible déclarée · {nutritionNumber(reference)} {unit} · réf. {target.id}</Text><Text accessible accessibilityLabel={`Écart arithmétique ${difference} ${unit}`} style={[type.small,{color:color.system}]}>Écart {difference} {unit}</Text>{ratio!==null?<><View testID="nutrition-target-ratio" style={{height:2,backgroundColor:color.line}}><View style={{height:2,width:`${Math.min(100,ratio*100)}%`,backgroundColor:color.system}}/></View><Text style={type.small}>Rapport arithmétique · {Math.round(ratio*1000)/10}%</Text></>:<Text style={type.small}>Rapport non défini · cible zéro</Text>}</View>;
}
export function NutritionMemory(p:{state:NutritionCollectionState;field:NutritionField;onDay:(day:string)=>void}){
 const [width,setWidth]=useState(330),[expanded,setExpanded]=useState(false),large=useWindowDimensions().fontScale>=1.25,s=p.state,field=p.field,unit=units(field);
 if(s.state!=='confirmed'||!s.value)return <Text style={type.small}>{s.state==='partial'?'Lecture partielle · couverture non confirmée':'Historique à vérifier'}</Text>;
 const page=s.value,from=String(page.window?.from),through=String(page.window?.through),count=(Date.parse(through)-Date.parse(from))/86400000+1;
 const entries=page.entries.map(e=>'entry' in e?e.entry:e),byDay=new Map(entries.map(e=>[e.local_day,e])),coverage=page.coverage?.[field],total=page.totals?.[field];
 const calendar=Array.from({length:count},(_,i)=>new Date(Date.parse(from)+i*86400000).toISOString().slice(0,10));
 const points=entries.filter(e=>e.state==='ACTIVE'&&e.values[field]!==null);
 const numbers=points.map(e=>e.values[field]!),low=Math.min(...numbers),high=Math.max(...numbers),min=low===high?Math.max(0,low-1000):low,max=low===high?high+1000:high;
 const left=8,right=Math.max(140,width-82),top=18,bottom=154,x=(day:string)=>left+(Date.parse(day)-Date.parse(from))/Math.max(86400000,Date.parse(through)-Date.parse(from))*(right-left),y=(value:number)=>bottom-(value-min)/(max-min)*(bottom-top);
 return <View style={{gap:8}} onLayout={event=>{const w=event.nativeEvent.layout.width;if(Number.isFinite(w)&&w>=220)setWidth(w);}}>
  <Text style={type.small}>{from} → {through} · {unit}</Text>
  {coverage?<View accessible accessibilityLabel={`Couverture ${labels[field]} : ${coverage.known_days} jours connus, ${coverage.missing_days} jours sans valeur, ${coverage.partial_days} partiel, ${coverage.declared_complete_days} déclaré complet, ${coverage.withdrawn_days} retiré, sur ${coverage.total_calendar_days} jours`}><Text style={type.small}>{coverage.known_days} jours renseignés · {coverage.missing_days} sans valeur</Text><Text style={type.small}>{coverage.partial_days} partiels · {coverage.declared_complete_days} déclarés complets · {coverage.withdrawn_days} retirés / {coverage.total_calendar_days} jours</Text></View>:null}
  {points.length>=2?<View testID="nutrition-history-chart" accessible accessibilityLabel={`${labels[field]} : observations datées uniquement, ${points.length} points ; valeurs exactes disponibles ci-dessous`}><Svg width={width} height={178} accessibilityElementsHidden importantForAccessibility="no-hide-descendants">{[min,(min+max)/2,max].map((value,i)=><React.Fragment key={i}><Line x1={left} x2={right} y1={y(value)} y2={y(value)} stroke={color.line}/><SvgText x={right+8} y={y(value)+4} fill={color.ink3} fontSize={12}>{nutritionNumber(Math.round(value))}</SvgText></React.Fragment>)}{points.map(e=><Circle testID={`nutrition-history-point-${e.id}`} key={e.id} cx={x(e.local_day!)} cy={y(e.values[field]!)} r={4} fill={color.ink2}/>)}</Svg></View>:<Text style={type.small}>Chronologie insuffisante pour un graphique · valeurs exactes ci-dessous</Text>}
  {total?<Text style={type.small}>Somme connue · {nutritionNumber(total.value)} {unit} sur {total.known_days} jours{total.reason?' · somme hors plage arithmétique':''}</Text>:null}
  {(expanded?calendar:calendar.slice(-7)).map(day=>{const e=byDay.get(day),status=!e?'absent':e.state==='WITHDRAWN'?'retiré':e.declared_complete?'déclaré complet':'partiel',value=e?.state==='ACTIVE'?nutritionNumber(e.values[field]):null;
   return <View key={day} style={{borderTopWidth:1,borderColor:color.line}}><EmbeddedAction label={`${day} · ${value===null?'':value+' '+unit+' · '}${status}`} onPress={()=>p.onDay(day)}/></View>;})}
  {calendar.length>7?<EmbeddedAction label={expanded?'Réduire les jours':`Tous les ${calendar.length} jours`} expanded={expanded} onPress={()=>setExpanded(!expanded)}/>:null}
 </View>;
}
