/** Screen stays on during the workout only — the instrument never asks for it. */
import { activateKeepAwakeAsync, deactivateKeepAwake } from 'expo-keep-awake';

const TAG = 'auren-workout';

export const keepAwake = {
  enable: () => {
    void activateKeepAwakeAsync(TAG).catch(() => undefined);
  },
  disable: () => {
    void deactivateKeepAwake(TAG).catch(() => undefined);
  },
};
