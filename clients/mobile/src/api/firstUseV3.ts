/** Parallel, owned controller. Mutation identities survive uncertainty and process restart. */
import type {PlanV3Stored,FirstSessionCommandV3,FirstSessionReceiptV3,ExecutionV3,CapabilitiesV3,BlueprintSnapshotV3,EvaluationV3,CalibrationReadV1,ContextV3} from '../domain/planV3Types';
import {workPositionV3,workPermissionV3} from '../domain/planV3Workout';
import type {PlanV3Journal} from '../storage/planV3Journal';
import type {BlueprintV3Client,DeclarationPatchV3,DeclarationsV3} from './blueprintV3';
import type {FirstPlanV3Client,V3Outcome} from './firstPlanV3';
import {jsonCopy} from './firstPlanV3';
import {commandFromEvaluationV3,type FirstSessionV3Client} from './firstSessionV3';
import type {CalibrationV1Client} from './calibrationV1';
import {bindCalibrationCapabilities} from './calibrationProfilesV2';
type Ports={ownerId:number;journal:PlanV3Journal;sessions:FirstSessionV3Client;plan:FirstPlanV3Client;
 blueprint:BlueprintV3Client;calibration:CalibrationV1Client;newId:()=>string;current:()=>boolean};
export class FirstUseV3Controller {
 state:PlanV3Stored|null=null;
 localOperations:import('../storage/planV3Journal').LocalPlanOperationV3[]=[];
 capabilities:CapabilitiesV3|null=null;
 encounter:CalibrationReadV1|null=null;
 notice:string|null=null;
 private busy=false;
 private interactionRevision=0;
 private draftPending:Record<string,unknown>|null=null;
 private draftWriting:Promise<void>|null=null;
 constructor(private readonly ports:Ports,private readonly changed:()=>void=()=>undefined){}
 get active(){return this.ports.current();}
 private async persist(state:PlanV3Stored){if(!this.active)return;await this.ports.journal.save(state,()=>this.active);if(!this.active)return;this.state=await this.ports.journal.read();if(this.active)this.changed();}
 async restore(){
  const state=await this.ports.journal.read();if(!this.active)return;
  if(state){
   if(state.owner_id!==this.ports.ownerId)throw Error('journal_owner_mismatch');
   const next=jsonCopy(state);
   if(next.execution){next.execution.applicability={...next.execution.applicability,state:'UNKNOWN',reason:'REVALIDATION_REQUIRED'};next.execution.observation_only=true;next.execution.allowed_actions=next.execution.allowed_actions.filter(a=>a!=='NEXT_WORK_SET');next.phase=next.phase==='COMPLETE'?'COMPLETE':'PAUSED';}
   await this.persist(next);
  }else{
   const initial:PlanV3Stored={profile:'PLAN_V3',local_version:'first-session-local/3.0.0',owner_id:this.ports.ownerId,phase:'FIRST_USE',intent:null,execution:null,source:{},local_facts:{},drafts:{}};
   if(await this.ports.journal.claim(initial,()=>this.active)){if(this.active)this.state=initial;}
  }
  await this.readLocalHistory();this.changed();
 }
 private async exclusive(task:()=>Promise<void>){if(this.busy||!this.active)return;this.busy=true;this.changed();try{if(this.draftWriting)await this.draftWriting;await task();}finally{this.busy=false;await this.flushCalibrationDraft();if(this.active)this.changed();}}
 get loading(){return this.busy;}
 private invalidateCalibrationGuidance(){if(this.encounter)this.encounter={...this.encounter,result:null,authority:null,allowed_actions:[],unavailable_reason:'REVALIDATION_REQUIRED'};this.changed();}
 async load(){await this.exclusive(async()=>{
  this.invalidateCalibrationGuidance();this.capabilities=null;
  const result=await this.ports.plan.capabilities();if(!this.active)return;
  if(result.state!=='confirmed'){this.notice='Capacité indisponible';return;}
  this.capabilities=result.value;
  if(!this.state)return;
  if(!result.value.controlled_test_available)this.notice='Producteur non servi';
  const declarations=await this.ports.blueprint.read();if(!this.active)return;
  if(declarations.state==='confirmed'){await this.persist({...this.state,source:{...this.state.source,declarations:declarations.value}});await this.recoverPending(declarations.value);}
  else this.notice='Lecture des informations indisponible';
  if(this.state.intent&&this.state.intent.state!=='denied'&&this.state.intent.state!=='cancelled')await this.reconcileStartInternal();
  else if(!this.state.execution){
   const handoff=await this.ports.sessions.handoff(()=>this.active);
   if(this.active&&handoff.state==='confirmed'&&handoff.value.handoff)await this.applyReceipt(handoff.value.handoff);
  }
 });}
 private async recoverPending(declarations:DeclarationsV3){
  if(!this.state||!this.capabilities)return;
  const pending=this.state.source.pending as {kind:string;request_id:string;body:Record<string,unknown>;calibration_draft_ref?:string}|undefined;
  const receipts=declarations.receipts;if(!pending||!receipts)return;
  const source={...this.state.source};let found=false;
  if(pending.kind==='capture'){
   const receipt=receipts.snapshots.find(r=>r.request_id===pending.request_id&&r.source_revision===pending.body.revision);
   if(receipt){const result=await this.ports.blueprint.readSnapshot(receipt.snapshot_ref,()=>this.active);if(result.state==='confirmed'){source.snapshot=result.value;found=true;}}
  }else if(pending.kind==='evaluate'||pending.kind==='time-ack'){
   const receipt=receipts.evaluations.find(r=>r.request_id===pending.request_id&&r.operation_kind===(pending.kind==='evaluate'?'EVALUATE':'TIME_ACK'));
   const snapshot=source.snapshot as BlueprintSnapshotV3|undefined;
   if(receipt&&snapshot&&receipt.snapshot_ref===snapshot.snapshot_ref){const result=await this.ports.plan.readEvaluation(receipt.evaluation_ref,snapshot,this.capabilities,()=>this.active);
    if(result.state==='confirmed'){source.evaluation=result.value;found=true;}}
  }else{
   const receipt=receipts.sources.find(r=>r.request_id===pending.request_id);
   if(receipt){
    found=pending.kind==='declarations'&&receipt.kind==='DECLARATIONS'||pending.kind==='calibration-event'&&receipt.kind!=='DECLARATIONS'||pending.kind==='select-calibration'&&receipt.kind==='CALIBRATION_ENCOUNTER_SELECTED'||pending.kind==='open-observed'&&receipt.kind==='CONTEXT_OPENED'||pending.kind==='observed-event'&&receipt.kind==='CALIBRATION_EVENT'||pending.kind==='open-calibration'&&receipt.kind==='CALIBRATION_ENCOUNTER_OPENED';
    if(found&&pending.kind==='open-calibration')source.encounter_ref=receipt.event_ref;
    if(found&&pending.kind==='select-calibration')source.encounter_ref=pending.body.encounter;
    if(found&&pending.kind==='open-observed')source.observed_episode_ref=receipt.event_ref;
    if(found&&pending.kind==='calibration-event'&&receipt.kind==='CALIBRATION_EVENT_REPORTED')this.confirmCalibrationDraft(source,pending,receipt.event_ref);
    if(found&&pending.kind==='observed-event'&&(pending.body.event as {kind:string})?.kind==='ATTEMPT_OBSERVED')source.observed_trial_ref=receipt.event_ref;
   }
  }
  if(found&&this.active){delete source.pending;await this.persist({...this.state!,source});this.notice='Action retrouvée dans les reçus du compte.';}
 }
 async retryPendingExplicitly(){await this.exclusive(async()=>{
  const pending=this.state?.source.pending as {kind:string;body:any}|undefined;if(!pending)return;
  const b=pending.body;
  if(pending.kind==='declarations')await this.sourceMutation(pending.kind,b,key=>this.ports.blueprint.saveDeclarations(key,b.revision,b.fields,()=>this.active));
  else if(pending.kind==='capture')await this.sourceMutation(pending.kind,b,key=>this.ports.blueprint.capture(key,b.revision,()=>this.active));
  else if(pending.kind==='open-observed')await this.sourceMutation(pending.kind,b,key=>this.ports.blueprint.observe(key,b.revision,{kind:'CONTEXT_OPENED',context:b.context,availability:'AVAILABLE'},()=>this.active));
  else if(pending.kind==='observed-event')await this.sourceMutation(pending.kind,b,key=>this.ports.blueprint.observe(key,b.revision,{kind:'CALIBRATION_EVENT',episode_ref:b.episode,event:b.event},()=>this.active));
  else if(pending.kind==='open-calibration')await this.sourceMutation(pending.kind,b,key=>this.ports.calibration.open(key,b.revision,b.context,b.availability,b.concern,()=>this.active));
  else if(pending.kind==='select-calibration')await this.sourceMutation(pending.kind,b,key=>this.ports.calibration.select(key,b.revision,b.encounter,()=>this.active));
  else if(pending.kind==='calibration-event'){
   const view=await this.ports.calibration.read(b.encounter,()=>this.active,this.capabilities);
   if(view.state==='confirmed')await this.sourceMutation(pending.kind,b,key=>this.ports.blueprint.observe(key,b.revision,{kind:'ENCOUNTER_OBSERVATION',encounter_ref:b.encounter,expected_authority:b.authority,observation:b.observation},()=>this.active));
  }else if(pending.kind==='evaluate'&&this.capabilities){
   const snapshot=this.state?.source.snapshot as BlueprintSnapshotV3|undefined;
   if(snapshot)await this.sourceMutation(pending.kind,b,key=>this.ports.plan.evaluate(snapshot,this.capabilities!,key,()=>this.active));
  }else if(pending.kind==='time-ack'&&this.capabilities){
   const evaluation=this.state?.source.evaluation as EvaluationV3|undefined;
   if(evaluation)await this.sourceMutation(pending.kind,b,key=>this.ports.plan.acknowledge(evaluation,this.capabilities!,key,()=>this.active));
  }
 });}
 /** Persist action/body BEFORE its sole send; only an explicit repeat uses that same identity. */
 private async sourceMutation<T>(kind:string,body:unknown,send:(key:string)=>Promise<V3Outcome<T>>):Promise<T|null>{
  if(!this.state||!this.active)return null;
  const pending=this.state.source.pending as {kind:string;body:unknown;request_id:string;calibration_draft_ref?:string}|undefined;
  if(pending&&(pending.kind!==kind||JSON.stringify(pending.body)!==JSON.stringify(body))){this.notice='Une action doit être relue ou répétée explicitement avant de modifier ces informations.';return null;}
  const activeDraft=this.calibrationDraft((body as {encounter?:string})?.encounter??'') as {draft_ref?:string}|null;
  const operation=pending??{kind,body:jsonCopy(body),request_id:this.ports.newId(),...(activeDraft?.draft_ref?{calibration_draft_ref:activeDraft.draft_ref}:{})};
  await this.persist({...this.state,source:{...this.state.source,pending:operation}});if(!this.active)return null;
  const result=await send(operation.request_id);if(!this.active||!this.state)return null;
  if(result.state==='confirmed'){
   const source={...this.state.source};delete source.pending;
   this.confirmCalibrationDraft(source,operation as any,(result.value as {event_ref?:string}).event_ref);
   if(kind==='capture')source.snapshot=result.value;
   if(kind==='evaluate'||kind==='time-ack')source.evaluation=result.value;
   if(kind==='open-observed')source.observed_episode_ref=(result.value as {episode_ref:string}).episode_ref;
   if(kind==='observed-event'&&(body as {event?:{kind:string}}).event?.kind==='ATTEMPT_OBSERVED')source.observed_trial_ref=(result.value as {event_ref:string}).event_ref;
   if(kind==='open-calibration')source.encounter_ref=(result.value as {encounter_ref:string}).encounter_ref;
   if(kind==='select-calibration')source.encounter_ref=(body as {encounter:string}).encounter;
   if(['open-calibration','select-calibration','calibration-event'].includes(kind)){delete source.snapshot;delete source.evaluation;}
   await this.persist({...this.state,source});this.notice=null;return result.value;
  }
  if(result.state==='rejected'){
   const source={...this.state.source};delete source.pending;await this.persist({...this.state,source});this.notice=result.code??'Demande refusée';
  }else this.notice='Réponse incertaine. Relire avant de répéter cette même action.';
  return null;
 }
 private get revision():number|null{const d=this.state?.source.declarations as {source_revision?:number}|undefined;return typeof d?.source_revision==='number'?d.source_revision:null;}
 async saveDeclarations(fields:DeclarationPatchV3){let confirmed=false;await this.exclusive(async()=>{
  if(this.revision===null)return;const revision=this.revision;
  const saved=await this.sourceMutation('declarations',{fields,revision},key=>this.ports.blueprint.saveDeclarations(key,revision,fields,()=>this.active));
  if(saved&&this.state){
   const read=await this.ports.blueprint.read(()=>this.active);
   if(read.state==='confirmed'&&this.active){
    const source:Record<string,unknown>={...this.state.source,declarations:read.value};delete source.snapshot;delete source.evaluation;delete source.setup_confirmed_for;
    await this.persist({...this.state,source});confirmed=true;
   }
  }
 });return confirmed&&this.active;}

