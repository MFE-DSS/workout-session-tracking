/** One human library opening. There is deliberately no automatic POST replay. */
import {jsonCopy,positiveId} from '../api/firstPlanV3';
import type {LibraryClient} from '../api/library';
import type {CurrentLibrarySelection} from '../api/libraryResource';
import type {ExecutionPlan} from '../api/types';
import type {LibraryPendingOpenings,LibraryOpening,LibrarySessionIdentity} from '../storage/libraryPendingOpenings';
export type OwnedLibraryRead={state:'confirmed';owner_id:number;backend_scope:string;session:LibrarySessionIdentity|null}|{state:'unknown'|'unavailable'};
export type LibraryOpeningState={phase:'hydrating'|'idle'|'submitting'|'unknown'|'owned_found'|'created'|'refused'|'resumed'|'cancelled'|'unavailable';pending?:LibraryOpening;owned?:LibrarySessionIdentity;code?:string};
export type LibraryOpeningPorts={onOpened?:()=>void;client:LibraryClient;pending:LibraryPendingOpenings;uuid:()=>string;now:()=>number;otherActionPending:()=>boolean;
 readOwned:(current:()=>boolean)=>Promise<OwnedLibraryRead>;
 adoptLegacy:(execution:ExecutionPlan,current:()=>boolean)=>Promise<void>;
 resumeOwned:(session:LibrarySessionIdentity,current:()=>boolean)=>Promise<void>};
