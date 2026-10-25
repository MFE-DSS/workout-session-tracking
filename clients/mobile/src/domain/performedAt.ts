/**
 * D11 with the operator's integrity amendment (spec §8.8bis).
 *
 * NEVER the raw device wall clock alone: an execution time is a server time
 * anchor plus MONOTONIC elapsed time. A wall clock changed by the user or the
 * network does not move it. When no monotonic reading links the set to the
 * anchor (the process restarted in between), the time is flagged `estimated`.
 *
 * The server stays the judge (bounds + ordering); this only produces a claim.
 */

export type TimeAnchor = {
  /** Server time (epoch ms) as read from a read model. */
  serverMs: number;
  /** Monotonic reading (ms) taken at the same instant, valid for this process only. */
  monoMs: number;
  /** Identifies the process that took `monoMs`; a restart invalidates the pair. */
  processId: string;
};

export type PerformedAt = { epochMs: number; estimated: boolean };

export function performedAt(
  anchor: TimeAnchor,
  monoNowMs: number,
  processId: string,
  wallNowMs: number,
): PerformedAt {
  if (anchor.processId === processId && monoNowMs >= anchor.monoMs) {
    return { epochMs: anchor.serverMs + (monoNowMs - anchor.monoMs), estimated: false };
  }
  return { epochMs: wallNowMs, estimated: true };
}

/**
 * The bounds the SERVER will apply (`started_at ≤ t ≤ server now`, non-decreasing
 * within an exercise). Mirrored here only so the lab can show what would be kept;
 * the client never rewrites a time to fit.
 */
export function withinServerBounds(
  t: number,
  sessionStartedMs: number,
  serverNowMs: number,
  previousInExerciseMs: number | null,
): boolean {
  if (t < sessionStartedMs || t > serverNowMs) return false;
  return previousInExerciseMs === null || t >= previousInExerciseMs;
}
