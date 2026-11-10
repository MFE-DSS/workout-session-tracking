/** QA-only native configuration; source revision is checked against EAS at upload. */
function applyQA(config, env = process.env) {
  if (!env.AUREN_QA_BUILD || env.AUREN_QA_BUILD === '0') return config;
  if (env.AUREN_QA_BUILD !== '1') throw new Error('Invalid QA build selector');
  const target = require('./release-qa-target.json');
  const local = env.AUREN_QA_SOURCE_SHA;
  const remote = env.EAS_BUILD_GIT_COMMIT_HASH;
  const revision = remote || local;
  if (!revision || !/^[a-f0-9]{40}$/.test(revision) || (local && remote && local !== remote)) {
    throw new Error('QA source revision missing or inconsistent');
  }
  if (env.EAS_BUILD_PLATFORM && env.EAS_BUILD_PLATFORM !== 'android') {
    throw new Error('This QA profile is Android only');
  }
  if (env.EXPO_PUBLIC_GALLERY || env.EXPO_PUBLIC_PLAN_V3_CONTROLLED_TEST !== '1') {
    throw new Error('QA requires the real controlled native consumer');
  }
  const url = new URL(target.apiUrl);
  if (target.schemaVersion !== 'release-qa-target/1.0.0' || target.state !== 'ATTESTED' ||
      target.dataScope !== 'SYNTHETIC_ONLY' ||
      !/^[a-f0-9]{40}$/.test(target.backendRevision) ||
      !/^[a-f0-9]{64}$/.test(target.packagingDigest) ||
      !Number.isSafeInteger(target.authorityGeneration) || target.authorityGeneration < 1 ||
      url.protocol !== 'https:' || !/^[a-z0-9-]+\.trycloudflare\.com$/.test(url.hostname) ||
      url.port || url.username || url.password || url.pathname !== '/' || url.search || url.hash ||
      env.EXPO_PUBLIC_API_URL !== target.apiUrl) {
    throw new Error('QA target is not the exact attested HTTPS synthetic bench');
  }
  return {
    ...config, name: 'AUREN QA', scheme: 'auren-releaseqa02',
    android: {...config.android, package: 'dev.auren.releaseqa02'},
    extra: {...config.extra, releaseQA: {...target, sourceRevision: revision}},
  };
}
module.exports = {applyQA};
