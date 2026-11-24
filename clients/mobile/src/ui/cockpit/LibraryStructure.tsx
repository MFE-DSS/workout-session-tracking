import React, { useMemo, useState } from 'react';
import { Pressable, Text, View, useWindowDimensions } from 'react-native';
import type { LibraryComposition, LibraryEntry, LibraryExercise } from '../../api/library';
import { CalibrationLink } from '../plan/calibrationControls';
import { color, type } from '../theme';

const MARK_LIMIT = 8;
const ROW_BATCH = 8;
const unitCount = (count: number, singular: string, plural: string) =>
  `${count} ${count === 1 ? singular : plural}`;

export function LibraryCountStructure({ entry }: { entry: LibraryEntry }) {
  const counts = entry.counts;
  const metrics = [
    { value: entry.kind === 'OWNED_PROGRAM' ? counts.sessions : null, singular: 'séance', plural: 'séances', marks: true },
    { value: counts.exercise_slots, singular: 'exercice', plural: 'exercices', marks: true },
    { value: counts.prescribed_sets, singular: 'série prévue', plural: 'séries prévues', marks: false },
  ].filter((metric): metric is typeof metric & { value: number } => metric.value !== null);
  const status = counts.count_state === 'KNOWN'
    ? null
    : counts.count_state === 'PARTIAL' ? 'Composition partielle' : 'Composition inconnue';
  const label = [...metrics.map(metric => unitCount(metric.value, metric.singular, metric.plural)), status]
    .filter(Boolean).join(' · ');
  return (
    <View testID={`library-structure-${entry.source_ref}`} accessible accessibilityLabel={label} style={{ gap: 6 }}>
      <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 12 }}>
        {metrics.map(({ value, singular, plural, marks }) => (
          <View key={plural} testID={marks ? 'library-exercise-count' : undefined} style={{ gap: 4, maxWidth: '100%' }}>
            <Text style={type.small}>
              <Text style={[type.bodyStrong, { fontVariant: ['tabular-nums'] }]}>{value}</Text> {value === 1 ? singular : plural}
            </Text>
            {marks && value > 0 ? (
              <View
                importantForAccessibility="no-hide-descendants"
                accessibilityElementsHidden
                style={{ flexDirection: 'row', alignItems: 'center', flexWrap: 'wrap', gap: 4 }}
              >
                {Array.from({ length: Math.min(value, MARK_LIMIT) }, (_, i) => (
                  <View key={i} testID={plural === 'exercices' ? 'library-slot-mark' : 'library-session-count-mark'} style={{ width: plural === 'séances' ? 28 : 12, height: 12, borderLeftWidth: 2, borderColor: color.ink3, backgroundColor: color.plate }} />
                ))}
                {value > MARK_LIMIT ? <Text style={type.small}>+{value - MARK_LIMIT}</Text> : null}
              </View>
            ) : null}
          </View>
        ))}
      </View>
      {status ? <Text style={type.small}>{status}</Text> : null}
    </View>
  );
}

