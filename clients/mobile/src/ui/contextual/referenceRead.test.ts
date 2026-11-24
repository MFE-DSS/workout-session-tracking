import {accountHarness,deferred,reply} from '../../../test/accountDataHarness';
import {contextualFixture} from '../../../test/contextualHarness';
import {TrainingHistoryClient} from '../../api/trainingHistory';
import {FirstSessionV3Client} from '../../api/firstSessionV3';
import {RuntimeV3Client,V3_VERSIONS} from '../../api/firstPlanV3';
import {contextTarget} from './referenceModel';
import {readContext} from './referenceRead';
async function setup(){const h=await accountHarness(),f=contextualFixture();f.page.window={period:'all',time_zone:'UTC',from:null,until:f.page.window.until};f.page.weekly_counts=[];
 const runtime=new RuntimeV3Client(h.auth,h.call,async()=>({owner_id:7,contract_version:V3_VERSIONS.runtime,versions:V3_VERSIONS,execution:f.execution}));
 const reader=new TrainingHistoryClient(h.auth,h.call,new FirstSessionV3Client(runtime));
 h.handle(async path=>path.startsWith('/me/training-history?')?reply(f.page):reply({detail:{error:'execution_profile_required'}},409));
 return{h,f,reader,target:contextTarget(f.state,f.set.set_id)!};
}
test('real authenticated client reads same SCI occurrence through signed history and typed existing endpoint',async()=>{
 const {h,reader,target}=await setup(),r=await readContext(reader,target,()=>true);
 expect(r).toMatchObject({state:'ready',reference:{value:17.5,reps:9},current:null,indexReadId:'c'.repeat(32)});
 expect(h.calls.filter(x=>x.body!==null).map(x=>x.path)).toEqual(['/auth/login']);
});
test('owner mismatch cannot expose even a correctly typed source',async()=>{
 const {reader,target}=await setup();expect(await readContext(reader,{...target,ownerId:8},()=>true)).toEqual({state:'unknown'});
});
test('an unknown GET cannot be interpreted as no prior performance',async()=>{
 const {h,reader,target}=await setup();h.handle(async()=>reply({},503));expect(await readContext(reader,target,()=>true)).toEqual({state:'unknown'});
});
test('late response after resource invalidation never returns source values',async()=>{
 const {h,f,reader,target}=await setup(),d=deferred<Response>();let active=true;h.handle(async()=>d.promise);const pending=readContext(reader,target,()=>active);
 for(let i=0;i<25;i++)await Promise.resolve();active=false;d.resolve(reply(f.page));expect(await pending).toEqual({state:'cancelled'});
});
test('scan bound never becomes complete absence and duplicate cursor cannot loop',async()=>{
 const {reader,target,f}=await setup();let pages=0;const fake={sessions:async()=>{pages++;return{state:'confirmed',value:{...f.page,entries:[],next_cursor:'same',completeness:'MORE_AVAILABLE'}};},detail:reader.detail.bind(reader)} as any;
 expect(await readContext(fake,target,()=>true)).toEqual({state:'unknown'});expect(pages).toBe(2);
});
