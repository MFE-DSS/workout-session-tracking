import React from 'react';
import Svg, { Path } from 'react-native-svg';

import { color as tokens } from '../theme';
import { ACTIVE_CURSOR, polygonPath } from './geometry';
import type { CalibrationMarkerProps } from './ReferenceMarker';

/**
 * The value the user is choosing — the object in flight, and the only primitive
 * of the rail that carries the full `signal`. Taller and narrower than the
 * ReferenceMarker; same slot, same walls, same axis. Decorative: the rail says it in words.
 */
export function ActiveCursor({ size = 4, color = tokens.signal, testID }: CalibrationMarkerProps) {
  const g = ACTIVE_CURSOR;
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