export function LibraryProgramSequence({
  sessions, prescriptionPartial, disabled, onSelect,
}: { sessions: LibraryComposition[]; prescriptionPartial: boolean; disabled: boolean; onSelect: (ref: string) => void }) {
  const [shown, setShown] = useState(ROW_BATCH);
  const remaining = sessions.length - shown;
  return (
    <View testID="library-sequence">
      {sessions.length === 0 ? (
        <Text style={type.small}>{prescriptionPartial ? 'Aucune séance reçue pour ce programme.' : 'Aucune séance dans ce programme.'}</Text>
      ) : null}
      {sessions.slice(0, shown).map((session, i) => {
        const targets = session.exercises.flatMap(exercise => exercise.rep_targets);
        const work = targets.filter(target => !target.is_warmup).length;
        const warmups = targets.length - work;
        const quantities = [
          work > 0 ? unitCount(work,
            prescriptionPartial ? 'série reçue' : 'série prévue',
            prescriptionPartial ? 'séries reçues' : 'séries prévues') : null,
          warmups > 0 ? unitCount(warmups,
            prescriptionPartial ? 'préparation reçue' : 'préparation',
            prescriptionPartial ? 'préparations reçues' : 'préparations') : null,
        ].filter(Boolean);
        const summary = quantities.join(' · ') ||
          (prescriptionPartial ? 'Aucune prescription reçue' : 'Prescription non renseignée');
        const ordered = [...session.exercises].sort((a, b) => a.position - b.position);
        const groups = ordered.slice(0, ROW_BATCH).map((exercise, position) => {
          const units = exercise.rep_targets.slice(0, MARK_LIMIT);
          const remaining = exercise.rep_targets.length - units.length;
          const label = `${position + 1}. ${exercise.name} · ${units.map(target =>
            `${target.is_warmup ? 'préparation' : 'série'} ${target.set_index} : ${target.min_reps === target.max_reps ? target.min_reps : `${target.min_reps}–${target.max_reps}`} rép.`).join(' ; ') || 'Prescription non renseignée'}${remaining > 0 ? ` ; ${unitCount(remaining, 'autre unité reçue', 'autres unités reçues')}` : ''}`;
          return { exercise, units, remaining, label };
        });
        const otherExercises = ordered.length - groups.length;
        const spokenGroups = groups.map(g => g.label).join(' / ');
        return (
          <Pressable
            key={session.source_ref}
            testID={`library-session-${session.source_ref}`}
            accessibilityRole="button"
            accessibilityLabel={`${i + 1}. ${session.name} · ${summary}${spokenGroups ? ` · ${spokenGroups}` : ''}${otherExercises > 0 ? ` · ${unitCount(otherExercises, 'autre exercice reçu', 'autres exercices reçus')}` : ''}`}
            accessibilityState={{ disabled }}
            disabled={disabled}
            onPress={() => onSelect(session.source_ref)}
            style={({ pressed }) => ({
              minHeight: 48, minWidth: 48,
              paddingVertical: 12, gap: 12, alignItems: 'stretch', flexDirection: 'row',
              opacity: disabled ? 0.4 : pressed ? 0.65 : 1,
            })}
          >
            <View importantForAccessibility="no-hide-descendants" style={{ width: 40, alignItems: 'center' }}>
              <View style={{ width: 40, minHeight: 40, alignItems: 'center', justifyContent: 'center' }}>
                <Text style={[type.bodyStrong, type.tabular]}>{String(i + 1).padStart(2, '0')}</Text>
              </View>
              {i + 1 < sessions.length ? <View style={{ width: 1, flex: 1, minHeight: 16, backgroundColor: color.line }} /> : null}
            </View>
            <View style={{ flex: 1, minWidth: 0, gap: 8, paddingVertical: 4, paddingRight: 4 }}>
              <Text style={type.bodyStrong}>{session.name}</Text>
              <Text style={type.small}>{summary}</Text>
              <View importantForAccessibility="no-hide-descendants" style={{ gap: 10 }}>
                {groups.map(({ exercise, units, remaining, label }) => (
                  <View key={exercise.id} testID={`library-sequence-exercise-${session.source_ref}/${exercise.id}`}
                    accessibilityLabel={label}
                    style={{ gap: 4 }}>
                    <Text style={type.small}>{exercise.name}</Text>
                    <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 4 }}>
                      {units.map((target, j) => <View key={`${target.set_index}/${target.is_warmup}`}
                        testID={`library-sequence-unit-${session.source_ref}/${exercise.id}/${j}`}
                        style={{ borderBottomWidth: target.is_warmup ? 1 : 3, borderColor: color.ink3, paddingHorizontal: 6, paddingBottom: 4 }}>
                        <Text style={[type.small, type.tabular]}>{target.is_warmup ? 'P · ' : ''}{target.min_reps === target.max_reps ? target.min_reps : `${target.min_reps}–${target.max_reps}`}</Text>
                      </View>)}
                      {remaining > 0 ? <Text style={type.small}>+{remaining} unités</Text> : null}
                      {units.length ? <Text style={type.small}>rép.</Text> : null}
                    </View>
                  </View>
                ))}
                {otherExercises > 0 ? <Text style={type.small}>+{otherExercises} exercices · Examiner</Text> : null}
              </View>
              <Text style={[type.small, { color: disabled ? color.ink3 : color.signal }]}>Examiner →</Text>
            </View>
          </Pressable>
        );
      })}
      {remaining > 0 ? (
        <CalibrationLink
          testID="library-more-sessions"
          label={`Afficher la suite · ${unitCount(remaining, 'séance restante', 'séances restantes')}`}
          onPress={() => setShown(shown + ROW_BATCH)}
        />
      ) : null}
    </View>
  );
}

