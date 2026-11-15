/** Explicit owned acquisition; receipts are historical, fresh GETs alone supply facts. */
import type {ProgramBuilderClient,BuilderOutcome} from '../../api/programBuilder';
import type {BuilderExerciseOption,BuilderProgram,BuilderProgramSummary,BuilderReceipt} from '../../api/programBuilderDTO';
import {BUILDER_VERSION,builderCommandJSON,type BuilderOperation} from '../../domain/programBuilderCommand';
import type {PendingBuilderCommand,ProgramBuilderPendingCommands} from '../../storage/programBuilderPendingCommands';
import {ProgramBuilderRecovery} from '../../sync/programBuilderRecovery';
import {draftFromProgram,manualMovement,moveItem,setCount,treePayload,type BuilderDraft,type DraftMovement} from './programBuilderModel';
export type ProgramBuilderPorts={client:ProgramBuilderClient;store:ProgramBuilderPendingCommands;current:()=>boolean;newId:()=>string};
export type BuilderConfirmation='PUBLISH'|'NEW_CYCLE'|'ARCHIVE';
export type ProgramBuilderState={view:'index'|'create'|'editor';programs:BuilderProgramSummary[];programCursor:string|null;exercises:BuilderExerciseOption[];exerciseCursor:string|null;picker:boolean;pickerFresh:boolean;
 source?:BuilderProgram;draft?:BuilderDraft;activeSession:number;activeMovement:number;fresh:boolean;conflict:boolean;busy:boolean;message:string;pending:PendingBuilderCommand[];replayKeys:string[];confirm:BuilderConfirmation|null};
