/**
 * The haptic vocabulary (N0 §10) — six words, then one more for D12.
 *
 * Never decorative, never every second, never the only carrier of a state (the
 * screen always says it too). iOS silences the Taptic Engine itself in Low
 * Power Mode or when haptics are off in Settings; we do not override that.
 */
import * as Haptics from 'expo-haptics';
import { Platform } from 'react-native';

function safe(run: () => Promise<void>): void {
  if (Platform.OS === 'web') return;
  run().catch(() => undefined);
}

export const feedback = {
  /** ± weight / reps: one notch. */
  step: () => safe(() => Haptics.selectionAsync()),
  /** The set is durable ON THE DEVICE (after the SQLite commit, not on the tap). */
  setSaved: () => safe(() => Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success)),
  /** Rest is over, app in the foreground: one stronger beat. */
  restDone: () => safe(() => Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy)),
  /** The next exercise opened by itself. */
  nextExercise: () => safe(() => Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light)),
  /** An action that cannot be taken (missing value, refused change). */
  refused: () => safe(() => Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning)),
  /** A set could not be saved on the device. */
  failed: () => safe(() => Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error)),
  /** D12 — a record or a level reached: three rising beats, once, at the moment it is shown. */
  reward: () =>
    safe(async () => {
      const beat = () => new Promise((r) => setTimeout(r, 90));
      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      await beat();
      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
      await beat();
      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
    }),
};
