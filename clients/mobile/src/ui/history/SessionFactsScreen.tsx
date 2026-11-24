import React, { useState } from 'react';
import { Text, View } from 'react-native';
import type { HistoricalDetail, HistoryExerciseLink } from '../../api/trainingHistory';
import type { SetFactV3 } from '../../domain/planV3Types';
import { CalibrationLink } from '../plan/calibrationControls';
import { type } from '../theme';
import { dateLabel, sessionStatus } from './historyView';
import { HistoricalExerciseInstrument, HistoricalFactsFrame } from './HistoricalFactsInstrument';

function observationUnit(observation: SetFactV3 | null) {
  switch (observation?.context.load_semantics) {
    case 'PER_IMPLEMENT': return 'kg par haltère';
    case 'MACHINE_DISPLAY_KG': return 'kg affichés';
    case 'TOTAL_EXTERNAL': return 'kg externes totaux';
    default: return '· unité non confirmée';
  }
}

function sideLabel(side: string) {
  return side === 'BILATERAL' ? 'bilatéral' : side === 'LEFT' ? 'côté gauche' : side === 'RIGHT' ? 'côté droit' : 'côté inconnu';
}

function sessionLine(session: { started_at: string; status: string; excluded_from_stats: boolean }, timeZone: string) {
  return `${dateLabel(session.started_at, timeZone)} · ${sessionStatus(session.status)}${session.excluded_from_stats ? ' · exclue des statistiques' : ''}`;
}

function journalTime(set: { completed: boolean; completed_at: string | null }) {
  return set.completed || set.completed_at !== null ?
    ` · horodatage du journal ${set.completed_at ?? 'non renseigné'}` : '';
}

