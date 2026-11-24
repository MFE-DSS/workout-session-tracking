import React, { useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View, useWindowDimensions } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { AurenMark } from '../brand/AurenMark';
import { CalibrationLink } from '../plan/calibrationControls';
import { color, space, type } from '../theme';
import { numeric } from './historyView';

export function HistoricalFactsFrame(p: { name: string; status?: string; onBack?: () => void; previous?: boolean; children: React.ReactNode }) {
  const insets = useSafeAreaInsets();
  return <View style={[styles.screen, { paddingTop: insets.top }]}><ScrollView
    style={styles.screen}
    contentInsetAdjustmentBehavior="never"
    contentContainerStyle={{ paddingHorizontal: space.gutter, paddingTop: 12, paddingBottom: insets.bottom + 12, gap: 12 }}
  >
    <View style={styles.masthead}>
      {p.onBack ? <View style={styles.back}><CalibrationLink testID="account-back" label="Retour" onPress={p.onBack} /></View> : null}
      <View style={styles.brand}><AurenMark size={20} color={color.ink} /><Text style={type.eyebrow}>AUREN</Text></View>
    </View>
    <View style={styles.heading}>
      <Text testID={p.status === undefined ? undefined : 'history-session-title'} selectable accessibilityRole="header"
        style={p.status === undefined ? styles.title : type.bodyStrong}>{p.name}</Text>
      {p.status ? <Text selectable style={type.small}>{p.status}</Text> : null}
      {p.previous ? <Text accessibilityLiveRegion="polite" style={type.small}>Lecture précédente</Text> : null}
    </View>
    {p.children}
  </ScrollView></View>;
}

export function HistoricalEntryRow(p: { title: string; status: string; date?: string; onPress: () => void; disabled: boolean; testID?: string }) {
  return <Pressable testID={p.testID} accessibilityRole="button" accessibilityLabel={`${p.date ? `${p.date}, ` : ''}${p.title}, ${p.status}`}
    accessibilityState={{ disabled: p.disabled }} disabled={p.disabled} onPress={p.onPress}
    style={({ pressed }) => [styles.entry, { opacity: p.disabled ? 0.5 : pressed ? 0.6 : 1 }]}>
    <View importantForAccessibility="no-hide-descendants" style={{ width: 8, alignSelf: 'stretch', alignItems: 'center' }}>
      <View style={{ width: 1, flex: 1, backgroundColor: color.line }} />
      <View style={{ width: 5, height: 5, backgroundColor: color.ink3 }} />
      <View style={{ width: 1, flex: 1, backgroundColor: color.line }} />
    </View>
    <View style={styles.entryText}>
      {p.date ? <Text style={type.small}>{p.date}</Text> : null}
      <Text style={type.bodyStrong}>{p.title}</Text>
      <Text style={type.small}>{p.status}</Text>
    </View>
    <Text accessible={false} importantForAccessibility="no" style={type.bodyStrong}>›</Text>
  </Pressable>;
}

export type HistoricalSetFact = {
  set: { set_id: number; kind: string; set_index: number; completed: boolean; reps: number | null; completed_at: string | null; raw_reps_repr?: string | null };
  load: number | null;
  unit: string;
  rawLoad?: string | null;
  hasObservation?: boolean;
  approximate?: boolean;
};

function emptyFact({ set, load, rawLoad, hasObservation }: HistoricalSetFact) {
  return !hasObservation && !set.completed && set.completed_at === null && set.reps === null && load === null && rawLoad == null && set.raw_reps_repr == null;
}

