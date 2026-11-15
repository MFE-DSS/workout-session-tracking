import React from 'react';
import {Text,View,useWindowDimensions} from 'react-native';
import {color,type} from '../theme';
/** Open composition; Frame C and W1 masters remain untouched. */
export function InstrumentSurface(p:{label:string;state:string;children:React.ReactNode;action?:React.ReactNode;editing?:boolean}){
 const large=useWindowDimensions().fontScale>=1.25;
 return <View testID="da08-surface" style={{gap:12}}>
  <View style={{flexDirection:large?'column':'row',justifyContent:'space-between',gap:4}}><Text accessibilityRole="header" style={[type.bodyStrong,{fontSize:19,lineHeight:25}]}>{p.label}</Text><Text style={[type.small,{color:p.editing?color.signal:color.ink3}]}>{p.state}</Text></View>
  <View style={{flexDirection:large?'column':'row',gap:12,alignItems:large?'stretch':'center',paddingVertical:12,borderBottomWidth:1,borderColor:p.editing?color.signal:color.line}}><View style={{flex:1,minWidth:0}}>{p.children}</View>{p.action}</View>
 </View>;
}
