import React,{act} from 'react';
import {createRoot,type Root} from 'test-renderer';
import witness from '../../../test/libraryWitness.json';
import {LibraryScreen,type LibraryScreenProps} from './LibraryScreen';
import type {LibraryPage,LibraryDetail} from '../../api/library';
jest.mock('react-native-safe-area-context',()=>({useSafeAreaInsets:()=>({top:47,bottom:34,left:0,right:0})}));
let root:Root;beforeEach(()=>{root=createRoot();});afterEach(async()=>{await act(async()=>root.unmount());});
const node=(id:string)=>root.container.queryAll((n:any)=>n.props.testID===id)[0]?.props;
const clone=<T,>(v:T):T=>JSON.parse(JSON.stringify(v));
const text=(x:any):string=>Array.isArray(x)?x.map(text).join(''):typeof x==='string'||typeof x==='number'?String(x):x?.props?text(x.props.children):'';
const allText=()=>root.container.queryAll(()=>true).map((n:any)=>text(n.props.children)).join('\n');
const press=async(id:string)=>act(async()=>node(id).onClick({nativeEvent:{},stopPropagation:()=>{},currentTarget:1,target:1}));
function props():LibraryScreenProps{
 const page=clone(witness.page) as LibraryPage;page.entries=page.entries.filter(e=>e.name==='qa-http');
 return {state:{index:{status:'confirmed',previous:false,value:page},detail:{status:'idle',previous:false},selectedRef:null,view:'INDEX'},opening:{phase:'idle'},query:{section:'all',zone:null},onFilter:()=>{},onRefresh:()=>{},onMore:()=>{},onSelect:()=>{},onBack:()=>{},onAskStart:()=>{},onConfirm:()=>{},onVerify:()=>{},onResume:()=>{},onCancel:()=>{},onResumeExisting:()=>{}};
}
test('compact native catalogue opens source detail, never fabricates a recommendation',async()=>{
 const p=props(),selected:string[]=[];p.onSelect=ref=>selected.push(ref);
 await act(async()=>root.render(React.createElement(LibraryScreen,p)));expect(allText()).toContain('qa-http');
 await press('library-entry-'+p.state.index.value!.entries[0].source_ref);expect(selected).toEqual([witness.created.source_ref]);
 expect(allText()).not.toContain('Recommandé');expect(allText()).not.toContain('Démarrer le programme');
});
test('current detail keeps planned prescriptions, unknown context and one clear primary action',async()=>{
 const p=props();p.state.view='DETAIL';p.state.selectedRef=witness.created.source_ref;p.state.detail={status:'confirmed',previous:false,value:clone(witness.detail) as LibraryDetail};
 await act(async()=>root.render(React.createElement(LibraryScreen,p)));
 expect(node('library-ask-start')).toBeDefined();expect(node('library-confirm-start')).toBeUndefined();
 expect(allText()).toContain('8–12 rép. prévues');expect(allText()).toContain('Matériel non confirmé');
 expect(allText()).not.toContain('masse externe totale');await press('library-sources');expect(allText()).toContain('Composition prévue');
});
test('confirmation is a separate explicit action and previous data cannot start',async()=>{
 const p=props();p.state.view='CONFIRM';p.state.selectedRef=witness.created.source_ref;p.state.detail={status:'confirmed',previous:false,value:clone(witness.detail) as LibraryDetail};
 let sent=0;p.onConfirm=()=>sent++;await act(async()=>root.render(React.createElement(LibraryScreen,p)));
 await press('library-confirm-start');expect(sent).toBe(1);
 p.state.detail.previous=true;p.state.detail.status='unknown';await act(async()=>root.render(React.createElement(LibraryScreen,p)));
 expect(node('library-confirm-start')?.accessibilityState.disabled).toBe(true);
});
test('unknown start offers verify and explicit local cancellation, no retry or second start',async()=>{
 const p=props();p.opening={phase:'unknown'};await act(async()=>root.render(React.createElement(LibraryScreen,p)));
 expect(node('library-verify')).toBeDefined();expect(node('library-confirm-start')).toBeUndefined();
 await press('library-cancel-options');expect(allText()).toContain('Cela n’annule aucune séance sur le serveur.');
 expect(node('library-cancel-confirm')).toBeDefined();
});
test('known owned session has resume priority and all interactive targets are at least48dp',async()=>{
 const p=props();p.existingSession={session_id:42,session_profile:'PLAN_V3'};
 await act(async()=>root.render(React.createElement(LibraryScreen,p)));expect(node('library-resume-existing')).toBeDefined();
 const controls=root.container.queryAll((n:any)=>n.props.accessibilityRole==='button'||n.props.accessibilityRole==='radio');
 for(const c of controls)expect(c.props.style.minHeight).toBeGreaterThanOrEqual(48);
});
test('pending and unknown data do not become an empty catalogue',async()=>{
 const p=props();p.state.index={status:'pending',previous:false};await act(async()=>root.render(React.createElement(LibraryScreen,p)));
 expect(allText()).toContain('Lecture de la bibliothèque');expect(allText()).not.toContain('Aucune séance');
 p.state.index={status:'unknown',previous:false};await act(async()=>root.render(React.createElement(LibraryScreen,p)));
 expect(allText()).toContain('Lecture non confirmée');expect(allText()).not.toContain('Aucune séance');
});