export function SessionFactsScreen(p: { detail: HistoricalDetail; onBack: () => void; timeZone: string; previous?: boolean; onExercise?: (link: HistoryExerciseLink) => void }) {
  const [prescription, setPrescription] = useState(false);
  const [sources, setSources] = useState<Set<number>>(() => new Set());
  const d = p.detail;
  const selected = d.selected_se_id ?? (d.kind === 'LEGACY' ? d.facts.selected_se_id : undefined);
  const ordered = <T extends { se_id: number }>(items: T[]) => selected === undefined ? items :
    [...items].sort((a, b) => Number(b.se_id === selected) - Number(a.se_id === selected));
  const historyLink = (seId: number) => {
    const link = d.exercise_links?.find(item => item.se_id === seId);
    return link?.exercise_ref && p.onExercise ?
      <CalibrationLink testID={`history-exercise-${seId}`} label="Historique du mouvement" disabled={p.previous} onPress={() => p.onExercise?.(link)} /> : null;
  };
  const sourceLink = (seId: number) => <CalibrationLink testID={`history-provenance-${seId}`} label="Sources et limites"
    expanded={sources.has(seId)} onPress={() => setSources(old => {
      const next = new Set(old);
      if (next.has(seId)) next.delete(seId);
      else next.add(seId);
      return next;
    })} />;

  if (d.kind === 'LEGACY') {
    const { exercises, session, cardio } = d.facts;
    return <HistoricalFactsFrame name={session.name || 'Séance'} onBack={p.onBack} previous={p.previous} status={sessionLine(session, p.timeZone)}>
      {ordered(exercises).map(e => <HistoricalExerciseInstrument key={e.se_id} name={e.executed_name || e.prescribed_name || e.code}
        seId={e.se_id} context="Matériel non capturé" selected={selected === e.se_id}
        facts={e.sets.map(set => ({ set, load: set.weight_kg, rawLoad: set.raw_weight_repr, unit: 'kg saisis' }))}>
        {historyLink(e.se_id)}
        {sourceLink(e.se_id)}
        {sources.has(e.se_id) ? <View style={{ gap: 8 }}>
          <Text selectable style={type.small}>Journal historique · début {session.started_at}{session.ended_at ? ` · fin ${session.ended_at}` : ''}</Text>
          {e.substituted_name ? <Text selectable style={type.small}>Mouvement remplacé · {e.prescribed_name}</Text> : null}
          {e.sets.map(set => <View key={set.set_id} style={{ gap: 4 }}>
            <Text selectable style={type.small}>
              {set.kind === 'warmup' ? 'Préparation' : 'Série'} {set.set_index}{journalTime(set)}
            </Text>
            {set.raw_weight_repr != null ? <Text selectable style={type.small}>Valeur de charge source · {set.raw_weight_repr}</Text> : null}
            {set.raw_reps_repr != null ? <Text selectable style={type.small}>Répétitions source · {set.raw_reps_repr}</Text> : null}
          </View>)}
          <Text style={type.small}>Prescription non capturée. La masse externe totale reste inconnue.</Text>
        </View> : null}
      </HistoricalExerciseInstrument>)}
      {cardio.duration_min !== null ? <Text selectable style={type.body}>
        Cardio · {cardio.duration_min} min{cardio.bpm_avg !== null ? ` · ${cardio.bpm_avg} bpm` : ''}
        {cardio.machine_calories !== null ? ` · ${cardio.machine_calories} kcal machine` : ''}
      </Text> : null}
    </HistoricalFactsFrame>;
  }

  const execution = d.execution;
  return <HistoricalFactsFrame name="Séance conservée" onBack={p.onBack} previous={p.previous} status={sessionLine(execution, p.timeZone)}>
    {ordered(execution.exercises).map(e => <HistoricalExerciseInstrument key={e.se_id} name={e.canonical_exercise_id}
      seId={e.se_id} selected={selected === e.se_id}
      facts={e.sets.map(set => ({
        set, hasObservation: set.observation !== null, load: set.observation?.setting?.value ?? null,
        unit: observationUnit(set.observation), approximate: set.observation?.performed_at_estimated,
      }))}>
      {historyLink(e.se_id)}
      {sourceLink(e.se_id)}
      {sources.has(e.se_id) ? <View style={{ gap: 8 }}>
        <Text selectable style={type.small}>Journal historique · début {execution.started_at}{execution.ended_at ? ` · fin ${execution.ended_at}` : ''}</Text>
        <Text selectable style={type.small}>Appareil · {e.prescription.context.equipment_ref}</Text>
        <Text selectable style={type.small}>Réalisation · {e.prescription.context.realization_ref}</Text>
        <Text selectable style={type.small}>Contexte prescrit · {e.prescription.context.context_ref} · {sideLabel(e.prescription.context.side)}</Text>
        {e.sets.map(set => <View key={set.set_id} style={{ gap: 4 }}>
          <Text selectable style={type.small}>Série {set.set_index} · version {set.revision}{journalTime(set)}</Text>
          {set.observation ? <Text selectable style={type.small}>
            Contexte observé · {set.observation.context.context_ref} · {set.observation.context.equipment_ref} · {sideLabel(set.observation.context.side)}
          </Text> : null}
          {set.observation ? <Text selectable style={type.small}>
            Occurrence déclarée · {set.observation.performed_at}{set.observation.performed_at_estimated ? ' · heure approximative' : ''}
          </Text> : null}
        </View>)}
        <Text style={type.small}>Faits consultables en lecture seule.</Text>
      </View> : null}
      {prescription ? <Text style={type.small}>Prescription capturée : {e.prescription.dose.work_sets} séries · {e.prescription.dose.min_reps}–{e.prescription.dose.max_reps} rép. · repos {e.prescription.dose.rest_seconds} s. Ces valeurs sont les cibles enregistrées.</Text> : null}
    </HistoricalExerciseInstrument>)}
    <CalibrationLink label="Prescription capturée" expanded={prescription} onPress={() => setPrescription(open => !open)} />
  </HistoricalFactsFrame>;
}
