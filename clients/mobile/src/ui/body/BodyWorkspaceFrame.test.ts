import React,{act} from 'react';
import {createRoot} from 'test-renderer';
import {BodyWorkspaceFrame} from './BodyWorkspaceFrame';
jest.mock('react-native-safe-area-context',()=>({useSafeAreaInsets:()=>({top:47,bottom:34,left:0,right:0})}));
test('workspace owns explicit top inset even inside retained native tabs',async()=>{
 const root=createRoot();await act(async()=>root.render(React.createElement(BodyWorkspaceFrame,{inTab:true,onBack:()=>{},disabled:false,children:'content'})));
 const scroll=root.container.queryAll((n:any)=>n.props.keyboardShouldPersistTaps==='handled')[0].props;
 expect(scroll.contentInsetAdjustmentBehavior).toBe('never');
 const viewport=root.container.queryAll((n:any)=>n.props.testID==='body-safe-viewport')[0].props;
 expect(viewport.style.paddingTop).toBe(47);expect(viewport.style.paddingBottom).toBe(34);
 expect(scroll.contentContainerStyle.paddingTop).toBe(8);
 await act(async()=>root.unmount());
});
