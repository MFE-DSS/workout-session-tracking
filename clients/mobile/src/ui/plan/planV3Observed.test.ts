import React,{act} from 'react';
import {createRoot} from 'test-renderer';
import {PlanV3ObservedScreen} from './PlanV3ObservedScreen';
jest.mock('react-native-safe-area-context',()=>({useSafeAreaInsets:()=>({top:47,bottom:34,left:0,right:0})}));
test('restart resumes the actual owned observation and accepts only its displayed exact setting',async()=>{
 const root=createRoot(),accept=jest.fn(async()=>true);
 const context={canonical_exercise_id:'exercise',realization_ref:'realization',equipment_ref:'machine-A',context_ref:'room-A',side:'BILATERAL',load_semantics:'PER_IMPLEMENT'};
 const trial={event_id:'actual-trial',kind:'ATTEMPT_OBSERVED',setting:{kind:'MASS_KG',value:13,unit:'kg'},reps:9};
 const episode={episode_ref:'owned-episode',kind:'CONTEXT_OPENED',context,events:[trial]};
 const controller:any={state:{source:{declarations:{observation_progress:[episode]}}},loading:false,notice:null,capabilities:{supported_realizations:[{candidate_id:'exercise',display_name:'Exercice observé',realization_ref:'realization'}]},
 selectObservedEpisode:async(ref:string)=>{controller.state.source.observed_episode_ref=ref;return true;},recordObservedEvent:accept};
 await act(async()=>root.render(React.createElement(PlanV3ObservedScreen,{controller,onBack(){}})));
 const resume=root.container.queryAll(n=>n.props.testID==='plan-v3-resume-observed-owned-episode')[0];
 expect(resume).toBeDefined();
 await act(async()=>resume.props.onClick({nativeEvent:{},stopPropagation(){},currentTarget:1,target:1}));
 const button=root.container.queryAll(n=>n.props.accessibilityLabel==='Accepter ce réglage provisoire exact pour réessai')[0];
 expect(button).toBeDefined();
 expect(root.container.queryAll(n=>n.children.filter(ch=>typeof ch==='string').join('').includes('13 kg par élément')).length).toBeGreaterThan(0);
 await act(async()=>button.props.onClick({nativeEvent:{},stopPropagation(){},currentTarget:1,target:1}));
 expect(accept).toHaveBeenCalledWith({kind:'SETTING_ACCEPTED',reference_event_id:'actual-trial'});
 await act(async()=>root.unmount());
});
test('a cached trial id without readable owned details offers no blind acceptance',async()=>{
 const root=createRoot(),controller:any={state:{source:{observed_episode_ref:'missing',observed_trial_ref:'cached',declarations:{observation_progress:[]}}},loading:false,capabilities:{supported_realizations:[]}};
 await act(async()=>root.render(React.createElement(PlanV3ObservedScreen,{controller,onBack(){}})));
 expect(root.container.queryAll(n=>n.props.accessibilityLabel==='Accepter ce réglage provisoire exact pour réessai')).toHaveLength(0);
 await act(async()=>root.unmount());
});
