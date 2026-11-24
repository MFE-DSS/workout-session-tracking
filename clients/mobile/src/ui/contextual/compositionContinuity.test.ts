import React,{act} from 'react';
import {Keyboard} from 'react-native';
import {createRoot} from 'test-renderer';
import {contextualFixture} from '../../../test/contextualHarness';
import {contextTarget} from './referenceModel';
import {ContextualInstrument} from './ContextualInstrument';
jest.mock('react-native-safe-area-context',()=>({useSafeAreaInsets:()=>({top:24,bottom:24,left:0,right:0})}));
const event={nativeEvent:{},stopPropagation(){},currentTarget:1,target:1},flush=async()=>{for(let i=0;i<100;i++)await Promise.resolve();};
function setup(){const f=contextualFixture(),c:any={state:f.state,active:true,loading:false,localOperations:[],notice:null,recordFact:jest.fn(),refreshExecution:async()=>{}};return{f,c,props:{controller:c,target:contextTarget(f.state,f.set.set_id)!,reader:{sessions:async()=>({state:'confirmed' as const,value:f.page}),detail:async()=>({state:'confirmed' as const,value:f.detail})},revision:1,current:()=>true,serverNowMs:Date.now(),onSync:async()=>{},onExit(){},onJournal(){},onSubmitted(){},onContinue(){}}};}
test('system IME keeps the confirmed reference visible; cancelling one field retains the other draft and sends nothing',async()=>{
 const handlers:Record<string,()=>void>={};const spy=jest.spyOn(Keyboard,'addListener').mockImplementation(((name:string,fn:()=>void)=>{handlers[name]=fn;return{remove(){}};}) as any);
 const {c,props}=setup(),root=createRoot(),by=(id:string)=>root.container.queryAll(n=>n.props.testID===id)[0];
 await act(async()=>{root.render(React.createElement(ContextualInstrument,props));await flush();});
 await act(async()=>by('context-edit-load').props.onClick(event));await act(async()=>by('context-load').props.onChangeText('18,5'));
 await act(async()=>handlers.keyboardDidShow());expect(by('context-reference-value')).toBeDefined();
 await act(async()=>by('context-edit-reps').props.onClick(event));await act(async()=>by('context-reps').props.onChangeText('8'));await act(async()=>by('context-cancel').props.onClick(event));
 expect(c.recordFact).not.toHaveBeenCalled();await act(async()=>by('context-edit-load').props.onClick(event));expect(by('context-load').props.value).toBe('18,5');
 await act(async()=>root.unmount());spy.mockRestore();
});
test('the same current-set chassis and both typed windows survive uncertain delivery then confirmed server readback',async()=>{
 const {f,c,props}=setup(),root=createRoot(),by=(id:string)=>root.container.queryAll(n=>n.props.testID===id)[0];
 await act(async()=>{root.render(React.createElement(ContextualInstrument,props));await flush();});
 const object=by('context-current-set'),load=by('context-load-window'),reps=by('context-reps-window');expect(object).toBeDefined();expect(load).toBeDefined();expect(reps).toBeDefined();
 const fact:any={completed:true,reps:8,setting:{kind:'MASS_KG',unit:'kg',value:18.5},context:f.exercise.prescription.context,performed_at:'2026-11-24T09:00:00Z',performed_at_estimated:false};
 f.state.local_facts[String(f.set.set_id)]={op_id:'stable-c',fact,local_revision:1,expected_server_revision:0,sync:'saved_local'};
 c.localOperations=[{owner_id:7,session_id:f.execution.session_id,set_id:f.set.set_id,op_id:'stable-c',fact,local_revision:1,expected_server_revision:0,state:'pending'}];
 await act(async()=>{root.render(React.createElement(ContextualInstrument,props));await flush();});expect(by('context-current-set')).toBe(object);expect(by('context-load-window')).toBe(load);expect(by('context-reps-window')).toBe(reps);expect(by('context-recorded-value')).toBeDefined();
 c.localOperations[0].state='acked';f.state.local_facts[String(f.set.set_id)].sync='acked';f.set.completed=true;f.set.revision=1;f.set.reps=8;f.set.observation=fact;
 await act(async()=>{root.render(React.createElement(ContextualInstrument,{...props,target:contextTarget(f.state,f.set.set_id)!,revision:2}));await flush();});expect(by('context-current-set')).toBe(object);expect(by('context-load-window')).toBe(load);expect(by('context-reps-window')).toBe(reps);expect(c.recordFact).not.toHaveBeenCalled();
 await act(async()=>root.unmount());
});
test('the accessible reference names its actual value, typed unit and repetitions',async()=>{const {props}=setup(),root=createRoot();await act(async()=>{root.render(React.createElement(ContextualInstrument,props));await flush();});const ref=root.container.queryAll(n=>n.props.testID==='context-reference-value')[0];expect(ref.props.accessibilityLabel).toContain('17,5 kg affichés');expect(ref.props.accessibilityLabel).toContain('9 répétitions');await act(async()=>root.unmount());});
