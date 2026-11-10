import {accountHarness,deferred,reply,weightPage} from '../../test/accountDataHarness';
import {historyPage,summary,exercisePage,occurrencesPage,legacyFacts,ref,window4} from '../../test/trainingHistoryHarness';
import {TrainingHistoryClient} from './trainingHistory';
import {TrainingHistoryResource,WeightWindowResource} from './trainingHistoryResource';
import {WeightHistoryClient} from './weightHistory';
import {WeightHistoryResource} from './weightHistoryResource';
async function setup(){const s=await accountHarness();return{...s,resource:new TrainingHistoryResource(s.auth,new TrainingHistoryClient(s.auth,s.call))};}
const flush=async()=>{for(let i=0;i<30;i++)await Promise.resolve();};
test('sessions retain full-period counts, not the sum of pages or a planned calendar',async()=>{
 const s=await setup();s.handle(async p=>reply(p.includes('cursor=')?{...historyPage(),entries:[summary(12)]}:{...historyPage(),completeness:'MORE_AVAILABLE',next_cursor:ref('next')}));
 await s.resource.refresh('4w','UTC');await s.resource.nextSessions();expect(s.resource.state.sessions.value?.entries.map(e=>e.session_id)).toEqual([11,12]);
 expect(s.resource.state.sessions.value?.counts.completed_with_work).toBe(1);expect(s.resource.state.sessions.value?.planned_calendar.count).toBeNull();
});
test.each(['unknown','read','counts','cycle'])('pagination %s keeps only previous facts and cannot claim complete',async kind=>{
 const s=await setup();let second=false;s.handle(async()=>{if(!second)return reply({...historyPage(),completeness:'MORE_AVAILABLE',next_cursor:ref('next')});if(kind==='unknown')throw Error('offline');
 const p=historyPage();if(kind==='read')p.read_id='d'.repeat(32);if(kind==='counts')p.counts.completed=99;if(kind==='cycle'){p.completeness='MORE_AVAILABLE';p.next_cursor=ref('next');}return reply(p);});
 await s.resource.refresh('4w','UTC');second=true;await s.resource.nextSessions();expect(s.resource.state.sessions).toMatchObject({status:'unknown',previous:true,value:{entries:[{session_id:11}],completeness:'MORE_AVAILABLE'}});
});
test('selection must belong to current read and a late detail cannot replace a new period',async()=>{
 const s=await setup(),late=deferred<Response>();s.handle(async()=>reply(historyPage()));await s.resource.refresh('4w','UTC');
 const count=s.calls.length;await s.resource.selectEntry({...summary(),entry_ref:ref('foreign')});expect(s.calls).toHaveLength(count);
 s.handle(async()=>late.promise);const old=s.resource.selectEntry(summary());await flush();
 s.handle(async()=>reply({...historyPage(),read_id:'d'.repeat(32),window:{...window4,period:'all',from:null},weekly_counts:[]}));await s.resource.refresh('all','UTC');
 late.resolve(reply(legacyFacts()));await old;expect(s.resource.state.detail.status).toBe('idle');expect(s.resource.state.sessions.value?.window.period).toBe('all');
});
test('zero-match partial index stays scanning, occurrences select exact fact and back preserves parent',async()=>{
 const s=await setup();s.handle(async p=>reply(p.includes('exercises')?{...exercisePage(),state:'SCANNING',entries:[],scan:'PARTIAL_SCAN',coverage_complete:false,source_inspected:1000,next_cursor:ref('scan')}:historyPage()));
 await s.resource.refresh('4w','UTC');await s.resource.loadExercises();expect(s.resource.state.exercises.value?.state).toBe('SCANNING');
 s.handle(async()=>reply(exercisePage()));await s.resource.nextExercises();s.handle(async()=>reply(occurrencesPage()));await s.resource.selectExercise(ref('exercise'));
 s.handle(async()=>reply({...legacyFacts(),selected_se_id:21}));await s.resource.selectOccurrence(occurrencesPage().entries[0]);expect(s.resource.state.detail.value?.kind).toBe('LEGACY');
 s.resource.back();expect(s.resource.state.detail.status).toBe('idle');expect(s.resource.state.selectedExercise).toBe(ref('exercise'));s.resource.back();expect(s.resource.state.selectedExercise).toBeNull();
});
test('changed owner entry requires refresh; account switch clears all pages and stale detail',async()=>{
 const s=await setup(),late=deferred<Response>();s.handle(async()=>reply(historyPage()));await s.resource.refresh('4w','UTC');
 s.handle(async()=>reply({detail:{error:'READ_CHANGED'}},409));await s.resource.selectEntry(summary());expect(s.resource.state.detail.status).toBe('changed');
 s.handle(async()=>late.promise);const old=s.resource.selectEntry(summary());await flush();await s.auth.logout();s.setOwner(8);await s.auth.login('b','test-only',null);
 expect(s.resource.state.sessions.value).toBeUndefined();late.resolve(reply(legacyFacts()));await old;expect(s.resource.state.detail.status).toBe('idle');
});
function weight(id:number,date:string,cursor:string|null=null){const p=weightPage(id,7,cursor);p.entries[0].measured_at=date;return p;}
async function weights(){const s=await accountHarness();return{...s,r:new WeightWindowResource(s.auth,new WeightHistoryResource(s.auth,new WeightHistoryClient(s.auth,s.call)))};}
test('existing weight consumers scan to measured lower bound, preserving same-date IDs and quality gaps',async()=>{
 const s=await weights();let n=0;s.handle(async()=>{n++;if(n===1)return reply(weight(15,'2026-11-11T00:00:00Z','new'));if(n===2)return reply(weight(14,'2026-11-09T00:00:00Z','same'));if(n===3){const p:any=weight(13,'2026-11-09T00:00:00Z','old');p.entries[0]={...p.entries[0],quality:'INVALID_NONFINITE',value:null,raw_value_repr:'inf'};return reply(p);}return reply(weight(12,'2026-10-18T00:00:00Z','unneeded'));});
 await s.r.refresh(window4);expect(n).toBe(4);expect(s.r.state).toMatchObject({status:'confirmed',coverage:'COMPLETE',entries:[{measurement_id:14},{measurement_id:13,value:null}]});
});
test('weight consent clears facts; offline retains only previous facts with incomplete coverage',async()=>{
 const s=await weights();s.handle(async()=>reply(weight(14,'2026-11-09T00:00:00Z')));await s.r.refresh(window4);s.handle(async()=>{throw Error('offline');});await s.r.refresh(window4);
 expect(s.r.state).toMatchObject({status:'unknown',previous:true,coverage:'PARTIAL',entries:[{measurement_id:14}]});s.handle(async()=>reply({detail:{error:'body_consent_required'}},403));await s.r.refresh(window4);expect(s.r.state).toMatchObject({status:'consent_required',entries:[]});
});
test('weight budget1000 per explicit interaction stays partial, never an invented empty period',async()=>{
 const s=await weights();let page=0;s.handle(async()=>{const p:any=weight(2000-page*50,'2026-11-09T00:00:00Z',`c${page}`);p.entries=Array.from({length:50},(_,i)=>({...p.entries[0],measurement_id:2000-page*50-i,provenance:{origin:'UNKNOWN',acquisition:'UNKNOWN',source_ref:`body_measurements/${2000-page*50-i}/weight_kg`}}));page++;return reply(p);});
 await s.r.refresh(window4);expect(page).toBe(20);expect(s.r.state).toMatchObject({status:'confirmed',coverage:'PARTIAL',canContinue:true});expect(s.r.state.entries).toHaveLength(1000);
});
test('old weight response cannot survive an account switch',async()=>{
 const s=await weights(),late=deferred<Response>();s.handle(async()=>late.promise);const old=s.r.refresh(window4);await flush();await s.auth.logout();s.setOwner(8);await s.auth.login('b','test-only',null);
 expect(s.r.state.entries).toEqual([]);late.resolve(reply(weight(14,'2026-11-09T00:00:00Z')));await old;expect(s.r.state.entries).toEqual([]);
});
test('confirmed session links open the exact owned exercise, preserve back navigation and reject invented links',async()=>{
 const s=await setup();s.handle(async()=>reply(historyPage()));await s.resource.refresh('4w','UTC');
 s.handle(async()=>reply(legacyFacts()));await s.resource.selectEntry(summary());
 const count=s.calls.length;await s.resource.openExerciseFromDetail(22,ref('exercise'));await s.resource.openExerciseFromDetail(21,ref('foreign'));
 expect(s.calls).toHaveLength(count);expect(s.resource.state.selectedEntry).toBe(11);
 s.handle(async()=>reply(occurrencesPage()));await s.resource.openExerciseFromDetail(21,ref('exercise'));
 expect(s.calls.at(-1)?.path).toContain(`/exercises/${encodeURIComponent(ref('exercise'))}`);
 expect(s.resource.state).toMatchObject({selectedEntry:null,selectedExercise:ref('exercise'),selectedExerciseLabel:'Captured exercise',occurrences:{status:'confirmed'}});
 s.handle(async()=>reply({...legacyFacts(),selected_se_id:21}));await s.resource.selectOccurrence(occurrencesPage().entries[0]);
 expect(s.resource.state.detail.value?.selected_se_id).toBe(21);s.resource.back();expect(s.resource.state.selectedExercise).toBe(ref('exercise'));
 s.resource.back();expect(s.resource.state.selectedExercise).toBeNull();
});
test('late exercise navigation response after account change cannot restore previous owner history',async()=>{
 const s=await setup();s.handle(async()=>reply(historyPage()));await s.resource.refresh('4w','UTC');
 s.handle(async()=>reply(legacyFacts()));await s.resource.selectEntry(summary());
 const late=deferred<Response>();s.handle(async()=>late.promise);const task=s.resource.openExerciseFromDetail(21,ref('exercise'));await flush();
 await s.auth.logout();s.setOwner(8);await s.auth.login('b','test-only',null);
 late.resolve(reply(occurrencesPage()));await task;
 expect(s.resource.state).toMatchObject({selectedExercise:null,occurrences:{status:'idle'}});
});
test('duplicate exercise pages merge identities rather than duplicating historical points',async()=>{
 const s=await setup();s.handle(async()=>reply(historyPage()));await s.resource.refresh('4w','UTC');s.handle(async()=>reply({...exercisePage(),scan:'PARTIAL_SCAN',coverage_complete:false,next_cursor:ref('next')}));await s.resource.loadExercises();
 s.handle(async()=>reply(exercisePage()));await s.resource.nextExercises();expect(s.resource.state.exercises.value?.entries).toHaveLength(1);expect(s.resource.state.exercises.value?.coverage_complete).toBe(true);
});
test('concurrent next calls share no extra read and failing detail does not turn empty into success',async()=>{
 const s=await setup(),late=deferred<Response>();s.handle(async()=>reply({...historyPage(),completeness:'MORE_AVAILABLE',next_cursor:ref('next')}));await s.resource.refresh('4w','UTC');
 s.handle(async()=>late.promise);const first=s.resource.nextSessions(),second=s.resource.nextSessions();await flush();expect(s.calls.filter(c=>c.path.includes('cursor=')).length).toBe(1);
 late.resolve(reply({...historyPage(),entries:[summary(12)]}));await Promise.all([first,second]);expect(s.resource.state.sessions.value?.entries).toHaveLength(2);
 s.handle(async()=>{throw Error('offline');});await s.resource.selectEntry(summary());expect(s.resource.state.detail).toMatchObject({status:'unknown',previous:false});
});
test('weight page error keeps scanned facts as previous; a period change never reuses them',async()=>{
 const s=await weights();let n=0;s.handle(async()=>{if(++n===1)return reply(weight(14,'2026-11-09T00:00:00Z','next'));throw Error('offline');});
 await s.r.refresh(window4);expect(s.r.state).toMatchObject({status:'unknown',coverage:'PARTIAL'});
 // A failed ongoing scan may retain only points the adapter really received.
 expect(s.r.state.entries.map(e=>e.measurement_id)).toEqual([14]);
 s.handle(async()=>{throw Error('offline');});await s.r.refresh({...window4,period:'all',from:null});expect(s.r.state.entries).toEqual([]);
});
