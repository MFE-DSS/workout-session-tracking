import {createHash} from 'node:crypto';
import witness from '../../test/libraryWitness.json';
import {SqliteFile} from '../../test/sqliteFile';
import {attachLibraryPendingOpenings} from '../storage/libraryPendingOpenings';
import {createSerialQueue} from '../storage/serial';
import {LibraryOpeningController} from './libraryOpening';
import type {LibraryClient,LibraryStartOutcome} from '../api/library';
const hash=async(raw:string)=>createHash('sha256').update(raw).digest('hex');
const owner=witness.page.owner_id,backend='https://qa.test.invalid',localId='d477ea9f-7bd9-4fc4-a679-c50f86a2ad41';
let file:SqliteFile;
beforeEach(()=>{file=new SqliteFile();});afterEach(()=>file.close());
async function setup(){
 const p:any={...file.port(),getAllAsync:async(sql:string,...args:any[])=>file.db.prepare(sql).all(...args)};
 p.withExclusiveTransactionAsync=async(action:(tx:any)=>Promise<void>)=>{file.db.exec('BEGIN IMMEDIATE');try{await action(p);file.db.exec('COMMIT');}catch(e){file.db.exec('ROLLBACK');throw e;}};
 const pending=await attachLibraryPendingOpenings(p,createSerialQueue(),owner,backend,hash,()=>true);
 const auth={revision:1};let sends=0,adopted=0,resumed=0,allow=true,saveFails=false;
 let result:LibraryStartOutcome={state:'created',value:witness.created as any};
 let owned:any={state:'confirmed',owner_id:owner,backend_scope:backend,session:{session_id:42,session_profile:'PLAN_V3'}};
 const client={auth,backendScope:backend,owner:async()=>owner,start:async()=>{sends++;return result;}} as unknown as LibraryClient;
 const make=()=>new LibraryOpeningController({client,pending,now:()=>1000,uuid:()=>localId,otherActionPending:()=>!allow,
  readOwned:async()=>{if(owned instanceof Error)throw owned;return owned;},adoptLegacy:async()=>{if(saveFails)throw Error('local save failed');adopted++;},resumeOwned:async()=>{resumed++;}});
 return {pending,client,make,controller:make(),auth,get sends(){return sends;},get adopted(){return adopted;},get resumed(){return resumed;},refused:()=>result={state:'refused',value:witness.refused as any},unknown:()=>result={state:'unknown'},block:()=>allow=false,failSave:()=>saveFails=true,setOwned:(v:any)=>owned=v};
}
const choice={source_ref:witness.created.source_ref,selection_ref:witness.request.selection_ref,read_revision:witness.detail.read_revision};
test('prepare/readback/sent precede single creation and persistence precedes exact resolution',async()=>{
 const s=await setup();await s.controller.hydrate();await s.controller.submit(choice,()=>true);
 expect(s.sends).toBe(1);expect(s.adopted).toBe(1);expect(s.controller.state.phase).toBe('created');
 expect(await s.pending.unresolved(()=>true)).toBeNull();expect((await s.pending.get(localId,()=>true))?.creation_outcome).toBe('CONFIRMED');
});
test('lost response survives new controller and verify/resume never replays creation',async()=>{
 const s=await setup();s.unknown();await s.controller.submit(choice,()=>true);expect(s.sends).toBe(1);
 const restored=s.make();await restored.hydrate();expect(restored.state.phase).toBe('unknown');
 await restored.verify();expect(restored.state.phase).toBe('owned_found');expect(s.sends).toBe(1);
 await restored.resume();expect(s.resumed).toBe(1);expect(s.sends).toBe(1);
 expect((await s.pending.get(localId,()=>true))?.creation_outcome).toBe('UNKNOWN');
});
test('201 followed by failed local execution save stays unresolved',async()=>{
 const s=await setup();s.failSave();await s.controller.submit(choice,()=>true);
 expect(s.sends).toBe(1);expect(s.controller.state.phase).toBe('unknown');
 expect((await s.pending.unresolved(()=>true))?.state).toBe('SENT_UNKNOWN');
 await s.controller.submit(choice,()=>true);expect(s.sends).toBe(1);
});
test('failed preparation prevents network send',async()=>{
 const s=await setup();file.db.exec('DROP TABLE library_pending_openings_v1');
 await s.controller.submit(choice,()=>true);expect(s.sends).toBe(0);expect(s.controller.state.phase).toBe('unavailable');
});
test('global pending action or noncurrent selection prevents preparation and send',async()=>{
 const s=await setup();s.block();await s.controller.submit(choice,()=>true);expect(s.sends).toBe(0);
 expect(await s.pending.unresolved(()=>true)).toBeNull();
});
test('definitive refusal is resolved separately from network unknown',async()=>{
 const s=await setup();s.refused();await s.controller.submit(choice,()=>true);
 expect(s.controller.state.phase).toBe('owned_found');expect(s.adopted).toBe(0);
 expect((await s.pending.get(localId,()=>true))?.creation_outcome).toBe('NOT_CREATED');
});
test('explicit local cancel preserves UNKNOWN and does not call server or close workout',async()=>{
 const s=await setup();s.unknown();await s.controller.submit(choice,()=>true);await s.controller.cancel(false);
 expect(await s.pending.unresolved(()=>true)).not.toBeNull();await s.controller.cancel(true);
 expect((await s.pending.get(localId,()=>true))?.resolution_kind).toBe('INTENTION_CANCELLED');
 expect((await s.pending.get(localId,()=>true))?.creation_outcome).toBe('UNKNOWN');expect(s.sends).toBe(1);expect(s.resumed).toBe(0);
});
test('foreign owned reading or changed session never resolves or resumes the intention',async()=>{
 const s=await setup();s.unknown();await s.controller.submit(choice,()=>true);
 s.setOwned({state:'confirmed',owner_id:owner+1,backend_scope:backend,session:{session_id:43,session_profile:'LEGACY'}});
 await s.controller.verify();expect(s.controller.state.phase).toBe('unknown');expect(s.resumed).toBe(0);
 expect(await s.pending.unresolved(()=>true)).not.toBeNull();
});
test('account change clears visible state while preserving original owner intention',async()=>{
 const s=await setup();s.unknown();await s.controller.submit(choice,()=>true);s.auth.revision++;
 expect(s.controller.state.phase).toBe('cancelled');expect(s.controller.state.pending).toBeUndefined();
 expect(await s.pending.unresolved(()=>true)).not.toBeNull();await s.controller.verify();expect(s.resumed).toBe(0);
});

