import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
import React,{act} from 'react';
import {createRoot} from 'test-renderer';
import {PlanV3FirstUseScreen} from './PlanV3FirstUseScreen';
jest.mock('react-native-safe-area-context',()=>({useSafeAreaInsets:()=>({top:47,bottom:34,left:0,right:0})}));
test('first calibration is available without seven qualified settings; an uncertain start only offers reconciliation',async()=>{
 const root=createRoot();const exit=jest.fn(),read=jest.fn();
 const controller:any={saveCalibrationDraft:async()=>{},calibrationDraft:()=>null,newCalibrationDraftRef:()=>"draft-test",loading:false,notice:null,state:{source:{},intent:null},capabilities:{controlled_test_available:true,initial_calibration_pilot:{display_name:'Extension de jambes assise'}},evaluate:jest.fn()};
 await act(async()=>root.render(React.createElement(PlanV3FirstUseScreen,{controller,onExit:exit,onPreferences:exit})));
 expect(root.container.queryAll(n=>n.props.testID==='plan-v3-first-calibration')).toHaveLength(1);
 controller.state.intent={state:'unknown',request_id:'same'};controller.reconcileStart=read;
 await act(async()=>root.render(React.createElement(PlanV3FirstUseScreen,{controller,onExit:exit,onPreferences:exit})));
 expect(root.container.queryAll(n=>n.props.testID==='plan-v3-start')).toHaveLength(0);
 expect(root.container.queryAll(n=>n.props.testID==='plan-v3-reconcile')).toHaveLength(1);
 await act(async()=>root.unmount());
});
test('opening preparation does not display trial instructions or imply permission to perform a loaded trial',async()=>{
 const root=createRoot();const controller:any={saveCalibrationDraft:async()=>{},calibrationDraft:()=>null,newCalibrationDraftRef:()=>"draft-test",loading:false,notice:null,state:{source:{encounter_ref:'owned'},intent:null},
 capabilities:{controlled_test_available:true,initial_calibration_pilot:{display_name:'Extension de jambes'}},encounter:{result:{state:'CALIBRATION_REQUIRED',phase:'PREPARE'},progress:{ledger_complete:true,observed_attempt_count:0},allowed_actions:['RECORD_TRIAL']},readCalibration:async()=>{}};
 await act(async()=>root.render(React.createElement(PlanV3FirstUseScreen,{controller,onExit(){},onPreferences(){}})));
 const target=root.container.queryAll(n=>n.props.testID==='plan-v3-resume-calibration')[0];
 await act(async()=>target.props.onClick({nativeEvent:{},stopPropagation(){},currentTarget:1,target:1}));
 expect(root.container.queryAll(n=>n.props.accessibilityLabel==='Répétitions réellement faites')).toHaveLength(0);
 await act(async()=>root.unmount());
});
test('an exact-setting acceptance is unavailable when the owned observation details cannot be read',async()=>{
 const root=createRoot();const controller:any={saveCalibrationDraft:async()=>{},calibrationDraft:()=>null,newCalibrationDraftRef:()=>"draft-test",loading:false,notice:null,state:{source:{encounter_ref:'owned'},intent:null},
 capabilities:{controlled_test_available:true,initial_calibration_pilot:{display_name:'Extension de jambes'}},
 encounter:{result:{state:'OBSERVED',phase:'OBSERVE'},progress:{ledger_complete:true,observed_attempt_count:1,observation_refs:['trial'],acceptance_refs:[]},allowed_actions:['ACCEPT_EXACT_SETTING']},readCalibration:async()=>{}};
 await act(async()=>root.render(React.createElement(PlanV3FirstUseScreen,{controller,onExit(){},onPreferences(){}})));
 const target=root.container.queryAll(n=>n.props.testID==='plan-v3-resume-calibration')[0];
 await act(async()=>target.props.onClick({nativeEvent:{},stopPropagation(){},currentTarget:1,target:1}));
 expect(root.container.queryAll(n=>n.props.accessibilityLabel==='Accepter ce réglage provisoire exact')).toHaveLength(0);
 await act(async()=>root.unmount());
});
test('a rejected stale revision still offers an explicit owned re-read without a pending mutation',async()=>{
 const root=createRoot(),load=jest.fn(async()=>{}),controller:any={saveCalibrationDraft:async()=>{},calibrationDraft:()=>null,newCalibrationDraftRef:()=>"draft-test",loading:false,notice:'source_revision_changed',state:{source:{}},capabilities:{controlled_test_available:true},load};
 await act(async()=>root.render(React.createElement(PlanV3FirstUseScreen,{controller,onExit(){},onPreferences(){}})));
 const read=root.container.queryAll(n=>n.props.testID==='plan-v3-read-sources')[0];expect(read).toBeDefined();
 await act(async()=>read.props.onClick({nativeEvent:{},stopPropagation(){},currentTarget:1,target:1}));expect(load).toHaveBeenCalledTimes(1);
 await act(async()=>root.unmount());
});
test('setup-only discovery stays reachable before selecting a numeric load',async()=>{
 const root=createRoot(),controller:any={saveCalibrationDraft:async()=>{},calibrationDraft:()=>null,newCalibrationDraftRef:()=>"draft-test",loading:false,notice:null,state:{source:{encounter_ref:'owned'},intent:null},
 capabilities:{controlled_test_available:true,initial_calibration_pilot:{display_name:'Extension'}},
 encounter:{result:{state:'SUPPORTED_INITIAL_EXPLORATION',phase:'FAMILIARIZE'},progress:{ledger_complete:true,observed_attempt_count:0,preparation:{instruction_ref:'manual',setup_ref:'seat'}},allowed_actions:['INITIATE_FAMILIARIZATION']},readCalibration:async()=>{}};
 await act(async()=>root.render(React.createElement(PlanV3FirstUseScreen,{controller,onExit(){},onPreferences(){}})));
 await act(async()=>root.container.queryAll(n=>n.props.testID==='plan-v3-resume-calibration')[0].props.onClick({nativeEvent:{},stopPropagation(){},currentTarget:1,target:1}));
 expect(root.container.queryAll(n=>n.props.testID==='plan-v3-setup-discovery')).toHaveLength(1);
 expect(root.container.queryAll(n=>n.props.testID==='plan-v3-loaded-trial')).toHaveLength(0);
 await act(async()=>root.unmount());
});

