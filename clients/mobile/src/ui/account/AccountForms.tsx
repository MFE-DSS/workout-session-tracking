import React, { useEffect, useRef, useState } from 'react';
import type { TextInput } from 'react-native';
import type { AccountOutcome, PasswordChange, Registration } from '../../auth/authSession';
import { PrimaryAction } from '../components';
import { AccountField, AccountFrame, AccountLink, AccountMessage } from './AccountFrame';
export type SignupProps = { busy: boolean; outcome: AccountOutcome | null; onSubmit: (value: Registration) => void; onBack: () => void; onLogin: () => void };
export type PasswordProps = { busy: boolean; outcome: AccountOutcome | null; onSubmit: (value: PasswordChange) => void; onBack: () => void; onLogin: () => void };
const REJECTION: Record<string, string> = {
  username_too_short: 'Utilise au moins 3 caractères pour ton identifiant.', username_too_long: 'Ton identifiant doit contenir au plus 64 caractères.',
  username_unavailable: 'Cet identifiant est déjà utilisé.', email_unavailable: 'Cet email est déjà associé à un compte.',
  invalid_username: 'Utilise de 3 à 64 caractères : lettres, chiffres, tiret ou soulignement.',
  invalid_email: 'Vérifie l’adresse email.', invalid_password: 'Le mot de passe ne respecte pas les règles AUREN. Utilise au moins 8 caractères et évite un mot de passe trop long.',
  password_mismatch: 'Les mots de passe ne correspondent pas.', invalid_current_password: 'Le mot de passe actuel est incorrect.',
  credentials_changed: 'Les accès ont changé. Reconnecte-toi pour vérifier le compte.',
};
function useSubmission(busy: boolean, outcome: AccountOutcome | null) {
  const lock = useRef(false);
  useEffect(() => { if (!busy) lock.current = false; }, [busy, outcome]);
  return () => { if (busy || lock.current || outcome?.state === 'unknown' || outcome?.state === 'confirmed') return false; lock.current = true; return true; };
}
function Refusal({ outcome, local }: { outcome: AccountOutcome | null; local: string | null }) {
  const text = local ?? (outcome?.state === 'rejected' ? REJECTION[outcome.code ?? ''] ?? 'La demande a été refusée. Vérifie les informations avant de réessayer.' : null);
  return text ? <AccountMessage alert text={text} /> : null;
}
export function SignupScreen(p: SignupProps) {
  const [username, setUsername] = useState(''); const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState(''); const [email, setEmail] = useState(''); const [local, setLocal] = useState<string | null>(null);
  const passwordRef = useRef<React.ComponentRef<typeof TextInput>>(null); const confirmRef = useRef<React.ComponentRef<typeof TextInput>>(null); const emailRef = useRef<React.ComponentRef<typeof TextInput>>(null);
  const take = useSubmission(p.busy, p.outcome);
  const submit = () => {
    if (!username.trim() || !password || !confirm) { setLocal('Complète ton identifiant et les deux champs de mot de passe.'); return; }
    if (password !== confirm) { setLocal('Les mots de passe ne correspondent pas.'); return; }
    if (!take()) return; setLocal(null);
    p.onSubmit({ username: username.trim(), password, password_confirm: confirm, email: email.trim() });
  };
  const unknown = p.outcome?.state === 'unknown';
  return <AccountFrame title="Créer ton compte" lead="Ton entraînement et ton historique, dans ton espace AUREN." onBack={p.onBack} backDisabled={p.busy} footer={<>
    {unknown ? <PrimaryAction testID="signup-verify" label="Vérifier mon compte" onPress={p.onLogin} />
      : <PrimaryAction testID="signup-submit" busy={p.busy} label={p.busy ? 'Création…' : 'Créer mon compte'} onPress={submit} />}
    <AccountLink disabled={p.busy} label="J’ai déjà un compte" onPress={p.onLogin} />
  </>}>
    <AccountField editable={!p.busy} returnKeyType="next" onSubmitEditing={() => passwordRef.current?.focus()} label="Identifiant" value={username} onChangeText={setUsername} autoComplete="username" textContentType="username" />
    <AccountField editable={!p.busy} inputRef={passwordRef} returnKeyType="next" onSubmitEditing={() => confirmRef.current?.focus()} label="Mot de passe" value={password} onChangeText={setPassword} secureTextEntry autoComplete="new-password" textContentType="newPassword" helper="Au moins 8 caractères." />
    <AccountField editable={!p.busy} inputRef={confirmRef} returnKeyType="next" onSubmitEditing={() => emailRef.current?.focus()} label="Confirmer le mot de passe" value={confirm} onChangeText={setConfirm} secureTextEntry autoComplete="new-password" textContentType="newPassword" />
    <AccountField editable={!p.busy} inputRef={emailRef} returnKeyType="go" onSubmitEditing={submit} label="Email (facultatif)" value={email} onChangeText={setEmail} keyboardType="email-address" autoComplete="email" textContentType="emailAddress" helper="Utile pour récupérer ton compte. Sans email, la récupération par email ne sera pas possible." />
    {unknown ? <AccountMessage text="La réponse n’est pas arrivée. Ton compte peut avoir été créé : vérifie en te connectant avant de refaire une demande." /> : <Refusal outcome={p.outcome} local={local} />}
  </AccountFrame>;
}
export function PasswordScreen(p: PasswordProps) {
  const [current, setCurrent] = useState(''); const [next, setNext] = useState(''); const [confirm, setConfirm] = useState('');
  const nextRef = useRef<React.ComponentRef<typeof TextInput>>(null); const confirmRef = useRef<React.ComponentRef<typeof TextInput>>(null);
  const [local, setLocal] = useState<string | null>(null); const take = useSubmission(p.busy, p.outcome);
  const submit = () => {
    if (!current || !next || !confirm) { setLocal('Complète les trois champs.'); return; }
    if (next !== confirm) { setLocal('Les mots de passe ne correspondent pas.'); return; }
    if (!take()) return; setLocal(null);
    p.onSubmit({ current_password: current, new_password: next, new_password_confirm: confirm });
  };
  const unknown = p.outcome?.state === 'unknown';
  return <AccountFrame title="Ton mot de passe" lead="Les autres connexions seront révoquées après la modification." onBack={p.onBack} backDisabled={p.busy} footer={unknown
    ? <PrimaryAction testID="password-verify" label="Vérifier par connexion" onPress={p.onLogin} />
    : <PrimaryAction testID="password-submit" busy={p.busy} label={p.busy ? 'Modification…' : 'Mettre à jour'} onPress={submit} />}>
    <AccountField editable={!p.busy} returnKeyType="next" onSubmitEditing={() => nextRef.current?.focus()} label="Mot de passe actuel" value={current} onChangeText={setCurrent} secureTextEntry autoComplete="current-password" textContentType="password" />
    <AccountField editable={!p.busy} inputRef={nextRef} returnKeyType="next" onSubmitEditing={() => confirmRef.current?.focus()} label="Nouveau mot de passe" value={next} onChangeText={setNext} secureTextEntry autoComplete="new-password" textContentType="newPassword" helper="Au moins 8 caractères." />
    <AccountField editable={!p.busy} inputRef={confirmRef} returnKeyType="go" onSubmitEditing={submit} label="Confirmer le mot de passe" value={confirm} onChangeText={setConfirm} secureTextEntry autoComplete="new-password" textContentType="newPassword" />
    {unknown ? <AccountMessage text="Le résultat doit être vérifié. Reconnecte-toi avec le nouveau mot de passe ; si nécessaire, essaie l’ancien. Aucune modification n’est rejouée automatiquement." /> : <Refusal outcome={p.outcome} local={local} />}
  </AccountFrame>;
}
