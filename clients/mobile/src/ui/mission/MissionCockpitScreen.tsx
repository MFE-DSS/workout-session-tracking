import React,{useState} from 'react';
import {StyleSheet,Text,View,useWindowDimensions} from 'react-native';
import {useSafeAreaInsets} from 'react-native-safe-area-context';
import type {HistoricalMission} from '../../api/missionAction';
import {scheme} from '../../domain/format';
import {EmbeddedAction} from '../body/EmbeddedAction';
import {BodyMapTriptych} from '../bodymap/BodyMapTriptych';
import {zoneGridHeight} from '../bodymap/triptychLayout';
import {presetForZone,type BodyMapViewPreset} from '../bodymap/viewPresets';
import {NumericReadout} from '../instrument/NumericReadout';
import {color,space,type} from '../theme';
import {MissionCockpitFrame} from './MissionCockpitFrame';

type Props={mission:HistoricalMission;busy?:boolean;onStart:(slug:string)=>void;onOpenLab:()=>void;onSecondaryOpened:()=>void};
/** No new source of authority: READY is still selected and guarded by ConnectedApp. */
export function MissionCockpitScreen(p:Props){
 // Disclosure belongs to this exact source identity; it cannot carry an old movement into another mission.
 return <ReadyInstrument key={p.mission.template.slug} {...p}/>;
}
function ReadyInstrument(p:Props){
 const m=p.mission,[preparing,setPreparing]=useState(false),[why,setWhy]=useState(false);
 const {width,fontScale}=useWindowDimensions(),insets=useSafeAreaInsets();
 const presets=[...new Set((m.zones??[]).map(z=>presetForZone(z.zone)).filter((x):x is BodyMapViewPreset=>x!==undefined))];
 const remainingLimits=m.reason.limiting.filter(limit=>!m.reason.reasons.some(reason=>reason.includes(limit)));
 const start=(slug:string)=>{if(!p.busy)p.onStart(slug);};
 const identity=<View style={{flexDirection:fontScale>=1.25?'column':'row',gap:8,alignItems:'flex-start'}}>
  <Text accessibilityRole="header" style={[type.bodyStrong,{fontSize:19,lineHeight:25,flexShrink:1,minWidth:0},fontScale<1.25?{flex:1}:null]}>{m.template.name}</Text>
  <Text style={[type.small,{flexShrink:1,maxWidth:fontScale>=1.25?'100%':'40%'}]}>Séance proposée</Text>
 </View>;
 return <MissionCockpitFrame identity={identity} revealEnd={preparing} menu={<EmbeddedAction label="Options" onPress={p.onOpenLab}/>} footer={
  <View style={[styles.command,{flexDirection:fontScale>=1.25?'column':'row'}]}>
   <EmbeddedAction testID="mission-prepare" label="Préparer" expanded={preparing} active={preparing} onPress={()=>setPreparing(!preparing)}/>
   <EmbeddedAction testID="start" label={p.busy?'Démarrage…':'Démarrer'} primary busy={!!p.busy} disabled={!!p.busy} onPress={()=>start(m.template.slug)}/>
  </View>}>
  <View style={styles.instrument}>
   {m.template.subtitle&&!presets.length?<Text style={type.small}>{m.template.subtitle}</Text>:null}
   <View style={[styles.scope,{flexDirection:fontScale>=1.25?'column':'row',flexWrap:'wrap'}]}>
    <Scope value={m.scope.exercise_count} label={m.scope.exercise_count===1?'exercice':'exercices'}/>
    <Scope value={m.scope.work_set_count} label="séries de travail"/>
   </View>
  </View>
  {presets.length?<View testID="mission-zones" style={{marginHorizontal:-space.gutter}}>
   <BodyMapTriptych width={Math.max(1,width-insets.left-insets.right)} height={zoneGridHeight(presets.length)} presets={presets}/>
  </View>:null}
  <View style={styles.reason}><Text style={[type.bodyStrong,{color:color.system}]}>{historicalPhrase(m.reason.phrase)}</Text>
   <EmbeddedAction testID="mission-why" label="Sources et autres séances" expanded={why} onPress={()=>{if(!why)p.onSecondaryOpened();setWhy(!why);}}/>
  </View>
  {preparing&&m.scope.first_exercise?<View testID="mission-preparation-content" style={styles.preparation}>
   <Text style={type.eyebrow}>Premier mouvement</Text>
   <Text style={type.bodyStrong}>{m.scope.first_exercise.name}</Text>
   {m.scope.first_exercise.set_scheme?<Text style={type.body}>{scheme(m.scope.first_exercise.set_scheme)}</Text>:null}
  </View>:null}
  {why?<View testID="mission-source-content" style={{gap:12}}>
   <Text style={type.eyebrow}>Explication héritée — couverture et récupération non qualifiées</Text>
   <Text style={type.small}>{m.reason.phrase}</Text>
   <Text style={type.small}>Séances terminées retenues ; identité du modèle, sans preuve sur ses muscles.</Text>
   {m.reason.reasons.filter(r=>r!==m.reason.phrase).map((r,i)=><Text key={i} style={type.small}>{r}</Text>)}
   {m.reason.provenance?<Text style={type.small}>{mappingProvenance(m.reason.provenance)}</Text>:null}
   {m.reason.horizon?<><Text style={type.small}>{`Séries de travail complétées enregistrées · ${m.reason.horizon}`}</Text>
    <Text style={type.small}>Fenêtre du moteur sur la date de début des séances ; bornes datées non fournies par cette lecture.</Text></>:null}
   <Text style={type.small}>Aucune disponibilité musculaire qualifiée.</Text>
   {remainingLimits.length?<Text style={type.small}>{remainingLimits.join(' · ')}</Text>:null}
   {m.alternatives.map(a=><View key={a.slug} style={styles.alternative}>
    <Text style={type.bodyStrong}>{a.name}</Text><Text style={type.small}>{historicalPhrase(a.phrase)}</Text>{a.phrase.startsWith('Jamais fait.')?<Text style={type.small}>{`Trace de l’alternative : ${a.phrase}`}</Text>:null}
    <EmbeddedAction testID={'mission-alternative-'+a.slug} label={'Démarrer plutôt '+a.name} disabled={!!p.busy||!a.executable} onPress={()=>{if(a.executable)start(a.slug);}}/>
   </View>)}
  </View>:null}
 </MissionCockpitFrame>;
}
// Wording only: the untouched engine trace remains available in disclosure/source receipts.
// A missing template KPI is not evidence that its muscles have never worked.
function historicalPhrase(phrase:string){
 const prefix='Jamais fait.';
 return phrase.startsWith(prefix)?'Ce modèle de séance : aucun passage terminé retrouvé.'+phrase.slice(prefix.length):phrase;
}
function mappingProvenance(value:string){
 if(value==='mesurée')return 'Cartographie dans l’historique retenu : aucune zone inconnue signalée par le moteur.';
 if(value==='partielle')return 'Cartographie partielle dans l’historique retenu : au moins un exercice non classé.';
 return `Provenance transmise par le moteur : ${value}`;
}
function Scope(p:{value:number;label:string}){
 return <View style={{flexDirection:'row',alignItems:'baseline',gap:8,flexWrap:'wrap',flexShrink:1,maxWidth:'100%'}} accessible accessibilityLabel={`${p.value} ${p.label}`}>
  <NumericReadout value={String(p.value)} role={type.figure}/><Text style={type.small}>{p.label}</Text>
 </View>;
}
const styles=StyleSheet.create({
 instrument:{gap:12,paddingVertical:12,borderBottomWidth:1,borderColor:color.line},
 scope:{gap:24,paddingTop:12},command:{alignItems:'stretch',justifyContent:'space-between',backgroundColor:color.plate,borderRadius:16},
 reason:{borderLeftWidth:2,borderLeftColor:color.system,paddingLeft:12,gap:4},
 preparation:{gap:8,paddingVertical:12,borderTopWidth:1,borderColor:color.line},
 alternative:{gap:4,borderTopWidth:1,borderColor:color.line,paddingTop:12},
});
