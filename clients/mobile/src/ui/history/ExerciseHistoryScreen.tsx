import React from 'react';
import { Text, View } from 'react-native';
import type { HistoryOccurrence, ExercisePage } from '../../api/trainingHistory';
import type { ReadSlot } from '../../api/trainingHistoryResource';
import { CalibrationLink } from '../plan/calibrationControls';
import { type } from '../theme';
import { memoryDateLabel, sessionStatus } from './historyView';
import { HistoricalEntryRow, HistoricalFactsFrame } from './HistoricalFactsInstrument';

export function ExerciseHistoryScreen(p: { name: string; read: ReadSlot<ExercisePage<HistoryOccurrence>>; timeZone: string; onSelect: (entry: HistoryOccurrence) => void; onBack: () => void; onMore: () => void }) {
  const r = p.read, v = r.value;
  return <HistoricalFactsFrame name={p.name} onBack={p.onBack} previous={r.previous}>
    {r.status === 'pending' ? <Text style={type.small} accessibilityLiveRegion="polite">Lecture des occurrences…</Text> : null}
    {!v && r.status !== 'pending' ? <Text style={type.small}>Historique à actualiser.</Text> : null}
    {v && !v.coverage_complete ? <Text style={type.small}>Lecture partielle · des occurrences peuvent rester à retrouver.</Text> : null}
    <View>
      {v?.entries.map(e => <HistoricalEntryRow key={e.occurrence_ref} testID={`history-occurrence-${e.occurrence_ref}`} title={memoryDateLabel(e, v.entries, p.timeZone)}
        status={`${sessionStatus(e.status)}${e.excluded_from_stats ? ' · exclue des statistiques' : ''}`}
        disabled={r.status !== 'confirmed'} onPress={() => p.onSelect(e)} />)}
    </View>
    {v?.coverage_complete && !v.entries.length ? <Text style={type.small}>Aucune occurrence dans cette période.</Text> : null}
    {v?.next_cursor && r.status === 'confirmed' ? <CalibrationLink label="Continuer la lecture" onPress={p.onMore} /> : null}
  </HistoricalFactsFrame>;
}
