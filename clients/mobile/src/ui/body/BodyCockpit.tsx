import React,{useState} from 'react';
import {Text,View,Pressable,useWindowDimensions} from 'react-native';
import type {BodyEntry,BodyKey,BodySpec} from '../../api/bodyMeasurements';
import {bodyDay,bodyNumber,bodyObservations,defaultObservation,compareObservations} from './bodyCockpitModel';
import {NumericReadout} from '../instrument/NumericReadout';
import {color,type} from '../theme';
import {InstrumentSurface} from './InstrumentSurface';
import {EmbeddedAction} from './EmbeddedAction';
import {MeasurementMemory} from './MeasurementMemory';
import {sourceLabel} from './instrumentMemoryModel';
export type BodyInstrumentProps={entries:BodyEntry[];specs:BodySpec[];previous:boolean;partial:boolean;locked:boolean;onAcquire:(key:BodyKey,reference?:BodyEntry)=>void;onInspect:(root:number)=>void};
const names:Partial<Record<BodyKey,string>>={weight_kg:'Masse corporelle',waist_cm:'Tour de taille',arm_cm_left:'Bras gauche',arm_cm_right:'Bras droit'};
const clean=(s:string)=>s.replace(/\s*\((kg|cm)\)\s*$/,'');
export function BodyCommand(p:{label:string;onPress:()=>void;disabled?:boolean;selected?:boolean;signal?:boolean;testID?:string;children?:React.ReactNode}){
 return <Pressable testID={p.testID} onPress={p.onPress} disabled={p.disabled} accessibilityRole="button" accessibilityLabel={p.label} accessibilityState={{disabled:!!p.disabled,...(p.selected===undefined?{}:{selected:p.selected})}}
  style={({pressed})=>({minHeight:48,justifyContent:'center',opacity:p.disabled?0.5:pressed?0.6:1})}>{p.children??<Text style={[type.bodyStrong,{color:p.signal?color.signal:color.ink2}]}>{p.label}</Text>}</Pressable>;
}
export function BodyCockpit(p:BodyInstrumentProps){
 const [field,setField]=useState<BodyKey>(p.specs.some(s=>s.key==='weight_kg')?'weight_kg':p.specs[0]?.key??'weight_kg'),[chosen,setChosen]=useState<number|null>(null),[day,setDay]=useState<string|null|false>(false),[all,setAll]=useState(false),[reference,setReference]=useState<number|null>(null),[comparing,setComparing]=useState(false);
 const {fontScale}=useWindowDimensions(),large=fontScale>=1.25,rows=bodyObservations(p.entries,field),selected=chosen===null?defaultObservation(rows):rows.find(o=>o.entry.measurement_id===chosen)??null,spec=p.specs.find(s=>s.key===field),unit=spec?.unit??'kg',others=p.specs.filter(s=>s.key!==field),preferred=['weight_kg','waist_cm','arm_cm_left','arm_cm_right'];
 const auxiliary=all?others:[...others.filter(s=>preferred.includes(s.key)),...others.filter(s=>!preferred.includes(s.key))].slice(0,3);
 const choose=(key:BodyKey)=>{setField(key);setChosen(null);setDay(false);setReference(null);setComparing(false);};
 const state=p.previous?'Lecture précédente':selected?sourceLabel(selected):rows.length?'Choisir le relevé':'Non renseigné';
 const ref=rows.find(o=>o.entry.measurement_id===reference),diff=selected&&ref?compareObservations(ref,selected):null;
 return <View testID="body-cockpit" style={{gap:24}}>
 <InstrumentSurface label={names[field]??clean(spec?.label??field)} state={state} action={<EmbeddedAction label="+ Relever" primary testID="body-new" disabled={p.locked} onPress={()=>p.onAcquire(field,selected?.entry)}/>}>
  <NumericReadout testID={selected?'body-current-value':'body-value-unknown'} value={selected?.value.value!=null?bodyNumber(selected.value.value):selected?.value.raw_value_repr??'—'} unit={unit} role={type.figure}/>
  <Text style={type.small}>{selected?bodyDay(selected.day):' '}</Text>
 </InstrumentSurface>
 <MeasurementMemory rows={rows} unit={unit} selected={selected?.entry.measurement_id??null} onChoose={d=>setDay(d)}/>
 <View style={{flexDirection:'row',flexWrap:'wrap',justifyContent:'space-between',gap:8}}><EmbeddedAction testID="body-compare-open" label="Comparer" disabled={!selected||!rows.some(o=>compareObservations(o,selected))} onPress={()=>{setComparing(true);setDay(null);}}/><EmbeddedAction label="Relevés exacts" testID="body-observations-open" onPress={()=>{setComparing(false);setDay(day===false?null:false);}}/><EmbeddedAction label="Sources / versions ›" testID="body-sources" disabled={!selected} onPress={()=>selected&&p.onInspect(selected.entry.root_ref)}/></View>
 {day!==false?<View style={{gap:4}}>{rows.filter(o=>!day||o.day===day).map(o=><EmbeddedAction key={o.entry.measurement_id} testID={`body-${comparing?'reference':'observation'}-${o.entry.measurement_id}`} disabled={comparing&&(!selected||!compareObservations(o,selected))} label={`${bodyDay(o.day)} · ${o.value.value===null?o.value.raw_value_repr??'inconnu':bodyNumber(o.value.value)} ${o.value.unit} · v${o.entry.revision} · ${o.entry.root_ref}`} active={chosen===o.entry.measurement_id} onPress={()=>{if(comparing&&selected){setReference(o.entry.measurement_id);setChosen(selected.entry.measurement_id);}else{setChosen(o.entry.measurement_id);setReference(null);}setDay(false);setComparing(false);}}/>)}<EmbeddedAction label="Fermer" onPress={()=>setDay(false)}/></View>:null}
 {diff?<View testID="body-comparison" style={{gap:4}}><Text style={type.small}>{diff.from} → {diff.through} · {diff.days} jours déclarés</Text><NumericReadout value={(diff.difference>0?'+':'')+bodyNumber(diff.difference)} unit={unit} role={{...type.bodyStrong,color:color.system,fontSize:22}}/><Text style={type.small}>Écart arithmétique · conditions de mesure inconnues</Text><EmbeddedAction label="Retirer la comparaison" onPress={()=>setReference(null)}/></View>:null}
 {p.partial?<Text style={type.small}>Fenêtre chargée partiellement</Text>:null}
 <View style={{gap:12,borderTopWidth:1,borderColor:color.line,paddingTop:12}}><View style={{flexDirection:large?'column':'row',justifyContent:'space-between',alignItems:large?'stretch':'center',gap:8}}><Text style={type.eyebrow}>Mesures du dossier</Text><EmbeddedAction testID="body-fields-open" label={all?'Réduire':'Toutes ›'} onPress={()=>setAll(!all)}/></View><View style={{flexDirection:large?'column':'row',flexWrap:'wrap',gap:12}}>{auxiliary.map(s=>{const observations=bodyObservations(p.entries,s.key),o=defaultObservation(observations);return <View testID={`body-peripheral-${s.key}`} key={s.key} style={{flexBasis:large?'100%':'29%',flexGrow:1,borderTopWidth:1,borderColor:color.ink3,paddingTop:8}}><EmbeddedAction testID={`body-field-${s.key}`} label={clean(s.label)} onPress={()=>choose(s.key)}/><NumericReadout value={o?.value.value!=null?bodyNumber(o.value.value):'—'} unit={o?s.unit:undefined} role={{...type.bodyStrong,fontSize:24,lineHeight:28}}/><Text style={type.small}>{o?bodyDay(o.day):observations.length?'Choisir le relevé':'Non renseigné'}</Text></View>;})}</View></View>
 </View>;
}
