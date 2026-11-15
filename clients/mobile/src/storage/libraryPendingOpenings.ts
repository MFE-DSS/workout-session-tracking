/** Operational intention on the owned journal connection/queue; no training facts. */
import {jsonCopy,positiveId,hexDigest} from '../api/firstPlanV3';
import {libraryStartJSON} from '../api/library';
import type {PlanSQL} from './planV3Journal';
import type {Serial} from './serial';
export type LibraryResolution='CREATED_CONFIRMED'|'REFUSED_CONFIRMED'|'RESUMED_OWNED'|'INTENTION_CANCELLED';
export type LibrarySessionIdentity={session_id:number;session_profile:'LEGACY'|'PLAN_V3'};
export type LibraryOpening={owner_id:number;backend_scope:string;local_id:string;local_version:1;source_ref:string;selection_ref:string;method:'POST';path:'/me/library/start';payload_json:string;digest:string;created_at_ms:number;state:'PREPARED'|'SENT_UNKNOWN'|'RESOLVED';resolution_kind:LibraryResolution|null;creation_outcome:'UNKNOWN'|'CONFIRMED'|'NOT_CREATED';session_id:number|null;session_profile:'LEGACY'|'PLAN_V3'|null};
export type LibraryOpeningInput=Pick<LibraryOpening,'local_id'|'source_ref'|'selection_ref'|'created_at_ms'>;
export interface LibraryPendingOpenings{
 readonly ownerId:number;readonly backendScope:string;
 prepare(input:LibraryOpeningInput,current:()=>boolean):Promise<LibraryOpening>;
 get(localId:string,current:()=>boolean):Promise<LibraryOpening|null>;
 unresolved(current:()=>boolean):Promise<LibraryOpening|null>;
 markSent(localId:string,digest:string,current:()=>boolean):Promise<LibraryOpening>;
 resolve(localId:string,kind:LibraryResolution,session:LibrarySessionIdentity|null,current:()=>boolean):Promise<void>;
}
const table='library_pending_openings_v1';
const columns=['owner_id','backend_scope','local_id','local_version','source_ref','selection_ref','method','path','payload_json','digest','created_at_ms','state','resolution_kind','creation_outcome','session_id','session_profile'];
const SCHEMA=`CREATE TABLE IF NOT EXISTS library_pending_openings_v1 (
 owner_id INTEGER NOT NULL CHECK(owner_id>0),backend_scope TEXT NOT NULL,
 local_id TEXT NOT NULL,local_version INTEGER NOT NULL CHECK(local_version=1),
 source_ref TEXT NOT NULL,selection_ref TEXT NOT NULL,method TEXT NOT NULL CHECK(method='POST'),
 path TEXT NOT NULL CHECK(path='/me/library/start'),payload_json TEXT NOT NULL,digest TEXT NOT NULL,
 created_at_ms INTEGER NOT NULL CHECK(created_at_ms>=0),
 state TEXT NOT NULL CHECK(state IN ('PREPARED','SENT_UNKNOWN','RESOLVED')),
 resolution_kind TEXT CHECK(resolution_kind IN ('CREATED_CONFIRMED','REFUSED_CONFIRMED','RESUMED_OWNED','INTENTION_CANCELLED')),
 creation_outcome TEXT NOT NULL CHECK(creation_outcome IN ('UNKNOWN','CONFIRMED','NOT_CREATED')),
 session_id INTEGER,session_profile TEXT CHECK(session_profile IN ('LEGACY','PLAN_V3')),
 PRIMARY KEY(owner_id,backend_scope,local_id));
 CREATE UNIQUE INDEX IF NOT EXISTS library_one_unresolved_opening_v1
 ON library_pending_openings_v1(owner_id,backend_scope) WHERE state<>'RESOLVED';`;
