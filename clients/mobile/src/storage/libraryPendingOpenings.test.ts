import {createHash} from 'node:crypto';
import witness from '../../test/libraryWitness.json';
import {SqliteFile} from '../../test/sqliteFile';
import {createSerialQueue} from './serial';
import {attachLibraryPendingOpenings,type LibraryOpening} from './libraryPendingOpenings';
import {libraryStartJSON} from '../api/library';
const hash=async(raw:string)=>createHash('sha256').update(raw).digest('hex');
const backend='https://qa.test.invalid';
const localId='d477ea9f-7bd9-4fc4-a679-c50f86a2ad41';
const input=()=>({local_id:localId,source_ref:witness.created.source_ref,selection_ref:witness.request.selection_ref,created_at_ms:1000});
let file:SqliteFile;
beforeEach(()=>{file=new SqliteFile();});
afterEach(()=>file.close());
const port=()=>{
 const p:any={...file.port(),getAllAsync:async<T,>(sql:string,...args:any[])=>file.db.prepare(sql).all(...args) as T[]};
 p.withExclusiveTransactionAsync=async(action:(tx:any)=>Promise<void>)=>{
  file.db.exec('BEGIN IMMEDIATE');try{await action(p);file.db.exec('COMMIT');}catch(e){file.db.exec('ROLLBACK');throw e;}
 };return p;
};
const attach=(owner=witness.page.owner_id,scope=backend,current=()=>true)=>attachLibraryPendingOpenings(port(),createSerialQueue(),owner,scope,hash,current);

test('exact intention survives real SQLite close/reopen and unrelated Legacy/V3 snapshot replacement',async()=>{
 let s=await attach();const p=await s.prepare(input(),()=>true);
 expect(p.state).toBe('PREPARED');expect(p.payload_json).toBe(libraryStartJSON(witness.request.selection_ref));
 await s.markSent(localId,p.digest,()=>true);
 file.db.exec("CREATE TABLE active_session(id INTEGER PRIMARY KEY,snapshot TEXT); INSERT INTO active_session VALUES(1,'{\"profile\":\"PLAN_V3\"}'); UPDATE active_session SET snapshot='{\"phase\":\"COMPLETE\"}' WHERE id=1");
 file.reopen();s=await attach();const restored=await s.unresolved(()=>true);
 expect(restored?.state).toBe('SENT_UNKNOWN');expect(restored?.digest).toBe(witness.created.request_sha256);
 expect(restored?.creation_outcome).toBe('UNKNOWN');
});
test('one unresolved intention per owner/backend without blocking a different account or backend',async()=>{
 const a=await attach();await a.prepare(input(),()=>true);
 await expect(a.prepare({...input(),local_id:'966999bf-fc5f-4c66-baa7-10637423877f'},()=>true)).rejects.toThrow();
 const b=await attach(witness.page.owner_id+1);expect(await b.unresolved(()=>true)).toBeNull();
 await b.prepare(input(),()=>true);expect((await a.unresolved(()=>true))?.owner_id).toBe(witness.page.owner_id);
 const other=await attach(witness.page.owner_id,'https://another.test.invalid');expect(await other.unresolved(()=>true)).toBeNull();
});
test.each(['RESUMED_OWNED','INTENTION_CANCELLED'] as const)('%s never invents an exact creation receipt',async kind=>{
 const s=await attach(),p=await s.prepare(input(),()=>true);await s.markSent(localId,p.digest,()=>true);
 await s.resolve(localId,kind,kind==='RESUMED_OWNED'?{session_id:42,session_profile:'PLAN_V3'}:null,()=>true);
 expect(await s.unresolved(()=>true)).toBeNull();
 const row=await s.get(localId,()=>true);expect(row?.creation_outcome).toBe('UNKNOWN');expect(row?.resolution_kind).toBe(kind);
});
test('corrupted exact body/digest stops recovery instead of silently repairing it',async()=>{
 const s=await attach();await s.prepare(input(),()=>true);
 file.db.prepare('UPDATE library_pending_openings_v1 SET payload_json=? WHERE local_id=?').run('{"selection_ref":"other"}',localId);
 await expect(s.unresolved(()=>true)).rejects.toThrow('invalid_library_intention');
});
test('stale identity rolls back a real local write',async()=>{
 const s=await attach();let n=0;
 await expect(s.prepare(input(),()=>++n<3)).rejects.toThrow('stale_identity');
 expect(await s.unresolved(()=>true)).toBeNull();
});
test('cannot confirm creation before sent or resolve against another owner',async()=>{
 const s=await attach(),p=await s.prepare(input(),()=>true);
 await expect(s.resolve(localId,'CREATED_CONFIRMED',{session_id:41,session_profile:'LEGACY'},()=>true)).rejects.toThrow();
 await s.markSent(localId,p.digest,()=>true);
 const b=await attach(witness.page.owner_id+1);
 await expect(b.resolve(localId,'CREATED_CONFIRMED',{session_id:41,session_profile:'LEGACY'},()=>true)).rejects.toThrow();
 expect((await s.unresolved(()=>true))?.state).toBe('SENT_UNKNOWN');
});
test('recognized refusal records non-creation separately and permits a fresh explicit intention',async()=>{
 const s=await attach(),p=await s.prepare(input(),()=>true);await s.markSent(localId,p.digest,()=>true);
 await s.resolve(localId,'REFUSED_CONFIRMED',null,()=>true);
 expect((await s.get(localId,()=>true))?.creation_outcome).toBe('NOT_CREATED');
 await s.prepare({...input(),local_id:'966999bf-fc5f-4c66-baa7-10637423877f'},()=>true);
 expect((await s.unresolved(()=>true))?.state).toBe('PREPARED');
});

test('review I2: retired attachment rejects every operation even if the operation predicate stays true',async()=>{
 let connected=true;
 const s=await attachLibraryPendingOpenings(port(),createSerialQueue(),witness.page.owner_id,backend,hash,()=>connected);
 const p=await s.prepare(input(),()=>true);connected=false;
 const operations=[()=>s.get(localId,()=>true),()=>s.unresolved(()=>true),()=>s.prepare({...input(),local_id:'966999bf-fc5f-4c66-baa7-10637423877f'},()=>true),()=>s.markSent(localId,p.digest,()=>true),()=>s.resolve(localId,'INTENTION_CANCELLED',null,()=>true)];
 for(const operation of operations)await expect(operation()).rejects.toThrow('stale_identity');
 expect(file.db.prepare('SELECT state FROM library_pending_openings_v1').get().state).toBe('PREPARED');
});
test('review I2: attachment retirement after INSERT rolls back the actual SQLite transaction',async()=>{
 let connected=true,retireOnInsert=false;const db=port(),run=db.runAsync;
 db.runAsync=async(sql:string,...args:any[])=>{const r=await run(sql,...args);if(retireOnInsert&&sql.startsWith('INSERT INTO library_pending_openings'))connected=false;return r;};
 const s=await attachLibraryPendingOpenings(db,createSerialQueue(),witness.page.owner_id,backend,hash,()=>connected);
 retireOnInsert=true;await expect(s.prepare(input(),()=>true)).rejects.toThrow('stale_identity');
 expect(file.db.prepare('SELECT COUNT(*) AS n FROM library_pending_openings_v1').get().n).toBe(0);
});
