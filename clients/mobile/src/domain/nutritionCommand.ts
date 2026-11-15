/** Exact manual facts/declared targets. No calorie recommendation or macro conversion. */
export const NUT_FIELDS=['kcal_milli','protein_milli','carbohydrate_milli','fat_milli'] as const;
export type NutritionField=typeof NUT_FIELDS[number];
export type NutritionNamespace='DAY'|'TARGET';
export type NutritionVariant='STANDARD'|'TRAINING'|'REST';
export type NutritionValues=Record<NutritionField,number|null>;
export type NutritionInput={namespace:NutritionNamespace;method:'POST';path:string;request_id:string;payload_json:string};
export type PreparedNutritionRequest=NutritionInput&{owner_id:number;backend_scope:string;body_digest:string};
export const nutRecord=(x:unknown):x is Record<string,unknown>=>typeof x==='object'&&x!==null&&!Array.isArray(x);
export const nutExact=(x:unknown,keys:readonly string[]):x is Record<string,unknown>=>nutRecord(x)&&Object.keys(x).length===keys.length&&keys.every(k=>Object.hasOwn(x,k));
export const nutId=(x:unknown):x is number=>Number.isSafeInteger(x)&&(x as number)>0;
export const nutHash=(x:unknown):x is string=>typeof x==='string'&&/^[0-9a-f]{64}$/.test(x);
export const nutDay=(x:unknown):x is string=>typeof x==='string'&&/^[0-9]{4}-[0-9]{2}-[0-9]{2}$/.test(x)&&x.slice(0,4)!=='0000'&&Number.isFinite(Date.parse(x+'T00:00:00Z'))&&new Date(x+'T00:00:00Z').toISOString().slice(0,10)===x;
export const nutVariant=(x:unknown):x is NutritionVariant=>['STANDARD','TRAINING','REST'].includes(x as string);
export const nutMilli=(x:unknown):x is number=>Number.isSafeInteger(x)&&(x as number)>=0&&(x as number)<=999999999;
export const nutRequestId=(x:unknown):x is string=>typeof x==='string'&&/^[A-Za-z0-9][A-Za-z0-9_.:-]{0,63}$/.test(x);
function fail():never{throw Error('invalid_nutrition_command');}
export function parseNutritionDecimal(input:string):number{
 if(!/^[0-9]{1,6}(?:[.,][0-9]{1,3})?$/.test(input))throw Error('invalid_nutrition_decimal');
 const [whole,fraction='']=input.replace(',','.').split('.');
 const result=Number(whole)*1000+Number(fraction.padEnd(3,'0'));
 if(!nutMilli(result))throw Error('invalid_nutrition_decimal');return result;
}
export function nutritionSorted(value:unknown):string{
 const sort=(x:unknown):unknown=>nutRecord(x)?Object.fromEntries(Object.keys(x).sort().map(k=>[k,sort(x[k])])):x;
 return JSON.stringify(sort(value));
}
export function nutritionKey(input:Pick<NutritionInput,'namespace'|'path'|'payload_json'>):string{
 if(input.namespace==='DAY')return input.path.slice('/me/nutrition/days/'.length,-'/revisions'.length);
 const body=JSON.parse(input.payload_json);return body.variant+'/'+body.effective_from;
}
function validate(namespace:NutritionNamespace,path:string,body:unknown):asserts body is Record<string,unknown>{
 const common=['contract_version','request_id','expected_head_token','operation','values'];
 if(!nutExact(body,[...common,...(namespace==='DAY'?['timezone','target_ref','confirm_complete']:['variant','effective_from'])])||body.contract_version!=='nutrition-command/1.0.0'||!nutRequestId(body.request_id)||!nutHash(body.expected_head_token)||!nutRecord(body.values))fail();
 const values=body.values as Record<string,unknown>;
 if(Object.entries(values).some(([k,v])=>!NUT_FIELDS.includes(k as NutritionField)||v!==null&&!nutMilli(v)))fail();
 if(namespace==='TARGET'){
  if(path!=='/me/nutrition/targets/revisions'||!nutVariant(body.variant)||!nutDay(body.effective_from)||!['SET_FIELDS','DISABLE'].includes(body.operation as string))fail();
  if(body.operation==='SET_FIELDS'?!Object.keys(values).length:Object.keys(values).length!==0)fail();
 }else{
  const match=/^\/me\/nutrition\/days\/([0-9]{4}-[0-9]{2}-[0-9]{2})\/revisions$/.exec(path);
  if(!match||!nutDay(match[1])||!['SET_FIELDS','SET_TARGET_REF','COMPLETE','WITHDRAW'].includes(body.operation as string)||body.target_ref!==null&&!nutId(body.target_ref))fail();
  if(body.operation==='SET_FIELDS'){
   if(!Object.keys(values).length||body.target_ref!==null||typeof body.timezone!=='string'||!body.timezone.length||body.timezone.length>128||!/^[\x20-\x7e]+$/.test(body.timezone)||body.confirm_complete!==null&&typeof body.confirm_complete!=='boolean')fail();
   try{new Intl.DateTimeFormat('en',{timeZone:body.timezone as string});}catch{fail();}
  }else{
   if(Object.keys(values).length||body.timezone!==null)fail();
   if(body.operation==='COMPLETE'?(typeof body.confirm_complete!=='boolean'||body.target_ref!==null):(body.confirm_complete!==null||body.operation==='WITHDRAW'&&body.target_ref!==null))fail();
  }
 }
}
export function nutritionCommand(namespace:NutritionNamespace,path:string,body:unknown):NutritionInput{
 if(namespace!=='DAY'&&namespace!=='TARGET')fail();validate(namespace,path,body);
 return {namespace,method:'POST',path,request_id:body.request_id as string,payload_json:nutritionSorted(body)};
}
export function nutritionCanonical(input:NutritionInput):string{
 if(input.method!=='POST'||!['DAY','TARGET'].includes(input.namespace))fail();
 const body:unknown=JSON.parse(input.payload_json);validate(input.namespace,input.path,body);
 // Strict canonical wire rejects duplicate keys and 1.0/1e0 before storage or replay.
 if(body.request_id!==input.request_id||nutritionSorted(body)!==input.payload_json)fail();
 return 'NUT-CMD-1\n'+nutritionSorted({body,method:input.method,namespace:input.namespace,path:input.path});
}
