import React, { useRef, useState } from 'react';
import { View, type TextInput } from 'react-native';
import { PrimaryAction } from './components';
import { AccountField, AccountFrame, AccountLink, AccountMessage } from './account/AccountFrame';

/** One branded entry. Returning users are routed past it by ConnectedApp, never by a local fixture. */
export function LoginScreen(props: {
  error: 'invalid' | 'network' | null;
  busy: boolean;
  onSubmit: (username: string, password: string) => void;
  onCreateAccount?: () => void;
  onRecover?: () => void;
  onPrivacy?: () => void;
}) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const passwordRef = useRef<React.ComponentRef<typeof TextInput>>(null);
  const sentAt = useRef<number | null>(null);
  const ready = username.trim().length > 0 && password.length > 0 && !props.busy;
  const submit = () => {
    const now = Date.now();
    if (!ready || (sentAt.current !== null && now - sentAt.current < 1500)) return;
    sentAt.current = now;
    props.onSubmit(username.trim(), password);
  };
  return <AccountFrame entry entryName="AUREN AI" footer={<>
    <PrimaryAction testID="login" tone={ready ? 'signal' : 'quiet'} busy={props.busy} label={props.busy ? 'Connexion…' : 'Se connecter'} onPress={submit} />
    {props.onCreateAccount ? <AccountLink testID="entry-signup" disabled={props.busy} label="Créer mon compte" onPress={props.onCreateAccount} /> : null}
    <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 24 }}>
      {props.onRecover ? <AccountLink label="Récupération du compte" onPress={props.onRecover} /> : null}
      {props.onPrivacy ? <AccountLink label="Confidentialité" onPress={props.onPrivacy} /> : null}
    </View>
  </>}>
    <AccountField centered label="Identifiant" value={username} onChangeText={setUsername} editable={!props.busy} autoComplete="username" textContentType="username" returnKeyType="next" onSubmitEditing={() => passwordRef.current?.focus()} />
    <AccountField centered label="Mot de passe" inputRef={passwordRef} editable={!props.busy} value={password} onChangeText={setPassword} secureTextEntry autoComplete="current-password" textContentType="password" returnKeyType="go" onSubmitEditing={submit} />
    {props.error ? <AccountMessage alert text={props.error === 'invalid' ? 'Identifiant ou mot de passe incorrect.' : 'AUREN est injoignable. Vérifie la connexion, puis réessaie.'} /> : null}
  </AccountFrame>;
}
