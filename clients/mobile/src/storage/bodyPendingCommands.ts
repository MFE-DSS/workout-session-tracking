/** Exact BODY commands only. Canonical measurement history stays on the server. */
import {bodyCommandCanonical,decodeBodyReceipt,type PreparedBodyRequest,type BodyReceipt} from '../api/bodyMeasurements';
import type {PlanSQL} from './planV3Journal';
import type {Serial} from './serial';
export type BodyCommandInput=Pick<PreparedBodyRequest,'method'|'path'|'request_id'|'payload_json'>;
export type PendingBodyCommand=PreparedBodyRequest&{state:'PREPARED'|'SENT_UNKNOWN'|'ACKED'|'REJECTED';receipt:BodyReceipt|null;rejection:string|null;created_at_ms:number};
export interface BodyPendingCommands{
 prepare(input:BodyCommandInput,current:()=>boolean):Promise<PendingBodyCommand>;
 pending():Promise<PendingBodyCommand[]>;
 read(key:string):Promise<PendingBodyCommand|null>;
 markUnknown(key:string,current:()=>boolean,initialOnly?:boolean):Promise<void>;
 ack(key:string,receipt:BodyReceipt,current:()=>boolean):Promise<void>;
 reject(key:string,code:string,current:()=>boolean):Promise<void>;
}
const SCHEMA=`CREATE TABLE IF NOT EXISTS body_pending_commands_v1(
 owner_id INTEGER NOT NULL,backend_scope TEXT NOT NULL,request_id TEXT NOT NULL,
 local_version INTEGER NOT NULL CHECK(local_version=1),namespace TEXT NOT NULL CHECK(namespace='BODY'),
 logical_key TEXT NOT NULL,method TEXT NOT NULL CHECK(method='POST'),path TEXT NOT NULL,
 payload_json TEXT NOT NULL,body_digest TEXT NOT NULL,state TEXT NOT NULL CHECK(state IN ('PREPARED','SENT_UNKNOWN','ACKED','REJECTED')),
 receipt_json TEXT,rejection TEXT,created_at_ms INTEGER NOT NULL,PRIMARY KEY(owner_id,backend_scope,request_id));
 CREATE UNIQUE INDEX IF NOT EXISTS uq_body_pending_logical ON body_pending_commands_v1(owner_id,backend_scope,logical_key) WHERE state IN ('PREPARED','SENT_UNKNOWN');`;
export async function attachBodyPending(db:PlanSQL,serial:Serial,owner:number,scope:string,digest:(s:string)=>Promise<string>):Promise<BodyPendingCommands>{
 if(!Number.isSafeInteger(owner)||owner<=0||!scope||scope.length>2048)throw Error('body_owner_mismatch');
 await serial(async()=>{await db.execAsync(SCHEMA);});
 const guard=(current:()=>boolean)=>{if(!current())throw Error('stale_identity');};
 const decode=async(row:any):Promise<PendingBodyCommand|null>=>{
  if(!row)return null;
  if(row.owner_id!==owner||row.backend_scope!==scope||row.namespace!=='BODY'||row.local_version!==1||!['PREPARED','SENT_UNKNOWN','ACKED','REJECTED'].includes(row.state))throw Error('invalid_body_storage');
  const canonical=bodyCommandCanonical(row);
  if(!/^[a-f0-9]{64}$/.test(row.body_digest)||await digest(canonical)!==row.body_digest)throw Error('invalid_body_storage');
  const receipt=row.receipt_json?decodeBodyReceipt(JSON.parse(row.receipt_json),owner,row):null;
  if((row.state==='ACKED')!==Boolean(receipt))throw Error('invalid_body_storage');
  return {owner_id:owner,backend_scope:scope,request_id:row.request_id,method:row.method,path:row.path,payload_json:row.payload_json,body_digest:row.body_digest,state:row.state,receipt,rejection:row.rejection,created_at_ms:row.created_at_ms};
 };
 const raw=(tx:PlanSQL,key:string)=>tx.getFirstAsync<any>('SELECT * FROM body_pending_commands_v1 WHERE owner_id=? AND backend_scope=? AND request_id=?',owner,scope,key);
 const read=async(key:string)=>decode(await raw(db,key));
 const transaction=(current:()=>boolean,work:(tx:PlanSQL)=>Promise<void>)=>serial(async()=>{guard(current);await db.withExclusiveTransactionAsync(async tx=>{guard(current);await work(tx);guard(current);});});
 return {read,
  async prepare(input,current){
   const canonical=bodyCommandCanonical(input),bodyDigest=await digest(canonical);guard(current);
   if(!/^[a-f0-9]{64}$/.test(bodyDigest))throw Error('invalid_body_digest');
   const logical=input.path==='/me/body/measurements'?'new':`root/${JSON.parse(canonical).root_ref}`;
   await transaction(current,async tx=>{
    const prior=await raw(tx,input.request_id);
    if(prior){if(prior.payload_json!==input.payload_json||prior.path!==input.path||prior.method!==input.method||prior.body_digest!==bodyDigest)throw Error('idempotency_mismatch');await decode(prior);return;}
    if(await tx.getFirstAsync("SELECT request_id FROM body_pending_commands_v1 WHERE owner_id=? AND backend_scope=? AND logical_key=? AND state IN ('PREPARED','SENT_UNKNOWN')",owner,scope,logical))throw Error('body_pending_conflict');
    await tx.runAsync("INSERT INTO body_pending_commands_v1 VALUES(?,?,?,1,'BODY',?,?,?,?,?,'PREPARED',NULL,NULL,?)",owner,scope,input.request_id,logical,input.method,input.path,input.payload_json,bodyDigest,Date.now());
   });
   guard(current);const saved=await read(input.request_id);guard(current);if(!saved)throw Error('body_prepare_not_durable');return saved;
  },
  async pending(){const rows=await db.getAllAsync<any>("SELECT * FROM body_pending_commands_v1 WHERE owner_id=? AND backend_scope=? AND state IN ('PREPARED','SENT_UNKNOWN') ORDER BY created_at_ms,request_id",owner,scope);return Promise.all(rows.map(async row=>(await decode(row))!));},
  async markUnknown(key,current,initialOnly=false){await transaction(current,async tx=>{const row=await decode(await raw(tx,key));if(!row)throw Error('body_command_missing');if(initialOnly&&row.state!=='PREPARED')throw Error('body_verification_required');if(['ACKED','REJECTED'].includes(row.state))throw Error('body_command_terminal');await tx.runAsync("UPDATE body_pending_commands_v1 SET state='SENT_UNKNOWN' WHERE owner_id=? AND backend_scope=? AND request_id=? AND state='PREPARED'",owner,scope,key);});},
  async ack(key,value,current){await transaction(current,async tx=>{const row=await decode(await raw(tx,key));if(!row||!decodeBodyReceipt(value,owner,row)||row.state==='REJECTED')throw Error('body_receipt_mismatch');await tx.runAsync("UPDATE body_pending_commands_v1 SET state='ACKED',receipt_json=? WHERE owner_id=? AND backend_scope=? AND request_id=?",JSON.stringify(value),owner,scope,key);});},
  async reject(key,code,current){await transaction(current,async tx=>{const row=await decode(await raw(tx,key));if(!row||row.state==='ACKED')throw Error('body_command_terminal');await tx.runAsync("UPDATE body_pending_commands_v1 SET state='REJECTED',rejection=? WHERE owner_id=? AND backend_scope=? AND request_id=?",code.slice(0,128),owner,scope,key);});},
 };
}
