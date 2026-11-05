/** Approved weight GET only. No measurement writer, implicit consent or profile-weight fallback. */
import { AuthSession } from '../auth/authSession';
import { ApiFailure, type Transport } from './http';
export type WeightEntry={measurement_id:number;value:number|null;raw_value_repr:string|null;measured_at:string;recorded_at:string|null;quality:'KNOWN'|'LEGACY_OUTSIDE_CURRENT_BOUNDS'|'INVALID_NONFINITE';provenance:{origin:'UNKNOWN';acquisition:'UNKNOWN';source_ref:string}};
export type WeightHistory={contract_version:'weight-history/1.0.0';owner_id:number;unit:'kg';legacy_profile_included:false;timezone_basis:'DATABASE_UTC_CONVENTION';state:'AVAILABLE'|'EMPTY';entries:WeightEntry[];next_cursor:string|null};
export type WeightOutcome={state:'confirmed';value:WeightHistory}|{state:'consent_required'|'unavailable'|'rejected'|'unknown'|'cancelled'};
const id=(value:unknown):value is number=>Number.isSafeInteger(value)&&(value as number)>0;
const instant=(value:unknown):value is string=>typeof value==='string'&&/(?:Z|[+-]\d{2}:\d{2})$/.test(value)&&Number.isFinite(Date.parse(value));
function snapshot(raw:unknown,owner:number):WeightHistory|null{
 const value=raw as WeightHistory|null;
 if(!value||value.contract_version!=='weight-history/1.0.0'||value.owner_id!==owner||value.unit!=='kg'
   ||value.legacy_profile_included!==false||value.timezone_basis!=='DATABASE_UTC_CONVENTION'||!Array.isArray(value.entries))return null;
 if(value.state!=='AVAILABLE'&&value.state!=='EMPTY')return null;
 if((value.state==='EMPTY')!==(value.entries.length===0))return null;
 if(value.next_cursor!==null&&(typeof value.next_cursor!=='string'||!value.next_cursor.length||value.next_cursor.length>256))return null;
 if(value.state==='EMPTY'&&value.next_cursor!==null)return null;
 const ids=new Set<number>();
 for(const row of value.entries){
  if(!row||!id(row.measurement_id)||ids.has(row.measurement_id)||!instant(row.measured_at)||(row.recorded_at!==null&&!instant(row.recorded_at)))return null;
  ids.add(row.measurement_id);
  if(row.provenance?.origin!=='UNKNOWN'||row.provenance.acquisition!=='UNKNOWN'||row.provenance.source_ref!==`body_measurements/${row.measurement_id}/weight_kg`)return null;
  if(row.quality==='INVALID_NONFINITE'){
   if(row.value!==null||typeof row.raw_value_repr!=='string'||!row.raw_value_repr.length)return null;
  }else if(row.quality==='KNOWN'||row.quality==='LEGACY_OUTSIDE_CURRENT_BOUNDS'){
   if(typeof row.value!=='number'||!Number.isFinite(row.value)||row.raw_value_repr!==null)return null;
   if(row.quality==='KNOWN'&&row.value<=0)return null;
  }else return null;
 }
 return value;
}
export class WeightHistoryClient{
 constructor(private readonly auth:AuthSession,private readonly call:Transport){}
 async read(options:{limit?:number;cursor?:string}={}):Promise<WeightOutcome>{
  const revision=this.auth.revision,limit=options.limit??50;
  if(!Number.isSafeInteger(limit)||limit<1||limit>100)return{state:'rejected'};
  if(options.cursor!==undefined&&(typeof options.cursor!=='string'||options.cursor.length>256))return{state:'rejected'};
  try{
   const owner=await this.auth.authorized((token)=>this.call<{id:number}>('/auth/me',{token}));
   if(revision!==this.auth.revision)return{state:'cancelled'};
   if(!id(owner?.id))return{state:'unknown'};
   const path=`/me/body/weight-history?limit=${limit}${options.cursor!==undefined?`&cursor=${encodeURIComponent(options.cursor)}`:''}`;
   const raw=await this.auth.authorized((token)=>this.call<unknown>(path,{token}));
   if(revision!==this.auth.revision)return{state:'cancelled'};
   const value=snapshot(raw,owner.id);return value?{state:'confirmed',value}:{state:'unknown'};
  }catch(error){
   if(revision!==this.auth.revision)return{state:'cancelled'};
   if(error instanceof ApiFailure&&error.kind==='http'){
    if(error.status===403&&error.code==='body_consent_required')return{state:'consent_required'};
    if(error.status===404)return{state:'unavailable'};
    if(error.status>=400&&error.status<500&&error.status!==408)return{state:'rejected'};
   }
   return{state:'unknown'};
  }
 }
}
