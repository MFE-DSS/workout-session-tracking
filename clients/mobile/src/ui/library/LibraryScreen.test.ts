import React,{act} from 'react';
import {createRoot,type Root} from 'test-renderer';
import witness from '../../../test/libraryWitness.json';
import {LibraryScreen,type LibraryScreenProps} from './LibraryScreen';
import {decodeLibraryDetail,type LibraryPage,type LibraryDetail} from '../../api/library';
jest.mock('react-native-safe-area-context',()=>({useSafeAreaInsets:()=>({top:47,bottom:34,left:0,right:0})}));
let root:Root;beforeEach(()=>{root=createRoot();});afterEach(async()=>{await act(async()=>root.unmount());});
const findNode=(id:string)=>root.container.queryAll(n=>n.props.testID===id)[0];
const node=(id:string)=>findNode(id)?.props;
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
 expect(node('library-verify')?.accessibilityLabel).toBe('Vérifier le départ');expect(node('library-confirm-start')).toBeUndefined();
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
 expect(node('library-session-qa-session-one')?.accessibilityLabel).toContain('série 1 : 8–12 rép.');expect(node('library-session-qa-session-two')).toBeDefined();
 await press('library-session-qa-session-two');expect(selected).toBe('qa-session-two');
 expect(allText()).not.toContain('Lundi');expect(allText()).not.toContain('Programme actif');expect(node('library-ask-start')).toBeUndefined();
});
test('DA07 catalogue structure uses exact exercise slots and never inferred muscle zones',async()=>{
 const p=props(),e=p.state.index.value!.entries[0];e.counts={sessions:1,exercise_slots:7,prescribed_sets:21,count_state:'KNOWN'};
 await act(async()=>root.render(React.createElement(LibraryScreen,p)));
 expect(node('library-structure-'+e.source_ref)?.accessibilityLabel).toBe('7 exercices · 21 séries prévues');
 e.counts={sessions:null,exercise_slots:null,prescribed_sets:null,count_state:'UNKNOWN'};
 await act(async()=>root.render(React.createElement(LibraryScreen,p)));
 expect(node('library-structure-'+e.source_ref)?.accessibilityLabel).toBe('Composition inconnue');
});


test('whole review I2/M1: known session notes and actual technique remain consultable without native start support',async()=>{
 const p=props(),d=clone(witness.detail) as LibraryDetail;d.composition[0].notes='Consigne de séance synthétique';d.composition[0].exercises[0].rep_targets[0].technique='RP';
 p.state.view='DETAIL';p.state.detail={status:'confirmed',previous:false,value:d};await act(async()=>root.render(React.createElement(LibraryScreen,p)));
 await press('library-sources');expect(allText()).toContain('Consigne de séance synthétique');expect(allText()).toContain('RP');
});

function showDetail(p:LibraryScreenProps,d:LibraryDetail,ref=d.composition[0].source_ref){
 p.state.view='DETAIL';
 p.state.selectedRef=ref;
 p.state.detail={status:'confirmed',previous:false,value:d};
}

function fixtureSourceRef(value:Pick<LibraryDetail['source'],'kind'|'id'|'program_id'>){
 const [encoded,digest]=witness.created.source_ref.split('.');
 const ref=JSON.parse(atob(encoded.replace(/-/g,'+').replace(/_/g,'/')));
 ref.value=value;
 return btoa(JSON.stringify(ref)).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'')+'.'+digest;
}

function ownedProgramFixture(){
 const detail=clone(witness.detail) as LibraryDetail;
 const identity={kind:'OWNED_PROGRAM',id:12,program_id:null} as const;
 const sourceRef=fixtureSourceRef(identity);
 const session=detail.composition[0];
 session.source_ref=fixtureSourceRef({kind:'OWNED_SESSION',id:19,program_id:identity.id});
 session.selection={...session.selection,domain_launchable:false,selection_ref:null};
 session.exercises=session.exercises.map(e=>({...e,code:null,machine_slug:null,machine_family:null}));
 detail.source={...identity,name:'Mon programme',status:'VALIDATED',version:1};
 detail.selection=null;
 return {detail,sourceRef};
}

