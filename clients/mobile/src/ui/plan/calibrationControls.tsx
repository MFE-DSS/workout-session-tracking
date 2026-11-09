/** Local calibration controls. Existing palette and roles, no global primitive changes. */
import React from 'react';
import {Pressable,Text,View} from 'react-native';
import {color,type} from '../theme';
export function CalibrationAction(p:{label:string;onPress:()=>void;disabled?:boolean;busy?:boolean;reason?:string;testID?:string}){
 const disabled=Boolean(p.disabled||p.busy);
 return <View testID="calibration-primary-action" style={{gap:6}}>
  <Pressable testID={p.testID} accessibilityRole="button" accessibilityLabel={p.label} accessibilityHint={p.reason} accessibilityState={{disabled,busy:Boolean(p.busy)}} disabled={disabled} onPress={p.onPress}
   style={({pressed})=>({minHeight:48,paddingVertical:12,paddingHorizontal:16,borderRadius:16,backgroundColor:color.signal,justifyContent:'center',opacity:disabled ? 0.5 : pressed ? 0.7 : 1})}>
   <Text style={[type.bodyStrong,{color:color.onSignal,textAlign:'center'}]}>{p.label}</Text>
  </Pressable>
  {p.reason?<Text accessibilityLiveRegion="polite" style={type.small}>{p.reason}</Text>:null}
 </View>;
}
export function CalibrationLink(p:{label:string;onPress:()=>void;testID?:string;disabled?:boolean;expanded?:boolean;selected?:boolean;inputRef?:React.Ref<React.ComponentRef<typeof Pressable>>}){
 return <Pressable ref={p.inputRef} testID={p.testID} accessibilityRole="button" accessibilityLabel={p.label} accessibilityState={{disabled:Boolean(p.disabled),...(p.expanded===undefined?{}:{expanded:p.expanded}),...(p.selected===undefined?{}:{selected:p.selected})}} disabled={p.disabled} onPress={p.onPress}
  style={({pressed})=>({minHeight:48,justifyContent:'center',paddingVertical:10,opacity:p.disabled ? 0.5 : pressed ? 0.6 : 1})}>
  <Text style={[type.bodyStrong,{color:color.ink2}]}>{p.label}</Text>
 </Pressable>;
}
export function CalibrationChoices<T extends string|boolean|null>(p:{label:string;value:T|undefined;options:ReadonlyArray<{value:T;label:string}>;onChange:(v:T)=>void;disabled?:boolean}){
 return <View accessibilityLabel={p.label} style={{gap:6}}>
  <Text style={type.eyebrow}>{p.label}</Text>
  <View style={{flexDirection:'row',flexWrap:'wrap',gap:8}}>{p.options.map((o,i)=><Pressable key={i} disabled={p.disabled} accessibilityRole="radio" accessibilityLabel={o.label} accessibilityState={{selected:p.value===o.value,checked:p.value===o.value,disabled:Boolean(p.disabled)}} onPress={()=>p.onChange(o.value)}
   style={({pressed})=>({minHeight:48,flexShrink:1,justifyContent:'center',paddingHorizontal:12,paddingVertical:10,borderRadius:12,borderWidth:1,borderColor:p.value===o.value?color.ink:color.line,backgroundColor:p.value===o.value?color.plate:color.field,opacity:pressed ? 0.6 : 1})}>
   <Text style={[type.bodyStrong,{color:color.ink}]}>{p.value===o.value?'✓ ':''}{o.label}</Text>
  </Pressable>)}</View>
 </View>;
}
