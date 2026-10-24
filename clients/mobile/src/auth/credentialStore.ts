/**
 * D9 — the refresh credential lives in the iOS Keychain (Android Keystore),
 * through Expo's secure-storage adapter, and NOWHERE else: not AsyncStorage,
 * not the SQLite journal, not a file, not a log.
 *
 * `AFTER_FIRST_UNLOCK_THIS_DEVICE_ONLY`: readable while the phone is locked in
 * a pocket between sets (the sync runs then), never restored onto another
 * device from a backup — a device session belongs to ONE device.
 *
 * The access token is never stored: it lives in memory (`AuthSession`).
 */
import * as SecureStore from 'expo-secure-store';

import type { CredentialStore } from './authSession';

const KEY = 'auren.refresh.v1';
const OPTIONS: SecureStore.SecureStoreOptions = {
  keychainAccessible: SecureStore.AFTER_FIRST_UNLOCK_THIS_DEVICE_ONLY,
};

export const credentialStore: CredentialStore = {
  read: () => SecureStore.getItemAsync(KEY, OPTIONS),
  write: (refreshToken) => SecureStore.setItemAsync(KEY, refreshToken, OPTIONS),
  clear: () => SecureStore.deleteItemAsync(KEY, OPTIONS),
};
