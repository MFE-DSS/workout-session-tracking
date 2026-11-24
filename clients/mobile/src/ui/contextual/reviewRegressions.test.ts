import React,{act} from 'react';
import {createRoot} from 'test-renderer';
import {contextualFixture} from '../../../test/contextualHarness';
import {contextTarget} from './/referenceModel';
import {ContextualInstrument} from './/ContextualInstrument';
jest.mock('react-native-safe-area-context',()=>({useSafeAreaInsets:()=>({top:24,bottom:24,left:0,right:0})}));
const flush=async()=>{for(let i=0;i<100;i++)await Promise.resolve();};
async function renderFact(mode:'resolved'|'server-uncompleted'|'server-stale'){
 const f=contextualFixture(),id=f.set.set_id,fact:any={completed:true,reps:8,setting:{kind:'MASS_KG',unit:'kg',value:18.5},context:f.exercise.prescription.context,performed_at:'2026-11-24T08:00:00Z',performed_at_estimated:false};
 const sync=mode==='resolved'?'resolved':'acked';
 f.state.local_facts[String(id)]={op_id:'prior-command',fact,local_revision:1,expected_server_revision:0,sync};
 if(mode==='server-uncompleted'||mode==='server-stale'){f.set.completed=false;f.set.revision=mode==='server-stale'?0:2;f.set.reps=0;f.set.observation={...fact,reps:0,completed:false};}
 const c:any={state:f.state,loading:false,localOperations:[{owner_id:7,session_id:f.execution.session_id,se_id:f.exercise.se_id,set_id:id,op_id:'prior-command',local_revision:1,fact,state:sync}],notice:null};
 const root=createRoot();
 await act(async()=>{root.render(React.createElement(ContextualInstrument,{controller:c,target:contextTarget(f.state,id)!,reader:{sessions:async()=>({state:'confirmed',value:f.page}),detail:async()=>({state:'confirmed',value:f.detail})} as any,revision:1,current:()=>true,serverNowMs:Date.now(),onSync:async()=>{},onExit(){},onJournal(){},onSubmitted(){},onContinue(){}}));await flush();});
 return root;
}
test('resolved refusal must release stale saved fact and allow work to continue',async()=>{
 const root=await renderFact('resolved');
 const button=root.container.queryAll(n=>n.props.accessibilityLabel==='Continuer la séance')[0];
 expect(button).toBeDefined();
 expect(button?.props.accessibilityState?.disabled).not.toBe(true);
 await act(async()=>root.unmount());
});
test('effective server removal of completion must stop presenting old completed values',async()=>{
 const root=await renderFact('server-uncompleted');
 const old=root.container.queryAll(n=>n.props.testID==='context-recorded-value');

 expect(old).toHaveLength(0);
 await act(async()=>root.unmount());
});
import {useContextRead} from './/useContextRead';
test('canonical reread changing the source revision must invalidate the earlier reference',async()=>{
 const f=contextualFixture();let output:any;
 const reader:any={sessions:jest.fn(async()=>({state:'confirmed',value:f.page})),detail:jest.fn(async()=>({state:'confirmed',value:JSON.parse(JSON.stringify(f.detail))}))};
 function V(){output=useContextRead(reader,contextTarget(f.state,f.set.set_id)!,1,()=>true);return null;}
 const root=createRoot();await act(async()=>{root.render(React.createElement(V));await flush();});
 expect(output.read.reference.value).toBe(17.5);
 f.exercise.sets[0].revision=2;f.exercise.sets[0].observation!.setting!.value=20;
 await act(async()=>{root.render(React.createElement(V));await flush();});

 expect(output.read?.reference?.revision).not.toBe(1);
 await act(async()=>root.unmount());
});

test('a server read older than the command receipt cannot negate that receipt',async()=>{
 const root=await renderFact('server-stale');expect(root.container.queryAll(n=>n.props.testID==='context-recorded-value')).toHaveLength(1);await act(async()=>root.unmount());
});
