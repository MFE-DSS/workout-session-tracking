/**
 * Rest timer — deadline/anchor model (N0 §11).
 *
 * The truth is a DEADLINE, never a decremented counter. Every render, every
 * foreground return, every restore after a kill recomputes the remaining time
 * from it, so the display stays correct whatever the render cadence was.
 */

export type RestClock = {
  /** Wall-clock epoch ms at which the rest ends. Persisted across restarts. */
  deadlineMs: number;
  /** Wall-clock epoch ms at which the rest started (for the ring's proportion). */
  startedMs: number;
};

export const REST_STEP_MS = 15_000;
export const REST_MAX_MS = 10 * 60_000;

export function remainingMs(clock: RestClock, nowMs: number): number {
  return Math.max(0, clock.deadlineMs - nowMs);
}

export function isElapsed(clock: RestClock, nowMs: number): boolean {
  return remainingMs(clock, nowMs) === 0;
}

/** Fraction of the rest still to run, in [0, 1] — drives the ring, not the truth. */
export function remainingFraction(clock: RestClock, nowMs: number): number {
  const total = clock.deadlineMs - clock.startedMs;
  if (total <= 0) return 0;
  return Math.min(1, remainingMs(clock, nowMs) / total);
}

/** ±15 s: moves the deadline, never below now, never beyond the cap. */
export function shift(clock: RestClock, deltaMs: number, nowMs: number): RestClock {
  const next = Math.min(clock.deadlineMs + deltaMs, nowMs + REST_MAX_MS);
  return { ...clock, deadlineMs: Math.max(nowMs, next) };
}

/** `1:12`, `0:05` — whole seconds, rounded UP so `0:00` only shows when it is over. */
export function formatClock(ms: number): string {
  const total = Math.ceil(ms / 1000);
  const m = Math.floor(total / 60);
  const s = total % 60;
  return `${m}:${s.toString().padStart(2, '0')}`;
}
