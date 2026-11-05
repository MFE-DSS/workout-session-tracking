/** Review projection only: synthetic declared facts, no network and no storage. */
import React, { useState } from 'react';
import type { TrainingDeclarations, TrainingDeclarationsSnapshot } from '../../../api/trainingPreferences';
import { TrainingPreferencesForm } from '../TrainingPreferencesScreen';
import type { useTrainingPreferencesEditor } from '../useTrainingPreferencesEditor';
import fixture from './trainingDeclarations.fixture.json';

type Editor = ReturnType<typeof useTrainingPreferencesEditor>;
export type PreferencesReviewMode = 'availability' | 'priorities' | 'unknown' | 'offline' | 'saving' | 'loading' | 'saved' | 'expired' | 'refused';
export function TrainingPreferencesReview(p: { mode: PreferencesReviewMode; onClose: () => void }) {
  const initial: Editor['phase'] = p.mode === 'offline' ? 'unavailable' : p.mode === 'unknown' ? 'unknown'
    : p.mode === 'saving' ? 'saving' : p.mode === 'loading' ? 'loading' : p.mode === 'saved' ? 'saved' : p.mode === 'expired' ? 'expired' : 'ready';
  const [phase, setPhase] = useState(initial);
  const [step, setStep] = useState<1 | 2>(['priorities', 'refused', 'unknown', 'saving'].includes(p.mode) ? 2 : 1);
  const [draft, setDraft] = useState<TrainingDeclarations>({ ...fixture.declarations, sessions_per_week: p.mode === 'availability' ? null : 4 });
  const [confirmed, setConfirmed] = useState<TrainingDeclarations>(fixture.declarations);
  const snapshot = { ...fixture, declarations: confirmed } as TrainingDeclarationsSnapshot;
  const editor: Editor = { phase, draft, snapshot: ['loading', 'unavailable', 'expired'].includes(phase) ? null : snapshot,
    dirty: JSON.stringify(draft) !== JSON.stringify(confirmed),
    outcome: p.mode === 'refused' ? { state: 'rejected', code: 'invalid_training_preferences' } : null,
    edit: (changes) => setDraft((old) => ({ ...old, ...changes })),
    reload: async () => { setPhase('ready'); },
    save: async () => { setConfirmed(draft); setPhase('saved'); },
  };
  return <TrainingPreferencesForm editor={editor} step={step} onBack={() => step === 2 ? setStep(1) : p.onClose()}
    onNext={() => setStep(2)} onSave={() => void editor.save()} onReload={() => void editor.reload()}
    onClose={p.onClose} onReconnect={p.onClose} onWebProfile={p.onClose} />;
}
