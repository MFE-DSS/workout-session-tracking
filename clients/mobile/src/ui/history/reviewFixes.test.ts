
import React,{act} from 'react';
import {createRoot} from 'test-renderer';
import {accountHarness,reply,weightPage,deferred} from '../../../test/accountDataHarness';
import {historyPage,legacyFacts,scienceHistory} from '../../../test/trainingHistoryHarness';
import {TrainingHistoryHost} from './TrainingHistoryHost';
import {TrainingHistoryClient} from '../../api/trainingHistory';
import {RuntimeV3Client,V3_VERSIONS} from '../../api/firstPlanV3';
import {FirstSessionV3Client} from '../../api/firstSessionV3';
import {setFact} from './historyView';
jest.mock('react-native-safe-area-context',()=>({useSafeAreaInsets:()=>({top:47,bottom:34,left:0,right:0})}));
const flush=async()=>{for(let i=0;i<80;i++)await Promise.resolve();};
test('review fix I2: leaving the host stops weight continuations',async()=>{
 const s=await accountHarness(),late=deferred<Response>(),root=createRoot();let weightReads=0;
 s.handle(async p=>{
  if(p.startsWith('/me/training-history?'))return reply(historyPage());
  if(p.startsWith('/me/body/weight-history')){weightReads++;if(weightReads===1)return late.promise;return reply({...weightPage(),state:'EMPTY',entries:[]});}
  return reply(null,404);
 });
 await act(async()=>{root.render(React.createElement(TrainingHistoryHost,{auth:s.auth,call:s.call,timeZone:'UTC'}));await flush();});
 expect(weightReads).toBe(1);await act(async()=>root.unmount());
 const page=weightPage(10,7,'next');page.entries[0].measured_at='2026-11-05T00:00:00Z';
 await act(async()=>{late.resolve(reply(page));await flush();});
 expect(weightReads).toBe(1);
});
test('review fix I3: invalid source values stay distinct from missing facts',()=>{
 const invalid:any={completed:true,reps:null,weight_kg:null,raw_weight_repr:'inf',raw_reps_repr:'9007199254740993'};
 const missing={completed:true,reps:null,weight_kg:null,raw_weight_repr:null};
 expect(setFact(invalid)).not.toBe(setFact(missing));
 expect(setFact(invalid)).toContain('inf');expect(setFact(invalid)).toContain('9007199254740993');expect(setFact(invalid)).toContain('invalide');
});
test('review fix I4: completed SCI facts require their typed observation',async()=>{
 const s=await accountHarness(),sci:any=scienceHistory();
 const logged=sci.execution.exercises[0].sets[0];
 const v3=new FirstSessionV3Client(new RuntimeV3Client(s.auth,s.call,async()=>({owner_id:7,contract_version:V3_VERSIONS.runtime,versions:V3_VERSIONS,execution:sci.execution})));
 const client=new TrainingHistoryClient(s.auth,s.call,v3);
 s.handle(async()=>reply({detail:{error:'execution_profile_required'}},409));
 expect((await client.detail(historyPage(),sci.entry)).state).toBe('confirmed');
 logged.observation=null;logged.revision=0;
 const outcome=await client.detail(historyPage(),sci.entry);
 expect(outcome.state).toBe('unknown');
 expect(logged.completed).toBe(true);expect(logged.reps).not.toBeNull();
});

test('review fix I1: a503 preserves previous same-owner page facts',async()=>{
 const {TrainingHistoryResource}=require('../../api/trainingHistoryResource');
 const {ref}=require('../../../test/trainingHistoryHarness');
 const s=await accountHarness(),r=new TrainingHistoryResource(s.auth,new TrainingHistoryClient(s.auth,s.call));
 s.handle(async()=>reply({...historyPage(),completeness:'MORE_AVAILABLE',next_cursor:ref('next')}));
 await r.refresh('4w','UTC');expect(r.state.sessions.value.entries).toHaveLength(1);
 s.handle(async()=>reply({detail:{error:'training_history_unavailable'}},503));
 await r.nextSessions();expect(r.state.sessions).toMatchObject({status:'unknown',previous:true,value:{entries:[{session_id:11}]}});
});
