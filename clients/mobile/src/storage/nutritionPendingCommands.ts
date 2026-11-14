/** Operational command copies on the owned journal connection, never nutrition history. */
import {nutritionCanonical,nutritionKey,nutHash,type NutritionInput,type PreparedNutritionRequest,type NutritionNamespace} from '../domain/nutritionCommand';
import {decodeNutritionReceipt,type NutritionReceipt} from '../api/nutrition';
import type {PlanSQL} from './planV3Journal';
import type {Serial} from './serial';
export type PendingNutritionCommand=PreparedNutritionRequest&{state:'PREPARED'|'SENT_UNKNOWN'|'ACKED'|'CONFLICT';receipt:NutritionReceipt|null;rejection:string|null;created_at_ms:number};
export interface NutritionPendingCommands{
 prepare(input:NutritionInput,current:()=>boolean):Promise<PendingNutritionCommand>;
 read(namespace:NutritionNamespace,key:string):Promise<PendingNutritionCommand|null>;
 pending():Promise<PendingNutritionCommand[]>;
 markUnknown(namespace:NutritionNamespace,key:string,current:()=>boolean,initialOnly?:boolean):Promise<void>;
 ack(namespace:NutritionNamespace,key:string,receipt:NutritionReceipt,current:()=>boolean):Promise<void>;
 conflict(namespace:NutritionNamespace,key:string,code:string,current:()=>boolean):Promise<void>;
}
const SCHEMA=`CREATE TABLE IF NOT EXISTS nutrition_pending_commands_v1(
 owner_id INTEGER NOT NULL,backend_scope TEXT NOT NULL,namespace TEXT NOT NULL CHECK(namespace IN ('DAY','TARGET')),
 request_id TEXT NOT NULL,local_version INTEGER NOT NULL CHECK(local_version=1),logical_key TEXT NOT NULL,
 method TEXT NOT NULL CHECK(method='POST'),path TEXT NOT NULL,payload_json TEXT NOT NULL,body_digest TEXT NOT NULL,
 state TEXT NOT NULL CHECK(state IN ('PREPARED','SENT_UNKNOWN','ACKED','CONFLICT')),receipt_json TEXT,rejection TEXT,created_at_ms INTEGER NOT NULL,
 PRIMARY KEY(owner_id,backend_scope,namespace,request_id));
 CREATE UNIQUE INDEX IF NOT EXISTS uq_nutrition_pending_key ON nutrition_pending_commands_v1(owner_id,backend_scope,namespace,logical_key) WHERE state IN ('PREPARED','SENT_UNKNOWN');`;
