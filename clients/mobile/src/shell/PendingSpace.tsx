/**
 * MOB-01 — a space whose functions are not migrated yet (spec `mobile/navigation-shell`, « Espace non migré »).
 *
 * It says what the space will hold, invents no content and offers AT MOST one action: the existing web page.
 */
import React from 'react';
import { Linking } from 'react-native';

import { QuietScreen } from '../ui/QuietScreen';
import { useShell } from './ShellContext';

export function PendingSpace(props: { eyebrow: string; title: string; text: string; webPath: string }) {
  const { openJournal, siteUrl } = useShell();
  return (
    <QuietScreen
      eyebrow={props.eyebrow}
      title={props.title}
      text={props.text}
      action={siteUrl ? { label: 'Ouvrir sur le site', onPress: () => void Linking.openURL(`${siteUrl}${props.webPath}`) } : undefined}
      onOpenJournal={openJournal}
    />
  );
}
