import React, { act } from 'react';
import { createRoot, type Root } from 'test-renderer';
import { FirstUseContent, FirstUseScreen } from './FirstUseScreen';
import type { FirstUseState } from '../../api/firstUse';
jest.mock('react-native-safe-area-context',()=>({useSafeAreaInsets:()=>({top:47,bottom:34,left:0,right:0})}));
let root:Root;
beforeEach(()=>{root=createRoot();});afterEach(async()=>{await act(async()=>root.unmount());});
const find=(id:string)=>root.container.queryAll(n=>n.props.testID===id)[0]?.props;
const click=async(id:string)=>{await act(async()=>find(id).onClick({nativeEvent:{},stopPropagation(){},currentTarget:1,target:1}));};
test.each<FirstUseState>([{state:'loading'},{state:'no_plan_producer'},{state:'required_consent'},{state:'missing_information',missing:['sessions_per_week']},{state:'unknown'},{state:'unavailable',reason:'POLICY_UNAVAILABLE'}])('state $state has an honest exit without body fields, inventory or fake prescription',async(state)=>{
 const today=jest.fn(),prefs=jest.fn(),reload=jest.fn();
 await act(async()=>root.render(React.createElement(FirstUseContent,{state,onToday:today,onPreferences:prefs,onReload:reload,onBack:today})));
 expect(find('first-use-today')).toBeDefined();await click('first-use-today');expect(today).toHaveBeenCalledTimes(1);
 expect(root.container.queryAll(n=>n.type==='input')).toHaveLength(0);
 if(state.state==='no_plan_producer'){await click('first-use-preferences');expect(prefs).toHaveBeenCalledTimes(1);}
 if(state.state==='unknown'){await click('first-use-reload');expect(reload).toHaveBeenCalledTimes(1);}
});
test('screen subscribes to its current controller and invalidates late reads when closed',async()=>{
 let state:FirstUseState={state:'loading'},listener=()=>{};
 const controller={get state(){return state;},subscribe:(fn:()=>void)=>{listener=fn;return()=>{listener=()=>{};};},load:jest.fn(async()=>state),invalidate:jest.fn()};
 await act(async()=>root.render(React.createElement(FirstUseScreen,{controller,onToday(){},onPreferences(){},onBack(){}})));
 expect(controller.load).toHaveBeenCalledTimes(1);
 await act(async()=>{state={state:'unknown'};listener();});expect(find('first-use-reload')).toBeDefined();
 await act(async()=>root.unmount());expect(controller.invalidate).toHaveBeenCalledTimes(1);
});
