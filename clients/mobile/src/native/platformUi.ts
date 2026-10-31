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

/**
 * How a screen keeps its focused field and its action above the soft keyboard.
 * PLAT-01, measured on Android 16: Expo 58 draws Android edge to edge, so the
 * window is no longer resized by the keyboard — without padding, « Se connecter »
 * and the whole numeric-entry sheet sat under it. Android now needs what iOS had.
 */
export const keyboardAvoidance = { behavior: 'padding' as const };

export const fontFamily = {
  text: Platform.select({ ios: 'System', android: 'sans-serif', default: undefined }),
  numerals: Platform.select({ ios: 'System', android: 'sans-serif-condensed', default: undefined }),
};
