import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { IconButton, PrimaryAction } from './components';
import { color, space, type } from './theme';

export type ResumePosition = {
  exerciseIndex: number;
  exerciseTotal: number;
  setsDone: number;
  setsTotal: number;
  exerciseName: string | null;
};

/**
 * D9 / R16 — a session left open (paused, or the app was closed): the same
 * one-question screen as MISSION — « où en suis-je ? » — and one action.
 * Only counted facts: no percentage, no time left (AUREN_INSTRUMENTS §6.3).
 */
export function ResumeScreen(props: {
  name: string;
  subtitle: string | null;
  position: ResumePosition | null;
  note: string | null;
  onResume: () => void;
  onOpenJournal: () => void;
}) {
  const insets = useSafeAreaInsets();
  const p = props.position;
  return (
    <View style={[styles.root, { paddingTop: insets.top + 8, paddingBottom: insets.bottom + 12 }]}>
      <View style={styles.top}>
        <View style={{ width: 48 }} />
        <Text style={type.eyebrow}>AUREN · Séance en pause</Text>
        <IconButton glyph="⋯" label="Journal local" onPress={props.onOpenJournal} />
      </View>
      <Text style={styles.name} accessibilityRole="header" maxFontSizeMultiplier={1.3}>
        {props.name}
      </Text>
      {props.subtitle ? <Text style={[type.body, styles.centered, { marginTop: 4 }]}>{props.subtitle}</Text> : null}

      {p ? (
        <View style={styles.card} accessible accessibilityLabel={`Exercice ${p.exerciseIndex} sur ${p.exerciseTotal}, ${p.setsDone} séries faites sur ${p.setsTotal}`}>
          <Text style={type.eyebrow}>On reprend à</Text>
          {p.exerciseName ? <Text style={[type.bodyStrong, styles.centered, { marginTop: 4 }]}>{p.exerciseName}</Text> : null}
          <Text style={[type.small, styles.centered, type.tabular, { marginTop: 4 }]}>
            {`Exercice ${p.exerciseIndex} sur ${p.exerciseTotal} · ${p.setsDone} séries faites sur ${p.setsTotal}`}
          </Text>
        </View>
      ) : null}
      {props.note ? <Text style={[type.small, styles.centered, { marginTop: space.m }]}>{props.note}</Text> : null}

      <View style={{ flex: 1 }} />
      <PrimaryAction testID="resume" label="Reprendre" sublabel={props.name} onPress={props.onResume} />
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: color.field, paddingHorizontal: space.gutter },
  top: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  centered: { textAlign: 'center' },
  name: { ...type.title, fontSize: 46, lineHeight: 50, marginTop: 30, textAlign: 'center' },
  card: {
    alignItems: 'center',
    marginTop: 30,
    backgroundColor: color.plate,
    borderRadius: 18,
    borderWidth: 1,
    borderColor: color.line,
    padding: 16,
  },
});