export function LibraryTechniqueSources({ exercises }: { exercises: LibraryExercise[] }) {
  const [start, setStart] = useState(0);
  const sources = useMemo(() => exercises.flatMap(exercise =>
    exercise.rep_targets.filter(target => target.technique).map(target => ({ exercise, target }))), [exercises]);
  if (sources.length === 0) return null;

  const lastStart = Math.floor((sources.length - 1) / ROW_BATCH) * ROW_BATCH;
  const nextStart = start + ROW_BATCH;
  const remaining = Math.max(0, sources.length - nextStart);
  return (
    <>
      {sources.slice(start, nextStart).map(({ exercise, target }) => (
        <Text selectable key={`${exercise.id}/${target.set_index}/${target.is_warmup}`} style={type.small}>
          {exercise.name} · {target.is_warmup ? 'préparation' : 'série'} {target.set_index} · méthode déclarée : {target.technique}
        </Text>
      ))}
      {start > ROW_BATCH ? (
        <CalibrationLink testID="library-first-techniques" label="Premières méthodes" onPress={() => setStart(0)} />
      ) : null}
      {start > 0 ? (
        <CalibrationLink
          testID="library-previous-techniques"
          label="Méthodes précédentes"
          onPress={() => setStart(start - ROW_BATCH)}
        />
      ) : null}
      {remaining > 0 ? (
        <CalibrationLink
          testID="library-more-techniques"
          label={`Afficher la suite · ${unitCount(remaining, 'méthode restante', 'méthodes restantes')}`}
          onPress={() => setStart(nextStart)}
        />
      ) : null}
      {nextStart < lastStart ? (
        <CalibrationLink testID="library-last-techniques" label="Dernières méthodes" onPress={() => setStart(lastStart)} />
      ) : null}
    </>
  );
}

function ExercisePrescription({ exercise, large }: { exercise: LibraryExercise; large: boolean }) {
  const [shown, setShown] = useState(ROW_BATCH);
  const remaining = exercise.rep_targets.slice(shown);
  const work = remaining.filter(target => !target.is_warmup).length;
  const warmups = remaining.length - work;
  const counts = [
    work > 0 ? unitCount(work, 'série restante', 'séries restantes') : null,
    warmups > 0 ? unitCount(warmups, 'préparation restante', 'préparations restantes') : null,
  ].filter(Boolean).join(' · ');
  return (
    <View style={{ gap: 8, paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: color.line }}>
      <Text selectable accessibilityRole="header" style={type.bodyStrong}>{exercise.name}</Text>
      {exercise.rep_targets.length === 0 ? <Text style={type.small}>Prescription non renseignée</Text> : null}
      <View style={{ flexDirection: large ? 'column' : 'row', flexWrap: 'wrap', gap: 8 }}>
      {exercise.rep_targets.slice(0, shown).map(target => {
        const key = `${target.set_index}/${target.is_warmup}`;
        const name = `${target.is_warmup ? 'Préparation' : 'Série'} ${target.set_index}`;
        const reps = target.min_reps === target.max_reps ? target.min_reps : `${target.min_reps}–${target.max_reps}`;
        const prescription = `${reps} rép. prévues`;
        return (
          <View
            key={key}
            testID={`library-prescription-unit-${exercise.id}/${key}`}
            accessible
            accessibilityLabel={`${name} · ${prescription}`}
            style={{
              flexDirection: 'column', alignItems: 'flex-start', maxWidth: '100%',
              borderBottomWidth: target.is_warmup ? 1 : 3, borderBottomColor: color.ink3, paddingVertical: 8, paddingHorizontal: 6, gap: 4,
            }}
          >
            <Text style={type.eyebrow}>{name}</Text>
            <Text selectable style={type.bodyStrong}>{prescription}</Text>
          </View>
        );
      })}
      </View>
      {remaining.length > 0 ? (
        <CalibrationLink
          testID={`library-more-sets-${exercise.id}`}
          label={`Afficher la suite · ${counts}`}
          onPress={() => setShown(shown + ROW_BATCH)}
        />
      ) : null}
    </View>
  );
}

export function LibraryPrescription({ exercises }: { exercises: LibraryExercise[] }) {
  const [shown, setShown] = useState(ROW_BATCH);
  const large = useWindowDimensions().fontScale >= 1.25;
  const remaining = exercises.length - shown;
  const ordered = [...exercises].sort((a, b) => a.position - b.position);
  return (
    <View>
      {ordered.length === 0 ? <Text style={type.small}>Prescription non renseignée</Text> : null}
      {ordered.slice(0, shown).map(exercise => (
        <ExercisePrescription key={exercise.id} exercise={exercise} large={large} />
      ))}
      {remaining > 0 ? (
        <CalibrationLink
          testID="library-more-exercises"
          label={`Afficher la suite · ${unitCount(remaining, 'exercice restant', 'exercices restants')}`}
          onPress={() => setShown(shown + ROW_BATCH)}
        />
      ) : null}
    </View>
  );
}
