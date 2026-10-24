/**
 * Web PREVIEW only — the credential is kept in memory and dies with the tab.
 * A browser has no secure enclave this slice can rely on, so nothing is persisted.
 */
import type { CredentialStore } from './authSession';

let held: string | null = null;

export const credentialStore: CredentialStore = {
  read: () => Promise.resolve(held),
  write: (refreshToken) => {
    held = refreshToken;
    return Promise.resolve();
  },
  clear: () => {
    held = null;
    return Promise.resolve();
  },
};