const clone=<T,>(value:T):T=>JSON.parse(JSON.stringify(value));
const confirmations:readonly BuilderOperation[]=['PUBLISH','NEW_CYCLE','ARCHIVE'];
export class ProgramBuilderController{
 readonly state:ProgramBuilderState={view:'index',programs:[],programCursor:null,exercises:[],exerciseCursor:null,picker:false,pickerFresh:false,activeSession:0,activeMovement:0,fresh:false,conflict:false,busy:false,message:'',pending:[],replayKeys:[],confirm:null};
 private recovery:ProgramBuilderRecovery;private selectedId:number|null=null;private disposed=false;
 constructor(private ports:ProgramBuilderPorts,private changed:()=>void=()=>{}){
  this.recovery=new ProgramBuilderRecovery(ports.client,ports.store,()=>this.current());
 }
 private current=()=>!this.disposed&&this.ports.current();
 dispose(){this.disposed=true;}
 private emit(){if(this.current())this.changed();}
 private async run(work:()=>Promise<void>){
  if(!this.current()||this.state.busy)return;
  this.state.busy=true;this.state.message='';this.emit();
  try{await work();}catch{if(this.current()){this.state.message='Vérification indisponible · le brouillon est conservé.';this.state.fresh=false;}}
  finally{if(this.current()){this.state.busy=false;this.emit();}}
 }
 private outcome<T>(outcome:BuilderOutcome<T>):T|undefined{
  if(!this.current())return;
  if(outcome.state==='confirmed')return outcome.value;
  this.state.message=outcome.state==='rejected'?`Commande refusée · ${outcome.code??outcome.status}. Le brouillon est conservé.`:outcome.state==='changed'||outcome.state==='cancelled'?'Compte ou source changé · revenir à la bibliothèque.':'Résultat non confirmé · vérifier avant toute nouvelle commande.';
  return;
 }
 private async pending(){const rows=await this.ports.store.pending(this.current);if(this.current()){this.state.pending=rows;this.state.replayKeys=this.state.replayKeys.filter(k=>rows.some(r=>r.command_id===k));}}
 private async read(id:number,replace=false,receiptDigest?:string){
  const outcome=await this.ports.client.program(id);if(!this.current())return;
  const value=this.outcome(outcome);if(!value){this.state.fresh=false;return;}
  const p=value.program,dirty=this.dirty(),changed=this.state.source!==undefined&&this.state.source.source_digest!==p.source_digest;
  this.state.source=clone(p);this.state.fresh=true;
  if(replace&&(!receiptDigest||receiptDigest===p.source_digest)||!this.state.draft||!dirty){this.state.draft=draftFromProgram(p);this.state.conflict=false;}
  else if(changed){this.state.conflict=true;this.state.message='Le programme a changé. Votre brouillon est conservé ; relisez la source avant de choisir.';}
 }
 refresh(){return this.run(async()=>{
  await this.pending();if(!this.current())return;
  const page=this.outcome(await this.ports.client.programs());if(page){this.state.programs=page.items;this.state.programCursor=page.next_cursor;}
  if(this.selectedId!==null&&this.current())await this.read(this.selectedId);
 });}
 morePrograms(){return this.run(async()=>{if(!this.state.programCursor)return;const page=this.outcome(await this.ports.client.programs(25,this.state.programCursor));if(page){this.state.programs=[...this.state.programs,...page.items];this.state.programCursor=page.next_cursor;}});}
 select(id:number){return this.run(async()=>{
  this.selectedId=id;this.state.source=undefined;this.state.draft=undefined;this.state.fresh=false;this.state.conflict=false;this.state.confirm=null;this.state.picker=false;this.state.activeSession=0;this.state.activeMovement=0;this.state.view='editor';
  await this.pending();if(this.current())await this.read(id,true);
 });}
 create(){if(!this.current()||this.state.busy)return;this.selectedId=null;Object.assign(this.state,{view:'create',source:undefined,draft:{title:'',sessions:[]},fresh:false,conflict:false,picker:false,confirm:null,message:''});this.emit();}
 index(){if(!this.current()||this.state.busy)return;this.selectedId=null;Object.assign(this.state,{view:'index',source:undefined,draft:undefined,fresh:false,picker:false,confirm:null,message:''});this.emit();}
 title(value:string){if(!this.editable())return;this.state.draft!.title=value;this.state.confirm=null;this.emit();}
 dirtyTitle(){return !!this.state.draft&&this.state.draft.title!==(this.state.source?.title??'');}
 dirtyTree(){return !!this.state.draft&&JSON.stringify(this.state.draft.sessions)!==JSON.stringify(this.state.source?draftFromProgram(this.state.source).sessions:[]);}
 dirty(){return this.dirtyTitle()||this.dirtyTree();}
 editable(){return this.current()&&!this.state.busy&&!this.state.conflict&&!!this.state.draft&&(this.state.view==='create'||this.state.fresh&&['draft','validated'].includes(this.state.source?.status??''))&&!this.rootPending();}
 rootPending(){return this.state.pending.some(r=>r.program_id===(this.state.source?.id??null));}
 private edit(change:()=>void){if(!this.editable()||this.state.view!=='editor')return;change();this.state.confirm=null;this.emit();}
 activeSession(){return this.state.draft?.sessions[this.state.activeSession];}
 activeMovement():DraftMovement|undefined{return this.activeSession()?.movements[this.state.activeMovement];}
 selectSession(index:number){if(this.state.busy||!this.current()||!this.state.draft?.sessions[index])return;this.state.activeSession=index;this.state.activeMovement=0;this.state.picker=false;this.emit();}
 selectMovement(index:number){if(this.state.busy||!this.current()||!this.activeSession()?.movements[index])return;this.state.activeMovement=index;this.state.picker=false;this.emit();}
 addSession(){this.edit(()=>{if(this.state.draft!.sessions.length>=7)return;this.state.draft!.sessions.push({name:'',kind:'strength',focus:'',duration_target_minutes:null,notes:null,movements:[]});this.state.activeSession=this.state.draft!.sessions.length-1;this.state.activeMovement=0;this.state.picker=false;});}
 removeSession(){this.edit(()=>{this.state.draft!.sessions.splice(this.state.activeSession,1);this.state.activeSession=Math.max(0,Math.min(this.state.activeSession,this.state.draft!.sessions.length-1));this.state.activeMovement=0;this.state.picker=false;});}
 moveSession(delta:-1|1){this.edit(()=>{this.state.activeSession=moveItem(this.state.draft!.sessions,this.state.activeSession,delta);});}
 sessionName(value:string){this.edit(()=>{const s=this.activeSession();if(s)s.name=value;});}
 sessionKind(kind:'strength'|'cardio'){this.edit(()=>{const s=this.activeSession();if(s)s.kind=kind;});}
 removeMovement(){this.edit(()=>{const s=this.activeSession();if(s){s.movements.splice(this.state.activeMovement,1);this.state.activeMovement=Math.max(0,Math.min(this.state.activeMovement,s.movements.length-1));}});}
 moveMovement(delta:-1|1){this.edit(()=>{const s=this.activeSession();if(s)this.state.activeMovement=moveItem(s.movements,this.state.activeMovement,delta);});}
 loadExercises(more=false){return this.run(async()=>{
  if(!this.state.draft||!this.state.fresh||this.state.conflict||this.rootPending()||!['draft','validated'].includes(this.state.source?.status??''))return;
  this.state.picker=true;this.state.pickerFresh=false;
  const value=this.outcome(await this.ports.client.exercises(25,more?this.state.exerciseCursor??undefined:undefined));
  if(value){this.state.exercises=more?[...this.state.exercises,...value.items]:value.items;this.state.exerciseCursor=value.next_cursor;this.state.pickerFresh=true;}
 });}
 closePicker(){if(this.state.busy)return;this.state.picker=false;this.emit();}
 chooseExercise(option:BuilderExerciseOption){this.edit(()=>{
  const s=this.activeSession(),canonical=this.state.pickerFresh&&this.state.exercises.find(e=>e.slug===option.slug&&e.name===option.name&&e.ekb_version===option.ekb_version);
  if(!s||s.movements.length>=10||!canonical)return;s.movements.push(manualMovement(canonical));this.state.activeMovement=s.movements.length-1;this.state.picker=false;
 });}
 movementSets(value:string){this.edit(()=>{const m=this.activeMovement();if(m?.kind==='manual')setCount(m,value);});}
 target(index:number,field:'min'|'max',value:string){this.edit(()=>{const m=this.activeMovement();if(m?.kind==='manual'&&m.targets[index])m.targets[index][field]=value;});}
 cancelConfirmation(){this.state.confirm=null;this.emit();}
 discard(){if(!this.current()||this.state.busy||!this.state.source||!this.state.fresh)return;this.state.draft=draftFromProgram(this.state.source);this.state.conflict=false;this.state.confirm=null;this.state.message='Brouillon remplacé par la source relue.';this.emit();}
 private allowed(operation:BuilderOperation){
  const p=this.state.source;if(operation==='CREATE')return this.state.view==='create'&&!this.rootPending();
  if(!p||!this.state.fresh||this.state.conflict||this.rootPending())return false;
  if(operation==='RENAME'||operation==='SAVE_TREE')return ['draft','validated'].includes(p.status);
  if(this.dirty())return false;
  return operation==='VALIDATE'?p.status==='draft':operation==='PUBLISH'?p.status==='validated':operation==='NEW_CYCLE'?p.status==='published':operation==='ARCHIVE'&&p.status!=='archived';
 }
 can(operation:BuilderOperation){if(!this.current()||this.state.busy||!this.allowed(operation))return false;try{this.body(operation,'check');return true;}catch{return false;}}
 private body(operation:BuilderOperation,key:string){
  const payload=operation==='CREATE'||operation==='RENAME'?{title:this.state.draft?.title}:operation==='SAVE_TREE'?treePayload(this.state.draft!):{};
  const body={contract_version:BUILDER_VERSION,command_id:key,operation,program_id:operation==='CREATE'?null:this.state.source!.id,expected_source_digest:operation==='CREATE'?null:this.state.source!.source_digest,payload};builderCommandJSON(body);return body;
 }
 private async received(result:BuilderOutcome<BuilderReceipt>,creationTitle?:string){
  if(!this.current())return;const receipt=this.outcome(result);await this.pending();if(!this.current())return;
  if(receipt){
   if(this.selectedId!==receipt.program_id&&this.dirty()&&!(receipt.operation==='CREATE'&&this.state.view==='create'&&this.state.draft?.title===creationTitle)){this.state.message='Résultat vérifié · le brouillon courant est conservé.';return;}
   const draft=this.state.draft?clone(this.state.draft):undefined,treeDirty=this.dirtyTree(),titleDirty=this.dirtyTitle();
   this.selectedId=receipt.program_id;this.state.view='editor';this.state.fresh=false;this.state.confirm=null;await this.read(receipt.program_id,true,receipt.resulting_source_digest);
   if(this.current()&&draft&&this.state.fresh&&!this.state.conflict&&this.state.source?.source_digest===receipt.resulting_source_digest&&this.state.draft){
    if(receipt.operation==='RENAME'&&treeDirty)this.state.draft.sessions=draft.sessions;
    if(receipt.operation==='SAVE_TREE'&&titleDirty)this.state.draft.title=draft.title;
   }
  }
  else if(result.state!=='unknown'){this.state.fresh=false;}
 }
 command(operation:BuilderOperation,confirmed=false){
  if(!this.can(operation))return Promise.resolve();
  if(confirmations.includes(operation)){
   if(!confirmed){this.state.confirm=operation as BuilderConfirmation;this.emit();return Promise.resolve();}
   if(this.state.confirm!==operation)return Promise.resolve();
  }
  return this.run(async()=>{const body=this.body(operation,this.ports.newId());this.state.confirm=null;await this.received(await this.recovery.send(body),operation==='CREATE'?this.state.draft?.title:undefined);});
 }
 verify(row:PendingBuilderCommand){return this.run(async()=>{
  this.state.replayKeys=this.state.replayKeys.filter(k=>k!==row.command_id);
  const result=await this.recovery.verify(row);if(!this.current())return;
  if(result.state==='unknown')this.state.replayKeys.push(row.command_id);await this.received(result,row.operation==='CREATE'?JSON.parse(row.payload_json).payload.title:undefined);
 });}
 replay(row:PendingBuilderCommand){if(!this.state.replayKeys.includes(row.command_id))return Promise.resolve();return this.run(async()=>{
  this.state.replayKeys=this.state.replayKeys.filter(k=>k!==row.command_id);await this.received(await this.recovery.replay(row),row.operation==='CREATE'?JSON.parse(row.payload_json).payload.title:undefined);
 });}
}
