import type {BodyMeasurementsClient,BodyOutcome,BodyReceipt} from '../api/bodyMeasurements';
import type {BodyCommandInput,BodyPendingCommands,PendingBodyCommand} from '../storage/bodyPendingCommands';
/** No background/offline writes. Verification and replay are separate user actions. */
export class BodyCommandRecovery{
 private verified=new Set<string>();
 constructor(private client:BodyMeasurementsClient,private store:BodyPendingCommands,private current:()=>boolean){}
 private owned(command:PendingBodyCommand){return this.current()&&command.owner_id===this.client.ownerId&&command.backend_scope===this.client.backendScope;}
 private terminal(command:PendingBodyCommand):BodyOutcome<BodyReceipt>|null{
  if(command.state==='ACKED')return{state:'confirmed',value:command.receipt!};
  // 409 describes this local terminal conflict, not the historical HTTP status.
  if(command.state==='REJECTED')return{state:'rejected',code:command.rejection,status:409};
  return null;
 }
 private async apply(command:PendingBodyCommand,outcome:BodyOutcome<BodyReceipt>,freshAttempt=false){
  if(!this.owned(command))return {state:'cancelled'} as const;
  if(outcome.state==='confirmed')await this.store.ack(command.request_id,outcome.value,this.current);
  // A refusal of lookup/replay cannot prove an earlier unknown attempt failed.
  if(freshAttempt&&(outcome.state==='rejected'||outcome.state==='consent_required'))await this.store.reject(command.request_id,outcome.state==='rejected'?outcome.code??'rejected':'body_consent_required',this.current);
  return this.current()?outcome:{state:'cancelled'} as const;
 }
 async send(input:BodyCommandInput):Promise<BodyOutcome<BodyReceipt>>{
  if(!this.current())return{state:'cancelled'};
  const prior=await this.store.read(input.request_id);
  if(prior){
   const exact=await this.store.prepare(input,this.current);
   if(!this.owned(exact))return{state:'cancelled'};
   const terminal=this.terminal(exact);if(terminal)return terminal;
   if(exact.state==='SENT_UNKNOWN')throw Error('body_verification_required');
  }
  if(!input.path.endsWith('/erase')){const consent=await this.client.consent();if(!this.current())return{state:'cancelled'};if(consent.state!=='confirmed')return consent;if(!consent.value.granted)return{state:'consent_required'};}
  const command=await this.store.prepare(input,this.current);
  if(!this.owned(command))return{state:'cancelled'};
  const terminal=this.terminal(command);if(terminal)return terminal;
  if(command.state==='SENT_UNKNOWN')throw Error('body_verification_required');
  // SENT_UNKNOWN is durable before the network starts, including force-kill.
  await this.store.markUnknown(command.request_id,this.current,true);
  const durable=await this.store.read(command.request_id);if(!durable)throw Error('body_prepare_not_durable');
  if(!this.current())return{state:'cancelled'};
  return this.apply(durable,await this.client.submit(durable),true);
 }
 async verify(command:PendingBodyCommand):Promise<BodyOutcome<BodyReceipt>>{
  if(!this.owned(command))return{state:'cancelled'};
  const saved=await this.store.read(command.request_id);if(!saved||saved.body_digest!==command.body_digest)throw Error('body_command_missing');
  if(!this.owned(saved))return{state:'cancelled'};
  const terminal=this.terminal(saved);if(terminal)return terminal;
  const result=await this.client.status(saved);if(!this.current())return{state:'cancelled'};
  if(result.state==='unknown')this.verified.add(saved.request_id);else this.verified.delete(saved.request_id);
  return this.apply(saved,result);
 }
 async replay(command:PendingBodyCommand):Promise<BodyOutcome<BodyReceipt>>{
  if(!this.owned(command))return{state:'cancelled'};
  const saved=await this.store.read(command.request_id);
  if(!saved||saved.body_digest!==command.body_digest)throw Error('body_command_missing');
  if(!this.owned(saved))return{state:'cancelled'};
  const terminal=this.terminal(saved);if(terminal)return terminal;
  if(!this.verified.delete(command.request_id))throw Error('body_verification_required');
  if(!this.current())return{state:'cancelled'};
  await this.store.markUnknown(saved.request_id,this.current);
  return this.apply(saved,await this.client.submit(saved));
 }
}
