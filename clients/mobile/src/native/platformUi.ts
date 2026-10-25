/**
 * The ONLY place where UI presentation depends on the platform.
 *
 * Screens and the workout domain never test `Platform.OS`; they consume these
 * resolved values. iOS gets its native page sheet; Android (and the web
 * preview) get a transparent modal with a bottom panel.
 */
import { Platform } from 'react-native';

export const nativeSheet = {
  /** `pageSheet` is the system sheet on iOS; elsewhere a bottom panel is drawn. */
  presentationStyle: Platform.OS === 'ios' ? ('pageSheet' as const) : undefined,
  drawsOwnBackdrop: Platform.OS !== 'ios',
};

export const fontFamily = {
  text: Platform.select({ ios: 'System', android: 'sans-serif', default: undefined }),
  numerals: Platform.select({ ios: 'System', android: 'sans-serif-condensed', default: undefined }),
};
