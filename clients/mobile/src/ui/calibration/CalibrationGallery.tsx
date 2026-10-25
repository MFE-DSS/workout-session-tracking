import React, { useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaProvider, useSafeAreaInsets } from 'react-native-safe-area-context';

import { color, space, type } from '../theme';
import { ActiveCursor } from './ActiveCursor';
import { CalibrationRail } from './CalibrationRail';
import type { Boundaries } from './layout';
import { ReferenceMarker } from './ReferenceMarker';

/**
 * DA-02.2 — the visual acceptance bench (`AUREN_CALIBRATION_SYSTEM §12`), mounted
 * only when a build sets EXPO_PUBLIC_GALLERY=calibration. Every value here is a
 * DEMONSTRATION input: no engine produces calibration yet (`VNEXT §8.11`).
 */
/** A demonstration scale only — the engine's own normalization does not exist yet. */
const LOW_KG = 52.5;
const HIGH_KG = 87.5;
const pos = (kg: number) => (kg - LOW_KG) / (HIGH_KG - LOW_KG);
const B: Boundaries = {
  lowBoundary: 0,
  targetLowBoundary: pos(68.75),
  targetHighBoundary: pos(71.25),
  highCostBoundary: pos(78.75),
};
const REF = { position: pos(70), value: 70 };
/** the selectable loads: one rail index each, every 2,5 kg */
const LOADS = Array.from({ length: 13 }, (_, i) => 55 + i * 2.5);
const STEPS = LOADS.map(pos);
const SCENARIOS = [
  { name: 'EXACT TARGET', value: 70 },
  { name: 'EASY', value: 62.5 },
  { name: 'PUSH', value: 75 },
  { name: 'HIGH COST', value: 82.5 },
];
const WIDTHS = [180, 320, 390];

export function CalibrationGallery() {
  return (
    <SafeAreaProvider>
      <Bench />
    </SafeAreaProvider>
  );
}

function Bench() {
  const insets = useSafeAreaInsets();
  const [step, setStep] = useState(LOADS.indexOf(70));
  const last = LOADS.length - 1;
  const toStep = (p: number) => {
    const i = STEPS.indexOf(p);
    if (i >= 0) setStep(i);
  };
  return (
    <ScrollView
      style={{ flex: 1, backgroundColor: color.field }}
      contentContainerStyle={{ paddingTop: insets.top + 12, paddingBottom: insets.bottom + 40, paddingHorizontal: space.gutter }}
    >
      <Text style={type.eyebrow}>DA-02.2 · banc d’acceptation</Text>
      <Text style={[type.title, { fontSize: 26, marginTop: 4 }]}>Calibration System</Text>
      <Text style={[type.small, { marginTop: 4 }]}>Valeurs de démonstration : aucune ne vient du moteur.</Text>

      <Section title="Marqueurs · token · monochrome · compact">
        <View style={styles.markers}>
          <Pair label="tokens" a={color.system} b={color.signal} size={10} />
          <Pair label="monochrome" a={color.ink} b={color.ink} size={10} />
          <Pair label="compact (u = 2)" a={color.system} b={color.signal} size={2} />
        </View>
      </Section>

      <Section title="Curseur — glisser ou ± 2,5">
        <CalibrationRail
          {...B}
          steps={STEPS}
          stepValues={LOADS}
          referencePosition={REF.position}
          selectedPosition={STEPS[step]}
          referenceValue={REF.value}
          selectedValue={LOADS[step]}
          unit="kg"
          onSelectPosition={toStep}
          onIncrement={() => setStep(Math.min(last, step + 1))}
          onDecrement={() => setStep(Math.max(0, step - 1))}
        />
        <View style={styles.stepper}>
          <Step label="− 2,5" disabled={step === 0} onPress={() => setStep(step - 1)} />
          <Step label="+ 2,5" disabled={step === last} onPress={() => setStep(step + 1)} />
        </View>
      </Section>

      {SCENARIOS.map((sc) => (
        <Section key={sc.name} title={sc.name}>
          {WIDTHS.map((w) => (
            <View key={w} style={{ marginTop: space.s }}>
              <Text style={styles.width}>{w} px</Text>
              <View style={styles.frame}>
                <CalibrationRail
                  {...B}
                  width={w}
                  steps={STEPS}
                  stepValues={LOADS}
                  referencePosition={REF.position}
                  selectedPosition={pos(sc.value)}
                  referenceValue={REF.value}
                  selectedValue={sc.value}
                  unit="kg"
                />
              </View>
            </View>
          ))}
        </Section>
      ))}
    </ScrollView>
  );
}

function Section(props: { title: string; children: React.ReactNode }) {
  return (
    <View style={{ marginTop: space.l }}>
      <Text style={type.eyebrow}>{props.title}</Text>
      <View style={{ marginTop: space.s }}>{props.children}</View>
    </View>
  );
}

function Pair(props: { label: string; a: string; b: string; size: number }) {
  return (
    <View style={{ alignItems: 'center' }}>
      <View style={{ flexDirection: 'row', alignItems: 'flex-end', gap: props.size * 2 }}>
        <ReferenceMarker size={props.size} color={props.a} />
        <ActiveCursor size={props.size} color={props.b} />
      </View>
      <Text style={[styles.width, { marginTop: 6 }]}>{props.label}</Text>
    </View>
  );
}

function Step(props: { label: string; disabled: boolean; onPress: () => void }) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={props.label}
      disabled={props.disabled}
      onPress={props.onPress}
      style={[styles.step, props.disabled && { opacity: 0.35 }]}
    >
      <Text style={[type.bodyStrong, type.tabular]}>{props.label}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  markers: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-end' },
  width: { ...type.small, fontSize: 11 },
  frame: { alignSelf: 'flex-start', borderWidth: StyleSheet.hairlineWidth, borderColor: color.line, paddingVertical: 6 },
  stepper: { flexDirection: 'row', gap: space.m, marginTop: space.m },
  step: {
    flex: 1,
    minHeight: 48,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 14,
    borderWidth: 1,
    borderColor: color.line,
    backgroundColor: color.plate,
  },
});