export function HistoricalExerciseInstrument(p: {
  name: string; context?: string; seId: number; selected: boolean; facts: HistoricalSetFact[]; children: React.ReactNode;
}) {
  const [preparationsOpen, setPreparationsOpen] = useState(false);
  const isEmptyPreparation = (fact: HistoricalSetFact) => fact.set.kind === 'warmup' && emptyFact(fact);
  const preparations = p.facts.filter(isEmptyPreparation);
  return <View testID={`history-instrument-${p.seId}`} style={styles.exercise}>
    <View style={styles.heading}>
      <Text selectable accessibilityRole="header" style={type.bodyStrong}>{p.name}</Text>
      {p.selected ? <Text testID={`history-selected-exercise-${p.seId}`} style={type.small}>Exercice sélectionné</Text> : null}
      {p.context ? <Text testID={`history-context-${p.seId}`} style={type.small}>{p.context}</Text> : null}
    </View>
    <View style={styles.ledger}>
      {p.facts.filter(fact => !isEmptyPreparation(fact)).map(fact => <HistoricalSetRow key={fact.set.set_id} fact={fact} />)}
      {preparations.length ? <>
        <CalibrationLink testID={`history-preparations-${p.seId}`} expanded={preparationsOpen}
          label={`${preparations.length} ${preparations.length === 1 ? 'préparation' : 'préparations'} · aucun fait enregistré`}
          onPress={() => setPreparationsOpen(open => !open)} />
        {preparationsOpen ? preparations.map(fact => <HistoricalSetRow key={fact.set.set_id} fact={fact} />) : null}
      </> : null}
    </View>
    {p.children}
  </View>;
}

function HistoricalSetRow({ fact }: { fact: HistoricalSetFact }) {
  const { fontScale } = useWindowDimensions();
  const { set, load, unit, rawLoad, hasObservation, approximate } = fact;
  const empty = emptyFact(fact);
  const incomplete = hasObservation && (load === null || set.reps === null);
  return <View testID={`history-set-${set.set_id}`} style={[styles.fact, fontScale > 1 ? styles.stacked : null]}>
    <View style={styles.factIndex}>
      <Text style={type.eyebrow}>{`${set.kind === 'warmup' ? 'Préparation' : 'Série'} ${set.set_index}`}</Text>
    </View>
    {!empty ? <>
      <Text testID={`history-load-${set.set_id}`} selectable={load !== null}
        accessibilityLabel={rawLoad == null && load === null ? 'Charge inconnue' : undefined} style={styles.value}>
        {rawLoad != null ? 'Charge invalide' : load === null ? '—' : `${numeric(load)} ${unit}`}
      </Text>
      <Text testID={`history-reps-${set.set_id}`} selectable={set.reps !== null}
        accessibilityLabel={set.raw_reps_repr == null && set.reps === null ? 'Répétitions inconnues' : undefined} style={styles.value}>
        {set.raw_reps_repr != null ? 'Répétitions invalides' : set.reps === null ? '—' : `${set.reps} rép.`}
      </Text>
    </> : null}
    <Text style={type.small}>
      {empty ? 'Aucun fait enregistré' : set.completed ? 'Complétée' : 'Non complétée'}
      {incomplete ? ' · Observation incomplète' : ''}
      {approximate ? ' · Heure approximative' : ''}
    </Text>
  </View>;
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: color.field },
  masthead: { flexDirection: 'row', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: 8 },
  back: { minWidth: 48 },
  brand: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  heading: { gap: 4 },
  title: { ...type.title, fontSize: 22, lineHeight: 28 },
  entry: { minHeight: 48, flexDirection: 'row', alignItems: 'center', gap: 8, borderBottomColor: color.line,
    borderBottomWidth: StyleSheet.hairlineWidth, paddingVertical: 8 },
  entryText: { flex: 1, gap: 4 },
  exercise: { gap: 8, borderTopColor: color.line, borderTopWidth: StyleSheet.hairlineWidth, paddingTop: 12 },
  ledger: { backgroundColor: color.plate, paddingHorizontal: 12, paddingVertical: 4 },
  fact: { flexDirection: 'row', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between',
    columnGap: 8, rowGap: 4, paddingVertical: 8, borderBottomColor: color.line, borderBottomWidth: StyleSheet.hairlineWidth },
  factIndex: { minWidth: 48, borderLeftWidth: 2, borderLeftColor: color.ink3, paddingLeft: 8, gap: 2 },
  stacked: { flexDirection: 'column', alignItems: 'stretch' },
  value: { ...type.bodyStrong, ...type.tabular, fontSize: 22, lineHeight: 28, flexShrink: 1 },
});
