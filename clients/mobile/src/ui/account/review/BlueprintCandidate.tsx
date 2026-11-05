/** REVIEW ONLY. Local edits illustrate the approved composition; no API, journal or profile persistence. */
import React, { useState } from 'react';
import { Text, View } from 'react-native';
import { AccountField, AccountFrame, AccountLink } from '../AccountFrame';
import { PrimaryAction, SecondaryButton } from '../../components';
import { color, type } from '../../theme';

export function BlueprintCandidate(p: { step: 1 | 2 | 3 | 4; missing?: boolean; onNext: () => void; onBack: () => void }) {
  const [values, setValues] = useState<Record<string, string>>({});
  const [frequency, setFrequency] = useState<number | null>(null);
  const field = (label: string, placeholder?: string, helper?: string) => <AccountField key={label} label={label} value={values[label] ?? ''} onChangeText={(v) => setValues((old) => ({ ...old, [label]: v }))} placeholder={placeholder} helper={helper} />;
  const title = ['Ton point de départ', 'Ta disponibilité', 'Ton physique', 'Ton premier plan'][p.step - 1];
  const lead = ['Quelques repères pour apprendre à te connaître.', 'Un rythme réaliste, adapté à ta semaine.', 'Ce que tu veux construire. Ce qui compte pour toi.', p.missing ? 'Nous ne pouvons pas encore te proposer un plan personnalisé.' : 'Les informations connues et la suite de ton entraînement.'][p.step - 1];
  return <AccountFrame title={title} lead={lead} step={`${p.step} / 4`} onBack={p.onBack} footer={<>
    <PrimaryAction label={p.step === 4 ? p.missing ? 'Réessayer' : 'Voir ma séance' : 'Continuer'} onPress={p.onNext} />
    {p.step < 4 ? <AccountLink label="Passer pour l’instant" onPress={p.onNext} /> : null}
  </>}>
    {p.step === 1 ? <>
      <View style={{ flexDirection: 'row', gap: 12 }}><View style={{ flex: 1 }}>{field('Taille · cm')}</View><View style={{ flex: 1 }}>{field('Poids · kg')}</View></View>
      {field('Date de mesure', 'JJ/MM/AAAA', 'Choisis la date à laquelle tu as pris cette mesure.')}
      {field('Expérience en musculation', 'À préciser')}
    </> : null}
    {p.step === 2 ? <>
      <Text style={type.eyebrow}>Séances par semaine</Text>
      <View style={{ flexDirection: 'row', gap: 6, flexWrap: 'wrap' }}>{[1,2,3,4,5,6,7].map((n) => <SecondaryButton key={n} label={String(n)} onPress={() => setFrequency(n)} style={{ minWidth: 42, backgroundColor: n === frequency ? color.line : color.plate }} />)}</View>
      {field('Durée habituelle · min')}
      {field('Environnement d’entraînement', 'Ton lieu et ton matériel')}
    </> : null}
    {p.step === 3 ? <>
      {field('Priorités physiques', 'Développement global ou zones prioritaires')}
      {field('Exercices à éviter', 'Facultatif')}
      {field('Contraintes à prendre en compte', 'Facultatif')}
      <Text style={type.small}>Tes déclarations restent distinctes des observations ou conclusions d’AUREN.</Text>
    </> : null}
    {p.step === 4 ? <>
      <Text style={type.eyebrow}>Ce qui est connu</Text><Text style={type.body}>Ton compte est créé.</Text>
      <View style={{ height: 1, backgroundColor: color.line, marginVertical: 8 }} />
      <Text style={type.eyebrow}>Ce qui reste à préciser</Text>
      <Text style={type.body}>{p.missing ? 'Les informations nécessaires à une première proposition ne sont pas encore établies.' : 'Tes informations de départ, ta disponibilité et tes priorités.'}</Text>
    </> : null}
  </AccountFrame>;
}
