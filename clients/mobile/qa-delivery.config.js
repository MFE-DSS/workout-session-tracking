/** Continuous QA only; deployment attestation is independently verified by release gates.
 * URL below was produced by eas update:configure --platform android (CLI 27.2.0).
 * No source SHA, timestamp or observed science generation belongs in native config.
 */
const PROJECT = 'c7243bfc-29b3-4486-aafe-e69b9c904bbe';
const UPDATE_URL = 'https://u.expo.dev/c7243bfc-29b3-4486-aafe-e69b9c904bbe';
function stableQAOrigin(value) {
  try {
    const u = new URL(value), h = u.hostname, labels = h.split('.');
    return u.protocol === 'https:' && !u.username && !u.password && !u.port &&
      u.pathname === '/' && !u.search && !u.hash && labels.length >= 3 &&
      labels.every(s => /^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$/.test(s)) &&
      labels.slice(0,-2).some(s => /^qa(?:-[a-z0-9-]+)?$/.test(s)) &&
      !labels.some(s => ['prod','production','example','invalid','localhost'].includes(s)) &&
      !['spignos.com','trycloudflare.com','ngrok.io','ngrok-free.app','loca.lt',
        'localtest.me','example.com','example.org','example.net'].some(s => h === s || h.endsWith(`.${s}`));
  } catch { return false; }
}
function applyQADelivery(config, env=process.env, target) {
  if (!env.AUREN_QA_DELIVERY || env.AUREN_QA_DELIVERY === '0') return config;
  if (env.AUREN_QA_DELIVERY !== '1' || env.AUREN_QA_BUILD === '1' || env.EXPO_PUBLIC_GALLERY ||
      env.EXPO_PUBLIC_QA_DELIVERY !== '1' || env.EXPO_PUBLIC_PLAN_V3_CONTROLLED_TEST !== '1' ||
      !/^[a-f0-9]{40}$/.test(env.EXPO_PUBLIC_QA_NATIVE_SHA || '') ||
      !/^[a-f0-9]{40}$/.test(env.EXPO_PUBLIC_QA_JS_SHA || '') ||
      (env.EAS_BUILD_PLATFORM && env.EAS_BUILD_PLATFORM !== 'android')) {
    throw Error('Invalid continuous QA profile');
  }
  target ??= require('./qa-delivery-target.json');
  if (target.schemaVersion !== 'qa-delivery-target/1.0.0' || target.state !== 'ATTESTED' ||
      target.availability !== 'STABLE' || target.dataScope !== 'SYNTHETIC_ONLY' ||
      !/^qa-[a-z0-9_-]{3,60}$/.test(target.environmentId) || !stableQAOrigin(target.apiUrl) ||
      env.EXPO_PUBLIC_API_URL !== target.apiUrl || config.extra?.eas?.projectId !== PROJECT ||
      target.apiContract !== 'first-session-runtime/3.0.0' || target.localSchema !== 'first-session-local/3.0.0' ||
      !['deploymentReference','continuityReference','backupReference'].every(k =>
        typeof target[k] === 'string' && target[k].trim().length > 0)) {
    throw Error('Continuous QA target unavailable or not attested');
  }
  return {...config, name:'AUREN QA', scheme:'auren-releaseqa02', version:'0.0.2',
    android:{...config.android,package:'dev.auren.releaseqa02',versionCode:3},
    runtimeVersion:{policy:'fingerprint'}, updates:{url:UPDATE_URL,enabled:true},
    extra:{...config.extra,qaDelivery:{environmentId:target.environmentId,apiUrl:target.apiUrl,
      apiContract:target.apiContract,localSchema:target.localSchema}},
  };
}
module.exports = {applyQADelivery,stableQAOrigin};
