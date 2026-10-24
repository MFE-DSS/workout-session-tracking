/**
 * Device and build identity for the PHYSICAL_DEVICE_GATE evidence — the same
 * shape on every platform. `physical` comes from the OS (`Device.isDevice`),
 * never from a guess: a simulator or emulator always reports `false`.
 */
import Constants from 'expo-constants';
import * as Device from 'expo-device';
import { Platform } from 'react-native';

export type DeviceIdentity = {
  platform: string;
  model: string | null;
  model_id: string | null;
  os_version: string | null;
  physical: boolean;
};

export type BuildIdentity = {
  expo_sdk: string | null;
  react_native: string | null;
  app_version: string | null;
  build_id: string | null;
};

export function deviceIdentity(): DeviceIdentity {
  return {
    platform: Platform.OS,
    model: Device.modelName,
    model_id: Device.modelId ?? null,
    os_version: Device.osVersion,
    physical: Device.isDevice,
  };
}

export function buildIdentity(): BuildIdentity {
  // `Platform.constants` does not exist in the web preview
  const rn = (Platform.constants as { reactNativeVersion?: { major: number; minor: number; patch: number } } | undefined)?.reactNativeVersion;
  return {
    expo_sdk: Constants.expoConfig?.sdkVersion ?? null,
    react_native: rn ? `${rn.major}.${rn.minor}.${rn.patch}` : null,
    app_version: Constants.expoConfig?.version ?? null,
    build_id: process.env.EXPO_PUBLIC_BUILD_ID ?? null,
  };
}
