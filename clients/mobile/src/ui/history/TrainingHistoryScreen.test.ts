import React,{act} from 'react';
import {createRoot,type Root} from 'test-renderer';
import {historyPage,legacyFacts,window4} from '../../../test/trainingHistoryHarness';
import {weightPage} from '../../../test/accountDataHarness';
import {TrainingHistoryScreen,type ProgressProps} from './TrainingHistoryScreen';
jest.mock('react-native-safe-area-context',()=>({useSafeAreaInsets:()=>({top:47,bottom:34,left:0,right:0})}));
let root:Root;beforeEach(()=>{root=createRoot();});afterEach(async()=>{await act(async()=>root.unmount());});
const empty={status:'idle' as const,previous:false};
function props():ProgressProps{return{state:{sessions:{status:'confirmed',previous:false,value:historyPage()},exercises:empty,occurrences:empty,detail:empty,selectedEntry:null,selectedExercise:null},weight:{status:'confirmed',entries:weightPage().entries,previous:false,coverage:'COMPLETE',canContinue:false,window:window4},period:'4w',onPeriod:()=>{},onRefresh:()=>{},onMore:()=>{},onExercises:()=>{},onExercise:()=>{},onMoreExercises:()=>{},onOccurrence:()=>{},onMoreOccurrences:()=>{},onEntry:()=>{},onBack:()=>{},onMoreWeight:()=>{}};}
const node=(id:string)=>root.container.queryAll((n:any)=>n.props.testID===id)[0]?.props;
const screenText=()=>root.container.queryAll(()=>true).flatMap((n:any)=>
 [n.props.children].flat().filter((child:unknown)=>typeof child==='string'||typeof child==='number')
).join(' ');
async function press(id:string){await act(async()=>node(id).onClick({nativeEvent:{},stopPropagation:()=>{},currentTarget:1,target:1}));}
test('one native Progress surface has real counts, explicit period and owner entry selection with no write affordance',async()=>{
 const p=props(),entries:number[]=[];p.onEntry=e=>entries.push(e.session_id);await act(async()=>root.render(React.createElement(TrainingHistoryScreen,p)));
 expect(node('progress-frequency').children).toBe('1');expect(node('progress-period')).toBeDefined();await press('progress-session-11');expect(entries).toEqual([11]);
 expect(node('progress-help-body')).toBeUndefined();await press('progress-help');expect(node('progress-help-body')).toBeDefined();expect(node('progress-weight-write')).toBeUndefined();
});
test('previous/offline facts and zero partial scans cannot be presented as a confirmed empty history',async()=>{
 const p=props();p.state.sessions.status='unknown';p.state.sessions.previous=true;p.state.exercises={status:'confirmed',previous:false,value:{contract_version:'training-exercise-index/1.0.0',owner_id:7,read_id:historyPage().read_id,window:window4,rows_read_at:window4.until,state:'SCANNING',entries:[],scan:'PARTIAL_SCAN',coverage_complete:false,source_inspected:1000,unresolved_count:0,next_cursor:'continue'}};
 await act(async()=>root.render(React.createElement(TrainingHistoryScreen,p)));expect(node('progress-previous')).toBeDefined();expect(node('progress-exercises-partial')).toBeDefined();expect(node('progress-empty-exercises')).toBeUndefined();
});
test('read-only detail keeps unknown legacy context and separate real completion facts',async()=>{
 const p=props();p.state.detail={status:'confirmed',previous:false,value:{kind:'LEGACY',facts:legacyFacts()}};p.state.selectedEntry=11;await act(async()=>root.render(React.createElement(TrainingHistoryScreen,p)));
 expect(node('history-set-31')).toBeDefined();expect(node('history-context-21').children).toBe('Matériel non capturé');expect(node('progress-period')).toBeUndefined();
});
test('consent applies only to weight, never hides canonical session history or manufactures an agreement',async()=>{
 const p=props();p.weight={...p.weight,status:'consent_required',entries:[]};await act(async()=>root.render(React.createElement(TrainingHistoryScreen,p)));
 expect(node('progress-session-11')).toBeDefined();expect(node('progress-weight-consent')).toBeDefined();expect(node('progress-weight-chart')).toBeUndefined();
});
test('SCI historical render keeps per-dumbbell observation and captured prescription behind disclosure',async()=>{
 const {scienceHistory}=require('../../../test/trainingHistoryHarness'),sci=scienceHistory(),p=props();
 const {allowed_actions,applicability,observation_only,cursor,...execution}=sci.execution;
 p.state.detail={status:'confirmed',previous:false,value:{kind:'SCI',execution}};p.state.selectedEntry=11;
 await act(async()=>root.render(React.createElement(TrainingHistoryScreen,p)));
 const text=(x:any):string=>Array.isArray(x)?x.map(text).join(''):typeof x==='string'||typeof x==='number'?String(x):x?.props?text(x.props.children):'';
 const allText=root.container.queryAll(()=>true).map((n:any)=>text(n.props.children)).join('\n');
 expect(allText).toContain('20 kg par haltère');expect(allText).not.toContain('40 kg');expect(allText).not.toContain('Prescription capturée :');
});
test('a large returned page stays compact and its full-period count is not the visible row count',async()=>{
 const p=props(),page=historyPage();page.entries=Array.from({length:10},(_,i)=>({...page.entries[0],session_id:100+i}));
 page.counts={...page.counts,recorded:37,completed:37,completed_with_work:37};page.weekly_counts=Array.from({length:8},(_,i)=>({...page.weekly_counts[0],week_from:`2026-09-${String(1+i).padStart(2,'0')}T00:00:00Z`,completed_with_work:i===0?30:1}));
 p.state.sessions.value=page;await act(async()=>root.render(React.createElement(TrainingHistoryScreen,p)));
 expect(node('progress-frequency').children).toBe('37');expect(node('progress-session-104')).toBeDefined();expect(node('progress-session-105')).toBeUndefined();
 expect(root.container.queryAll((n:any)=>typeof n.props.testID==='string'&&n.props.testID.startsWith('progress-week-'))).toHaveLength(4);
 await press('progress-expand-sessions');expect(node('progress-session-109')).toBeDefined();await press('progress-expand-weeks');
 expect(root.container.queryAll((n:any)=>typeof n.props.testID==='string'&&n.props.testID.startsWith('progress-week-'))).toHaveLength(8);
});
test('weight plot shows its actual numeric scale rather than an unlabeled amplified change',async()=>{
 const p=props();await act(async()=>root.render(React.createElement(TrainingHistoryScreen,p)));
 expect(node('progress-weight-scale')).toBeDefined();expect(node('progress-weight-dates')).toBeDefined();
});

