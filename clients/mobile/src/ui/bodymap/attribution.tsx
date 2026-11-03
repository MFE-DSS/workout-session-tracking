import React from 'react';
import { Text, View } from 'react-native';

import { color, type } from '../theme';
import { BODY_SOURCE } from './bodyGeometry';

/**
 * DA-04.3 — the central credit of the body the BodyMap draws (react-native-body-highlighter,
 * MIT): its copyright and licence, as the MIT terms ask, in one central place (the journal
 * sheet), never repeated in the windows. The BodyParts3D / Servier master is no longer drawn
 * by the app, so its credit is no longer shown here (it stays with the design source).
 * tests/test_auren_bodymap_runtime.py checks this text against the vendored LICENSE.
 */
export const BODYMAP_ATTRIBUTION = [
  `Silhouette musculaire : ${BODY_SOURCE.package} ${BODY_SOURCE.version}, ${BODY_SOURCE.copyright}, licence ${BODY_SOURCE.license}.`,
] as const;
export const BODYMAP_NON_MEDICAL = 'Visualisation non médicale — revue anatomique professionnelle non réalisée.';
export const MIT_LICENSE_URL = 'https://opensource.org/license/mit';
/** MOB-01 · D4 — two tab icons are normalised from Lucide (ISC): the notice travels with the app, here, once. */
export const TAB_ICONS_ATTRIBUTION =
  'Icônes Programmes et Progrès : dérivées de Lucide 1.66.0 (file-stack, trending-up), © 2026 Lucide Icons and Contributors, licence ISC.';
export const ISC_LICENSE_URL = 'https://opensource.org/license/isc-license-txt';

export function LicencesSection() {
  return (
    <View testID="licences" accessibilityRole="summary" style={{ gap: 6 }}>
      <Text style={type.eyebrow}>Licences</Text>
      {BODYMAP_ATTRIBUTION.map((line) => (
        <Text key={line} style={type.small}>
          {line}
        </Text>
      ))}
      <Text style={type.small} selectable>
        {MIT_LICENSE_URL}
      </Text>
      <Text style={[type.small, { color: color.ink2 }]}>{BODYMAP_NON_MEDICAL}</Text>
      <Text style={type.small}>{TAB_ICONS_ATTRIBUTION}</Text>
      <Text style={type.small} selectable>
        {ISC_LICENSE_URL}
      </Text>
    </View>
  );
}