test.each(['LEGACY','PLAN_V3'] as const)('review I1: cross-device session_open offers fresh %s resume without a false creation receipt',async profile=>{
 const s=await setup();s.refused();s.setOwned({state:'confirmed',owner_id:owner,backend_scope:backend,session:{session_id:42,session_profile:profile}});
 await s.controller.submit(choice,()=>true);
 expect(s.controller.state.phase).toBe('owned_found');expect(s.controller.state.owned?.session_profile).toBe(profile);
 await s.controller.resume();expect(s.resumed).toBe(1);expect(s.sends).toBe(1);
 expect((await s.pending.get(localId,()=>true))?.creation_outcome).toBe('NOT_CREATED');
});
test('review I1: failed owned read after definite session_open preserves refusal and allows explicit verification',async()=>{
 const s=await setup();s.refused();s.setOwned({state:'unknown'});await s.controller.submit(choice,()=>true);
 expect(s.controller.state).toMatchObject({phase:'refused',code:'session_open'});
 s.setOwned({state:'confirmed',owner_id:owner,backend_scope:backend,session:{session_id:42,session_profile:'LEGACY'}});
 await s.controller.verify();expect(s.controller.state.phase).toBe('owned_found');expect(s.sends).toBe(1);
});
test('review I1: a changed owned session at resume does not adopt the earlier identity',async()=>{
 const s=await setup();s.refused();await s.controller.submit(choice,()=>true);
 s.setOwned({state:'confirmed',owner_id:owner,backend_scope:backend,session:{session_id:99,session_profile:'LEGACY'}});
 await s.controller.resume();expect(s.resumed).toBe(0);expect(s.sends).toBe(1);
 expect((await s.pending.get(localId,()=>true))?.creation_outcome).toBe('NOT_CREATED');
});

test('review I1 rejected-read follow-through: thrown owned read cannot erase definitive refusal',async()=>{
 const s=await setup();s.refused();s.setOwned(new Error('transport failed'));
 await s.controller.submit(choice,()=>true);expect(s.controller.state).toMatchObject({phase:'refused',code:'session_open'});
 s.setOwned({state:'confirmed',owner_id:owner,backend_scope:backend,session:{session_id:42,session_profile:'LEGACY'}});
 await s.controller.verify();expect(s.controller.state.phase).toBe('owned_found');expect(s.sends).toBe(1);
});
