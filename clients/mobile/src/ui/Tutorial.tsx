import React, { useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { feedback } from '../native/feedback';
import { PrimaryAction } from './components';
import { color, space, type } from './theme';

type Where = 'top' | 'middle' | 'bottom' | 'corner';

const STEPS: { where: Where; title: string; text: string }[] = [
  { where: 'top', title: 'En haut — où tu en es', text: 'L’exercice, la série en cours, et la barre de la séance.' },
  { where: 'middle', title: 'Au centre — ta série', text: '+ et − pour ajuster la charge et les reps ; touche le chiffre pour le saisir. Première fois sur un exercice : saisis la charge que tu prends.' },
  { where: 'bottom', title: 'En bas — une seule action', text: 'Valide la série. Le repos démarre tout seul, puis la suite s’enchaîne.' },
  { where: 'corner', title: 'À droite, ⋯ — les options', text: 'Machine prise ? Remplace l’exercice ici. Rien d’autre ne t’interrompt.' },
];

/**
 * D13 — the short tutorial, ON the first set, so each line points at the real
 * thing. Four steps, skippable, shown once.
 */
export function Tutorial(props: { onDone: () => void }) {
  const insets = useSafeAreaInsets();
  const [i, setI] = useState(0);
  const step = STEPS[i];
  const last = i === STEPS.length - 1;
  const next = () => {
    feedback.step();
    if (last) props.onDone();
    else setI(i + 1);
  };
  const place = {
    top: { top: insets.top + 120 },
    middle: { top: insets.top + 96 },
    bottom: { bottom: insets.bottom + 110 },
    corner: { top: insets.top + 72 },
  }[step.where];

  return (
    <View style={styles.veil} accessibilityViewIsModal>
      <Pointer where={step.where} insetTop={insets.top} insetBottom={insets.bottom} />
      <View style={[styles.card, place]} accessibilityLiveRegion="polite">
        <Text style={[type.eyebrow, { color: color.signal }]}>{`Guide · ${i + 1} / ${STEPS.length}`}</Text>
        <Text style={[type.bodyStrong, { fontSize: 20, marginTop: 6 }]} accessibilityRole="header">{step.title}</Text>
        <Text style={[type.body, { marginTop: 6 }]}>{step.text}</Text>
        <View style={{ height: space.m }} />
        <PrimaryAction label={last ? 'Compris, on y va' : 'Suivant'} onPress={next} />
        {!last ? (
          <Pressable accessibilityRole="button" accessibilityLabel="Passer le guide" onPress={props.onDone} style={styles.skip}>
            <Text style={[type.small, { color: color.ink2 }]}>Passer le guide</Text>
          </Pressable>
        ) : null}
      </View>
    </View>
  );
}

/** A frame around the zone the step talks about — position only, never a state carrier. */
function Pointer(props: { where: Where; insetTop: number; insetBottom: number }) {
  const frame = {
    top: { top: props.insetTop + 8, left: 12, right: 12, height: 104 },
    middle: { bottom: props.insetBottom + 92, left: 12, right: 12, height: 200 },
    bottom: { bottom: props.insetBottom + 6, left: 12, right: 12, height: 80 },
    corner: { top: props.insetTop + 12, right: 12, width: 60, height: 60 },
  }[props.where];
  return <View pointerEvents="none" style={[styles.pointer, frame]} />;
}

const styles = StyleSheet.create({
  veil: { position: 'absolute', top: 0, right: 0, bottom: 0, left: 0, backgroundColor: 'rgba(5,6,8,0.78)' },
  card: { position: 'absolute', left: space.gutter, right: space.gutter, backgroundColor: color.plate, borderRadius: 24, borderWidth: 1, borderColor: color.signal, padding: 18 },
  pointer: { position: 'absolute', borderRadius: 22, borderWidth: 2, borderColor: color.signal, borderStyle: 'dashed' },
  skip: { alignItems: 'center', paddingVertical: 12, minHeight: 44 },
});
