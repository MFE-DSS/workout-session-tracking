import React, { useRef, useState } from 'react';
import { KeyboardAvoidingView, StyleSheet, Text, TextInput, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { keyboardAvoidance } from '../native/platformUi';
import { PrimaryAction } from './components';
import { color, space, type } from './theme';

/**
 * D9 — the one sign-in of the device. Username and password, nothing else: no
 * social login, no Apple Sign In (out of scope). The password field is the
 * system's secure field, so iOS offers its password manager.
 */
export function LoginScreen(props: {
  error: 'invalid' | 'network' | null;
  busy: boolean;
  onSubmit: (username: string, password: string) => void;
}) {
  const insets = useSafeAreaInsets();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const passwordRef = useRef<React.ComponentRef<typeof TextInput>>(null);
  // `busy` arrives one render late: the keyboard's « go » and the button could
  // both submit before it does. A ref closes that window (seen on device: 2 POST per tap).
  const sentAtRef = useRef(0);
  const ready = username.trim().length > 0 && password.length > 0 && !props.busy;
  const submit = () => {
    const now = Date.now();
    if (!ready || now - sentAtRef.current < 1500) return;
    sentAtRef.current = now;
    props.onSubmit(username.trim(), password);
  };

  return (
    // the avoider's own padding replaces any paddingBottom set on it: the screen's margins live one view inside
    <KeyboardAvoidingView behavior={keyboardAvoidance.behavior} style={styles.avoider}>
      <View style={[styles.root, { paddingTop: insets.top + 8, paddingBottom: insets.bottom + 12 }]}>
        <Text style={[type.eyebrow, styles.centered]}>AUREN</Text>
        <Text style={styles.title} accessibilityRole="header">Connexion</Text>
        <Text style={[type.body, styles.centered, { marginTop: 6 }]}>Ton compte AUREN, le même que sur le site.</Text>

        <View style={styles.fields}>
          <Text style={type.eyebrow}>Identifiant</Text>
          <TextInput
            value={username}
            onChangeText={setUsername}
            autoCapitalize="none"
            autoCorrect={false}
            spellCheck={false}
            autoComplete="username"
            textContentType="username"
            returnKeyType="next"
            onSubmitEditing={() => passwordRef.current?.focus()}
            accessibilityLabel="Identifiant"
            style={styles.input}
            selectionColor={color.signal}
          />
          <Text style={[type.eyebrow, { marginTop: space.m }]}>Mot de passe</Text>
          <TextInput
            ref={passwordRef}
            value={password}
            onChangeText={setPassword}
            secureTextEntry
            autoCapitalize="none"
            autoCorrect={false}
            spellCheck={false}
            autoComplete="current-password"
            textContentType="password"
            returnKeyType="go"
            onSubmitEditing={submit}
            accessibilityLabel="Mot de passe"
            style={styles.input}
            selectionColor={color.signal}
          />
          {props.error ? (
            <Text style={styles.error} accessibilityLiveRegion="polite">
              {props.error === 'invalid' ? 'Identifiant ou mot de passe incorrect.' : 'AUREN est injoignable. Vérifie la connexion, puis réessaie.'}
            </Text>
          ) : null}
        </View>

        <View style={{ flex: 1 }} />
        <PrimaryAction
          testID="login"
          tone={ready ? 'signal' : 'quiet'}
          label={props.busy ? 'Connexion…' : 'Se connecter'}
          onPress={submit}
        />
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  avoider: { flex: 1, backgroundColor: color.field },
  root: { flex: 1, backgroundColor: color.field, paddingHorizontal: space.gutter },
  centered: { textAlign: 'center' },
  title: { ...type.title, fontSize: 40, lineHeight: 46, marginTop: 28, textAlign: 'center' },
  fields: { marginTop: 36 },
  input: {
    color: color.ink,
    fontSize: 20,
    fontWeight: '600',
    marginTop: 6,
    paddingVertical: 14,
    paddingHorizontal: 16,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: color.line,
    backgroundColor: color.plate,
  },
  error: { marginTop: space.m, color: color.alert, fontSize: 15, fontWeight: '600' },
});
