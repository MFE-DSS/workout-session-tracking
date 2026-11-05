/** Dedicated acceptance bench. No credentials, no network and no production/storage imports. */
import React, { useEffect, useState } from 'react';
import { useURL } from 'expo-linking';
import { Text, View, useWindowDimensions } from 'react-native';
import { SafeAreaProvider, SafeAreaFrameContext, SafeAreaInsetsContext } from 'react-native-safe-area-context';
import { LoginScreen } from '../../LoginScreen';
import { SignupScreen, PasswordScreen } from '../AccountForms';
import { AccountResultScreen, AccountSettingsScreen, JournalOwnershipScreen } from '../AccountPages';
import { BlueprintCandidate } from './BlueprintCandidate';
import { MissionScreenFixture } from '../../contract/MissionScreenFixture';
import { color, type } from '../../theme';

export const REVIEW_CASES = [
  ['entry', '01 · Entrée', 'Composition candidate · consommateur natif'],
  ['signup', '02 · Inscription', 'Composition candidate · API de compte existante'],
  ['created', '03 · Compte créé', 'Confirmation serveur uniquement'],
  ['point', '04 · Point de départ', 'Candidat Blueprint · UI_DATA_GAP-01 · saisie de démonstration'],
  ['availability', '05 · Disponibilité', 'Candidat Blueprint · UI_DATA_GAP-02 · pas de sauvegarde'],
  ['priorities', '06 · Physique souhaité', 'Candidat Blueprint · UI_DATA_GAP-03 · pas de sauvegarde'],
  ['first-plan', '07 · Premier plan', 'Candidat de handoff · UI_DATA_GAP-04'],
  ['mission-reference', '08 · MISSION', 'Référence LOCKED existante · fixture canonique de démonstration'],
  ['settings', '09 · Compte', 'Suppression inactive · politique et confidentialité à définir'],
  ['password', '10 · Mot de passe', 'Composition candidate · mutation canonique'],
  ['password-done', '10b · Mot de passe modifié', 'Confirmation serveur du changement uniquement'],
  ['entry-error', '11 · Connexion refusée', 'Identifiants non reconnus'],
  ['signup-error', '12 · Création refusée', 'Refus canonique · identifiant indisponible'],
  ['signup-unknown', '13 · Réponse perdue', 'Aucune nouvelle création automatique'],
  ['password-unknown', '14 · Résultat à vérifier', 'Aucune répétition de changement de mot de passe'],
  ['owner-offline', '15 · Propriétaire incertain', 'Aucun détail du journal avant preuve'],
  ['owner-checking', '16 · Vérification', 'Chargement · aucune confirmation inventée'],
  ['expired', '17 · Accès expiré', 'Reconnexion · faits locaux conservés'],
  ['entry-loading', '18 · Connexion en cours', 'Action occupée et clavier accessible'],
  ['no-plan', '19 · Information manquante', 'Candidat de sortie · manque exact fourni par le domaine'],
] as const;
type CaseId = typeof REVIEW_CASES[number][0];
const nextOf = (id: string): CaseId => REVIEW_CASES[(REVIEW_CASES.findIndex((c) => c[0] === id) + 1) % REVIEW_CASES.length][0];
function Candidate(p: { id: CaseId; go: (id: CaseId) => void; width: number; height: number }) {
  const back = () => p.go('entry'); const next = () => p.go(nextOf(p.id));
  if (p.id.startsWith('entry')) return <LoginScreen error={p.id === 'entry-error' ? 'invalid' : null} busy={p.id === 'entry-loading'} onSubmit={() => p.go('entry-error')} onCreateAccount={() => p.go('signup')} onRecover={() => p.go('expired')} onPrivacy={() => p.go('settings')} />;
  if (p.id.startsWith('signup')) return <SignupScreen busy={false} outcome={p.id === 'signup-unknown' ? { state: 'unknown' } : p.id === 'signup-error' ? { state: 'rejected', code: 'username_unavailable' } : null} onSubmit={() => p.go('created')} onBack={back} onLogin={back} />;
  if (p.id === 'password-done') return <AccountResultScreen kind="password" onContinue={() => p.go('settings')} />;
  if (p.id.startsWith('password')) return <PasswordScreen busy={false} outcome={p.id === 'password-unknown' ? { state: 'unknown' } : null} onSubmit={() => p.go('password-done')} onBack={() => p.go('settings')} onLogin={back} />;
  if (p.id === 'created') return <AccountResultScreen kind="created" onContinue={() => p.go('point')} />;
  if (['point','availability','priorities','first-plan','no-plan'].includes(p.id)) return <BlueprintCandidate step={p.id === 'point' ? 1 : p.id === 'availability' ? 2 : p.id === 'priorities' ? 3 : 4} missing={p.id === 'no-plan'} onBack={back} onNext={p.id === 'first-plan' ? () => p.go('mission-reference') : next} />;
  if (p.id === 'mission-reference') return <MissionScreenFixture width={p.width} height={p.height} source="main" />;
  if (p.id === 'settings') return <AccountSettingsScreen username="Compte de démonstration" onPassword={() => p.go('password')} onExport={() => p.go('expired')} onPrivacy={() => p.go('owner-offline')} onSignOut={back} />;
  if (p.id === 'owner-offline' || p.id === 'owner-checking' || p.id === 'expired') return <JournalOwnershipScreen state={p.id === 'expired' ? 'expired' : p.id === 'owner-checking' ? 'checking' : 'offline'} onVerify={() => p.go('owner-checking')} onChangeAccount={back} />;
  return null;
}
function Framed(p: { id: CaseId; width: number; height: number; go: (id: CaseId) => void; android: boolean }) {
  const insets = p.android ? { top: 24, bottom: 24, left: 0, right: 0 } : { top: 47, bottom: 34, left: 0, right: 0 };
  return <SafeAreaFrameContext.Provider value={{ x: 0, y: 0, width: p.width, height: p.height }}><SafeAreaInsetsContext.Provider value={insets}>
    <View testID={`review-${p.id}`} style={{ width: p.width, height: p.height, backgroundColor: color.field, overflow: 'hidden' }}><Candidate {...p} /></View>
  </SafeAreaInsetsContext.Provider></SafeAreaFrameContext.Provider>;
}
export function AccountReviewBoard() {
  const incomingUrl = useURL();
  const search = (globalThis as { location?: { search?: string } }).location?.search ?? '';
  const query = new URLSearchParams(search);
  const initial = query.get('case') ?? process.env.EXPO_PUBLIC_REVIEW_CASE;
  const [selected, setSelected] = useState<CaseId | null>(REVIEW_CASES.some((c) => c[0] === initial) ? initial as CaseId : null);
  useEffect(() => {
    if (!incomingUrl) return;
    const candidate = new URLSearchParams(incomingUrl.split('?')[1] ?? '').get('case');
    if (REVIEW_CASES.some((c) => c[0] === candidate)) setSelected(candidate as CaseId);
  }, [incomingUrl]);
  const window = useWindowDimensions();
  const android = query.get('frame') === 'android';
  const width = Number(query.get('width')) || (selected ? Math.min(window.width, 430) : 390);
  const height = Number(query.get('height')) || (selected ? window.height : 844);
  if (selected) return <SafeAreaProvider><Framed id={selected} width={width} height={height} go={setSelected} android={android} /></SafeAreaProvider>;
  return <SafeAreaProvider><View style={{ padding: 24, gap: 24, backgroundColor: color.field }}>
    <Text accessibilityRole="header" style={type.title}>AUREN · MOB-03</Text>
    <Text style={type.body}>Planche candidate · Croquis validé le 5 novembre · Aucun compte ni donnée enregistrés sur ce banc.</Text>
    <Text style={type.small}>Les étapes Blueprint illustrent la composition ; leurs contrats manquent encore. Les cadres sont des previews web, pas une recette iPhone/Android.</Text>
    <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 24 }}>{REVIEW_CASES.map(([id, label, note]) => <View key={id} style={{ width, gap: 12 }}>
      <Text style={type.bodyStrong}>{label}</Text><Text style={[type.small, { minHeight: 40 }]}>{note}</Text>
      <View style={{ borderWidth: 1, borderColor: color.line }}><Framed id={id} width={width} height={height} go={setSelected} android={android} /></View>
    </View>)}</View>
  </View></SafeAreaProvider>;
}
