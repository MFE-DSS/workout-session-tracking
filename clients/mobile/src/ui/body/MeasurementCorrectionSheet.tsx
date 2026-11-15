import React,{useRef,useState} from 'react';
import {InputAccessoryView,Keyboard,Modal,Platform,ScrollView,Text,TextInput,View,KeyboardAvoidingView,useWindowDimensions} from 'react-native';
import {SafeAreaProvider,SafeAreaView} from 'react-native-safe-area-context';
import type {BodyEntry,BodyKey,BodySpec} from '../../api/bodyMeasurements';
import {keyboardAvoidance} from '../../native/platformUi';
import {EmbeddedAction} from './EmbeddedAction';
import {InstrumentSurface} from './InstrumentSurface';
import {color,type} from '../theme';
import {bodyDay,bodyNumber} from './bodyCockpitModel';
import {measurementValues,measurementLabel,type BodyForm} from './measurementInputModel';
export function MeasurementCorrectionSheet(p:{specs:BodySpec[];initial?:BodyEntry;reference?:BodyEntry;busy:boolean;onSave:(form:BodyForm)=>void;onClose:()=>void}){
 const {width,fontScale}=useWindowDimensions(),large=fontScale>=1.25,innerWidth=Math.max(240,width-40);
 const [active,setActive]=useState(p.specs[0].key),[inputWidth,setInputWidth]=useState(90);
 const [draft,setDraft]=useState<Partial<Record<BodyKey,string>>>(()=>Object.fromEntries(p.specs.map(s=>[s.key,p.initial?.fields[s.key].value==null?'':String(p.initial.fields[s.key].value).replace('.',',')]))),[cleared,setCleared]=useState<Partial<Record<BodyKey,boolean>>>({});
 const [day,setDay]=useState(''),[dirty,setDirty]=useState(false),[leave,setLeave]=useState(false),[help,setHelp]=useState(false);const first=useRef<React.ComponentRef<typeof TextInput>>(null);
 const validDay=/^\d{4}-\d{2}-\d{2}$/.test(day)&&Number.isFinite(Date.parse(day+'T00:00:00Z'))&&new Date(day+'T00:00:00Z').toISOString().slice(0,10)===day&&day<=new Date().toISOString().slice(0,10);
 let values:BodyForm['values']={},valid=true;try{values=measurementValues(p.specs,draft,cleared,p.initial);}catch{valid=false;}
 const changed=Object.keys(values).length>0||validDay;
 const hasFact=Object.values(values).some(value=>value!==null);
 const canSave=valid&&(p.initial?(validDay||day==='')&&changed:validDay&&hasFact);
 const previous=p.initial??p.reference;
 const spec=p.specs.find(s=>s.key===active)!;
 const close=()=>{if(p.busy)return;if(dirty)setLeave(true);else p.onClose();};
 return <Modal visible transparent animationType="none" onRequestClose={close} presentationStyle="overFullScreen" accessibilityViewIsModal>
  <SafeAreaProvider style={{backgroundColor:color.field}}><SafeAreaView edges={['top','bottom','left','right']} style={{flex:1}}><KeyboardAvoidingView style={{flex:1,backgroundColor:color.field}} behavior={keyboardAvoidance.behavior}>
   <ScrollView keyboardShouldPersistTaps="handled" contentInsetAdjustmentBehavior="never" contentContainerStyle={{paddingTop:16,paddingBottom:12,paddingHorizontal:20,gap:12}}>
    <View testID="body-editor-instrument" style={{gap:12}}>
     <Text style={type.eyebrow}>BODY / acquisition</Text>
     {leave?<View style={{gap:8}}><Text style={type.bodyStrong}>Quitter sans enregistrer ?</Text><Text style={type.small}>Ce brouillon n’a pas été envoyé.</Text><EmbeddedAction label="Garder le brouillon" onPress={()=>setLeave(false)}/><EmbeddedAction label="Quitter sans enregistrer" onPress={p.onClose}/></View>:<>
      {p.specs.length>1?<View style={{flexDirection:large?'column':'row',gap:12}}>{p.specs.map(s=><View key={s.key} style={{flex:1}}><EmbeddedAction testID={`body-side-${s.key}`} label={`${measurementLabel(s.label)} · ${draft[s.key]||'inconnu'}`} active={s.key===active} disabled={p.busy} onPress={()=>{Keyboard.dismiss();setActive(s.key);}}/></View>)}</View>:null}
      <InstrumentSurface label={measurementLabel(spec.label)} state={p.initial?'Correction':'Brouillon'} editing><View style={{flexDirection:'row',alignItems:'baseline',gap:8}}>
       <Text accessible={false} importantForAccessibility="no-hide-descendants" numberOfLines={1} maxFontSizeMultiplier={1.25} onTextLayout={e=>{const width=e.nativeEvent.lines[0]?.width;if(Number.isFinite(width)&&width>0)setInputWidth(Math.ceil(width));}} style={[type.figure,{position:'absolute',opacity:0,fontSize:(draft[spec.key]?.length??0)>9?30:40}]}>{draft[spec.key]||'—'}</Text>
       <TextInput ref={first} testID={`body-value-${spec.key}`} accessibilityLabel={`${spec.label}, ${spec.unit==='kg'?'kilogrammes':'centimètres'}`} value={draft[spec.key]??''} onChangeText={v=>{setDraft(d=>({...d,[spec.key]:v}));setCleared(d=>({...d,[spec.key]:false}));setDirty(true);}} selectionColor={color.signal} editable={!p.busy} keyboardType="decimal-pad" inputMode="decimal" returnKeyType="done" onSubmitEditing={()=>Keyboard.dismiss()} inputAccessoryViewID={Platform.OS==='ios'?'body-decimal-done':undefined} placeholder={cleared[spec.key]?'À effacer':'—'} placeholderTextColor={color.ink3} maxFontSizeMultiplier={1.25} style={[type.figure,{flexShrink:1,width:Math.min(Math.max(48,inputWidth+8),innerWidth-80),minWidth:0,minHeight:56,fontSize:(draft[spec.key]?.length??0)>9?30:40,paddingVertical:0}]}/>
       <Text maxFontSizeMultiplier={1.25} style={[type.bodyStrong,{fontSize:16,color:color.ink2}]}>{spec.unit}</Text>
      </View></InstrumentSurface>
      <View style={{gap:4}}><Text style={type.small}>Jour déclaré{p.initial?' · vide : date source conservée':''}</Text>
       <View style={{flexDirection:large?'column':'row',alignItems:large?'stretch':'center',gap:8}}>
        <TextInput testID="body-day" accessibilityLabel="Jour de mesure, année mois jour" value={day} onChangeText={v=>{setDay(v);setDirty(true);}} placeholder="AAAA-MM-JJ" placeholderTextColor={color.ink3} autoCorrect={false} autoCapitalize="none" inputMode="text" returnKeyType="next" onSubmitEditing={()=>first.current?.focus()} editable={!p.busy} style={[type.bodyStrong,{flex:large?undefined:1,minHeight:48,borderBottomWidth:1,borderColor:color.line}]}/>
        {!large||!validDay?<EmbeddedAction label="Aujourd’hui" disabled={p.busy} onPress={()=>{setDay(new Date().toISOString().slice(0,10));setDirty(true);}}/>:null}
       </View>
      </View>
      {previous?<Text testID="body-acquisition-reference" style={type.small}>{p.initial?'Original':'Réf.'} · {previous.fields[spec.key]?.value==null?'inconnu':bodyNumber(previous.fields[spec.key].value!)} {spec.unit} · {bodyDay(previous.date_precision==='DAY_UTC_CONVENTION'?previous.measured_at.slice(0,10):null)}{previous.date_precision==='DAY_UTC_CONVENTION'?'':' · précision inconnue'}</Text>:null}
      {p.initial?.fields[spec.key].quality!=='MISSING'&&p.initial?<EmbeddedAction label={cleared[spec.key]?'Annuler l’effacement':`Effacer ${spec.label.toLowerCase()}`} disabled={p.busy} onPress={()=>{setCleared(c=>({...c,[spec.key]:!c[spec.key]}));setDirty(true);}}/>:null}
      {cleared[spec.key]?<Text style={type.small}>Champ à effacer · original conservé dans les versions.</Text>:null}
      {!valid?<Text accessibilityLiveRegion="polite" style={[type.small,{color:color.alert}]}>Valeur hors des bornes de saisie ou format invalide. Vérifie l’unité.</Text>:null}
      <View style={{flexDirection:large?'column':'row',gap:16}}><View style={{flex:large?undefined:1}}><EmbeddedAction testID="body-cancel" label="Annuler" disabled={p.busy} onPress={close}/></View><View style={{flex:large?undefined:2}}><EmbeddedAction testID="body-save" busy={p.busy} label={p.initial?'Corriger':'Enregistrer'} active disabled={!canSave||p.busy} onPress={()=>{Keyboard.dismiss();p.onSave({values,...(validDay?{measured_on:day}:{})});}}/></View></View>
     </>}
    </View>
    <EmbeddedAction label="Source et aide" expanded={help} onPress={()=>setHelp(!help)}/>
    {help?<Text style={type.small}>Saisie personnelle{p.initial?' · original conservé':''}. Un côté peut rester inconnu. Jour déclaré selon le calendrier UTC ; aucune heure de mesure déduite. Les bornes contrôlent la saisie, sans être des objectifs.</Text>:null}
   </ScrollView>
  </KeyboardAvoidingView>
  {Platform.OS==='ios'?<InputAccessoryView nativeID="body-decimal-done"><View style={{backgroundColor:color.field,paddingHorizontal:20,alignItems:'flex-end'}}><EmbeddedAction label="Terminé" onPress={()=>Keyboard.dismiss()}/></View></InputAccessoryView>:null}
 </SafeAreaView></SafeAreaProvider></Modal>;
}
