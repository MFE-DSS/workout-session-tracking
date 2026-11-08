import {FirstUseV3Controller} from './firstUseV3';
import type {PlanV3Stored,FirstSessionCommandV3} from '../domain/planV3Types';
const command={evaluation_ref:'e',snapshot_ref:'s'} as FirstSessionCommandV3;
function fixture(){let stored:PlanV3Stored|null=null;const calls:string[]=[];
 const journal:any={history:async()=>[],read:async()=>stored,claim:async(s:PlanV3Stored)=>{stored=structuredClone(s);return true;},save:async(s:PlanV3Stored)=>{stored=structuredClone(s);calls.push('saved:'+s.intent?.state);}};
 const sessions:any={submit:async()=>{calls.push('POST');return{state:'unknown'};},readRequest:async()=>{calls.push('GET');return{state:'rejected',status:404};},handoff:async()=>({state:'confirmed',value:{handoff:null}})};
 const ports:any={ownerId:7,journal,sessions,plan:{capabilities:async()=>({state:'unavailable',reason:'NOT_SERVED'})},blueprint:{},calibration:{},newId:()=> 'stable',current:()=>true};
 return {ports,calls,journal,sessions,stored:()=>stored};}
test('stable start intent is durable BEFORE transmission; restart only reads and never replaces missing receipt with success',async()=>{
 const f=fixture();const c=new FirstUseV3Controller(f.ports);await c.restore();await c.startCommand(command);
 expect(f.calls).toEqual(['saved:submitted','POST','saved:unknown']);expect(f.stored()?.intent?.request_id).toBe('stable');
 const restored=new FirstUseV3Controller(f.ports);await restored.restore();await restored.reconcileStart();
 expect(f.calls.filter(x=>x==='POST')).toHaveLength(1);expect(restored.state?.intent?.state).toBe('unknown');
 await restored.retryStartExplicitly();expect(f.calls.filter(x=>x==='POST')).toHaveLength(2);expect(restored.state?.intent?.request_id).toBe('stable');
});
test('stale response after identity switch never writes a session or changes another owner',async()=>{
 const f=fixture();let live=true;f.ports.current=()=>live;
 f.sessions.submit=async()=>{live=false;return{state:'confirmed',value:{state:'CREATED',session_id:20}};};
 const c=new FirstUseV3Controller(f.ports);await c.restore();await c.startCommand(command);
 expect(f.stored()?.intent?.state).toBe('submitted');expect(f.stored()?.execution).toBeNull();
});
test('restored execution cannot carry cached CURRENT permission into new work',async()=>{
 const f=fixture(),c=new FirstUseV3Controller(f.ports);await c.restore();
 await f.journal.save({...c.state,phase:'ACTIVE',execution:{session_id:2,applicability:{state:'CURRENT'},observation_only:false,allowed_actions:['NEXT_WORK_SET']}});
 await c.restore();expect(c.state?.execution?.applicability.state).toBe('UNKNOWN');expect(c.state?.execution?.allowed_actions).not.toContain('NEXT_WORK_SET');
});
test('lost source response is reconciled from owned receipt metadata without mutation replay',async()=>{
 const f=fixture(),c=new FirstUseV3Controller(f.ports);await c.restore();
 await f.journal.save({...c.state,source:{declarations:{source_revision:0}}});await c.restore();
 f.ports.blueprint.saveDeclarations=async()=>({state:'unknown'});
 await c.saveDeclarations({limitations:{state:'KNOWN',value:[]}});expect(c.state?.source.pending).toBeDefined();
 f.ports.plan.capabilities=async()=>({state:'confirmed',value:{owner_id:7,controlled_test_available:true}});
 f.ports.blueprint.read=async()=>({state:'confirmed',value:{owner_id:7,source_revision:1,receipts:{sources:[{request_id:'stable',event_ref:'source1',source_revision:1,kind:'DECLARATIONS'}],snapshots:[],evaluations:[]}}});
 await c.load();expect(c.state?.source.pending).toBeUndefined();expect(c.state?.source.declarations).toMatchObject({source_revision:1});
 expect(f.calls.filter(x=>x==='POST')).toHaveLength(0);
});
test('backgrounding while applicability is in flight cannot restore a current work permission',async()=>{
 const f=fixture(),c=new FirstUseV3Controller(f.ports);await c.restore();
 const execution:any={session_id:2,server_now:'2026-11-08T12:00:00Z',status:'in_progress',applicability:{state:'UNKNOWN'},allowed_actions:['RECORD_FACT'],observation_only:true,exercises:[{se_id:3,sets:[{set_id:4,completed:false}]}]};
 await f.journal.save({...c.state,execution,phase:'PAUSED'});await c.restore();
 let resolve!:(value:unknown)=>void;f.sessions.execution=()=>new Promise(done=>{resolve=done;});
 const pending=c.beginNext();await Promise.resolve();await c.pause();
 resolve({state:'confirmed',value:{...execution,applicability:{state:'CURRENT'},allowed_actions:['NEXT_WORK_SET'],observation_only:false}});await pending;
 expect(c.state?.phase).toBe('PAUSED');expect(c.state?.execution?.applicability.state).toBe('UNKNOWN');
});
test('observed-context entry records actual source events without invoking the pilot or inventing an attempt',async()=>{
 const f=fixture(),c=new FirstUseV3Controller(f.ports);await c.restore();await f.journal.save({...c.state,source:{declarations:{source_revision:0}}});await c.restore();
 const events:unknown[]=[];f.ports.blueprint.observe=async(_key:string,revision:number,event:unknown)=>{events.push(event);return{state:'confirmed',value:{event_ref:'event-real',episode_ref:'episode-real',source_revision:revision+1}};};
 f.ports.blueprint.read=async()=>({state:'confirmed',value:{source_revision:1}});
 const context:any={canonical_exercise_id:'rdl',context_ref:'room',equipment_ref:'db',realization_ref:'bilateral',side:'BILATERAL',load_semantics:'PER_IMPLEMENT'};
 await c.openObservedContext(context);expect(events).toEqual([{kind:'CONTEXT_OPENED',context,availability:'AVAILABLE'}]);
 expect(c.state?.source.observed_episode_ref).toBe('episode-real');
 await c.recordObservedEvent({kind:'FAMILIARIZATION_CONFIRMED'});
 expect(events[1]).toEqual({kind:'CALIBRATION_EVENT',episode_ref:'episode-real',event:{kind:'FAMILIARIZATION_CONFIRMED'}});
 expect(events).toHaveLength(2);
});
test('explicit evaluation reads the latest owned revision before capture',async()=>{
 const f=fixture(),c=new FirstUseV3Controller(f.ports);await c.restore();await f.journal.save({...c.state,source:{declarations:{source_revision:0}}});await c.restore();
 f.ports.blueprint.read=async()=>({state:'confirmed',value:{source_revision:3}});
 let captured=-1;f.ports.blueprint.capture=async(_key:string,revision:number)=>{captured=revision;return{state:'rejected',status:503,code:'test-no-producer'};};
 c.capabilities={controlled_test_available:true} as any;
 await c.evaluate();expect(captured).toBe(3);
});
test('a new explicit start after a confirmed refusal preserves the old intent and uses a new identity',async()=>{
 const f=fixture(),c=new FirstUseV3Controller(f.ports);await c.restore();
 const old:any={request_id:'refused',command,state:'denied',receipt:{request_id:'refused',state:'DENIED'}};
 await f.journal.save({...c.state,intent:old});await c.restore();await c.startCommand(command);
 expect(c.state?.intent?.request_id).toBe('stable');expect(c.state?.source.previous_intents).toEqual([old]);expect(f.calls).toContain('POST');
});
test('confirmed declaration edit invalidates evaluations while retaining owned encounter and observation references',async()=>{
 const f=fixture(),c=new FirstUseV3Controller(f.ports);await c.restore();
 await f.journal.save({...c.state,source:{declarations:{source_revision:0},encounter_ref:'pilot',observed_episode_ref:'observed',snapshot:{snapshot_ref:'old'},evaluation:{evaluation_ref:'old'}}});await c.restore();
 f.ports.blueprint.saveDeclarations=async()=>({state:'confirmed',value:{source_revision:1}});
 f.ports.blueprint.read=async()=>({state:'confirmed',value:{source_revision:1}});
 const saved=await c.saveDeclarations({sessions_per_week:{state:'KNOWN',value:2}});
 expect(c.state?.source.encounter_ref).toBe('pilot');expect(c.state?.source.observed_episode_ref).toBe('observed');
 expect(c.state?.source.snapshot).toBeUndefined();expect(c.state?.source.evaluation).toBeUndefined();expect(saved).toBe(true);
});
test('creation availability off still reconciles an existing owned handoff as observation-only',async()=>{
 const f=fixture(),c=new FirstUseV3Controller(f.ports);await c.restore();
 f.ports.plan.capabilities=async()=>({state:'confirmed',value:{owner_id:7,controlled_test_available:false,controlled_authority:null}});
 f.ports.blueprint.read=async()=>({state:'confirmed',value:{source_revision:0}});
 f.sessions.handoff=async()=>({state:'confirmed',value:{handoff:{request_id:'old',state:'CREATED',session_id:12}}});
 f.sessions.execution=async()=>({state:'confirmed',value:{session_id:12,status:'in_progress',allowed_actions:['RECORD_FACT'],observation_only:true,applicability:{state:'UNKNOWN'}}});
 await c.load();expect(c.state?.execution?.session_id).toBe(12);expect(c.state?.execution?.allowed_actions).not.toContain('NEXT_WORK_SET');
});
test('pilot read completed after pause cannot restore old guidance; past facts remain',async()=>{
 const f=fixture(),c=new FirstUseV3Controller(f.ports);await c.restore();
 await f.journal.save({...c.state,source:{encounter_ref:'pilot'}});await c.restore();
 const view:any={encounter_ref:'pilot',result:{phase:'TRIAL'},allowed_actions:['INITIATE_TRIAL'],authority:{generation:1},progress:{observation_refs:['actual'],observed_attempt_count:1,ledger_complete:true}};
 c.encounter=view;let resolve!:(value:unknown)=>void;f.ports.calibration.read=()=>new Promise(done=>{resolve=done;});
 const pending=c.readCalibration();await Promise.resolve();await c.pause();
 resolve({state:'confirmed',value:view});await pending;
 expect(c.encounter?.allowed_actions).toEqual([]);expect(c.encounter?.result).toBeNull();expect(c.encounter?.progress.observation_refs).toEqual(['actual']);
});
test('failed pilot reread removes guidance while preserving historical observation details',async()=>{
 const f=fixture(),c=new FirstUseV3Controller(f.ports);await c.restore();await f.journal.save({...c.state,source:{encounter_ref:'pilot'}});await c.restore();
 c.encounter={result:{phase:'TRIAL'},allowed_actions:['INITIATE_TRIAL'],authority:{generation:1},progress:{observation_refs:['actual']}} as any;
 f.ports.calibration.read=async()=>({state:'unknown'});await c.readCalibration();
 expect(c.encounter?.allowed_actions).toEqual([]);expect(c.encounter?.result).toBeNull();expect(c.encounter?.progress.observation_refs).toEqual(['actual']);
});
test('an explicitly corrected acked fact uses the latest server revision and keeps a completed session closed',async()=>{
 const f=fixture(),c=new FirstUseV3Controller(f.ports);await c.restore();
 const fact:any={context:{load_semantics:'PER_IMPLEMENT'},setting:{kind:'MASS_KG',value:12,unit:'kg'},reps:9,completed:true,performed_at:'2026-11-08T12:00:00Z'};
 const execution:any={session_id:2,status:'completed',allowed_actions:[],observation_only:true,applicability:{state:'UNKNOWN'},exercises:[{se_id:3,prescription:fact,sets:[{set_id:4,revision:3,completed:true}]}]};
 await f.journal.save({...c.state,phase:'COMPLETE',execution,local_facts:{'4':{op_id:'old',fact,local_revision:1,expected_server_revision:0,sync:'acked'}}});await c.restore();
 let sent:any;f.journal.commitSet=async(op:any,_command:any,state:any)=>{sent=op;await f.journal.save(state);};
 await c.recordFact(4,12,10,'2026-11-08T12:00:00Z',false);
 expect(sent.expected_server_revision).toBe(3);expect(sent.local_revision).toBe(2);expect(c.state?.phase).toBe('COMPLETE');
});
test('a pilot mutation completed after background does not launch a fresh permission read in that background generation',async()=>{
 const f=fixture(),c=new FirstUseV3Controller(f.ports);await c.restore();await f.journal.save({...c.state,source:{encounter_ref:'pilot'}});await c.restore();
 const view:any={encounter_ref:'pilot',source_revision:0,result:{phase:'TRIAL'},allowed_actions:['INITIATE_TRIAL'],authority:{generation:1},progress:{observation_refs:['actual']}};
 c.encounter=view;let finish!:(value:unknown)=>void,entered!:()=>void;const sent=new Promise<void>(done=>{entered=done;});
 f.ports.calibration.record=()=>new Promise(done=>{finish=done;entered();});
 f.ports.calibration.read=jest.fn(async()=>({state:'confirmed',value:view}));
 f.ports.blueprint.read=async()=>({state:'confirmed',value:{source_revision:1}});
 const pending=c.recordCalibration({kind:'CALIBRATION_ACTION_REQUESTED',action:'INITIATE_TRIAL'});await sent;await c.pause();
 finish({state:'confirmed',value:{event_ref:'actual-receipt'}});await pending;
 expect(f.ports.calibration.read).not.toHaveBeenCalled();expect(c.encounter?.allowed_actions).toEqual([]);
});
test('returning to a historical first session preserves the immutable local operation sequence',async()=>{
 const f=fixture(),c=new FirstUseV3Controller(f.ports);await c.restore();
 const fact:any={context:{load_semantics:'PER_IMPLEMENT'},setting:{kind:'MASS_KG',value:12,unit:'kg'},reps:9,completed:true,performed_at:'2026-11-08T12:00:00Z'};
 const execution:any={session_id:2,status:'completed',allowed_actions:[],observation_only:true,applicability:{state:'UNKNOWN'},exercises:[{se_id:3,prescription:fact,sets:[{set_id:4,revision:3,completed:true}]}]};
 f.journal.history=async()=>[{session_id:2,set_id:4,local_revision:5,state:'acked'}];
 await f.journal.save({...c.state,phase:'COMPLETE',execution});await c.restore();
 let sent:any;f.journal.commitSet=async(op:any,_command:any,state:any)=>{sent=op;await f.journal.save(state);};
 await c.recordFact(4,12,10,'2026-11-08T12:00:00Z',false);
 expect(sent.local_revision).toBe(6);expect(sent.expected_server_revision).toBe(3);
});
test('backgrounding a closed first session preserves its completed lifecycle for later legacy admission',async()=>{
 const f=fixture(),c=new FirstUseV3Controller(f.ports);await c.restore();
 await f.journal.save({...c.state,phase:'COMPLETE',execution:{session_id:2,status:'completed',applicability:{state:'UNKNOWN'},allowed_actions:[]}});await c.restore();
 await c.pause();expect(c.state?.phase).toBe('COMPLETE');expect(c.state?.execution?.status).toBe('completed');
});
