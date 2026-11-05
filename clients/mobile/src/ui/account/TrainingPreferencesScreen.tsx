import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Text, View } from 'react-native';
import { confirmDiscardPreferences } from '../../native/discardPreferences';
import { PrimaryAction, SecondaryButton, Sheet, SheetRow } from '../components';
import { color, type } from '../theme';
import { AccountFrame, AccountLink, AccountMessage } from './AccountFrame';
import { useTrainingPreferencesEditor, type TrainingPreferencesGateway } from './useTrainingPreferencesEditor';

type Editor = ReturnType<typeof useTrainingPreferencesEditor>;
type FormProps = {
  editor: Editor; step: 1 | 2; onBack: () => void; onNext: () => void;
  onSave: () => void; onReload: () => void; onClose: () => void; onReconnect: () => void;
  onWebProfile?: () => void;
};

/** The same real composition is used in production and on the isolated review bench. */
export function TrainingPreferencesForm(p: FormProps) {
  const e = p.editor;
  const footer = (action: React.ReactNode) => <>{action}{p.onWebProfile ? <AccountLink testID="preferences-web-profile" label="Profil complet sur le site" onPress={p.onWebProfile} /> : null}</>;
  if (e.phase === 'saved') return <AccountFrame title="Préférences enregistrées."
    footer={footer(<PrimaryAction testID="preferences-done" label="Revenir au profil" onPress={p.onClose} />)} />;
  if (!e.snapshot || !e.draft || e.phase === 'unavailable' || e.phase === 'expired') {
    const message = e.phase === 'loading' ? 'Lecture de tes préférences sur AUREN…' : e.phase === 'expired'
      ? 'Reconnecte-toi pour retrouver tes préférences. Les séries sur cet appareil restent conservées.'
      : 'Tes préférences n’ont pas pu être lues. Réessaie avec une connexion.';
    return <AccountFrame title="Tes préférences" onBack={p.onBack} footer={footer(<PrimaryAction testID="preferences-reload"
      busy={e.phase === 'loading'} label={e.phase === 'loading' ? 'Lecture…' : e.phase === 'expired' ? 'Me reconnecter' : 'Réessayer'}
      onPress={e.phase === 'expired' ? p.onReconnect : p.onReload} />)}><AccountMessage text={message} /></AccountFrame>;
  }
  const draft = e.draft, options = e.snapshot.options;
  const locked = !['ready', 'saved'].includes(e.phase);
  const choice = (id: string, label: string, selected: boolean, onPress: () => void) => <SecondaryButton key={id}
    testID={id} label={label} selected={selected} disabled={locked} onPress={onPress}
    style={{ minWidth: 44, minHeight: 44, backgroundColor: selected ? color.line : color.plate }} />;
  const toggle = (key: 'focus_priorities', value: string) => {
    const previous = draft[key] ?? [];
    e.edit({ [key]: previous.includes(value) ? previous.filter((v) => v !== value) : [...previous, value] });
  };
  const unknown = e.phase === 'unknown';
  return <AccountFrame title={p.step === 1 ? 'Ta disponibilité' : 'Tes priorités'} step={`${p.step} / 2`}
    lead={p.step === 1 ? undefined : 'Les zones que tu souhaites privilégier.'}
    onBack={p.onBack} backDisabled={e.phase === 'saving'} footer={footer(unknown
      ? <PrimaryAction testID="preferences-reload" label="Relire sur AUREN" onPress={p.onReload} />
      : <PrimaryAction testID={p.step === 1 ? 'preferences-next' : 'preferences-save'}
        label={e.phase === 'saving' ? 'Enregistrement…' : p.step === 1 ? 'Continuer' : e.dirty ? 'Enregistrer' : 'Terminer'}
        busy={e.phase === 'saving' || e.phase === 'loading'} onPress={p.step === 1 ? p.onNext : e.dirty ? p.onSave : p.onClose} />)}>
    {unknown ? <AccountMessage text="Enregistrement à vérifier. Relis les valeurs actuelles sur AUREN avant une nouvelle tentative." /> : null}
    {e.phase === 'ready' && e.outcome?.state === 'rejected' ? <AccountMessage alert text="Ces préférences ont été refusées. Ta saisie est conservée." /> : null}
    {p.step === 1 ? <>
      <Text style={type.eyebrow}>Séances par semaine</Text>
      <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 8 }}>
        {choice('preferences-frequency-null', 'Non déclaré', draft.sessions_per_week === null, () => e.edit({ sessions_per_week: null }))}
        {Array.from({ length: options.sessions_per_week.max - options.sessions_per_week.min + 1 }, (_, i) => i + options.sessions_per_week.min)
          .map((n) => choice(`preferences-frequency-${n}`, String(n), draft.sessions_per_week === n, () => e.edit({ sessions_per_week: n })))}
      </View>
    </> : <>
      <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 8 }}>
        {choice('preferences-focus-null', 'Non déclaré', draft.focus_priorities === null, () => e.edit({ focus_priorities: null }))}
        {choice('preferences-focus-empty', 'Sans priorité', draft.focus_priorities?.length === 0, () => e.edit({ focus_priorities: [] }))}
      </View>
      <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 8 }}>{options.focus_priorities.map((c) => {
        const rank = draft.focus_priorities?.indexOf(c.value) ?? -1;
        return <View key={c.value} style={{ width: '48%', flexGrow: 1 }}>{choice(`preferences-focus-${c.value}`, rank < 0 ? c.label : `${rank + 1} · ${c.label}`, rank >= 0, () => toggle('focus_priorities', c.value))}</View>;
      })}</View>
    </>}
    <Text style={type.small}>{p.step === 1 ? 'Tu peux laisser un choix non déclaré.' : 'Choix facultatifs ; un second appui retire une zone.'}</Text>
  </AccountFrame>;
}

