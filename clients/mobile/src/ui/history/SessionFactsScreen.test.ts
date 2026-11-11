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
test('detail back and disclosures keep 48dp touch targets',async()=>{
 await legacy();const controls=root.container.queryAll((n:any)=>n.props.accessibilityRole==='button');expect(controls.length).toBeGreaterThan(1);
 for(const c of controls)expect(c.props.style.minHeight).toBeGreaterThanOrEqual(48);
});
test('zero, absent and invalid facts stay distinct without substituting a prescription',async()=>{
 const f=legacyFacts();f.exercises[0].sets[0]={...f.exercises[0].sets[0],weight_kg:0,reps:0};await legacy(f);
 expect(text(node('history-load-31').children)).toBe('0 kg saisis');expect(text(node('history-reps-31').children)).toBe('0 rép.');
 f.exercises[0].sets[0]={...f.exercises[0].sets[0],weight_kg:null,reps:null,completed:false,completed_at:null};await legacy(f);
 expect(allText()).toContain('Aucun fait enregistré');expect(allText()).toContain('Charge inconnue');
 f.exercises[0].sets[0]={...f.exercises[0].sets[0],raw_weight_repr:'inf'};await legacy(f);
 expect(allText()).toContain('Charge invalide');await press('history-provenance-21');expect(allText()).toContain('inf');
});
test('SCI per-implement and machine observations retain their typed units as primary facts',async()=>{
 const sci=scienceHistory();await act(async()=>root.render(React.createElement(SessionFactsScreen,{detail:{kind:'SCI',execution:{...sci.execution,contract_version:'first-plan-execution/3.0.0',status:'completed',derived_metrics:'NON_EVALUABLE'}},timeZone:'UTC',onBack:()=>{}})));
 expect(allText()).toContain('20 kg par haltère');expect(allText()).toContain('17,5 kg affichés');expect(allText()).not.toContain('40 kg');
 expect(allText()).not.toContain('Prescription capturée :');
});
test('an incomplete SCI observation remains an observed fact when load and repetitions are unknown',async()=>{
 const sci=scienceHistory(),e=sci.execution.exercises[0],s=e.sets[0];
 e.sets=[{...s,completed:false,reps:null,completed_at:null,observation:{...s.observation,setting:null,reps:null,completed:false}}];
 sci.execution.exercises=[e];
 await act(async()=>root.render(React.createElement(SessionFactsScreen,{detail:{kind:'SCI',execution:{...sci.execution,contract_version:'first-plan-execution/3.0.0',status:'completed',derived_metrics:'NON_EVALUABLE'}},timeZone:'UTC',onBack:()=>{}})));
 expect(allText()).toContain('Non complétée');expect(allText()).not.toContain('Aucun fait enregistré');
 expect(allText()).toContain('Charge inconnue');expect(allText()).toContain('Répétitions inconnues');
 await press(`history-provenance-${e.se_id}`);expect(allText()).toContain('Occurrence déclarée');
});
