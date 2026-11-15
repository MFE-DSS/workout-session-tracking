import React,{act} from 'react';
import {createRoot,type Root} from 'test-renderer';
import {BodyMeasurementsSurface} from './BodyMeasurementsSurface';
jest.mock('react-native-safe-area-context',()=>({SafeAreaProvider:({children}:any)=>children,SafeAreaView:({children,...props}:any)=>require('react').createElement(require('react-native').View,props,children),useSafeAreaInsets:()=>({top:24,bottom:24,left:0,right:0})}));
let root:Root;beforeEach(()=>{root=createRoot();});afterEach(async()=>{await act(async()=>root.unmount());});
const flush=async()=>{for(let i=0;i<100;i++)await Promise.resolve();};
const node=(id:string)=>root.container.queryAll((n:any)=>n.props.testID===id)[0]?.props;
const consent={granted:true,owner_id:7,consent_version:1,consent_token:'a'.repeat(64)};
function setup(granted=true){const client:any={ownerId:7,consent:async()=>({state:'confirmed',value:{...consent,granted}}),read:async()=>granted?{state:'confirmed',value:{state:'EMPTY',entries:[],window:{from:'2025-11-11',through:'2026-11-11'},field_specs:[{key:'weight_kg',label:'Poids',unit:'kg',min:20,max:400}],next_cursor:null}}:{state:'consent_required'},setConsent:jest.fn()};
 const store:any={pending:async()=>[],prepare:jest.fn()};return {client,store,props:{client,pending:store,auth:{revision:1} as any,current:()=>true,newId:()=> 'body-1',onClose:()=>{}}};}
test('real family requires an explicit agreement and never opens a writer before confirmed field specs',async()=>{
 const f=setup(false);await act(async()=>{root.render(React.createElement(BodyMeasurementsSurface,f.props));await flush();});
 expect(node('body-consent-grant')).toBeDefined();expect(node('body-new')).toBeUndefined();expect(f.client.setConsent).not.toHaveBeenCalled();
});
test('owned readback has an honest empty state and opens the one-field sheet through its actual consumer',async()=>{
 const f=setup();await act(async()=>{root.render(React.createElement(BodyMeasurementsSurface,f.props));await flush();});
 expect(node('body-empty')).toBeDefined();
 await act(async()=>node('body-new').onClick({nativeEvent:{},stopPropagation:()=>{},currentTarget:1,target:1}));
 expect(node('body-value-weight_kg')).toBeDefined();expect(node('body-save').accessibilityState.disabled).toBe(true);expect(f.store.prepare).not.toHaveBeenCalled();
});