test('a decoded partial owned programme qualifies the received targets on its session row',async()=>{
 const p=props(),{detail,sourceRef}=ownedProgramFixture(),session=detail.composition[0];
 detail.limitations.push('PRESCRIPTION_PARTIAL');
 session.exercises[0].rep_targets.unshift({
  set_index:1,min_reps:4,max_reps:4,technique:null,is_warmup:true,
 });
 const decoded=decodeLibraryDetail(detail,witness.page.owner_id,sourceRef);
 expect(decoded).not.toBeNull();
 showDetail(p,decoded!,sourceRef);
 p.state.index.value!.entries=[{
  ...p.state.index.value!.entries[0],source_ref:sourceRef,kind:'OWNED_PROGRAM',section:'programs',
  name:detail.source.name,source_status:'VALIDATED',
  counts:{sessions:1,exercise_slots:1,prescribed_sets:2,count_state:'KNOWN'},
 }];
 const select=jest.fn();
 p.onSelect=select;
 await act(async()=>root.render(React.createElement(LibraryScreen,p)));
 const sessionId='library-session-'+session.source_ref;
 expect(node(sessionId)?.accessibilityLabel).toContain('1. qa-http · 2 séries reçues · 1 préparation reçue');
 expect(node(sessionId)?.accessibilityLabel).toContain('préparation 1 : 4 rép. ; série 1 : 8–12 rép. ; série 2 : 8–12 rép.');
 expect(allText()).toContain('Prescription partielle');
 expect(node('library-structure-'+sourceRef)).toBeUndefined();
 expect(node('library-ask-start')).toBeUndefined();
 await press(sessionId);
 expect(select.mock.calls).toEqual([[session.source_ref]]);
 await press('library-sources');
 expect(allText()).toContain('Composition reçue · programme personnel, version 1 · source #12');
});

test('a decoded partial owned programme with empty composition reports that no sessions were received',async()=>{
 const p=props(),{detail,sourceRef}=ownedProgramFixture();
 detail.limitations.push('PRESCRIPTION_PARTIAL');
 detail.composition=[];
 const decoded=decodeLibraryDetail(detail,witness.page.owner_id,sourceRef);
 expect(decoded).not.toBeNull();
 showDetail(p,decoded!,sourceRef);
 await act(async()=>root.render(React.createElement(LibraryScreen,p)));
 expect(allText()).toContain('Prescription partielle');
 expect(allText()).toContain('Aucune séance reçue pour ce programme.');
 expect(allText()).not.toContain('Aucune séance dans ce programme.');
});

function annotatedTargets(exerciseNumber:number){
 return Array.from({length:100},(_,i)=>({
  set_index:i+1,min_reps:8,max_reps:12,technique:`Méthode ${exerciseNumber}/${i+1}`,is_warmup:i===0,
 }));
}

function mountedTechniqueSources(){
 return root.container.queryAll(n=>Array.isArray(n.props.children)&&n.props.children.includes(' · méthode déclarée : '))
  .map(n=>text(n.props.children));
}

test('Sources et limites pages through 100 annotated targets with an exact remaining count',async()=>{
 const p=props(),detail=clone(witness.detail) as LibraryDetail;
 const session=detail.composition[0],exercise=session.exercises[0];
 exercise.rep_targets=annotatedTargets(1);
 const decoded=decodeLibraryDetail(detail,witness.page.owner_id,session.source_ref);
 expect(decoded).not.toBeNull();
 showDetail(p,decoded!);
 await act(async()=>root.render(React.createElement(LibraryScreen,p)));
 expect(mountedTechniqueSources()).toHaveLength(0);
 await press('library-sources');
 expect(mountedTechniqueSources()).toHaveLength(8);
 expect(mountedTechniqueSources()[0]).toBe('Synthetic unmapped exercise · préparation 1 · méthode déclarée : Méthode 1/1');
 expect(node('library-more-techniques')?.accessibilityLabel).toBe('Afficher la suite · 92 méthodes restantes');
 await press('library-more-techniques');
 expect(mountedTechniqueSources()).toHaveLength(8);
 expect(mountedTechniqueSources()[0]).toContain('Méthode 1/9');
 expect(node('library-more-techniques')?.accessibilityLabel).toBe('Afficher la suite · 84 méthodes restantes');
 await press('library-last-techniques');
 expect(mountedTechniqueSources()).toHaveLength(4);
 expect(mountedTechniqueSources().at(-1)).toBe('Synthetic unmapped exercise · série 100 · méthode déclarée : Méthode 1/100');
 expect(node('library-more-techniques')).toBeUndefined();
 await press('library-previous-techniques');
 expect(mountedTechniqueSources()).toHaveLength(8);
 expect(mountedTechniqueSources().at(-1)).toContain('Méthode 1/96');
 expect(node('library-more-techniques')?.accessibilityLabel).toBe('Afficher la suite · 4 méthodes restantes');
 await press('library-first-techniques');
 expect(mountedTechniqueSources()[0]).toContain('Méthode 1/1');
});

