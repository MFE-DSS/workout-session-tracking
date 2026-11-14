import {BodyMeasurementsResource,BodyWeightWindowResource,BodyErasureResource} from './bodyMeasurementsResource';
import type {BodyPage} from './bodyMeasurements';
const auth:any={revision:1};
const page=(id=11,day='2026-11-11'):BodyPage=>({contract_version:'body-measurements/1.0.0',owner_id:7,body_revision:1,state:'AVAILABLE',next_cursor:null,window:{from:null,through:null},field_specs:[],entries:[{measurement_id:id,root_ref:id,revision:1,state:'CURRENT',head_token:'a'.repeat(64),date_precision:'DAY_UTC_CONVENTION',timezone_basis:'DATABASE_UTC_CONVENTION',measured_at:day+'T00:00:00Z',recorded_at:day+'T15:00:00Z',fields:{weight_kg:{value:72,quality:'KNOWN',raw_value_repr:null,unit:'kg',provenance:{origin:'USER_DECLARED',acquisition:'MANUAL_ENTRY',source_ref:`body_measurements/${id}/weight_kg`}}} as any}]});
beforeEach(()=>{auth.revision=1;});
test('same query may retain previous memory after network failure, consent withdrawal clears facts',async()=>{
 let outcome:any={state:'confirmed',value:page()};const r=new BodyMeasurementsResource(auth,{read:async()=>outcome} as any);
 await r.refresh({mode:'weight'});outcome={state:'unknown'};await r.refresh({mode:'weight'});expect(r.state).toMatchObject({status:'unknown',previous:true,value:{entries:[{measurement_id:11}]}});
 outcome={state:'consent_required'};await r.refresh({mode:'weight'});expect(r.state.value).toBeUndefined();
});
test('account change discards a delayed result; changed query never borrows previous facts',async()=>{
 let resolve!:(v:any)=>void;const r=new BodyMeasurementsResource(auth,{read:()=>new Promise(done=>{resolve=done;})} as any);
 const pending=r.refresh();auth.revision++;resolve({state:'confirmed',value:page()});await pending;expect(r.state.value).toBeUndefined();
});
test('declared UTC day remains the selected calendar day west of UTC, without inventing an instant',async()=>{
 const source=new BodyMeasurementsResource(auth,{read:async()=>({state:'confirmed',value:page()})} as any);
 const r=new BodyWeightWindowResource(auth,source);await r.refresh({period:'4w',time_zone:'America/New_York',from:'2026-11-11T05:00:00Z',until:'2026-11-12T05:00:00Z'} as any);
 expect(r.state.entries).toHaveLength(1);expect((r.state.entries[0] as any).bodySource.date_precision).toBe('DAY_UTC_CONVENTION');
});
test('mixed revisions across pages cannot silently produce a current chronology',async()=>{
 let second=false;const p=page();p.next_cursor='next';const r=new BodyMeasurementsResource(auth,{read:async()=>{if(!second){second=true;return{state:'confirmed',value:p};}return{state:'confirmed',value:{...page(12),body_revision:2}};}} as any);
 await r.refresh();await r.loadNext();expect(r.state.status).toBe('changed');expect(r.state.value).toBeUndefined();
});
test('the current declared day is included before the end-of-day without assigning an hour',async()=>{
 const source=new BodyMeasurementsResource(auth,{read:async()=>({state:'confirmed',value:page()})} as any);
 const r=new BodyWeightWindowResource(auth,source);await r.refresh({period:'4w',time_zone:'Europe/Paris',from:'2026-11-10T23:00:00Z',until:'2026-11-11T12:30:00Z'} as any);
 expect(r.state.entries).toHaveLength(1);
});
const erasurePage=(id=11)=>({contract_version:'body-measurements/1.0.0',owner_id:7,body_revision:1,projection:'ERASURE_ONLY',state:'AVAILABLE',window:{from:null,through:null},next_cursor:null,
 entries:[{root_ref:id,measurement_id:id,revision:1,head_token:'a'.repeat(64),measured_at:'2025-01-02T00:00:00Z',date_precision:'DAY_UTC_CONVENTION',version_count:1}]});
test('erasure pages retain metadata only and reject repeated roots across a traversal',async()=>{
 let second=false;const first:any={...erasurePage(),next_cursor:'next'};
 const resource=new BodyErasureResource({revision:1} as any,{readErasure:async()=>{if(!second){second=true;return{state:'confirmed',value:first};}return{state:'confirmed',value:{...erasurePage(12),entries:[{...erasurePage().entries[0],measurement_id:12}]}};}} as any);
 await resource.refresh();expect(resource.state.value?.entries[0]).not.toHaveProperty('fields');
 await resource.loadNext();expect(resource.state.status).toBe('changed');expect(resource.state.value).toBeUndefined();
});
test('a late erasure page cannot remain visible after an account revision change',async()=>{
 const current={revision:1} as any;let finish!:(v:any)=>void;
 const resource=new BodyErasureResource(current,{readErasure:()=>new Promise(resolve=>{finish=resolve;})} as any);
 const loading=resource.refresh();current.revision++;finish({state:'confirmed',value:erasurePage()});await loading;
 expect(resource.state.status).toBe('idle');expect(resource.state.value).toBeUndefined();
});
test('an interrupted erasure read remains previous and cannot be treated as an empty result',async()=>{
 let fail=false;const resource=new BodyErasureResource({revision:1} as any,{readErasure:async()=>fail?{state:'unknown'}:{state:'confirmed',value:erasurePage()}} as any);
 await resource.refresh();fail=true;await resource.refresh();expect(resource.state.status).toBe('unknown');expect(resource.state.previous).toBe(true);expect(resource.state.value?.entries).toHaveLength(1);
});
