import React from 'react';
import { Text, View } from 'react-native';
import type { WorkoutState } from '../domain/workout';
import type { ServerSetState } from '../sync/serverState';
import { Sheet, SheetRow } from './components';
import { space, type } from './theme';

const LABEL: Record<ServerSetState, string> = {
  synced: 'Reçue par AUREN',
  pending: 'En attente d’envoi ou de confirmation',
  refused: 'À vérifier — refusée par AUREN',
  unknown: 'État serveur inconnu',
};

/** Presentation only: the connected caller owns the canonical persisted delivery state. */
export function SessionSetDetails(props: {
  visible: boolean;
  state: WorkoutState;
  serverStateOf?: (setId: number) => ServerSetState;
  onClose: () => void;
  onOpenJournal: () => void;
}) {
  const plan = props.state.plan;
  return <Sheet visible={props.visible} title="Séries de la séance" onClose={props.onClose}>
    {plan?.exercises.map((exercise) => {
      const sets = plan.sets.filter((set) => set.se_id === exercise.se_id && props.state.done[set.set_id]);
      if (!sets.length) return null;
      return <View key={exercise.se_id} style={{ marginBottom: space.m }}>
        <Text style={type.bodyStrong} accessibilityRole="header">{exercise.executed_name}</Text>
        {sets.map((set) => <SheetRow key={set.set_id} title={`Série ${set.index}`}
          detail={LABEL[props.serverStateOf?.(set.set_id) ?? 'unknown']} />)}
      </View>;
    })}
    {!Object.keys(props.state.done).length ? <Text style={type.small}>Aucune série réalisée dans cette séance.</Text> : null}
    <SheetRow title="Journal local" onPress={props.onOpenJournal} />
  </Sheet>;
}
