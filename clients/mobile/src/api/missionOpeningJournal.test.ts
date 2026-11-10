import {DatabaseSync} from 'node:sqlite';
import {mkdtempSync,rmSync} from 'node:fs';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
let mockDb:DatabaseSync;
jest.mock('expo-sqlite',()=>({openDatabaseAsync:async()=>{
 const handle:any={execAsync:async(sql:string)=>mockDb.exec(sql),runAsync:async(sql:string,...args:any[])=>mockDb.prepare(sql).run(...(Array.isArray(args[0])?args[0]:args)),
 getFirstAsync:async(sql:string,...args:any[])=>mockDb.prepare(sql).get(...(Array.isArray(args[0])?args[0]:args))??null,
 getAllAsync:async(sql:string,...args:any[])=>mockDb.prepare(sql).all(...(Array.isArray(args[0])?args[0]:args)),
 withExclusiveTransactionAsync:async(fn:any)=>{mockDb.exec('BEGIN IMMEDIATE');try{await fn(handle);mockDb.exec('COMMIT');}catch(e){mockDb.exec('ROLLBACK');throw e;}}};return handle;
}}));
import {openJournal} from '../storage/journal';
import {initialState} from '../domain/workout';
import {FirstUseV3Controller} from './firstUseV3';
import {markLegacyStart,legacyStartMarker,restoreExistingV3} from './missionOpening';
const controller=(journal:any)=>new FirstUseV3Controller({ownerId:7,journal,current:()=>true,newId:()=> 'unused'} as any,()=>{});
test('real SQL guard accepts legacy after untouched V3 bootstrap and protects an existing V3 draft',async()=>{
 mockDb=new DatabaseSync(':memory:');try{
  const journal=await openJournal('owned',{planV3OwnerId:7}),c=controller(journal.planV3);
  await restoreExistingV3(c,journal.planV3!);expect(c.state).toBeNull();
  const legacy={...initialState,phase:'SET',plan:{session_id:31}} as any;
  await journal.beginLegacy!(legacy,()=>true);expect((await journal.restore()).snapshot?.plan?.session_id).toBe(31);
  await journal.saveSnapshot(initialState);await c.restore();expect(c.state?.profile).toBe('PLAN_V3');
  const again=controller(journal.planV3);await restoreExistingV3(again,journal.planV3!);
  expect(again.state?.owner_id).toBe(7);await expect(journal.beginLegacy!(legacy,()=>true)).rejects.toThrow('active_session_conflict');
 }finally{mockDb.close();}
});
test('legacy start uncertainty survives actual SQLite close/reopen in the original snapshot',async()=>{
 const dir=mkdtempSync(join(tmpdir(),'auren-mob04-opening-')),file=join(dir,'owned.db');mockDb=new DatabaseSync(file);
 try{
  const journal=await openJournal('owned',{planV3OwnerId:7});await journal.saveSnapshot(markLegacyStart(initialState,'server-template',123));mockDb.close();mockDb=new DatabaseSync(file);
  const reopened=await openJournal('owned',{planV3OwnerId:7});expect(legacyStartMarker((await reopened.restore()).snapshot)?.template_slug).toBe('server-template');
  const c=controller(reopened.planV3);await restoreExistingV3(c,reopened.planV3!);expect(legacyStartMarker((await reopened.restore()).snapshot)).not.toBeNull();
 }finally{mockDb.close();rmSync(dir,{recursive:true});}
});
