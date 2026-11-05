import React from 'react';
import { View, Text } from 'react-native';
import { PrimaryAction, SheetRow } from '../components';
import { color, type } from '../theme';
import { AccountFrame, AccountLink, AccountMessage } from './AccountFrame';

export function AccountResultScreen(p: { kind: 'created' | 'password'; onContinue: () => void }) {
  return <AccountFrame title={p.kind === 'created' ? 'Ton compte est créé.' : 'Mot de passe mis à jour.'}
    lead={p.kind === 'created' ? 'Ton espace AUREN est prêt. Retrouve maintenant ce que tu peux faire aujourd’hui.' : 'Cette connexion reste active. Les anciens accès ont été révoqués.'}
    footer={<PrimaryAction testID="account-result-continue" label="Continuer" onPress={p.onContinue} />}>
    <View style={{ height: 1, backgroundColor: color.line, marginVertical: 16 }} />
    <Text style={type.eyebrow}>{p.kind === 'created' ? 'Comprendre · Planifier · Exécuter' : 'Compte sécurisé'}</Text>
  </AccountFrame>;
}
export function AccountSettingsScreen(p: { username: string | null; onPassword: () => void; onExport?: () => void; onPrivacy?: () => void; onPreferences?: () => void; onWebProfile?: () => void; onSignOut: () => void }) {
  return <AccountFrame title="Ton compte" lead={p.username ?? 'Compte lié à cet appareil'} footer={<AccountLink label="Se déconnecter" onPress={p.onSignOut} testID="settings-signout" />}>
    <SheetRow title="Changer le mot de passe" onPress={p.onPassword} />
    {p.onExport ? <SheetRow title="Exporter mes données" detail="Sur le site · une connexion web peut être nécessaire" onPress={p.onExport} /> : null}
    {p.onPrivacy ? <SheetRow title="Confidentialité" onPress={p.onPrivacy} /> : null}
    <View style={{ paddingVertical: 16, gap: 8 }}>
      <Text style={type.eyebrow}>Suppression du compte</Text>
      <AccountMessage text="La suppression du compte n’est pas disponible dans cette version." />
    </View>
    {p.onPreferences ? <SheetRow title="Préférences d’entraînement" onPress={p.onPreferences} />
      : p.onWebProfile ? <SheetRow title="Profil d’entraînement" detail="Sur le site, pour l’instant" onPress={p.onWebProfile} /> : null}
  </AccountFrame>;
}
export function JournalOwnershipScreen(p: { state: 'checking' | 'offline' | 'expired'; busy?: boolean; onVerify: () => void; onChangeAccount: () => void }) {
  const title = p.state === 'expired' ? 'Retrouvons ton compte.' : p.state === 'checking' ? 'Un instant.' : 'Ton journal est conservé.';
  return <AccountFrame title={title} lead={p.state === 'expired'
    ? 'Reconnecte-toi pour retrouver ton espace. Les séries gardées sur cet appareil restent conservées.'
    : p.state === 'checking' ? 'AUREN vérifie à quel compte appartient le journal de cet appareil.'
    : 'Une connexion est nécessaire pour vérifier son propriétaire avant de l’ouvrir. Aucune série n’est effacée.'}
    footer={<>
      <PrimaryAction testID="owner-verify" busy={p.busy || p.state === 'checking'} label={p.state === 'checking' ? 'Vérification…' : p.state === 'expired' ? 'Me reconnecter' : 'Vérifier'} onPress={p.onVerify} />
      <AccountLink label="Changer de compte" onPress={p.onChangeAccount} />
    </>}><View style={{ height: 1, backgroundColor: color.line, marginVertical: 16 }} /></AccountFrame>;
}