export class LibraryOpeningController{
 private value:LibraryOpeningState={phase:'hydrating'};private readonly revision:number;private busy=false;private disposed=false;
 constructor(private readonly ports:LibraryOpeningPorts){
  this.revision=ports.client.auth.revision;
  if(ports.pending.backendScope!==ports.client.backendScope)throw Error('library_backend_mismatch');
 }
 private active=()=>!this.disposed&&this.revision===this.ports.client.auth.revision;
 get state():LibraryOpeningState{return this.active()?jsonCopy(this.value):{phase:'cancelled'};}
 dispose(){this.disposed=true;}
 private async owned(){return this.active()&&await this.ports.client.owner(this.active)===this.ports.pending.ownerId&&this.active();}
 private async load(){
  if(!await this.owned())return null;
  return this.ports.pending.unresolved(this.active);
 }
 async hydrate(){
  if(this.busy||!this.active())return this.state;this.busy=true;
  try{
   if(!await this.owned())return this.state;
   const p=await this.ports.pending.unresolved(this.active);
   if(this.active())this.value=p?{phase:'unknown',pending:p}:{phase:'idle'};
  }catch{if(this.active())this.value={phase:'unavailable'};}finally{this.busy=false;}
  return this.state;
 }
 async submit(selection:CurrentLibrarySelection,selectionCurrent:()=>boolean){
  if(this.busy||!this.active()||!selectionCurrent()||this.ports.otherActionPending()||this.value.code==='session_open')return this.state;
  this.busy=true;const current=()=>this.active()&&selectionCurrent();
  try{
   if(!await this.owned()||!current())return this.state;
   const old=await this.ports.pending.unresolved(current);
   if(old){if(this.active())this.value={phase:'unknown',pending:old};return this.state;}
   if(!current()||this.ports.otherActionPending())return this.state;
   const p=await this.ports.pending.prepare({local_id:this.ports.uuid(),source_ref:selection.source_ref,selection_ref:selection.selection_ref,created_at_ms:this.ports.now()},current);
   this.value={phase:'submitting',pending:p};
   const exact=await this.ports.pending.get(p.local_id,current);
   if(!exact||exact.digest!==p.digest||exact.payload_json!==p.payload_json||!current()||this.ports.otherActionPending())throw Error('library_preparation_changed');
   const sent=await this.ports.pending.markSent(p.local_id,p.digest,current);
   if(!current()||this.ports.otherActionPending())throw Error('library_preparation_changed');
   const r=await this.ports.client.start(this.ports.pending.ownerId,sent.selection_ref,sent.source_ref,sent.digest,current);
   if(!this.active())return this.state;
   this.value={phase:'unknown',pending:sent};
   if(r.state==='created'){
    // Adopt only after the native journal confirms its write; failure leaves
    // the sent intention unknown and prevents another fresh POST.
    await this.ports.adoptLegacy(r.value.execution,this.active);
    await this.ports.pending.resolve(sent.local_id,'CREATED_CONFIRMED',{session_id:r.value.execution.session_id,session_profile:'LEGACY'},this.active);
    if(this.active()){this.value={phase:'created'};this.ports.onOpened?.();}
   }else if(r.state==='refused'){
    await this.ports.pending.resolve(sent.local_id,'REFUSED_CONFIRMED',null,this.active);
    if(this.active())this.value={phase:'refused',code:r.value.code};
    if(r.value.code==='session_open'){const owned=await this.candidate();if(this.active()&&owned)this.value={phase:'owned_found',owned,code:'session_open'};}
   }
  }catch{
   if(this.active()){
    try{const pending=await this.load();if(this.active())this.value=pending?{phase:'unknown',pending}:{phase:'unavailable'};}
    catch{if(this.active())this.value={phase:'unavailable'};}
   }
  }finally{this.busy=false;}
  return this.state;
 }
 private async candidate():Promise<LibrarySessionIdentity|null>{
  let r:OwnedLibraryRead;try{r=await this.ports.readOwned(this.active);}catch{return null;}
  if(!this.active()||r.state!=='confirmed'||r.owner_id!==this.ports.pending.ownerId||r.backend_scope!==this.ports.pending.backendScope||!r.session||!positiveId(r.session.session_id)||!['LEGACY','PLAN_V3'].includes(r.session.session_profile))return null;
  return r.session;
 }
 async verify(){
  if(this.busy||!this.active())return this.state;this.busy=true;
  try{
   const pending=await this.load();if(!this.active())return this.state;
   if(!pending&&this.value.code!=='session_open')return this.state;
   const owned=await this.candidate();
   if(this.active())this.value=owned?{phase:'owned_found',...(pending?{pending}:{}),owned,...(!pending?{code:'session_open'}:{})}:pending?{phase:'unknown',pending}:{phase:'refused',code:'session_open'};
  }catch{if(this.active()&&this.value.pending)this.value={phase:'unknown',pending:this.value.pending};}finally{this.busy=false;}
  return this.state;
 }
 async resume(){
  if(this.busy||!this.active()||this.value.phase!=='owned_found'||!this.value.owned)return this.state;
  this.busy=true;const expected=this.value.owned,pending=this.value.pending;
  try{
   if(!await this.owned())return this.state;
   const fresh=await this.candidate();
   if(!fresh||fresh.session_id!==expected.session_id||fresh.session_profile!==expected.session_profile){if(this.active())this.value=pending?{phase:'unknown',pending}:{phase:'refused',code:'session_open'};return this.state;}
   await this.ports.resumeOwned(fresh,this.active);
   if(pending)await this.ports.pending.resolve(pending.local_id,'RESUMED_OWNED',fresh,this.active);
   if(this.active()){this.value={phase:'resumed'};this.ports.onOpened?.();}
  }catch{if(this.active())this.value=pending?{phase:'unknown',pending}:{phase:'refused',code:'session_open'};}finally{this.busy=false;}
  return this.state;
 }
 async cancel(confirmed:boolean){
  if(!confirmed||this.busy||!this.active())return this.state;this.busy=true;
  try{
   const pending=await this.load();if(!pending||!this.active())return this.state;
   await this.ports.pending.resolve(pending.local_id,'INTENTION_CANCELLED',null,this.active);
   if(this.active())this.value={phase:'idle'};
  }catch{if(this.active())this.value={phase:'unavailable'};}finally{this.busy=false;}
  return this.state;
 }
}
