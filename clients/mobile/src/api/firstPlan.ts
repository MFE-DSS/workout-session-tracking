/** SCI consumer only. No default endpoint, exercise selection, dose policy or fallback. */
import { AuthSession } from '../auth/authSession';
import { ApiFailure, type Transport } from './http';
import schemas from './firstPlan.contract.json';
import { scienceSchemaMatches } from './scienceSchema';
export type FirstPlanInput = { request: unknown; fingerprint: string };
/** A future trusted producer must verify canonical fingerprint AND validate_exchange
 * against the real policy/catalogue registry. A JSON schema alone cannot approve READY.
 */
export type FirstPlanProducer = {
  read(token: string, input: FirstPlanInput): Promise<unknown>;
  verify(token: string, input: FirstPlanInput, recommendation: unknown): Promise<boolean>;
};
type Status='READY'|'INSUFFICIENT_DATA'|'CONFLICTING_DATA'|'POLICY_UNAVAILABLE'|'CONSTRAINT_UNSATISFIABLE'|'REVIEW_REQUIRED';
export type FirstPlanOutcome =
  | {state:'available';status:'READY';recommendation:Record<string,unknown>}
  | {state:'insufficient_information';status:'INSUFFICIENT_DATA';missing:string[]}
  | {state:'rejected';status?:Status;code?:string|null}
  | {state:'unavailable';status?:Status;reason:string}
  | {state:'pending'} | {state:'unknown'};
const clone = <T>(v:T):T => JSON.parse(JSON.stringify(v));
export class FirstPlanClient {
  private value:FirstPlanOutcome={state:'unavailable',reason:'NOT_SERVED'};
  private generation:number;
  private sequence=0;
  constructor(private readonly auth:AuthSession,private readonly call:Transport,private readonly producer:FirstPlanProducer|null=null){this.generation=auth.revision;}
  get state():FirstPlanOutcome{return this.generation===this.auth.revision?clone(this.value):{state:'unknown'};}
  async load(input:FirstPlanInput):Promise<FirstPlanOutcome>{
    const revision=this.auth.revision, sequence=++this.sequence;
    this.generation=revision;
    const current=()=>revision===this.auth.revision&&sequence===this.sequence;
    const finish=(value:FirstPlanOutcome):FirstPlanOutcome=>{if(!current())return{state:'unknown'};this.value=clone(value);return clone(value);};
    if(!this.producer)return finish({state:'unavailable',reason:'NOT_SERVED'});
    this.value={state:'pending'};
    if(!/^[a-f0-9]{64}$/.test(input.fingerprint)||!scienceSchemaMatches(input.request,schemas.request))return finish({state:'unknown'});
    const captured=clone(input);
    try{
      const owner=await this.auth.authorized((token)=>this.call<{id:number}>('/auth/me',{token}));
      if(!current()||!Number.isSafeInteger(owner?.id)||owner.id<=0)return finish({state:'unknown'});
      const result=await this.auth.authorized(async(token):Promise<FirstPlanOutcome>=>{
        const envelope=await this.producer!.read(token,captured) as any;
        if(!current()||!envelope||envelope.owner_id!==owner.id)return{state:'unknown'};
        if(envelope.kind==='pending')return{state:'pending'};
        if(envelope.kind==='unavailable')return{state:'unavailable',reason:'NOT_SERVED'};
        if(envelope.kind==='rejected')return{state:'rejected'};
        if(envelope.kind!=='result'||!scienceSchemaMatches(envelope.result,schemas.response))return{state:'unknown'};
        const raw=envelope.result;
        const request=captured.request as any;
        if(raw.request_fingerprint!==captured.fingerprint||raw.engine_version!==request.versions.engine)return{state:'unknown'};
        if(!await this.producer!.verify(token,captured,raw)||!current())return{state:'unknown'};
        switch(raw.status as Status){
          case 'READY':
            if(!request.versions.engine||request.policies.state!=='APPROVED'||!raw.candidate_plan||raw.candidate_plan.review_state!=='REVIEWED')return{state:'unknown'};
            return{state:'available',status:'READY',recommendation:clone(raw)};
          case 'INSUFFICIENT_DATA':return{state:'insufficient_information',status:raw.status,missing:[...raw.assessment.missing_fields]};
          case 'CONFLICTING_DATA': case 'CONSTRAINT_UNSATISFIABLE':return{state:'rejected',status:raw.status};
          case 'POLICY_UNAVAILABLE': case 'REVIEW_REQUIRED':return{state:'unavailable',status:raw.status,reason:raw.status};
        }
        return{state:'unknown'};
      },{retryUnauthorized:false});
      return finish(result);
    }catch(error){
      return finish(error instanceof ApiFailure&&error.kind==='http'&&error.status>=400&&error.status<500&&error.status!==408
        ?{state:'rejected',code:error.code}:{state:'unknown'});
    }
  }
}
