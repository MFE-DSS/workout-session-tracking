import React,{act} from 'react';
import {Text} from 'react-native';
import {createRoot,type Root} from 'test-renderer';
import {firstUse,historical,resumed} from '../../../test/missionActionHarness';
import {MissionActionHost,type MissionActionHostProps} from './MissionActionHost';
import {decodeMissionAction} from '../../api/missionAction';
jest.mock('react-native-safe-area-context',()=>({useSafeAreaInsets:()=>({top:47,bottom:34,left:0,right:0})}));
let root:Root;
beforeEach(()=>{root=createRoot();});
afterEach(async()=>{await act(async()=>root.unmount());});
const confirmed=(raw:unknown,path:'FIRST_USE'|'HISTORICAL'='FIRST_USE')=>{
 const value=decodeMissionAction(raw,7,path,true);if(!value)throw Error('invalid test testimony');return{state:'confirmed' as const,value};
};
function props(read:MissionActionHostProps['read']):MissionActionHostProps{return{read,path:'FIRST_USE',local:null,onAction:async()=>{},onVerify:async()=>{},onSelectPath:()=>{},onOpenJournal:()=>{},historical:React.createElement(Text,{testID:"locked-mission-consumer"},"MISSION")};}
const byId=(id:string)=>root.container.queryAll((n:any)=>n.props.testID===id)[0]?.props;
async function press(id:string){const p=byId(id);expect(p).toBeDefined();await act(async()=>p.onClick({nativeEvent:{},stopPropagation:()=>{},currentTarget:1,target:1}));}
test('first-use orientation has one compact action; details and alternate path are subordinate',async()=>{
 const p=props(confirmed(firstUse())),actions:unknown[]=[];p.onAction=async(a)=>{actions.push(a);};
 await act(async()=>root.render(React.createElement(MissionActionHost,p)));
 expect(root.container.queryAll((n:any)=>n.props.testID==='calibration-primary-action')).toHaveLength(1);
 expect(byId('mission-action-detail')).toBeUndefined();await press('mission-action-details');expect(byId('mission-action-detail')).toBeDefined();
 await press('mission-action-primary');expect(actions).toEqual([firstUse()]);
 const paths:string[]=[];p.onSelectPath=(path)=>paths.push(path);await act(async()=>root.render(React.createElement(MissionActionHost,p)));
 await press('mission-action-other');expect(paths).toEqual(['HISTORICAL']);
});
test.each(['START','CLOSE','SOURCE'] as const)('local %s uncertainty overrides even a valid historical start',async(kind)=>{
 const p=props(confirmed(historical(),'HISTORICAL')),actions:unknown[]=[];p.local={kind};p.path='HISTORICAL';p.onAction=async(a)=>{actions.push(a);};let verified=0;p.onVerify=async()=>{verified++;};
 await act(async()=>root.render(React.createElement(MissionActionHost,p)));
 expect(byId('locked-mission-consumer')).toBeUndefined();expect(byId('mission-action-other')).toBeUndefined();
 await press('mission-action-primary');expect(verified).toBe(1);expect(actions).toEqual([]);
});
test.each(['pending','unknown'] as const)('a %s read never exposes its previous start permission',async(state)=>{
 const p=props({state,previous:confirmed(firstUse()).value}),actions:unknown[]=[];p.onAction=async(a)=>{actions.push(a);};
 await act(async()=>root.render(React.createElement(MissionActionHost,p)));
 expect(byId('locked-mission-consumer')).toBeUndefined();
 if(state==='pending')expect(byId('mission-action-primary')?.accessibilityState.disabled).toBe(true);
 else await press('mission-action-primary');expect(actions).toEqual([]);
});
test('confirmed historical MISSION is returned directly without a layout wrapper or extra footer',async()=>{
 const p=props(confirmed(historical(),'HISTORICAL'));p.path='HISTORICAL';
 expect(MissionActionHost(p)).toBe(p.historical);
});
test('closed owned first session has a factual read action, never a second start',async()=>{
 const p=props(confirmed(resumed('first-plan-execution/3.0.0',true))),actions:any[]=[];p.onAction=async(a)=>{actions.push(a);};
 await act(async()=>root.render(React.createElement(MissionActionHost,p)));
 expect(byId('mission-action-primary').accessibilityLabel).toBe('Lire la séance');await press('mission-action-primary');
 expect(actions[0].primary_action).toEqual({kind:'OPEN_FIRST_SESSION_HISTORY',session_id:19});
});
test('unavailable and conflict carry no invented recommendation or new-start callback',async()=>{
 const p=props(confirmed({...firstUse(),state:'CONFLICT',source:'OPEN_SESSION',primary_action:null,payload:null,reason:'MULTIPLE_OPEN_SESSIONS'})),actions:unknown[]=[];p.onAction=async(a)=>{actions.push(a);};
 await act(async()=>root.render(React.createElement(MissionActionHost,p)));await press('mission-action-primary');expect(actions).toEqual([]);
});
test('failed resume keeps the owned session and explains the read still needed',async()=>{
 const p=props(confirmed(resumed('LEGACY_V1')));p.offline=true;
 await act(async()=>root.render(React.createElement(MissionActionHost,p)));
 const content=root.container.queryAll((n:any)=>typeof n.props.children==='string').map((n:any)=>n.props.children).join(' ');
 expect(content).toContain('Reprise à vérifier');expect(content).toContain('connexion');
 expect(byId('mission-action-primary').accessibilityLabel).toBe('Reprendre');
});
test('an in-flight start disables verification and cannot issue another operation',async()=>{
 const p=props(confirmed(historical(),'HISTORICAL'));p.local={kind:'START'};p.checking=true;const verify=jest.fn();p.onVerify=verify;
 await act(async()=>root.render(React.createElement(MissionActionHost,p)));
 expect(byId('mission-action-primary').accessibilityState.disabled).toBe(true);await press('mission-action-primary');expect(verify).not.toHaveBeenCalled();
});
