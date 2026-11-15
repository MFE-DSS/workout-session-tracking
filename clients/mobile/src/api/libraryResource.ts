/** Memory-only views. Only confirmed current details can expose an exact choice. */
import {jsonCopy} from './firstPlanV3';
import type {LibraryClient,LibraryDetail,LibraryOutcome,LibraryPage,LibraryQuery} from './library';
export type LibrarySlot<T>={status:'idle'|'pending'|'confirmed'|'unknown'|'changed'|'unavailable';value?:T;previous:boolean;receivedAtMs?:number};
export type LibraryState={index:LibrarySlot<LibraryPage>;detail:LibrarySlot<LibraryDetail>;selectedRef:string|null;view:'INDEX'|'DETAIL'|'CONFIRM'};
export type CurrentLibrarySelection={source_ref:string;selection_ref:string;read_revision:string};
const initial=():LibraryState=>({index:{status:'idle',previous:false},detail:{status:'idle',previous:false},selectedRef:null,view:'INDEX'});
export class LibraryResource{
 private value=initial();private revision:number;private backend:string;private epoch=0;private indexSeq=0;private detailSeq=0;
 private query:LibraryQuery={section:'all',zone:null};private stack:string[]=[];private cursors=new Set<string>();
 constructor(readonly client:LibraryClient,private readonly now:()=>number=()=>Date.now()){this.revision=client.auth.revision;this.backend=client.backendScope;}
 get state():LibraryState{
  if(this.revision!==this.client.auth.revision||this.backend!==this.client.backendScope){this.revision=this.client.auth.revision;this.backend=this.client.backendScope;this.invalidate();}
  return jsonCopy(this.value);
 }
 invalidate(){this.epoch++;this.value=initial();this.stack=[];this.cursors.clear();}
 private async index(query:LibraryQuery,append:boolean){
  void this.state;const epoch=this.epoch,seq=++this.indexSeq,revision=this.revision,before=this.value.index;
  const current=()=>epoch===this.epoch&&seq===this.indexSeq&&revision===this.client.auth.revision&&this.backend===this.client.backendScope;
  this.value.index={...before,status:'pending',previous:before.value!==undefined};
  let outcome:LibraryOutcome<LibraryPage>;try{outcome=await this.client.page(query,current);}catch{outcome={state:'unknown'};}
  if(!current())return this.state;
  if(outcome.state==='confirmed'){
   let page=outcome.value;
   if(append&&before.value){
    const old=before.value;
    if(page.owner_id!==old.owner_id||page.read_revision!==old.read_revision||page.section!==old.section||page.requested_zone!==old.requested_zone||page.applied_zone!==old.applied_zone||JSON.stringify(page.groups)!==JSON.stringify(old.groups)||page.entries.some(e=>old.entries.some(x=>x.source_ref===e.source_ref))||(page.next_cursor!==null&&this.cursors.has(page.next_cursor))){this.value.index={...before,status:'changed',previous:before.value!==undefined};return this.state;}
    page={...page,entries:[...old.entries,...page.entries]};
   }
   this.value.index={status:'confirmed',previous:false,value:jsonCopy(page),receivedAtMs:append&&before.receivedAtMs!==undefined?before.receivedAtMs:this.now()};
  }else this.value.index={...before,status:outcome.state==='cancelled'?'unknown':outcome.state,previous:before.value!==undefined};
  return this.state;
 }
 refresh(query:LibraryQuery){
  void this.state;const old=this.value.index,same=this.query.section===query.section&&this.query.zone===query.zone;
  this.invalidate();this.query={...query,cursor:null};if(same)this.value.index=old;
  return this.index(this.query,false);
 }
 next(){
  const p=this.state.index;if(p.status!=='confirmed'||!p.value?.next_cursor)return Promise.resolve(this.state);
  this.cursors.add(p.value.next_cursor);return this.index({...this.query,cursor:p.value.next_cursor},true);
 }
 async select(sourceRef:string,fromBack=false){
  const state=this.state;
  const visible=state.index.status==='confirmed'&&state.index.value?.entries.some(e=>e.source_ref===sourceRef)||state.detail.status==='confirmed'&&state.detail.value?.composition.some(s=>s.source_ref===sourceRef);
  if(!fromBack&&!visible)return state;
  if(!fromBack&&state.selectedRef&&state.selectedRef!==sourceRef&&state.detail.status==='confirmed')this.stack.push(state.selectedRef);
  const previous=state.selectedRef===sourceRef?state.detail.value:undefined;
  this.value.selectedRef=sourceRef;this.value.view='DETAIL';this.value.detail={status:'pending',previous:previous!==undefined,...(previous?{value:previous,receivedAtMs:state.detail.receivedAtMs}:{})};
  const seq=++this.detailSeq,epoch=this.epoch,revision=this.revision;
  const current=()=>seq===this.detailSeq&&epoch===this.epoch&&revision===this.client.auth.revision;
  let outcome:LibraryOutcome<LibraryDetail>;try{outcome=await this.client.detail(sourceRef,current);}catch{outcome={state:'unknown'};}
  if(!current())return this.state;
  this.value.detail=outcome.state==='confirmed'?{status:'confirmed',value:outcome.value,previous:false,receivedAtMs:this.now()}:{...this.value.detail,status:outcome.state==='cancelled'?'unknown':outcome.state,previous:previous!==undefined};
  return this.state;
 }
 selection():CurrentLibrarySelection|null{
  const s=this.state,d=s.detail.value;
  return s.view!=='INDEX'&&s.detail.status==='confirmed'&&!s.detail.previous&&d?.selection?.selection_ref&&s.selectedRef?{source_ref:s.selectedRef,selection_ref:d.selection.selection_ref,read_revision:d.read_revision}:null;
 }
 selectionCurrent(selected:CurrentLibrarySelection){const now=this.selection();return now!==null&&now.source_ref===selected.source_ref&&now.selection_ref===selected.selection_ref&&now.read_revision===selected.read_revision;}
 confirm(){if(this.selection())this.value.view='CONFIRM';return this.state;}
 back(){
  const s=this.state;this.detailSeq++;
  if(s.view==='CONFIRM'){this.value.view='DETAIL';return Promise.resolve(this.state);}
  const parent=this.stack.pop();if(parent)return this.select(parent,true);
  this.value.selectedRef=null;this.value.detail={status:'idle',previous:false};this.value.view='INDEX';return Promise.resolve(this.state);
 }
}
