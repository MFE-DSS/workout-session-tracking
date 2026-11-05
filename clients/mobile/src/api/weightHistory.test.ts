import { AuthSession } from '../auth/authSession';
import { ApiFailure, type Transport } from './http';
import { WeightHistoryClient } from './weightHistory';
const pair={access_token:'test-access',refresh_token:'rt1.test.secret',access_expires_in:900,server_now:'2026-11-05T12:00:00Z'};
const snapshot={contract_version:'weight-history/1.0.0',owner_id:7,unit:'kg',legacy_profile_included:false,timezone_basis:'DATABASE_UTC_CONVENTION',state:'AVAILABLE',next_cursor:null,entries:[{measurement_id:11,value:72,raw_value_repr:null,measured_at:'2025-01-02T00:00:00+00:00',recorded_at:'2026-11-05T12:00:00Z',quality:'KNOWN',provenance:{origin:'UNKNOWN',acquisition:'UNKNOWN',source_ref:'body_measurements/11/weight_kg'}}]};
async function setup(resource:Transport){let credential:string|null=null;const seen:any[]=[];
 const call:Transport=async(path,init)=>{seen.push({path,...init});if(path==='/auth/me')return{id:7,username:'owner'} as any;if(path==='/auth/logout')return undefined as any;if(path==='/auth/login'||path==='/auth/refresh')return pair as any;return resource(path,init);};
 const auth=new AuthSession(call,{read:async()=>credential,write:async(v)=>{credential=v;},clear:async()=>{credential=null;}});await auth.login('owner','test-only',null);
 return{auth,seen,client:new WeightHistoryClient(auth,call)};
}
test('real AuthSession reads the approved GET with bearer and retains source/date/unit',async()=>{
 const s=await setup(async()=>snapshot as any), result=await s.client.read();
 expect(result).toEqual({state:'confirmed',value:snapshot});
 expect(s.seen.at(-1)).toMatchObject({path:'/me/body/weight-history?limit=50',token:'test-access'});
});
test.each([[403,'body_consent_required','consent_required'],[404,null,'unavailable'],[401,'auth','rejected'],[503,null,'unknown']])('HTTP %s stays explicit',async(status,code,state)=>{
 const s=await setup(async()=>{throw new ApiFailure('http',status as number,code as any);});
 expect((await s.client.read()).state).toBe(state);
});
test.each(['owner','unit','date','version','missing_value','provenance'])('invalid %s is never confirmed',async(kind)=>{
 const value=JSON.parse(JSON.stringify(snapshot));
 if(kind==='owner')value.owner_id=8;if(kind==='unit')value.unit='lb';if(kind==='date')value.entries[0].measured_at=null;
 if(kind==='version')value.contract_version='unknown';if(kind==='missing_value')value.entries[0].value=null;
 if(kind==='provenance')value.entries[0].provenance.origin='USER_OBSERVED';
 const s=await setup(async()=>value as any);expect((await s.client.read()).state).toBe('unknown');
});
test('late weight data is cancelled after an account switch',async()=>{
 let done!:(v:any)=>void;const s=await setup(()=>new Promise((r)=>{done=r;}));
 const reading=s.client.read();for(let i=0;i<12;i++)await Promise.resolve();
 await s.auth.logout();await s.auth.login('next','test-only',null);done(snapshot);
 expect((await reading).state).toBe('cancelled');
});
test('opaque cursor is encoded and never treated as a second path or an owner id',async()=>{
 const s=await setup(async()=>({...snapshot,state:'EMPTY',entries:[]}) as any);
 expect((await s.client.read({limit:1,cursor:'a/b?owner_id=8'})).state).toBe('confirmed');
 expect(s.seen.at(-1).path).toBe('/me/body/weight-history?limit=1&cursor=a%2Fb%3Fowner_id%3D8');
});
