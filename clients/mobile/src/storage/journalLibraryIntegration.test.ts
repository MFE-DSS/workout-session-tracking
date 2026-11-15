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
import witness from '../../test/libraryWitness.json';
const hash=async(s:string)=>createHash('sha256').update(s).digest('hex');
const id='d477ea9f-7bd9-4fc4-a679-c50f86a2ad41';
const input={local_id:id,source_ref:witness.created.source_ref,selection_ref:witness.request.selection_ref,created_at_ms:1};
test('owned shared journal attaches a durable backend-partitioned library intention, not a sync outbox command',async()=>{
 mockDb=new DatabaseSync(':memory:');try{
 const open=(ownerId:number,backendScope:string,current=()=>true)=>openJournal('owned',{libraryOwner:{ownerId,backendScope,sha256:hash,current}});
 const a=await open(1,'https://a.invalid');expect(a.library).toBeDefined();
 await a.library!.prepare(input,()=>true);await a.library!.markSent(id,await hash(JSON.stringify(witness.request)),()=>true);
 const restarted=await open(1,'https://a.invalid');expect((await restarted.library!.unresolved(()=>true))?.state).toBe('SENT_UNKNOWN');
 expect(await restarted.outboxRows()).toEqual([]);
 expect(await (await open(2,'https://a.invalid')).library!.unresolved(()=>true)).toBeNull();
 expect(await (await open(1,'https://b.invalid')).library!.unresolved(()=>true)).toBeNull();
 }finally{mockDb.close();}
});
test('retired journal attachment rejects even a fresh callback and preserves its original intention',async()=>{
 mockDb=new DatabaseSync(':memory:');try{
 let active=true;const j=await openJournal('owned',{libraryOwner:{ownerId:1,backendScope:'https://a.invalid',sha256:hash,current:()=>active}});
 await j.library!.prepare(input,()=>true);active=false;
 await expect(j.library!.resolve(id,'INTENTION_CANCELLED',null,()=>true)).rejects.toThrow('stale_identity');
 expect(mockDb.prepare('SELECT state FROM library_pending_openings_v1').get()).toMatchObject({state:'PREPARED'});
 }finally{mockDb.close();}
});
