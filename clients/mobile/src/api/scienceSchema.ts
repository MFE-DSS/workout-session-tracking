/** Structural decoder for the closed keyword set of the pinned SCI v1 exports.
 * It does NOT implement scientific semantics or replace server validate_exchange.
 * An unsupported future keyword fails closed instead of silently changing meaning.
 */
const annotations = new Set(['$schema','$id','$defs','title','description','default']);
const keywords = new Set(['$ref','type','anyOf','const','enum','properties','required','additionalProperties','items','minItems','maxItems','minLength','maxLength','minimum','maximum','exclusiveMinimum','exclusiveMaximum','pattern','format']);
const owns = (v: object,k: string) => Object.prototype.hasOwnProperty.call(v,k);
const object = (v: unknown): v is Record<string,unknown> => v !== null && typeof v === 'object' && !Array.isArray(v);
function dateTime(value: string): boolean {
  const match = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/.exec(value);
  if (!match || !Number.isFinite(Date.parse(value))) return false;
  const [,year,month,day,hour,minute,second] = match.map(Number);
  return month>=1 && month<=12 && day>=1 && day<=new Date(Date.UTC(year,month,0)).getUTCDate()
    && hour<24 && minute<60 && second<60;
}
export function scienceSchemaMatches(value: unknown, schema: any, root: any = schema, depth = 0): boolean {
  if (depth>64 || schema===null || typeof schema!=='object' || Array.isArray(schema)) return false;
  if (Object.keys(schema).some((key)=>!annotations.has(key)&&!keywords.has(key))) return false;
  if (schema.$ref) {
    if (typeof schema.$ref!=='string'||!schema.$ref.startsWith('#/$defs/')) return false;
    const key=schema.$ref.slice(8).replace(/~1/g,'/').replace(/~0/g,'~');
    return Boolean(root.$defs?.[key])&&scienceSchemaMatches(value,root.$defs[key],root,depth+1);
  }
  if (schema.anyOf) return Array.isArray(schema.anyOf)&&schema.anyOf.some((s:any)=>scienceSchemaMatches(value,s,root,depth+1));
  if (owns(schema,'const')&&value!==schema.const) return false;
  if (schema.enum&&!schema.enum.includes(value)) return false;
  switch(schema.type) {
    case 'null': return value===null;
    case 'boolean': if(typeof value!=='boolean')return false; break;
    case 'string':
      if(typeof value!=='string')return false;
      if(schema.minLength!==undefined&&[...value].length<schema.minLength)return false;
      if(schema.maxLength!==undefined&&[...value].length>schema.maxLength)return false;
      if(schema.pattern&&!new RegExp(schema.pattern).test(value))return false;
      if(schema.format&&(schema.format!=='date-time'||!dateTime(value)))return false;
      break;
    case 'integer': case 'number':
      if(typeof value!=='number'||!Number.isFinite(value))return false;
      if(schema.type==='integer'&&!Number.isSafeInteger(value))return false;
      if(schema.minimum!==undefined&&value<schema.minimum)return false;
      if(schema.maximum!==undefined&&value>schema.maximum)return false;
      if(schema.exclusiveMinimum!==undefined&&value<=schema.exclusiveMinimum)return false;
      if(schema.exclusiveMaximum!==undefined&&value>=schema.exclusiveMaximum)return false;
      break;
    case 'array':
      if(!Array.isArray(value))return false;
      if(schema.minItems!==undefined&&value.length<schema.minItems)return false;
      if(schema.maxItems!==undefined&&value.length>schema.maxItems)return false;
      if(schema.items&&!value.every((item)=>scienceSchemaMatches(item,schema.items,root,depth+1)))return false;
      break;
    case 'object':
      if(!object(value))return false;
      if(schema.required?.some((key:string)=>!owns(value,key)))return false;
      for(const key of Object.keys(value)) {
        if(schema.properties&&owns(schema.properties,key)) { if(!scienceSchemaMatches(value[key],schema.properties[key],root,depth+1))return false; }
        else if(schema.additionalProperties===false)return false;
      }
      break;
    case undefined: break;
    default: return false;
  }
  return true;
}
