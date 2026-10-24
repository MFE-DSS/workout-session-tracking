/**
 * One writer at a time.
 *
 * On the first physical-device run a set was shown « non enregistrée ». The
 * likeliest cause: `withExclusiveTransactionAsync` opens its own connection,
 * and the app wrote a lab metric and the session snapshot on the main
 * connection at the same moment — SQLite then refuses one of the writers
 * ("database is locked"). Not yet confirmed by a device log; the commit error
 * is now logged so the next run says. Either way, every journal write goes
 * through this queue, so two writes never overlap. A failed task does not
 * block the ones queued behind it.
 */
export type Serial = <T>(task: () => Promise<T>) => Promise<T>;

export function createSerialQueue(): Serial {
  let tail: Promise<unknown> = Promise.resolve();
  return <T>(task: () => Promise<T>): Promise<T> => {
    const run = tail.then(task, task);
    tail = run.catch(() => undefined);
    return run;
  };
}

/** Retries a transient failure (e.g. a lock held a moment too long), then gives up loudly. */
export async function withRetry<T>(task: () => Promise<T>, attempts = 3, delayMs = 60): Promise<T> {
  let last: unknown;
  for (let i = 0; i < attempts; i += 1) {
    try {
      return await task();
    } catch (e) {
      last = e;
      await new Promise((r) => setTimeout(r, delayMs * (i + 1)));
    }
  }
  throw last;
}
