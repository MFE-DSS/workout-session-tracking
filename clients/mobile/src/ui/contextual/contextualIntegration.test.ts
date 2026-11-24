import React,{act} from 'react';
import {createRoot} from 'test-renderer';
import {PlanV3ExecutionScreen} from '../plan/PlanV3ExecutionScreen';
import {contextualFixture} from '../../../test/contextualHarness';
jest.mock('react-native-safe-area-context',()=>({useSafeAreaInsets:()=>({top:24,bottom:24,left:0,right:0})}));
const event={nativeEvent:{},stopPropagation(){},currentTarget:1,target:1},flush=async()=>{for(let i=0;i<100;i++)await Promise.resolve();};
test('real execution consumer pins submitted set feedback while controller cursor moves to another exercise',async()=>{
 const f=contextualFixture(),target=f.set.set_id;let sends=0;
 const c:any={state:f.state,active:true,loading:false,localOperations:[],notice:null,eventTime:()=>({epochMs:Date.parse('2026-11-24T09:00:00Z'),estimated:false}),refreshExecution:async()=>{},beginNext:async()=>{},recordFact:async(id:number,value:number,reps:number,at:string,estimated:boolean)=>{
  sends++;const fact={setting:{kind:'MASS_KG',unit:'kg',value},context:f.exercise.prescription.context,reps,completed:true,performed_at:at,performed_at_estimated:estimated};
  c.state={...c.state,phase:'PAUSED',local_facts:{[id]:{op_id:'op-1',fact,local_revision:1,expected_server_revision:0,sync:'acked'}}};
  c.localOperations=[{owner_id:7,session_id:f.execution.session_id,se_id:f.exercise.se_id,set_id:id,local_revision:1,expected_server_revision:0,op_id:'op-1',fact,state:'acked'}];
  f.set.completed=true;f.set.reps=reps;f.set.revision=1;f.set.observation=fact as any;
 }};
 const reader:any={sessions:async()=>({state:'confirmed',value:f.page}),detail:async()=>({state:'confirmed',value:f.detail})};
 const root=createRoot(),by=(id:string)=>root.container.queryAll(n=>n.props.testID===id)[0];const props={controller:c,contextual:{reader,revision:1,current:()=>true},serverNowMs:Date.now(),onSync:async()=>{},onExit(){}};
 await act(async()=>{root.render(React.createElement(PlanV3ExecutionScreen,props));await flush();});expect(by('context-instrument')).toBeDefined();
 await act(async()=>by('context-edit-load').props.onClick(event));await act(async()=>by('context-load').props.onChangeText('19'));await act(async()=>by('context-edit-reps').props.onClick(event));await act(async()=>by('context-reps').props.onChangeText('8'));await act(async()=>by('context-submit').props.onClick(event));
 await act(async()=>{root.render(React.createElement(PlanV3ExecutionScreen,props));await flush();});
 expect(by('context-instrument')).toBeDefined();expect(root.container.queryAll(n=>n.props.testID==='context-load')).toHaveLength(0);expect(sends).toBe(1);expect(c.localOperations[0].set_id).toBe(target);
 await act(async()=>root.unmount());
});
test('cold-restored uncertain set stays in its instrument when its receipt is later reconciled',async()=>{
 const f=contextualFixture(),id=f.set.set_id,fact:any={completed:true,reps:8,setting:{kind:'MASS_KG',unit:'kg',value:18.5},context:f.exercise.prescription.context,performed_at:'2026-11-24T09:00:00Z',performed_at_estimated:false};
 f.set.completed=true;f.set.revision=1;f.set.reps=8;f.set.observation=fact;f.state.local_facts[String(id)]={op_id:'restored',fact,local_revision:1,expected_server_revision:0,sync:'saved_local'};
 const c:any={state:f.state,active:true,loading:false,localOperations:[{owner_id:7,session_id:f.execution.session_id,set_id:id,state:'pending',fact,op_id:'restored',local_revision:1,expected_server_revision:0}],notice:null};
 const reader:any={sessions:async()=>({state:'confirmed',value:f.page}),detail:async()=>({state:'confirmed',value:f.detail})},props={controller:c,contextual:{reader,revision:1,current:()=>true},serverNowMs:Date.now(),onSync:async()=>{},onExit(){}};
 const root=createRoot();await act(async()=>{root.render(React.createElement(PlanV3ExecutionScreen,props));await flush();});expect(root.container.queryAll(n=>n.props.testID==='context-instrument')).toHaveLength(1);
 c.localOperations[0].state='acked';f.state.local_facts[String(id)].sync='acked';
 await act(async()=>{root.render(React.createElement(PlanV3ExecutionScreen,props));await flush();});expect(root.container.queryAll(n=>n.props.testID==='context-instrument')).toHaveLength(1);
 await act(async()=>root.unmount());
});
