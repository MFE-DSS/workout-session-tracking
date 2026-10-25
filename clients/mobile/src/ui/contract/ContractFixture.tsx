import React from 'react';
import { Text, View } from 'react-native';

import { CalibrationRail } from '../calibration/CalibrationRail';
import { HorizontalInstrumentSurface } from '../instrument/HorizontalInstrumentSurface';
import { InstrumentFrame } from '../instrument/InstrumentFrame';
import { InstrumentWithStepControls } from '../instrument/InstrumentWithStepControls';
import { RecessedWindowFixture } from '../instrument/RecessedWindowFixture';
import { color, type } from '../theme';
import { candidateById } from './candidates';
import { CALIBRATION_LINE_DEMO, type ContractFixture, fixtureById, selectedPositionOf } from './fixtures';

/** Fixed frame around the component: the same in every baseline. */
const PAD = 12;
/** A still fixture's controls look enabled (they would be in the product); a press does nothing here. */
const NOOP = () => undefined;

function Governed({ f }: { f: ContractFixture }) {
  if (f.contract === 'FRAME-C-V1') return <InstrumentFrame variant="rail" width={f.width} height={f.height} />;
  if (f.contract === 'RECESSED-WINDOW-V1') return <RecessedWindowFixture width={f.width} height={f.height} fixture={f.fixture} />;
  if (f.contract === 'INSTRUMENT-CONTROLS-B3') {
    return (
      <InstrumentWithStepControls
        {...CALIBRATION_LINE_DEMO}
        width={f.width}
        height={f.height}
        selectedPosition={selectedPositionOf(f)}
        selectedValue={f.selectedValue}
        presentation={f.presentation}
        onSelectPosition={NOOP}
      />
    );
  }
  if (f.contract === 'INSTRUMENT-SURFACE-B1' || f.contract === 'INSTRUMENT-SURFACE-B2') {
    return (
      <HorizontalInstrumentSurface
        {...CALIBRATION_LINE_DEMO}
        width={f.width}
        height={f.height}
        selectedPosition={selectedPositionOf(f)}
        selectedValue={f.selectedValue}
        presentation={f.contract === 'INSTRUMENT-SURFACE-B2' ? 'rest' : 'adjusting'}
      />
    );
  }
  return (
    <CalibrationRail
      {...CALIBRATION_LINE_DEMO}
      width={f.width}
      selectedPosition={selectedPositionOf(f)}
      selectedValue={f.selectedValue}
    />
  );
}

/**
 * DA-GOV-01 — renders ONE governed fixture, chosen by `?fixture=<id>`, on the
 * field, at its exact width, nothing else on the page: what the visual gate
 * screenshots. Mounted only by a build with EXPO_PUBLIC_GALLERY=contract.
 *
 * DA-02.4B.1 — the same page renders a review CANDIDATE (candidates.ts) under its
 * own testID: captured for the operator, never compared by the gate.
 */
export function ContractFixtureScreen() {
  const search = (globalThis as { location?: { search?: string } }).location?.search ?? '';
  const id = new URLSearchParams(search).get('fixture');
  const f = fixtureById(id);
  const candidate = f ? undefined : candidateById(id);
  if (candidate) {
    return (
      <View style={{ flex: 1, backgroundColor: color.field, alignItems: 'flex-start' }}>
        <View testID="contract-candidate" style={{ padding: PAD, backgroundColor: color.field }}>
          <RecessedWindowFixture width={candidate.width} height={candidate.height} fixture={candidate.fixture} />
        </View>
      </View>
    );
  }
  if (!f) {
    return (
      <View testID="contract-unknown" style={{ flex: 1, backgroundColor: color.field, padding: PAD }}>
        <Text style={type.small}>{`Fixture inconnue : ${id ?? '(aucune)'}`}</Text>
      </View>
    );
  }
  return (
    <View style={{ flex: 1, backgroundColor: color.field, alignItems: 'flex-start' }}>
      <View testID="contract-fixture" style={{ padding: PAD, backgroundColor: color.field }}>
        <Governed f={f} />
      </View>
    </View>
  );
}
