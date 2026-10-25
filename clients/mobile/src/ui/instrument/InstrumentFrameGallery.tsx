import React, { useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, useWindowDimensions, View } from 'react-native';
import { SafeAreaProvider, useSafeAreaInsets } from 'react-native-safe-area-context';

import { CalibrationField } from '../calibration/CalibrationField';
import { CalibrationRail } from '../calibration/CalibrationRail';
import { color, space, type } from '../theme';
import type { FrameVariant } from './frameGeometry';
import { InstrumentFrame } from './InstrumentFrame';

/**
 * DA-02.3 — Instrument Frame exploration bench, mounted only when a build sets
 * EXPO_PUBLIC_GALLERY=frame (the mechanism of CalibrationGallery). Four
 * candidates × three sizes × {empty, readout, rail, BodyMap placeholder}, and a
 * screen where several frames coexist. No product integration; no choice made.
 */
export const SIZES: [number, number][] = [
  [180, 120],
  [320, 180],
  [390, 220],
];
export const VARIANTS: FrameVariant[] = ['recessed', 'indexed', 'rail', 'faceplate'];
const NAMES: Record<FrameVariant, string> = {
  recessed: 'A · Recessed',
  indexed: 'B · Indexed',
  rail: 'C · Rail-mounted',
  faceplate: 'D · Asymmetric faceplate',
};

// demonstration rail: 55–85 kg every 2,5 kg, prescription 70 (no engine value)
const LOW = 52.5;
const HIGH = 87.5;
const pos = (kg: number) => (kg - LOW) / (HIGH - LOW);
const LOADS = Array.from({ length: 13 }, (_, i) => 55 + i * 2.5);
const RAIL = {
  lowBoundary: 0,
  targetLowBoundary: pos(68.75),
  targetHighBoundary: pos(71.25),
  highCostBoundary: pos(78.75),
  steps: LOADS.map(pos),
  stepValues: LOADS,
  referencePosition: pos(70),
  referenceValue: 70,
  selectedPosition: pos(72.5),
  selectedValue: 72.5,
  unit: 'kg',
};

export type Fixture = 'empty' | 'readout' | 'rail' | 'field' | 'bodymap';
export const FIXTURES: Fixture[] = ['empty', 'readout', 'rail', 'field', 'bodymap'];

/**
 * The rail AS the frame's background (operator review of DA-02.3): it measures the
 * space the frame gives it, then fills it. Interactive when given a step setter.
 */
function MeasuredField(props: { step?: number; onStep?: (i: number) => void }) {
  const [box, setBox] = useState<{ w: number; h: number } | null>(null);
  const i = props.step ?? LOADS.indexOf(72.5);
  const steps = RAIL.steps;
  return (
    <View style={{ flex: 1 }} onLayout={(e) => setBox({ w: e.nativeEvent.layout.width, h: e.nativeEvent.layout.height })}>
      {box ? (
        <CalibrationField
          {...RAIL}
          width={box.w}
          height={box.h}
          selectedPosition={steps[i]}
          selectedValue={LOADS[i]}
          onSelectPosition={props.onStep ? (p) => props.onStep?.(steps.indexOf(p)) : undefined}
          onIncrement={props.onStep ? () => props.onStep?.(Math.min(steps.length - 1, i + 1)) : undefined}
          onDecrement={props.onStep ? () => props.onStep?.(Math.max(0, i - 1)) : undefined}
        />
      ) : null}
    </View>
  );
}

/** The three fictitious contents of the brief (+ empty, for the structure alone). */
export function fixtureContent(fixture: Fixture): React.ReactNode {
  switch (fixture) {
    case 'empty':
      return null;
    case 'readout':
      return (
        <View style={styles.center}>
          <Text style={styles.readout} numberOfLines={1} adjustsFontSizeToFit>
            72.5<Text style={styles.unit}> kg</Text>
          </Text>
        </View>
      );
    case 'rail':
      return (
        <View style={styles.center}>
          <CalibrationRail {...RAIL} />
        </View>
      );
    case 'field':
      return <MeasuredField />;
    case 'bodymap':
      return <View style={styles.placeholder} />;
  }
}

export function InstrumentFrameGallery() {
  return (
    <SafeAreaProvider>
      <Bench />
    </SafeAreaProvider>
  );
}

