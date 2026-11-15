/** Full ConnectedApp + real BODY clients/resources + file SQLite. Only OS/RPC boundaries are synthetic. */
import React,{act} from 'react';
import {createRoot,type Root} from 'test-renderer';
import {DatabaseSync} from 'node:sqlite';
import {createHash} from 'node:crypto';
import {mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {BODY_KEYS,bodyCommandCanonical} from '../api/bodyMeasurements';
import {firstUse,negotiatedReply} from '../../test/missionActionHarness';
import {historyPage} from '../../test/trainingHistoryHarness';

const mockConnections=new Map<string,DatabaseSync>();let mockDir:string,mockCredential:string|null='rt1.body-device.secret';
let mockOperation=0;
jest.mock('expo-sqlite',()=>({openDatabaseAsync:async(name:string)=>{
 if(!mockConnections.has(name))mockConnections.set(name,new(require('node:sqlite').DatabaseSync)(require('node:path').join(mockDir,name)));
 const db=mockConnections.get(name)!;const h:any={execAsync:async(s:string)=>db.exec(s),runAsync:async(s:string,...a:any[])=>db.prepare(s).run(...(Array.isArray(a[0])?a[0]:a)),getFirstAsync:async(s:string,...a:any[])=>db.prepare(s).get(...(Array.isArray(a[0])?a[0]:a))??null,getAllAsync:async(s:string,...a:any[])=>db.prepare(s).all(...(Array.isArray(a[0])?a[0]:a)),withExclusiveTransactionAsync:async(f:any)=>{db.exec('BEGIN IMMEDIATE');try{await f(h);db.exec('COMMIT');}catch(e){db.exec('ROLLBACK');throw e;}}};return h;
}}));
jest.mock('expo-crypto',()=>({randomUUID:()=>`body-ui-${++mockOperation}`,CryptoDigestAlgorithm:{SHA256:'SHA256'},digestStringAsync:async(_algorithm:string,s:string)=>require('node:crypto').createHash('sha256').update(s).digest('hex')}));
jest.mock('../auth/credentialStore',()=>({credentialStore:{read:async()=>mockCredential,write:async(v:string)=>{mockCredential=v;},clear:async()=>{mockCredential=null;}}}));
jest.mock('../storage/ownershipStore',()=>({openOwnershipBook:async()=>jest.requireActual('../storage/ownershipStore').createOwnershipBook(await require('expo-sqlite').openDatabaseAsync('auren-owners-v1.db'))}));
jest.mock('../storage/legacyInspection',()=>({inspectLegacyJournal:async()=>({snapshot:null,sets:[],outbox:[]})}));
jest.mock('../native/restNotification',()=>({restNotification:{onDelivery:()=>()=>{},cancel:async()=>{},prepare:async()=>false,schedule:async()=>null}}));
jest.mock('../native/keepAwake',()=>({keepAwake:{enable:()=>{},disable:()=>{}}}));
jest.mock('../native/motion',()=>({useReducedMotion:()=>true,announce:()=>{}}));
jest.mock('../native/feedback',()=>({feedback:new Proxy({},{get:()=>()=>{}})}));
jest.mock('../shell/routeContext',()=>({shellRoutes:{}}));
jest.mock('react-native-safe-area-context',()=>({SafeAreaView:({children,...props}:any)=>require('react').createElement(require('react-native').View,props,children),useSafeAreaInsets:()=>({top:47,bottom:34,left:0,right:0}),useSafeAreaFrame:()=>({width:390,height:844}),SafeAreaProvider:({children}:any)=>children}));
jest.mock('expo-router',()=>({useFocusEffect:(fn:any)=>require('react').useEffect(fn,[fn]),ExpoRoot:()=>{
 const React=require('react'),{Pressable,Text,View}=require('react-native'),shell=require('../shell/ShellContext').useShell();
 const [tab,setTab]=React.useState('profil');return React.createElement(View,null,...['profil','progres'].map(t=>React.createElement(Pressable,{key:t,testID:`body-tab-${t}`,onPress:()=>setTab(t)},React.createElement(Text,null,t))),tab==='profil'?shell.account:shell.progress);
}}));
const originalTarget=process.env.EXPO_PUBLIC_API_URL;
let App:React.ComponentType,root:Root,owner=7,granted=true,rows:any[]=[],previous:any[]=[],version=0;
const requests:{method:string;path:string;body:any}[]=[],receipts=new Map<string,any>();let loseNext=false;
const hash=(s:string)=>createHash('sha256').update(s).digest('hex');
const specs=BODY_KEYS.map(key=>({key,label:key,min:1,max:500,unit:key==='weight_kg'?'kg':'cm'}));
function entry(id:number,values:any,rootRef=id,revision=1){return{root_ref:rootRef,measurement_id:id,revision,state:'CURRENT',head_token:hash(String(id)),measured_at:'2026-11-11T00:00:00Z',recorded_at:'2026-11-11T12:00:00Z',date_precision:'DAY_UTC_CONVENTION',timezone_basis:'DATABASE_UTC_CONVENTION',fields:Object.fromEntries([...BODY_KEYS,'calf_cm'].map(k=>[k,{value:values[k]??null,raw_value_repr:null,quality:values[k]==null?'MISSING':'KNOWN',unit:k==='weight_kg'?'kg':'cm',provenance:{origin:values[k]==null?'UNKNOWN':'USER_DECLARED',acquisition:values[k]==null?'UNKNOWN':revision===1?'MANUAL_ENTRY':'MANUAL_CORRECTION',source_ref:`body_measurements/${id}/${k}`}}]))};}
const reply=(v:unknown,status=200,body=false)=>({ok:status<400,status,json:async()=>JSON.parse(JSON.stringify(v)),headers:{get:(key:string)=>body&&key==='X-Auren-Body-Contract'?'body-measurements/1.0.0':null}}) as unknown as Response;
function page(entries=rows){return{contract_version:'body-measurements/1.0.0',owner_id:owner,body_revision:version,state:entries.length?'AVAILABLE':'EMPTY',entries,next_cursor:null,window:{from:null,through:null},field_specs:specs};}
async function rpc(input:any,init?:RequestInit):Promise<Response>{
 const u=new URL(String(input)),path=u.pathname.replace('/api/mobile/v1',''),method=init?.method??'GET',body=init?.body?JSON.parse(String(init.body)):null;requests.push({method,path,body});
 if(path==='/auth/me')return reply({id:owner,username:'body-synthetic'});
 if(path==='/auth/refresh'||path==='/auth/login')return reply({access_token:'test-body-access',refresh_token:'rt1.body-device.secret',access_expires_in:900,server_now:new Date().toISOString()});
 if(path==='/auth/logout')return reply({});
 if(path==='/mission-action')return negotiatedReply(firstUse(owner));
 if(path.startsWith('/me/training-history')){const p=historyPage();p.window={...p.window,until:new Date().toISOString(),time_zone:u.searchParams.get('time_zone')??'UTC'};return reply(p);}
 if(path==='/me/body/consent')return reply({contract_version:'body-measurements/1.0.0',owner_id:owner,granted:method==='POST'?(granted=body.granted):granted,consent_version:1,granted_at:'2026-11-11T12:00:00Z',withdrawn_at:granted?null:'2026-11-11T13:00:00Z',consent_token:'a'.repeat(64)},200,true);
 if(path.startsWith('/me/body/operations/')){const receipt=receipts.get(path.split('/').at(-1)!);return reply(receipt??{detail:{error:'body_operation_unknown'}},receipt?200:404,true);}
 if(path.startsWith('/me/body/measurements')){
  if(method==='GET'&&u.searchParams.get('purpose')==='erasure'){
   const match=path.match(/\/measurements\/(\d+)$/);
   const minimal=(e:any)=>({root_ref:e.root_ref,measurement_id:e.measurement_id,revision:e.revision,head_token:e.head_token,measured_at:e.measured_at,date_precision:e.date_precision,version_count:previous.filter(p=>p.root_ref===e.root_ref).length+1});
   if(match){const found=rows.find(e=>e.root_ref===Number(match[1]));return reply(found?{contract_version:'body-measurements/1.0.0',owner_id:owner,projection:'ERASURE_ONLY',entry:minimal(found)}:{detail:{error:'measurement_not_found'}},found?200:404,true);}
   return reply({contract_version:'body-measurements/1.0.0',owner_id:owner,projection:'ERASURE_ONLY',body_revision:version,state:rows.length?'AVAILABLE':'EMPTY',entries:rows.map(minimal),next_cursor:null,window:{from:null,through:null}},200,true);
  }
  if(!granted&&!path.endsWith('/erase'))return reply({detail:{error:'body_consent_required'}},403,true);
  const match=path.match(/\/measurements\/(\d+)(?:\/(\w+))?$/);
  if(method==='POST'){
   let receipt=receipts.get(body.request_id);
   if(!receipt){const operation=match?.[2]==='erase'?'ERASE':match?'CORRECT':'CREATE',prior=match?rows.find(e=>e.root_ref===Number(match[1])):undefined;
    version++;const id=20+version,rootRef=prior?.root_ref??id;
    if(prior){previous.push({...prior,state:'SUPERSEDED',head_token:null});rows=rows.filter(e=>e.root_ref!==rootRef);}
    if(operation!=='ERASE')rows.unshift(entry(id,{...(prior?Object.fromEntries(Object.entries(prior.fields).map(([k,v]:any)=>[k,v.value])):{}),...body.values},rootRef,(prior?.revision??0)+1));else previous=previous.filter(e=>e.root_ref!==rootRef);
    receipt={contract_version:'body-operation/1.0.0',owner_id:owner,command_digest:hash(bodyCommandCanonical({method:'POST',path,request_id:body.request_id,payload_json:JSON.stringify(body)})),request_id:body.request_id,operation,root_ref:rootRef,measurement_id:operation==='ERASE'?prior.measurement_id:id,applied_revision:(prior?.revision??0)+1,recorded_at:'2026-11-11T12:00:00Z',state:operation==='ERASE'?'ERASED':'APPLIED'};receipts.set(body.request_id,receipt);
   }
   if(loseNext){loseNext=false;throw Error('controlled response loss after RPC applied');}return reply(receipt,200,true);
  }
  if(match&&match[2]!=='versions'){const e=rows.find(e=>e.root_ref===Number(match[1]));return reply({contract_version:'body-measurements/1.0.0',owner_id:owner,entry:e},e?200:404,true);}
  const entries=match?[...rows,...previous].filter(e=>e.root_ref===Number(match[1])):rows;
  const p=page(entries);if(u.searchParams.has('from'))p.window={from:u.searchParams.get('from'),through:u.searchParams.get('through')} as any;
  return reply(p,200,true);
 }
 return reply({detail:{error:'not_served_in_test'}},404);
}
beforeAll(()=>{process.env.EXPO_PUBLIC_API_URL='https://body-synthetic.invalid';jest.spyOn(global,'fetch').mockImplementation((input,init)=>rpc(input,init));App=require('../../ConnectedApp').default;});
beforeEach(()=>{mockDir=mkdtempSync(join(tmpdir(),'auren-body-connected-'));mockCredential='rt1.body-device.secret';mockOperation=0;owner=7;granted=true;rows=[];previous=[];version=0;requests.length=0;receipts.clear();loseNext=false;root=createRoot();});
afterEach(async()=>{await act(async()=>root.unmount());for(const db of mockConnections.values())db.close();mockConnections.clear();rmSync(mockDir,{recursive:true,force:true});});
afterAll(()=>{jest.restoreAllMocks();if(originalTarget===undefined)delete process.env.EXPO_PUBLIC_API_URL;else process.env.EXPO_PUBLIC_API_URL=originalTarget;});
const flush=async()=>{for(let i=0;i<400;i++)await Promise.resolve();};
const node=(id:string)=>root.container.queryAll((n:any)=>n.props.testID===id)[0]?.props;
async function pressLabel(label:string){const n=root.container.queryAll((n:any)=>n.props.accessibilityRole==='button'&&n.props.accessibilityLabel===label)[0];expect(n).toBeDefined();await act(async()=>{n.props.onClick({nativeEvent:{},stopPropagation:()=>{},currentTarget:1,target:1});await flush();});}
async function press(id:string){expect(node(id)).toBeDefined();await act(async()=>{node(id).onClick({nativeEvent:{},stopPropagation:()=>{},currentTarget:1,target:1});await flush();});}
async function enter(id:string,value:string){await act(async()=>{node(id).onChangeText(value);await flush();});}
async function mount(){await act(async()=>{root.render(React.createElement(App));await flush();});}
test('ConnectedApp opens owned BODY from Profile, writes a comma decimal and reads the same effective value in Progress',async()=>{
 await mount();await pressLabel('Mesures corporelles');await press('body-new');await enter('body-value-weight_kg','72,5');await enter('body-day','2026-11-11');await press('body-save');
 expect(rows[0].fields.weight_kg.value).toBe(72.5);expect(receipts.size).toBe(1);expect(node('body-notice')).toBeDefined();
 await pressLabel('Retour');await press('body-tab-progres');expect(node('progress-weight-chart')).toBeDefined();
 expect(requests.some(r=>r.path==='/me/body/measurements/weight-history')).toBe(true);
 const local=[...mockConnections.values()].flatMap(db=>{try{return db.prepare('SELECT state FROM body_pending_commands_v1').all();}catch{return[];}});expect(local).toContainEqual(expect.objectContaining({state:'ACKED'}));await press('progress-weight-write');expect(node('body-current-value')).toBeDefined();await press('body-sources');expect(requests.some(r=>r.path==='/me/body/measurements/21')).toBe(true);
});
test('ConnectedApp linked correction/audit/explicit erase share the same owned reader and leave no resurrected chart point',async()=>{
 rows=[entry(11,{weight_kg:80,arm_cm_left:32.5})];version=1;await mount();await pressLabel('Mesures corporelles');await press('body-sources');await pressLabel('Corriger');await pressLabel('Poids');await enter('body-value-weight_kg','79,5');await press('body-save');
 expect(previous[0].fields.weight_kg.value).toBe(80);expect(rows[0].fields.arm_cm_left.value).toBe(32.5);expect(rows[0].measurement_id).not.toBe(11);
 await press('body-sources');await pressLabel('Voir les versions');expect(previous[0].state).toBe('SUPERSEDED');await pressLabel('Retour');await pressLabel('Supprimer le relevé');expect(receipts.size).toBe(1);await pressLabel('Confirmer la suppression');
 expect(rows).toEqual([]);expect(previous).toEqual([]);await pressLabel('Retour');await press('body-tab-progres');expect(node('progress-weight-chart')).toBeUndefined();
});
test('lost response stays durable on the full app path; verify acknowledges the same key without a duplicate POST',async()=>{
 await mount();await pressLabel('Mesures corporelles');await press('body-new');await enter('body-value-weight_kg','72');await enter('body-day','2026-11-11');loseNext=true;await press('body-save');
 expect(rows).toHaveLength(1);const writes=requests.filter(r=>r.method==='POST'&&r.path==='/me/body/measurements');expect(writes).toHaveLength(1);await act(async()=>{root.unmount();await flush();});for(const db of mockConnections.values())db.close();mockConnections.clear();root=createRoot();await mount();await pressLabel('Mesures corporelles');await pressLabel('Vérifier');expect(receipts.size).toBe(1);expect(requests.filter(r=>r.method==='POST'&&r.path==='/me/body/measurements')).toHaveLength(1);
});

test('full app requires an explicit consent action and clears BODY facts after withdrawal',async()=>{
 granted=false;await mount();await pressLabel('Mesures corporelles');expect(node('body-new')).toBeUndefined();expect(node('body-consent-grant')).toBeDefined();expect(requests.filter(r=>r.path==='/me/body/consent'&&r.method==='POST')).toHaveLength(0);
 await press('body-consent-grant');expect(node('body-new')).toBeDefined();await pressLabel('Aide et accord');await pressLabel('Retirer l’accord des mesures');expect(node('body-new')).toBeUndefined();expect(node('body-consent-grant')).toBeDefined();expect(granted).toBe(false);
});
test('withdrawal then a full SQLite reopen permits new explicit erasure and unknown-receipt recovery without regrant',async()=>{
 rows=[entry(11,{weight_kg:80})];version=1;await mount();await pressLabel('Mesures corporelles');await pressLabel('Aide et accord');await pressLabel('Retirer l’accord des mesures');
 expect(granted).toBe(false);
 await act(async()=>{root.unmount();await flush();});for(const db of mockConnections.values())db.close();mockConnections.clear();root=createRoot();await mount();await pressLabel('Mesures corporelles');
 await press('body-manage-erasure');await press('body-erase-entry-11');
 expect(node('body-new')).toBeUndefined();expect(node('body-value-weight_kg')).toBeUndefined();
 await pressLabel('Supprimer le relevé');loseNext=true;await pressLabel('Confirmer la suppression');
 expect(rows).toEqual([]);expect(granted).toBe(false);
 const erases=()=>requests.filter(r=>r.method==='POST'&&r.path==='/me/body/measurements/11/erase');expect(erases()).toHaveLength(1);
 await act(async()=>{root.unmount();await flush();});for(const db of mockConnections.values())db.close();mockConnections.clear();root=createRoot();await mount();await pressLabel('Mesures corporelles');await pressLabel('Vérifier');
 expect(erases()).toHaveLength(1);expect(requests.filter(r=>r.path==='/me/body/consent'&&r.method==='POST'&&r.body.granted)).toHaveLength(0);
 const commands=[...mockConnections.values()].flatMap(db=>{try{return db.prepare('SELECT state FROM body_pending_commands_v1').all();}catch{return[];}});expect(commands).toContainEqual(expect.objectContaining({state:'ACKED'}));
});
test('BODY stays in its originating native tab; shell remains available without mounting two measurement controllers',async()=>{
 rows=[entry(11,{weight_kg:80})];await mount();await pressLabel('Mesures corporelles');
 expect(node('connected-content').pointerEvents).toBe('auto');expect(node('body-cockpit')).toBeDefined();
 await press('body-tab-progres');expect(node('body-cockpit')).toBeUndefined();expect(node('progress-weight-chart')).toBeDefined();
});
