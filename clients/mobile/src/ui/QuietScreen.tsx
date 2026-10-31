import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { IconButton, PrimaryAction, SheetRow } from './components';
import { color, space, type } from './theme';

/**
 * D9 — the states between two missions, said plainly and quietly: offline,
 * nothing servable today, or a session the instrument does not run yet. One
 * line of fact, at most one way forward — never an invented mission.
 */
export function QuietScreen(props: {
  title: string;
  text: string;
  action?: { label: string; onPress: () => void };
  choices?: { key: string; title: string; detail?: string; onPress: () => void }[];
  onOpenJournal: () => void;
}) {
  const insets = useSafeAreaInsets();
  return (
    <View style={[styles.root, { paddingTop: insets.top + 8, paddingBottom: insets.bottom + 12 }]}>
      <View style={styles.top}>
        <View style={{ width: 44 }} />
        <Text style={type.eyebrow}>AUREN · Aujourd’hui</Text>
        <IconButton icon="more" label="Journal local" onPress={props.onOpenJournal} />
      </View>
      <Text style={styles.title} accessibilityRole="header">{props.title}</Text>
      <Text style={[type.body, styles.text]} accessibilityLiveRegion="polite">{props.text}</Text>
      {props.choices?.length ? (
        <View style={{ marginTop: space.l }}>
          {props.choices.map((c) => (
            <SheetRow key={c.key} title={c.title} detail={c.detail} onPress={c.onPress} />
          ))}
        </View>
      ) : null}
      <View style={{ flex: 1 }} />
      {props.action ? <PrimaryAction tone="quiet" label={props.action.label} onPress={props.action.onPress} /> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: color.field, paddingHorizontal: space.gutter },
  top: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  title: { ...type.title, fontSize: 34, lineHeight: 40, marginTop: 40, textAlign: 'center' },
  text: { marginTop: 12, textAlign: 'center', color: color.ink2 },
});
