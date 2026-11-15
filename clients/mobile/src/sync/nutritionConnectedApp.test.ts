/** Full ConnectedApp + real NUT clients/resources + file SQLite. Only OS/RPC boundaries are synthetic. */
import React,{act} from 'react';
import {createRoot,type Root} from 'test-renderer';
import {DatabaseSync} from 'node:sqlite';
import {createHash} from 'node:crypto';
import {mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {nutritionCanonical,NUT_FIELDS} from '../domain/nutritionCommand';
import {firstUse,negotiatedReply} from '../../test/missionActionHarness';
import {historyPage} from '../../test/trainingHistoryHarness';

const mockConnections=new Map<string,DatabaseSync>();let mockDir:string,mockCredential:string|null='rt1.body-device.secret';
let mockOperation=0;
jest.mock('expo-sqlite',()=>({openDatabaseAsync:async(name:string)=>{
 if(!mockConnections.has(name))mockConnections.set(name,new(require('node:sqlite').DatabaseSync)(require('node:path').join(mockDir,name)));
 const db=mockConnections.get(name)!;const h:any={execAsync:async(s:string)=>db.exec(s),runAsync:async(s:string,...a:any[])=>db.prepare(s).run(...(Array.isArray(a[0])?a[0]:a)),getFirstAsync:async(s:string,...a:any[])=>db.prepare(s).get(...(Array.isArray(a[0])?a[0]:a))??null,getAllAsync:async(s:string,...a:any[])=>db.prepare(s).all(...(Array.isArray(a[0])?a[0]:a)),withExclusiveTransactionAsync:async(f:any)=>{db.exec('BEGIN IMMEDIATE');try{await f(h);db.exec('COMMIT');}catch(e){db.exec('ROLLBACK');throw e;}}};return h;
}}));
jest.mock('expo-crypto',()=>({randomUUID:()=>`nut-ui-${++mockOperation}`,CryptoDigestAlgorithm:{SHA256:'SHA256'},digestStringAsync:async(_algorithm:string,s:string)=>require('node:crypto').createHash('sha256').update(s).digest('hex')}));
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
 const [tab,setTab]=React.useState('profil');return React.createElement(View,null,...['profil','progres'].map(t=>React.createElement(Pressable,{key:t,testID:`nutrition-tab-${t}`,onPress:()=>setTab(t)},React.createElement(Text,null,t))),tab==='profil'?shell.account:shell.progress);
}}));
const originalTarget=process.env.EXPO_PUBLIC_API_URL;let App:React.ComponentType,root:Root,owner=7,granted=true;
const requests:{method:string;path:string;body:any}[]=[],receipts=new Map<string,any>();let day:any=null,lose=false,rejectNext=false,denyVersions=false;
const token='a'.repeat(64);const reply=(v:unknown,status=200,nut=false)=>({ok:status<400,status,json:async()=>JSON.parse(JSON.stringify(v)),headers:{get:(key:string)=>nut&&key==='X-Auren-Nutrition-Contract'?'nutrition-manual/1.0.0':null}}) as unknown as Response;
async function rpc(input:any,init?:RequestInit):Promise<Response>{
 const u=new URL(String(input)),path=u.pathname.replace('/api/mobile/v1',''),method=init?.method??'GET',body=init?.body?JSON.parse(String(init.body)):null;requests.push({method,path,body});
 if(path==='/auth/me')return reply({id:owner,username:'nutrition-synthetic'});
 if(path==='/auth/refresh'||path==='/auth/login')return reply({access_token:'test-nut-access',refresh_token:'rt1.body-device.secret',access_expires_in:900,server_now:new Date().toISOString()});
 if(path==='/auth/logout')return reply({});if(path==='/mission-action')return negotiatedReply(firstUse(owner));
 if(path.startsWith('/me/training-history')){const p=historyPage();p.window={...p.window,until:new Date().toISOString(),time_zone:u.searchParams.get('time_zone')??'UTC'};return reply(p);}
 if(path==='/me/nutrition/consent')return reply({contract_version:'nutrition-manual/1.0.0',owner_id:owner,purpose:'nutrition_manual',state:'PRESENT',granted:method==='POST'?(granted=body.granted):granted,wording_version:1,current_wording_version:1,granted_at:'2026-11-12T00:00:00Z',withdrawn_at:granted?null:'2026-11-12T13:00:00Z',consent_token:token},200,true);
 if(path==='/me/nutrition/capabilities')return reply({contract_version:'nutrition-manual/1.0.0',owner_id:owner,mode:'MANUAL_DAILY',state:'AVAILABLE',can_read:granted,can_write:granted,assisted_modes:[]},200,true);
 if(path.startsWith('/me/nutrition/operations/')){const receipt=receipts.get(path.split('/').at(-1)!);return reply(receipt??{detail:{error:'foreign_or_missing'}},receipt?200:404,true);}
 if(denyVersions&&method==='GET'&&path.endsWith('/revisions'))return reply({detail:{error:'consent_required'}},403,true);
 if(path.startsWith('/me/nutrition/days/')){
  const key=path.split('/')[4];if(method==='POST'){
   if(rejectNext){rejectNext=false;return reply({detail:{error:'stale_head'}},409,true);}
   let receipt=receipts.get(body.request_id);if(!receipt){const id=(day?.id??0)+1;
    const values={...(day?.values??Object.fromEntries(NUT_FIELDS.map(f=>[f,null]))),...body.values};
    day={id,revision:(day?.revision??0)+1,values,units:Object.fromEntries(NUT_FIELDS.map(f=>[f,{unit:f==='kcal_milli'?'kcal':'g',scale:1000}])),provenance:{fields:Object.fromEntries(NUT_FIELDS.filter(f=>values[f]!==null).map(f=>[f,{origin:'USER_DECLARED',method:id===1?'MANUAL_ENTRY':'MANUAL_CORRECTION',source_ref:`nutrition_day_revisions_v1/${id}/${f}`}])) ,date:{origin:'USER_DECLARED',precision:'LOCAL_DAY',source_ref:`nutrition_day_revisions_v1/${id}`}},recorded_at:'2026-11-12T12:00:00Z',head_token:token,local_day:key,timezone:body.timezone??day.timezone,state:'ACTIVE',declared_complete:false,target_ref:null};
    receipt={contract_version:'nutrition-operation/1.0.0',owner_id:owner,namespace:'DAY',request_id:body.request_id,command_digest:createHash('sha256').update(nutritionCanonical({namespace:'DAY',method:'POST',path,request_id:body.request_id,payload_json:String(init!.body)})).digest('hex'),state:'APPLIED',entity_ref:id,applied_revision:day.revision,recorded_at:day.recorded_at};receipts.set(body.request_id,receipt);
   }if(lose){lose=false;throw Error('response lost after synthetic RPC applied');}return reply(receipt,200,true);
  }return reply({contract_version:'nutrition-manual/1.0.0',owner_id:owner,key:{local_day:key},state:day?.local_day===key?'PRESENT':'ABSENT',head_token:token,entry:day?.local_day===key?day:null},200,true);
 }
 // Partial/unavailable history stays unavailable; it is not fabricated from the current day.
 return reply({detail:{error:'not_served_in_test'}},404,path.startsWith('/me/nutrition/'));
}
beforeAll(()=>{process.env.EXPO_PUBLIC_API_URL='https://nut-synthetic.invalid';jest.spyOn(global,'fetch').mockImplementation((input,init)=>rpc(input,init));App=require('../../ConnectedApp').default;});
beforeEach(()=>{mockDir=mkdtempSync(join(tmpdir(),'auren-nut-connected-'));mockCredential='rt1.body-device.secret';mockOperation=0;owner=7;granted=true;day=null;requests.length=0;receipts.clear();lose=false;rejectNext=false;denyVersions=false;root=createRoot();});
afterEach(async()=>{await act(async()=>root.unmount());for(const db of mockConnections.values())db.close();mockConnections.clear();rmSync(mockDir,{recursive:true,force:true});});
afterAll(()=>{jest.restoreAllMocks();if(originalTarget===undefined)delete process.env.EXPO_PUBLIC_API_URL;else process.env.EXPO_PUBLIC_API_URL=originalTarget;});
const flush=async()=>{for(let i=0;i<450;i++)await Promise.resolve();};
const node=(id:string)=>root.container.queryAll((n:any)=>n.props.testID===id)[0]?.props;
async function press(id:string){expect(node(id)).toBeDefined();await act(async()=>{node(id).onClick({nativeEvent:{},stopPropagation:()=>{},currentTarget:1,target:1});await flush();});}
async function pressLabel(label:string){const n=root.container.queryAll((n:any)=>n.props.accessibilityRole==='button'&&n.props.accessibilityLabel===label)[0];expect(n).toBeDefined();await act(async()=>{n.props.onClick({nativeEvent:{},stopPropagation:()=>{},currentTarget:1,target:1});await flush();});}
async function mount(){await act(async()=>{root.render(React.createElement(App));await flush();});await press('nutrition-tab-progres');await press('progress-nutrition');}
test('ConnectedApp Progress opens the owned NUT consumer and commits a typed zero with unknown macros',async()=>{
 await mount();await press('nutrition-edit-kcal_milli');await act(async()=>{node('nutrition-value').onChangeText('0');await flush();});await press('nutrition-save');
 expect(day.values).toEqual({kcal_milli:0,protein_milli:null,carbohydrate_milli:null,fat_milli:null});expect(day.declared_complete).toBe(false);
 const local=[...mockConnections.values()].flatMap(db=>{try{return db.prepare('SELECT state FROM nutrition_pending_commands_v1').all();}catch{return[];}});expect(local).toContainEqual(expect.objectContaining({state:'ACKED'}));
 expect(requests.filter(r=>r.method==='POST'&&r.path.includes('/days/'))).toHaveLength(1);
});
test('lost response survives full app/disk restart and reconciles by exact receipt without another creation',async()=>{
 await mount();await press('nutrition-edit-kcal_milli');await act(async()=>{node('nutrition-value').onChangeText('1750');await flush();});lose=true;await press('nutrition-save');expect(day.values.kcal_milli).toBe(1750000);
 await act(async()=>root.unmount());for(const db of mockConnections.values())db.close();mockConnections.clear();root=createRoot();await mount();await pressLabel('Vérifier le reçu');
 expect(receipts.size).toBe(1);expect(requests.filter(r=>r.method==='POST'&&r.path.includes('/days/'))).toHaveLength(1);
 const local=[...mockConnections.values()].flatMap(db=>{try{return db.prepare('SELECT state FROM nutrition_pending_commands_v1').all();}catch{return[];}});expect(local).toContainEqual(expect.objectContaining({state:'ACKED'}));
});
test('a rejected correction remains editable and sends nothing else until explicit head review and confirmation',async()=>{
 await mount();await press('nutrition-edit-kcal_milli');await act(async()=>{node('nutrition-value').onChangeText('1750');await flush();});rejectNext=true;await press('nutrition-save');
 expect(day).toBeNull();expect(node('nutrition-value')?.value).toBe('1750');expect(node('nutrition-save').accessibilityState.disabled).toBe(true);
 const count=()=>requests.filter(r=>r.method==='POST'&&r.path.includes('/days/')).length;expect(count()).toBe(1);
 await pressLabel('Relire avant de confirmer');expect(count()).toBe(1);expect(node('nutrition-value')?.value).toBe('1750');
 await press('nutrition-save');expect(count()).toBe(2);expect(day.values.kcal_milli).toBe(1750000);
 const local=[...mockConnections.values()].flatMap(db=>{try{return db.prepare('SELECT state FROM nutrition_pending_commands_v1').all();}catch{return[];}});expect(local).toContainEqual(expect.objectContaining({state:'CONFLICT'}));expect(local).toContainEqual(expect.objectContaining({state:'ACKED'}));
});
test('history consent withdrawal removes the visible day value from the complete consumer',async()=>{
 await mount();await press('nutrition-edit-kcal_milli');await act(async()=>{node('nutrition-value').onChangeText('1750');await flush();});await press('nutrition-save');
 denyVersions=true;await pressLabel('Versions de ce jour');expect(node('nutrition-consent-grant')).toBeDefined();expect(node('nutrition-edit-kcal_milli')).toBeUndefined();
 expect(root.container.queryAll((n:any)=>typeof n.props.accessibilityLabel==='string'&&n.props.accessibilityLabel.includes('1 750'))).toHaveLength(0);
});
