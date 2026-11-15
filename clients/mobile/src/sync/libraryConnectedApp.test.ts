/** Full ConnectedApp + real BODY clients/resources + file SQLite. Only OS/RPC boundaries are synthetic. */
import React,{act} from 'react';
import {createRoot,type Root} from 'test-renderer';
import {DatabaseSync} from 'node:sqlite';
import {createHash} from 'node:crypto';
import {mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import witness from '../../test/libraryWitness.json';
import {firstUse,negotiatedReply} from '../../test/missionActionHarness';
import {historyPage} from '../../test/trainingHistoryHarness';

const mockConnections=new Map<string,DatabaseSync>();let mockDir:string,mockCredential:string|null='rt1.body-device.secret';
let mockOperation=0;
jest.mock('expo-sqlite',()=>({openDatabaseAsync:async(name:string)=>{
 if(!mockConnections.has(name))mockConnections.set(name,new(require('node:sqlite').DatabaseSync)(require('node:path').join(mockDir,name)));
 const db=mockConnections.get(name)!;const h:any={execAsync:async(s:string)=>db.exec(s),runAsync:async(s:string,...a:any[])=>db.prepare(s).run(...(Array.isArray(a[0])?a[0]:a)),getFirstAsync:async(s:string,...a:any[])=>db.prepare(s).get(...(Array.isArray(a[0])?a[0]:a))??null,getAllAsync:async(s:string,...a:any[])=>db.prepare(s).all(...(Array.isArray(a[0])?a[0]:a)),withExclusiveTransactionAsync:async(f:any)=>{db.exec('BEGIN IMMEDIATE');try{await f(h);db.exec('COMMIT');}catch(e){db.exec('ROLLBACK');throw e;}}};return h;
}}));
jest.mock('expo-crypto',()=>({randomUUID:()=>`d477ea9f-7bd9-4fc4-a679-${String(++mockOperation).padStart(12,'0')}`,CryptoDigestAlgorithm:{SHA256:'SHA256'},digestStringAsync:async(_algorithm:string,s:string)=>require('node:crypto').createHash('sha256').update(s).digest('hex')}));
jest.mock('../auth/credentialStore',()=>({credentialStore:{read:async()=>mockCredential,write:async(v:string)=>{mockCredential=v;},clear:async()=>{mockCredential=null;}}}));
jest.mock('../storage/ownershipStore',()=>({openOwnershipBook:async()=>jest.requireActual('../storage/ownershipStore').createOwnershipBook(await require('expo-sqlite').openDatabaseAsync('auren-owners-v1.db'))}));
jest.mock('../storage/legacyInspection',()=>({inspectLegacyJournal:async()=>({snapshot:null,sets:[],outbox:[]})}));
jest.mock('../native/restNotification',()=>({restNotification:{onDelivery:()=>()=>{},cancel:async()=>{},prepare:async()=>false,schedule:async()=>null}}));
jest.mock('../native/keepAwake',()=>({keepAwake:{enable:()=>{},disable:()=>{}}}));
jest.mock('../native/motion',()=>({useReducedMotion:()=>true,announce:()=>{}}));
jest.mock('../native/feedback',()=>({feedback:new Proxy({},{get:()=>()=>{}})}));
jest.mock('../shell/routeContext',()=>({shellRoutes:{}}));
jest.mock('react-native-safe-area-context',()=>({useSafeAreaInsets:()=>({top:47,bottom:34,left:0,right:0}),useSafeAreaFrame:()=>({width:390,height:844}),SafeAreaProvider:({children}:any)=>children}));
jest.mock('expo-router',()=>({useFocusEffect:(fn:any)=>require('react').useEffect(()=>mockActiveTab==='programmes'?fn():undefined,[fn,mockActiveTab]),useRouter:()=>({replace:()=>mockTab('today')}),ExpoRoot:({linking={}}:any)=>{
 const React=require('react');
 // SDK58 ExpoRoot defaults linking to a new object; useRouterConfig memoizes
 // its qualified root by that identity. Reproduce the native remount boundary.
 const RouterTree=React.useMemo(()=>function RouterTree(){
 const React=require('react'),{Pressable,Text,View}=require('react-native'),shell=require('../shell/ShellContext').useShell();
 const [tab,setTab]=React.useState('programmes');mockTab=setTab;mockActiveTab=tab;
 const Programs=require('../routes/programmes').default;
 return React.createElement(View,null,...['programmes','today','progres'].map(t=>React.createElement(Pressable,{key:t,testID:`library-tab-${t}`,onPress:()=>setTab(t)},React.createElement(Text,null,t))),React.createElement(View,{testID:'library-active-'+tab},React.createElement(Programs)),tab==='today'?shell.today:tab==='progres'?shell.progress:null);
 },[linking]);return React.createElement(RouterTree);
}}));
let mockTab:(t:string)=>void=()=>{};let mockActiveTab='programmes';
const originalTarget=process.env.EXPO_PUBLIC_API_URL;
let App:React.ComponentType,root:Root,owner=1,open=false,loseNext=false,offline=false,unavailableOpen=false;
const requests:{method:string;path:string;body:any}[]=[];
const reply=(v:unknown,status=200,library=false)=>({ok:status<400,status,json:async()=>JSON.parse(JSON.stringify(v)),headers:{get:(key:string)=>library&&key==='X-Auren-Library-Contract'?'owned-library/1.0.0':null}}) as unknown as Response;
async function rpc(input:any,init?:RequestInit):Promise<Response>{
 const u=new URL(String(input)),path=u.pathname.replace('/api/mobile/v1',''),method=init?.method??'GET',body=init?.body?JSON.parse(String(init.body)):null;requests.push({method,path,body});
 if(offline)throw Error('controlled offline');
 if(path==='/auth/me')return reply({id:owner,username:'library-synthetic'});
 if(path==='/auth/refresh'||path==='/auth/login')return reply({access_token:'test-library-access',refresh_token:'rt1.body-device.secret',access_expires_in:900,server_now:new Date().toISOString()});
 if(path==='/auth/logout')return reply({});
 if(path==='/mission-action'){
  if(!open){const host=new Headers(init?.headers).has('X-Auren-Mission-V3-Host'),f=firstUse(owner);return negotiatedReply(host&&!unavailableOpen?f:{...f,state:'UNAVAILABLE',source:unavailableOpen?'OPEN_SESSION':'OWNED_FIRST_USE',primary_action:null,payload:null,reason:'EXECUTION_PROFILE_REQUIRED'},200,host);}
  const r=require('../../test/missionActionHarness').resumed();r.owner_id=owner;r.primary_action.session_id=witness.created.execution.session_id;r.payload.session.id=witness.created.execution.session_id;return negotiatedReply(r,200,new Headers(init?.headers).has('X-Auren-Mission-V3-Host'));
 }
 if(path==='/me/library')return reply(witness.page,200,true);
 if(path.startsWith('/me/library/items/'))return reply(witness.detail,200,true);
 if(path==='/me/library/start'){
  open=true;if(loseNext){loseNext=false;throw Error('controlled loss after server creation');}return reply(witness.created,201,true);
 }
 if(path===`/sessions/${witness.created.execution.session_id}/execution`)return reply(witness.created.execution);
 if(path.startsWith('/me/training-history')){const p=historyPage();p.owner_id=owner;p.window={...p.window,until:new Date().toISOString(),time_zone:u.searchParams.get('time_zone')??'UTC'};return reply(p);}
 return reply({detail:{error:'not_served_in_test'}},404);
}
beforeAll(()=>{process.env.EXPO_PUBLIC_API_URL='https://library-synthetic.invalid';jest.spyOn(global,'fetch').mockImplementation((input,init)=>rpc(input,init));App=require('../../ConnectedApp').default;});
beforeEach(()=>{mockDir=mkdtempSync(join(tmpdir(),'auren-library-connected-'));mockCredential='rt1.body-device.secret';mockOperation=0;owner=1;open=false;loseNext=false;offline=false;unavailableOpen=false;requests.length=0;root=createRoot();});
afterEach(async()=>{await act(async()=>root.unmount());for(const db of mockConnections.values())db.close();mockConnections.clear();rmSync(mockDir,{recursive:true,force:true});});
afterAll(()=>{jest.restoreAllMocks();if(originalTarget===undefined)delete process.env.EXPO_PUBLIC_API_URL;else process.env.EXPO_PUBLIC_API_URL=originalTarget;});
const flush=async()=>{for(let i=0;i<700;i++)await Promise.resolve();};
const node=(id:string)=>root.container.queryAll((n:any)=>n.props.testID===id)[0]?.props;
async function press(id:string){expect(node(id)).toBeDefined();await act(async()=>{node(id).onClick({nativeEvent:{},stopPropagation:()=>{},currentTarget:1,target:1});await flush();});}
async function mount(){await act(async()=>{root.render(React.createElement(App));await flush();});}
async function choose(){await press('library-entry-'+witness.created.source_ref);await press('library-ask-start');await press('library-confirm-start');}
function intent(){return [...mockConnections.values()].flatMap(db=>{try{return db.prepare('SELECT * FROM library_pending_openings_v1').all();}catch{return[];}}) as any[];}
function snapshots(){return [...mockConnections.values()].flatMap(db=>{try{return db.prepare('SELECT snapshot FROM active_session').all().map((r:any)=>JSON.parse(r.snapshot));}catch{return[];}});}
async function relaunch(){await act(async()=>{root.unmount();await flush();});for(const db of mockConnections.values())db.close();mockConnections.clear();root=createRoot();await mount();}
test('actual ConnectedApp Programmes creates once, adopts to the owned journal, returns to Today with the same identity and restores it after relaunch',async()=>{
 await mount();await choose();expect(requests.filter(r=>r.method==='POST'&&r.path==='/me/library/start')).toHaveLength(1);
 expect(intent()[0]).toMatchObject({state:'RESOLVED',resolution_kind:'CREATED_CONFIRMED',session_id:witness.created.execution.session_id});
 expect(snapshots()).toContainEqual(expect.objectContaining({plan:expect.objectContaining({session_id:witness.created.execution.session_id})}));
 expect(node('library-active-today')).toBeDefined();expect(node('library-entry-'+witness.created.source_ref)).toBeUndefined();
 await press('mission-action-primary');expect(node('library-tab-today')).toBeUndefined();
 expect(snapshots()).toContainEqual(expect.objectContaining({plan:expect.objectContaining({session_id:witness.created.execution.session_id})}));
 await relaunch();expect(snapshots()).toContainEqual(expect.objectContaining({plan:expect.objectContaining({session_id:witness.created.execution.session_id})}));
 expect(requests.filter(r=>r.method==='POST'&&r.path==='/me/library/start')).toHaveLength(1);
});
test('lost response survives app and SQLite restart, blocks Today fresh actions and verifies/resumes the owned session without replay',async()=>{
 await mount();loseNext=true;await choose();expect(intent()[0].state).toBe('SENT_UNKNOWN');
 await press('library-tab-today');expect(node('library-pending-today')).toBeDefined();await press('library-tab-programmes');
 await relaunch();expect(intent()[0].state).toBe('SENT_UNKNOWN');await press('library-verify');await press('library-resume-found');
 expect(intent()[0]).toMatchObject({state:'RESOLVED',resolution_kind:'RESUMED_OWNED',creation_outcome:'UNKNOWN',session_id:witness.created.execution.session_id});
 expect(snapshots()).toContainEqual(expect.objectContaining({plan:expect.objectContaining({session_id:witness.created.execution.session_id})}));
 expect(requests.filter(r=>r.method==='POST'&&r.path==='/me/library/start')).toHaveLength(1);
});
test('A/B/A relaunch keeps the unknown opening in its owner partition and never replays it',async()=>{
 await mount();loseNext=true;await choose();expect(intent()[0].owner_id).toBe(1);
 owner=2;await relaunch();expect(intent()).toEqual([]);expect(node('library-entry-'+witness.created.source_ref)).toBeUndefined();
 owner=1;await relaunch();expect(intent()[0]).toMatchObject({owner_id:1,state:'SENT_UNKNOWN'});
 expect(requests.filter(r=>r.method==='POST'&&r.path==='/me/library/start')).toHaveLength(1);
});
test('offline verification remains unknown and explicit reconnect recovers without a second start',async()=>{
 await mount();loseNext=true;await choose();offline=true;await press('library-verify');
 expect(intent()[0].state).toBe('SENT_UNKNOWN');expect(node('library-resume-found')).toBeUndefined();
 offline=false;await press('library-verify');expect(node('library-resume-found')).toBeDefined();
 await press('library-resume-found');expect(intent()[0].resolution_kind).toBe('RESUMED_OWNED');
 expect(requests.filter(r=>r.method==='POST'&&r.path==='/me/library/start')).toHaveLength(1);
});


test('unavailable open-session execution is not reinterpreted as absence or permission for a new start',async()=>{
 unavailableOpen=true;await mount();await press('library-entry-'+witness.created.source_ref);
 expect(node('library-ask-start')?.accessibilityState.disabled).toBe(true);
 expect(requests.filter(r=>r.method==='POST'&&r.path==='/me/library/start')).toHaveLength(0);
});