test('Sources et limites reaches the last technique of a 10000-target programme in one page change',async()=>{
 const p=props(),{detail,sourceRef}=ownedProgramFixture(),original=detail.composition[0];
 detail.composition=Array.from({length:2},(_,sessionIndex)=>({
  ...original,
  source_ref:fixtureSourceRef({kind:'OWNED_SESSION',id:19+sessionIndex,program_id:detail.source.id}),
  name:`Séance ${sessionIndex+1}`,
  exercises:Array.from({length:50},(_,exerciseIndex)=>{
   const exerciseNumber=50*sessionIndex+exerciseIndex+1;
   return {
    ...original.exercises[0],id:exerciseNumber,position:exerciseIndex+1,name:`Exercice ${exerciseNumber}`,
    rep_targets:annotatedTargets(exerciseNumber),
   };
  }),
 }));
 const decoded=decodeLibraryDetail(detail,witness.page.owner_id,sourceRef);
 expect(decoded).not.toBeNull();
 showDetail(p,decoded!,sourceRef);
 await act(async()=>root.render(React.createElement(LibraryScreen,p)));
 await press('library-sources');
 expect(mountedTechniqueSources()).toHaveLength(8);
 expect(node('library-more-techniques')?.accessibilityLabel).toBe('Afficher la suite · 9992 méthodes restantes');
 await press('library-last-techniques');
 expect(mountedTechniqueSources()).toHaveLength(8);
 expect(mountedTechniqueSources().at(-1)).toBe('Exercice 100 · série 100 · méthode déclarée : Méthode 100/100');
 expect(node('library-more-techniques')).toBeUndefined();
 await press('library-previous-techniques');
 expect(mountedTechniqueSources()).toHaveLength(8);
 expect(mountedTechniqueSources().at(-1)).toContain('Méthode 100/92');
 expect(node('library-more-techniques')?.accessibilityLabel).toBe('Afficher la suite · 8 méthodes restantes');
});

test('partial index counts preserve supplied quantities and never turn missing counts into zero',async()=>{
 const p=props(),entry=p.state.index.value!.entries[0];
 entry.counts={sessions:1,exercise_slots:15,prescribed_sets:null,count_state:'PARTIAL'};
 await act(async()=>root.render(React.createElement(LibraryScreen,p)));
 const structure=findNode('library-structure-'+entry.source_ref);
 expect(structure?.props.accessibilityLabel).toBe('15 exercices · Composition partielle');
 const exerciseCount=findNode('library-exercise-count');
 expect(text(exerciseCount?.props.children)).toContain('15 exercices');
 expect(exerciseCount?.queryAll(n=>n.props.testID==='library-slot-mark')).toHaveLength(8);
 expect(allText()).toContain('+7');
 expect(allText()).not.toContain('0 série');
});

test('owned programme structure stays separate from the catalogue and includes all three known counts',async()=>{
 const p=props(),catalogue=(clone(witness.page) as LibraryPage).entries.find(e=>e.section==='core')!;
 p.state.index.value!.entries=[
  {...catalogue,source_ref:'personal-program',name:'Mon programme',kind:'OWNED_PROGRAM',section:'programs',source_status:'PUBLISHED',
   counts:{sessions:2,exercise_slots:1,prescribed_sets:1,count_state:'KNOWN'}},
  catalogue,
 ];
 await act(async()=>root.render(React.createElement(LibraryScreen,p)));
 const headingsAndEntries=root.container.queryAll(n=>n.props.testID?.startsWith('library-section-')||n.props.testID?.startsWith('library-entry-')).map(n=>n.props.testID);
 expect(headingsAndEntries).toEqual(['library-section-programs','library-entry-personal-program','library-section-core','library-entry-'+catalogue.source_ref]);
 expect(node('library-structure-personal-program')?.accessibilityLabel).toBe('2 séances · 1 exercice · 1 série prévue');
 expect(allText()).toContain('Publié · programme personnel');
});