test('opening Mesures uses the existing BODY port even when the agreement is absent',async()=>{
 const p=props(),open=jest.fn();p.onBody=open;p.weight.status='consent_required';
 await act(async()=>root.render(React.createElement(TrainingHistoryScreen,p)));
 expect(node('progress-weight-write').accessibilityLabel).toBe('Ouvrir Mesures');
 expect(root.container.queryAll((n:any)=>n.props.accessibilityLabel==='Mensurations et historique')).toHaveLength(0);
 expect(screenText()).not.toContain('72 kg');
 await press('progress-weight-write');expect(open).toHaveBeenCalledTimes(1);
});

test('weekly frequency retains the received count and identifies the partial current week',async()=>{
 const p=props(),page=historyPage();page.weekly_counts=[{week_from:'2026-11-09T00:00:00Z',week_until:'2026-11-16T00:00:00Z',completed_with_work:8,partial_current_week:true}];
 p.state.sessions.value=page;
 await act(async()=>root.render(React.createElement(TrainingHistoryScreen,p)));
 expect(node('progress-frequency').children).toBe('1');
 const week=node('progress-week-2026-11-09T00:00:00Z');
 expect(week.accessibilityLabel).toContain('8 séances');
 expect(week.accessibilityLabel).toContain('semaine partielle');
 expect(screenText()).not.toMatch(/adhérence|objectif|%/);
});

test('review fix I5: session detail offers exact exercise history and identifies selected occurrence',async()=>{
 const p=props() as any;p.state.selectedEntry=11;p.state.detail={status:'confirmed',previous:false,value:{kind:'LEGACY',facts:{...legacyFacts(),selected_se_id:21},exercise_links:[{se_id:21,name:'Captured exercise',exercise_ref:'e.'+'a'.repeat(64)}]}};
 const selected:any[]=[];p.onDetailExercise=(seId:number,ref:string)=>selected.push([seId,ref]);
 await act(async()=>root.render(React.createElement(TrainingHistoryScreen,p)));
 expect(node('history-selected-exercise-21')).toBeDefined();
 expect(root.container.queryAll((n:any)=>n.props.testID==='history-exercise-21')).toHaveLength(1);
 await press('history-exercise-21');expect(selected).toEqual([[21,'e.'+'a'.repeat(64)]]);
});


test('BC frequency memory shows only actual weeks and exactly the received session marks including zero',async()=>{
 const p=props(),page=historyPage();
 page.weekly_counts=[
  {week_from:'2026-11-02T00:00:00Z',week_until:'2026-11-09T00:00:00Z',completed_with_work:0,partial_current_week:false},
  {week_from:'2026-11-16T00:00:00Z',week_until:'2026-11-23T00:00:00Z',completed_with_work:11,partial_current_week:true},
 ];
 p.state.sessions.value=page;
 await act(async()=>root.render(React.createElement(TrainingHistoryScreen,p)));
 expect(root.container.queryAll(n=>String(n.props.testID??'').startsWith('frequency-mark-2026-11-02'))).toHaveLength(0);
 expect(root.container.queryAll(n=>String(n.props.testID??'').startsWith('frequency-mark-2026-11-16'))).toHaveLength(8);
 expect(screenText()).toContain('+3');
 expect(root.container.queryAll(n=>String(n.props.testID??'').startsWith('progress-week-'))).toHaveLength(2);
 expect(node('progress-week-2026-11-16T00:00:00Z').accessibilityLabel).toContain('11 séances');
 expect(node('progress-week-2026-11-09T00:00:00Z')).toBeUndefined();
});


