import React,{act} from 'react';
import {createRoot} from 'test-renderer';
import {contextualFixture} from '../../../test/contextualHarness';
import {contextTarget} from './/referenceModel';
import {ContextualInstrument} from './/ContextualInstrument';
jest.mock('react-native-safe-area-context',()=>({useSafeAreaInsets:()=>({top:24,bottom:24,left:0,right:0})}));
const flush=async()=>{for(let i=0;i<100;i++)await Promise.resolve();};
test('resolved command does not impose its unapplied expected revision on the retained server fact',async()=>{
 const f=contextualFixture(),id=f.set.set_id,fact:any={completed:true,reps:8,setting:{kind:'MASS_KG',unit:'kg',value:18.5},context:f.exercise.prescription.context,performed_at:'2026-11-24T08:00:00Z',performed_at_estimated:false};
 f.state.local_facts[String(id)]={op_id:'retired-pending',fact,local_revision:2,expected_server_revision:1,sync:'resolved'};
 f.set.completed=true;f.set.revision=1;f.set.reps=7;f.set.observation={...fact,reps:7,setting:{kind:'MASS_KG',unit:'kg',value:20}};
 const c:any={state:f.state,loading:false,localOperations:[{owner_id:7,session_id:f.execution.session_id,se_id:f.exercise.se_id,set_id:id,op_id:'retired-pending',local_revision:2,expected_server_revision:1,fact,state:'resolved'}],notice:null};
 const root=createRoot();
 await act(async()=>{root.render(React.createElement(ContextualInstrument,{controller:c,target:contextTarget(f.state,id)!,reader:{sessions:async()=>({state:'confirmed',value:f.page}),detail:async()=>({state:'confirmed',value:f.detail})} as any,revision:1,current:()=>true,serverNowMs:Date.now(),onSync:async()=>{},onExit(){},onJournal(){},onSubmitted(){},onContinue(){}}));await flush();});
 expect(root.container.queryAll(n=>n.props.testID==='context-recorded-value')).toHaveLength(1);
 await act(async()=>root.unmount());
});
