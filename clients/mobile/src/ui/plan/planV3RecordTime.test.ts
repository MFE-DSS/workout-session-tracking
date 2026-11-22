import React,{act} from 'react';
import {createRoot} from 'test-renderer';
import {PlanV3ExecutionScreen} from './PlanV3ExecutionScreen';
jest.mock('react-native-safe-area-context',()=>({useSafeAreaInsets:()=>({top:47,bottom:34,left:0,right:0})}));
const event={nativeEvent:{},stopPropagation(){},currentTarget:1,target:1};
test.each([false,true])('TIME01 actual acquisition uses action-time provenance rather than old render time (estimated=%s)',async(estimated)=>{
 const expected=Date.parse('2026-11-22T12:00:15Z');
 const c:any={loading:false,notice:null,eventTime:()=>({epochMs:expected,estimated}),recordFact:jest.fn(async()=>{}),refreshExecution:async()=>{},localOperations:[],
  state:{phase:'ACTIVE',local_facts:{},source:{},execution:{session_id:5,status:'in_progress',applicability:{state:'CURRENT'},observation_only:false,allowed_actions:['NEXT_WORK_SET'],
   exercises:[{se_id:3,canonical_exercise_id:'leg',prescription:{context:{load_semantics:'MACHINE_DISPLAY_KG'},setting:{value:17.5},dose:{min_reps:8,max_reps:12,rir_target:2}},sets:[{set_id:13,set_index:1,completed:false}]}]}}};
 const root=createRoot();
 const label=(text:string)=>root.container.queryAll(n=>n.props.accessibilityLabel===text)[0];
 const press=async(node:any)=>act(async()=>node.props.onClick(event));
 const input=async(text:string,value:string)=>act(async()=>label(text).props.onChangeText(value));
 await act(async()=>root.render(React.createElement(PlanV3ExecutionScreen,{controller:c,serverNowMs:Date.parse('2026-11-22T12:00:00Z'),onSync:async()=>{},onExit(){}})));
 await press(label('Appareil — kg'));await input('Réglage fait · kg affichés par l’appareil','17.5');await press(label('Garder cette saisie'));
 await press(label('Reps —'));await input('Reps faites','9');await press(label('Garder cette saisie'));
 const record=root.container.queryAll(n=>n.props.testID==='plan-v3-record-set')[0];expect(record).toBeDefined();await press(record);
 expect(c.recordFact).toHaveBeenCalledWith(13,17.5,9,new Date(expected).toISOString(),estimated);
 await act(async()=>root.unmount());
});
