import React from 'react';
import Svg, { Path } from 'react-native-svg';

import { AUREN_MARK_V1, markDrawingFor } from './markGeometry';

/**
 * DA-03.2 — `AUREN-MARK-V1`. The caller gives a size and an ink; the optical drawing is
 * chosen here, never by the caller, and nothing is rendered under 12 px.
 *
 * Monochrome first: `color` inks the whole mark. `cursorColor` / `markerColor` are the
 * contextual two-colour expression (app icon: `signal` over `system`) — never required.
 * Every colour is a theme token passed in; the geometry carries none. Decorative: the
 * name it stands for is always said by adjacent text.
 */
export function AurenMark(p: { size: number; color: string; cursorColor?: string; markerColor?: string; testID?: string }) {
  const drawing = markDrawingFor(p.size);
  if (!drawing) return null;
  const g = AUREN_MARK_V1[drawing];
  return (
    <Svg
      testID={p.testID ?? 'auren-mark'}
      width={p.size}
      height={p.size}
      viewBox={`0 0 ${g.grid} ${g.grid}`}
      accessible={false}
      importantForAccessibility="no-hide-descendants"
    >
      <Path d={g.cursor} fill={p.cursorColor ?? p.color} />
      <Path d={g.marker} fill={p.markerColor ?? p.color} />
    </Svg>
  );
}
