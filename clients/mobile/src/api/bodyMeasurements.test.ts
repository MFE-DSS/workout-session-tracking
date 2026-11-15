import {AuthSession} from '../auth/authSession';
import {ApiFailure,type Transport} from './http';
import {BodyMeasurementsClient,createBodyTransport,bodyCommandCanonical} from './bodyMeasurements';

const scope='http://127.0.0.1:8173';
const pair={access_token:'test-access',refresh_token:'rt1.test.secret',access_expires_in:900,server_now:'2026-11-11T12:00:00Z'};
const keys=['weight_kg','waist_cm','neck_cm','chest_cm','shoulder_width_cm','arm_cm_left','arm_cm_right','thigh_cm_left','thigh_cm_right','hip_cm','calf_cm_left','calf_cm_right','wingspan_cm'];
function fixture(){
 const fields=Object.fromEntries([...keys,'calf_cm'].map(key=>[key,{value:null,raw_value_repr:null,quality:'MISSING',unit:key==='weight_kg'?'kg':'cm',provenance:{origin:'UNKNOWN',acquisition:'UNKNOWN',source_ref:`body_measurements/11/${key}`}}]));
 fields.weight_kg={value:72,raw_value_repr:null,quality:'KNOWN',unit:'kg',provenance:{origin:'USER_DECLARED',acquisition:'MANUAL_ENTRY',source_ref:'body_measurements/11/weight_kg'}} as any;
 return {contract_version:'body-measurements/1.0.0',owner_id:7,body_revision:1,state:'AVAILABLE',next_cursor:null,window:{from:'2026-11-01',through:'2026-11-11'},
  field_specs:keys.map(key=>({key,label:key,min:1,max:500,unit:key==='weight_kg'?'kg':'cm'})),
  entries:[{root_ref:11,measurement_id:11,revision:1,state:'CURRENT',head_token:'a'.repeat(64),measured_at:'2026-11-11T00:00:00+00:00',recorded_at:'2026-11-11T12:00:00+00:00',date_precision:'DAY_UTC_CONVENTION',timezone_basis:'DATABASE_UTC_CONVENTION',fields}]};
}
async function setup(reply:(path:string,init?:any)=>Promise<unknown>){
 let credential:string|null=null;
 let owner=7;
 const call:Transport=async(path)=>{if(path==='/auth/me')return{id:owner} as any;if(path==='/auth/logout')return undefined as any;return pair as any;};
 const auth=new AuthSession(call,{read:async()=>credential,write:async(v)=>{credential=v;},clear:async()=>{credential=null;}});
 await auth.login('body-owner','synthetic',null);
 const bodyCall:Transport=async(path,init)=>await reply(path,init) as any;
 return {auth,setOwner:(next:number)=>{owner=next;},client:new BodyMeasurementsClient(auth,call,{scope,call:bodyCall},7)};
}
function erasureFixture(){
 const full=fixture(),row=full.entries[0];
 return {contract_version:full.contract_version,owner_id:full.owner_id,body_revision:1,
  projection:'ERASURE_ONLY',state:'AVAILABLE',window:{from:null,through:null},next_cursor:null,
  entries:[{root_ref:row.root_ref,measurement_id:row.measurement_id,revision:row.revision,
   head_token:row.head_token,measured_at:row.measured_at,date_precision:row.date_precision,version_count:1}]};
}
test('erasure discovery uses a separate closed projection and exact owned head without consent grant',async()=>{
 const value=erasureFixture(),paths:string[]=[];const s=await setup(async path=>{paths.push(path);return path.includes('/11?')?{contract_version:value.contract_version,owner_id:7,projection:'ERASURE_ONLY',entry:value.entries[0]}:value;});
 expect(await s.client.readErasure()).toEqual({state:'confirmed',value});
 expect(await s.client.erasureHead(11)).toEqual({state:'confirmed',value:value.entries[0]});
 expect(paths).toEqual(['/me/body/measurements?purpose=erasure&limit=50','/me/body/measurements/11?purpose=erasure']);
 expect((await s.client.read()).state).toBe('unknown');
});
test.each(['owner','numeric_fields','specs','projection','head_token','root','revision','count','window'])('invalid erasure %s projection is never confirmed',async kind=>{
 const value:any=erasureFixture();
 if(kind==='owner')value.owner_id=8;
 if(kind==='numeric_fields')value.entries[0].fields=fixture().entries[0].fields;
 if(kind==='specs')value.field_specs=fixture().field_specs;
 if(kind==='projection')delete value.projection;
 if(kind==='head_token')value.entries[0].head_token='invalid';
 if(kind==='root')value.entries[0].root_ref=12;
 if(kind==='revision')value.entries[0].revision=true;
 if(kind==='count')value.entries[0].version_count=99;
 if(kind==='window')value.window.from='2025-01-01';
 const s=await setup(async()=>value);expect((await s.client.readErasure()).state).toBe('unknown');
});
test('owned source-aware page retains raw unit, day precision and provenance',async()=>{
 const value=fixture(),s=await setup(async()=>value);
 expect(await s.client.read({from:'2026-11-01',through:'2026-11-11'})).toEqual({state:'confirmed',value});
});
test.each(['owner','unit','date','version','head','source_field','missing_field'])('invalid %s is never confirmed',async(kind)=>{
 const value=fixture();
 if(kind==='owner')value.owner_id=8;
 if(kind==='unit')value.entries[0].fields.weight_kg.unit='cm';
 if(kind==='date')value.entries[0].date_precision='INSTANT_VERIFIED';
 if(kind==='version')value.contract_version='body-measurements/2.0.0';
 if(kind==='head')value.entries[0].head_token='not-a-token';
 if(kind==='source_field')value.entries[0].fields.weight_kg.provenance.source_ref='body_measurements/11/waist_cm';
 if(kind==='missing_field')delete value.entries[0].fields.calf_cm;
 const s=await setup(async()=>value);
 expect((await s.client.read()).state).toBe('unknown');
});
test('late body data is cancelled on logout/account switch',async()=>{
 let resolve!:(value:unknown)=>void;
 const s=await setup(()=>new Promise(done=>{resolve=done;}));
 const reading=s.client.read();for(let i=0;i<12;i++)await Promise.resolve();
 await s.auth.logout();await s.auth.login('other','synthetic',null);s.setOwner(8);
 resolve(fixture());expect((await reading).state).toBe('cancelled');
});
test('a different authenticated owner never reaches the body transport',async()=>{
 let requested=false;const s=await setup(async()=>{requested=true;return fixture();});s.setOwner(8);
 expect((await s.client.read()).state).toBe('changed');expect(requested).toBe(false);
});
test('body HTTP uses its own exact negotiation and verifies echo',async()=>{
 let sent:RequestInit|undefined;
 const response=(echo:string|null)=>({ok:true,status:200,headers:{get:()=>echo},json:async()=>fixture()}) as unknown as Response;
 const transport=createBodyTransport(scope,async(_url,init)=>{sent=init;return response('body-measurements/1.0.0');});
 expect(await transport.call('/me/body/measurements',{token:'test-access'})).toEqual(fixture());
 expect(sent?.headers).toMatchObject({'X-Auren-Body-Contract':'body-measurements/1.0.0',Authorization:'Bearer test-access'});
 const incompatible=createBodyTransport(scope,async()=>response(null));
 await expect(incompatible.call('/me/body/measurements')).rejects.toThrow();
});
test('native command canonical bytes match the independent server digest input',()=>{
 const command={method:'POST' as const,path:'/me/body/measurements',request_id:'capture-1',
  payload_json:JSON.stringify({values:{weight_kg:72},request_id:'capture-1',measured_on:'2026-11-11'})};
 expect(bodyCommandCanonical(command)).toBe('{"measured_on":"2026-11-11","operation":"CREATE","request_id":"capture-1","values":{"weight_kg":72}}');
 expect(()=>bodyCommandCanonical({...command,payload_json:'{"request_id":"another-key","values":{"weight_kg":72}}'})).toThrow();
});
test('a status receipt with another body digest cannot acknowledge this command',async()=>{
 const command={owner_id:7,backend_scope:scope,method:'POST' as const,path:'/me/body/measurements/11/corrections',request_id:'correct-1',
  payload_json:JSON.stringify({request_id:'correct-1',expected_head_token:'a'.repeat(64),values:{weight_kg:73}}),body_digest:'a'.repeat(64)};
 const s=await setup(async()=>({contract_version:'body-operation/1.0.0',owner_id:7,command_digest:'b'.repeat(64),request_id:'correct-1',operation:'CORRECT',root_ref:11,measurement_id:12,applied_revision:2,recorded_at:'2026-11-11T12:00:00Z',state:'APPLIED'}));
 expect((await s.client.status(command)).state).toBe('unknown');
});
test('automatic credential refresh cannot retry an A command with a B token',async()=>{
 let stored:string|null=null;
 const call:Transport=async(path,init)=>{if(path==='/auth/me')return{id:init?.token==='other-access'?8:7} as any;if(path==='/auth/refresh')return{...pair,access_token:'other-access'} as any;return pair as any;};
 const auth=new AuthSession(call,{read:async()=>stored,write:async v=>{stored=v;},clear:async()=>{stored=null;}});
 await auth.login('synthetic-a','synthetic',null);
 const tokens:string[]=[];const bodyCall:Transport=async(_path,init)=>{tokens.push(init?.token??'');throw new ApiFailure('http',401,'expired');};
 const c=new BodyMeasurementsClient(auth,call,{scope,call:bodyCall},7);
 const command={owner_id:7,backend_scope:scope,method:'POST' as const,path:'/me/body/measurements',request_id:'capture-1',payload_json:JSON.stringify({request_id:'capture-1',measured_on:'2026-11-11',values:{weight_kg:72}}),body_digest:'a'.repeat(64)};
 expect((await c.submit(command)).state).toBe('changed');expect(tokens).toEqual(['test-access']);
});
