/** Actual ConnectedApp builder + owner journal/client/recovery; OS and HTTP server boundary synthetic. */
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
let builderRows:any[]=[],builderReceipts=new Map<string,any>(),loseBuilder=false;
const builderDigest='a'.repeat(64);
const builderReply=(v:unknown,status=200)=>({ok:status<400,status,text:async()=>JSON.stringify(v),headers:new Headers({'X-Auren-Program-Builder':'program-builder/1.0.0','Cache-Control':'no-store','Content-Type':'application/json'})}) as Response;
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
 if(path.startsWith('/me/program-builder/')){
  const envelope=(v:any)=>({contract_version:'program-builder/1.0.0',owner_id:owner,...v});
  if(path==='/me/program-builder/commands'){
   const receipt=builderReceipts.get(body.command_id)??{contract_version:'program-builder/1.0.0',owner_id:owner,command_id:body.command_id,request_sha256:createHash('sha256').update(String(init!.body)).digest('hex'),operation:body.operation,program_id:owner+300,resulting_source_digest:builderDigest,resulting_version:1,publication_ids:[],selections:[],recorded_at:'2026-11-15T12:30:00Z'};
   builderReceipts.set(body.command_id,receipt);
   if(!builderRows.some(r=>r.id===owner+300))builderRows.push({id:owner+300,title:body.payload.title,slug_base:'programme',status:'draft',version:1,source_digest:builderDigest,publication_ids:[],sessions:[]});
   if(loseBuilder){loseBuilder=false;throw Error('response lost after commit');}
   return builderReply(receipt,201);
  }
  if(path.startsWith('/me/program-builder/operations/'))return builderReply(builderReceipts.get(path.split('/').pop()!)??{detail:{error:'unknown_operation'}},builderReceipts.has(path.split('/').pop()!)?200:404);
  if(path.startsWith('/me/program-builder/programs/'))return builderReply(envelope({program:builderRows.find(r=>r.id===owner+300)}));
  if(path==='/me/program-builder/programs')return builderReply(envelope({items:builderRows.filter(r=>r.id===owner+300).map(({sessions,slug_base,publication_ids,...r})=>r),next_cursor:null}));
  if(path==='/me/program-builder/exercises')return builderReply(envelope({items:[],next_cursor:null}));
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
beforeEach(()=>{mockDir=mkdtempSync(join(tmpdir(),'auren-library-connected-'));mockCredential='rt1.body-device.secret';mockOperation=0;builderRows=[];builderReceipts.clear();loseBuilder=false;owner=1;open=false;loseNext=false;offline=false;unavailableOpen=false;requests.length=0;root=createRoot();});
afterEach(async()=>{await act(async()=>root.unmount());for(const db of mockConnections.values())db.close();mockConnections.clear();rmSync(mockDir,{recursive:true,force:true});});
afterAll(()=>{jest.restoreAllMocks();if(originalTarget===undefined)delete process.env.EXPO_PUBLIC_API_URL;else process.env.EXPO_PUBLIC_API_URL=originalTarget;});
const flush=async()=>{for(let i=0;i<700;i++)await Promise.resolve();};
const node=(id:string)=>root.container.queryAll((n:any)=>n.props.testID===id)[0]?.props;
async function press(id:string){expect(node(id)).toBeDefined();await act(async()=>{node(id).onClick({nativeEvent:{},stopPropagation:()=>{},currentTarget:1,target:1});await flush();});}
async function mount(){await act(async()=>{root.render(React.createElement(App));await flush();});}
async function relaunch(){await act(async()=>{root.unmount();await flush();});for(const db of mockConnections.values())db.close();mockConnections.clear();root=createRoot();await mount();}
function builderIntent(){return [...mockConnections.values()].flatMap(db=>{try{return db.prepare('SELECT * FROM program_builder_pending_commands_v1').all();}catch{return[];}}) as any[];}
async function createBuilder(){await press('library-builder');await press('builder-create');await act(async()=>{node('builder-title').onChangeText('Programme personnel');await flush();});await press('builder-create-confirm');}
test('ConnectedApp attaches the real durable builder partition before any network mutation',async()=>{
 await mount();expect([...mockConnections.values()].filter(db=>db.prepare("SELECT name FROM sqlite_master WHERE name='program_builder_pending_commands_v1'").get())).toHaveLength(1);
 expect(requests.filter(r=>r.method==='POST'&&r.path==='/me/program-builder/commands')).toHaveLength(0);
});
test('actual builder creation is acknowledged into the owned SQLite journal and read back from fresh source',async()=>{
 await mount();await createBuilder();expect(builderIntent()[0]).toMatchObject({owner_id:1,backend_scope:'https://library-synthetic.invalid',state:'ACKED'});
 expect(node('builder-add-session')).toBeDefined();
 expect(requests.filter(r=>r.method==='POST'&&r.path==='/me/program-builder/commands')).toHaveLength(1);
 await relaunch();await press('library-builder');await press('builder-program-301');expect(node('builder-add-session')).toBeDefined();
 expect(requests.filter(r=>r.method==='POST'&&r.path==='/me/program-builder/commands')).toHaveLength(1);
});
test('lost creation response survives SQLite relaunch and A/B/A, then exact GET receipt reconciles without POST replay',async()=>{
 await mount();loseBuilder=true;await createBuilder();const key=builderIntent()[0].command_id;expect(builderIntent()[0].state).toBe('SENT_UNKNOWN');
 owner=2;await relaunch();await press('library-builder');expect(builderIntent()).toEqual([]);expect(node('builder-verify-'+key)).toBeUndefined();
 owner=1;await relaunch();await press('library-builder');expect(builderIntent()[0].state).toBe('SENT_UNKNOWN');
 offline=true;await press('builder-verify-'+key);expect(builderIntent()[0].state).toBe('SENT_UNKNOWN');offline=false;
 await press('builder-verify-'+key);expect(builderIntent()[0].state).toBe('ACKED');expect(node('builder-add-session')).toBeDefined();
 expect(requests.filter(r=>r.method==='POST'&&r.path==='/me/program-builder/commands')).toHaveLength(1);
});

test('changing native tabs preserves the unsent programme draft without emitting a command',async()=>{
 await mount();await press('library-builder');await press('builder-create');await act(async()=>{node('builder-title').onChangeText('À conserver');await flush();});
 await press('library-tab-today');await press('library-tab-programmes');
 expect(node('builder-title')?.value).toBe('À conserver');expect(builderIntent()).toEqual([]);
 expect(requests.filter(r=>r.method==='POST'&&r.path==='/me/program-builder/commands')).toHaveLength(0);
});
