import React,{act} from 'react';
import {createRoot} from 'test-renderer';
import {FirstUseV3Controller} from '../../api/firstUseV3';
import {PlanV3Host} from './PlanV3Host';
import {AppState} from 'react-native';

let mockExecutionProps:any;
const appStateDescriptor=Object.getOwnPropertyDescriptor(AppState,'currentState')!;
function currentState(state:'active'|'background'){Object.defineProperty(AppState,'currentState',{value:state,writable:true,configurable:true});}
jest.mock('./PlanV3ExecutionScreen',()=>({PlanV3ExecutionScreen:(props:any)=>{mockExecutionProps=props;return null;}}));
jest.mock('./PlanV3FirstUseScreen',()=>({PlanV3FirstUseScreen:()=>null}));

function fixture(){
 let stored:any={profile:'PLAN_V3',local_version:'first-session-local/3.0.0',owner_id:7,phase:'ACTIVE',intent:null,source:{},local_facts:{},drafts:{},
  execution:{session_id:5,server_now:'2026-11-21T19:10:01.538Z',status:'in_progress',applicability:{state:'CURRENT'},observation_only:false,allowed_actions:['RECORD_FACT','NEXT_WORK_SET'],exercises:[]}};
 const journal:any={read:async()=>structuredClone(stored),save:async(s:any)=>{stored=structuredClone(s);},history:async()=>[]};
 const sessions:any={execution:async()=>({state:'confirmed',value:structuredClone(stored.execution)})};
 const c=new FirstUseV3Controller({ownerId:7,journal,sessions,plan:{} as any,blueprint:{} as any,calibration:{} as any,newId:()=> 'new-op',current:()=>true});
 return {c,journal,sessions,stored:()=>stored};
}
afterEach(()=>{Object.defineProperty(AppState,'currentState',appStateDescriptor);jest.useRealTimers();jest.restoreAllMocks();});

test('TIME01 restored server_now cannot become a current clock in the actual Host',async()=>{
 jest.useFakeTimers();jest.setSystemTime(new Date('2026-11-22T11:35:36Z'));
 const f=fixture();await f.c.restore();const root=createRoot();
 await act(async()=>root.render(React.createElement(PlanV3Host,{controller:f.c,onExit(){},onPreferences(){},onSync:async()=>{}})));
 expect(Number.isNaN(mockExecutionProps.serverNowMs)).toBe(true);
 expect(f.stored().execution.server_now).toBe('2026-11-21T19:10:01.538Z');
 await act(async()=>root.unmount());
});

test('TIME01 a fresh read owns its monotonic anchor, independent of wall clock and render cadence',async()=>{
 jest.useFakeTimers();jest.setSystemTime(new Date('2026-11-22T12:00:00Z'));
 const f=fixture();await f.c.restore();await f.c.refreshExecution();
 const start=Date.parse(f.stored().execution.server_now);
 jest.advanceTimersByTime(2500);jest.setSystemTime(new Date('2026-11-23T12:00:00Z'));
 expect(f.c.executionNowMs()).toBe(start+2500);
 expect(f.c.eventTime()).toEqual({epochMs:start+2500,estimated:false});
});

test('TIME01 pause and restore destroy the in-memory link but preserve the persisted DTO',async()=>{
 jest.useFakeTimers();jest.setSystemTime(new Date('2026-11-22T12:00:00Z'));
 const f=fixture();await f.c.restore();await f.c.refreshExecution();await f.c.pause();
 expect(Number.isNaN(f.c.executionNowMs())).toBe(true);
 expect(f.c.eventTime()).toEqual({epochMs:Date.now(),estimated:true});
 await f.c.refreshExecution();await f.c.restore();
 expect(Number.isNaN(f.c.executionNowMs())).toBe(true);
 expect(f.stored().execution.server_now).toBe('2026-11-21T19:10:01.538Z');
});

test('TIME01 failed refresh cannot retain an earlier clock link',async()=>{
 jest.useFakeTimers();const f=fixture();await f.c.restore();await f.c.refreshExecution();
 f.sessions.execution=async()=>({state:'unknown'});await f.c.refreshExecution();
 expect(f.c.eventTime().estimated).toBe(true);
});

test('TIME01 a read completed after pause cannot create a fresh clock link',async()=>{
 jest.useFakeTimers();const f=fixture();await f.c.restore();
 let finish!:(r:any)=>void;f.sessions.execution=()=>new Promise(resolve=>{finish=resolve;});
 const pending=f.c.refreshExecution();await Promise.resolve();await f.c.pause();
 finish({state:'confirmed',value:f.stored().execution});await pending;
 expect(f.c.eventTime().estimated).toBe(true);
});

test('TIME01 restore during an earlier request cannot lend that response a new clock identity',async()=>{
 jest.useFakeTimers();const f=fixture();await f.c.restore();
 let finish!:(r:any)=>void;f.sessions.execution=()=>new Promise(resolve=>{finish=resolve;});
 const pending=f.c.refreshExecution();await Promise.resolve();await f.c.restore();
 finish({state:'confirmed',value:f.stored().execution});await pending;
 expect(f.c.eventTime().estimated).toBe(true);
});

