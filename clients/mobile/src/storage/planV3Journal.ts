/** Owned extension on the existing connection and writer queue. No V1 kg coercion. */
import type {PlanV3Stored, PlanV3SetOperation, PlanV3SetCommand, ExecutionV3} from '../domain/planV3Types';
import type {Serial} from './serial';

type Binding = string|number|null;
export interface PlanSQL {
  execAsync(sql:string):Promise<unknown>;
  runAsync(sql:string,...params:Binding[]):Promise<unknown>;
  getFirstAsync<T>(sql:string,...params:Binding[]):Promise<T|null>;
  getAllAsync<T>(sql:string,...params:Binding[]):Promise<T[]>;
  withExclusiveTransactionAsync(task:(tx:PlanSQL)=>Promise<void>):Promise<void>;
}
const UPSERT='INSERT INTO active_session(id,snapshot,updated_at_ms) VALUES(1,?,?) ON CONFLICT(id) DO UPDATE SET snapshot=excluded.snapshot,updated_at_ms=excluded.updated_at_ms';
const SCHEMA=`CREATE TABLE IF NOT EXISTS journal_v3_set_operations (
 op_id TEXT PRIMARY KEY NOT NULL, owner_id INTEGER NOT NULL, session_id INTEGER NOT NULL,
 se_id INTEGER NOT NULL, set_id INTEGER NOT NULL, local_revision INTEGER NOT NULL,
 expected_server_revision INTEGER NOT NULL, fact_json TEXT NOT NULL,
 performed_at_estimated INTEGER NOT NULL, recorded_at_ms INTEGER NOT NULL,
 UNIQUE(owner_id,session_id,set_id,local_revision));`;