test('review BC-I2: same-day occurrences remain distinct visible and spoken choices opening their exact refs',async()=>{
 const {occurrencesPage}=require('../../../test/trainingHistoryHarness'),p=props(),page=occurrencesPage();
 const e=page.entries[0];page.entries=[{...e,started_at:'2026-11-09T08:00:00Z',occurrence_ref:'morning'}, {...e,started_at:'2026-11-09T19:00:00Z',occurrence_ref:'evening'}, {...e,started_at:'2026-11-09T20:00:00+01:00',se_id:22,occurrence_ref:'second-slot'}];
 p.state.selectedExercise='exercise';p.state.occurrences={status:'confirmed',previous:false,value:page};const selected:string[]=[];p.onOccurrence=e=>selected.push(e.occurrence_ref);
 await act(async()=>root.render(React.createElement(TrainingHistoryScreen,p)));
 const labels=page.entries.map((e:any)=>node('history-occurrence-'+e.occurrence_ref).accessibilityLabel);
 expect(new Set(labels).size).toBe(3);expect(screenText()).toContain('08:00');expect(screenText()).toContain('19:00');
 for(const e of page.entries)await press('history-occurrence-'+e.occurrence_ref);
 expect(selected).toEqual(['morning','evening','second-slot']);
});
test('review BC-I2: same-name sessions on the same day retain distinct identity and callbacks',async()=>{
 const p=props(),page=historyPage(),e=page.entries[0];page.entries=[{...e,session_id:11},{...e,session_id:12}];p.state.sessions.value=page;
 const ids:number[]=[];p.onEntry=e=>ids.push(e.session_id);await act(async()=>root.render(React.createElement(TrainingHistoryScreen,p)));
 expect(node('progress-session-11').accessibilityLabel).not.toBe(node('progress-session-12').accessibilityLabel);
 await press('progress-session-11');await press('progress-session-12');expect(ids).toEqual([11,12]);
});


test('C-final: current-week axis stops at the received reading boundary, never at a local clock or future week end', async () => {
  const p = props(), page = historyPage();
  page.window = { ...page.window, time_zone: 'Europe/Paris', until: '2026-11-19T12:00:00Z' };
  page.weekly_counts = [{ week_from: '2026-11-15T23:00:00Z', week_until: '2026-11-22T23:00:00Z', completed_with_work: 2, partial_current_week: true }];
  p.state.sessions.value = page;
  await act(async () => root.render(React.createElement(TrainingHistoryScreen, p)));
  const week = node('progress-week-2026-11-15T23:00:00Z');
  expect(week.accessibilityLabel).toContain('16 nov. 2026');
  expect(week.accessibilityLabel).toContain('19 nov. 2026');
  expect(week.accessibilityLabel).toContain('13:00:00');
  expect(week.accessibilityLabel).not.toContain('23 nov. 2026');
  expect(week.accessibilityLabel).toContain('semaine partielle en cours');
  expect(['→ 19/11', '→ 19 nov. 2026']).toContain(node('progress-boundary-until-2026-11-15T23:00:00Z').children);
  expect(root.container.queryAll(n => String(n.props.testID ?? '').startsWith('frequency-mark-'))).toHaveLength(2);
});

test('C-final: unknown history without a prior page cannot manufacture zero weeks', async () => {
  const p = props(); p.state.sessions = { status: 'unknown', previous: false };
  await act(async () => root.render(React.createElement(TrainingHistoryScreen, p)));
  expect(node('progress-frequency')).toBeUndefined();
  expect(root.container.queryAll(n => String(n.props.testID ?? '').startsWith('progress-week-'))).toHaveLength(0);
  expect(screenText()).toContain('La lecture n’a pas pu être confirmée');
});


test('C-review I2: exclusive weekly bounds and the partial reading time are visible as well as spoken', async () => {
  const p = props(), page = historyPage();
  page.window = { ...page.window, time_zone: 'Europe/Paris', until: '2026-11-19T12:00:00Z' };
  page.weekly_counts = [{ week_from: '2026-11-15T23:00:00Z', week_until: '2026-11-22T23:00:00Z', completed_with_work: 2, partial_current_week: true }];
  p.state.sessions.value = page;
  await act(async () => root.render(React.createElement(TrainingHistoryScreen, p)));
  expect(screenText()).toContain('Fin exclue');
  expect(node('progress-cutoff-time-2026-11-15T23:00:00Z').children).toBe('13:00:00');
});
