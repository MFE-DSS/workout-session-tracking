/** Typed factual outbox dispatch; first-session start is never part of automatic replay. */
import {ApiFailure} from '../api/http';
import type {FirstSessionV3Client} from '../api/firstSessionV3';
import type {PlanV3Journal} from '../storage/planV3Journal';
import type {OutboxRow} from '../storage/outbox';
import {isObject,positiveId,revision} from '../api/firstPlanV3';
export async function sendPlanV3Outbox(row:OutboxRow,client:FirstSessionV3Client,journal:PlanV3Journal,current:()=>boolean){
 if(!current())throw new ApiFailure('http',401,'stale_identity');
 const body=JSON.parse(row.payload);
 if(row.kind!=='PLAN_V3_SET'||!isObject(body)||body.op_id!==row.op_id||!positiveId(body.session_id)||!positiveId(body.set_id)||!revision(body.expected_set_revision)||!isObject(body.observation))throw new ApiFailure('http',422,'invalid_typed_operation');
 const result=await client.recordSet(body.session_id,body.set_id,body.op_id,body.expected_set_revision,body.observation as never,current);
 if(!current()||result.state==='cancelled')throw new ApiFailure('http',401,'stale_identity');
 if(result.state==='confirmed'){await journal.acknowledge(row.op_id,current);return result.value;}
 if(result.state==='rejected'){await journal.reject(row.op_id,current,result.code);throw new ApiFailure('http',result.status,result.code);}
 throw new ApiFailure('network');
}