test('programme sequence bounds the initial modules and lets the last exact source be selected',async()=>{
 const p=props(),d=clone(witness.detail) as LibraryDetail,original=d.composition[0];
 d.source={...d.source,kind:'OWNED_PROGRAM',name:'Programme avec dix séances',status:'PUBLISHED',version:1};
 d.selection=null;
 d.composition=Array.from({length:10},(_,i)=>({...original,source_ref:'session-'+(i+1),name:'Séance '+(i+1)}));
 showDetail(p,d,'program');
 const selected=jest.fn();p.onSelect=selected;
 await act(async()=>root.render(React.createElement(LibraryScreen,p)));
 const sessionIds=()=>findNode('library-sequence')?.queryAll(n=>n.props.accessibilityRole==='button'&&n.props.testID?.startsWith('library-session-')).map(n=>n.props.testID);
 expect(sessionIds()).toEqual(['library-session-session-1','library-session-session-2','library-session-session-3','library-session-session-4','library-session-session-5','library-session-session-6','library-session-session-7','library-session-session-8']);
 expect(node('library-more-sessions')?.accessibilityLabel).toBe('Afficher la suite · 2 séances restantes');
 await press('library-more-sessions');
 expect(sessionIds()?.slice(-2)).toEqual(['library-session-session-9','library-session-session-10']);
 await press('library-session-session-10');
 expect(selected.mock.calls).toEqual([['session-10']]);
});

test('selected session keeps source positions and each actual repetition target with its type and unit',async()=>{
 const p=props(),d=clone(witness.detail) as LibraryDetail,row=d.composition[0],original=row.exercises[0];
 row.exercises=[
  {...original,id:2,position:2,name:'Second exercice',set_scheme:'3x99',rep_targets:[]},
  {...original,id:1,position:1,name:'Premier exercice',rep_targets:[
   {set_index:1,min_reps:4,max_reps:4,technique:null,is_warmup:true},
   {set_index:1,min_reps:8,max_reps:12,technique:null,is_warmup:false},
   {set_index:3,min_reps:5,max_reps:5,technique:null,is_warmup:false},
  ]},
 ];
 showDetail(p,d);
 const ask=jest.fn(),confirm=jest.fn();p.onAskStart=ask;p.onConfirm=confirm;
 await act(async()=>root.render(React.createElement(LibraryScreen,p)));
 const selected=findNode('library-selected-session');
 expect(selected?.queryAll(n=>n.props.testID==='library-ask-start')).toHaveLength(1);
 expect(selected?.queryAll(n=>n.props.testID?.startsWith('library-prescription-unit-')).map(n=>n.props.accessibilityLabel)).toEqual([
  'Préparation 1 · 4 rép. prévues','Série 1 · 8–12 rép. prévues','Série 3 · 5 rép. prévues',
 ]);
 expect(allText().indexOf('Premier exercice')).toBeLessThan(allText().indexOf('Second exercice'));
 expect(allText()).toContain('Prescription non renseignée');
 expect(allText()).not.toContain('99 rép.');
 await press('library-ask-start');
 expect(ask.mock.calls).toEqual([[expect.objectContaining({nativeEvent:{}})]]);expect(confirm).not.toHaveBeenCalled();
 p.state.view='CONFIRM';
 await act(async()=>root.render(React.createElement(LibraryScreen,p)));
 expect(findNode('library-selected-session')?.queryAll(n=>n.props.testID==='library-confirm-start')).toHaveLength(1);
 await press('library-confirm-start');expect(confirm.mock.calls).toEqual([[expect.objectContaining({nativeEvent:{}})]]);
});

