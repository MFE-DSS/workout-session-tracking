import React,{act} from 'react';
import {createRoot,type Root} from 'test-renderer';
import {legacyFacts,scienceHistory} from '../../../test/trainingHistoryHarness';
import {SessionFactsScreen} from './SessionFactsScreen';
jest.mock('react-native-safe-area-context',()=>({useSafeAreaInsets:()=>({top:24,bottom:24,left:0,right:0})}));
let root:Root;beforeEach(()=>{root=createRoot();});afterEach(async()=>{await act(async()=>root.unmount());});
const node=(id:string)=>root.container.queryAll((n:any)=>n.props.testID===id)[0]?.props;
const text=(x:any):string=>Array.isArray(x)?x.map(text).join(''):typeof x==='string'||typeof x==='number'?String(x):x?.props?text(x.props.children):'';
const allText=()=>root.container.queryAll(()=>true).map((n:any)=>text(n.props.children)).join('\n');
async function press(id:string){await act(async()=>node(id).onClick({nativeEvent:{},stopPropagation:()=>{},currentTarget:1,target:1}));}
async function legacy(facts=legacyFacts()){
 await act(async()=>root.render(React.createElement(SessionFactsScreen,{detail:{kind:'LEGACY',facts},timeZone:'UTC',onBack:()=>{}})));
}
test('compact history keeps numeric entered facts and one visible uncertainty, with exact provenance on demand',async()=>{
 await legacy();expect(node('history-session-title').style.fontSize).toBeLessThanOrEqual(20);
 expect(text(node('history-load-31').children)).toBe('17,5 kg saisis');expect(text(node('history-reps-31').children)).toBe('9 rép.');
 expect(node('history-context-21').children).toBe('Matériel non capturé');expect(allText()).toContain('Terminée');
 expect(allText()).not.toContain('masse externe totale');expect(allText()).not.toContain('2026-11-09T10:05:00Z');
 await press('history-provenance-21');expect(allText()).toContain('masse externe totale');expect(allText()).toContain('2026-11-09T10:05:00Z');
 expect(allText()).toContain('Journal historique');
});
test('Legacy sources identify a completed set whose journal timestamp is absent',async()=>{
 const f=legacyFacts();
 f.exercises[0].sets[0].completed_at=null;
 await legacy(f);
 expect(allText()).toContain('Complétée');
 expect(allText()).not.toContain('horodatage du journal non renseigné');
 await press('history-provenance-21');
 expect(allText()).toContain('Série 1 · horodatage du journal non renseigné');
});
test('detail back and disclosures keep 48dp touch targets',async()=>{
 await legacy();const controls=root.container.queryAll((n:any)=>n.props.accessibilityRole==='button');expect(controls.length).toBeGreaterThan(1);
 for(const c of controls)expect(c.props.style.minHeight).toBeGreaterThanOrEqual(48);
});
test('zero, absent and invalid facts stay distinct without substituting a prescription',async()=>{
 const f=legacyFacts();f.exercises[0].sets[0]={...f.exercises[0].sets[0],weight_kg:0,reps:0};await legacy(f);
 expect(text(node('history-load-31').children)).toBe('0 kg saisis');expect(text(node('history-reps-31').children)).toBe('0 rép.');
 f.exercises[0].sets[0]={...f.exercises[0].sets[0],weight_kg:null,reps:null,completed:false,completed_at:null};await legacy(f);
 expect(allText()).toContain('Aucun fait enregistré');
 expect(node('history-load-31')).toBeUndefined();expect(node('history-reps-31')).toBeUndefined();
 f.exercises[0].sets[0]={...f.exercises[0].sets[0],raw_weight_repr:'inf'};await legacy(f);
 expect(allText()).toContain('Charge invalide');await press('history-provenance-21');expect(allText()).toContain('inf');
});
test('SCI per-implement and machine observations retain their typed units as primary facts',async()=>{
 const sci=scienceHistory();await act(async()=>root.render(React.createElement(SessionFactsScreen,{detail:{kind:'SCI',execution:{...sci.execution,contract_version:'first-plan-execution/3.0.0',status:'completed',derived_metrics:'NON_EVALUABLE'}},timeZone:'UTC',onBack:()=>{}})));
 expect(allText()).toContain('20 kg par haltère');expect(allText()).toContain('17,5 kg affichés');expect(allText()).not.toContain('40 kg');
 expect(allText()).toContain('Heure approximative');
 const e=sci.execution.exercises[0],s=e.sets[0];
 expect(allText()).not.toContain(e.prescription.context.equipment_ref);
 await press(`history-provenance-${e.se_id}`);
 expect(allText()).toContain(e.prescription.context.equipment_ref);
 expect(allText()).toContain(e.prescription.context.context_ref);
 expect(allText()).toContain(s.observation.performed_at);
 expect(allText()).toContain('version 1');
 expect(allText()).not.toContain('Prescription capturée :');
});
test('SCI sources retain the unknown journal time and qualify the exact occurrence timestamp',async()=>{
 const sci=scienceHistory(),e=sci.execution.exercises[0],s=e.sets[0];
 s.completed_at=null;
 e.sets=[s];
 sci.execution.exercises=[e];
 await act(async()=>root.render(React.createElement(SessionFactsScreen,{detail:{kind:'SCI',execution:{...sci.execution,contract_version:'first-plan-execution/3.0.0',status:'completed',derived_metrics:'NON_EVALUABLE'}},timeZone:'UTC',onBack:()=>{}})));
 await press(`history-provenance-${e.se_id}`);
 expect(allText()).toContain('horodatage du journal non renseigné');
 expect(allText()).toContain(`Occurrence déclarée · ${s.observation.performed_at} · heure approximative`);
});
test('an incomplete SCI observation remains an observed fact when load and repetitions are unknown',async()=>{
 const sci=scienceHistory(),e=sci.execution.exercises[0],s=e.sets[0];
 e.sets=[{...s,completed:false,reps:null,completed_at:null,observation:{...s.observation,setting:null,reps:null,completed:false}}];
 sci.execution.exercises=[e];
 await act(async()=>root.render(React.createElement(SessionFactsScreen,{detail:{kind:'SCI',execution:{...sci.execution,contract_version:'first-plan-execution/3.0.0',status:'completed',derived_metrics:'NON_EVALUABLE'}},timeZone:'UTC',onBack:()=>{}})));
 expect(allText()).toContain('Observation incomplète');expect(allText()).toContain('Non complétée');
 expect(allText()).not.toContain('Aucun fait enregistré');
 expect(node(`history-load-${s.set_id}`).accessibilityLabel).toBe('Charge inconnue');
 expect(node(`history-reps-${s.set_id}`).accessibilityLabel).toBe('Répétitions inconnues');
 await press(`history-provenance-${e.se_id}`);expect(allText()).toContain('Occurrence déclarée');
});

