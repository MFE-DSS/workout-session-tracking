/**
 * PLAT-01 — what the Android hardware back does (`openspec/changes/android-pilot-readiness`,
 * spec `mobile/android-platform`).
 *
 * During a workout (a set or a rest, not the resume screen) back must never leave the app:
 * it opens the same « Quitter la séance » sheet as ✕. An open sheet closes, and nothing
 * else happens (its `Modal.onRequestClose` already does it). Everywhere else the system
 * decides — the workout survives the exit and is restored at relaunch.
 */
export type BackContext = {
  screen: 'BOOT' | 'LOGIN' | 'APP';
  /** phase SET or REST */
  inWorkout: boolean;
  /** the workout shows the resume screen */
  paused: boolean;
  /** any sheet is open */
  sheetOpen: boolean;
};

export type BackAction = 'close-sheet' | 'exit-sheet' | 'system';

export function backAction(c: BackContext): BackAction {
  if (c.sheetOpen) return 'close-sheet';
  if (c.screen === 'APP' && c.inWorkout && !c.paused) return 'exit-sheet';
  return 'system';
}