const uuid=(x:unknown):x is string=>typeof x==='string'&&/^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/.test(x);
const ref=(x:unknown):x is string=>typeof x==='string'&&x.length<=4096&&/^[A-Za-z0-9_-]+\.[a-f0-9]{64}$/.test(x);
const invalid=()=>{throw Error('invalid_library_intention');};
export async function attachLibraryPendingOpenings(db:PlanSQL,serial:Serial,ownerId:number,backendScope:string,sha256:(value:string)=>Promise<string>,current:()=>boolean):Promise<LibraryPendingOpenings>{
 const attachmentCurrent=current;
 const guard=(operationCurrent:()=>boolean)=>{if(!attachmentCurrent()||!operationCurrent())throw Error('stale_identity');};
 if(!positiveId(ownerId)||!backendScope||backendScope.length>2048)throw Error('invalid_library_scope');
 await serial(async()=>{guard(current);await db.withExclusiveTransactionAsync(async tx=>{
  guard(current);await tx.execAsync(SCHEMA);
  const shape=await tx.getAllAsync<{name:string;pk:number}>(`PRAGMA table_info(${table})`);
  if(shape.length!==columns.length||shape.some((x,i)=>x.name!==columns[i])||shape.filter(x=>x.pk>0).map(x=>x.name).join('/')!=='owner_id/backend_scope/local_id')throw Error('library_schema_unavailable');
  guard(current);
 });});
 const verify=async(raw:LibraryOpening|null,current:()=>boolean):Promise<LibraryOpening|null>=>{
  guard(current);if(!raw)return null;
  // SQLite ports may return a null-prototype row; its scalar columns retain
  // their exact values while the DTO gets an ordinary JSON object container.
  const r=jsonCopy({...raw});
  if(Object.keys(r).length!==columns.length||r.owner_id!==ownerId||r.backend_scope!==backendScope||!uuid(r.local_id)||r.local_version!==1||!ref(r.source_ref)||!ref(r.selection_ref)||r.method!=='POST'||r.path!=='/me/library/start'||!Number.isSafeInteger(r.created_at_ms)||r.created_at_ms<0||!hexDigest(r.digest)||r.payload_json!==libraryStartJSON(r.selection_ref))invalid();
  if(await sha256(r.payload_json)!==r.digest)invalid();guard(current);
  if(r.state==='PREPARED'||r.state==='SENT_UNKNOWN'){
   if(r.resolution_kind!==null||r.creation_outcome!=='UNKNOWN'||r.session_id!==null||r.session_profile!==null)invalid();
  }else if(r.state==='RESOLVED'){
   if(r.resolution_kind==='CREATED_CONFIRMED'){
    if(r.creation_outcome!=='CONFIRMED'||!positiveId(r.session_id)||r.session_profile!=='LEGACY')invalid();
   }else if(r.resolution_kind==='REFUSED_CONFIRMED'){
    if(r.creation_outcome!=='NOT_CREATED'||r.session_id!==null||r.session_profile!==null)invalid();
   }else if(r.resolution_kind==='RESUMED_OWNED'){
    if(r.creation_outcome!=='UNKNOWN'||!positiveId(r.session_id)||!['LEGACY','PLAN_V3'].includes(String(r.session_profile)))invalid();
   }else if(r.resolution_kind==='INTENTION_CANCELLED'){
    if(r.creation_outcome!=='UNKNOWN'||r.session_id!==null||r.session_profile!==null)invalid();
   }else invalid();
  }else invalid();
  return r;
 };
 const read=(tx:PlanSQL,localId:string)=>tx.getFirstAsync<LibraryOpening>(`SELECT * FROM ${table} WHERE owner_id=? AND backend_scope=? AND local_id=?`,ownerId,backendScope,localId);
 const unresolved=async(tx:PlanSQL,current:()=>boolean)=>{
  guard(current);
  const rows=await tx.getAllAsync<LibraryOpening>(`SELECT * FROM ${table} WHERE owner_id=? AND backend_scope=? AND state<>'RESOLVED' LIMIT 2`,ownerId,backendScope);
  if(rows.length>1)invalid();return verify(rows[0]??null,current);
 };
 const transaction=async<T,>(current:()=>boolean,task:(tx:PlanSQL)=>Promise<T>):Promise<T>=>serial(async()=>{
  guard(current);let result!:T;await db.withExclusiveTransactionAsync(async tx=>{guard(current);result=await task(tx);guard(current);});return result;
 });
 return {ownerId,backendScope,
  get:async(localId,current)=>serial(async()=>{guard(current);if(!uuid(localId))invalid();return verify(await read(db,localId),current);}),
  unresolved:async current=>serial(()=>unresolved(db,current)),
  async prepare(input,current){
   const value=jsonCopy(input);
   if(Object.keys(value).sort().join('/')!=='created_at_ms/local_id/selection_ref/source_ref'||!uuid(value.local_id)||!ref(value.source_ref)||!ref(value.selection_ref)||!Number.isSafeInteger(value.created_at_ms)||value.created_at_ms<0)invalid();
   const payload=libraryStartJSON(value.selection_ref),digest=await sha256(payload);if(!hexDigest(digest))invalid();
   return transaction(current,async tx=>{
    if(await unresolved(tx,current))throw Error('library_opening_unresolved');
    await tx.runAsync(`INSERT INTO ${table} (owner_id,backend_scope,local_id,local_version,source_ref,selection_ref,method,path,payload_json,digest,created_at_ms,state,resolution_kind,creation_outcome,session_id,session_profile) VALUES(?,?,?,1,?,?,'POST','/me/library/start',?,?,?,'PREPARED',NULL,'UNKNOWN',NULL,NULL)`,ownerId,backendScope,value.local_id,value.source_ref,value.selection_ref,payload,digest,value.created_at_ms);
    const row=await verify(await read(tx,value.local_id),current);if(!row)invalid();return row!;
   });
  },
  async markSent(localId,digest,current){return transaction(current,async tx=>{
   const row=await verify(await read(tx,localId),current);if(!row||row.digest!==digest||row.state!=='PREPARED')throw Error('library_opening_not_prepared');
   await tx.runAsync(`UPDATE ${table} SET state='SENT_UNKNOWN' WHERE owner_id=? AND backend_scope=? AND local_id=? AND state='PREPARED'`,ownerId,backendScope,localId);
   const sent=await verify(await read(tx,localId),current);if(sent?.state!=='SENT_UNKNOWN')invalid();return sent!;
  });},
  async resolve(localId,kind,session,current){await transaction(current,async tx=>{
   const row=await verify(await read(tx,localId),current);if(!row||row.state==='RESOLVED'||!['CREATED_CONFIRMED','REFUSED_CONFIRMED','RESUMED_OWNED','INTENTION_CANCELLED'].includes(kind))throw Error('library_opening_not_pending');
   if((kind==='CREATED_CONFIRMED'||kind==='REFUSED_CONFIRMED')&&row.state!=='SENT_UNKNOWN')throw Error('library_opening_not_sent');
   const withSession=kind==='CREATED_CONFIRMED'||kind==='RESUMED_OWNED';
   if(withSession?(!session||!positiveId(session.session_id)||!['LEGACY','PLAN_V3'].includes(session.session_profile)||kind==='CREATED_CONFIRMED'&&session.session_profile!=='LEGACY'):session!==null)invalid();
   const outcome=kind==='CREATED_CONFIRMED'?'CONFIRMED':kind==='REFUSED_CONFIRMED'?'NOT_CREATED':'UNKNOWN';
   await tx.runAsync(`UPDATE ${table} SET state='RESOLVED',resolution_kind=?,creation_outcome=?,session_id=?,session_profile=? WHERE owner_id=? AND backend_scope=? AND local_id=? AND state<>'RESOLVED'`,kind,outcome,session?.session_id??null,session?.session_profile??null,ownerId,backendScope,localId);
   await verify(await read(tx,localId),current);
  });}
 };
}
