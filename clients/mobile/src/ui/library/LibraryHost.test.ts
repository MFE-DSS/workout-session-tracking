import React,{act} from 'react';
import {AppState,BackHandler} from 'react-native';
import {createHash} from 'node:crypto';
import {createRoot,type Root} from 'test-renderer';
import {accountHarness,reply} from '../../../test/accountDataHarness';
import witness from '../../../test/libraryWitness.json';
import {SqliteFile} from '../../../test/sqliteFile';
import {createLibraryPorts,LibraryClient,LIBRARY_VERSION} from '../../api/library';
import {attachLibraryPendingOpenings} from '../../storage/libraryPendingOpenings';
import {createSerialQueue} from '../../storage/serial';
import {LibraryHost} from './LibraryHost';
jest.mock('react-native-safe-area-context',()=>({useSafeAreaInsets:()=>({top:47,bottom:34,left:0,right:0})}));
let root:Root,file:SqliteFile;
beforeEach(()=>{root=createRoot();file=new SqliteFile();});
afterEach(async()=>{await act(async()=>root.unmount());file.close();jest.restoreAllMocks();});
const flush=async()=>{for(let i=0;i<100;i++)await Promise.resolve();};
const node=(id:string)=>root.container.queryAll((n:any)=>n.props.testID===id)[0]?.props;
const press=async(id:string)=>act(async()=>{node(id).onClick({nativeEvent:{},stopPropagation:()=>{},currentTarget:1,target:1});await flush();});
const hash=async(s:string)=>createHash('sha256').update(s).digest('hex');
async function setup(){
 const s=await accountHarness();s.setOwner(witness.page.owner_id);await s.auth.login('synthetic','synthetic',null);let posts=0,adopted=0;
 const fetcher=async(url:string|URL|Request,init?:RequestInit)=>{
  const path=new URL(String(url)).pathname;
  if(path.endsWith('/auth/me'))return reply(await s.call('/auth/me',{token:String((init?.headers as any)?.Authorization??'').replace('Bearer ','')}));
  let raw:any,status=200;
  if(init?.method==='POST'){posts++;raw=witness.created;status=201;}
  else if(path.includes('/items/'))raw=witness.detail;
  else{raw=JSON.parse(JSON.stringify(witness.page));raw.entries=raw.entries.filter((e:any)=>e.name==='qa-http');}
  return {...reply(raw,status),headers:{get:()=>LIBRARY_VERSION}} as unknown as Response;
 };
 const client=new LibraryClient(s.auth,createLibraryPorts('https://qa.test.invalid',fetcher as typeof fetch,hash));
 const p:any={...file.port(),getAllAsync:async(sql:string,...args:any[])=>file.db.prepare(sql).all(...args)};
 p.withExclusiveTransactionAsync=async(action:(tx:any)=>Promise<void>)=>{file.db.exec('BEGIN IMMEDIATE');try{await action(p);file.db.exec('COMMIT');}catch(e){file.db.exec('ROLLBACK');throw e;}};
 const pending=await attachLibraryPendingOpenings(p,createSerialQueue(),witness.page.owner_id,client.backendScope,hash,()=>true);
 const ports={client,pending,uuid:()=> 'd477ea9f-7bd9-4fc4-a679-c50f86a2ad41',now:()=>1000,otherActionPending:()=>false,
  readOwned:async()=>({state:'confirmed' as const,owner_id:witness.page.owner_id,backend_scope:client.backendScope,session:null}),
  adoptLegacy:async()=>{adopted++;},resumeOwned:async()=>{}};
 return {ports,get posts(){return posts;},get adopted(){return adopted;}};
}
test('native Host reads actual DTO contract and requires detail plus explicit confirmation before POST',async()=>{
 const s=await setup();await act(async()=>{root.render(React.createElement(LibraryHost,{ports:s.ports,onResumeExisting:()=>{}}));await flush();});
 expect(node('library-entry-'+witness.created.source_ref)).toBeDefined();expect(s.posts).toBe(0);
 await press('library-entry-'+witness.created.source_ref);expect(node('library-ask-start')).toBeDefined();expect(s.posts).toBe(0);
 await press('library-ask-start');expect(node('library-confirm-start')).toBeDefined();expect(s.posts).toBe(0);
 await press('library-confirm-start');await act(async()=>{await new Promise(r=>setTimeout(r,10));await flush();});
 expect(s.posts).toBe(1);expect(s.adopted).toBe(1);expect(await s.ports.pending.unresolved(()=>true)).toBeNull();
});
test('Android back leaves confirmation without creating a workout',async()=>{
 let back=()=>false;jest.spyOn(BackHandler,'addEventListener').mockImplementation((_e,handler)=>{back=()=>handler(undefined as never)===true;return{remove:jest.fn()};});
 const s=await setup();await act(async()=>{root.render(React.createElement(LibraryHost,{ports:s.ports,onResumeExisting:()=>{}}));await flush();});
 expect(back()).toBe(false);await press('library-entry-'+witness.created.source_ref);await press('library-ask-start');
 await act(async()=>{expect(back()).toBe(true);await flush();});expect(node('library-confirm-start')).toBeUndefined();expect(s.posts).toBe(0);
});

test('review: successful opening must not navigate again on a later parent render',async()=>{
 const s=await setup(),navigate=jest.fn();
 const render=()=>root.render(React.createElement(LibraryHost,{ports:s.ports,onResumeExisting:()=>{},onOpened:()=>navigate()}));
 await act(async()=>{render();await flush();});
 await press('library-entry-'+witness.created.source_ref);await press('library-ask-start');await press('library-confirm-start');
 await act(async()=>{await new Promise(r=>setTimeout(r,10));await flush();});
 expect(navigate).toHaveBeenCalledTimes(1);
 await act(async()=>{render();await flush();});
 expect(navigate).toHaveBeenCalledTimes(1);
});


test('foreground during durable preparation must not invalidate the confirmed choice or suppress the first POST',async()=>{
 let foreground=(state:string)=>{};jest.spyOn(AppState,'addEventListener').mockImplementation((_event,listener)=>{foreground=listener as (s:string)=>void;return{remove:jest.fn()};});
 const s=await setup(),original=s.ports.pending.prepare.bind(s.ports.pending);let prepared=false,finish=()=>{};
 const gate=new Promise<void>(resolve=>{finish=resolve;});s.ports.pending.prepare=async(...args)=>{const row=await original(...args);prepared=true;await gate;return row;};
 await act(async()=>{root.render(React.createElement(LibraryHost,{ports:s.ports,onResumeExisting:()=>{}}));await flush();});
 await press('library-entry-'+witness.created.source_ref);await press('library-ask-start');await press('library-confirm-start');
 await act(async()=>{await new Promise(r=>setTimeout(r,10));await flush();});expect(prepared).toBe(true);
 await act(async()=>{foreground('active');await flush();});
 await act(async()=>{finish();await new Promise(r=>setTimeout(r,10));await flush();});
 expect(s.posts).toBe(1);expect(s.adopted).toBe(1);
});
