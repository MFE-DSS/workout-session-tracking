import React from 'react';
import { View } from 'react-native';

import { HorizontalInstrumentSurface, type HorizontalInstrumentSurfaceProps } from './HorizontalInstrumentSurface';
import { StepControls } from './StepControls';

/**
 * DA-02.4B.3 — EXPLORATION. The locked surface (`INSTRUMENT-SURFACE-B1` / `-B2`),
 * untouched, with the − / + controls under its frame: the rail keeps its full width
 * and nothing is placed beside it.
 */
export function InstrumentWithStepControls(p: HorizontalInstrumentSurfaceProps) {
  return (
    <View testID={p.testID} style={{ width: p.width }}>
      <HorizontalInstrumentSurface {...p} testID={undefined} />
      <StepControls
        width={p.width}
        steps={p.steps}
        stepValues={p.stepValues}
        selectedPosition={p.selectedPosition}
        unit={p.unit}
        onSelectPosition={p.onSelectPosition}
      />
    </View>
  );
}
