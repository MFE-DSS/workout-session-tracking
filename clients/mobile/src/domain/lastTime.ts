/**
 * DA-05.1 — « la dernière fois », read from the plan's `previous` (the server's own summary).
 *
 * The operator (2026-10-31): the last time is available, but shown « quand c'est nécessaire, pas
 * systématique ». It is necessary when it TELLS something the screen does not already show: when the load
 * on the dial is not the load of last time (a change prescribed, or the athlete moving away from it).
 */
export type Previous = { relative: string; weights: string; reps: string };

/** The heaviest load of the last time, in kilos; `null` when there is none or it cannot be read. */
export function lastLoadKg(previous: Previous | null): number | null {
  if (!previous) return null;
  const loads = previous.weights
    .split(' / ')
    .map((w) => Number(w))
    .filter((n) => Number.isFinite(n) && n > 0);
  return loads.length ? Math.max(...loads) : null;
}

/** Whether « La dernière fois » is shown under the intention, for the load currently on the dial. */
export function showsLastTime(previous: Previous | null, currentLoad: number | null): boolean {
  if (!previous) return false;
  const last = lastLoadKg(previous);
  return last === null || currentLoad !== last;
}
