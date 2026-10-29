import React from 'react';
import { Text, View } from 'react-native';

import { color, type } from '../theme';

/**
 * DA-04.0b / DA-04.1 — the central attribution of the BodyMap, required before any
 * product mount. The text is the registry's (`auren_bodymap_source.yaml`: `attribution_fr`,
 * `non_medical_notice_fr`, `license_url`), word for word; tests/test_auren_bodymap_runtime.py
 * checks the parity. One central place (the journal sheet), not repeated in every card.
 */
export const BODYMAP_ATTRIBUTION = [
  'Anatomie adaptée de BodyParts3D, © The Database Center for Life Science, sous licence CC BY 4.0.',
  'Dorsaux et sangle abdominale adaptés de Servier Medical Art, sous licence CC BY 4.0.',
] as const;
export const BODYMAP_NON_MEDICAL = 'Visualisation non médicale — revue anatomique professionnelle non réalisée.';
export const CC_BY_4_URL = 'https://creativecommons.org/licenses/by/4.0/';

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
        {CC_BY_4_URL}
      </Text>
      <Text style={[type.small, { color: color.ink2 }]}>{BODYMAP_NON_MEDICAL}</Text>
    </View>
  );
}