test('long exercise prescriptions keep the actual last series available behind an exact count',async()=>{
 const p=props(),d=clone(witness.detail) as LibraryDetail,exercise=d.composition[0].exercises[0];
 exercise.rep_targets=Array.from({length:10},(_,i)=>({set_index:i+1,min_reps:i+1,max_reps:i+1,technique:null,is_warmup:false}));
 showDetail(p,d);
 await act(async()=>root.render(React.createElement(LibraryScreen,p)));
 expect(allText()).not.toContain('10 rép. prévues');
 expect(node('library-more-sets-'+exercise.id)?.accessibilityLabel).toBe('Afficher la suite · 2 séries restantes');
 await press('library-more-sets-'+exercise.id);
 expect(allText()).toContain('10 rép. prévues');
});

test('the hidden suffix still distinguishes a preparation after the eighth target from work',async()=>{
 const p=props(),d=clone(witness.detail) as LibraryDetail,exercise=d.composition[0].exercises[0];
 exercise.rep_targets=Array.from({length:10},(_,i)=>({
  set_index:i+1,min_reps:i+1,max_reps:i+1,technique:null,is_warmup:i===8,
 }));
 showDetail(p,d);
 await act(async()=>root.render(React.createElement(LibraryScreen,p)));
 const more='library-more-sets-'+exercise.id;
 expect(node(more)?.accessibilityLabel).toBe('Afficher la suite · 1 série restante · 1 préparation restante');
 await press(more);
 expect(node('library-prescription-unit-'+exercise.id+'/9/true')?.accessibilityLabel).toBe('Préparation 9 · 9 rép. prévues');
 expect(node('library-prescription-unit-'+exercise.id+'/10/false')?.accessibilityLabel).toBe('Série 10 · 10 rép. prévues');
});

test.each(['VALIDATED','native_unknown','domain_unavailable','other_source','stale_selection'] as const)('a confirmation stays blocked for %s',async condition=>{
 const p=props(),d=clone(witness.detail) as LibraryDetail;
 showDetail(p,d);
 p.state.view='CONFIRM';
 if(condition==='VALIDATED'){d.source.kind='OWNED_SESSION';d.source.status='VALIDATED';}
 if(condition==='native_unknown')d.selection!.native_support={state:'UNKNOWN',reason:'NATIVE_EXECUTION_UNSUPPORTED'};
 if(condition==='domain_unavailable')d.selection!.domain_launchable=false;
 if(condition==='other_source')p.state.selectedRef='different-session';
 if(condition==='stale_selection')p.opening={phase:'refused',code:'stale_selection'};
 await act(async()=>root.render(React.createElement(LibraryScreen,p)));
 expect(node('library-confirm-start')?.accessibilityState.disabled).toBe(true);
});

test('a decoded VALIDATED session with no selection reference offers no start action',async()=>{
 const p=props(),d=clone(witness.detail) as LibraryDetail;
 const sourceRef=fixtureSourceRef({kind:'OWNED_SESSION',id:d.source.id,program_id:12});
 d.source={...d.source,kind:'OWNED_SESSION',program_id:12,status:'VALIDATED',version:3};
 d.selection={domain_launchable:false,native_support:{state:'SUPPORTED',reason:null},selection_ref:null};
 d.composition[0]={
  ...d.composition[0],source_ref:sourceRef,selection:d.selection,
  exercises:d.composition[0].exercises.map(e=>({...e,code:null,machine_slug:null,machine_family:null})),
 };
 const decoded=decodeLibraryDetail(d,witness.page.owner_id,sourceRef);
 expect(decoded).not.toBeNull();
 showDetail(p,decoded!);
 await act(async()=>root.render(React.createElement(LibraryScreen,p)));
 expect(allText()).toContain('Validé · non publié');
 expect(node('library-ask-start')).toBeUndefined();
 expect(node('library-confirm-start')).toBeUndefined();
});