test('confirmed external withdrawal must clear cached numeric versions',async()=>{
 const root=createRoot();let granted=true;
 const spec={key:'weight_kg',label:'Poids',unit:'kg',min:20,max:400};
 const entry={root_ref:1,measurement_id:1,revision:1,state:'CURRENT',date_precision:'DAY_UTC_CONVENTION',measured_at:'2026-11-11T00:00:00Z',recorded_at:'2026-11-11T00:00:00Z',head_token:'a'.repeat(64),fields:{weight_kg:{value:72.123,quality:'KNOWN',unit:'kg',provenance:{origin:'USER_DECLARED',acquisition:'MANUAL_ENTRY'}}}};
 const page={state:'AVAILABLE',entries:[entry],field_specs:[spec],next_cursor:null};
 const client={ownerId:7,consent:async()=>({state:'confirmed',value:{granted,owner_id:7,consent_version:1,consent_token:'a'.repeat(64)}}),read:async()=>granted?{state:'confirmed',value:page}:{state:'consent_required'},head:async()=>granted?{state:'confirmed',value:entry}:{state:'consent_required'}};
 const props={client,pending:{pending:async()=>[]},auth:{revision:1},current:()=>true,newId:()=> 'body-1',onClose:()=>{}};
 const find=(id:string)=>root.container.queryAll((n:any)=>n.props.testID===id)[0]?.props;
 const label=(s:string)=>root.container.queryAll((n:any)=>n.props.accessibilityLabel===s&&n.props.onClick)[0]?.props;
 const click=async(p:any)=>act(async()=>{p.onClick({nativeEvent:{},stopPropagation:()=>{},currentTarget:1,target:1});await flush();});
 try{
  await act(async()=>{root.render(React.createElement(BodyMeasurementsSurface,props as any));await flush();});
  await click(find('body-sources'));await click(label('Voir les versions'));
  expect(root.container.queryAll((n:any)=>String(n.props.accessibilityLabel??'').includes('72.123')).length).toBeGreaterThan(0);
  granted=false;await click(label('Actualiser'));
  expect(find('body-consent-grant')).toBeDefined();
  expect(root.container.queryAll((n:any)=>String(n.props.accessibilityLabel??'').includes('72.123')).length).toBe(0);
 }finally{await act(async()=>root.unmount());}
});
test('legacy unlateralisable calf remains inspectable through the owned root index',async()=>{
 const f=setup(),legacy:any={root_ref:17,measurement_id:17,revision:0,state:'CURRENT',measured_at:'2025-11-01T00:00:00Z',recorded_at:'2025-11-01T00:00:00Z',date_precision:'UNKNOWN',fields:{calf_cm:{quality:'KNOWN',value:39,unit:'cm',provenance:{origin:'UNKNOWN',acquisition:'UNKNOWN'}}}};
 f.client.read=async()=>({state:'confirmed',value:{state:'AVAILABLE',entries:[legacy],field_specs:[{key:'weight_kg',label:'Poids',unit:'kg',min:20,max:400}],next_cursor:null}});f.client.head=jest.fn(async()=>({state:'confirmed',value:legacy}));
 await act(async()=>{root.render(React.createElement(BodyMeasurementsSurface,f.props));await flush();});
 await act(async()=>node('body-roots-open').onClick({nativeEvent:{},stopPropagation:()=>{},currentTarget:1,target:1}));await act(async()=>{node('body-entry-17').onClick({nativeEvent:{},stopPropagation:()=>{},currentTarget:1,target:1});await flush();});expect(f.client.head).toHaveBeenCalledWith(17);
});
test('bilateral CREATE can acquire either side first and keeps the other independently unknown',async()=>{
 const f=setup();f.client.read=async()=>({state:'confirmed',value:{state:'EMPTY',entries:[],field_specs:[{key:'arm_cm_left',label:'Bras gauche',unit:'cm',min:10,max:100},{key:'arm_cm_right',label:'Bras droit',unit:'cm',min:10,max:100}],next_cursor:null}});
 await act(async()=>{root.render(React.createElement(BodyMeasurementsSurface,f.props));await flush();});await act(async()=>node('body-field-arm_cm_right').onClick({nativeEvent:{},stopPropagation:()=>{},currentTarget:1,target:1}));await act(async()=>node('body-new').onClick({nativeEvent:{},stopPropagation:()=>{},currentTarget:1,target:1}));expect(node('body-value-arm_cm_right')).toBeDefined();expect(node('body-side-arm_cm_left')).toBeDefined();expect(f.store.prepare).not.toHaveBeenCalled();
});
test('cancel acquisition returns to the same selected instrument instead of remounting a default field',async()=>{
 const f=setup();f.client.read=async()=>({state:'confirmed',value:{state:'EMPTY',entries:[],field_specs:[{key:'arm_cm_left',label:'Bras gauche',unit:'cm',min:10,max:100},{key:'arm_cm_right',label:'Bras droit',unit:'cm',min:10,max:100}],next_cursor:null}});
 const click=async(id:string)=>act(async()=>{node(id).onClick({nativeEvent:{},stopPropagation:()=>{},currentTarget:1,target:1});await flush();});
 await act(async()=>{root.render(React.createElement(BodyMeasurementsSurface,f.props));await flush();});await click('body-field-arm_cm_right');await click('body-new');await click('body-cancel');expect(node('body-field-arm_cm_left')).toBeDefined();expect(node('body-field-arm_cm_right')).toBeUndefined();expect(f.store.prepare).not.toHaveBeenCalled();
});
