import React, { useState } from 'react';
import { StyleSheet, Text, View, useWindowDimensions } from 'react-native';
import type { HistoryPeriod, HistoryEntry, HistoryOccurrence } from '../../api/trainingHistory';
import type { TrainingHistoryState, WeightWindowState } from '../../api/trainingHistoryResource';
import { CalibrationChoices, CalibrationLink } from '../plan/calibrationControls';
import { color, type } from '../theme';
import { dateLabel, memoryDateLabel, periodLabel, sessionStatus } from './historyView';
import { HistoricalEntryRow, HistoricalFactsFrame } from './HistoricalFactsInstrument';
import { WeightTrend } from './WeightTrend';
import { SessionFactsScreen } from './SessionFactsScreen';
import { ExerciseHistoryScreen } from './ExerciseHistoryScreen';

export type ProgressProps = {
  state: TrainingHistoryState;
  weight: WeightWindowState;
  period: HistoryPeriod;
  onPeriod: (period: HistoryPeriod) => void;
  onRefresh: () => void;
  onMore: () => void;
  onExercises: () => void;
  onExercise: (ref: string) => void;
  onMoreExercises: () => void;
  onOccurrence: (entry: HistoryOccurrence) => void;
  onMoreOccurrences: () => void;
  onEntry: (entry: HistoryEntry) => void;
  onBack: () => void;
  onMoreWeight: () => void;
  onDetailExercise?: (seId: number, ref: string) => void;
  onBody?: () => void;
  onNutrition?: () => void;
};

function weekTickLabel(instant: string, timeZone: string) {
  try { return new Intl.DateTimeFormat('fr-FR', { day: '2-digit', month: '2-digit', timeZone }).format(new Date(instant)); }
  catch { return instant; }
}

function weekTimeLabel(instant: string, timeZone: string) {
  try { return new Intl.DateTimeFormat('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit', hourCycle: 'h23', timeZone }).format(new Date(instant)); }
  catch { return instant; }
}

function weekInstantLabel(instant: string, timeZone: string) {
  return `${dateLabel(instant, timeZone)} à ${weekTimeLabel(instant, timeZone)}`;
}

