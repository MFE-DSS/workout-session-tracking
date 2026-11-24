import React,{act} from 'react';
import {createRoot} from 'test-renderer';
import {contextualFixture} from '../../../test/contextualHarness';
import {contextTarget} from './referenceModel';
import {ContextualInstrument} from './ContextualInstrument';
jest.mock('react-native-safe-area-context',()=>({useSafeAreaInsets:()=>({top:24,bottom:24,left:0,right:0})}));
const event={nativeEvent:{},stopPropagation(){},currentTarget:1,target:1};
const flush=async()=>{for(let i=0;i<100;i++)await Promise.resolve();};
test('reference is in Action, current fields stay empty, and one explicit confirmation keeps action-time provenance',async()=>{
 const f=contextualFixture(),at=Date.parse('2026-11-24T09:00:00Z'),c:any={state:f.state,loading:false,active:true,localOperations:[],notice:null,eventTime:()=>({epochMs:at,estimated:true}),recordFact:jest.fn(async()=>{}),refreshExecution:async()=>{},beginNext:async()=>{}};
 const reader:any={sessions:async()=>({state:'confirmed',value:f.page}),detail:async()=>({state:'confirmed',value:f.detail})};
 const root=createRoot();const by=(id:string)=>root.container.queryAll(n=>n.props.testID===id)[0];
 await act(async()=>{root.render(React.createElement(ContextualInstrument,{controller:c,target:contextTarget(f.state,f.set.set_id)!,reader,revision:1,current:()=>true,serverNowMs:Date.now(),onSync:async()=>{},onExit(){},onJournal(){},onSubmitted(){},onContinue(){}}));await flush();});
 await act(async()=>by('context-edit-load').props.onClick(event));expect(by('context-load').props.value).toBe('');expect(by('context-reference')).toBeDefined();expect(c.recordFact).not.toHaveBeenCalled();
 await act(async()=>by('context-load').props.onChangeText('18,5'));await act(async()=>by('context-edit-reps').props.onClick(event));expect(by('context-reps').props.value).toBe('');await act(async()=>by('context-reps').props.onChangeText('8'));
 await act(async()=>by('context-submit').props.onClick(event));
 expect(c.recordFact).toHaveBeenCalledTimes(1);expect(c.recordFact).toHaveBeenCalledWith(f.set.set_id,18.5,8,new Date(at).toISOString(),true);await act(async()=>root.unmount());
});
test('unavailable reference does not prevent otherwise allowed manual acquisition',async()=>{
 const f=contextualFixture(),c:any={state:f.state,loading:false,active:true,localOperations:[],notice:null};const root=createRoot();
 await act(async()=>{root.render(React.createElement(ContextualInstrument,{controller:c,target:contextTarget(f.state,f.set.set_id)!,reader:{sessions:async()=>({state:'unknown'})} as any,revision:1,current:()=>true,serverNowMs:Date.now(),onSync:async()=>{},onExit(){},onJournal(){},onSubmitted(){},onContinue(){}}));await flush();});
 expect(root.container.queryAll(n=>n.props.testID==='context-edit-load')).toHaveLength(1);expect(root.container.queryAll(n=>n.props.testID==='context-reference-value')).toHaveLength(0);await act(async()=>root.unmount());
});
test('newer effective server observation is the primary readout after acknowledged local submission',async()=>{
 const f=contextualFixture(),id=f.set.set_id,localFact={completed:true,reps:8,setting:{kind:'MASS_KG',unit:'kg',value:18.5},context:f.exercise.prescription.context,performed_at:'2026-11-24T08:00:00Z',performed_at_estimated:false};
 f.state.local_facts[String(id)]={op_id:'prior-command',fact:localFact as any,local_revision:1,expected_server_revision:0,sync:'acked'};
 f.set.completed=true;f.set.revision=2;f.set.reps=7;f.set.observation={...localFact,reps:7,setting:{kind:'MASS_KG',unit:'kg',value:20}} as any;
 const c:any={state:f.state,loading:false,localOperations:[],notice:null};const root=createRoot();
 await act(async()=>{root.render(React.createElement(ContextualInstrument,{controller:c,target:contextTarget(f.state,id)!,reader:{sessions:async()=>({state:'confirmed',value:f.page}),detail:async()=>({state:'confirmed',value:f.detail})} as any,revision:1,current:()=>true,serverNowMs:Date.now(),onSync:async()=>{},onExit(){},onJournal(){},onSubmitted(){},onContinue(){}}));await flush();});
 const primary=root.container.queryAll(n=>n.props.testID==='context-recorded-value')[0];expect(primary?.props.children).toContain('20');
 await act(async()=>root.unmount());
});
