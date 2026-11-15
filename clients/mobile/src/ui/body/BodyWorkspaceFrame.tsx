import React from 'react';
import {ScrollView,Text,View,useWindowDimensions} from 'react-native';
import {useSafeAreaInsets} from 'react-native-safe-area-context';
import {AurenMark} from '../brand/AurenMark';
import {color,type} from '../theme';
import {BodyCommand} from './BodyCockpit';

/** Local composition only. The owning ConnectedApp retains its native D4 shell. */
export function BodyWorkspaceFrame(p:{children:React.ReactNode;onBack:()=>void;disabled:boolean;inTab?:boolean}){
 const insets=useSafeAreaInsets(),large=useWindowDimensions().fontScale>=1.25;
 // Retained native tabs can lose automatic scroll insets after modal/font changes.
 // The safe-area provider remains the authority; do not depend on that scroll state.
 return <View testID="body-safe-viewport" style={{flex:1,backgroundColor:color.field,paddingTop:insets.top,paddingBottom:insets.bottom}}><ScrollView keyboardShouldPersistTaps="handled" contentInsetAdjustmentBehavior="never" contentContainerStyle={{paddingHorizontal:20,paddingTop:8,paddingBottom:16,gap:16}}>
  <View style={{minHeight:48,borderBottomWidth:1,borderColor:color.line,flexDirection:large?'column':'row',alignItems:large?'flex-start':'center',gap:12}}><AurenMark size={20} color={color.ink}/><Text accessibilityRole="header" style={[type.bodyStrong,{flex:large?undefined:1}]}>BODY</Text><BodyCommand label="Retour" onPress={p.onBack} disabled={p.disabled}/></View>
  {p.children}
 </ScrollView></View>;
}
