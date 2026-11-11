import {accountHarness,deferred,reply} from '../../test/accountDataHarness';
import {exercisePage,historyPage,legacyFacts,occurrencesPage,ref,scienceHistory} from '../../test/trainingHistoryHarness';
import {TrainingHistoryClient,comparisonKey} from './trainingHistory';
import {RuntimeV3Client,V3_VERSIONS} from './firstPlanV3';
import {FirstSessionV3Client} from './firstSessionV3';
async function setup(){const s=await accountHarness();let execution:unknown=null;const calls:string[]=[];
 const v3=new FirstSessionV3Client(new RuntimeV3Client(s.auth,s.call,async(path)=>{calls.push(path);return{owner_id:7,contract_version:V3_VERSIONS.runtime,versions:V3_VERSIONS,execution};}));
 return{...s,client:new TrainingHistoryClient(s.auth,s.call,v3),v3Calls:calls,execution:(value:unknown)=>{execution=value;}};
}
test('actual auth reads the requested explicit period and preserves facts instead of planned sessions',async()=>{
 const s=await setup();s.handle(async()=>reply(historyPage()));
 expect(await s.client.sessions({period:'4w',timeZone:'UTC'})).toEqual({state:'confirmed',value:historyPage()});
 expect(s.calls.at(-1)?.path).toBe('/me/training-history?period=4w&time_zone=UTC&limit=50');
 expect(s.calls.at(-1)?.body).toBeNull();
});
test.each(['owner','version','window','date','count','planned','profile','mapping','empty','cursor','links_missing','links_duplicate','links_foreign'])('invalid history %s cannot become confirmed progress',async(kind)=>{
 const s=await setup(),raw:any=historyPage();
 if(kind==='owner')raw.owner_id=8;if(kind==='version')raw.contract_version='unknown';if(kind==='window')raw.window={...raw.window,time_zone:'Europe/Paris'};
 if(kind==='date')raw.entries[0].started_at='2026-02-30T12:00:00Z';if(kind==='count')raw.counts.recorded=true;if(kind==='planned')raw.planned_calendar.count=8;
 if(kind==='profile')raw.entries[0].execution_profile='SCI_V3';if(kind==='mapping')raw.entries[0].descriptor.mapping[0].se_id=false;
 if(kind==='empty')raw.state='EMPTY';if(kind==='cursor'){raw.completeness='MORE_AVAILABLE';raw.next_cursor=null;}
 if(kind==='links_missing')delete raw.entries[0].exercise_links;
 if(kind==='links_duplicate')raw.entries[0].exercise_links.push(raw.entries[0].exercise_links[0]);
 if(kind==='links_foreign')raw.entries[0].exercise_links[0].se_id=999;
 s.handle(async()=>reply(raw));expect(await s.client.sessions({period:'4w',timeZone:'UTC'})).toEqual({state:'unknown'});
});
test('raw legacy detail keeps captured facts and unknown context, with no current catalogue dose',async()=>{
 const s=await setup(),page=historyPage();s.handle(async()=>reply(legacyFacts()));
 const result=await s.client.detail(page,page.entries[0]);expect(result).toMatchObject({state:'confirmed',value:{kind:'LEGACY',facts:legacyFacts()}});
 expect(s.v3Calls).toEqual([]);expect(comparisonKey({profile:'LEGACY_V1'})).toBeNull();
});
test.each(['session','read_id','reps','unit','prescription','context'])('invalid legacy detail %s does not produce an inferred fact',async(kind)=>{
 const s=await setup(),page=historyPage(),facts:any=legacyFacts();
 if(kind==='session')facts.session.session_id=99;if(kind==='read_id')facts.read_id='d'.repeat(32);
 if(kind==='reps')facts.exercises[0].sets[0].reps=true;if(kind==='unit')facts.exercises[0].load_semantics='TOTAL_EXTERNAL';
 if(kind==='prescription')facts.prescription='RECONSTRUCTED';if(kind==='context')facts.exercises[0].equipment_context='CURRENT_CATALOGUE';
 s.handle(async()=>reply(facts));expect(await s.client.detail(page,page.entries[0])).toEqual({state:'unknown'});
});
test('SCI guard dispatches once to the real existing V3 client and exposes a read-only historical model',async()=>{
 const s=await setup(),page=historyPage(),sci=scienceHistory();s.execution(sci.execution);s.handle(async()=>reply({detail:{error:'execution_profile_required'}},409));
 const result=await s.client.detail(page,sci.entry);expect(result).toMatchObject({state:'confirmed',value:{kind:'SCI',execution:{session_id:11}}});
 expect(s.v3Calls).toEqual(['/sessions/11/execution']);
 if(result.state==='confirmed'&&result.value.kind==='SCI'){
  expect(result.value).not.toHaveProperty('allowed_actions');expect(result.value.execution).not.toHaveProperty('allowed_actions');
  const dumbbell=result.value.execution.exercises.find((e:any)=>e.prescription.context.load_semantics==='PER_IMPLEMENT')!;
  expect(dumbbell.sets[0].observation?.setting?.value).toBe(20);
  expect(comparisonKey({profile:'SCI_V3',exercise:dumbbell})).toEqual(expect.any(String));
 }
});
test.each(['binding','session','start','slot','intent','canonical','set','context','semantics','setting','reps','revision','date','extra_context','extra_setting','completion'])('additional historical V3 validation rejects incoherent %s',async(kind)=>{
 const s=await setup(),sci:any=scienceHistory(),e=sci.execution.exercises[0],set=e.sets[0];
 if(kind==='binding')sci.execution.binding_digest='c'.repeat(64);if(kind==='session')sci.execution.session_id=99;if(kind==='start')sci.execution.started_at='2026-11-08T10:00:00Z';
 if(kind==='slot')e.slot_id='different';if(kind==='intent')e.intent_id='different';if(kind==='canonical')e.canonical_exercise_id='different';
 if(kind==='set')set.set_id=999;if(kind==='context')set.observation.context={...set.observation.context,equipment_ref:'different'};
 if(kind==='semantics')set.observation.context={...set.observation.context,load_semantics:'PER_IMPLEMENT'};
 if(kind==='setting')set.observation.setting.value=NaN;if(kind==='reps')set.observation.reps=7;
 if(kind==='revision')set.revision=0;if(kind==='date')set.completed_at='no offset';
 if(kind==='extra_context')set.observation.context={...set.observation.context,location:'not-in-published-context'};
 if(kind==='extra_setting')set.observation.setting={...set.observation.setting,total_external_kg:35};
 if(kind==='completion'){set.reps=null;set.observation.reps=null;}
 s.execution(sci.execution);s.handle(async()=>reply({detail:{error:'execution_profile_required'}},409));
 expect(await s.client.detail(historyPage(),sci.entry)).toEqual({state:'unknown'});
});
test('a legacy guard error cannot switch a legacy selection into SCI, and unrelated409 requires refresh',async()=>{
 const s=await setup(),page=historyPage();s.handle(async()=>reply({detail:{error:'execution_profile_required'}},409));
 expect(await s.client.detail(page,page.entries[0])).toEqual({state:'unknown'});expect(s.v3Calls).toEqual([]);
 s.handle(async()=>reply({detail:{error:'READ_CHANGED'}},409));expect(await s.client.detail(page,page.entries[0])).toEqual({state:'changed'});
});
test('zero-match partial exercise scan stays scanning and occurrence selection is transmitted exactly',async()=>{
 const s=await setup(),page=historyPage(),partial={...exercisePage(),state:'SCANNING',entries:[],scan:'PARTIAL_SCAN',source_inspected:1000,coverage_complete:false,next_cursor:ref('next')};
 s.handle(async()=>reply(partial));expect(await s.client.exercises(page)).toEqual({state:'confirmed',value:partial});
 s.handle(async()=>reply(occurrencesPage()));const found=await s.client.occurrences(page,ref('exercise'));
 expect(found.state).toBe('confirmed');
 const occurrence=occurrencesPage().entries[0];s.handle(async()=>reply({...legacyFacts(),selected_se_id:21}));
 expect((await s.client.detail(page,occurrence)).state).toBe('confirmed');expect(s.calls.at(-1)?.path).toContain('occurrence_ref=');
});
test('late detail after A/B switch is cancelled rather than returning any owner facts',async()=>{
 const s=await setup(),late=deferred<Response>();s.handle(async()=>late.promise);const read=s.client.detail(historyPage(),historyPage().entries[0]);
 for(let i=0;i<25;i++)await Promise.resolve();await s.auth.logout();s.setOwner(8);await s.auth.login('b','test-only',null);late.resolve(reply(legacyFacts()));
 expect(await read).toEqual({state:'cancelled'});
});
