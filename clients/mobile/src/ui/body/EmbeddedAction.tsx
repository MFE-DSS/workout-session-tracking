import React from 'react';
import {Pressable,Text,View} from 'react-native';
import {color,type} from '../theme';
/** Local composite, no change to global CTA or its baseline. Touch area >=48. */
export function EmbeddedAction(p:{label:string;onPress:()=>void;disabled?:boolean;busy?:boolean;expanded?:boolean;active?:boolean;primary?:boolean;testID?:string}){
 return <Pressable testID={p.testID} accessibilityRole="button" accessibilityLabel={p.label} accessibilityState={{disabled:!!p.disabled,selected:!!p.active,...(p.busy===undefined?{}:{busy:p.busy}),...(p.expanded===undefined?{}:{expanded:p.expanded})}} disabled={p.disabled} onPress={p.onPress} style={({pressed})=>({minWidth:48,minHeight:48,justifyContent:'center',paddingHorizontal:12,opacity:p.disabled?0.4:pressed?0.65:1})}><View style={{flexDirection:'row',alignItems:'center',gap:8}}>{p.active?<View style={{width:4,height:18,backgroundColor:color.signal}}/>:null}<Text style={[type.bodyStrong,{color:p.active||p.primary?color.signal:color.ink2}]}>{p.label}</Text></View></Pressable>;
}
