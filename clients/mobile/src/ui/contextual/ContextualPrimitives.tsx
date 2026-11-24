import React,{useState} from 'react';
import {Pressable,Text,View,useWindowDimensions} from 'react-native';
import {RecessedWindow} from '../instrument/RecessedWindow';
import {recessedWindowGeometry} from '../instrument/recessedWindowGeometry';
import {InstrumentFrameC} from '../instrument/InstrumentFrame';
import {frameGeometry} from '../instrument/frameGeometry';
import {densityFor,UNIT} from '../calibration/layout';
import {color,space,type} from '../theme';
export function ContextFrame(p:{children:React.ReactNode|((layout:{width:number;u:number;originY:number})=>React.ReactNode)}){
 const width=useWindowDimensions().width-2*space.gutter,u=UNIT[densityFor(width)],[content,setContent]=useState(0),height=Math.max(100,content+8*u),g=frameGeometry('rail',width,height,u);
 return <InstrumentFrameC width={width} height={height} u={u}><View style={{width:g.content.w,gap:12}} onLayout={e=>setContent(Math.ceil(e.nativeEvent.layout.height))}>{typeof p.children==='function'?p.children({width:g.content.w,u,originY:g.content.y}):p.children}</View></InstrumentFrameC>;
}
export function ContextCommand(p:{label:string;display?:string;onPress:()=>void;primary?:boolean;disabled?:boolean;testID?:string}){
 return <Pressable testID={p.testID} accessibilityRole="button" accessibilityLabel={p.label} accessibilityState={{disabled:!!p.disabled}} disabled={p.disabled} onPress={p.onPress} style={({pressed})=>({minWidth:48,minHeight:48,padding:12,alignItems:'center',justifyContent:'center',backgroundColor:p.primary?color.signal:undefined,opacity:p.disabled?.45:pressed?.65:1})}><Text style={[type.bodyStrong,{color:p.primary?color.onSignal:color.ink2}]}>{p.display??p.label}</Text></Pressable>;
}
export function ContextDisclosure(p:{label:string;children:React.ReactNode}){
 const [open,setOpen]=useState(false);return <View><Pressable accessibilityRole="button" accessibilityLabel={p.label} accessibilityState={{expanded:open}} onPress={()=>setOpen(!open)} style={{minHeight:48,justifyContent:'center'}}><Text style={type.small}>{p.label} {open?'−':'+'}</Text></Pressable>{open?<View style={{gap:8}}>{p.children}</View>:null}</View>;
}

/** Composite adapter: measure content, retain the locked window geometry and parent grid. */
export function ContextWindow(p:{width:number;u:number;testID:string;onTop?:(y:number)=>void;children:React.ReactNode}){
 const [content,setContent]=useState(0),height=Math.max(96,content+4.5*p.u),g=recessedWindowGeometry(p.width,height,p.u);
 return <View onLayout={e=>p.onTop?.(e.nativeEvent.layout.y)}><RecessedWindow width={p.width} height={height} u={p.u} testID={p.testID}><View style={{width:g.content.w,gap:4}} onLayout={e=>setContent(Math.ceil(e.nativeEvent.layout.height))}>{p.children}</View></RecessedWindow></View>;
}
