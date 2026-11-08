/** Execution projection only; no dose, increments or readiness are inferred locally. */
import type {PlanV3Stored} from './planV3Types';
export function currentSetFactV3(state:PlanV3Stored,set:NonNullable<PlanV3Stored['execution']>['exercises'][number]['sets'][number]){
 const local=state.local_facts[String(set.set_id)];
 if(local&&local.sync!=='resolved'&&local.sync!=='failed'&&!(local.sync==='acked'&&set.revision>local.expected_server_revision+1))
  return {completed:local.fact.completed,reps:local.fact.reps,observation:local.fact,completed_at:local.fact.performed_at,sync:local.sync};
 return {completed:set.completed,reps:set.reps,observation:set.observation,completed_at:set.completed_at,sync:'server' as const};
}
export function workPositionV3(state:PlanV3Stored){
 const execution=state.execution;if(!execution)return null;
 for(let ei=0;ei<execution.exercises.length;ei++){
  const exercise=execution.exercises[ei];
  for(let si=0;si<exercise.sets.length;si++){
   const set=exercise.sets[si];
   if(!currentSetFactV3(state,set).completed)return {exercise,set,exerciseIndex:ei,setIndex:si};
  }
 }return null;
}
export type WorkPermissionV3={state:'WORK'|'REST'|'SETUP'|'WAIT_SYNC'|'OBSERVATION_ONLY'|'COMPLETE';remaining_ms?:number;reason?:string};
export function workPermissionV3(state:PlanV3Stored,serverNowMs:number):WorkPermissionV3 {
 const ex=state.execution;
 if(!ex||ex.status!=='in_progress')return {state:'OBSERVATION_ONLY'};
 if(ex.applicability.state!=='CURRENT'||ex.observation_only||!ex.allowed_actions.includes('NEXT_WORK_SET'))return {state:'OBSERVATION_ONLY'};
 if(Object.values(state.local_facts).some(f=>f.sync!=='acked'&&f.sync!=='resolved'))return {state:'WAIT_SYNC'};
 const position=workPositionV3(state);if(!position)return {state:'COMPLETE'};
 const {exercise,setIndex,exerciseIndex,set}=position;
 if(setIndex>0){
  const previous=exercise.sets[setIndex-1];
  const transition=previous.transition_after_set;
  if(!transition||transition.kind!=='REST_THEN_SET'||!previous.completed_at||!Number.isFinite(serverNowMs))return {state:'OBSERVATION_ONLY',reason:'REST_TIME_UNKNOWN'};
  const end=Date.parse(previous.completed_at)+transition.duration_seconds*1000;
  if(!Number.isFinite(end))return {state:'OBSERVATION_ONLY',reason:'REST_TIME_UNKNOWN'};
  if(serverNowMs<end)return {state:'REST',remaining_ms:end-serverNowMs};
 }
 if(setIndex===0&&exerciseIndex>0&&state.source.setup_confirmed_for!==set.set_id)return {state:'SETUP'};
 return {state:'WORK'};
}
