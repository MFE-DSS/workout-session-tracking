import React,{act} from 'react';
import {BackHandler,AppState} from 'react-native';
import {createRoot,type Root} from 'test-renderer';
import {accountHarness,reply,weightPage,deferred} from '../../../test/accountDataHarness';
import {historyPage,legacyFacts} from '../../../test/trainingHistoryHarness';
import {TrainingHistoryHost} from './TrainingHistoryHost';
jest.mock('react-native-safe-area-context',()=>({useSafeAreaInsets:()=>({top:47,bottom:34,left:0,right:0})}));
let root:Root;beforeEach(()=>{root=createRoot();});afterEach(async()=>{await act(async()=>root.unmount());jest.restoreAllMocks();});
const flush=async()=>{for(let i=0;i<60;i++)await Promise.resolve();};
const node=(id:string)=>root.container.queryAll((n:any)=>n.props.testID===id)[0]?.props;
async function setup(){const s=await accountHarness();s.handle(async p=>{
 if(p.startsWith('/me/training-history/sessions/'))return reply(legacyFacts());
 if(p.startsWith('/me/training-history?')){const v=historyPage();v.window.period=new URL('https://qa.invalid'+p).searchParams.get('period') as any;return reply(v);}
 if(p.startsWith('/me/body/weight-history')){const v=weightPage();v.entries[0].measured_at='2026-11-05T00:00:00Z';return reply(v);}
 return reply(null,404);
});return s;}
test('focused history consumer reads owned sessions then the existing dated weight source without writers',async()=>{
 const s=await setup();await act(async()=>{root.render(React.createElement(TrainingHistoryHost,{auth:s.auth,call:s.call,timeZone:'UTC'}));await flush();});
 expect(node('progress-frequency').children).toBe('1');expect(node('progress-weight-chart')).toBeDefined();
 expect(s.calls.some(c=>c.path.startsWith('/me/body/weight-history'))).toBe(true);
 expect(s.calls.filter(c=>!c.path.startsWith('/auth/')).every(c=>c.body===null)).toBe(true);
 await act(async()=>{await node('progress-session-11').onClick({nativeEvent:{},stopPropagation:()=>{},currentTarget:1,target:1});await flush();});expect(node('history-set-31')).toBeDefined();
});
test('changing period hides old weight while the new read is pending',async()=>{
 const s=await setup();await act(async()=>{root.render(React.createElement(TrainingHistoryHost,{auth:s.auth,call:s.call,timeZone:'UTC'}));await flush();});
 const late=deferred<Response>();s.handle(async()=>late.promise);
 const radio=root.container.queryAll((n:any)=>n.props.accessibilityRole==='radio'&&n.props.accessibilityLabel==='12 sem.')[0];
 await act(async()=>{radio.props.onClick({nativeEvent:{},stopPropagation:()=>{},currentTarget:1,target:1});await flush();});expect(node('progress-weight-chart')).toBeUndefined();
 await act(async()=>{late.resolve(reply({...historyPage(),window:{...historyPage().window,period:'12w'}}));await flush();});
});
test('unmount and account change prevent late history from requesting the old owners weight',async()=>{
 const s=await setup(),late=deferred<Response>();s.handle(async()=>late.promise);
 await act(async()=>{root.render(React.createElement(TrainingHistoryHost,{auth:s.auth,call:s.call,timeZone:'UTC'}));await flush();});
 await act(async()=>root.unmount());await s.auth.logout();s.setOwner(8);await s.auth.login('fixture','fixture-only',null);
 await act(async()=>{late.resolve(reply(historyPage()));await flush();});
 expect(s.calls.some(c=>c.path.startsWith('/me/body/weight-history'))).toBe(false);
});
test('native back consumes detail only, and foreground refresh rechecks current owned facts',async()=>{
 const s=await setup();let back:()=>boolean=()=>false,foreground:(state:string)=>void=()=>{};
 jest.spyOn(BackHandler,'addEventListener').mockImplementation((_event,handler)=>{back=()=>handler(undefined as never)===true;return{remove:jest.fn()};});
 jest.spyOn(AppState,'addEventListener').mockImplementation((_event,handler)=>{foreground=handler as any;return{remove:jest.fn()};});
 await act(async()=>{root.render(React.createElement(TrainingHistoryHost,{auth:s.auth,call:s.call,timeZone:'UTC'}));await flush();});
 expect(back()).toBe(false);
 await act(async()=>{await node('progress-session-11').onClick({nativeEvent:{},stopPropagation:()=>{},currentTarget:1,target:1});await flush();});
 expect(node('history-set-31')).toBeDefined();await act(async()=>{expect(back()).toBe(true);});expect(node('progress-frequency')).toBeDefined();
 const count=s.calls.filter(c=>c.path.startsWith('/me/training-history?')).length;
 await act(async()=>{foreground('active');await flush();});expect(s.calls.filter(c=>c.path.startsWith('/me/training-history?'))).toHaveLength(count+1);
});
