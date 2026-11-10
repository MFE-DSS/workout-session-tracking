/** Real app-config consumer, with a source-labelled synthetic target receipt. */
jest.mock('../../release-qa-target.json', () => ({
  schemaVersion: 'release-qa-target/1.0.0', state: 'ATTESTED',
  apiUrl: 'https://test-receipt-only.trycloudflare.com', dataScope: 'SYNTHETIC_ONLY',
  backendRevision: 'b8f5ffc2d6671521cbc276ab87397540aed60bb7',
  packagingDigest: '22b066a0fb363b1bd435323269bad8a7fa47e4149f18b91e4b039e89d8352dfc',
  authorityGeneration: 1,
}), {virtual: true});

const configure = require('../../app.config.js');
const targetReceipt = require('../../release-qa-target.json');
const qaKeys = ['AUREN_QA_BUILD', 'AUREN_QA_SOURCE_SHA', 'EAS_BUILD_GIT_COMMIT_HASH',
  'EXPO_PUBLIC_API_URL', 'EXPO_PUBLIC_PLAN_V3_CONTROLLED_TEST', 'EXPO_PUBLIC_GALLERY', 'APPLE_TEAM_ID', 'EAS_BUILD_PLATFORM'];
const saved = Object.fromEntries(qaKeys.map(k => [k, process.env[k]]));
const base = {name: 'AUREN Lab', scheme: 'auren-lab',
  android: {package: 'dev.auren.vnext.lab', versionCode: 2},
  ios: {bundleIdentifier: 'dev.auren.vnext.lab'}, extra: {eas: {projectId: 'existing-project'}}};
function valid() {
  process.env.AUREN_QA_BUILD = '1';
  process.env.AUREN_QA_SOURCE_SHA = 'b8f5ffc2d6671521cbc276ab87397540aed60bb7';
  process.env.EXPO_PUBLIC_API_URL = 'https://test-receipt-only.trycloudflare.com';
  process.env.EXPO_PUBLIC_PLAN_V3_CONTROLLED_TEST = '1';
}
beforeEach(() => {
  for (const k of qaKeys) delete process.env[k];
  targetReceipt.state = 'ATTESTED'; targetReceipt.authorityGeneration = 1;
});
afterAll(() => { for (const k of qaKeys) {
  if (saved[k] === undefined) delete process.env[k]; else process.env[k] = saved[k];
}});

test('ordinary build preserves accepted configuration', () => {
  expect(configure({config: base})).toEqual(base);
});
test('existing controlled build preserves its identity outside QA', () => {
  process.env.EXPO_PUBLIC_PLAN_V3_CONTROLLED_TEST = '1';
  const c = configure({config: base});
  expect(c.android.package).toBe('dev.auren.plan.v3.controlled');
  expect(c.ios.bundleIdentifier).toBe('dev.auren.plan.v3.controlled');
});
test('QA wins over controlled identity and embeds attested target and source', () => {
  valid(); const c = configure({config: base});
  expect(c.android.package).toBe('dev.auren.releaseqa02');
  expect(c.scheme).toBe('auren-releaseqa02');
  expect(c.extra.eas.projectId).toBe('existing-project');
  expect(c.extra.releaseQA.sourceRevision).toBe(process.env.AUREN_QA_SOURCE_SHA);
  expect(c.extra.releaseQA.backendRevision).toBe('b8f5ffc2d6671521cbc276ab87397540aed60bb7');
  expect(c.extra.releaseQA.dataScope).toBe('SYNTHETIC_ONLY');
  expect(c.android.usesCleartextTraffic).not.toBe(true);
});
test.each(['https://spignos.com', 'http://127.0.0.1:8140', 'http://192.168.1.1',
  'https://another-bench.trycloudflare.com', ''])('QA refuses unbound API %s', api => {
  valid(); process.env.EXPO_PUBLIC_API_URL = api;
  expect(() => configure({config: base})).toThrow();
});
test.each(['', 'bad-sha', '0'.repeat(64)])('QA refuses missing or malformed source %s', sha => {
  valid(); process.env.AUREN_QA_SOURCE_SHA = sha;
  expect(() => configure({config: base})).toThrow();
});
test('QA rejects an EAS SHA inconsistent with the local upload SHA', () => {
  valid(); process.env.EAS_BUILD_GIT_COMMIT_HASH = 'f'.repeat(40);
  expect(() => configure({config: base})).toThrow();
});
test('QA uses the actual EAS build revision remotely', () => {
  valid(); delete process.env.AUREN_QA_SOURCE_SHA;
  process.env.EAS_BUILD_GIT_COMMIT_HASH = 'f'.repeat(40);
  expect(configure({config: base}).extra.releaseQA.sourceRevision).toBe('f'.repeat(40));
});
test('QA never selects a gallery', () => {
  valid(); process.env.EXPO_PUBLIC_GALLERY = 'contract';
  expect(() => configure({config: base})).toThrow();
});
test('QA requires controlled native consumer', () => {
  valid(); delete process.env.EXPO_PUBLIC_PLAN_V3_CONTROLLED_TEST;
  expect(() => configure({config: base})).toThrow();
});
test('QA refuses unestablished target and imprecise authority generation', () => {
  valid(); targetReceipt.state = 'UNRESOLVED';
  expect(() => configure({config: base})).toThrow();
  targetReceipt.state = 'ATTESTED'; targetReceipt.authorityGeneration = Number.MAX_SAFE_INTEGER + 1;
  expect(() => configure({config: base})).toThrow();
});
test('Android QA cannot become an iOS build by profile reuse', () => {
  valid(); process.env.EAS_BUILD_PLATFORM = 'ios';
  expect(() => configure({config: base})).toThrow();
});
