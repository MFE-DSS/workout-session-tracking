/**
 * Extends app.json with the operator's signing team, read from the environment
 * at build time by `scripts/device.mjs` (from the local signing certificate).
 * No personal identifier is ever written to the repository.
 */
const {applyQA} = require('./qa.config');
module.exports = ({ config }) => applyQA({
  ...config,
  ...(process.env.EXPO_PUBLIC_PLAN_V3_CONTROLLED_TEST === '1' ? {name:'AUREN PLAN Test',scheme:'auren-plan-v3-test',android:{...config.android,package:'dev.auren.plan.v3.controlled'}} : {}),
  ios: {
    ...config.ios,
    ...(process.env.EXPO_PUBLIC_PLAN_V3_CONTROLLED_TEST === '1' ? {bundleIdentifier: 'dev.auren.plan.v3.controlled'} : {}),
    ...(process.env.APPLE_TEAM_ID ? { appleTeamId: process.env.APPLE_TEAM_ID } : {}),
  },
});