test('UNKNOWN names the exact pending source when available and recovery attaches the owned identity to resume',async()=>{
 const p=props(),entry=p.state.index.value!.entries[0],onVerify=jest.fn(),onResume=jest.fn(),onCancel=jest.fn();
 p.onVerify=onVerify;p.onResume=onResume;p.onCancel=onCancel;
 p.opening={phase:'unknown',pending:{
  owner_id:witness.page.owner_id,backend_scope:'qa',local_id:'d477ea9f-7bd9-4fc4-a679-c50f86a2ad41',local_version:1,
  source_ref:entry.source_ref,selection_ref:witness.detail.selection.selection_ref,method:'POST',path:'/me/library/start',
  payload_json:'{}',digest:'test',created_at_ms:1,state:'SENT_UNKNOWN',resolution_kind:null,creation_outcome:'UNKNOWN',session_id:null,session_profile:null,
 }};
 await act(async()=>root.render(React.createElement(LibraryScreen,p)));
 expect(allText()).toContain('Création initiale inconnue · qa-http');
 expect(node('library-resume-found')).toBeUndefined();
 await press('library-verify');expect(onVerify.mock.calls).toEqual([[expect.objectContaining({nativeEvent:{}})]]);
 p.opening={...p.opening,phase:'owned_found',owned:{session_id:42,session_profile:'PLAN_V3'}};
 await act(async()=>root.render(React.createElement(LibraryScreen,p)));
 expect(allText()).toContain('Création initiale inconnue · qa-http');
 expect(node('library-resume-found')?.accessibilityLabel).toBe('Reprendre la séance #42 · PLAN');
 expect(node('library-verify')).toBeUndefined();
 await press('library-resume-found');expect(onResume.mock.calls).toEqual([[expect.objectContaining({nativeEvent:{}})]]);
 await press('library-cancel-options');expect(onCancel).not.toHaveBeenCalled();
 await press('library-cancel-confirm');expect(onCancel.mock.calls).toEqual([[true]]);
});

test('mapped zones are drawn only for the exact source, including when another source has the same name',async()=>{
 const p=props(),d=clone(witness.detail) as LibraryDetail,entry=p.state.index.value!.entries[0];
 showDetail(p,d);
 p.state.index.value!.entries=[
  {...entry,source_ref:'another-source',zones:{state:'MAPPED',codes:['triceps']}},
  {...entry,zones:{state:'MAPPED',codes:['pecs']}},
 ];
 await act(async()=>root.render(React.createElement(LibraryScreen,p)));
 await press('library-sources');
 expect(findNode('library-zones')?.queryAll(n=>n.props.accessibilityRole==='image').map(n=>n.props.accessibilityLabel)).toEqual(['Pectoraux : zone mise en avant, vue de face']);
 p.state.index.value!.entries.splice(1,1);
 await act(async()=>root.render(React.createElement(LibraryScreen,p)));
 expect(node('library-zones')).toBeUndefined();
});

test('detail labels compatible index attributes and drops them when a newer read of the same reference contradicts the counts',async()=>{
 const p=props(),d=clone(witness.detail) as LibraryDetail,original=d.composition[0],entry=p.state.index.value!.entries[0];
 const sourceRef='stable-program-source';
 d.source={...d.source,kind:'OWNED_PROGRAM',name:'Programme édité',status:'PUBLISHED',version:1};
 d.selection=null;
 d.composition=[{
  ...original,source_ref:'session-one',name:'Séance 1',
  exercises:original.exercises.map(e=>({...e,rep_targets:[
   {set_index:1,min_reps:4,max_reps:4,technique:null,is_warmup:true},
   {set_index:1,min_reps:8,max_reps:12,technique:null,is_warmup:false},
  ]})),
 }];
 p.state.index.value!.entries=[{
  ...entry,kind:'OWNED_PROGRAM',source_ref:sourceRef,name:'Programme édité',source_status:'PUBLISHED',section:'programs',
  counts:{sessions:1,exercise_slots:1,prescribed_sets:1,count_state:'KNOWN'},zones:{state:'MAPPED',codes:['pecs']},
 }];
 showDetail(p,d,sourceRef);
 await act(async()=>root.render(React.createElement(LibraryScreen,p)));
 await press('library-sources');
 const compatibleLabels=allText();
 expect(node('library-structure-'+sourceRef)?.accessibilityLabel).toBe('1 séance · 1 exercice · 1 série prévue');
 expect(node('library-zones')).toBeDefined();

 const newer={...d,read_revision:'a'.repeat(64),source:{...d.source,version:2},composition:[
  ...d.composition,
  {...d.composition[0],source_ref:'session-two',name:'Séance 2',exercises:d.composition[0].exercises.map(e=>({...e,id:e.id+100}))},
 ]};
 showDetail(p,newer,sourceRef);
 await act(async()=>root.render(React.createElement(LibraryScreen,p)));
 expect(node('library-session-session-two')).toBeDefined();
 expect(node('library-structure-'+sourceRef)).toBeUndefined();
 expect(node('library-zones')).toBeUndefined();
 expect(compatibleLabels).toContain('Résumé de la bibliothèque');
 expect(compatibleLabels).toContain('Zones de la lecture de l’index');
});