 private async readSources(){if(!this.state)return false;const read=await this.ports.blueprint.read(()=>this.active);if(read.state==='confirmed'&&this.active){await this.persist({...this.state,source:{...this.state.source,declarations:read.value}});await this.recoverPending(read.value);return !this.state?.source.pending;}return false;}
 async selectObservedEpisode(episodeRef:string){
  if(!this.state)return false;const declarations=this.state.source.declarations as DeclarationsV3|undefined;
  const episode=declarations?.observation_progress?.find(e=>e.episode_ref===episodeRef);if(!episode)return false;
  const last=episode.events.filter(e=>e.kind==='ATTEMPT_OBSERVED').at(-1);
  await this.persist({...this.state,source:{...this.state.source,observed_episode_ref:episodeRef,observed_trial_ref:last?.event_id??null}});return this.active;
 }
 async openObservedContext(context:ContextV3){let accepted=false;await this.exclusive(async()=>{
  if(this.revision===null)return;const revision=this.revision;
  const receipt=await this.sourceMutation('open-observed',{context,revision},key=>this.ports.blueprint.observe(key,revision,{kind:'CONTEXT_OPENED',context,availability:'AVAILABLE'},()=>this.active));
  if(receipt&&this.state){accepted=true;await this.persist({...this.state,source:{...this.state.source,observed_episode_ref:receipt.episode_ref}});await this.readSources();}
 });return accepted&&this.active;}
 async recordObservedEvent(event:Record<string,unknown>){let accepted=false;await this.exclusive(async()=>{
  const episode=this.state?.source.observed_episode_ref;if(typeof episode!=='string'||this.revision===null)return;const revision=this.revision;
  const receipt=await this.sourceMutation('observed-event',{episode,revision,event},key=>this.ports.blueprint.observe(key,revision,{kind:'CALIBRATION_EVENT',episode_ref:episode,event},()=>this.active));
  if(receipt&&this.state){accepted=true;if(event.kind==='ATTEMPT_OBSERVED')await this.persist({...this.state,source:{...this.state.source,observed_trial_ref:receipt.event_ref}});await this.readSources();}
 });return accepted&&this.active;}
 async openCalibration(context:ContextV3,availability:'AVAILABLE'|'UNAVAILABLE'|'UNKNOWN',concern:'CLEAR'|'REPORTED'|'UNKNOWN'){
  await this.exclusive(async()=>{if(this.revision===null)return;const revision=this.revision,interaction=++this.interactionRevision;this.encounter=null;
   const opened=await this.sourceMutation('open-calibration',{context,availability,concern,revision},key=>this.ports.calibration.open(key,revision,context,availability,concern,()=>this.active));
   if(opened&&this.state){await this.persist({...this.state,source:{...this.state.source,encounter_ref:opened.encounter_ref}});await this.readSources();await this.readCalibrationInternal(interaction);}
  });
 }
 private async readCalibrationInternal(interaction=this.interactionRevision){const ref=this.state?.source.encounter_ref;if(typeof ref!=='string')return;
  const current=()=>this.active&&interaction===this.interactionRevision;if(!current())return;
  const result=await this.ports.calibration.read(ref,current,this.capabilities);if(!current())return;
  if(result.state==='confirmed'){this.encounter=bindCalibrationCapabilities(result.value,this.capabilities,this.ports.ownerId);this.notice=this.encounter.unavailable_reason??null;}
  else {if(this.encounter)this.encounter={...this.encounter,result:null,authority:null,allowed_actions:[],unavailable_reason:'REVALIDATION_REQUIRED'};this.notice='Rencontre indisponible';}this.changed();
 }
 async selectCalibration(encounter:string){let selected=false;await this.exclusive(async()=>{
  if(this.revision===null)return;const revision=this.revision,interaction=++this.interactionRevision;this.encounter=null;
  const receipt=await this.sourceMutation('select-calibration',{encounter,revision},key=>this.ports.calibration.select(key,revision,encounter,()=>this.active));
  if(receipt){selected=true;await this.readSources();await this.readCalibrationInternal(interaction);}
 });return selected&&this.active;}
 calibrationDraft(encounter:string):unknown {
  const drafts=this.state?.source.calibration_drafts as Record<string,unknown>|undefined;
  if(drafts?.[encounter])return jsonCopy(drafts[encounter]);
  const previous=this.state?.source.calibration_draft as Record<string,unknown>|undefined;
  return previous?.encounter_ref===encounter?jsonCopy(previous):null;
 }
 newCalibrationDraftRef(){return this.ports.newId();}
 private confirmCalibrationDraft(source:Record<string,unknown>,operation:{kind:string;body:any;calibration_draft_ref?:string},eventRef:unknown){
  if(operation.kind!=='calibration-event'||operation.body.observation?.event?.kind!=='ATTEMPT_OBSERVED'||typeof eventRef!=='string')return;
  const drafts={...(source.calibration_drafts as Record<string,Record<string,unknown>>??{})},ref=operation.body.encounter,draft=drafts[ref];
  if(draft&&typeof operation.calibration_draft_ref==='string'&&draft.draft_ref===operation.calibration_draft_ref){
   drafts[ref]={...draft,stage:'decision',committed_event_ref:eventRef};source.calibration_drafts=drafts;
  }
 }
 async saveCalibrationDraft(fields:Record<string,unknown>){
  if(!this.state||!this.active)return;this.draftPending=jsonCopy(fields);
  if(!this.busy)await this.flushCalibrationDraft();
 }
 private async flushCalibrationDraft():Promise<void>{
  if(this.draftWriting)return this.draftWriting;
  this.draftWriting=(async()=>{while(this.draftPending&&this.state&&this.active){
   const fields=this.draftPending;this.draftPending=null;
   const drafts={...(this.state.source.calibration_drafts as Record<string,unknown>??{})};
   if(typeof fields.encounter_ref==='string'){
    const old=drafts[fields.encounter_ref] as Record<string,unknown>|undefined;
    drafts[fields.encounter_ref]=old?.committed_event_ref&&old.draft_ref===fields.draft_ref?{...fields,stage:'decision',committed_event_ref:old.committed_event_ref}:fields;
   }
   await this.persist({...this.state,source:{...this.state.source,calibration_draft:fields,calibration_drafts:drafts}});
  }})();
  try{await this.draftWriting;}finally{this.draftWriting=null;}
 }
 async readCalibration(){await this.exclusive(()=>this.readCalibrationInternal());}
 async recordCalibration(observation:Record<string,unknown>){let accepted=false;await this.exclusive(async()=>{
  if(!this.encounter)return;const view=jsonCopy(this.encounter),interaction=this.interactionRevision;this.invalidateCalibrationGuidance();
  const receipt=await this.sourceMutation('calibration-event',{encounter:view.encounter_ref,revision:view.source_revision,authority:view.authority,observation},key=>this.ports.calibration.record(key,view,observation,()=>this.active));
  if(receipt){accepted=true;await this.readCalibrationInternal(interaction);if(this.state){const d=await this.ports.blueprint.read(()=>this.active);if(this.active&&d.state==='confirmed')await this.persist({...this.state,source:{...this.state.source,declarations:d.value}});}}
 });return accepted&&this.active;}
 async evaluate(){await this.exclusive(async()=>{
  if(!await this.readSources())return;
  if(!this.capabilities?.controlled_test_available){this.notice='Producteur non servi';return;}
  if(this.revision===null||!this.capabilities||!this.state)return;const revision=this.revision;
  let snapshot=this.state.source.snapshot as BlueprintSnapshotV3|undefined;
  if(!snapshot||snapshot.source_revision!==revision){
   const value=await this.sourceMutation('capture',{revision},key=>this.ports.blueprint.capture(key,revision,()=>this.active));if(!value||!this.state)return;snapshot=value;
   await this.persist({...this.state,source:{...this.state.source,snapshot}});
  }
  const captured=snapshot,caps=this.capabilities;
  const result=await this.sourceMutation('evaluate',{snapshot:captured.snapshot_ref},key=>this.ports.plan.evaluate(captured,caps,key,()=>this.active));
  if(result&&this.state)await this.persist({...this.state,source:{...this.state.source,evaluation:result}});
 });}
 async acknowledgeTime(){await this.exclusive(async()=>{
  const evaluation=this.state?.source.evaluation as EvaluationV3|undefined;if(!evaluation||!this.capabilities)return;const caps=this.capabilities;
  const result=await this.sourceMutation('time-ack',{evaluation:evaluation.evaluation_ref},key=>this.ports.plan.acknowledge(evaluation,caps,key,()=>this.active));
  if(result&&this.state)await this.persist({...this.state,source:{...this.state.source,evaluation:result}});
 });}
 async start(){const evaluation=this.state?.source.evaluation as EvaluationV3|undefined;if(!evaluation||!this.capabilities)return;
  const command=commandFromEvaluationV3(evaluation,this.capabilities);if(command)await this.startCommand(command);
 }
 async startCommand(command:FirstSessionCommandV3){await this.exclusive(async()=>{
  if(!this.state||this.state.execution)return;
  const previous=this.state.intent;
  if(previous&&!(previous.state==='denied'&&previous.receipt?.state==='DENIED'||previous.state==='cancelled'&&previous.receipt?.state==='CANCELLED'))return;
  const source=previous?{...this.state.source,previous_intents:[...((this.state.source.previous_intents as unknown[])??[]),previous]}:this.state.source;
  await this.persist({...this.state,source,phase:'START_UNKNOWN',intent:{request_id:this.ports.newId(),command:jsonCopy(command),state:'submitted',receipt:null}});
  await this.sendStart();
 });}
 private async sendStart(){if(!this.state?.intent||!this.active)return;
  const intent=jsonCopy(this.state.intent);const result=await this.ports.sessions.submit(intent.request_id,intent.command,()=>this.active);
  if(!this.active||!this.state?.intent)return;
  if(result.state==='confirmed')await this.applyReceipt(result.value);
  else await this.persist({...this.state,intent:{...this.state.intent,state:'unknown'}});
 }
 async retryStartExplicitly(){await this.exclusive(async()=>{if(this.state?.intent?.state==='unknown'||this.state?.intent?.state==='submitted')await this.sendStart();});}
 private async applyReceipt(receipt:FirstSessionReceiptV3){if(!this.active||!this.state)return;
  const intent=this.state.intent?{...this.state.intent,state:receipt.state.toLowerCase() as 'created'|'denied'|'cancelled',receipt}:null;
  await this.persist({...this.state,intent});
  if(receipt.state==='CREATED'&&receipt.session_id!==null)await this.readExecutionInternal(receipt.session_id);
  else this.notice=receipt.terminal_code;
 }
 private async reconcileStartInternal(){if(!this.state?.intent)return;const intent=this.state.intent;
  const result=await this.ports.sessions.readRequest(intent.request_id,()=>this.active);if(!this.active)return;
  if(result.state==='confirmed'){await this.applyReceipt(result.value);return;}
  const handoff=await this.ports.sessions.handoff(()=>this.active);if(!this.active)return;
  if(handoff.state==='confirmed'&&handoff.value.handoff){await this.applyReceipt(handoff.value.handoff);return;}
  if(this.state)await this.persist({...this.state,intent:{...intent,state:'unknown'}});
 }
 async reconcileStart(){await this.exclusive(()=>this.reconcileStartInternal());}
 async beginNext(){await this.exclusive(async()=>{
  const id=this.state?.execution?.session_id,interaction=this.interactionRevision;if(!id||this.state?.phase==='COMPLETE')return;await this.readExecutionInternal(id);
  if(!this.state?.execution||!this.active||interaction!==this.interactionRevision)return;
  if(workPermissionV3(this.state,Date.parse(this.state.execution.server_now)).state==='WORK')await this.persist({...this.state,phase:'ACTIVE'});
 });}
 async pause(){this.interactionRevision+=1;if(this.encounter)this.encounter={...this.encounter,result:null,authority:null,allowed_actions:[],unavailable_reason:'REVALIDATION_REQUIRED'};if(!this.state)return;await this.persist({...this.state,phase:this.state.phase==='COMPLETE'||this.state.execution?.status==='completed'?'COMPLETE':'PAUSED',execution:this.state.execution?{...this.state.execution,applicability:{...this.state.execution.applicability,state:'UNKNOWN',reason:'REVALIDATION_REQUIRED'},observation_only:true,allowed_actions:this.state.execution.allowed_actions.filter(a=>a!=='NEXT_WORK_SET')}:null});}
 async confirmSetup(){if(!this.state)return;const position=workPositionV3(this.state);if(!position)return;await this.persist({...this.state,source:{...this.state.source,setup_confirmed_for:position.set.set_id}});await this.refreshExecution();}
 async recordFact(setId:number,setting:number,reps:number|null,performedAt:string,estimated:boolean,completed=true){await this.exclusive(async()=>{
  if(!this.state?.execution||!Number.isFinite(setting)||setting<0||(reps!==null&&(!Number.isSafeInteger(reps)||reps<0))||(completed&&reps===null)||!Number.isFinite(Date.parse(performedAt)))return;
  const exercise=this.state.execution.exercises.find(e=>e.sets.some(s=>s.set_id===setId));const set=exercise?.sets.find(s=>s.set_id===setId);if(!exercise||!set)return;
  const prior=this.state.local_facts[String(setId)],opId=this.ports.newId();
  const fact={context:exercise.prescription.context,setting:{...exercise.prescription.setting,value:setting},reps,completed,performed_at:performedAt,performed_at_estimated:estimated};
  const revision=Math.max(prior?.local_revision??0,...this.localOperations.filter(row=>row.session_id===this.state!.execution!.session_id&&row.set_id===setId).map(row=>row.local_revision))+1,expected=prior&&prior.sync!=='acked'&&prior.sync!=='resolved'?prior.expected_server_revision+1:Math.max(set.revision,prior?.sync==='acked'?prior.expected_server_revision+1:0);
  const next={...this.state,phase:this.state.execution.status==='completed'?'COMPLETE' as const:'PAUSED' as const,local_facts:{...this.state.local_facts,[String(setId)]:{op_id:opId,fact,local_revision:revision,expected_server_revision:expected,sync:'saved_local' as const}}};
  await this.ports.journal.commitSet({owner_id:this.ports.ownerId,op_id:opId,session_id:this.state.execution.session_id,se_id:exercise.se_id,set_id:setId,local_revision:revision,expected_server_revision:expected,fact,performed_at_estimated:estimated,recorded_at_ms:Date.now()},
   {op_id:opId,kind:'PLAN_V3_SET',target:`set/${setId}`,payload:{session_id:this.state.execution.session_id,set_id:setId,op_id:opId,expected_set_revision:expected,observation:fact}},next,()=>this.active);
  if(this.active){this.state=await this.ports.journal.read();await this.readLocalHistory();this.changed();}
 });}
 async close(kind:'SESSION_FINISH'|'SESSION_ABANDON'){await this.exclusive(async()=>{
  if(!this.state?.execution)return;
  await this.ports.journal.enqueueClose(this.ports.newId(),kind,this.state.execution.session_id,{...this.state,phase:'COMPLETE'},()=>this.active);
  if(this.active){this.state=await this.ports.journal.read();this.changed();}
 });}
 private async readLocalHistory(){
  const id=this.state?.execution?.session_id,interaction=this.interactionRevision;if(!id)return;
  const history=await this.ports.journal.history(id);
  if(this.active&&interaction===this.interactionRevision){this.localOperations=history;this.changed();}
 }
 async resolveRefusal(setId:number){await this.exclusive(async()=>{
  const id=this.state?.execution?.session_id;if(!id)return;
  if(!await this.readExecutionInternal(id)||!this.active||!this.state?.execution){this.notice='Relis la version serveur avant de résoudre ce refus.';return;}
  await this.ports.journal.resolveRefusal(setId,this.state.execution,()=>this.active);
  if(this.active){this.state=await this.ports.journal.read();await this.readLocalHistory();this.notice='Version serveur retenue. Le refus et les faits locaux restent conservés.';this.changed();}
 });}
 private async readExecutionInternal(id:number){const interaction=this.interactionRevision,current=()=>this.active&&interaction===this.interactionRevision;const result=await this.ports.sessions.execution(id,current);if(!current()||!this.state)return;
  if(result.state==='confirmed'){await this.persist({...this.state,phase:result.value.status==='completed'||this.state.phase==='COMPLETE'?'COMPLETE':'PAUSED',execution:result.value});await this.readLocalHistory();return true;}
  else if(this.state.execution)await this.persist({...this.state,phase:'PAUSED',execution:{...this.state.execution,applicability:{...this.state.execution.applicability,state:'UNKNOWN',reason:'REVALIDATION_REQUIRED'},observation_only:true,allowed_actions:this.state.execution.allowed_actions.filter(a=>a!=='NEXT_WORK_SET')}});
 }
 async refreshExecution(){await this.exclusive(async()=>{const id=this.state?.execution?.session_id??this.state?.intent?.receipt?.session_id;if(id)await this.readExecutionInternal(id);});}
}
