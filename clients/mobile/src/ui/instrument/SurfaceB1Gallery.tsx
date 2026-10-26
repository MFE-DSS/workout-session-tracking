import React, { useState } from 'react';
import { ScrollView, Text, useWindowDimensions, View } from 'react-native';
import { SafeAreaProvider, useSafeAreaInsets } from 'react-native-safe-area-context';

import { CALIBRATION_LINE_DEMO, SURFACE_B1_FIXTURES, SURFACE_B2_FIXTURES } from '../contract/fixtures';
import { color, space, type } from '../theme';
import { useDisclosure } from './disclosure';
import { HorizontalInstrumentSurface } from './HorizontalInstrumentSurface';
import { InstrumentWithStepControls } from './InstrumentWithStepControls';

/**
 * DA-02.4B.1 — the device bench (EXPO_PUBLIC_GALLERY=surface-b1): the composed surface
 * judged on the phone, not only in the gate's browser. One surface the operator drags,
 * at the screen's width, then the six governed B.1 fixtures at their own sizes. Demonstration
 * values: the DA-02.2 bench's (`CALIBRATION_LINE_DEMO`), nothing from the engine.
 */
export function SurfaceB1Gallery() {
  return (
    <SafeAreaProvider>
      <Bench />
    </SafeAreaProvider>
  );
}

const LOADS = CALIBRATION_LINE_DEMO.stepValues;
const STEPS = CALIBRATION_LINE_DEMO.steps;

function Bench() {
  const insets = useSafeAreaInsets();
  const { width: screen } = useWindowDimensions();
  const [step, setStep] = useState(LOADS.indexOf(75));
  const { presentation, wake } = useDisclosure();
  const last = LOADS.length - 1;
  // the governed module sizes (DA-02.7 R2: 390 × 290, 320 × 210)
  const live = { width: Math.min(390, screen), height: screen >= 360 ? 290 : 210 };
  return (
    <ScrollView
      style={{ flex: 1, backgroundColor: color.field }}
      contentContainerStyle={{ paddingTop: insets.top + 12, paddingBottom: insets.bottom + 40, gap: 28 }}
    >
      <View style={{ paddingHorizontal: space.gutter }}>
        <Text style={type.eyebrow}>DA-02.4B · banc appareil</Text>
        <Text style={[type.small, { marginTop: 4 }]}>Valeurs de démonstration : aucune ne vient du moteur.</Text>
      </View>

      <Block label={`Glisser ou − / + · ${live.width} × ${live.height}`}>
        <InstrumentWithStepControls
          {...CALIBRATION_LINE_DEMO}
          width={live.width}
          height={live.height}
          selectedPosition={STEPS[step]}
          selectedValue={LOADS[step]}
          presentation={presentation}
          onSelectPosition={(p) => {
            wake();
            const i = STEPS.indexOf(p);
            if (i >= 0) setStep(i);
          }}
          onIncrement={() => {
            wake();
            setStep(Math.min(last, step + 1));
          }}
          onDecrement={() => {
            wake();
            setStep(Math.max(0, step - 1));
          }}
        />
      </Block>

      {[...SURFACE_B2_FIXTURES, ...SURFACE_B1_FIXTURES].map((f) => (
        <Block key={f.id} label={f.id}>
          <HorizontalInstrumentSurface
            {...CALIBRATION_LINE_DEMO}
            width={Math.min(f.width, screen)}
            height={f.height}
            selectedPosition={STEPS[LOADS.indexOf(f.selectedValue)]}
            selectedValue={f.selectedValue}
            presentation={f.contract === 'INSTRUMENT-SURFACE-B2' ? 'rest' : 'adjusting'}
          />
        </Block>
      ))}
    </ScrollView>
  );
}

function Block({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <View style={{ gap: 8, alignItems: 'center' }}>
      <Text style={[type.eyebrow, { alignSelf: 'flex-start', paddingHorizontal: space.gutter }]}>{label}</Text>
      {children}
    </View>
  );
}
