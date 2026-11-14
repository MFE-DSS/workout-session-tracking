import {DatabaseSync} from 'node:sqlite';
import {createHash} from 'node:crypto';
import {mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {attachBodyPending,type BodyPendingCommands} from './bodyPendingCommands';
import {createSerialQueue} from './serial';
import {BodyCommandRecovery} from '../sync/bodyCommandRecovery';

const scope='https://qa.invalid',hash=async(s:string)=>createHash('sha256').update(s).digest('hex');
const input=(key='create-1')=>({method:'POST' as const,path:'/me/body/measurements',request_id:key,payload_json:JSON.stringify({request_id:key,measured_on:'2026-11-11',values:{weight_kg:72}})});
function fixture(){
 const dir=mkdtempSync(join(tmpdir(),'auren-body-')),path=join(dir,'owned.db');let db=new DatabaseSync(path);
 const port=()=>{const c=db;const p:any={execAsync:async(s:string)=>c.exec(s),runAsync:async(s:string,...a:any[])=>c.prepare(s).run(...a),getFirstAsync:async(s:string,...a:any[])=>c.prepare(s).get(...a)??null,getAllAsync:async(s:string,...a:any[])=>c.prepare(s).all(...a),withExclusiveTransactionAsync:async(f:any)=>{c.exec('BEGIN IMMEDIATE');try{await f(p);c.exec('COMMIT');}catch(e){c.exec('ROLLBACK');throw e;}}};return p;};
 return {port,reopen:()=>{db.close();db=new DatabaseSync(path);},close:()=>{db.close();rmSync(dir,{recursive:true,force:true});}};
}
const receipt=(c:any)=>({contract_version:'body-operation/1.0.0',owner_id:7,command_digest:c.body_digest,request_id:c.request_id,operation:'CREATE',root_ref:11,measurement_id:11,applied_revision:1,recorded_at:'2026-11-11T12:00:00Z',state:'APPLIED'});
test('exact payload survives disk close/reopen, scoped to owner and backend',async()=>{
 const d=fixture();try{
  let j=await attachBodyPending(d.port(),createSerialQueue(),7,scope,hash);
  const c=await j.prepare(input(),()=>true);await j.markUnknown(c.request_id,()=>true);d.reopen();
  j=await attachBodyPending(d.port(),createSerialQueue(),7,scope,hash);
  expect((await j.pending())[0]).toMatchObject({...c,state:'SENT_UNKNOWN'});
  expect(await(await attachBodyPending(d.port(),createSerialQueue(),8,scope,hash)).pending()).toEqual([]);
  expect(await(await attachBodyPending(d.port(),createSerialQueue(),7,'https://other.invalid',hash)).pending()).toEqual([]);
  await expect(j.prepare(input('new-key'),()=>true)).rejects.toThrow('body_pending_conflict');
  await expect(j.prepare({...input(),payload_json:input().payload_json.replace('72','73')},()=>true)).rejects.toThrow('idempotency_mismatch');
 }finally{d.close();}
});
test('failure before durable prepare sends no HTTP; stale identity rolls back',async()=>{
 const client:any={ownerId:7,backendScope:scope,consent:async()=>({state:'confirmed',value:{granted:true}}),submit:jest.fn()};
 const broken={read:async()=>null,prepare:async()=>{throw Error('disk_full');}} as unknown as BodyPendingCommands;
 const recovery=new BodyCommandRecovery(client,broken,()=>true);
 await expect(recovery.send(input())).rejects.toThrow('disk_full');expect(client.submit).not.toHaveBeenCalled();
 const d=fixture();try{const j=await attachBodyPending(d.port(),createSerialQueue(),7,scope,hash);await expect(j.prepare(input(),()=>false)).rejects.toThrow('stale_identity');expect(await j.pending()).toEqual([]);}finally{d.close();}
});
test('response loss requires verify then explicit same-command replay, and ack survives restart',async()=>{
 const d=fixture();try{
  const j=await attachBodyPending(d.port(),createSerialQueue(),7,scope,hash);
  let delivered=false;const submitted:any[]=[];
  const client:any={ownerId:7,backendScope:scope,consent:async()=>({state:'confirmed',value:{granted:true}}),submit:async(c:any)=>{submitted.push(c);return delivered?{state:'confirmed',value:receipt(c)}:{state:'unknown'};},status:async()=>({state:'unknown'})};
  const r=new BodyCommandRecovery(client,j,()=>true);expect((await r.send(input())).state).toBe('unknown');
  const c=(await j.pending())[0];await expect(r.replay(c)).rejects.toThrow('body_verification_required');
  await r.verify(c);expect(submitted).toHaveLength(1);delivered=true;await r.replay(c);
  expect(submitted[1]).toEqual(submitted[0]);expect(await j.pending()).toEqual([]);d.reopen();
  const restored=await attachBodyPending(d.port(),createSerialQueue(),7,scope,hash);expect((await restored.read(c.request_id))?.state).toBe('ACKED');
 }finally{d.close();}
});
test('late account response cannot acknowledge, and receipt mismatch never closes the command',async()=>{
 const d=fixture();try{
  const j=await attachBodyPending(d.port(),createSerialQueue(),7,scope,hash);let current=true;
  const client:any={ownerId:7,backendScope:scope,consent:async()=>({state:'confirmed',value:{granted:true}}),submit:async(c:any)=>{current=false;return{state:'confirmed',value:receipt(c)};}};
  const r=new BodyCommandRecovery(client,j,()=>current);expect((await r.send(input())).state).toBe('cancelled');
  const c=(await j.pending())[0];expect(c.state).toBe('SENT_UNKNOWN');
  await expect(j.ack(c.request_id,{...receipt(c),command_digest:'b'.repeat(64)} as any,()=>true)).rejects.toThrow('body_receipt_mismatch');
  expect((await j.pending())[0].state).toBe('SENT_UNKNOWN');
 }finally{d.close();}
});
test('a real SQLite transaction failure before commit leaves no command and makes no HTTP call',async()=>{
 const d=fixture();try{
  const p=d.port(),j=await attachBodyPending(p,createSerialQueue(),7,scope,hash),run=p.runAsync;
  p.runAsync=async(sql:string,...args:any[])=>{if(sql.startsWith('INSERT INTO body_pending'))throw Error('disk_full');return run(sql,...args);};
  const client:any={ownerId:7,backendScope:scope,consent:async()=>({state:'confirmed',value:{granted:true}}),submit:jest.fn()};
  await expect(new BodyCommandRecovery(client,j,()=>true).send(input())).rejects.toThrow('disk_full');expect(client.submit).not.toHaveBeenCalled();expect(await j.pending()).toEqual([]);
 }finally{d.close();}
});

test('send cannot repeat an unknown command after disk reopen; terminal commands do not POST again',async()=>{
 const d=fixture();try{
  let j=await attachBodyPending(d.port(),createSerialQueue(),7,scope,hash);
  const client:any={ownerId:7,backendScope:scope,consent:async()=>({state:'confirmed',value:{granted:true}}),submit:jest.fn(async()=>({state:'unknown'}))};
  await new BodyCommandRecovery(client,j,()=>true).send(input());d.reopen();
  j=await attachBodyPending(d.port(),createSerialQueue(),7,scope,hash);
  const r=new BodyCommandRecovery(client,j,()=>true);
  await expect(r.send(input())).rejects.toThrow('body_verification_required');
  expect(client.submit).toHaveBeenCalledTimes(1);
  const c=(await j.pending())[0];await j.ack(c.request_id,receipt(c) as any,()=>true);
  expect(await r.send(input())).toEqual({state:'confirmed',value:receipt(c)});
  expect(client.submit).toHaveBeenCalledTimes(1);
 }finally{d.close();}
});
test.each(['verify','replay'] as const)('%s refusal cannot turn a previously unknown mutation into a rejected fact',async method=>{
 const d=fixture();try{
  let j=await attachBodyPending(d.port(),createSerialQueue(),7,scope,hash);
  const c=await j.prepare(input(),()=>true);await j.markUnknown(c.request_id,()=>true);
  const client:any={ownerId:7,backendScope:scope,status:jest.fn(async()=>({state:'unknown'})),submit:jest.fn(async()=>({state:'rejected',status:422,code:'current_contract_refusal'}))};
  const r=new BodyCommandRecovery(client,j,()=>true);
  if(method==='verify')client.status.mockResolvedValue({state:'consent_required'});
  else await r.verify(c);
  await r[method](c);d.reopen();j=await attachBodyPending(d.port(),createSerialQueue(),7,scope,hash);
  expect((await j.read(c.request_id))?.state).toBe('SENT_UNKNOWN');
  client.status.mockResolvedValue({state:'confirmed',value:receipt(c)});
  expect((await new BodyCommandRecovery(client,j,()=>true).verify(c)).state).toBe('confirmed');
  expect((await j.read(c.request_id))?.state).toBe('ACKED');
 }finally{d.close();}
});
test('verification of an acknowledged or rejected command is local and cannot change its terminal state',async()=>{
 const d=fixture();try{
  const j=await attachBodyPending(d.port(),createSerialQueue(),7,scope,hash),client:any={ownerId:7,backendScope:scope,status:jest.fn(async()=>({state:'unknown'})),submit:jest.fn(),consent:async()=>({state:'confirmed',value:{granted:true}})};
  const c=await j.prepare(input(),()=>true);await j.ack(c.request_id,receipt(c) as any,()=>true);
  const r=new BodyCommandRecovery(client,j,()=>true);
  expect((await r.verify(c)).state).toBe('confirmed');expect(client.status).not.toHaveBeenCalled();
  const rejected=await j.prepare(input('rejected-command'),()=>true);await j.reject(rejected.request_id,'head_conflict',()=>true);
  expect((await r.send(input('rejected-command'))).state).toBe('rejected');
  expect((await r.verify(rejected)).state).toBe('rejected');expect(client.status).not.toHaveBeenCalled();expect(client.submit).not.toHaveBeenCalled();
 }finally{d.close();}
});
test('two recovery instances cannot claim the same initial POST twice',async()=>{
 const d=fixture();try{
  const j=await attachBodyPending(d.port(),createSerialQueue(),7,scope,hash);
  const client:any={ownerId:7,backendScope:scope,consent:async()=>({state:'confirmed',value:{granted:true}}),submit:jest.fn(async()=>({state:'unknown'}))};
  const results=await Promise.allSettled([new BodyCommandRecovery(client,j,()=>true).send(input()),new BodyCommandRecovery(client,j,()=>true).send(input())]);
  expect(client.submit).toHaveBeenCalledTimes(1);expect(results.filter(r=>r.status==='rejected')).toHaveLength(1);
  expect((await j.pending())[0].state).toBe('SENT_UNKNOWN');
 }finally{d.close();}
});
test('an exact local acknowledged receipt survives withdrawal without regrant or network',async()=>{
 const d=fixture();try{
  const j=await attachBodyPending(d.port(),createSerialQueue(),7,scope,hash),c=await j.prepare(input(),()=>true);await j.ack(c.request_id,receipt(c) as any,()=>true);
  const client:any={ownerId:7,backendScope:scope,consent:jest.fn(async()=>({state:'confirmed',value:{granted:false}})),submit:jest.fn()};
  expect(await new BodyCommandRecovery(client,j,()=>true).send(input())).toEqual({state:'confirmed',value:receipt(c)});
  expect(client.submit).not.toHaveBeenCalled();expect(client.consent).not.toHaveBeenCalled();
 }finally{d.close();}
});
test('a direct fresh refusal is terminal but cannot be submitted again',async()=>{
 const d=fixture();try{
  const j=await attachBodyPending(d.port(),createSerialQueue(),7,scope,hash);
  const c:any={ownerId:7,backendScope:scope,consent:async()=>({state:'confirmed',value:{granted:true}}),submit:jest.fn(async()=>({state:'rejected',status:422,code:'invalid_fresh_value'}))};
  const r=new BodyCommandRecovery(c,j,()=>true);expect((await r.send(input())).state).toBe('rejected');
  expect((await j.read('create-1'))?.state).toBe('REJECTED');expect((await r.send(input())).state).toBe('rejected');expect(c.submit).toHaveBeenCalledTimes(1);
 }finally{d.close();}
});
