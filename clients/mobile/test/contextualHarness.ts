import type {ExecutionV3,PlanV3Stored} from '../src/domain/planV3Types';
import {scienceHistory,historyPage} from './trainingHistoryHarness';
export function contextualFixture(){
 const s=scienceHistory(),execution=s.execution as ExecutionV3;
 execution.status='in_progress';execution.ended_at=null;execution.observation_only=false;execution.applicability.state='CURRENT';execution.allowed_actions=['NEXT_WORK_SET','RECORD_FACT','FINISH'];
 const exercise=execution.exercises.find(e=>e.canonical_exercise_id==='leg-extensions-assises')!;
 if(!exercise)throw Error('canonical SCI fixture no longer has the admitted pilot');
 const set=exercise.sets[1];execution.cursor={exercise_index:execution.exercises.indexOf(exercise),set_index:1,set_id:set.set_id};
 const state:PlanV3Stored={profile:'PLAN_V3',local_version:'first-session-local/3.0.0',owner_id:7,phase:'ACTIVE',intent:null,execution,source:{},local_facts:{},drafts:{}};
 const page=historyPage();page.entries=[s.entry];
 return{state,execution,exercise,set,page,detail:{kind:'SCI' as const,execution}};
}