export function TrainingPreferencesScreen(p: { client: TrainingPreferencesGateway; onClose: () => void; onReconnect: () => void; onWebProfile?: () => void; registerExit?: (handler: (() => void) | null) => void }) {
  const editor = useTrainingPreferencesEditor(p.client);
  const [step, setStep] = useState<1 | 2>(1);
  const [discard, setDiscard] = useState(false);
  const saving = useRef(false);
  const lifetime = useMemo(() => ({ active: false }), [p.client]);
  useEffect(() => { lifetime.active = true; return () => { lifetime.active = false; }; }, [lifetime]);
  const close = useCallback(() => { if (lifetime.active) p.onClose(); }, [lifetime, p.onClose]);
  useEffect(() => { setStep(1); setDiscard(false); }, [p.client]);
  const back = useCallback(() => {
    if (saving.current || editor.phase === 'saving') return;
    if (step === 2 && editor.phase !== 'saved') { setStep(1); return; }
    if (editor.dirty) { if (!confirmDiscardPreferences(close)) setDiscard(true); }
    else close();
  }, [editor.dirty, editor.phase, step, close]);
  useEffect(() => { p.registerExit?.(back); return () => p.registerExit?.(null); }, [p.registerExit, back]);
  const save = async () => {
    if (saving.current) return;
    saving.current = true;
    try { await editor.save(); } finally { saving.current = false; }
  };
  return <>
    <TrainingPreferencesForm editor={editor} step={step} onBack={back} onNext={() => setStep(2)} onSave={() => void save()}
      onReload={() => void editor.reload()} onClose={close} onReconnect={p.onReconnect} onWebProfile={p.onWebProfile} />
    <Sheet visible={discard} title="Quitter les préférences ?" onClose={() => setDiscard(false)}>
      <AccountMessage text="Les modifications non enregistrées seront perdues." />
      <SheetRow title="Continuer à modifier" onPress={() => setDiscard(false)} />
      <SheetRow title="Quitter" onPress={close} />
    </Sheet>
  </>;
}
