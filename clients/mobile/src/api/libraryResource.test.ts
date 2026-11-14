import witness from '../../test/libraryWitness.json';
import {LibraryResource} from './libraryResource';
import {deferred} from '../../test/accountDataHarness';
import type {LibraryClient,LibraryOutcome,LibraryPage} from './library';
const clone=<T,>(x:T):T=>JSON.parse(JSON.stringify(x));
function harness(){
 const auth={revision:1};let page:LibraryOutcome<LibraryPage>={state:'confirmed',value:clone(witness.page) as LibraryPage};
 const client={auth,backendScope:'https://qa.test.invalid',page:async()=>page,detail:async()=>({state:'confirmed',value:clone(witness.detail)})} as unknown as LibraryClient;
 return {auth,client,resource:new LibraryResource(client),setPage:(v:LibraryOutcome<LibraryPage>)=>page=v};
}
test('only a confirmed current detail can expose a start selection',async()=>{
 const s=harness();await s.resource.refresh({section:'all',zone:null});
 expect(s.resource.selection()).toBeNull();
 await s.resource.select(witness.created.source_ref);
 expect(s.resource.selection()?.selection_ref).toBe(witness.request.selection_ref);
 s.resource.confirm();expect(s.resource.state.view).toBe('CONFIRM');
 s.auth.revision++;expect(s.resource.selection()).toBeNull();expect(s.resource.state.index.value).toBeUndefined();
});
test('failed refresh preserves a labelled previous read and disables its departure action',async()=>{
 const s=harness();await s.resource.refresh({section:'all',zone:null});await s.resource.select(witness.created.source_ref);
 s.setPage({state:'unknown'});await s.resource.refresh({section:'all',zone:null});
 expect(s.resource.state.index).toMatchObject({status:'unknown',previous:true,value:witness.page});
 expect(s.resource.selection()).toBeNull();
});
test('late detail cannot replace a newer navigation or an account change',async()=>{
 const s=harness();await s.resource.refresh({section:'all',zone:null});
 const late=deferred<any>();s.client.detail=async()=>late.promise;
 const pending=s.resource.select(witness.created.source_ref);s.resource.back();
 late.resolve({state:'confirmed',value:witness.detail});await pending;
 expect(s.resource.state.view).toBe('INDEX');expect(s.resource.state.detail.value).toBeUndefined();
});
test('a changed continuation cannot be called a complete combined collection',async()=>{
 const s=harness(),first=clone(witness.page) as LibraryPage;
 first.entries=first.entries.slice(0,1);first.next_cursor='cursor.'+'0'.repeat(64);first.collection_state='PARTIAL';
 s.setPage({state:'confirmed',value:first});await s.resource.refresh({section:'all',zone:null});
 const next=clone(witness.page) as LibraryPage;next.read_revision='f'.repeat(64);next.entries=next.entries.slice(1);
 s.setPage({state:'confirmed',value:next});await s.resource.next();
 expect(s.resource.state.index).toMatchObject({status:'changed',previous:true,value:first});
 expect(s.resource.state.index.value?.collection_state).toBe('PARTIAL');
});
test('cannot select an unobserved private source or use previous detail as current',async()=>{
 const s=harness();let calls=0;s.client.detail=async()=>{calls++;return {state:'unknown'};};
 await s.resource.refresh({section:'all',zone:null});await s.resource.select('not-a-visible-source');
 expect(calls).toBe(0);expect(s.resource.selection()).toBeNull();
});

test('review M3: a prior read retains its technical receipt date across failed refresh',async()=>{
 const s=harness();const resource=new LibraryResource(s.client,()=>1770000000000);
 await resource.refresh({section:'all',zone:null});expect(resource.state.index.receivedAtMs).toBe(1770000000000);
 s.setPage({state:'unknown'});await resource.refresh({section:'all',zone:null});
 expect(resource.state.index.previous).toBe(true);expect(resource.state.index.receivedAtMs).toBe(1770000000000);
});

test('review M3 follow-through: failed reread of selected detail keeps its receipt date',async()=>{
 const s=harness(),resource=new LibraryResource(s.client,()=>1770000000000);
 await resource.refresh({section:'all',zone:null});await resource.select(witness.created.source_ref);
 s.client.detail=async()=>({state:'unknown'});await resource.select(witness.created.source_ref);
 expect(resource.state.detail.previous).toBe(true);expect(resource.state.detail.receivedAtMs).toBe(1770000000000);
});
