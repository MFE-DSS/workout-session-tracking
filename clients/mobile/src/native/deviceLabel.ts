/**
 * PLAT-01 — the label of the device session opened at login: the real platform and model,
 * never another platform (it was the literal « iPhone AUREN » on every phone).
 * The server keeps 64 characters (`device_auth.DEVICE_LABEL_MAX`); the label stays under it.
 */
import type { DeviceIdentity } from './deviceInfo';

export const DEVICE_LABEL_MAX = 64;

export function deviceLabel(d: Pick<DeviceIdentity, 'platform' | 'model'>): string {
  const model = d.model?.split(/\s+/).join(' ').trim();
  const label = model ? `AUREN · ${d.platform} · ${model}` : `AUREN · ${d.platform}`;
  return label.slice(0, DEVICE_LABEL_MAX);
}
