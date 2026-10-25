/**
 * R16 — leaving a session is ONE native confirmation sheet with exactly four
 * choices. On iOS it is the system action sheet (`UIAlertController`): the
 * destructive choice is red, ANNULER is the system cancel row. Elsewhere the
 * caller shows the same four rows in its own sheet.
 */
import { ActionSheetIOS, Platform } from 'react-native';

export type ExitChoice = 'finish' | 'pause' | 'abandon' | 'cancel';

export const EXIT_OPTIONS: { choice: ExitChoice; label: string }[] = [
  { choice: 'finish', label: 'Terminer maintenant' },
  { choice: 'pause', label: 'Mettre en pause' },
  { choice: 'abandon', label: 'Abandonner la séance' },
  { choice: 'cancel', label: 'Annuler' },
];

/** The facts the sheet states before any choice: what is recorded, what is not. */
export function exitMessage(setsDone: number, setsPlanned: number): string {
  if (setsDone === 0) return 'Aucune série enregistrée pour l’instant.';
  return `${setsDone} série${setsDone > 1 ? 's' : ''} enregistrée${setsDone > 1 ? 's' : ''} sur ${setsPlanned}. Terminer les garde ; abandonner les garde aussi, mais la séance ne comptera pas.`;
}

/** Shows the native sheet. Returns false when the platform has none (caller falls back). */
export function showNativeExitSheet(message: string, onChoice: (c: ExitChoice) => void): boolean {
  if (Platform.OS !== 'ios') return false;
  ActionSheetIOS.showActionSheetWithOptions(
    {
      title: 'Quitter la séance',
      message,
      options: EXIT_OPTIONS.map((o) => o.label),
      destructiveButtonIndex: 2,
      cancelButtonIndex: 3,
      userInterfaceStyle: 'dark',
    },
    (index) => onChoice(EXIT_OPTIONS[index]?.choice ?? 'cancel'),
  );
  return true;
}