test('review I1: session_open cannot enable repeat start when parent existingSession was null',async()=>{
 const p=props();p.state.view='DETAIL';p.state.selectedRef=witness.created.source_ref;p.state.detail={status:'confirmed',previous:false,value:clone(witness.detail) as LibraryDetail};p.opening={phase:'refused',code:'session_open'};
 await act(async()=>root.render(React.createElement(LibraryScreen,p)));
 expect(node('library-ask-start')?.accessibilityState.disabled).toBe(true);expect(node('library-verify')).toBeDefined();
});

test('review I1 follow-through: definite-refusal resume does not claim original creation unknown',async()=>{
 const p=props();p.opening={phase:'owned_found',code:'session_open',owned:{session_id:42,session_profile:'PLAN_V3'}};
 await act(async()=>root.render(React.createElement(LibraryScreen,p)));
 expect(allText()).toContain('Séance déjà ouverte');expect(allText()).not.toContain('Création initiale inconnue');
 expect(node('library-resume-found')).toBeDefined();expect(node('library-cancel-options')).toBeUndefined();
});


test('DA07 sequence shows the real ordered session names and prescribed units without a calendar',async()=>{
 const p=props(),d=clone(witness.detail) as LibraryDetail;
 d.source={...d.source,kind:'OWNED_PROGRAM',name:'Programme QA publié',status:'PUBLISHED',program_id:null};
 d.selection=null;d.composition=[{...d.composition[0],source_ref:'qa-session-one',name:'Séance QA 1'},{...d.composition[0],source_ref:'qa-session-two',name:'Séance QA 2'}];
 p.state.view='DETAIL';p.state.detail={status:'confirmed',previous:false,value:d};let selected='';p.onSelect=ref=>selected=ref;
 await act(async()=>root.render(React.createElement(LibraryScreen,p)));
 expect(node('library-sequence')).toBeDefined();
 expect(node('library-session-qa-session-one')).toBeDefined();expect(node('library-session-qa-session-two')).toBeDefined();
 await press('library-session-qa-session-two');expect(selected).toBe('qa-session-two');
 expect(allText()).not.toContain('Lundi');expect(allText()).not.toContain('Programme actif');expect(node('library-ask-start')).toBeUndefined();
});
test('DA07 catalogue structure uses exact exercise slots and never inferred muscle zones',async()=>{
 const p=props(),e=p.state.index.value!.entries[0];e.counts={sessions:1,exercise_slots:7,prescribed_sets:21,count_state:'KNOWN'};
 await act(async()=>root.render(React.createElement(LibraryScreen,p)));
 expect(node('library-structure-'+e.source_ref)?.accessibilityLabel).toBe('7 exercices · 21 séries prévues');
 e.counts={sessions:null,exercise_slots:null,prescribed_sets:null,count_state:'UNKNOWN'};
 await act(async()=>root.render(React.createElement(LibraryScreen,p)));
 expect(node('library-structure-'+e.source_ref)).toBeUndefined();expect(allText()).toContain('Composition partiellement connue');
});


test('whole review I2/M1: known session notes and actual technique remain consultable without native start support',async()=>{
 const p=props(),d=clone(witness.detail) as LibraryDetail;d.composition[0].notes='Consigne de séance synthétique';d.composition[0].exercises[0].rep_targets[0].technique='RP';
 p.state.view='DETAIL';p.state.detail={status:'confirmed',previous:false,value:d};await act(async()=>root.render(React.createElement(LibraryScreen,p)));
 await press('library-sources');expect(allText()).toContain('Consigne de séance synthétique');expect(allText()).toContain('RP');
});
