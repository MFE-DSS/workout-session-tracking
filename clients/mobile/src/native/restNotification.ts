/**
 * Local "rest over" notification (N0 §11, operator gate amendment 1).
 *
 * This is NOT the timer's truth — the in-app deadline is. The OS decides when
 * a local notification is delivered; the lab MEASURES that distribution
 * (scheduled vs received) and reports it, it never fails the run on it, and it
 * never asks for exact-alarm privileges.
 */
import * as Notifications from 'expo-notifications';
import { Platform } from 'react-native';

const CHANNEL = 'rest';

/** In the foreground the instrument itself announces the end: no banner on top. */
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowBanner: false,
    shouldShowList: true,
    shouldPlaySound: false,
    shouldSetBadge: false,
  }),
});

let permissionAsked = false;

export async function prepareRestNotifications(): Promise<boolean> {
  if (Platform.OS === 'web') return false;
  if (Platform.OS === 'android') {
    await Notifications.setNotificationChannelAsync(CHANNEL, {
      name: 'Fin du repos',
      importance: Notifications.AndroidImportance.HIGH,
      vibrationPattern: [0, 180, 90, 180],
    });
  }
  const current = await Notifications.getPermissionsAsync();
  if (current.granted) return true;
  if (permissionAsked) return false;
  permissionAsked = true;
  const asked = await Notifications.requestPermissionsAsync();
  return asked.granted;
}

/** Returns the notification id, or null when unavailable. */
export async function scheduleRestEnd(seconds: number, body: string): Promise<string | null> {
  if (Platform.OS === 'web' || seconds <= 0) return null;
  try {
    return await Notifications.scheduleNotificationAsync({
      content: {
        title: 'Repos terminé',
        body,
        data: { scheduledForMs: Date.now() + seconds * 1000 },
      },
      trigger: {
        type: Notifications.SchedulableTriggerInputTypes.TIME_INTERVAL,
        seconds: Math.max(1, Math.round(seconds)),
        channelId: CHANNEL,
      },
    });
  } catch {
    return null;
  }
}

export async function cancelRestEnd(id: string | null): Promise<void> {
  if (!id || Platform.OS === 'web') return;
  await Notifications.cancelScheduledNotificationAsync(id).catch(() => undefined);
}

/** The service the instrument consumes; platform specifics stay in this file. */
export const restNotification = {
  prepare: prepareRestNotifications,
  schedule: scheduleRestEnd,
  cancel: cancelRestEnd,
  onDelivery: (record: (latenessMs: number) => void) => onRestNotificationDelivery(record),
};

/**
 * Delivery measurement: fires when a rest notification is received while the
 * app runs, or opened from the lock screen. `lateness` = received − scheduled.
 */
export function onRestNotificationDelivery(record: (latenessMs: number) => void): () => void {
  if (Platform.OS === 'web') return () => undefined;
  const handle = (n: Notifications.Notification) => {
    const scheduled = Number(n.request.content.data?.scheduledForMs);
    if (Number.isFinite(scheduled)) record(n.date - scheduled);
  };
  const a = Notifications.addNotificationReceivedListener(handle);
  const b = Notifications.addNotificationResponseReceivedListener((r) => handle(r.notification));
  return () => {
    a.remove();
    b.remove();
  };
}
