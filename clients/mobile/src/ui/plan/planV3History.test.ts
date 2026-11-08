import React,{act} from 'react';
import {createRoot} from 'test-renderer';
import {PlanV3ExecutionScreen} from './PlanV3ExecutionScreen';
jest.mock('react-native-safe-area-context',()=>({useSafeAreaInsets:()=>({top:47,bottom:34,left:0,right:0})}));
test('completed native session exposes actual typed history, synchronization and explicit correction',async()=>{
 const root=createRoot(),fact={setting:{kind:'MASS_KG',value:14,unit:'kg'},context:{load_semantics:'PER_IMPLEMENT',context_ref:'room-A',equipment_ref:'device-A'},reps:9,completed:true,performed_at:'2026-11-08T12:00:00Z',performed_at_estimated:true};
 const c:any={loading:false,notice:null,localOperations:[],capabilities:{supported_realizations:[{candidate_id:'rdl',display_name:'Soulevé de terre roumain'}]},state:{phase:'COMPLETE',source:{},local_facts:{},execution:{session_id:2,status:'completed',exercises:[{canonical_exercise_id:'rdl',se_id:3,prescription:fact,sets:[{set_id:4,set_index:1,revision:2,completed:true,reps:9,completed_at:fact.performed_at,observation:fact}]}]}}};
 await act(async()=>root.render(React.createElement(PlanV3ExecutionScreen,{controller:c,serverNowMs:0,onSync:async()=>{},onExit(){}})));
 const read=root.container.queryAll(n=>n.props.testID==='plan-v3-read-journal')[0];expect(read).toBeDefined();
 await act(async()=>read.props.onClick({nativeEvent:{},stopPropagation(){},currentTarget:1,target:1}));
 expect(root.container.queryAll(n=>n.children.filter(x=>typeof x==='string').join('').includes('14 kg par élément')).length).toBeGreaterThan(0);
 expect(root.container.queryAll(n=>n.children.filter(x=>typeof x==='string').join('').includes('Date estimée')).length).toBeGreaterThan(0);
 expect(root.container.queryAll(n=>n.props.testID==='plan-v3-correct-4')).toHaveLength(1);
 await act(async()=>root.unmount());
});
