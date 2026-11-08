import {workPositionV3,workPermissionV3} from './planV3Workout';
import type {PlanV3Stored} from './planV3Types';
function state():PlanV3Stored{return {profile:'PLAN_V3',local_version:'first-session-local/3.0.0',owner_id:7,phase:'ACTIVE',intent:null,source:{},drafts:{},local_facts:{},execution:{session_id:1,status:'in_progress',applicability:{state:'CURRENT'},allowed_actions:['NEXT_WORK_SET'],observation_only:false,exercises:[
 {se_id:2,prescription:{dose:{rest_seconds:120}},sets:[{set_id:3,completed:true,completed_at:'2026-11-08T12:00:00Z',transition_after_set:{kind:'REST_THEN_SET',duration_seconds:120}},{set_id:4,completed:false}]},
 {se_id:5,prescription:{dose:{rest_seconds:90}},sets:[{set_id:6,completed:false}]}]} as any};}
test('exact prescribed rest gates the next set; setup between exercises has no invented timer',()=>{
 const s=state();expect(workPositionV3(s)?.set.set_id).toBe(4);
 expect(workPermissionV3(s,Date.parse('2026-11-08T12:01:00Z'))).toMatchObject({state:'REST',remaining_ms:60000});
 expect(workPermissionV3(s,Date.parse('2026-11-08T12:02:00Z')).state).toBe('WORK');
 s.execution!.exercises[0].sets[1].completed=true;
 expect(workPermissionV3(s,Date.parse('2026-11-08T12:03:00Z')).state).toBe('SETUP');
});
test('local pending fact and unknown authority never authorize a new work instruction',()=>{
 const s=state();s.local_facts['3']={op_id:'o',local_revision:1,expected_server_revision:0,sync:'saved_local',fact:{} as any};
 expect(workPermissionV3(s,Date.now()).state).toBe('WAIT_SYNC');
 s.local_facts={};s.execution!.applicability.state='UNKNOWN';expect(workPermissionV3(s,Date.now()).state).toBe('OBSERVATION_ONLY');
});
test('a newer server correction can make a previously acked local set incomplete again',()=>{
 const local:any={profile:'PLAN_V3',source:{},local_facts:{'1':{op_id:'old',expected_server_revision:0,sync:'acked',fact:{completed:true}}},execution:{status:'in_progress',exercises:[{se_id:2,sets:[{set_id:1,revision:2,completed:false}]}]}};
 expect(workPositionV3(local)?.set.set_id).toBe(1);
});
test('a definitively refused local edit cannot hide the server version or advance its current cursor',()=>{
 const state:any={source:{},local_facts:{'1':{op_id:'refused',expected_server_revision:0,sync:'failed',fact:{completed:true,reps:10}}},execution:{status:'in_progress',exercises:[{sets:[{set_id:1,revision:2,completed:false,reps:null,observation:null}]}]}};
 expect(workPositionV3(state)?.set.set_id).toBe(1);
});