export type LocalPlanOperationV3=PlanV3SetOperation & {state:'pending'|'inflight'|'acked'|'failed'|'resolved'};
export interface PlanV3Journal {
  history(sessionId:number):Promise<LocalPlanOperationV3[]>;
  reject(opId:string,current:()=>boolean,reason?:string|null):Promise<void>;
  resolveRefusal(setId:number,execution:ExecutionV3,current:()=>boolean):Promise<void>;
  read():Promise<PlanV3Stored|null>;
  claim(state:PlanV3Stored,current:()=>boolean):Promise<boolean>;
  save(state:PlanV3Stored,current:()=>boolean):Promise<void>;
  commitSet(operation:PlanV3SetOperation,command:PlanV3SetCommand,state:PlanV3Stored,current:()=>boolean):Promise<void>;
  acknowledge(opId:string,current:()=>boolean):Promise<void>;
  enqueueClose(opId:string,kind:'SESSION_FINISH'|'SESSION_ABANDON',sessionId:number,state:PlanV3Stored,current:()=>boolean):Promise<void>;
}
function json(value:unknown):string {
 return JSON.stringify(value,(_key,item)=>{if(typeof item==='number'&&!Number.isFinite(item))throw Error('invalid_local_number');return item;});
}
function parse(snapshot:string):PlanV3Stored|null {
 const value=JSON.parse(snapshot);
 return value?.profile==='PLAN_V3'&&value.local_version==='first-session-local/3.0.0'?value:null;
}
export async function attachPlanV3Journal(db:PlanSQL,serial:Serial,ownerId:number):Promise<PlanV3Journal>{
 if(!Number.isSafeInteger(ownerId)||ownerId<=0)throw Error('journal_owner_mismatch');
 await serial(async()=>{await db.execAsync(SCHEMA);});
 const guard=(current:()=>boolean)=>{if(!current())throw Error('stale_identity');};
 const owned=(state:PlanV3Stored)=>{if(state.owner_id!==ownerId)throw Error('journal_owner_mismatch');json(state);};
 const readFrom=async(tx:PlanSQL)=>tx.getFirstAsync<{snapshot:string}>('SELECT snapshot FROM active_session WHERE id=1');
 const read=async()=>{const row=await readFrom(db);if(!row)return null;const state=parse(row.snapshot);if(state)owned(state);return state;};
 const transaction=async(current:()=>boolean,task:(tx:PlanSQL)=>Promise<void>)=>serial(async()=>{
   guard(current);await db.withExclusiveTransactionAsync(async tx=>{guard(current);await task(tx);guard(current);});
 });
 const ensureActive=async(tx:PlanSQL)=>{const row=await readFrom(tx),state=row?parse(row.snapshot):null;
   if(!state)throw Error('active_session_conflict');owned(state);return state;};
 return {read,
  async history(sessionId){
   const rows=await db.getAllAsync<Record<string,unknown>>('SELECT j.*, o.state FROM journal_v3_set_operations j JOIN outbox o ON o.op_id=j.op_id WHERE j.owner_id=? AND j.session_id=? ORDER BY j.rowid',ownerId,sessionId);
   return rows.map(row=>({op_id:row.op_id,owner_id:row.owner_id,session_id:row.session_id,se_id:row.se_id,set_id:row.set_id,local_revision:row.local_revision,expected_server_revision:row.expected_server_revision,fact:JSON.parse(String(row.fact_json)),performed_at_estimated:Boolean(row.performed_at_estimated),recorded_at_ms:row.recorded_at_ms,state:row.state})) as LocalPlanOperationV3[];
  },
  async reject(opId,current,reason=null){await transaction(current,async tx=>{
   const state=await ensureActive(tx);
   const row=await tx.getFirstAsync<{set_id:number}>('SELECT set_id FROM journal_v3_set_operations WHERE owner_id=? AND op_id=?',ownerId,opId);if(!row)return;
   const key=String(row.set_id),fact=state.local_facts[key];
   if(fact?.op_id===opId)state.local_facts[key]={...fact,sync:'failed'};
   state.source={...state.source,refused_operations:{...(state.source.refused_operations as Record<string,unknown>??{}),[opId]:{reason,recorded_at:new Date().toISOString()}}};
   await tx.runAsync(UPSERT,json(state),Date.now());
  });},
  async resolveRefusal(setId,execution,current){await transaction(current,async tx=>{
   const state=await ensureActive(tx),set=execution.exercises.flatMap(e=>e.sets).find(s=>s.set_id===setId);
   if(execution.session_id!==state.execution?.session_id||!set)throw Error('session_set_mismatch');
   const rows=await tx.getAllAsync<{op_id:string;state:string;queue_order:number}>(
    "SELECT j.op_id,o.state,o.rowid AS queue_order FROM journal_v3_set_operations j JOIN outbox o ON j.op_id=o.op_id WHERE j.owner_id=? AND j.session_id=? AND j.set_id=? AND o.state NOT IN ('acked','resolved') ORDER BY o.rowid",ownerId,execution.session_id,setId);
   // A known refusal is necessary. Unknown/in-flight operations cannot be retired.
   if(!rows.length||rows[0].state!=='failed'||rows.some(row=>!['failed','pending'].includes(row.state)))throw Error('refusal_resolution_not_available');
   for(const row of rows)await tx.runAsync("UPDATE outbox SET state='resolved' WHERE op_id=? AND state IN ('failed','pending')",row.op_id);
   const fact=state.local_facts[String(setId)];if(fact)state.local_facts[String(setId)]={...fact,sync:'resolved'};
   const prior=state.source.refusal_resolutions as unknown[]|undefined;
   state.source={...state.source,refusal_resolutions:[...(prior??[]),{set_id:setId,op_ids:rows.map(row=>row.op_id),choice:'USE_SERVER_VERSION',server_revision:set.revision,resolved_at:new Date().toISOString()}]};
   state.execution=execution;
   await tx.runAsync(UPSERT,json(state),Date.now());
  });},
  async enqueueClose(opId,kind,sessionId,state,current){owned(state);await transaction(current,async tx=>{
   const active=await ensureActive(tx);if(active.execution?.session_id!==sessionId)throw Error('session_set_mismatch');
   const payload=json({session_id:sessionId,at:new Date().toISOString()});
   const old=await tx.getFirstAsync<{kind:string;payload:string}>('SELECT kind,payload FROM outbox WHERE op_id=?',opId);
   if(old){if(old.kind!==kind||JSON.parse(old.payload).session_id!==sessionId)throw Error('idempotency_mismatch');return;}
   await tx.runAsync("INSERT INTO outbox(op_id,kind,target,payload,created_at_ms,attempts,state) VALUES(?,?,?,?,?,0,'pending')",opId,kind,`session/${sessionId}`,payload,Date.now());
   await tx.runAsync(UPSERT,json({...state,local_facts:active.local_facts}),Date.now());
  });},
  async claim(state,current){
   owned(state);let claimed=false;
   await transaction(current,async tx=>{
    const row=await readFrom(tx);
    if(row){
     const existing=parse(row.snapshot);
     if(existing){owned(existing);return;}
     const old=JSON.parse(row.snapshot);
     if(old.phase!=='MISSION'&&old.phase!=='COMPLETE')return;
    }
    const pending=await tx.getFirstAsync<{op_id:string}>("SELECT op_id FROM outbox WHERE state NOT IN ('acked','resolved') LIMIT 1");
    if(pending)return;
    await tx.runAsync(UPSERT,json(state),Date.now());claimed=true;
   });return claimed;
  },
  async save(state,current){owned(state);await transaction(current,async tx=>{
   const active=await ensureActive(tx),merged={...state,local_facts:{...state.local_facts}};
   for(const [key,fact] of Object.entries(active.local_facts)){
    const next=merged.local_facts[key];
    if(!next||fact.local_revision>next.local_revision||fact.op_id===next.op_id&&['acked','failed','resolved'].includes(fact.sync))merged.local_facts[key]=fact;
   }
   await tx.runAsync(UPSERT,json(merged),Date.now());
  });},
  async commitSet(operation,command,state,current){
   owned(state);
   if(operation.owner_id!==ownerId||operation.op_id!==command.op_id||command.kind!=='PLAN_V3_SET'
    ||command.payload.op_id!==operation.op_id||command.payload.session_id!==operation.session_id||command.payload.set_id!==operation.set_id
    ||command.payload.expected_set_revision!==operation.expected_server_revision||json(command.payload.observation)!==json(operation.fact))throw Error('invalid_set_operation');
   await transaction(current,async tx=>{
    const active=await ensureActive(tx);
    if(active.execution?.session_id!==operation.session_id||state.execution?.session_id!==operation.session_id
      ||!active.execution.exercises.some(e=>e.se_id===operation.se_id&&e.sets.some(s=>s.set_id===operation.set_id)))throw Error('session_set_mismatch');
    const prior=await tx.getFirstAsync<{fact_json:string;owner_id:number;session_id:number;se_id:number;set_id:number;local_revision:number;expected_server_revision:number}>(
      'SELECT * FROM journal_v3_set_operations WHERE op_id=?',operation.op_id);
    if(prior){
     if(prior.owner_id!==ownerId||prior.session_id!==operation.session_id||prior.se_id!==operation.se_id||prior.set_id!==operation.set_id
      ||prior.local_revision!==operation.local_revision||prior.expected_server_revision!==operation.expected_server_revision||prior.fact_json!==json(operation.fact))throw Error('idempotency_mismatch');
     return; // Exact replay cannot roll back a newer correction or instrument position.
    }
    const latest=await tx.getFirstAsync<{revision:number}>('SELECT MAX(local_revision) AS revision FROM journal_v3_set_operations WHERE owner_id=? AND session_id=? AND set_id=?',ownerId,operation.session_id,operation.set_id);
    if(operation.local_revision!==(latest?.revision??0)+1)throw Error('local_revision_mismatch');
    await tx.runAsync('INSERT INTO journal_v3_set_operations VALUES(?,?,?,?,?,?,?,?,?,?)',operation.op_id,ownerId,operation.session_id,operation.se_id,operation.set_id,
      operation.local_revision,operation.expected_server_revision,json(operation.fact),operation.performed_at_estimated?1:0,operation.recorded_at_ms);
    await tx.runAsync("INSERT INTO outbox(op_id,kind,target,payload,created_at_ms,attempts,state) VALUES(?,?,?,?,?,0,'pending')",
      command.op_id,command.kind,command.target,json(command.payload),operation.recorded_at_ms);
    await tx.runAsync(UPSERT,json(state),Date.now());
   });
  },
  async acknowledge(opId,current){await transaction(current,async tx=>{
   const state=await ensureActive(tx);
   const row=await tx.getFirstAsync<{set_id:number}>('SELECT set_id FROM journal_v3_set_operations WHERE owner_id=? AND op_id=?',ownerId,opId);
   if(!row)return;
   const key=String(row.set_id),fact=state.local_facts[key];
   if(fact?.op_id===opId){state.local_facts[key]={...fact,sync:'acked'};await tx.runAsync(UPSERT,json(state),Date.now());}
  });},
 };
}
