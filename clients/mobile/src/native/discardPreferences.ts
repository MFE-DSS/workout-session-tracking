import { Alert, Platform } from 'react-native';

/** A form exit never alters training facts; only its unconfirmed in-memory draft. */
export function confirmDiscardPreferences(onDiscard: () => void): boolean {
  if (Platform.OS === 'web') return false;
  Alert.alert('Quitter les préférences ?', 'Les modifications non enregistrées seront perdues.', [
    { text: 'Continuer à modifier', style: 'cancel' },
    { text: 'Quitter', style: 'destructive', onPress: onDiscard },
  ]);
  return true;
}
