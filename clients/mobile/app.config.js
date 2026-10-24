/**
 * Extends app.json with the operator's signing team, read from the environment
 * at build time by `scripts/device.mjs` (from the local signing certificate).
 * No personal identifier is ever written to the repository.
 */
module.exports = ({ config }) => ({
  ...config,
  ios: {
    ...config.ios,
    ...(process.env.APPLE_TEAM_ID ? { appleTeamId: process.env.APPLE_TEAM_ID } : {}),
  },
});
