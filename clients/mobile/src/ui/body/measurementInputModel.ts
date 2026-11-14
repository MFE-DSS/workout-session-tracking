import type {BodyEntry,BodyKey,BodySpec} from '../../api/bodyMeasurements';
export type BodyForm={values:Partial<Record<BodyKey,number|null>>;measured_on?:string};
export const measurementLabel=(label:string)=>label.replace(/\s*\((?:kg|cm)\)\s*$/,'');
export function measurementValues(specs:BodySpec[],draft:Partial<Record<BodyKey,string>>,cleared:Partial<Record<BodyKey,boolean>>,initial?:BodyEntry){
 const result:BodyForm['values']={};
 for(const spec of specs){
  if(cleared[spec.key]){result[spec.key]=null;continue;}
  const raw=draft[spec.key]?.trim();if(!raw)continue;
  // An unchanged inherited fact is not a new acquisition, including its legacy
  // numeric representation. No number/provenance is copied into the command.
  const prior=initial?.fields[spec.key].value;
  if(prior!=null&&Number.isFinite(prior)&&/^[+-]?\d+(?:[.,]\d+)?(?:[eE][+-]?\d+)?$/.test(raw)&&Number(raw.replace(',','.'))===prior)continue;
  if(!/^\d+(?:[.,]\d+)?$/.test(raw))throw Error('invalid_value');
  const value=Number(raw.replace(',','.'));if(!Number.isFinite(value)||value<spec.min||value>spec.max)throw Error('invalid_value');
  if(!initial||initial.fields[spec.key].value!==value)result[spec.key]=value;
 }
 return result;
}
