import React from 'react';
import { View } from 'react-native';
import { AurenMark } from './brand/AurenMark';
import { color } from './theme';

/** D-MOB02-2 : dessin primaire déjà verrouillé, seul, sans texte ni animation. */
export function BootScreen() {
  return (
    <View accessible accessibilityLabel="AUREN" style={{ flex: 1, backgroundColor: color.field, alignItems: 'center', justifyContent: 'center' }}>
      <AurenMark size={64} color={color.ink} />
    </View>
  );
}
