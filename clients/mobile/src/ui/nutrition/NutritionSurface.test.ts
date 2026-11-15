import React,{act} from 'react';
import {createRoot,type Root} from 'test-renderer';
import {NutritionSurface} from './NutritionSurface';
jest.mock('react-native-safe-area-context',()=>({SafeAreaProvider:({children}:any)=>children,SafeAreaView:({children,...props}:any)=>require('react').createElement(require('react-native').View,props,children),useSafeAreaInsets:()=>({top:47,bottom:34,left:0,right:0})}));
let root:Root;beforeEach(()=>{root=createRoot();});afterEach(async()=>{await act(async()=>root.unmount());});
const flush=async()=>{for(let i=0;i<100;i++)await Promise.resolve();};
const node=(id:string)=>root.container.queryAll((n:any)=>n.props.testID===id)[0]?.props;
function setup(granted=true){
 const consent={contract_version:'nutrition-manual/1.0.0',owner_id:7,purpose:'nutrition_manual',state:'PRESENT',granted,wording_version:1,current_wording_version:1,granted_at:'2026-11-12T00:00:00Z',withdrawn_at:null,consent_token:'a'.repeat(64)};
 const client:any={ownerId:7,backendScope:'https://qa.invalid',capabilities:async()=>({state:'confirmed',value:{contract_version:'nutrition-manual/1.0.0',owner_id:7,mode:'MANUAL_DAILY',state:'AVAILABLE',can_read:true,can_write:true,assisted_modes:[]}}),consent:async()=>({state:'confirmed',value:consent}),head:async(k:any)=>({state:'confirmed',value:{contract_version:'nutrition-manual/1.0.0',owner_id:7,key:k,state:'ABSENT',head_token:'a'.repeat(64),entry:null}}),read:async()=>({state:'unknown'}),setConsent:jest.fn()};
 return{client,props:{client,auth:{revision:1} as any,pending:{pending:async()=>[]} as any,current:()=>true,newId:()=> 'nutrition-1',onClose:()=>{},day:'2026-11-12',timezone:'Europe/Paris'}};
}
test('actual native consumer requests separate consent before presenting any acquisition controls',async()=>{
 const x=setup(false);await act(async()=>{root.render(React.createElement(NutritionSurface,x.props));await flush();});
 expect(node('nutrition-consent-grant')).toBeDefined();expect(node('nutrition-edit-kcal_milli')).toBeUndefined();expect(x.client.setConsent).not.toHaveBeenCalled();
});
test('an empty day remains empty and opens a typed editor with disabled blank save',async()=>{
 const x=setup();await act(async()=>{root.render(React.createElement(NutritionSurface,x.props));await flush();});
 expect(node('nutrition-empty')).toBeDefined();
 await act(async()=>{node('nutrition-edit-kcal_milli').onClick({nativeEvent:{},stopPropagation:()=>{},currentTarget:1,target:1});await flush();});
 expect(node('nutrition-value').accessibilityLabel).toContain('kcal');
 expect(node('nutrition-save').accessibilityState.disabled).toBe(true);expect(node('nutrition-target-ratio')).toBeUndefined();
});
test('parent rerender keeps the current draft when the UUID callback identity changes',async()=>{
 const x=setup();await act(async()=>{root.render(React.createElement(NutritionSurface,x.props));await flush();});
 await act(async()=>{node('nutrition-edit-kcal_milli').onClick({nativeEvent:{},stopPropagation:()=>{},currentTarget:1,target:1});await flush();});
 await act(async()=>{node('nutrition-value').onChangeText('1750');await flush();});
 await act(async()=>{root.render(React.createElement(NutritionSurface,{...x.props,newId:()=> 'nutrition-next'}));await flush();});
 expect(node('nutrition-value')).toBeDefined();expect(node('nutrition-value').value).toBe('1750');
});
test('native back closes current target context before leaving the nutrition workspace',async()=>{
 const {BackHandler}=require('react-native');let handler=()=>false;const close=jest.fn();
 const spy=jest.spyOn(BackHandler,'addEventListener').mockImplementation((_name:any,fn:any)=>{handler=fn;return{remove:jest.fn()};});
 try{const x=setup();await act(async()=>{root.render(React.createElement(NutritionSurface,{...x.props,onClose:close}));await flush();});
  await act(async()=>{node('nutrition-targets').onClick({nativeEvent:{},stopPropagation:()=>{},currentTarget:1,target:1});await flush();});
  await act(async()=>{expect(handler()).toBe(true);await flush();});expect(close).not.toHaveBeenCalled();
  expect(root.container.queryAll((n:any)=>n.props.accessibilityLabel==='Date d’effet de la cible, année mois jour')).toHaveLength(0);
 }finally{spy.mockRestore();}
});
