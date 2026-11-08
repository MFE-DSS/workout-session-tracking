import {compactPending,type OutboxRow} from './outbox';
test('typed corrections retain insertion order even when the device clock goes backwards',()=>{
 const row=(id:string,kind:string,time:number):OutboxRow=>({op_id:id,kind,target:'set/1',payload:'{}',created_at_ms:time,attempts:0,state:'pending'});
 const rows=[row('old','SET_COMPLETION',300),row('first','PLAN_V3_SET',200),row('correction','PLAN_V3_SET',100)];
 expect(compactPending(rows).map(r=>r.op_id)).toEqual(['old','first','correction']);
});