test('the preparation count hides only rows without facts and reveals each original set',async()=>{
 const f=legacyFacts(),exercise=f.exercises[0],work=exercise.sets[0];
 const empty={...work,kind:'warmup',completed:false,weight_kg:null,reps:null,completed_at:null};
 exercise.sets=[
  {...empty,set_id:40,set_index:1},
  {...empty,set_id:41,set_index:2,raw_weight_repr:'NaN'},
  {...empty,set_id:42,set_index:3},
  {...empty,set_id:43,set_index:4,weight_kg:0},
  {...empty,set_id:44,set_index:5,completed_at:'2026-11-09T10:03:00Z'},
  {...empty,set_id:45,set_index:6,kind:'UNKNOWN'},
  work,
 ];
 await legacy(f);
 const disclosure='history-preparations-21';
 expect(node(disclosure)?.accessibilityLabel).toContain('2 préparations');
 expect(node(disclosure).accessibilityState.expanded).toBe(false);
 expect(node('history-set-40')).toBeUndefined();expect(node('history-set-42')).toBeUndefined();
 expect(node('history-set-41')).toBeDefined();expect(node('history-set-43')).toBeDefined();
 expect(node('history-set-44')).toBeDefined();expect(node('history-set-45')).toBeDefined();
 expect(text(node('history-load-43').children)).toBe('0 kg saisis');
 await press(disclosure);
 expect(node(disclosure).accessibilityState.expanded).toBe(true);
 expect(text(node('history-set-40').children)).toContain('Préparation 1');
 expect(text(node('history-set-42').children)).toContain('Préparation 3');
 await press(disclosure);
 expect(node('history-set-40')).toBeUndefined();
});


test('BC source disclosure distinguishes observed context and prescribed side instead of assuming bilateral',async()=>{
 const sci=scienceHistory(),e=sci.execution.exercises[0],s=e.sets[0];
 e.prescription.context={...e.prescription.context,side:'LEFT'};
 s.observation.context={...s.observation.context,side:'RIGHT',equipment_ref:'observed-equipment'};
 e.sets=[s];sci.execution.exercises=[e];
 await act(async()=>root.render(React.createElement(SessionFactsScreen,{detail:{kind:'SCI',execution:{...sci.execution,contract_version:'first-plan-execution/3.0.0',status:'completed',derived_metrics:'NON_EVALUABLE'}},timeZone:'UTC',onBack:()=>{}})));
 await press(`history-provenance-${e.se_id}`);
 expect(allText()).toContain('Contexte prescrit');expect(allText()).toContain('côté gauche');
 expect(allText()).toContain('Contexte observé');expect(allText()).toContain('côté droit');
 expect(allText()).toContain('observed-equipment');expect(allText()).not.toContain(' · bilatéral');
});