test('BC sequence keeps each exercise identity attached to its own prescribed units in position order',async()=>{
 const p=props(),d=clone(witness.detail) as LibraryDetail,base=d.composition[0].exercises[0];
 d.source={...d.source,kind:'OWNED_PROGRAM',name:'Programme QA publié',status:'PUBLISHED'};d.selection=null;
 d.composition[0].exercises=[
  {...base,id:92,position:2,name:'Tirage QA',rep_targets:[{set_index:1,min_reps:6,max_reps:6,is_warmup:false,technique:null}]},
  {...base,id:91,position:1,name:'Presse QA',rep_targets:[{set_index:1,min_reps:4,max_reps:4,is_warmup:true,technique:null},...base.rep_targets]},
 ];
 showDetail(p,d);const select=jest.fn(),start=jest.fn();p.onSelect=select;p.onAskStart=start;
 await act(async()=>root.render(React.createElement(LibraryScreen,p)));
 const groups=root.container.queryAll(n=>String(n.props.testID??'').startsWith('library-sequence-exercise-'));
 expect(groups.map(n=>n.props.accessibilityLabel)).toEqual([
  '1. Presse QA · préparation 1 : 4 rép. ; série 1 : 8–12 rép. ; série 2 : 8–12 rép.',
  '2. Tirage QA · série 1 : 6 rép.',
 ]);
 await press('library-session-'+d.composition[0].source_ref);
 expect(select.mock.calls).toEqual([[d.composition[0].source_ref]]);expect(start).not.toHaveBeenCalled();
});


test('review BC-I1: operable sequence reads each displayed movement once, in position order with exact overflow',async()=>{
 const p=props(),d=clone(witness.detail) as LibraryDetail,base=d.composition[0].exercises[0];
 d.source={...d.source,kind:'OWNED_PROGRAM',status:'PUBLISHED'};d.selection=null;
 const six=Array.from({length:6},(_,i)=>({...base.rep_targets[0],set_index:i+1}));
 d.composition[0].exercises=[{...base,id:92,position:2,name:'Deuxième QA',rep_targets:six},{...base,id:91,position:1,name:'Premier QA',rep_targets:six}];
 showDetail(p,d);await act(async()=>root.render(React.createElement(LibraryScreen,p)));
 const label=node('library-session-'+d.composition[0].source_ref).accessibilityLabel;
 expect(label.indexOf('Premier QA')).toBeLessThan(label.indexOf('Deuxième QA'));
 expect(label.match(/série 1 :/g)).toHaveLength(2);expect(label).not.toContain('autres unités reçues');
 d.composition[0].exercises=Array.from({length:9},(_,i)=>({...base,id:100+i,position:i,name:'Mouvement '+i,rep_targets:Array.from({length:9},(_,j)=>({...base.rep_targets[0],set_index:j+1}))}));
 await act(async()=>root.render(React.createElement(LibraryScreen,p)));
 const overflow=node('library-session-'+d.composition[0].source_ref).accessibilityLabel;
 expect(overflow.match(/1 autre unité reçue/g)).toHaveLength(8);expect(overflow).toContain('1 autre exercice reçu');
});
test('review BC-M2: stale selection exposes the existing refresh without permitting a new start',async()=>{
 const p=props(),d=clone(witness.detail) as LibraryDetail;showDetail(p,d);p.opening={phase:'refused',code:'stale_selection'};
 const refresh=jest.fn();p.onRefresh=refresh;await act(async()=>root.render(React.createElement(LibraryScreen,p)));
 expect(node('library-ask-start').accessibilityState.disabled).toBe(true);await press('library-refresh-refusal');
 expect(refresh).toHaveBeenCalledTimes(1);expect(node('library-ask-start').accessibilityState.disabled).toBe(true);
});
