import React from 'react';
import { View } from 'react-native';
import Svg, { Path } from 'react-native-svg';

import { color } from '../theme';
import { BODY_PARTS, ZONE_SLUGS } from './bodyGeometry';
import { type BodyMapViewPreset, cameraFor, viewBoxString } from './viewPresets';

/**
 * DA-04.1 / DA-04.3 — one camera over the body: a functional LOCALISATION, not an atlas.
 *
 * Hierarchy: the zone put in the foreground  >  the rest of the body  >  the chassis.
 * - the foreground zone is the only colour: `system`, solid — information supplied by
 *   AUREN, like the ReferenceMarker. Never `signal`, which stays the operator's action
 *   (SEMANTIC-TOKENS-V1, operator 2026-10-29). It means « zone currently foregrounded by
 *   AUREN » — never activation, intensity, EMG, injury, recovery or effectiveness;
 * - every other part of the body is one quiet tone; the gaps between the parts draw the
 *   muscle groups — a silent skeleton, never dark masses competing with the foreground;
 * - no shadow, no gradient, no glow; the parts are the package's, untouched.
 *
 * The foreground zone is painted LAST so no neighbour covers it. Paths are never altered.
 */
export const BODYMAP_ROLE = {
  body: color.ink3,
  foreground: color.system,
} as const;

/** Opacity of the quiet body, measured on the window's `field` (DA-04.3 report). */
export const BODYMAP_QUIET = {
  /** every part that is not the foreground zone: ink3 at 0.22 on field */
  body: 0.22,
} as const;

export type BodyMapViewProps = {
  preset: BodyMapViewPreset;
  width: number;
  height: number;
  testID?: string;
};

export function BodyMapView({ preset, width, height, testID }: BodyMapViewProps) {
  const cam = cameraFor(preset, width / height);
  const zoneSlugs: readonly string[] = (ZONE_SLUGS[preset.zone] as Partial<Record<string, readonly string[]>>)[preset.side] ?? [];
  const parts = BODY_PARTS[preset.side];
  const rest = parts.filter((p) => !zoneSlugs.includes(p.slug));
  const foreground = parts.filter((p) => zoneSlugs.includes(p.slug));
  return (
    <View
      testID={testID ?? 'window-bodymap'}
      accessible
      accessibilityRole="image"
      accessibilityLabel={`${preset.label} : zone mise en avant, vue de ${preset.side === 'front' ? 'face' : 'dos'}`}
      style={{ width, height }}
    >
      <Svg width={width} height={height} viewBox={viewBoxString(cam)} accessible={false} importantForAccessibility="no-hide-descendants">
        {rest.flatMap((p) =>
          p.d.map((d, i) => <Path key={`${p.slug}-${i}`} d={d} fill={BODYMAP_ROLE.body} fillOpacity={BODYMAP_QUIET.body} />),
        )}
        {foreground.flatMap((p) => p.d.map((d, i) => <Path key={`${p.slug}-${i}-z`} d={d} fill={BODYMAP_ROLE.foreground} />))}
      </Svg>
    </View>
  );
}
