import React from 'react';
import { ScrollView, Text, View } from 'react-native';
import { SafeAreaProvider, useSafeAreaInsets } from 'react-native-safe-area-context';

import { color, space, type } from '../theme';
import { RecessedWindowFixture, type WindowFixture } from './RecessedWindowFixture';

/**
 * DA-02.5 — the isolated Recessed Window bench (EXPO_PUBLIC_GALLERY=recessed-window):
 * `RECESSED-WINDOW-V1` × F1 / F2 / F3 (pair, 60/40) × 390 / 320, monochrome, in an
 * unchanged Frame C. Demonstration content only; no product screen mounts a window yet.
 */
const FIXTURES: { id: WindowFixture; name: string }[] = [
  { id: 'f1', name: 'F1 · texte / chiffre' },
  { id: 'f2', name: 'F2 · BodyMap (gabarit)' },
  { id: 'f3-pair', name: 'F3 · deux fenêtres égales' },
  { id: 'f3-split', name: 'F3 · deux fenêtres 60 / 40' },
];
const SIZES: [number, number][] = [
  [390, 220],
  [320, 180],
];

export function RecessedWindowGallery() {
  return (
    <SafeAreaProvider>
      <Bench />
    </SafeAreaProvider>
  );
}

function Bench() {
  const insets = useSafeAreaInsets();
  return (
    <ScrollView
      style={{ flex: 1, backgroundColor: color.field }}
      contentContainerStyle={{ paddingTop: insets.top + 12, paddingBottom: insets.bottom + 40, gap: 28 }}
    >
      <View style={{ paddingHorizontal: space.gutter }}>
        <Text style={type.eyebrow}>DA-02.5 · Recessed Window · V1</Text>
        <Text style={[type.small, { marginTop: 4 }]}>Contenus de démonstration. Aucun écran produit.</Text>
      </View>
      {SIZES.flatMap(([w, h]) =>
        FIXTURES.map((f) => (
          <View key={`${w}-${f.id}`} style={{ gap: 8, alignItems: 'center' }}>
            <Text style={[type.eyebrow, { alignSelf: 'flex-start', paddingHorizontal: space.gutter }]}>{`${f.name} · ${w} × ${h}`}</Text>
            <RecessedWindowFixture width={w} height={h} fixture={f.id} />
          </View>
        )),
      )}
    </ScrollView>
  );
}
