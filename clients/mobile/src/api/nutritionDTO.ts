/** Closed factual DTOs. Unknown/withdrawn never become zero or a complete log. */
import {NUT_FIELDS,nutDay,nutExact,nutHash,nutId,nutMilli,nutRecord,nutVariant,type NutritionNamespace,type NutritionValues} from '../domain/nutritionCommand';
const CONTRACT='nutrition-manual/1.0.0';
const instant=(x:unknown):x is string=>typeof x==='string'&&x.length<=64&&/(?:Z|[+-][0-9]{2}:[0-9]{2})$/.test(x)&&Number.isFinite(Date.parse(x));
const nat=(x:unknown):x is number=>Number.isSafeInteger(x)&&(x as number)>=0;
export type NutritionConsent={contract_version:typeof CONTRACT;owner_id:number;purpose:'nutrition_manual';state:'ABSENT'|'PRESENT';granted:boolean;wording_version:number;current_wording_version:1;granted_at:string|null;withdrawn_at:string|null;consent_token:string};
export type NutritionEntry={id:number;revision:number;values:NutritionValues;units:Record<string,{unit:'kcal'|'g';scale:1000}>;provenance:Record<string,unknown>;recorded_at:string;head_token:string|null;local_day?:string;timezone?:string;state?:'ACTIVE'|'WITHDRAWN';declared_complete?:boolean;target_ref?:number|null;variant?:'STANDARD'|'TRAINING'|'REST';effective_from?:string;enabled?:boolean};
export type NutritionHead={contract_version:typeof CONTRACT;owner_id:number;key:Record<string,string>;state:'ABSENT'|'PRESENT';head_token:string;entry:NutritionEntry|null};
export type NutritionRead={kind:'days'|'targets'|'versions'|'export';from?:string;through?:string;namespace?:NutritionNamespace;reference?:string|number;limit?:number;cursor?:string};
export type NutritionPage={contract_version:typeof CONTRACT;owner_id:number;read_id:string;window:Record<string,unknown>|null;entries:(NutritionEntry|{namespace:NutritionNamespace;entry:NutritionEntry})[];next_cursor:string|null;collection_state:'PARTIAL'|'COMPLETE';coverage?:Record<string,Record<string,number>>;totals?:Record<string,{value:number|null;known_days:number;reason?:'UNKNOWN_ARITHMETIC_RANGE'}>};
export function decodeNutritionConsent(raw:unknown,owner:number):NutritionConsent|null{
 if(!nutExact(raw,['contract_version','owner_id','purpose','state','granted','wording_version','current_wording_version','granted_at','withdrawn_at','consent_token'])||raw.contract_version!==CONTRACT||raw.owner_id!==owner||raw.purpose!=='nutrition_manual'||!['ABSENT','PRESENT'].includes(raw.state as string)||typeof raw.granted!=='boolean'||!nutId(raw.wording_version)||raw.current_wording_version!==1||!nutHash(raw.consent_token)||raw.granted_at!==null&&!instant(raw.granted_at)||raw.withdrawn_at!==null&&!instant(raw.withdrawn_at))return null;
 if(raw.state==='ABSENT'&&(raw.granted||raw.granted_at!==null||raw.withdrawn_at!==null)||raw.granted&&raw.granted_at===null)return null;
 return raw as NutritionConsent;
}
function provenance(raw:unknown,namespace:NutritionNamespace,id:number):boolean{
 if(!nutRecord(raw)||Object.keys(raw).some(k=>!['fields','date'].includes(k))||!nutRecord(raw.fields)||Object.keys(raw.fields).some(k=>!NUT_FIELDS.includes(k as any)))return false;
 const table=namespace==='DAY'?'nutrition_day_revisions_v1':'nutrition_target_revisions_v1';
 for(const [field,p] of Object.entries(raw.fields)){
  if(!nutExact(p,['origin','method','source_ref'])||p.origin!==(namespace==='DAY'?'USER_DECLARED':'USER_DEFINED_TARGET')||!['MANUAL_ENTRY','MANUAL_CORRECTION'].includes(p.method as string)||typeof p.source_ref!=='string')return false;
  const prefix=table+'/',suffix='/'+field,ref=Number(p.source_ref.slice(prefix.length,-suffix.length));
  if(!p.source_ref.startsWith(prefix)||!p.source_ref.endsWith(suffix)||!nutId(ref)||ref>id||p.source_ref!==`${table}/${ref}/${field}`)return false;
 }
 if(raw.date!==undefined){const p=raw.date;if(!nutExact(p,['origin','precision','source_ref'])||p.origin!=='USER_DECLARED'||p.precision!=='LOCAL_DAY'||typeof p.source_ref!=='string'||!p.source_ref.startsWith(table+'/'))return false;
  const ref=Number(p.source_ref.slice(table.length+1));if(!nutId(ref)||ref>id||p.source_ref!==`${table}/${ref}`)return false;}
 return true;
}
export function decodeNutritionEntry(raw:unknown,namespace:NutritionNamespace,historical=false):NutritionEntry|null{
 const common=['id','revision','values','units','provenance','recorded_at','head_token'];
 const extra=namespace==='DAY'?['local_day','timezone','state','declared_complete','target_ref']:['variant','effective_from','enabled'];
 if(!nutExact(raw,[...common,...extra])||!nutId(raw.id)||!nutId(raw.revision)||!instant(raw.recorded_at)||!nutExact(raw.values,NUT_FIELDS)||!nutExact(raw.units,NUT_FIELDS)||!provenance(raw.provenance,namespace,raw.id))return null;
 if(historical?raw.head_token!==null:!nutHash(raw.head_token))return null;
 for(const field of NUT_FIELDS){const unit=raw.units[field];if(raw.values[field]!==null&&!nutMilli(raw.values[field])||!nutExact(unit,['unit','scale'])||unit.unit!==(field==='kcal_milli'?'kcal':'g')||unit.scale!==1000)return null;}
 if(!nutRecord(raw.provenance)||!nutRecord(raw.provenance.fields)||raw.provenance.date===undefined||NUT_FIELDS.some(f=>(raw.values as Record<string,unknown>)[f]!==null&&!Object.hasOwn((raw.provenance as any).fields,f)))return null;
 const known=NUT_FIELDS.some(f=>(raw.values as Record<string,unknown>)[f]!==null);
 if(namespace==='DAY'){
  if(!nutDay(raw.local_day)||typeof raw.timezone!=='string'||raw.timezone.length>128||!raw.timezone.length||typeof raw.declared_complete!=='boolean'||raw.target_ref!==null&&!nutId(raw.target_ref)||!['ACTIVE','WITHDRAWN'].includes(raw.state as string))return null;
  if(raw.state==='ACTIVE'?!known:known||raw.target_ref!==null||raw.declared_complete)return null;
 }else if(!nutVariant(raw.variant)||!nutDay(raw.effective_from)||typeof raw.enabled!=='boolean'||raw.enabled!==known)return null;
 return raw as NutritionEntry;
}
export function decodeNutritionHead(raw:unknown,owner:number,namespace:NutritionNamespace,key:Record<string,string>):NutritionHead|null{
 if(!nutExact(raw,['contract_version','owner_id','key','state','head_token','entry'])||raw.contract_version!==CONTRACT||raw.owner_id!==owner||!nutHash(raw.head_token)||!nutExact(raw.key,Object.keys(key))||Object.entries(key).some(([k,v])=>(raw.key as any)[k]!==v))return null;
 if(raw.state==='ABSENT')return raw.entry===null?raw as NutritionHead:null;
 if(raw.state!=='PRESENT')return null;
 const entry=decodeNutritionEntry(raw.entry,namespace);
 if(!entry||entry.head_token!==raw.head_token||Object.entries(key).some(([k,v])=>(entry as any)[k]!==v))return null;
 return raw as NutritionHead;
}
export function nutritionReadQuery(options:NutritionRead):string{
 const limit=options.limit??100;if(!nutId(limit)||limit>100||options.cursor!==undefined&&(!options.cursor.length||options.cursor.length>4096))throw Error('invalid_nutrition_query');
 let path:string;
 if(options.kind==='days'){
  if(!nutDay(options.from)||!nutDay(options.through))throw Error('invalid_nutrition_window');
  const days=(Date.parse(options.through)-Date.parse(options.from))/86400000;if(days<0||days>365)throw Error('invalid_nutrition_window');
  path=`days?from=${options.from}&through=${options.through}&`;
 }else if(options.kind==='versions'){
  if(options.namespace==='DAY'?!nutDay(options.reference):options.namespace!=='TARGET'||!nutId(options.reference))throw Error('invalid_nutrition_reference');
  path=`${options.namespace==='DAY'?'days':'targets'}/${options.reference}/revisions?`;
 }else if(['targets','export'].includes(options.kind))path=options.kind+'?';
 else throw Error('invalid_nutrition_query');
 return path+`limit=${limit}`+(options.cursor===undefined?'':`&cursor=${encodeURIComponent(options.cursor)}`);
}
export function decodeNutritionPage(raw:unknown,owner:number,options:NutritionRead):NutritionPage|null{
 const keys=['contract_version','owner_id','read_id','window','entries','next_cursor','collection_state',...(options.kind==='days'?['coverage','totals']:[])];
 if(!nutExact(raw,keys)||raw.contract_version!==CONTRACT||raw.owner_id!==owner||!nutHash(raw.read_id)||!Array.isArray(raw.entries)||raw.entries.length>(options.limit??100)||raw.next_cursor!==null&&(typeof raw.next_cursor!=='string'||!raw.next_cursor.length||raw.next_cursor.length>4096)||raw.collection_state!==(raw.next_cursor===null?'COMPLETE':'PARTIAL')||raw.entries.length===0&&raw.next_cursor!==null)return null;
 if(options.kind==='days'){
  if(!nutExact(raw.window,['from','through'])||raw.window.from!==options.from||raw.window.through!==options.through||!nutExact(raw.coverage,NUT_FIELDS)||!nutExact(raw.totals,NUT_FIELDS))return null;
  const calendar=(Date.parse(options.through!)-Date.parse(options.from!))/86400000+1;
  for(const f of NUT_FIELDS){const c=raw.coverage[f],t=raw.totals[f];
   if(!nutExact(c,['known_days','missing_days','partial_days','declared_complete_days','withdrawn_days','total_calendar_days'])||Object.values(c).some(v=>!nat(v)||(v as number)>calendar)||c.total_calendar_days!==calendar||(c.known_days as number)+(c.missing_days as number)!==calendar||!nutExact(t,nutRecord(t)&&t.reason!==undefined?['value','known_days','reason']:['value','known_days'])||t.known_days!==c.known_days||t.value!==null&&!nat(t.value)||t.reason!==undefined&&t.reason!=='UNKNOWN_ARITHMETIC_RANGE'||t.reason!==undefined&&t.value!==null||t.known_days===0&&t.value!==null||t.known_days!==0&&t.value===null&&t.reason===undefined)return null;
  }
 }else if(options.kind==='versions'){
  if(!nutExact(raw.window,['namespace','key'])||raw.window.namespace!==options.namespace)return null;
  if(options.namespace==='DAY'?raw.window.key!==options.reference:!Array.isArray(raw.window.key)||raw.window.key.length!==2||!nutVariant(raw.window.key[0])||!nutDay(raw.window.key[1]))return null;
 }else if(raw.window!==null)return null;
 const ids=new Set<string>(),logicalKeys=new Set<string>();
 for(const item of raw.entries){
  let namespace:NutritionNamespace=options.kind==='days'?'DAY':options.kind==='targets'?'TARGET':options.namespace!,value:unknown=item;
  if(options.kind==='export'){
   if(!nutExact(item,['namespace','entry'])||!['DAY','TARGET'].includes(item.namespace as string))return null;namespace=item.namespace as NutritionNamespace;value=item.entry;
  }
  const e=decodeNutritionEntry(value,namespace,options.kind==='versions'||options.kind==='export');
  if(!e||ids.has(namespace+'/'+e.id))return null;ids.add(namespace+'/'+e.id);
  const key=namespace==='DAY'?e.local_day!:e.variant+'/'+e.effective_from;
  if(['days','targets'].includes(options.kind)&&logicalKeys.has(key))return null;logicalKeys.add(key);
  if(options.kind==='days'&&(e.local_day!<options.from!||e.local_day!>options.through!))return null;
  if(options.kind==='versions'&&(namespace==='DAY'?e.local_day!==options.reference:e.variant!==(raw.window as any).key[0]||e.effective_from!==(raw.window as any).key[1]))return null;
 }
 if(options.kind==='days'&&raw.collection_state==='COMPLETE'&&options.cursor===undefined&&!nutritionCoverageMatches(raw as NutritionPage))return null;
 return raw as NutritionPage;
}

/** Called on the fully assembled snapshot, never on one page of a traversal. */
export function nutritionCoverageMatches(page:NutritionPage):boolean{
 if(!page.coverage||!page.totals||!page.window)return false;
 const count=(Date.parse(page.window.through as string)-Date.parse(page.window.from as string))/86400000+1;
 const entries=page.entries as NutritionEntry[];
 const active=entries.filter(e=>e.state==='ACTIVE');
 for(const field of NUT_FIELDS){
  const numbers=active.map(e=>e.values[field]).filter((v):v is number=>v!==null);
  const expected={known_days:numbers.length,missing_days:count-numbers.length,partial_days:active.filter(e=>!e.declared_complete).length,declared_complete_days:active.filter(e=>e.declared_complete).length,withdrawn_days:entries.filter(e=>e.state==='WITHDRAWN').length,total_calendar_days:count};
  if(Object.entries(expected).some(([k,v])=>page.coverage![field][k]!==v))return false;
  const total=numbers.length?numbers.reduce((sum,n)=>sum+n,0):null;
  if(page.totals[field].value!==total||page.totals[field].known_days!==numbers.length||page.totals[field].reason!==undefined)return false;
 }
 return true;
}
