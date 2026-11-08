import {DatabaseSync} from 'node:sqlite';
let mockDb:DatabaseSync;
jest.mock('expo-sqlite',()=>({openDatabaseAsync:async()=>{
 const handle:any={execAsync:async(sql:string)=>mockDb.exec(sql),runAsync:async(sql:string,...args:any[])=>mockDb.prepare(sql).run(...(Array.isArray(args[0])?args[0]:args)),
 getFirstAsync:async(sql:string,...args:any[])=>mockDb.prepare(sql).get(...(Array.isArray(args[0])?args[0]:args))??null,
 getAllAsync:async(sql:string,...args:any[])=>mockDb.prepare(sql).all(...(Array.isArray(args[0])?args[0]:args)),
 withExclusiveTransactionAsync:async(fn:any)=>{mockDb.exec('BEGIN IMMEDIATE');try{await fn(handle);mockDb.exec('COMMIT');}catch(e){mockDb.exec('ROLLBACK');throw e;}}};return handle;
}}));
import {openJournal} from './journal';
import {initialState} from '../domain/workout';
import type {PlanV3Stored} from '../domain/planV3Types';
test('shared journal attaches V3 only after owner proof and never casts or overwrites V3 as V1',async()=>{
 mockDb=new DatabaseSync(':memory:');try{
 const j=await openJournal('owned',{planV3OwnerId:7});expect(j.planV3).toBeDefined();
 const state:PlanV3Stored={profile:'PLAN_V3',local_version:'first-session-local/3.0.0',owner_id:7,phase:'FIRST_USE',intent:null,execution:null,source:{},local_facts:{},drafts:{}};
 await j.planV3!.claim(state,()=>true);
 expect((await j.restore()).snapshot).toBeNull();await j.saveSnapshot(initialState);
 expect(await j.planV3!.read()).toEqual(state);
 }finally{mockDb.close();}
});
test('a newly admitted legacy session can follow a confirmed closed V3 session; late generic saves cannot take its place',async()=>{
 mockDb=new DatabaseSync(':memory:');try{
 const j=await openJournal('owned',{planV3OwnerId:7});
 const old:any={profile:'PLAN_V3',local_version:'first-session-local/3.0.0',owner_id:7,phase:'COMPLETE',intent:null,execution:{session_id:21,status:'completed'},source:{},local_facts:{},drafts:{}};
 await j.planV3!.claim(old,()=>true);
 const fresh:any={...initialState,phase:'SET',plan:{session_id:31}};
 await j.saveSnapshot(fresh);expect((await j.restore()).snapshot).toBeNull();
 await j.beginLegacy!(fresh,()=>true);expect((await j.restore()).snapshot?.plan?.session_id).toBe(31);
 }finally{mockDb.close();}
});

test.each(['unfinished','pending'])('legacy adoption refuses %s V3 work without replacing its journal',async(reason)=>{
 mockDb=new DatabaseSync(':memory:');try{
 const j=await openJournal('owned',{planV3OwnerId:7});
 const old:any={profile:'PLAN_V3',local_version:'first-session-local/3.0.0',owner_id:7,phase:reason==='unfinished'?'SET':'COMPLETE',intent:null,execution:{session_id:21,status:reason==='unfinished'?'in_progress':'completed'},source:{},local_facts:{},drafts:{}};
 await j.planV3!.claim(old,()=>true);
 if(reason==='pending')mockDb.exec("INSERT INTO outbox(op_id,kind,target,payload,state,created_at_ms) VALUES('pending-op','PLAN_V3_SET','/test','{}','pending',1)");
 await expect(j.beginLegacy!({...initialState,phase:'SET',plan:{session_id:31}} as any,()=>true)).rejects.toThrow(reason==='pending'?'pending_journal_conflict':'active_session_conflict');
 expect((await j.planV3!.read())?.execution?.session_id).toBe(21);
 }finally{mockDb.close();}
});
test('resolved refusals remain in history but no longer masquerade as unsent work during logout',async()=>{
 mockDb=new DatabaseSync(':memory:');try{
 const j=await openJournal('owned',{planV3OwnerId:7});
 mockDb.exec("INSERT INTO outbox(op_id,kind,target,payload,state,created_at_ms) VALUES('refused','PLAN_V3_SET','set/4','{}','resolved',1)");
 expect(await j.outboxRows()).toEqual([]);
 expect((await j.restore()).outbox).toEqual([expect.objectContaining({op_id:'refused',state:'resolved'})]);
 }finally{mockDb.close();}
});
