import type {NutritionClient,NutritionOutcome,NutritionReceipt} from '../api/nutrition';
import type {NutritionInput} from '../domain/nutritionCommand';
import type {NutritionPendingCommands,PendingNutritionCommand} from '../storage/nutritionPendingCommands';
/** Explicit user verification/replay only. No background nutrition mutation. */
export class NutritionRecovery{
 private verified=new Set<string>();
 constructor(private client:NutritionClient,private store:NutritionPendingCommands,private current:()=>boolean){}
 private key(command:PendingNutritionCommand){return command.namespace+'/'+command.request_id+'/'+command.body_digest;}
 private owned(command:PendingNutritionCommand){return this.current()&&command.owner_id===this.client.ownerId&&command.backend_scope===this.client.backendScope;}
 private async apply(command:PendingNutritionCommand,outcome:NutritionOutcome<NutritionReceipt>,freshAttempt=false){
  if(!this.owned(command))return{state:'cancelled'} as const;
  if(outcome.state==='confirmed')await this.store.ack(command.namespace,command.request_id,outcome.value,this.current);
  // A lookup/replay refusal says nothing about an earlier unknown application.
  if(freshAttempt&&(outcome.state==='rejected'||outcome.state==='consent_required'))await this.store.conflict(command.namespace,command.request_id,outcome.state==='rejected'?outcome.code??'rejected':'consent_required',this.current);
  return this.current()?outcome:{state:'cancelled'} as const;
 }
 private async consent():Promise<NutritionOutcome<NutritionReceipt>|null>{
  const outcome=await this.client.consent();if(!this.current())return{state:'cancelled'};
  if(outcome.state!=='confirmed')return outcome;
  return outcome.value.granted&&outcome.value.wording_version===outcome.value.current_wording_version?null:{state:'consent_required'};
 }
 async send(input:NutritionInput):Promise<NutritionOutcome<NutritionReceipt>>{
  if(!this.current())return{state:'cancelled'};
  const consent=await this.consent();if(consent)return consent;
  const command=await this.store.prepare(input,this.current);
  if(command.state==='ACKED')return{state:'confirmed',value:command.receipt!};
  if(command.state==='CONFLICT')return{state:'rejected',code:command.rejection,status:409};
  if(command.state==='SENT_UNKNOWN')throw Error('nutrition_verification_required');
  const fresh=await this.consent();if(fresh)return fresh;
  await this.store.markUnknown(command.namespace,command.request_id,this.current,true);
  const durable=await this.store.read(command.namespace,command.request_id);if(!durable)throw Error('nutrition_prepare_not_durable');
  if(!this.owned(durable))return{state:'cancelled'};
  return this.apply(durable,await this.client.submit(durable),true);
 }
 async verify(command:PendingNutritionCommand):Promise<NutritionOutcome<NutritionReceipt>>{
  if(!this.owned(command))return{state:'cancelled'};
  const saved=await this.store.read(command.namespace,command.request_id);if(!saved||saved.body_digest!==command.body_digest)throw Error('nutrition_command_missing');
  if(saved.state==='ACKED')return{state:'confirmed',value:saved.receipt!};
  if(saved.state==='CONFLICT')return{state:'rejected',code:saved.rejection,status:409};
  const outcome=await this.client.status(saved);if(!this.current())return{state:'cancelled'};
  if(outcome.state==='unknown')this.verified.add(this.key(saved));else this.verified.delete(this.key(saved));
  return this.apply(saved,outcome);
 }
 async replay(command:PendingNutritionCommand):Promise<NutritionOutcome<NutritionReceipt>>{
  if(!this.owned(command))return{state:'cancelled'};
  if(!this.verified.delete(this.key(command)))throw Error('nutrition_verification_required');
  const saved=await this.store.read(command.namespace,command.request_id);
  if(!saved||saved.body_digest!==command.body_digest||!['PREPARED','SENT_UNKNOWN'].includes(saved.state))throw Error('nutrition_command_missing');
  if(!this.current())return{state:'cancelled'};
  await this.store.markUnknown(saved.namespace,saved.request_id,this.current);
  return this.apply(saved,await this.client.submit(saved));
 }
}
