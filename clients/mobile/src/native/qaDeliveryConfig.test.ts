/** Real helper/config boundary, all target fixtures remain synthetic test-only. */
const {applyQADelivery} = require('../../qa-delivery.config');
const configureDelivery = require('../../app.config.js');
const target = {
  schemaVersion:'qa-delivery-target/1.0.0',state:'ATTESTED',environmentId:'qa-rel03',
  apiUrl:'https://qa-rel03.onrender.com',dataScope:'SYNTHETIC_ONLY',availability:'STABLE',
  deploymentReference:'provider-receipt',continuityReference:'copy-receipt',backupReference:'backup-receipt',
  apiContract:'first-session-runtime/3.0.0',localSchema:'first-session-local/3.0.0',
};
const base = {name:'Lab',scheme:'auren-lab',version:'0.0.1',
  android:{package:'dev.auren.vnext.lab',versionCode:2},ios:{},
  extra:{eas:{projectId:'c7243bfc-29b3-4486-aafe-e69b9c904bbe'}}};
const env = {AUREN_QA_DELIVERY:'1',EXPO_PUBLIC_QA_DELIVERY:'1',
  EXPO_PUBLIC_PLAN_V3_CONTROLLED_TEST:'1',EXPO_PUBLIC_API_URL:target.apiUrl,
  EXPO_PUBLIC_QA_NATIVE_SHA:'a'.repeat(40),EXPO_PUBLIC_QA_JS_SHA:'a'.repeat(40)};
test('non delivery profile preserves config by identity without target resolution',()=>{
  expect(applyQADelivery(base,{},null)).toBe(base);
});
test('new QA has fingerprint policy/stable native extra and preserves upgrade identity',()=>{
  const c=applyQADelivery(base,env,target);
  expect(c.android).toEqual({package:'dev.auren.releaseqa02',versionCode:3});
  expect(c.version).toBe('0.0.2'); expect(c.scheme).toBe('auren-releaseqa02');
  expect(c.runtimeVersion).toEqual({policy:'fingerprint'});
  expect(c.extra.qaDelivery).toEqual({environmentId:'qa-rel03',apiUrl:target.apiUrl,
    apiContract:'first-session-runtime/3.0.0',localSchema:'first-session-local/3.0.0'});
});
test.each(['https://qa-fake.trycloudflare.com','https://qa-fake.ngrok-free.app',
  'https://spignos.com','https://qa.example.com','https://production.qa-rel03.onrender.com',
  'http://qa-rel03.onrender.com','https://qa-rel03.onrender.com/path',null])('invalid target %s cannot yield distributable config',apiUrl=>{
  expect(()=>applyQADelivery(base,{...env,EXPO_PUBLIC_API_URL:apiUrl},{...target,apiUrl})).toThrow();
});
test.each(['UNPROVISIONED','PENDING'])('unknown target %s fails closed',state=>{
  expect(()=>applyQADelivery(base,env,{...target,state})).toThrow();
});
test('checked-in unprovisioned target fails before build/export',()=>{
  expect(()=>applyQADelivery(base,env)).toThrow();
});
test.each([{AUREN_QA_BUILD:'1'},{EXPO_PUBLIC_GALLERY:'fixture'},{EAS_BUILD_PLATFORM:'ios'},
  {EXPO_PUBLIC_PLAN_V3_CONTROLLED_TEST:'0'},{EXPO_PUBLIC_API_URL:'https://qa-other.onrender.com'},
  {EXPO_PUBLIC_QA_DELIVERY:'0'}])('conflicting profile refuses %j',bad=>{
  expect(()=>applyQADelivery(base,{...env,...bad},target)).toThrow();
});
test('non-QA actual consumer keeps accepted config with Updates installed',()=>{
  expect(configureDelivery({config:base})).toEqual(base);
});
test('continuous QA refuses missing deterministic JS metadata even when target exists',()=>{
  expect(()=>applyQADelivery(base,{...env,EXPO_PUBLIC_QA_NATIVE_SHA:undefined},target)).toThrow();
});
