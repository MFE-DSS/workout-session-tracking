import {createHash} from 'node:crypto';
import {nutritionCommand,parseNutritionDecimal,nutritionCanonical} from './nutritionCommand';

export const dayInput=(request_id='nut-contract-vector-1',values:Record<string,unknown>={kcal_milli:0})=>nutritionCommand('DAY','/me/nutrition/days/2026-11-12/revisions',{
 contract_version:'nutrition-command/1.0.0',request_id,expected_head_token:'0'.repeat(64),operation:'SET_FIELDS',values,timezone:'Europe/Paris',target_ref:null,confirm_complete:null,
});
test.each([
 [{kcal_milli:0},'81624acf1a2f7f57d63510c7d4a43e7b407963d473f88d72558ad55e4961cf5e'],
 [{protein_milli:999999999},'eef88ddb5e52fc13a37788ed2c366d309128949b3c297c565f1a9be568b72c9a'],
 [{fat_milli:1250,kcal_milli:null},'72544e11bedd46d138a75b59c69527768e6dd7283e99ab348fef0c2018164c6e'],
 [{fat_milli:1250},'e6e273f9c70a1bc8b998bc26f62ac0107126e3999a2f3e3b5d48cf321b480736'],
])('production TS command matches independent fixed Python/JS bytes', (values,hash)=>{
 expect(createHash('sha256').update(nutritionCanonical(dayInput(undefined,values))).digest('hex')).toBe(hash);
});
test.each(['1.2345','-1','1e3','Infinity','',' 1','1000000','1,2.3'])('decimal input refuses rounding/coercion: %s',s=>{
 expect(()=>parseNutritionDecimal(s)).toThrow();
});
test('comma, zero and exact three decimals have no float multiplication',()=>{
 expect(parseNutritionDecimal('0')).toBe(0);expect(parseNutritionDecimal('71,123')).toBe(71123);
 expect(parseNutritionDecimal('999999.999')).toBe(999999999);
});
test.each([true,-1,1.5,1000000000,NaN,Infinity])('invalid typed value rejected before persistence',bad=>{
 expect(()=>dayInput(undefined,{kcal_milli:bad})).toThrow();
});
test('noncanonical raw bytes, duplicates and exponent syntax cannot enter a durable command',()=>{
 const c=dayInput();
 for(const payload_json of [c.payload_json.replace('"kcal_milli":0','"kcal_milli":1e0'),c.payload_json.replace('"kcal_milli":0','"kcal_milli":0,"kcal_milli":0'),JSON.stringify(JSON.parse(c.payload_json),null,1)]){
  expect(()=>nutritionCanonical({...c,payload_json})).toThrow();
 }
});
