import {AuthSession} from '../auth/authSession';
import {ApiFailure,type Transport} from './http';
import {NutritionClient,createNutritionTransport,decodeNutritionReceipt} from './nutrition';
import {nutritionCommand} from '../domain/nutritionCommand';

const scope='https://qa.invalid',owner=7;
const pair={access_token:'access',refresh_token:'refresh',access_expires_in:3600,server_now:'2026-11-12T00:00:00Z'};
const input=()=>nutritionCommand('DAY','/me/nutrition/days/2026-11-12/revisions',{contract_version:'nutrition-command/1.0.0',request_id:'one',expected_head_token:'0'.repeat(64),operation:'SET_FIELDS',values:{kcal_milli:0},timezone:'Europe/Paris',target_ref:null,confirm_complete:null});
const prepared=()=>({...input(),owner_id:owner,backend_scope:scope,body_digest:'a'.repeat(64)});
export const receipt=(c=prepared())=>({contract_version:'nutrition-operation/1.0.0',owner_id:owner,namespace:'DAY',request_id:c.request_id,command_digest:c.body_digest,state:'APPLIED',entity_ref:1,applied_revision:1,recorded_at:'2026-11-12T00:00:00Z'});
async function fixture(fetchImpl:any,identity=()=>owner){
 let refresh=0;const authCall:Transport=async<T>(path:string)=>{
  if(path==='/auth/me')return {id:identity()} as T;
  if(path==='/auth/refresh')refresh++;
  return pair as T;
 };
 const auth=new AuthSession(authCall,{read:async()=>'refresh',write:async()=>{},clear:async()=>{}});
 await auth.login('synthetic','synthetic',null);
 return {auth,client:new NutritionClient(auth,{scope,call:authCall},createNutritionTransport(scope,fetchImpl),owner),refreshes:()=>refresh};
}
const response=(body:unknown,status=200,echo='nutrition-manual/1.0.0')=>({ok:status<400,status,headers:{get:()=>echo},json:async()=>body});
test('mutation emits saved exact body and negotiation; 401 never repeats it',async()=>{
 const fetchImpl=jest.fn(async()=>response({detail:{error:'auth'}},401));
 const f=await fixture(fetchImpl);expect(await f.client.submit(prepared())).toMatchObject({state:'unknown'});
 expect(fetchImpl).toHaveBeenCalledTimes(1);expect(f.refreshes()).toBe(0);
 const [url,init]=fetchImpl.mock.calls[0] as any;
 expect(url).toBe(scope+'/api/mobile/v1'+prepared().path);
 expect(init.body).toBe(prepared().payload_json);
 expect(init.headers['X-Auren-Nutrition-Contract']).toBe('nutrition-manual/1.0.0');
});
test('refresh to B and late A result cannot submit/confirm for A',async()=>{
 let account=8;const fetchImpl=jest.fn();const f=await fixture(fetchImpl,()=>account);
 expect(await f.client.submit(prepared())).toEqual({state:'changed'});expect(fetchImpl).not.toHaveBeenCalled();
 account=7;let resolve!:(x:unknown)=>void;
 fetchImpl.mockImplementation(()=>new Promise(r=>{resolve=r;}));
 const pending=f.client.submit(prepared());await new Promise(r=>setTimeout(r,0));
 await f.auth.logout();resolve(response(receipt()));
 expect(await pending).toEqual({state:'cancelled'});
});
test('foreign backend and malformed/foreign receipts cannot acknowledge',async()=>{
 const fetchImpl=jest.fn(async()=>response(receipt()));const f=await fixture(fetchImpl);
 expect(await f.client.submit({...prepared(),backend_scope:'https://other.invalid'})).toEqual({state:'changed'});
 expect(fetchImpl).not.toHaveBeenCalled();
 expect(decodeNutritionReceipt({...receipt(),owner_id:8},7,prepared())).toBeNull();
 expect(decodeNutritionReceipt({...receipt(),namespace:'TARGET'},7,prepared())).toBeNull();
 expect(decodeNutritionReceipt({...receipt(),extra:'unreviewed'},7,prepared())).toBeNull();
 expect(decodeNutritionReceipt(receipt(),7,prepared())).not.toBeNull();
});
test('contract mismatch and malformed body remain unknown, 404 status remains unknown',async()=>{
 const fetchImpl=jest.fn(async()=>response(receipt(),200,'wrong'));
 const f=await fixture(fetchImpl);expect(await f.client.submit(prepared())).toEqual({state:'unknown'});
 fetchImpl.mockImplementation(async()=>response({detail:{error:'foreign_or_missing'}},404));
 expect(await f.client.status(prepared())).toEqual({state:'unknown'});
 fetchImpl.mockRejectedValue(new ApiFailure('network'));expect(await f.client.status(prepared())).toEqual({state:'unknown'});
});
test('identity proof transport cannot be mounted against another backend',()=>{
 const call:Transport=async()=>{throw Error('no request expected');};
 const auth=new AuthSession(call,{read:async()=>null,write:async()=>{},clear:async()=>{}});
 expect(()=>new NutritionClient(auth,{scope:'https://other.invalid',call},createNutritionTransport(scope),7)).toThrow('nutrition_backend_mismatch');
});
test.each([[418,'future_error'],[422,null],[403,'unrecognized_policy'],[409,'unknown_conflict']])('unrecognized refusal %s/%s cannot establish nonapplication',async(status,code)=>{
 const f=await fixture(async()=>response({detail:{error:code}},status as number));
 expect(await f.client.submit(prepared())).toEqual({state:'unknown'});
});
test('reading an absent head needs only a natural key, with no invented intake or target',async()=>{
 const raw={contract_version:'nutrition-manual/1.0.0',owner_id:7,key:{local_day:'2026-11-12'},state:'ABSENT',head_token:'a'.repeat(64),entry:null};
 const fetchImpl=jest.fn(async()=>response(raw)),f=await fixture(fetchImpl);
 expect(await f.client.head({local_day:'2026-11-12'})).toEqual({state:'confirmed',value:raw});
 const [url,init]=fetchImpl.mock.calls[0] as any;
 expect(url).toBe(scope+'/api/mobile/v1/me/nutrition/days/2026-11-12');expect(init.method).toBe('GET');expect(init.body).toBeUndefined();
});