test('TIME01 opt-in QA trace exposes bounded clock provenance without measurements or credentials',async()=>{
 const old=process.env.EXPO_PUBLIC_QA_DELIVERY;process.env.EXPO_PUBLIC_QA_DELIVERY='1';
 const output=jest.spyOn(console,'info').mockImplementation(()=>{});
 try{
  const f=fixture();await f.c.restore();await f.c.refreshExecution();f.c.eventTime();await f.c.pause();
  const rows=output.mock.calls.filter(v=>v[0]==='AUREN_QA_TIME').map(v=>JSON.parse(String(v[1])));
  expect(rows.map(v=>v.event)).toEqual(['RESTORE','EXECUTION_READ_START','EXECUTION_READ_CONFIRMED','SET_ACTION_TIME','PAUSE']);
  for(const row of rows){
   expect(row.schemaVersion).toBe('qa-temporal-observation/1.0.0');
   expect(Number.isFinite(row.wall_ms)&&Number.isFinite(row.mono_ms)).toBe(true);
   expect(Object.keys(row).sort()).toEqual(['anchor','detail','event','generation','mono_ms','schemaVersion','wall_ms']);
   expect(JSON.stringify(row)).not.toMatch(/password|Bearer|token|local_facts|prescription|reps|setting/);
  }
 }finally{if(old===undefined)delete process.env.EXPO_PUBLIC_QA_DELIVERY;else process.env.EXPO_PUBLIC_QA_DELIVERY=old;}
});

test('review lifecycle: a post-pause background read cannot lend its anchor to the foreground',async()=>{
 jest.useFakeTimers();currentState('active');
 let lifecycle!:(state:any)=>void;
 jest.spyOn(AppState,'addEventListener').mockImplementation((_event:any,listener:any)=>{lifecycle=listener;return{remove(){}};});
 const f=fixture();await f.c.restore();const root=createRoot();
 await act(async()=>root.render(React.createElement(PlanV3Host,{controller:f.c,onExit(){},onPreferences(){},onSync:async()=>{}})));
 await act(async()=>{lifecycle('background');});
 await f.c.refreshExecution(); // An earlier SET's onSync continuation can do this.
 await act(async()=>{lifecycle('active');});
 expect(f.c.eventTime().estimated).toBe(true);
 await act(async()=>root.unmount());
});

test('review lifecycle: mounting an already backgrounded Host does not trust a pre-mount read',async()=>{
 jest.useFakeTimers();currentState('background');
 const f=fixture();await f.c.restore();await f.c.refreshExecution();const root=createRoot();
 await act(async()=>root.render(React.createElement(PlanV3Host,{controller:f.c,onExit(){},onPreferences(){},onSync:async()=>{}})));
 expect(f.c.eventTime().estimated).toBe(true);
 await act(async()=>root.unmount());
});

test('review QA trace: malformed server_now cannot inject arbitrary response text into logs',async()=>{
 const old=process.env.EXPO_PUBLIC_QA_DELIVERY;process.env.EXPO_PUBLIC_QA_DELIVERY='1';
 const output=jest.spyOn(console,'info').mockImplementation(()=>{});
 try{
  const f=fixture();await f.c.restore();
  f.sessions.execution=async()=>({state:'confirmed',value:{...f.stored().execution,server_now:'invalid-sensitive-text-'+ 'x'.repeat(10000)}});
  await f.c.refreshExecution();
  const rows=output.mock.calls.filter(v=>v[0]==='AUREN_QA_TIME').map(v=>JSON.parse(String(v[1])));
  expect(JSON.stringify(rows)).not.toContain('invalid-sensitive-text');
  expect(rows.find(v=>v.event==='EXECUTION_READ_CONFIRMED').detail.server_epoch_ms).toBeNull();
 }finally{if(old===undefined)delete process.env.EXPO_PUBLIC_QA_DELIVERY;else process.env.EXPO_PUBLIC_QA_DELIVERY=old;}
});

test('review first-use: onboarding without execution does not acquire a ticking render loop',async()=>{
 jest.useFakeTimers();currentState('active');
 const timer=jest.spyOn(global,'setInterval'),f=fixture();await f.c.restore();f.c.state!.execution=null;const root=createRoot();
 await act(async()=>root.render(React.createElement(PlanV3Host,{controller:f.c,onExit(){},onPreferences(){},onSync:async()=>{}})));
 expect(timer).not.toHaveBeenCalled();
 await act(async()=>root.unmount());
});

test('native recovery witness: failed execution read preserves the locally queued finish lifecycle',async()=>{
 const f=fixture();await f.c.restore();const commands:string[]=[];
 f.journal.enqueueClose=async(op:string,_kind:string,_session:number,state:any)=>{commands.push(op);await f.journal.save(state);};
 await f.c.close('SESSION_FINISH');expect(f.c.state?.phase).toBe('COMPLETE');
 f.sessions.execution=async()=>({state:'unknown'});await f.c.refreshExecution();
 expect(f.c.state?.phase).toBe('COMPLETE');expect(commands).toEqual(['new-op']);
 await f.c.restore();expect(f.c.state?.phase).toBe('COMPLETE');
});

test('failed execution read preserves a server-completed occurrence despite an older local phase',async()=>{
 const f=fixture();await f.c.restore();
 f.c.state!.execution!.status='completed';f.c.state!.phase='PAUSED';
 f.sessions.execution=async()=>({state:'unknown'});await f.c.refreshExecution();
 expect(f.c.state?.phase).toBe('COMPLETE');
 expect(f.c.state?.execution?.allowed_actions).not.toContain('NEXT_WORK_SET');
});
