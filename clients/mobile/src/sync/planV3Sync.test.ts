import {sendPlanV3Outbox} from './planV3Sync';
import type {OutboxRow} from '../storage/outbox';
test('mixed dispatcher sends exact typed operation and waits for owned local ack; unknown stays retryable',async()=>{
 const calls:string[]=[],payload={session_id:12,set_id:14,op_id:'same',expected_set_revision:2,observation:{reps:8}};
 const row:OutboxRow={op_id:'same',kind:'PLAN_V3_SET',target:'set/14',payload:JSON.stringify(payload),created_at_ms:1,attempts:0,state:'pending'};
 const client:any={recordSet:async(...args:any[])=>{expect(args.slice(0,5)).toEqual([12,14,'same',2,{reps:8}]);calls.push('HTTP');return{state:'confirmed',value:{state:'APPLIED'}};}};
 const journal:any={acknowledge:async()=>{calls.push('ACK');}};
 await sendPlanV3Outbox(row,client,journal,()=>true);expect(calls).toEqual(['HTTP','ACK']);
 client.recordSet=async()=>({state:'unknown'});
 await expect(sendPlanV3Outbox(row,client,journal,()=>true)).rejects.toMatchObject({kind:'network'});
 expect(calls).toEqual(['HTTP','ACK']);
});
test('a confirmed refusal is projected into the owned local journal and is never acknowledged',async()=>{
 const payload={session_id:12,set_id:14,op_id:'refused',expected_set_revision:1,observation:{reps:8}};
 const row:OutboxRow={op_id:'refused',kind:'PLAN_V3_SET',target:'set/14',payload:JSON.stringify(payload),created_at_ms:1,attempts:0,state:'pending'};
 const journal:any={acknowledge:jest.fn(),reject:jest.fn(async()=>{})};
 const client:any={recordSet:async()=>({state:'rejected',status:409,code:'set_revision_changed'})},current=()=>true;
 await expect(sendPlanV3Outbox(row,client,journal,current)).rejects.toMatchObject({status:409,code:'set_revision_changed'});
 expect(journal.reject).toHaveBeenCalledWith('refused',current,'set_revision_changed');expect(journal.acknowledge).not.toHaveBeenCalled();
});