export async function attachNutritionPending(db:PlanSQL,serial:Serial,owner:number,scope:string,digest:(s:string)=>Promise<string>):Promise<NutritionPendingCommands>{
 if(!Number.isSafeInteger(owner)||owner<=0||!scope||scope.length>2048)throw Error('nutrition_owner_mismatch');
 await serial(async()=>{await db.execAsync(SCHEMA);});
 const guard=(current:()=>boolean)=>{if(!current())throw Error('stale_identity');};
 const raw=(tx:PlanSQL,namespace:NutritionNamespace,key:string)=>tx.getFirstAsync<any>('SELECT * FROM nutrition_pending_commands_v1 WHERE owner_id=? AND backend_scope=? AND namespace=? AND request_id=?',owner,scope,namespace,key);
 const decode=async(row:any):Promise<PendingNutritionCommand|null>=>{
  if(!row)return null;
  const command:PendingNutritionCommand={owner_id:row.owner_id,backend_scope:row.backend_scope,namespace:row.namespace,method:row.method,path:row.path,request_id:row.request_id,payload_json:row.payload_json,body_digest:row.body_digest,state:row.state,receipt:row.receipt_json===null?null:JSON.parse(row.receipt_json),rejection:row.rejection,created_at_ms:row.created_at_ms};
  if(row.local_version!==1||row.owner_id!==owner||row.backend_scope!==scope||!['PREPARED','SENT_UNKNOWN','ACKED','CONFLICT'].includes(row.state)||!nutHash(row.body_digest)||await digest(nutritionCanonical(command))!==row.body_digest||row.logical_key!==nutritionKey(command)||!Number.isSafeInteger(row.created_at_ms)||row.created_at_ms<0)throw Error('invalid_nutrition_local_command');
  if(row.state==='ACKED'?command.receipt===null||!decodeNutritionReceipt(command.receipt,owner,command):command.receipt!==null)throw Error('nutrition_receipt_mismatch');
  if(row.state==='CONFLICT'?(typeof row.rejection!=='string'||!row.rejection.length||row.rejection.length>128):row.rejection!==null)throw Error('invalid_nutrition_local_command');
  return command;
 };
 const read=async(namespace:NutritionNamespace,key:string)=>decode(await raw(db,namespace,key));
 const transaction=(current:()=>boolean,work:(tx:PlanSQL)=>Promise<void>)=>serial(async()=>{guard(current);await db.withExclusiveTransactionAsync(async tx=>{guard(current);await work(tx);guard(current);});});
 return {read,
  async prepare(input,current){
   const bodyDigest=await digest(nutritionCanonical(input));guard(current);if(!nutHash(bodyDigest))throw Error('invalid_nutrition_digest');
   const key=nutritionKey(input);
   await transaction(current,async tx=>{
    const old=await raw(tx,input.namespace,input.request_id);
    if(old){if(old.payload_json!==input.payload_json||old.path!==input.path||old.method!==input.method||old.body_digest!==bodyDigest)throw Error('idempotency_mismatch');await decode(old);return;}
    if(await tx.getFirstAsync("SELECT request_id FROM nutrition_pending_commands_v1 WHERE owner_id=? AND backend_scope=? AND namespace=? AND logical_key=? AND state IN ('PREPARED','SENT_UNKNOWN')",owner,scope,input.namespace,key))throw Error('nutrition_pending_conflict');
    await tx.runAsync("INSERT INTO nutrition_pending_commands_v1 VALUES(?,?,?,?,1,?,?,?,?,?,'PREPARED',NULL,NULL,?)",owner,scope,input.namespace,input.request_id,key,input.method,input.path,input.payload_json,bodyDigest,Date.now());
   });
   guard(current);const saved=await read(input.namespace,input.request_id);guard(current);if(!saved)throw Error('nutrition_prepare_not_durable');return saved;
  },
  async pending(){const rows=await db.getAllAsync<any>("SELECT * FROM nutrition_pending_commands_v1 WHERE owner_id=? AND backend_scope=? AND state IN ('PREPARED','SENT_UNKNOWN') ORDER BY created_at_ms,namespace,request_id",owner,scope);return Promise.all(rows.map(async row=>(await decode(row))!));},
  async markUnknown(namespace,key,current,initialOnly=false){await transaction(current,async tx=>{const row=await decode(await raw(tx,namespace,key));if(!row||!['PREPARED','SENT_UNKNOWN'].includes(row.state))throw Error('nutrition_command_terminal');if(initialOnly&&row.state!=='PREPARED')throw Error('nutrition_verification_required');await tx.runAsync("UPDATE nutrition_pending_commands_v1 SET state='SENT_UNKNOWN' WHERE owner_id=? AND backend_scope=? AND namespace=? AND request_id=?",owner,scope,namespace,key);});},
  async ack(namespace,key,receipt,current){await transaction(current,async tx=>{const row=await decode(await raw(tx,namespace,key));if(!row||row.state==='CONFLICT'||!decodeNutritionReceipt(receipt,owner,row)||row.state==='ACKED'&&JSON.stringify(row.receipt)!==JSON.stringify(receipt))throw Error('nutrition_receipt_mismatch');await tx.runAsync("UPDATE nutrition_pending_commands_v1 SET state='ACKED',receipt_json=? WHERE owner_id=? AND backend_scope=? AND namespace=? AND request_id=?",JSON.stringify(receipt),owner,scope,namespace,key);});},
  async conflict(namespace,key,code,current){await transaction(current,async tx=>{const row=await decode(await raw(tx,namespace,key));if(!row||row.state==='ACKED'||!code)throw Error('nutrition_command_terminal');await tx.runAsync("UPDATE nutrition_pending_commands_v1 SET state='CONFLICT',rejection=? WHERE owner_id=? AND backend_scope=? AND namespace=? AND request_id=?",code.slice(0,128),owner,scope,namespace,key);});},
 };
}
