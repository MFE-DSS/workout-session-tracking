import { DatabaseSync } from 'node:sqlite';
import {mkdtempSync,rmSync} from 'node:fs';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
import {attachPlanV3Journal} from './planV3Journal';
import {createSerialQueue} from './serial';
import type {PlanV3Stored,PlanV3SetOperation,PlanV3SetCommand} from '../domain/planV3Types';

function fixture(){
 const dir=mkdtempSync(join(tmpdir(),'auren-plan-journal-')),path=join(dir,'owned.db');let connection=new DatabaseSync(path);
 function port(){const db=connection;const p:any={execAsync:async(sql:string)=>db.exec(sql),
  runAsync:async(sql:string,...args:any[])=>db.prepare(sql).run(...args),
  getFirstAsync:async(sql:string,...args:any[])=>db.prepare(sql).get(...args)??null,
  getAllAsync:async(sql:string,...args:any[])=>db.prepare(sql).all(...args),
  withExclusiveTransactionAsync:async(fn:(tx:any)=>Promise<void>)=>{db.exec('BEGIN IMMEDIATE');try{await fn(p);db.exec('COMMIT');}catch(error){db.exec('ROLLBACK');throw error;}}};return p;}
 connection.exec("CREATE TABLE active_session(id INTEGER PRIMARY KEY,snapshot TEXT NOT NULL,updated_at_ms INTEGER NOT NULL);CREATE TABLE outbox(op_id TEXT PRIMARY KEY,kind TEXT,target TEXT,payload TEXT,created_at_ms INTEGER,attempts INTEGER,state TEXT);");
 return {port,reopen:()=>{connection.close();connection=new DatabaseSync(path);},close:()=>{connection.close();rmSync(dir,{recursive:true,force:true});}};
}
const initial=():PlanV3Stored=>({profile:'PLAN_V3',local_version:'first-session-local/3.0.0',owner_id:7,phase:'FIRST_USE',intent:null,execution:null,source:{},local_facts:{},drafts:{}});

test('one additive local table, owned snapshot survives a real SQLite close/reopen',async()=>{
 const db=fixture();try{
  let journal=await attachPlanV3Journal(db.port(),createSerialQueue(),7);
  expect(await journal.claim(initial(),()=>true)).toBe(true);
  db.reopen();journal=await attachPlanV3Journal(db.port(),createSerialQueue(),7);
  expect(await journal.read()).toEqual(initial());
  expect((await db.port().getAllAsync("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")).map((r:any)=>r.name)).toEqual(['active_session','journal_v3_set_operations','outbox']);
 }finally{db.close();}
});
test('a live unresolved V1 session or another owner is never overwritten',async()=>{
 const db=fixture();try{
  const p=db.port();await p.runAsync('INSERT INTO active_session VALUES(1,?,?)',JSON.stringify({phase:'SET',plan:{session_id:12}}),1);
  const journal=await attachPlanV3Journal(p,createSerialQueue(),7);
  expect(await journal.claim(initial(),()=>true)).toBe(false);
  expect(JSON.parse((await p.getFirstAsync('SELECT snapshot FROM active_session')).snapshot).phase).toBe('SET');
  await expect(journal.save({...initial(),owner_id:8},()=>true)).rejects.toThrow('journal_owner_mismatch');
 }finally{db.close();}
});
test('an identity switch during a write rolls back the entire native transaction',async()=>{
 const db=fixture();try{
  const p=db.port(),journal=await attachPlanV3Journal(p,createSerialQueue(),7);let current=true;
  await journal.claim(initial(),()=>true);
  const run=p.runAsync;p.runAsync=async(...args:any[])=>{const result=await run(...args);current=false;return result;};
  await expect(journal.save({...initial(),phase:'PAUSED'},()=>current)).rejects.toThrow('stale_identity');
  expect((await journal.read())?.phase).toBe('FIRST_USE');
 }finally{db.close();}
});
function setFixture(){
 const fact:any={setting:{kind:'MASS_KG',unit:'kg',value:12},context:{canonical_exercise_id:'g1',context_ref:'c1',equipment_ref:'m1',realization_ref:'r1',load_semantics:'PER_IMPLEMENT',side:'BILATERAL'},reps:9,completed:true,performed_at:'2026-11-08T12:00:00Z'};
 const state=initial();state.phase='ACTIVE';state.execution={session_id:21,exercises:[{se_id:22,sets:[{set_id:23}]}]} as any;
 const op:PlanV3SetOperation={owner_id:7,op_id:'o1',session_id:21,se_id:22,set_id:23,local_revision:1,expected_server_revision:0,fact,performed_at_estimated:false,recorded_at_ms:100};
 const command:PlanV3SetCommand={op_id:'o1',kind:'PLAN_V3_SET',target:'set/23',payload:{session_id:21,set_id:23,op_id:'o1',expected_set_revision:0,observation:fact}};
 const next={...state,local_facts:{'23':{op_id:'o1',fact,local_revision:1,expected_server_revision:0,sync:'saved_local' as const}}};return {state,op,command,next};
}
test('typed fact, outbox and instrument are atomic and exact old replay cannot undo a correction',async()=>{
 const db=fixture();try{
  const j=await attachPlanV3Journal(db.port(),createSerialQueue(),7),f=setFixture();await j.claim(f.state,()=>true);
  await j.commitSet(f.op,f.command,f.next,()=>true);
  const fact2={...f.op.fact,reps:10};const op2={...f.op,op_id:'o2',local_revision:2,expected_server_revision:1,fact:fact2,recorded_at_ms:50};
  const c2={...f.command,op_id:'o2',payload:{...f.command.payload,op_id:'o2',expected_set_revision:1,observation:fact2}};
  const s2={...f.next,local_facts:{'23':{...f.next.local_facts['23'],op_id:'o2',fact:fact2,local_revision:2,expected_server_revision:1}}};
  await j.commitSet(op2,c2,s2,()=>true);await j.commitSet(f.op,f.command,f.next,()=>true);await j.acknowledge('o1',()=>true);
  expect((await j.read())?.local_facts['23']).toEqual(s2.local_facts['23']);
  await expect(j.commitSet({...f.op,fact:fact2},{...f.command,payload:{...f.command.payload,observation:fact2}},f.next,()=>true)).rejects.toThrow('idempotency_mismatch');
  db.reopen();const read=await attachPlanV3Journal(db.port(),createSerialQueue(),7);
  expect((await read.read())?.local_facts['23'].fact.context.load_semantics).toBe('PER_IMPLEMENT');
  expect((await db.port().getAllAsync('SELECT op_id FROM outbox ORDER BY rowid')).map((r:any)=>r.op_id)).toEqual(['o1','o2']);
 }finally{db.close();}
});
test('injected outbox failure commits neither typed fact nor instrument change',async()=>{
 const db=fixture();try{
  const p=db.port(),j=await attachPlanV3Journal(p,createSerialQueue(),7),f=setFixture();await j.claim(f.state,()=>true);
  const original=p.runAsync;p.runAsync=async(sql:string,...args:any[])=>{if(sql.startsWith('INSERT INTO outbox'))throw Error('injected_disk_error');return original(sql,...args);};
  await expect(j.commitSet(f.op,f.command,f.next,()=>true)).rejects.toThrow('injected_disk_error');
  expect(await p.getAllAsync('SELECT * FROM journal_v3_set_operations')).toEqual([]);
  expect(await p.getAllAsync('SELECT * FROM outbox')).toEqual([]);expect((await j.read())?.local_facts).toEqual({});
 }finally{db.close();}
});

