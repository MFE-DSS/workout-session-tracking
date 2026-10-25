import { useEffect, useRef, useState } from 'react';

/**
 * DA-02.4B.2 — progressive disclosure (operator rulings, 2026-10-25).
 *
 * REST: the value, the line, the band, the cursor, the marker and the prescribed value.
 * ADJUSTING (a finger on the rail, or + / −): the printed scale and the zone names too.
 * Back to REST 1,5 s after the last gesture, so the operator can still read where the
 * cursor landed. Presentation only: nothing here changes what the rail means.
 */
export type Presentation = 'rest' | 'adjusting';

export const REST_AFTER_MS = 1500;

type Timers = {
  set: (fn: () => void, ms: number) => unknown;
  clear: (handle: unknown) => void;
};

const SYSTEM_TIMERS: Timers = {
  set: (fn, ms) => setTimeout(fn, ms),
  clear: (h) => clearTimeout(h as ReturnType<typeof setTimeout>),
};

/** The state machine, with its clock injected: every gesture wakes it, silence puts it back to rest. */
export function disclosureController(onChange: (p: Presentation) => void, timers: Timers = SYSTEM_TIMERS) {
  let pending: unknown = null;
  return {
    wake() {
      onChange('adjusting');
      if (pending !== null) timers.clear(pending);
      pending = timers.set(() => {
        pending = null;
        onChange('rest');
      }, REST_AFTER_MS);
    },
    dispose() {
      if (pending !== null) timers.clear(pending);
      pending = null;
    },
  };
}

/** React binding: `presentation` for the surface, `wake` to call on every gesture. */
export function useDisclosure(): { presentation: Presentation; wake: () => void } {
  const [presentation, setPresentation] = useState<Presentation>('rest');
  const controller = useRef<ReturnType<typeof disclosureController> | null>(null);
  if (controller.current === null) controller.current = disclosureController(setPresentation);
  useEffect(() => () => controller.current?.dispose(), []);
  return { presentation, wake: () => controller.current?.wake() };
}