export function TrainingHistoryScreen(p: ProgressProps) {
  const [help, setHelp] = useState(false);
  const large = useWindowDimensions().fontScale >= 1.25;
  const [sessionsExpanded, setSessionsExpanded] = useState<string | null>(null);
  const [weeksExpanded, setWeeksExpanded] = useState<string | null>(null);
  const s = p.state, r = s.sessions, v = r.value;
  const timeZone = v?.window.time_zone ?? 'UTC';
  if (s.selectedEntry !== null) {
    if (s.detail.value) return <SessionFactsScreen detail={s.detail.value} timeZone={timeZone} previous={s.detail.previous}
      onBack={p.onBack} onExercise={link => { if (link.exercise_ref) p.onDetailExercise?.(link.se_id, link.exercise_ref); }} />;
    return <HistoricalFactsFrame name="Séance" onBack={p.onBack}>
      <Text style={type.body}>{s.detail.status === 'pending' ? 'Lecture des faits…' :
        s.detail.status === 'changed' ? 'La séance a changé. Actualise Progrès.' : 'Les faits n’ont pas pu être confirmés.'}</Text>
      <CalibrationLink label="Retour à Progrès" onPress={p.onRefresh} />
    </HistoricalFactsFrame>;
  }
  if (s.selectedExercise) {
    const name = s.selectedExerciseLabel ?? s.exercises.value?.entries.find(e => e.exercise_ref === s.selectedExercise)?.name ?? 'Exercice';
    return <ExerciseHistoryScreen name={name} read={s.occurrences} timeZone={timeZone}
      onSelect={p.onOccurrence} onMore={p.onMoreOccurrences} onBack={p.onBack} />;
  }

  return <HistoricalFactsFrame name="Progrès">
    <View testID="progress-period" style={styles.period}>
      <CalibrationChoices label="Période" value={p.period} options={[{ value: '4w', label: '4 sem.' }, { value: '12w', label: '12 sem.' }, { value: 'all', label: 'Tout' }]} onChange={p.onPeriod} />
      {v ? <Text style={type.small}>{periodLabel(v.window)}</Text> : null}
    </View>
    {r.previous ? <Text testID="progress-previous" accessibilityLiveRegion="polite" style={type.small}>
      Lecture précédente · {r.status === 'pending' ? 'actualisation…' : 'à actualiser'}
    </Text> : r.status === 'pending' ? <Text accessibilityLiveRegion="polite" style={type.small}>Actualisation…</Text> :
      r.status !== 'confirmed' ? <Text style={type.small}>La lecture n’a pas pu être confirmée.</Text> : null}
    {v ? <View style={styles.section}>
      <View style={styles.frequency}>
        <Text testID="progress-frequency" style={styles.frequencyValue}>{String(v.counts.completed_with_work)}</Text>
        <Text style={styles.frequencyLabel}>séances terminées avec séries enregistrées</Text>
      </View>
      {v.weekly_counts.length > 4 && weeksExpanded !== v.read_id ? <Text style={type.small}>Quatre dernières semaines de la période</Text> : null}
      {v.weekly_counts.length ? <Text style={type.small}>Bornes de lecture · Fin exclue</Text> : null}
      {v.weekly_counts.length ? <View style={{ flexDirection: large ? 'column' : 'row', flexWrap: 'wrap', gap: 12 }}>
        {(weeksExpanded === v.read_id ? v.weekly_counts : v.weekly_counts.slice(-4)).map(w => {
          const date = dateLabel(w.week_from, timeZone);
          const cutoff = Date.parse(v.window.until);
          const until = cutoff >= Date.parse(w.week_from) && cutoff < Date.parse(w.week_until) ? v.window.until : w.week_until;
          const count = `${w.completed_with_work} ${w.completed_with_work === 1 ? 'séance' : 'séances'}`;
          return <View testID={`progress-week-${w.week_from}`} key={w.week_from}
            style={[styles.week, w.partial_current_week ? styles.currentWeek : null, { flexBasis: large ? undefined : '20%', flexGrow: 1 }]} accessible
            accessibilityLabel={`Semaine du ${date}, ${count} terminées avec séries enregistrées, du ${weekInstantLabel(w.week_from, timeZone)} inclus au ${weekInstantLabel(until, timeZone)} exclu, ${timeZone}${w.partial_current_week ? ', semaine partielle en cours' : ''}`}>
            <Text style={type.small}>{large ? date : weekTickLabel(w.week_from, timeZone)}</Text>
            <View importantForAccessibility="no-hide-descendants" accessibilityElementsHidden style={styles.weekTrack}>
              {Array.from({ length: Math.min(w.completed_with_work, 8) }, (_, i) => <View key={i}
                testID={`frequency-mark-${w.week_from}/${i}`} style={styles.occurrenceSegment} />)}
              {w.completed_with_work > 8 ? <Text style={type.small}>{`+${w.completed_with_work - 8}`}</Text> : null}
            </View>
            <Text style={styles.weekCount}>{count}</Text>
            <Text testID={`progress-boundary-until-${w.week_from}`} style={type.small}>{`→ ${large ? dateLabel(until, timeZone) : weekTickLabel(until, timeZone)}`}</Text>
            {w.partial_current_week ? <>
              <Text testID={`progress-cutoff-time-${w.week_from}`} style={styles.weekCount}>{weekTimeLabel(until, timeZone)}</Text>
              <Text style={styles.currentLabel}>En cours</Text>
            </> : null}
          </View>;
        })}
      </View> : null}
      {v.weekly_counts.length > 4 ? <CalibrationLink testID="progress-expand-weeks"
        label={weeksExpanded === v.read_id ? 'Réduire les semaines' : 'Toutes les semaines de la période'}
        expanded={weeksExpanded === v.read_id} onPress={() => setWeeksExpanded(weeksExpanded === v.read_id ? null : v.read_id)} /> : null}
    </View> : null}
    <View style={styles.section}>
      <Text accessibilityRole="header" style={type.bodyStrong}>Séances récentes</Text>
      <View>
        {(sessionsExpanded === v?.read_id ? v?.entries : v?.entries.slice(0, 5))?.map(e =>
          <HistoricalEntryRow key={e.session_id} testID={`progress-session-${e.session_id}`} title={e.name || 'Séance'}
            date={memoryDateLabel(e, v!.entries, timeZone)} status={`${sessionStatus(e.status)}${e.excluded_from_stats ? ' · exclue des statistiques' : ''}`}
            disabled={r.status !== 'confirmed'} onPress={() => p.onEntry(e)} />)}
      </View>
      {v && v.entries.length > 5 ? <CalibrationLink testID="progress-expand-sessions"
        label={sessionsExpanded === v.read_id ? 'Réduire la liste' : `Voir les ${v.entries.length - 5} autres séances reçues`}
        expanded={sessionsExpanded === v.read_id} onPress={() => setSessionsExpanded(sessionsExpanded === v.read_id ? null : v.read_id)} /> : null}
      {v?.state === 'EMPTY' ? <Text style={type.small}>Aucune séance enregistrée dans cette période.</Text> : null}
      {v?.next_cursor && r.status === 'confirmed' ? <CalibrationLink label="Séances suivantes" onPress={p.onMore} /> : null}
    </View>
    <View style={styles.section}>
      <Text accessibilityRole="header" style={type.bodyStrong}>Exercice</Text>
      {s.exercises.status === 'idle' ? <CalibrationLink label="Choisir un exercice" onPress={p.onExercises} disabled={r.status !== 'confirmed'} /> : null}
      {s.exercises.status === 'pending' ? <Text style={type.small}>Recherche des exercices…</Text> : null}
      {s.exercises.previous ? <Text style={type.small}>Résultat précédent · à actualiser</Text> : null}
      {s.exercises.value?.entries.map(e => <CalibrationLink key={e.exercise_ref} label={e.name}
        disabled={s.exercises.status !== 'confirmed' || r.status !== 'confirmed'} onPress={() => p.onExercise(e.exercise_ref)} />)}
      {s.exercises.value?.state === 'SCANNING' ? <Text testID="progress-exercises-partial" style={type.small}>Recherche partielle · aucun résultat trouvé à ce stade.</Text> : null}
      {s.exercises.value?.state === 'EMPTY' ? <Text testID="progress-empty-exercises" style={type.small}>Aucun exercice regroupable dans cette période.</Text> : null}
      {s.exercises.value?.next_cursor && s.exercises.status === 'confirmed' ? <CalibrationLink label="Continuer la recherche" onPress={p.onMoreExercises} /> : null}
    </View>
    <View style={styles.section}>
      <View style={styles.sectionHeader}>
        <Text accessibilityRole="header" style={type.bodyStrong}>Poids</Text>
        {p.onBody ? <CalibrationLink testID="progress-weight-write" label="Ouvrir Mesures" onPress={p.onBody} /> : null}
      </View>
      <WeightTrend state={p.weight} onMore={p.onMoreWeight} />
    </View>
    {p.onNutrition ? <CalibrationLink testID="progress-nutrition" label="Journal Nutrition" onPress={p.onNutrition} /> : null}
    <CalibrationLink label="Actualiser" onPress={p.onRefresh} disabled={r.status === 'pending'} />
    <CalibrationLink testID="progress-help" label="Aide" expanded={help} onPress={() => setHelp(open => !open)} />
    {help ? <View testID="progress-help-body" style={{ gap: 8 }}>
      <Text style={type.small}>Les comptes couvrent la période entière : séances terminées, non exclues, avec au moins une série de travail complétée et un fait de répétitions ou de charge. Un statut terminé seul ne prouve pas un entraînement effectué.</Text>
      <Text style={type.small}>Le planning daté n’est pas conservé : aucun objectif ni taux d’adhérence n’est déduit. Les pages relisent les faits actuels ; leurs comptes datent de la première lecture.</Text>
      <Text style={type.small}>Le poids vient uniquement de mesures datées, sous accord applicable. Les points ne sont ni une recommandation ni une prédiction. Les prescriptions et les faits réalisés sont distincts.</Text>
    </View> : null}
  </HistoricalFactsFrame>;
}

const styles = StyleSheet.create({
  period: { gap: 8 },
  section: { gap: 8, borderTopColor: color.line, borderTopWidth: StyleSheet.hairlineWidth, paddingTop: 8 },
  sectionHeader: { flexDirection: 'row', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', columnGap: 12 },
  frequency: { flexDirection: 'row', alignItems: 'baseline', columnGap: 8 },
  frequencyValue: { ...type.title, ...type.tabular, fontSize: 22, lineHeight: 28 },
  frequencyLabel: { ...type.body, flex: 1 },
  week: { gap: 5, borderLeftColor: color.line, borderLeftWidth: 1, paddingLeft: 8, paddingVertical: 6 },
  currentWeek: { borderLeftColor: color.ink3 },
  currentLabel: { ...type.small, color: color.ink2 },
  weekTrack: { flexDirection: 'row', flexWrap: 'wrap', alignItems: 'center', alignContent: 'center', gap: 3, minHeight: 22, borderBottomWidth: 1, borderBottomColor: color.ink3, paddingBottom: 5 },
  occurrenceSegment: { width: 14, height: 5, backgroundColor: color.ink2 },
  weekCount: { ...type.small, ...type.tabular, color: color.ink2 },
});
