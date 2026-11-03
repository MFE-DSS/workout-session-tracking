/**
 * MOB-01 — where the native shell opens and what back does inside it
 * (`openspec/changes/native-navigation-shell`, spec `mobile/navigation-shell`).
 *
 * The shell holds four spaces (operator decision D1). An open workout — local or server — is offered for resume
 * BEFORE any space, whatever tab was active at close; without a valid session nothing but the login is reachable.
 * During a workout the shell is not on screen: `backAction` (`mobile/android-platform`) decides.
 */
export const SPACES = ['today', 'programs', 'progress', 'profile'] as const;
export type Space = (typeof SPACES)[number];
export const FIRST_SPACE: Space = SPACES[0];

export type OpenContext = {
  /** the token is still being restored or refreshed */
  authPending: boolean;
  /** a valid session exists */
  signedIn: boolean;
  /** a workout is open, locally or on the server */
  openWorkout: boolean;
};

export type OpenTarget = 'boot' | 'login' | 'resume' | Space;

export function initialSpace(c: OpenContext): OpenTarget {
  if (c.authPending) return 'boot';
  if (!c.signedIn) return 'login';
  if (c.openWorkout) return 'resume';
  return FIRST_SPACE;
}

export type ShellBackContext = {
  space: Space;
  /** screens pushed on the space's own stack above its root */
  depth: number;
};

export type ShellBack = 'pop' | 'first-space' | 'system';

export function backInShell(c: ShellBackContext): ShellBack {
  if (c.depth > 0) return 'pop';
  if (c.space !== FIRST_SPACE) return 'first-space';
  return 'system';
}
