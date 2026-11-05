/** First-use read orchestration. No Blueprint construction or recommendation fallback. */
import { AuthSession } from '../auth/authSession';
import { ApiFailure, type Transport } from './http';
import { FirstPlanClient, type FirstPlanInput } from './firstPlan';
import { TrainingPreferencesClient } from './trainingPreferences';

/** Future trusted canonical adapter, absent in production. Not a new HTTP schema. */
export type BlueprintSource = {read(token:string):Promise<{owner_id:number;input:FirstPlanInput}>};
export type FirstUseState =
 | {state:'loading'} | {state:'unknown'} | {state:'no_plan_producer'}
 | {state:'required_consent'} | {state:'missing_information';missing:string[]}
 | {state:'unavailable';reason:string};
const copy=<T>(x:T):T=>JSON.parse(JSON.stringify(x));
export class FirstUseController {
 private value:FirstUseState={state:'loading'};
 private generation:number;
 private sequence=0;
 private listeners=new Set<()=>void>();
 constructor(private readonly auth:AuthSession,private readonly call:Transport,
  private readonly preferences:TrainingPreferencesClient,private readonly plan:FirstPlanClient,
  private readonly blueprint:BlueprintSource|null=null){this.generation=auth.revision;}
 get state():FirstUseState{return this.generation===this.auth.revision?copy(this.value):{state:'unknown'};}
 subscribe(listener:()=>void){this.listeners.add(listener);return()=>{this.listeners.delete(listener);};}
 invalidate(){++this.sequence;this.value={state:'unknown'};this.emit();}
 private emit(){this.listeners.forEach(listener=>listener());}
 async load():Promise<FirstUseState>{
  const revision=this.auth.revision,sequence=++this.sequence;
  this.generation=revision;
  const current=()=>revision===this.auth.revision&&sequence===this.sequence;
  const finish=(state:FirstUseState):FirstUseState=>{if(!current())return{state:'unknown'};this.value=copy(state);this.emit();return copy(state);};
  this.value={state:'loading'};this.emit();
  try{
   const declarations=await this.preferences.read();
   if(!current())return{state:'unknown'};
   if(declarations.state==='unknown'||declarations.state==='cancelled')return finish({state:'unknown'});
   if(declarations.state==='rejected')return finish({state:'unavailable',reason:'PREFERENCES_UNAVAILABLE'});
   // Missing preferences are not a scientific insufficiency assessment. Weight,
   // anthropometry, priorities and an inventory never become local prerequisites.
   if(!this.blueprint)return finish({state:'no_plan_producer'});
   const owner=await this.auth.authorized(token=>this.call<{id:number}>('/auth/me',{token}));
   if(!current()||!Number.isSafeInteger(owner?.id)||owner.id<=0)return finish({state:'unknown'});
   const snapshot=await this.auth.authorized(token=>this.blueprint!.read(token),{retryUnauthorized:false});
   if(!current()||snapshot?.owner_id!==owner.id)return finish({state:'unknown'});
   const result=await this.plan.load(snapshot.input);
   if(!current())return{state:'unknown'};
   switch(result.state){
    case 'pending':return finish({state:'loading'});
    case 'unknown':return finish({state:'unknown'});
    case 'insufficient_information':return finish({state:'missing_information',missing:result.missing});
    case 'rejected':return finish(result.code==='body_consent_required'?{state:'required_consent'}:{state:'unavailable',reason:'PLAN_REJECTED'});
    case 'unavailable':return finish(result.reason==='NOT_SERVED'?{state:'no_plan_producer'}:{state:'unavailable',reason:result.reason});
    case 'available':
     // A scientifically valid proposal is not an executable owned workout.
     // No canonical first-session handoff exists yet; do not start MISSION as a fallback.
     return finish({state:'unavailable',reason:'SESSION_HANDOFF_NOT_SERVED'});
   }
  }catch(error){return finish(error instanceof ApiFailure&&error.code==='body_consent_required'&&error.status===403
    ?{state:'required_consent'}:{state:'unknown'});}
 }
}
