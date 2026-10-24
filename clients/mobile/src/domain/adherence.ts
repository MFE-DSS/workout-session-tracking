/**
 * Adherence to the agreed programme — LAB PROTOTYPE (engine V2, ruling 11).
 *
 * Planned rest is part of the programme: a week is HELD when it reaches the
 * sessions the user planned, and a rest day never breaks anything. Sessions
 * beyond the plan earn nothing — the engine does not reward extra sessions,
 * extra sets or tonnage. No points, no levels: those counted sessions.
 */
export type DoneSession = { atMs: number; slug: string };

export function weekStartMs(nowMs: number): number {
  const d = new Date(nowMs);
  const monday = (d.getDay() + 6) % 7;
  return new Date(d.getFullYear(), d.getMonth(), d.getDate() - monday).getTime();
}

const WEEK_DAYS = 7;

function weekBefore(startMs: number): number {
  const d = new Date(startMs);
  return new Date(d.getFullYear(), d.getMonth(), d.getDate() - WEEK_DAYS).getTime();
}

function countBetween(sessions: DoneSession[], fromMs: number, toMs: number): number {
  return sessions.filter((s) => s.atMs >= fromMs && s.atMs < toMs).length;
}

export function sessionsThisWeek(sessions: DoneSession[], nowMs: number): number {
  return countBetween(sessions, weekStartMs(nowMs), nowMs + 1);
}

/**
 * Consecutive HELD weeks, ending with the current one if it is already held,
 * otherwise with the last finished week. Counting stops at the first week
 * that did not reach its plan.
 */
export function weeksHeld(sessions: DoneSession[], nowMs: number, planned: number): number {
  if (planned <= 0) return 0;
  let start = weekStartMs(nowMs);
  let end = nowMs + 1;
  let held = 0;
  if (countBetween(sessions, start, end) < planned) {
    end = start;
    start = weekBefore(start);
  }
  while (countBetween(sessions, start, end) >= planned) {
    held += 1;
    end = start;
    start = weekBefore(start);
  }
  return held;
}