function Bench() {
  const insets = useSafeAreaInsets();
  const { width: screen } = useWindowDimensions();
  // the operator's pick of the exploration (2026-10-25): C — Rail-mounted; the others stay comparable
  const [pick, setPick] = useState<FrameVariant | 'all'>('rail');
  const [step, setStep] = useState(LOADS.indexOf(72.5));
  const shown = pick === 'all' ? VARIANTS : [pick];
  const screenW = Math.min(390, screen - 2 * space.gutter);
  return (
    <ScrollView
      style={{ flex: 1, backgroundColor: color.field }}
      contentContainerStyle={{ paddingTop: insets.top + 12, paddingBottom: insets.bottom + 40, paddingHorizontal: space.gutter }}
    >
      <Text style={type.eyebrow}>DA-02.3 · exploration</Text>
      <Text style={[type.title, { fontSize: 26, marginTop: 4 }]}>Instrument Frame</Text>
      <Text style={[type.small, { marginTop: 4 }]}>
        Quatre familles de structure, u = un index du rail. Choix de l’opérateur : C. Contenus de démonstration.
      </Text>

      <View style={styles.picker}>
        {(['all', ...VARIANTS] as const).map((k, i) => (
          <Pressable
            key={k}
            accessibilityRole="button"
            accessibilityLabel={k === 'all' ? 'Toutes les variantes' : NAMES[k]}
            accessibilityState={{ selected: pick === k }}
            onPress={() => setPick(k)}
            style={[styles.pick, pick === k && styles.pickOn]}
          >
            <Text style={[type.bodyStrong, { fontSize: 15, color: pick === k ? color.ink : color.ink3 }]}>
              {k === 'all' ? 'Tous' : 'ABCD'[i - 1]}
            </Text>
          </Pressable>
        ))}
      </View>

      {shown.map((variant) => (
        <View key={variant} style={{ marginTop: space.xl }}>
          <Text style={[type.bodyStrong, { fontSize: 19 }]}>{NAMES[variant]}</Text>

          <Text style={[type.eyebrow, styles.sub]}>Écran — trois modules ensemble</Text>
          <View style={{ gap: space.s }}>
            <InstrumentFrame variant={variant} width={screenW} height={130}>
              {fixtureContent('readout')}
            </InstrumentFrame>
            {/* the session's focus: the field takes the room (operator: « bien occuper la place ») */}
            <InstrumentFrame variant={variant} width={screenW} height={340}>
              <MeasuredField step={step} onStep={(i) => i >= 0 && setStep(i)} />
            </InstrumentFrame>
            <View style={styles.stepper}>
              <Step label="− 2,5" disabled={step === 0} onPress={() => setStep(step - 1)} />
              <Step label="+ 2,5" disabled={step === LOADS.length - 1} onPress={() => setStep(step + 1)} />
            </View>
            <InstrumentFrame variant={variant} width={screenW} height={220}>
              {fixtureContent('rail')}
            </InstrumentFrame>
            <InstrumentFrame variant={variant} width={screenW} height={200}>
              {fixtureContent('bodymap')}
            </InstrumentFrame>
          </View>

          {SIZES.map(([w, h]) => (
            <View key={`${w}x${h}`}>
              <Text style={[type.eyebrow, styles.sub]}>{`${w} × ${h} — à vide · readout · rail · BodyMap`}</Text>
              <View style={styles.row}>
                {FIXTURES.map((f) => (
                  <InstrumentFrame key={f} variant={variant} width={w} height={h}>
                    {fixtureContent(f)}
                  </InstrumentFrame>
                ))}
              </View>
            </View>
          ))}
        </View>
      ))}
    </ScrollView>
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
  stepper: { flexDirection: 'row', gap: space.m },
  step: {
    flex: 1,
    minHeight: 48,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: color.line,
    backgroundColor: color.plate,
  },
  center: { flex: 1, justifyContent: 'center' },
  readout: { ...type.readout, fontSize: 56, lineHeight: 60 },
  unit: { fontSize: 18, color: color.ink2 },
  placeholder: { flex: 1, borderWidth: 1, borderStyle: 'dashed', borderColor: color.line },
  picker: { flexDirection: 'row', gap: space.s, marginTop: space.m },
  pick: {
    minWidth: 48,
    minHeight: 44,
    paddingHorizontal: 12,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: color.line,
    backgroundColor: color.plate,
  },
  pickOn: { borderColor: color.ink2 },
  sub: { marginTop: space.m, marginBottom: space.s },
  row: { flexDirection: 'row', flexWrap: 'wrap', gap: space.m, alignItems: 'flex-start' },
});
