import React, { useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { scheme } from '../domain/format';
import type { Mission } from '../domain/types';
import { IconButton, PrimaryAction, Sheet, SheetRow } from './components';
import { color, space, type } from './theme';

const DAY = new Intl.DateTimeFormat('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' });

/**
 * MISSION / READY — « Qu'est-ce que je fais maintenant, et pourquoi ? »
 * One question, one action. The reason is the engine's own words; no duration
 * is shown because none is estimated (AUREN_INSTRUMENTS §6.2bis-3).
 */
export function MissionScreen(props: {
  mission: Mission;
  onStart: (slug: string) => void;
  onOpenLab: () => void;
  onSecondaryOpened: () => void;
}) {
  const insets = useSafeAreaInsets();
  const [why, setWhy] = useState(false);
  const m = props.mission;
  const secondary = m.reason.reasons.filter((r) => r !== m.reason.phrase);

  return (
    <View style={[styles.root, { paddingTop: insets.top + 8, paddingBottom: insets.bottom + 12 }]}>
      <View style={styles.top}>
        <View style={{ width: 44 }} />
        <Text style={type.eyebrow}>AUREN · Aujourd’hui</Text>
        <IconButton icon="more" label="Journal du labo" onPress={props.onOpenLab} />
      </View>
      <Text style={[type.small, styles.date]}>{DAY.format(new Date())}</Text>

      <Text style={styles.name} accessibilityRole="header" maxFontSizeMultiplier={1.3}>
        {m.template.name}
      </Text>
      {m.template.subtitle ? <Text style={[type.body, styles.subtitle]}>{m.template.subtitle}</Text> : null}

      <Pressable
        accessibilityRole="button"
        accessibilityLabel={`Pourquoi : ${m.reason.reasons.join(' ')}`}
        accessibilityHint="Ouvre le détail et les autres séances"
        onPress={() => {
          setWhy(true);
          props.onSecondaryOpened();
        }}
        style={styles.reason}
      >
        <Text style={styles.reasonLead}>{m.reason.phrase}</Text>
        {secondary.map((r) => (
          <Text key={r} style={[type.body, styles.reasonMore]}>
            {r}
          </Text>
        ))}
        <Text style={styles.provenance}>
          {m.reason.provenance === 'mesurée' ? 'Mesuré' : 'Lecture partielle'} · {m.reason.horizon}
        </Text>
      </Pressable>

      <View style={styles.scope}>
        <Figure value={m.scope.exercise_count} label={m.scope.exercise_count > 1 ? 'exercices' : 'exercice'} />
        <Figure value={m.scope.work_set_count} label="séries de travail" />
      </View>

      <View style={styles.first}>
        <Text style={type.eyebrow}>On commence par</Text>
        <Text style={[type.bodyStrong, { marginTop: 4, textAlign: 'center' }]}>{m.scope.first_exercise.name}</Text>
        <Text style={[type.small, { marginTop: 2 }]}>{scheme(m.scope.first_exercise.set_scheme)}</Text>
      </View>

      <View style={{ flex: 1 }} />
      <PrimaryAction
        testID="start"
        label="Démarrer"
        sublabel={m.template.name}
        hint="Démarre la séance recommandée"
        onPress={() => props.onStart(m.template.slug)}
      />

      <Sheet visible={why} title="Pourquoi cette séance" onClose={() => setWhy(false)}>
        {m.reason.reasons.map((r) => (
          <SheetRow key={r} title={r} />
        ))}
        {m.reason.limiting.length ? (
          <SheetRow title="Ce qui limite" detail={m.reason.limiting.join(' · ')} />
        ) : null}
        <Text style={[type.eyebrow, { marginTop: space.l, marginBottom: 4 }]}>Autres séances possibles</Text>
        {m.alternatives.map((a) => (
          <SheetRow
            key={a.slug}
            title={a.name}
            detail={a.phrase}
            a11y={`Démarrer plutôt ${a.name}`}
            onPress={() => {
              setWhy(false);
              props.onStart(a.slug);
            }}
          />
        ))}
      </Sheet>
    </View>
  );
}

function Figure(props: { value: number; label: string }) {
  return (
    <View style={{ alignItems: 'center' }} accessible accessibilityLabel={`${props.value} ${props.label}`}>
      <Text style={type.figure} maxFontSizeMultiplier={1.3}>
        {props.value}
      </Text>
      <Text style={[type.eyebrow, { marginTop: 2 }]}>{props.label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: color.field, paddingHorizontal: space.gutter },
  top: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  date: { marginTop: 10, textTransform: 'capitalize', textAlign: 'center' },
  name: { ...type.title, fontSize: 46, lineHeight: 50, marginTop: 22, textAlign: 'center' },
  subtitle: { textAlign: 'center', marginTop: 4 },
  reason: { marginTop: 26, paddingLeft: 14, borderLeftWidth: 3, borderLeftColor: color.system, paddingVertical: 2 },
  reasonLead: { ...type.bodyStrong, fontSize: 21, lineHeight: 27 },
  reasonMore: { marginTop: 6, fontSize: 16, lineHeight: 21 },
  provenance: { ...type.eyebrow, color: color.system, marginTop: 10, letterSpacing: 1 },
  scope: { flexDirection: 'row', justifyContent: 'center', gap: 48, marginTop: 30 },
  first: {
    alignItems: 'center',
    marginTop: 26,
    backgroundColor: color.plate,
    borderRadius: 18,
    borderWidth: 1,
    borderColor: color.line,
    padding: 16,
  },
});
