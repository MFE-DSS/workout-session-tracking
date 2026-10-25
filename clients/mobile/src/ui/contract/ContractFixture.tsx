import React from 'react';
import { Text, View } from 'react-native';

import { CalibrationRail } from '../calibration/CalibrationRail';
import { color, type } from '../theme';
import { CALIBRATION_LINE_DEMO, fixtureById, selectedPositionOf } from './fixtures';

/** Fixed frame around the component: the same in every baseline. */
const PAD = 12;

/**
 * DA-GOV-01 — renders ONE governed fixture, chosen by `?fixture=<id>`, on the
 * field, at its exact width, nothing else on the page: what the visual gate
 * screenshots. Mounted only by a build with EXPO_PUBLIC_GALLERY=contract.
 */
export function ContractFixtureScreen() {
  const search = (globalThis as { location?: { search?: string } }).location?.search ?? '';
  const id = new URLSearchParams(search).get('fixture');
  const f = fixtureById(id);
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
        <CalibrationRail
          {...CALIBRATION_LINE_DEMO}
          width={f.width}
          selectedPosition={selectedPositionOf(f)}
          selectedValue={f.selectedValue}
        />
      </View>
    </View>
  );
}
