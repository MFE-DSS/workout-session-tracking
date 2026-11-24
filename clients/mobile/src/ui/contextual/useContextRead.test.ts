import React,{act} from 'react';
import {createRoot} from 'test-renderer';
import {AppState} from 'react-native';
import {contextualFixture} from '../../../test/contextualHarness';
import {contextTarget} from './referenceModel';
import {useContextRead} from './useContextRead';
const descriptor=Object.getOwnPropertyDescriptor(AppState,'currentState')!;
const flush=async()=>{for(let i=0;i<60;i++)await Promise.resolve();};
afterEach(()=>{Object.defineProperty(AppState,'currentState',descriptor);jest.restoreAllMocks();});
test('background cancels an in-flight reference, foreground reacquires, and an account change hides it',async()=>{
 Object.defineProperty(AppState,'currentState',{value:'active',configurable:true});let listener:(s:any)=>void=()=>{};
 jest.spyOn(AppState,'addEventListener').mockImplementation((_e:any,l:any)=>{listener=l;return{remove(){}};});
 const f=contextualFixture(),t=contextTarget(f.state,f.set.set_id)!;let resolve:any;let owner=true;let output:any;
 const reader:any={sessions:jest.fn(()=>new Promise(r=>{resolve=r;})),detail:jest.fn(async()=>({state:'confirmed',value:f.detail}))};
 function View(p:{revision:number}){output=useContextRead(reader,t,p.revision,()=>owner);return null;}
 const root=createRoot();await act(async()=>root.render(React.createElement(View,{revision:1})));
 const late=resolve;await act(async()=>listener('background'));await act(async()=>{late({state:'confirmed',value:f.page});await flush();});
 expect(output.read).toBeNull();expect(reader.detail).not.toHaveBeenCalled();
 await act(async()=>listener('active'));await act(async()=>{resolve({state:'confirmed',value:f.page});await flush();});expect(output.read?.state).toBe('ready');
 owner=false;await act(async()=>root.render(React.createElement(View,{revision:2})));expect(output.read).toBeNull();expect(reader.sessions).toHaveBeenCalledTimes(2);
 await act(async()=>root.unmount());
});
