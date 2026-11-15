import React,{act} from 'react';
import {AppState,BackHandler,Keyboard} from 'react-native';
import {createRoot,type Root} from 'test-renderer';
import {ProgramBuilderHost} from './ProgramBuilderHost';
import {LibraryScreen,type LibraryScreenProps} from '../library/LibraryScreen';
import type {ProgramBuilderPorts} from './ProgramBuilderController';
jest.mock('react-native-safe-area-context',()=>({useSafeAreaInsets:()=>({top:47,bottom:34,left:0,right:0})}));
let root:Root;beforeEach(()=>{root=createRoot();});afterEach(async()=>{await act(async()=>root.unmount());jest.restoreAllMocks();});
const flush=async()=>{for(let i=0;i<30;i++)await Promise.resolve();};
const node=(id:string)=>root.container.queryAll((n:any)=>n.props.testID===id)[0]?.props;
const press=async(id:string)=>act(async()=>{node(id).onClick({nativeEvent:{},stopPropagation:()=>{},currentTarget:1,target:1});await flush();});
function ports(){const p={client:{ownerId:1,backendScope:'https://qa.invalid',programs:jest.fn(async()=>({state:'confirmed',value:{items:[],next_cursor:null}})),submit:jest.fn()},store:{ownerId:1,backendScope:'https://qa.invalid',pending:jest.fn(async()=>[])},current:()=>true,newId:()=> 'id'};return p as unknown as ProgramBuilderPorts;}
test('native Host foreground refresh is GET only and Android back reaches existing library',async()=>{
 let back=()=>false,foreground=(s:string)=>{};
 jest.spyOn(BackHandler,'addEventListener').mockImplementation((_e,h)=>{back=()=>h(undefined as never)===true;return{remove:jest.fn()};});
 jest.spyOn(AppState,'addEventListener').mockImplementation((_e,h)=>{foreground=h as (s:string)=>void;return{remove:jest.fn()};});
 const p=ports(),onBack=jest.fn();await act(async()=>{root.render(React.createElement(ProgramBuilderHost,{ports:p,onBack}));await flush();});
 expect(p.client.programs).toHaveBeenCalledTimes(1);await act(async()=>{foreground('active');await flush();});expect(p.client.programs).toHaveBeenCalledTimes(2);expect(p.client.submit).not.toHaveBeenCalled();
 await act(async()=>{expect(back()).toBe(true);await flush();});expect(onBack).toHaveBeenCalledTimes(1);
});
test('leaving a nonempty unsent draft requires explicit discard and never claims server cancellation',async()=>{
 const p=ports(),onBack=jest.fn();await act(async()=>{root.render(React.createElement(ProgramBuilderHost,{ports:p,onBack}));await flush();});await press('builder-create');
 await act(async()=>{node('builder-title').onChangeText('Personnel');await flush();});
 await press('builder-back');expect(node('builder-leave-confirm')).toBeDefined();expect(onBack).not.toHaveBeenCalled();
 await press('builder-stay');expect(node('builder-title').value).toBe('Personnel');await press('builder-back');await press('builder-leave-confirm');expect(node('builder-create')).toBeDefined();expect(p.client.submit).not.toHaveBeenCalled();
});
test('hardware back dismisses keyboard before leaving acquisition',async()=>{
 let back=()=>false,shown=()=>{};jest.spyOn(BackHandler,'addEventListener').mockImplementation((_e,h)=>{back=()=>h(undefined as never)===true;return{remove:jest.fn()};});
 jest.spyOn(Keyboard,'addListener').mockImplementation((event,h)=>{if(event==='keyboardDidShow')shown=h as ()=>void;return{remove:jest.fn()};});const dismiss=jest.spyOn(Keyboard,'dismiss').mockImplementation(()=>{});
 const onBack=jest.fn();await act(async()=>{root.render(React.createElement(ProgramBuilderHost,{ports:ports(),onBack}));await flush();});await act(async()=>{shown();back();await flush();});expect(dismiss).toHaveBeenCalledTimes(1);expect(onBack).not.toHaveBeenCalled();
});
test('library management entry exists only when connected to a real builder callback',async()=>{
 const p={state:{view:'INDEX',index:{status:'confirmed',previous:false,value:{entries:[],next_cursor:null}},detail:{status:'idle',previous:false}},opening:{phase:'idle'},query:{section:'all',zone:null},onRefresh:()=>{}} as unknown as LibraryScreenProps;
 await act(async()=>root.render(React.createElement(LibraryScreen,p)));expect(node('library-builder')).toBeUndefined();const onBuilder=jest.fn();await act(async()=>root.render(React.createElement(LibraryScreen,{...p,onBuilder})));await press('library-builder');expect(onBuilder).toHaveBeenCalledTimes(1);
});

test('inactive mounted workspace neither captures Android Back nor refreshes on app foreground',async()=>{
 let back=()=>false,foreground=(s:string)=>{};
 jest.spyOn(BackHandler,'addEventListener').mockImplementation((_e,h)=>{back=()=>h(undefined as never)===true;return{remove:jest.fn()};});
 jest.spyOn(AppState,'addEventListener').mockImplementation((_e,h)=>{foreground=h as (s:string)=>void;return{remove:jest.fn()};});
 const p=ports(),onBack=jest.fn();await act(async()=>{root.render(React.createElement(ProgramBuilderHost,{ports:p,onBack,active:true}));await flush();});
 await press('builder-create');await act(async()=>{node('builder-title').onChangeText('Conservé');root.render(React.createElement(ProgramBuilderHost,{ports:p,onBack,active:false}));await flush();});
 const reads=(p.client.programs as jest.Mock).mock.calls.length;await act(async()=>{expect(back()).toBe(false);foreground('active');await flush();});expect(p.client.programs).toHaveBeenCalledTimes(reads);expect(onBack).not.toHaveBeenCalled();
 await act(async()=>{root.render(React.createElement(ProgramBuilderHost,{ports:p,onBack,active:true}));await flush();});expect(node('builder-title').value).toBe('Conservé');expect(p.client.submit).not.toHaveBeenCalled();
});
