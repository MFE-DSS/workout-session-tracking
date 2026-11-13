import {NutritionResource} from './nutritionResource';
import {decodeNutritionPage} from './nutritionDTO';

const fields=['kcal_milli','protein_milli','carbohydrate_milli','fat_milli'];
const units=Object.fromEntries(fields.map(k=>[k,{unit:k==='kcal_milli'?'kcal':'g',scale:1000}]));
const page=(id=1,next:string|null=null,read_id='a'.repeat(64))=>({contract_version:'nutrition-manual/1.0.0',owner_id:7,read_id,window:null,entries:[{
 id,revision:1,variant:'STANDARD',effective_from:`2026-11-${id===1?'01':'02'}`,enabled:true,values:{kcal_milli:0,protein_milli:null,carbohydrate_milli:null,fat_milli:null},units,
 provenance:{fields:{kcal_milli:{origin:'USER_DEFINED_TARGET',method:'MANUAL_ENTRY',source_ref:`nutrition_target_revisions_v1/${id}/kcal_milli`}},date:{origin:'USER_DECLARED',precision:'LOCAL_DAY',source_ref:`nutrition_target_revisions_v1/${id}`}},recorded_at:'2026-11-12T00:00:00Z',head_token:'b'.repeat(64),
}],next_cursor:next,collection_state:next===null?'COMPLETE':'PARTIAL'});
test('typed DTO refuses wrong units, foreign provenance, unknown defaults and inconsistent completeness',()=>{
 const good=page();expect(decodeNutritionPage(good,7,{kind:'targets',limit:1})).not.toBeNull();
 const variants=[{...good,owner_id:8},{...good,collection_state:'PARTIAL'},{...good,extra:1},{...good,entries:[{...good.entries[0],values:{...good.entries[0].values,protein_milli:undefined}}]},
 {...good,entries:[{...good.entries[0],units:{...units,kcal_milli:{unit:'g',scale:1000}}}]},
 {...good,entries:[{...good.entries[0],provenance:{fields:{kcal_milli:{origin:'USER_DEFINED_TARGET',method:'MANUAL_ENTRY',source_ref:'nutrition_target_revisions_v1/99/kcal_milli'}}}}]},
 {...good,entries:[{...good.entries[0],provenance:{fields:{}}}]}];
 for(const raw of variants)expect(decodeNutritionPage(raw,7,{kind:'targets',limit:1})).toBeNull();
});
test('resource only certifies one complete snapshot; a lost continuation keeps explicit partial state',async()=>{
 const calls:any[]=[];let fail=true;
 const client:any={ownerId:7,backendScope:'https://qa.invalid',read:async(o:any)=>{calls.push(o);return o.cursor?(fail?{state:'unknown'}:{state:'confirmed',value:page(2,null)}):{state:'confirmed',value:page(1,'cursor-1')};}};
 const r=new NutritionResource(client,()=>true);
 const interrupted=await r.load({kind:'targets',limit:1});expect(interrupted.state).toBe('partial');
 expect(interrupted.value?.collection_state).toBe('PARTIAL');expect(interrupted.value?.entries).toHaveLength(1);
 fail=false;const complete=await r.resume();expect(complete.state).toBe('confirmed');expect(complete.value?.entries).toHaveLength(2);
 expect(calls.filter(c=>!c.cursor)).toHaveLength(1);
});
test.each(['changed_read_id','duplicate','cursor_loop'])('mixed or looping collection rejected: %s',async cause=>{
 let count=0;const client:any={ownerId:7,read:async()=>({state:'confirmed',value:++count===1?page(1,'cursor-1'):page(cause==='duplicate'?1:2,cause==='cursor_loop'?'cursor-1':null,cause==='changed_read_id'?'c'.repeat(64):'a'.repeat(64))})};
 const state=await new NutritionResource(client,()=>true).load({kind:'targets',limit:1});
 expect(state.state).toBe('unknown');expect(state.value).toBeNull();expect(count).toBe(2);
});
test('late account change cancels without exposing previous data',async()=>{
 let current=true;const client:any={ownerId:7,read:async()=>{current=false;return{state:'confirmed',value:page()};}};
 const state=await new NutritionResource(client,()=>current).load({kind:'targets'});
 expect(state).toEqual({state:'cancelled',value:null,previous:null});
});
test('empty complete collection with known totals is incoherent, not a confirmed nutrition log',async()=>{
 const coverage=Object.fromEntries(fields.map(f=>[f,{known_days:f==='kcal_milli'?1:0,missing_days:f==='kcal_milli'?0:1,partial_days:1,declared_complete_days:0,withdrawn_days:0,total_calendar_days:1}]));
 const totals=Object.fromEntries(fields.map(f=>[f,{value:f==='kcal_milli'?1000:null,known_days:f==='kcal_milli'?1:0}]));
 const raw={...page(),window:{from:'2026-11-12',through:'2026-11-12'},entries:[],coverage,totals};
 const options={kind:'days' as const,from:'2026-11-12',through:'2026-11-12'};
 expect(decodeNutritionPage(raw,7,options)).toBeNull();
 const client:any={ownerId:7,read:async()=>({state:'confirmed',value:raw})};
 expect((await new NutritionResource(client,()=>true).load(options)).state).toBe('unknown');
});