test('a stale controller snapshot cannot erase an ack written during a network await',async()=>{
 const db=fixture();try{
  const j=await attachPlanV3Journal(db.port(),createSerialQueue(),7),f=setFixture();await j.claim(f.state,()=>true);await j.commitSet(f.op,f.command,f.next,()=>true);
  await j.acknowledge('o1',()=>true);await j.save({...f.next,phase:'PAUSED'},()=>true);
  expect((await j.read())?.local_facts['23'].sync).toBe('acked');
 }finally{db.close();}
});
test('close command shares the typed fact FIFO and preserves the owned V3 snapshot',async()=>{
 const db=fixture();try{
  const p=db.port(),j=await attachPlanV3Journal(p,createSerialQueue(),7),f=setFixture();await j.claim(f.state,()=>true);await j.commitSet(f.op,f.command,f.next,()=>true);
  await j.enqueueClose('close-op','SESSION_FINISH',f.op.session_id,{...f.next,phase:'COMPLETE'},()=>true);
  expect((await p.getAllAsync('SELECT kind FROM outbox ORDER BY rowid')).map((r:any)=>r.kind)).toEqual(['PLAN_V3_SET','SESSION_FINISH']);
  expect((await j.read())?.phase).toBe('COMPLETE');
 }finally{db.close();}
});
test('explicit server-version resolution preserves refused immutable facts and unblocks pending closure without a false ack',async()=>{
 const db=fixture();try{
  const p=db.port(),j=await attachPlanV3Journal(p,createSerialQueue(),7),f=setFixture();
  await j.claim(f.state,()=>true);await j.commitSet(f.op,f.command,f.next,()=>true);
  await p.runAsync("UPDATE outbox SET state='failed' WHERE op_id='o1'");
  await (j as any).reject('o1',()=>true);
  expect((await j.read())?.local_facts['23'].sync).toBe('failed');
  await j.enqueueClose('close','SESSION_FINISH',21,{...f.next,phase:'COMPLETE'},()=>true);
  const old=(await p.getFirstAsync("SELECT fact_json FROM journal_v3_set_operations WHERE op_id='o1'")).fact_json;
  const server:any={...f.state.execution,status:'in_progress',exercises:[{se_id:22,sets:[{set_id:23,revision:2,completed:false,observation:null}]}]};
  await (j as any).resolveRefusal(23,server,()=>true);
  expect((await p.getFirstAsync("SELECT state FROM outbox WHERE op_id='o1'")).state).toBe('resolved');
  expect((await p.getFirstAsync("SELECT state FROM outbox WHERE op_id='close'")).state).toBe('pending');
  expect((await p.getFirstAsync("SELECT fact_json FROM journal_v3_set_operations WHERE op_id='o1'")).fact_json).toBe(old);
  expect((await j.read())?.local_facts['23'].sync).toBe('resolved');
  expect((await (j as any).history(21))[0]).toMatchObject({op_id:'o1',state:'resolved',fact:f.op.fact});
  db.reopen();const restored=await attachPlanV3Journal(db.port(),createSerialQueue(),7);
  expect((await restored.read())?.local_facts['23'].sync).toBe('resolved');
 }finally{db.close();}
});
