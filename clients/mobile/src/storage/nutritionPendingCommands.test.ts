import {DatabaseSync} from 'node:sqlite';
import {createHash} from 'node:crypto';
import {mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {attachNutritionPending} from './nutritionPendingCommands';
import {createSerialQueue} from './serial';
import {NutritionRecovery} from '../sync/nutritionRecovery';
import {nutritionCommand} from '../domain/nutritionCommand';

const scope='https://qa.invalid',hash=async(s:string)=>createHash('sha256').update(s).digest('hex');
const input=(request_id='one')=>nutritionCommand('DAY','/me/nutrition/days/2026-11-12/revisions',{contract_version:'nutrition-command/1.0.0',request_id,expected_head_token:'0'.repeat(64),operation:'SET_FIELDS',values:{kcal_milli:0},timezone:'Europe/Paris',target_ref:null,confirm_complete:null});
function fixture(){
 const dir=mkdtempSync(join(tmpdir(),'auren-nut-')),path=join(dir,'owned.db');let db=new DatabaseSync(path);
 const port=()=>{const c=db;const p:any={execAsync:async(s:string)=>c.exec(s),runAsync:async(s:string,...a:any[])=>c.prepare(s).run(...a),getFirstAsync:async(s:string,...a:any[])=>c.prepare(s).get(...a)??null,getAllAsync:async(s:string,...a:any[])=>c.prepare(s).all(...a),withExclusiveTransactionAsync:async(f:any)=>{c.exec('BEGIN IMMEDIATE');try{await f(p);c.exec('COMMIT');}catch(e){c.exec('ROLLBACK');throw e;}}};return p;};
 return {port,reopen:()=>{db.close();db=new DatabaseSync(path);},close:()=>{db.close();rmSync(dir,{recursive:true,force:true});}};
}
const receipt=(c:any)=>({contract_version:'nutrition-operation/1.0.0',owner_id:7,namespace:'DAY',request_id:c.request_id,command_digest:c.body_digest,state:'APPLIED',entity_ref:1,applied_revision:1,recorded_at:'2026-11-12T00:00:00Z'});
const client=(submit:any)=>({ownerId:7,backendScope:scope,consent:async()=>({state:'confirmed',value:{granted:true,wording_version:1,current_wording_version:1}}),submit,status:async()=>({state:'unknown'})} as any);
test('disk restart preserves bytes and unknown state, separating account/backend/namespace',async()=>{
 const d=fixture();try{
  let store=await attachNutritionPending(d.port(),createSerialQueue(),7,scope,hash);
  const sent:any[]=[];let online=false;
  const c=client(async(command:any)=>{sent.push(command);return online?{state:'confirmed',value:receipt(command)}:{state:'unknown'};});
  const r=new NutritionRecovery(c,store,()=>true);expect((await r.send(input())).state).toBe('unknown');
  await expect(r.send(input())).rejects.toThrow('nutrition_verification_required');expect(sent).toHaveLength(1);
  d.reopen();store=await attachNutritionPending(d.port(),createSerialQueue(),7,scope,hash);
  const pending=(await store.pending())[0];expect(pending.payload_json).toBe(input().payload_json);
  const restored=new NutritionRecovery(c,store,()=>true);
  await expect(restored.replay(pending)).rejects.toThrow('nutrition_verification_required');
  await restored.verify(pending);online=true;await restored.replay(pending);
  expect(sent[1]).toEqual(sent[0]);expect(await store.pending()).toEqual([]);
  expect((await store.read('DAY','one'))?.state).toBe('ACKED');
  expect(await(await attachNutritionPending(d.port(),createSerialQueue(),8,scope,hash)).read('DAY','one')).toBeNull();
  expect(await(await attachNutritionPending(d.port(),createSerialQueue(),7,'https://other.invalid',hash)).read('DAY','one')).toBeNull();
  expect(await store.read('TARGET','one')).toBeNull();
 }finally{d.close();}
});
test('real SQLite write failure and changed account roll back before mutation HTTP',async()=>{
 const d=fixture();try{
  const p=d.port(),store=await attachNutritionPending(p,createSerialQueue(),7,scope,hash),run=p.runAsync;
  p.runAsync=async(sql:string,...args:any[])=>{if(sql.startsWith('INSERT INTO nutrition_pending'))throw Error('disk_full');return run(sql,...args);};
  const c=client(jest.fn());await expect(new NutritionRecovery(c,store,()=>true).send(input())).rejects.toThrow('disk_full');
  expect(c.submit).not.toHaveBeenCalled();expect(await store.pending()).toEqual([]);
  await expect(store.prepare(input(),()=>false)).rejects.toThrow('stale_identity');
 }finally{d.close();}
});
test('late response or foreign receipt never closes the owned command',async()=>{
 const d=fixture();try{
  const store=await attachNutritionPending(d.port(),createSerialQueue(),7,scope,hash);let current=true;
  const c=client(async(command:any)=>{current=false;return{state:'confirmed',value:receipt(command)};});
  expect(await new NutritionRecovery(c,store,()=>current).send(input())).toEqual({state:'cancelled'});
  const pending=(await store.pending())[0];expect(pending.state).toBe('SENT_UNKNOWN');
  await expect(store.ack('DAY','one',{...receipt(pending),command_digest:'0'.repeat(64)} as any,()=>true)).rejects.toThrow('nutrition_receipt_mismatch');
  expect((await store.pending())[0].state).toBe('SENT_UNKNOWN');
 }finally{d.close();}
});
test('consent withdrawn after local prepare stops fresh HTTP without losing pending work',async()=>{
 const d=fixture();try{
  const store=await attachNutritionPending(d.port(),createSerialQueue(),7,scope,hash),c=client(jest.fn());let grants=0;
  c.consent=async()=>({state:'confirmed',value:{granted:++grants===1,wording_version:1,current_wording_version:1}});
  expect(await new NutritionRecovery(c,store,()=>true).send(input())).toEqual({state:'consent_required'});
  expect(c.submit).not.toHaveBeenCalled();expect((await store.pending())[0].state).toBe('PREPARED');
 }finally{d.close();}
});
test('lookup or replay refusal cannot certify that a previous unknown command never applied',async()=>{
 const d=fixture();try{
  const store=await attachNutritionPending(d.port(),createSerialQueue(),7,scope,hash),c=client(async()=>({state:'unknown'}));
  const recovery=new NutritionRecovery(c,store,()=>true);await recovery.send(input());
  const command=(await store.pending())[0];
  c.status=async()=>({state:'rejected',status:406,code:'unsupported_contract'});
  expect((await recovery.verify(command)).state).toBe('rejected');
  expect((await store.pending())[0].state).toBe('SENT_UNKNOWN');
  await expect(store.prepare(input('another-key'),()=>true)).rejects.toThrow('nutrition_pending_conflict');
  c.status=async()=>({state:'unknown'});await recovery.verify(command);
  c.submit=async()=>({state:'rejected',status:406,code:'unsupported_contract'});await recovery.replay(command);
  expect((await store.pending())[0].state).toBe('SENT_UNKNOWN');
  c.status=async()=>({state:'confirmed',value:receipt(command)});await recovery.verify(command);
  expect(await store.pending()).toEqual([]);
 }finally{d.close();}
});
test.each(['DAY','TARGET'] as const)('two %s recovery instances share one atomic initial-POST claim',async namespace=>{
 const d=fixture();try{
  const store=await attachNutritionPending(d.port(),createSerialQueue(),7,scope,hash),c=client(jest.fn(async()=>({state:'unknown'})));
  const request=namespace==='DAY'?input():nutritionCommand('TARGET','/me/nutrition/targets/revisions',{
   contract_version:'nutrition-command/1.0.0',request_id:'target-one',expected_head_token:'0'.repeat(64),operation:'SET_FIELDS',values:{kcal_milli:2200000},variant:'STANDARD',effective_from:'2026-11-12',
  });
  const results=await Promise.allSettled([new NutritionRecovery(c,store,()=>true).send(request),new NutritionRecovery(c,store,()=>true).send(request)]);
  expect(c.submit).toHaveBeenCalledTimes(1);expect(results.filter(r=>r.status==='rejected')).toHaveLength(1);
  d.reopen();const restored=await attachNutritionPending(d.port(),createSerialQueue(),7,scope,hash);
  expect((await restored.pending())[0]).toMatchObject({namespace,state:'SENT_UNKNOWN',payload_json:request.payload_json});
 }finally{d.close();}
});
