/** Owner-scoped form orchestration. Confirmed facts remain separate from an unsent draft. */
import { useCallback, useEffect, useMemo, useReducer } from 'react';
import type { TrainingDeclarations, TrainingDeclarationsOutcome, TrainingDeclarationsSnapshot, TrainingPreferencesClient } from '../../api/trainingPreferences';

type Phase = 'loading' | 'ready' | 'saving' | 'saved' | 'unknown' | 'unavailable' | 'expired';
type EditorState = {
  phase: Phase;
  snapshot: TrainingDeclarationsSnapshot | null;
  draft: TrainingDeclarations | null;
  outcome: TrainingDeclarationsOutcome | null;
};
const empty = (): EditorState => ({ phase: 'loading', snapshot: null, draft: null, outcome: null });
const copy = (d: TrainingDeclarations): TrainingDeclarations => ({ ...d,
  focus_priorities: d.focus_priorities === null ? null : [...d.focus_priorities],
  available_equipment: d.available_equipment === null ? null : [...d.available_equipment],
});
function equal(a: TrainingDeclarations, b: TrainingDeclarations): boolean {
  // Priorities are ordered; equipment families are a set in the canonical service.
  const families = (v: string[] | null) => v === null ? null : [...v].sort();
  return a.sessions_per_week === b.sessions_per_week &&
    JSON.stringify(a.focus_priorities) === JSON.stringify(b.focus_priorities) &&
    JSON.stringify(families(a.available_equipment)) === JSON.stringify(families(b.available_equipment));
}
const dirty = (s: EditorState) => !!s.snapshot && !!s.draft && !equal(s.snapshot.declarations, s.draft);
const expired = (r: TrainingDeclarationsOutcome) => r.state === 'cancelled' ||
  (r.state === 'rejected' && ['auth', 'unauthorized'].includes(r.code ?? ''));

export type TrainingPreferencesGateway = Pick<TrainingPreferencesClient, 'read' | 'save'>;
export function useTrainingPreferencesEditor(client: TrainingPreferencesGateway) {
  const [, render] = useReducer((v: number) => v + 1, 0);
  // A different client starts with no old owner's values, even before effects run.
  const scope = useMemo(() => ({ active: false, busy: false, serial: 0, state: empty() }), [client]);
  const publish = useCallback((state: EditorState) => { scope.state = state; if (scope.active) render(); }, [scope]);
  const edit = useCallback((changes: Partial<TrainingDeclarations>) => {
    if (!scope.active || scope.busy || !scope.state.draft || !['ready', 'saved'].includes(scope.state.phase)) return;
    publish({ ...scope.state, phase: 'ready', draft: copy({ ...scope.state.draft, ...changes }), outcome: null });
  }, [scope, publish]);

  const reload = useCallback(async () => {
    if (!scope.active || scope.busy) return;
    scope.busy = true;
    const ticket = ++scope.serial;
    const before = scope.state;
    const keepDraft = dirty(before);
    publish({ ...before, phase: 'loading', outcome: null });
    try {
      const result = await client.read();
      if (!scope.active || ticket !== scope.serial) return;
      if (result.state === 'confirmed') {
        publish({ phase: 'ready', snapshot: result.value,
          draft: copy(keepDraft && before.draft ? before.draft : result.value.declarations), outcome: result });
      } else if (expired(result)) {
        publish({ ...empty(), phase: 'expired', outcome: result });
      } else {
        publish({ ...before, phase: before.phase === 'unknown' ? 'unknown' : 'unavailable', outcome: result });
      }
    } finally { if (ticket === scope.serial) scope.busy = false; }
  }, [client, scope, publish]);

  const save = useCallback(async () => {
    const before = scope.state;
    if (!scope.active || scope.busy || !before.draft || !dirty(before) || !['ready', 'saved'].includes(before.phase)) return;
    scope.busy = true;
    const ticket = ++scope.serial;
    publish({ ...before, phase: 'saving', outcome: null });
    try {
      const result = await client.save(copy(before.draft));
      if (!scope.active || ticket !== scope.serial) return;
      if (result.state === 'confirmed') publish({ phase: 'saved', snapshot: result.value, draft: copy(result.value.declarations), outcome: result });
      else if (expired(result)) publish({ ...empty(), phase: 'expired', outcome: result });
      else publish({ ...before, phase: result.state === 'unknown' ? 'unknown' : 'ready', outcome: result });
    } finally { if (ticket === scope.serial) scope.busy = false; }
  }, [client, scope, publish]);

  useEffect(() => {
    scope.active = true;
    void reload();
    return () => { scope.active = false; scope.serial += 1; scope.busy = false; };
  }, [scope, reload]);

  return { ...scope.state, dirty: dirty(scope.state), edit, reload, save };
}
