import React,{useState} from 'react';
import {Text,View,useWindowDimensions} from 'react-native';
import Svg,{Circle} from 'react-native-svg';
import type {WeightWindowState} from '../../api/trainingHistoryResource';
import {CalibrationLink} from '../plan/calibrationControls';
import {color,type,space} from '../theme';
import {dateLabel,numeric,weightGeometry,weightExtent} from './historyView';
export function WeightTrend(p:{state:WeightWindowState;onMore:()=>void}){
 const [list,setList]=useState(false),{width}=useWindowDimensions(),s=p.state,w=Math.max(160,width-space.gutter*2),h=96;
 if(s.status==='consent_required')return <Text testID="progress-weight-consent" style={type.small}>Un accord est nécessaire pour consulter les mesures. Gère cet accord depuis Profil.</Text>;
 if(['unavailable','rejected','idle'].includes(s.status))return <Text style={type.small}>Mesures indisponibles.</Text>;
 const points=weightGeometry(s.entries,w,h),extent=weightExtent(s.entries),latest=s.entries.find(e=>e.quality==='KNOWN'&&e.value!==null);
 return <View style={{gap:8}}>
  {s.previous?<Text style={type.small}>Lecture précédente · à actualiser</Text>:null}
  {s.status==='pending'?<Text style={type.small}>Lecture des mesures…</Text>:null}
  {s.status==='unknown'?<Text style={type.small}>Lecture incomplète. Aucune nouvelle mesure n’est supposée.</Text>:null}
  {latest?<View style={{flexDirection:'row',alignItems:'baseline',gap:8,flexWrap:'wrap'}}><Text style={type.figure}>{numeric(latest.value!)} kg</Text><Text style={type.small}>{dateLabel(latest.measured_at,s.window?.time_zone)}</Text></View>:null}
  {extent?<Text testID="progress-weight-scale" style={type.small}>Échelle : {numeric(extent.low)}{extent.high!==extent.low?`–${numeric(extent.high)}`:''} kg</Text>:null}
  {points.length?<View testID="progress-weight-chart" accessible={false} importantForAccessibility="no-hide-descendants"><Svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} accessible={false}>{points.map(q=><Circle key={q.id} cx={q.x} cy={q.y} r={3.5} fill={color.ink}/>)}</Svg><View testID="progress-weight-dates" style={{flexDirection:'row',justifyContent:'space-between',flexWrap:'wrap',gap:8}}><Text style={type.small}>{extent?dateLabel(extent.from,s.window?.time_zone):''}</Text>{extent&&extent.until!==extent.from?<Text style={type.small}>{dateLabel(extent.until,s.window?.time_zone)}</Text>:null}</View><Text style={type.small}>Points mesurés · sans interpolation</Text></View>:null}
  {!s.entries.length&&s.status==='confirmed'?<Text style={type.small}>{s.coverage==='COMPLETE'?'Aucune mesure dans cette période.':'Recherche des mesures incomplète.'}</Text>:null}
  {s.entries.length?<CalibrationLink label={list?'Masquer les mesures':'Voir les mesures'} expanded={list} onPress={()=>setList(!list)}/>:null}
  {list?<View style={{gap:12}}>{s.entries.map(e=><View key={e.measurement_id} accessible accessibilityLabel={`${dateLabel(e.measured_at,s.window?.time_zone)}, ${e.quality==='KNOWN'?`${numeric(e.value!)} kilogrammes`:'valeur non comparable'}, mesure ${e.measurement_id}`}>
   <Text style={type.bodyStrong}>{dateLabel(e.measured_at,s.window?.time_zone)} · {e.quality==='KNOWN'?`${numeric(e.value!)} kg`:'Valeur non comparable'}</Text>
   <Text selectable style={type.small}>{e.quality!=='KNOWN'?`Valeur source : ${e.value??e.raw_value_repr} · `:''}Saisie {e.recorded_at?dateLabel(e.recorded_at,s.window?.time_zone):'non datée'} · origine non documentée</Text>
  </View>)}</View>:null}
  {s.canContinue?<CalibrationLink label="Continuer la lecture" onPress={p.onMore}/>:null}
 </View>;
}
