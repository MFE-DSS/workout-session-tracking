/** Owned manual instrument state. Values, targets, receipt and readback stay distinct. */
import type {NutritionClient,NutritionReceipt} from '../../api/nutrition';
import type {NutritionCapabilities,NutritionConsent,NutritionEntry,NutritionHead} from '../../api/nutritionDTO';
import {NutritionResource,type NutritionCollectionState} from '../../api/nutritionResource';
import {nutritionCommand,nutDay,parseNutritionDecimal,type NutritionField,type NutritionInput,type NutritionNamespace,type NutritionVariant} from '../../domain/nutritionCommand';
import type {NutritionPendingCommands,PendingNutritionCommand} from '../../storage/nutritionPendingCommands';
import type {NutritionRecovery} from '../../sync/nutritionRecovery';

export function applicableNutritionTargets(entries:NutritionEntry[],day:string):NutritionEntry[]{
 const latest=new Map<NutritionVariant,NutritionEntry>();
 for(const e of entries){if(!e.variant||!e.effective_from||e.effective_from>day)continue;
  const prior=latest.get(e.variant);if(!prior||e.effective_from>prior.effective_from!||e.effective_from===prior.effective_from&&e.revision>prior.revision)latest.set(e.variant,e);}
 return [...latest.values()].filter(e=>e.enabled);
}
export const nutritionNumber=(milli:number|null)=>milli===null?'—':(milli/1000).toLocaleString('fr-FR',{maximumFractionDigits:3});
const unknown=():NutritionCollectionState=>({state:'unknown',value:null,previous:null});
export type NutritionEditor={namespace:NutritionNamespace;field:NutritionField;head:NutritionHead;day:string;timezone:string;variant?:NutritionVariant;effectiveFrom?:string;value:string;clear:boolean};
export type NutritionWorkspaceState={day:string;timezone:string;status:'pending'|'confirmed'|'unknown'|'consent_required';busy:boolean;capabilities:NutritionCapabilities|null;consent:NutritionConsent|null;head:NutritionHead|null;previousHead:NutritionHead|null;days:NutritionCollectionState;targets:NutritionCollectionState;versions:NutritionCollectionState|null;versionsNamespace:NutritionNamespace;boundTarget:NutritionEntry|null;editor:NutritionEditor|null;pending:PendingNutritionCommand[];verified:string|null;notice:string;refusal:string|null;receipt:NutritionReceipt|null;period:7|30};
type Options={client:NutritionClient;pending?:NutritionPendingCommands;recovery:Pick<NutritionRecovery,'send'|'verify'|'replay'>|null;current:()=>boolean;newId:()=>string;day:string;timezone:string;notify:()=>void};
export class NutritionWorkspace{
 readonly state:NutritionWorkspaceState;
 private sequence=0;
 private days:NutritionResource;private targets:NutritionResource;private versions:NutritionResource;
 constructor(private p:Options){
  this.state={day:p.day,timezone:p.timezone,status:'pending',busy:false,capabilities:null,consent:null,head:null,previousHead:null,days:unknown(),targets:unknown(),versions:null,versionsNamespace:'DAY',boundTarget:null,editor:null,pending:[],verified:null,notice:'',refusal:null,receipt:null,period:7};
  this.days=new NutritionResource(p.client,p.current);this.targets=new NutritionResource(p.client,p.current);this.versions=new NutritionResource(p.client,p.current);
 }
 private clear(){Object.assign(this.state,{capabilities:null,head:null,previousHead:null,days:unknown(),targets:unknown(),versions:null,boundTarget:null,editor:null,refusal:null,receipt:null,pending:[],verified:null});}
 private current(sequence?:number){if(!this.p.current()){this.clear();return false;}return sequence===undefined||sequence===this.sequence;}
 private boundary(state:string){if(['changed','cancelled','consent_required'].includes(state)){this.sequence++;this.clear();this.state.consent=null;this.state.status=state==='consent_required'?'consent_required':'unknown';this.state.notice='Identité ou accord à vérifier';return false;}return true;}
 private emit(){if(this.current())this.p.notify();}
 invalidate(){this.sequence++;this.clear();}
 private writable(){return this.current()&&this.state.status==='confirmed'&&!!this.state.consent?.granted&&!!this.state.capabilities?.can_write&&!this.state.refusal&&!this.state.busy&&!!this.p.recovery&&!!this.p.pending;}
 private async pending(){try{const rows=await this.p.pending?.pending()??[];if(this.current())this.state.pending=rows;}catch{if(this.current())this.state.notice='Reprise locale indisponible · aucun nouvel envoi';}}
 async refresh(){
  const seq=++this.sequence,prior=this.state.head??this.state.previousHead;const matchingPrior=prior?.key.local_day===this.state.day?prior:null;this.state.status='pending';this.state.head=null;this.state.previousHead=null;this.emit();
  const consent=await this.p.client.consent();if(!this.current(seq))return;
  this.state.consent=consent.state==='confirmed'?consent.value:null;
  if(consent.state!=='confirmed'||!consent.value.granted){this.clear();this.state.status=consent.state==='confirmed'?'consent_required':'unknown';await this.pending();this.emit();return;}
  const capabilities=await this.p.client.capabilities();if(!this.current(seq))return;if(!this.boundary(capabilities.state)){this.emit();return;}this.state.capabilities=capabilities.state==='confirmed'?capabilities.value:null;
  const day=this.state.day,head=await this.p.client.head({local_day:day});if(!this.current(seq))return;if(!this.boundary(head.state)){this.emit();return;}
  this.state.status=head.state==='confirmed'?'confirmed':head.state==='consent_required'?'consent_required':'unknown';
  if(head.state==='confirmed')this.state.head=head.value;else this.state.previousHead=head.state==='consent_required'?null:matchingPrior;
  if(head.state==='consent_required'){this.clear();this.state.consent=null;this.emit();return;}
  const from=new Date(Date.parse(day+'T00:00:00Z')-(this.state.period-1)*86400000).toISOString().slice(0,10);
  const days=await this.days.load({kind:'days',from,through:day});if(!this.current(seq))return;if(!this.boundary(days.state)){this.emit();return;}this.state.days=days;
  const targets=await this.targets.load({kind:'targets'});if(!this.current(seq))return;if(!this.boundary(targets.state)){this.emit();return;}this.state.targets=targets;this.state.boundTarget=null;
  const ref=this.state.head?.entry?.target_ref;
  if(ref){const versions=new NutritionResource(this.p.client,this.p.current);const result=await versions.load({kind:'versions',namespace:'TARGET',reference:ref});if(!this.current(seq))return;if(!this.boundary(result.state)){this.emit();return;}
   if(result.state==='confirmed')this.state.boundTarget=result.value?.entries.map(e=>'entry' in e?e.entry:e).find(e=>e.id===ref)??null;}
  await this.pending();if(this.current(seq))this.emit();
 }
 async selectDay(day:string){if(!nutDay(day)||this.state.busy||this.state.editor)return false;this.state.day=day;this.state.head=null;this.state.versions=null;this.state.previousHead=null;this.state.receipt=null;await this.refresh();return true;}
 async period(period:7|30){if(this.state.busy)return;this.state.period=period;await this.refresh();}
 async consent(granted:boolean){if(!this.current()||this.state.busy||!this.state.consent)return;this.state.busy=true;this.emit();
  try{const result=await this.p.client.setConsent(granted,this.state.consent);if(!this.current())return;this.state.notice=result.state==='confirmed'?'Accord mis à jour':'Accord à vérifier';await this.refresh();}finally{this.state.busy=false;this.emit();}}
 editDay(field:NutritionField){if(!this.writable()||!this.state.head)return false;const head=this.state.head;
  this.state.editor={namespace:'DAY',field,head:JSON.parse(JSON.stringify(head)),day:this.state.day,timezone:head.entry?.timezone??this.state.timezone,value:'',clear:false};this.emit();return true;}
 async editTarget(variant:NutritionVariant,effectiveFrom:string,field:NutritionField){
  if(!this.writable()||!nutDay(effectiveFrom))return false;const seq=this.sequence;this.state.busy=true;this.emit();
  try{const result=await this.p.client.head({variant,effective_from:effectiveFrom});if(!this.current(seq)||!this.boundary(result.state)||result.state!=='confirmed')return false;
   this.state.editor={namespace:'TARGET',field,head:result.value,day:this.state.day,timezone:this.state.timezone,variant,effectiveFrom,value:'',clear:false};return true;
  }finally{this.state.busy=false;this.emit();}
 }
 setDraft(value:string){if(!this.current()||this.state.busy||!this.state.editor)return;this.state.editor.value=value;this.state.editor.clear=false;this.emit();}
 clearDraft(){if(!this.current()||this.state.busy||!this.state.editor)return;this.state.editor.clear=true;this.state.editor.value='';this.emit();}
 cancelDraft(){if(this.state.busy)return;this.state.editor=null;this.emit();}
 private command(namespace:NutritionNamespace,head:NutritionHead,operation:string,values:Record<string,number|null>,extras:Record<string,unknown>){
  const path=namespace==='DAY'?`/me/nutrition/days/${head.key.local_day}/revisions`:'/me/nutrition/targets/revisions';
  return nutritionCommand(namespace,path,{contract_version:'nutrition-command/1.0.0',request_id:this.p.newId(),expected_head_token:head.head_token,operation,values,...extras});
 }
 private async send(input:NutritionInput){
  if(!this.writable())return;this.state.busy=true;this.emit();
  try{const result=await this.p.recovery!.send(input);if(!this.current()||!this.boundary(result.state))return;
   this.state.verified=null;
   if(result.state==='rejected'){this.state.refusal=result.code??'refused';this.state.notice=result.code==='stale_head'?'Journée ou cible modifiée · relire avant d’enregistrer':result.code==='stale_target'?'Cible modifiée · choisir sa version actuelle':'Saisie refusée · vérifier les champs avant un nouvel enregistrement';return;}
   this.state.editor=null;
   if(result.state==='confirmed'){this.state.receipt=result.value;this.state.notice='Enregistrement confirmé';await this.refresh();}
   else this.state.notice=result.state==='consent_required'?'Accord requis':'Enregistrement à vérifier';
  }catch{if(this.current()){this.state.notice='Enregistrement à vérifier';await this.pending();if(this.state.pending.some(c=>c.request_id===input.request_id))this.state.editor=null;}}
  finally{if(this.current()){await this.pending();this.state.busy=false;this.emit();}}
 }
 async saveDraft(){const e=this.state.editor;if(!e||!this.writable())return;
  let value:number|null;try{if(!e.clear&&!e.value.length){this.state.notice='Renseigner une valeur ou choisir Effacer ce champ';this.emit();return;}value=e.clear?null:parseNutritionDecimal(e.value);}catch{this.state.notice='Valeur à vérifier · trois décimales au maximum';this.emit();return;}
  await this.send(this.command(e.namespace,e.head,'SET_FIELDS',{[e.field]:value},e.namespace==='DAY'?{timezone:e.timezone,target_ref:null,confirm_complete:null}:{variant:e.variant,effective_from:e.effectiveFrom}));
 }
 private async dayCommand(operation:'COMPLETE'|'SET_TARGET_REF'|'WITHDRAW',extra:{target_ref?:number|null;confirm_complete?:boolean}){if(!this.writable()||!this.state.head?.entry)return;
  await this.send(this.command('DAY',this.state.head,operation,{},{timezone:null,target_ref:extra.target_ref??null,confirm_complete:extra.confirm_complete??null}));}
 setComplete(value:boolean){return this.dayCommand('COMPLETE',{confirm_complete:value});}
 setTarget(reference:number|null){return this.dayCommand('SET_TARGET_REF',{target_ref:reference});}
 withdrawDay(){return this.dayCommand('WITHDRAW',{});}
 async disableEditedTarget(){const e=this.state.editor;if(e?.namespace!=='TARGET'||!e.head.entry||!this.writable())return;
  await this.send(this.command('TARGET',e.head,'DISABLE',{},{variant:e.variant,effective_from:e.effectiveFrom}));}
 async history(namespace:NutritionNamespace,reference:string|number){const seq=this.sequence;const value=await this.versions.load({kind:'versions',namespace,reference});if(!this.current(seq))return;if(!this.boundary(value.state)){this.emit();return;}this.state.versions=value;this.state.versionsNamespace=namespace;this.emit();}
 async reviewRefusal(){if(!this.current()||this.state.busy||!this.state.refusal)return;const editor=this.state.editor;this.state.busy=true;this.emit();
  try{await this.refresh();if(!this.current()||this.state.status!=='confirmed'||!this.state.capabilities?.can_write)return;
   if(editor?.namespace==='TARGET'){const seq=this.sequence,result=await this.p.client.head({variant:editor.variant!,effective_from:editor.effectiveFrom!});if(!this.current(seq)||!this.boundary(result.state)||result.state!=='confirmed')return;editor.head=JSON.parse(JSON.stringify(result.value));}
   else if(editor){if(this.state.head?.key.local_day!==editor.day)return;editor.head=JSON.parse(JSON.stringify(this.state.head));}
   if(editor&&this.state.editor!==editor)return;this.state.refusal=null;this.state.notice='Version actuelle relue · vérifier le brouillon avant de confirmer';
  }finally{this.state.busy=false;this.emit();}
 }
 closeHistory(){this.state.versions=null;this.emit();}
 async verify(command:PendingNutritionCommand){if(!this.current()||this.state.busy||!this.p.recovery)return;this.state.busy=true;this.emit();
  try{const result=await this.p.recovery.verify(command);if(!this.current()||!this.boundary(result.state))return;
   if(result.state==='confirmed'){this.state.notice='Reçu exact retrouvé';this.state.receipt=result.value;this.state.verified=null;await this.refresh();}
   else{this.state.verified=result.state==='unknown'?command.request_id:null;this.state.notice='Résultat à vérifier · aucun nouvel envoi';}
  }catch{if(this.current()){this.state.verified=null;this.state.notice='Résultat à vérifier · reprise indisponible';}}finally{if(this.current()){await this.pending();this.state.busy=false;this.emit();}}
 }
 async replay(command:PendingNutritionCommand){if(!this.current()||this.state.busy||this.state.verified!==command.request_id||!this.p.recovery)return;this.state.busy=true;this.emit();
  try{const result=await this.p.recovery.replay(command);if(!this.current()||!this.boundary(result.state))return;this.state.verified=null;
   if(result.state==='confirmed'){this.state.notice='Reçu exact confirmé';this.state.receipt=result.value;await this.refresh();}else this.state.notice='Résultat toujours à vérifier';
  }catch{if(this.current()){this.state.verified=null;this.state.notice='Résultat toujours à vérifier';}}finally{if(this.current()){await this.pending();this.state.busy=false;this.emit();}}
 }
}
