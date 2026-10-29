import React from 'react';
import { View } from 'react-native';
import Svg, { Path } from 'react-native-svg';

import { color } from '../theme';
import { MASTER_BASE, MASTER_ZONES, type MasterPath, type ZoneCode } from './masterGeometry';
import { type BodyMapViewPreset, cameraFor, viewBoxString } from './viewPresets';

/**
 * DA-04.1 — one camera over the BodyMap master: a functional LOCALISATION, not an atlas.
 *
 * Hierarchy: the zone put in the foreground  >  the surrounding anatomy  >  the chassis.
 * - the foreground zone is the only colour: `system`, solid — information supplied by
 *   AUREN, like the ReferenceMarker. Never `signal`, which stays the operator's action
 *   (SEMANTIC-TOKENS-V1, operator 2026-10-29). It means « zone currently foregrounded by
 *   AUREN » — never activation, intensity, EMG, injury, recovery or effectiveness;
 * - the body is a quiet silhouette, and the other zones are a fine outline on it — a
 *   silent skeleton, never dark masses competing with the foreground;
 * - no shadow, no gradient, no glow; the geometry is the master's, untouched.
 *
 * The foreground zone is painted LAST so no neighbour covers it (the master's own order
 * paints, e.g., the biceps over the lower deltoid). Paths are never altered.
 */
export const BODYMAP_ROLE = {
  silhouette: color.ink3,
  context: color.ink3,
  foreground: color.system,
} as const;

/** Opacities of the quiet roles, measured on the window's `field` (DA-04.1 report). */
export const BODYMAP_QUIET = {
  /** the body: ink3 at 0.16 on field */
  silhouette: 0.16,
  /** the other zones' fill, barely above the body */
  contextFill: 0.06,
  /** the other zones' outline */
  contextLine: 0.45,
  /** outline width, in screen px (converted to master units per camera) */
  lineWidthPx: 0.75,
} as const;

export type BodyMapViewProps = {
  preset: BodyMapViewPreset;
  width: number;
  height: number;
  testID?: string;
};

export function BodyMapView({ preset, width, height, testID }: BodyMapViewProps) {
  const cam = cameraFor(preset, width / height);
  const line = (BODYMAP_QUIET.lineWidthPx * cam.w) / width;
  const onSide = (p: MasterPath) => p.side === preset.side;
  const zones = Object.keys(MASTER_ZONES) as ZoneCode[];
  const context = zones.filter((z) => z !== preset.zone).flatMap((z) => MASTER_ZONES[z].filter(onSide));
  const foreground = MASTER_ZONES[preset.zone].filter(onSide);
  return (
    <View
      testID={testID ?? 'window-bodymap'}
      accessible
      accessibilityRole="image"
      accessibilityLabel={`${preset.label} : zone mise en avant, vue de ${preset.side === 'front' ? 'face' : 'dos'}`}
      style={{ width, height }}
    >
      <Svg width={width} height={height} viewBox={viewBoxString(cam)} accessible={false} importantForAccessibility="no-hide-descendants">
        <Path d={MASTER_BASE[preset.side].d} fill={BODYMAP_ROLE.silhouette} fillOpacity={BODYMAP_QUIET.silhouette} />
        {context.map((p) => (
          <Path
            key={p.id}
            d={p.d}
            fill={BODYMAP_ROLE.context}
            fillOpacity={BODYMAP_QUIET.contextFill}
            stroke={BODYMAP_ROLE.context}
            strokeOpacity={BODYMAP_QUIET.contextLine}
            strokeWidth={line}
            strokeLinejoin="round"
          />
        ))}
        {foreground.map((p) => (
          <Path key={p.id} d={p.d} fill={BODYMAP_ROLE.foreground} />
        ))}
      </Svg>
    </View>
  );
}