test('proposal exposes only the first admissible session, never a promise of the subsequent one',async()=>{
 const rows=JSON.parse(readFileSync(resolve(__dirname,'../../../../../docs/science/sci-p02-initial-policy/stage2-v3/producer-fixtures.v3.json'),'utf8'));
 const recommendation=rows.find((row:any)=>row.response.scientific_readiness==='SCIENTIFICALLY_READY').response;
 expect(recommendation.candidate_plan.sessions).toHaveLength(2);
 const root=createRoot(),controller:any={saveCalibrationDraft:async()=>{},calibrationDraft:()=>null,newCalibrationDraftRef:()=>"draft-test",loading:false,state:{source:{evaluation:{recommendation}}},capabilities:{controlled_test_available:true},evaluate:async()=>{}};
 await act(async()=>root.render(React.createElement(PlanV3FirstUseScreen,{controller,onExit(){},onPreferences(){}})));
 await act(async()=>root.container.queryAll(n=>n.props.testID==='plan-v3-open-proposal')[0].props.onClick({nativeEvent:{},stopPropagation(){},currentTarget:1,target:1}));
 expect(root.container.queryAll(n=>typeof n.props.testID==='string'&&n.props.testID.startsWith('plan-v3-slot-'))).toHaveLength(7);
 await act(async()=>root.unmount());
});

test('withdrawal removes familiarization instructions immediately without hiding past facts',async()=>{
 const root=createRoot(),controller:any={saveCalibrationDraft:async()=>{},calibrationDraft:()=>null,newCalibrationDraftRef:()=>"draft-test",loading:false,state:{source:{encounter_ref:'owned'}},capabilities:{controlled_test_available:true},readCalibration:async()=>{},
 encounter:{encounter_ref:'owned',result:{state:'SUPPORTED_INITIAL_EXPLORATION',phase:'FAMILIARIZE'},allowed_actions:['CONFIRM_FAMILIARIZATION'],progress:{preparation:{instruction_ref:'manual',setup_ref:'setup'},setting_choice:{setting:{kind:'MASS_KG',unit:'kg',value:17}},observed_attempt_count:0}}};
 await act(async()=>root.render(React.createElement(PlanV3FirstUseScreen,{controller,onExit(){},onPreferences(){}})));
 await act(async()=>root.container.queryAll(n=>n.props.testID==='plan-v3-resume-calibration')[0].props.onClick({nativeEvent:{},stopPropagation(){},currentTarget:1,target:1}));
 controller.encounter={...controller.encounter,result:{state:'WITHDRAWN',phase:'DECIDE'},allowed_actions:['RECORD_TRIAL']};
 await act(async()=>root.render(React.createElement(PlanV3FirstUseScreen,{controller,onExit(){},onPreferences(){}})));
 expect(root.container.queryAll(n=>typeof n.props.children==='string'&&n.props.children.includes('familiarise-toi réellement'))).toHaveLength(0);
 await act(async()=>root.unmount());
});

