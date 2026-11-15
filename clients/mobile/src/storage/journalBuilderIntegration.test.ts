import {DatabaseSync} from 'node:sqlite';
let mockDb:DatabaseSync;
jest.mock('expo-sqlite',()=>({openDatabaseAsync:async()=>{
 const handle:any={execAsync:async(sql:string)=>mockDb.exec(sql),runAsync:async(sql:string,...args:any[])=>mockDb.prepare(sql).run(...(Array.isArray(args[0])?args[0]:args)),
 getFirstAsync:async(sql:string,...args:any[])=>mockDb.prepare(sql).get(...(Array.isArray(args[0])?args[0]:args))??null,
 getAllAsync:async(sql:string,...args:any[])=>mockDb.prepare(sql).all(...(Array.isArray(args[0])?args[0]:args)),
 withExclusiveTransactionAsync:async(fn:any)=>{mockDb.exec('BEGIN IMMEDIATE');try{await fn(handle);mockDb.exec('COMMIT');}catch(e){mockDb.exec('ROLLBACK');throw e;}}};return handle;
}}));
import {openJournal} from './journal';
import {createHash} from 'node:crypto';
const hash=async(s:string)=>createHash('sha256').update(s).digest('hex');
const body={contract_version:'program-builder/1.0.0',command_id:'one',operation:'CREATE',program_id:null,expected_source_digest:null,payload:{title:'Programme'}};
test('real shared journal attaches builder recovery separately from the workout sync outbox',async()=>{
 mockDb=new DatabaseSync(':memory:');try{
  const open=(ownerId:number,backendScope:string,current=()=>true)=>openJournal('owned',{builderOwner:{ownerId,backendScope,sha256:hash,current}});
  const j=await open(1,'https://a.invalid');expect(j.builderPending).toBeDefined();
  const row=await j.builderPending!.prepare(body,()=>true);
  await j.builderPending!.markUnknown(row.command_id,row.request_sha256,()=>true);
  const restarted=await open(1,'https://a.invalid');
  expect((await restarted.builderPending!.pending(()=>true))[0].state).toBe('SENT_UNKNOWN');
  expect(await restarted.outboxRows()).toEqual([]);
  expect(await (await open(2,'https://a.invalid')).builderPending!.pending(()=>true)).toEqual([]);
  expect(await (await open(1,'https://b.invalid')).builderPending!.pending(()=>true)).toEqual([]);
 }finally{mockDb.close();}
});
test('retired builder attachment cannot be revived by a fresh callback',async()=>{
 mockDb=new DatabaseSync(':memory:');try{
  let active=true;const j=await openJournal('owned',{builderOwner:{ownerId:1,backendScope:'https://a.invalid',sha256:hash,current:()=>active}});
  expect(j.builderPending).toBeDefined();await j.builderPending!.prepare(body,()=>true);active=false;
  await expect(j.builderPending!.pending(()=>true)).rejects.toThrow('stale_identity');
  expect(mockDb.prepare('SELECT state FROM program_builder_pending_commands_v1').get()).toMatchObject({state:'PREPARED'});
 }finally{mockDb.close();}
});
