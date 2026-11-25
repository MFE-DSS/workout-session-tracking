import React,{useEffect,useRef} from 'react';
import {ScrollView,StyleSheet,Text,View} from 'react-native';
import {useSafeAreaInsets} from 'react-native-safe-area-context';
import {AurenMark} from '../brand/AurenMark';
import {color,space,type} from '../theme';

/** Today consumer layout. The footer stays outside scrolling content; D4 owns its own inset. */
export function MissionCockpitFrame(p:{children:React.ReactNode;footer:React.ReactNode;menu?:React.ReactNode;identity?:React.ReactNode;revealEnd?:boolean}){
 const insets=useSafeAreaInsets();
 const scroll=useRef<React.ComponentRef<typeof ScrollView>>(null);
 useEffect(()=>{if(p.revealEnd===false)scroll.current?.scrollTo({y:0,animated:true});},[p.revealEnd]);
 return <View style={[styles.root,{paddingTop:insets.top+8,paddingLeft:insets.left,paddingRight:insets.right}]}>
  <View style={styles.header}><View style={styles.brand}><AurenMark size={24} color={color.ink}/><Text style={type.eyebrow}>Aujourd’hui</Text></View>{p.menu}</View>
  {p.identity?<View style={{paddingHorizontal:space.gutter,paddingTop:12}}>{p.identity}</View>:null}
  <ScrollView ref={scroll} style={{flex:1}} contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled"
   onContentSizeChange={()=>{if(p.revealEnd)scroll.current?.scrollToEnd({animated:true});}}>{p.children}</ScrollView>
  <View style={styles.footer}>{p.footer}</View>
 </View>;
}
const styles=StyleSheet.create({
 root:{flex:1,backgroundColor:color.field},
 header:{paddingHorizontal:space.gutter,flexDirection:'row',alignItems:'center',justifyContent:'space-between',minHeight:48},
 brand:{flexDirection:'row',alignItems:'center',gap:12},
 content:{paddingHorizontal:space.gutter,paddingTop:16,paddingBottom:24,gap:16},
 footer:{paddingHorizontal:space.gutter,paddingVertical:8,borderTopWidth:1,borderColor:color.line,backgroundColor:color.field},
});