test.each([['MACHINE_DISPLAY_KG',17,'kg affichés'],['PER_IMPLEMENT',8.5,'kg par haltère']])('exact acceptance displays the observed %s value, not an unseen local choice',async(semantics,value,unit)=>{
 const root=createRoot(),controller:any={saveCalibrationDraft:async()=>{},calibrationDraft:()=>null,newCalibrationDraftRef:()=>"draft-test",loading:false,state:{source:{encounter_ref:'owned'}},capabilities:{controlled_test_available:true},readCalibration:async()=>{},
 encounter:{encounter_ref:'owned',result:{state:'OBSERVED',phase:'OBSERVE'},allowed_actions:['ACCEPT_EXACT_SETTING'],progress:{preparation:{},setting_choice:{setting:{kind:'MASS_KG',unit:'kg',value},available:true},observed_attempt_count:1,context:{canonical_exercise_id:'exercise',load_semantics:semantics,equipment_ref:'actual-device',context_ref:'actual-room'},observation_refs:['trial'],observations:[{event_id:'trial',setting:{kind:'MASS_KG',unit:'kg',value},reps:10}]}}};
 await act(async()=>root.render(React.createElement(PlanV3FirstUseScreen,{controller,onExit(){},onPreferences(){}})));
 await act(async()=>root.container.queryAll(n=>n.props.testID==='plan-v3-resume-calibration')[0].props.onClick({nativeEvent:{},stopPropagation(){},currentTarget:1,target:1}));
 const readout=root.container.queryAll(n=>n.props.testID==='calibration-setting-value');expect(readout).toHaveLength(1);
 expect(readout[0].props.children[0]).toBe(String(value));
 expect(root.container.queryAll(n=>n.props.children===unit)).toHaveLength(1);
 await act(async()=>root.unmount());
});

test('an actual attempt requires an actual setting; a selected value is never silently copied into the fact',async()=>{
 const root=createRoot(),reported:any[]=[],draft:any={encounter_ref:'owned',draft_ref:'fact',stage:'observation',load:'17',observedLoad:'',reps:'10',completed:true,successful:true,quality:'ACCEPTABLE',discomfort:'NO_CONCERN',stopReason:'COMPLETED',trialAt:'2026-11-09T10:00:00Z',trialDate:'',trialTime:'',instruction:'manual',setup:'setup'};
 const controller:any={saveCalibrationDraft:async()=>{},calibrationDraft:()=>draft,newCalibrationDraftRef:()=>"fact",loading:false,state:{source:{encounter_ref:'owned',calibration_draft:draft}},capabilities:{controlled_test_available:true},readCalibration:async()=>{},recordCalibration:async(o:any)=>{reported.push(o);return true;},
 encounter:{encounter_ref:'owned',result:{state:'SUPPORTED_INITIAL_EXPLORATION',phase:'TRIAL'},allowed_actions:['RECORD_TRIAL'],progress:{preparation:{},setting_choice:{setting:{kind:'MASS_KG',unit:'kg',value:17}},observed_attempt_count:0,context:{load_semantics:'MACHINE_DISPLAY_KG'}}}};
 await act(async()=>root.render(React.createElement(PlanV3FirstUseScreen,{controller,onExit(){},onPreferences(){}})));
 await act(async()=>root.container.queryAll(n=>n.props.testID==='plan-v3-resume-calibration')[0].props.onClick({nativeEvent:{},stopPropagation(){},currentTarget:1,target:1}));
 expect(root.container.queryAll(n=>n.props.accessibilityLabel==='Enregistrer ces faits')).toHaveLength(0);
 const input=root.container.queryAll(n=>n.props.testID==='calibration-setting-input')[0];expect(input).toBeDefined();expect(input.props.accessibilityLabel).toBe('Réglage réellement utilisé · kg affichés');
 await act(async()=>input.props.onChangeText('18'));
 await act(async()=>root.container.queryAll(n=>n.props.accessibilityLabel==='Enregistrer ces faits')[0].props.onClick({nativeEvent:{},stopPropagation(){},currentTarget:1,target:1}));
 expect(reported[0].event.setting.value).toBe(18);
 await act(async()=>root.unmount());
});
