import React from 'react';
import Svg, { Path } from 'react-native-svg';

import { color as tokens } from '../theme';
import { polygonPath, REFERENCE_MARKER } from './geometry';

export type CalibrationMarkerProps = {
  /** the grid unit `u` in px (the marker is 5u × 3u) */
  size?: number;
  /** a theme token; defaults to `system` — the engine's voice */
  color?: string;
  testID?: string;
};

/**
 * The prescription AUREN computed — set by the instrument, fixed while the user
 * adjusts. Lower and wider than the ActiveCursor; same slot, same walls, same axis.
 * Decorative: the rail says it in words.
 */
export function ReferenceMarker({ size = 4, color = tokens.system, testID }: CalibrationMarkerProps) {
  const g = REFERENCE_MARKER;
  return (
    <Svg
      testID={testID}
      width={g.width * size}
      height={g.height * size}
      accessible={false}
      importantForAccessibility="no-hide-descendants"
    >
      <Path d={polygonPath(g, size)} fill={color} />
    </Svg>
  );
}
