import React from 'react';
import { KeyboardAvoidingView, Pressable, ScrollView, StyleSheet, Text, TextInput, type TextInputProps, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { keyboardAvoidance } from '../../native/platformUi';
import { AurenMark } from '../brand/AurenMark';
import { color, space, type } from '../theme';

/** Composition only. All inks, type, field treatment and actions reuse AUREN's existing roles. */
export function AccountFrame(p: { title?: string; lead?: string; entry?: boolean; entryName?: string; step?: string; onBack?: () => void; backDisabled?: boolean; children?: React.ReactNode; footer?: React.ReactNode }) {
  const insets = useSafeAreaInsets();
  return <KeyboardAvoidingView behavior={keyboardAvoidance.behavior} style={styles.root}>
    <ScrollView keyboardShouldPersistTaps="handled" contentInsetAdjustmentBehavior="never"
      contentContainerStyle={{ flexGrow: 1, paddingHorizontal: space.gutter, paddingTop: insets.top + 12, paddingBottom: insets.bottom + 12 }}>
      {p.entry ? <View style={{ alignItems: 'center', paddingTop: 12 }}>
        <AurenMark size={64} color={color.ink} testID="entry-auren-mark" />
        <Text style={[type.eyebrow, { color: color.ink, marginTop: 12, letterSpacing: 4 }]}>{p.entryName ?? 'AUREN'}</Text>
        <Text style={[type.body, { textAlign: 'center', maxWidth: 260, marginTop: 16 }]}>Ton entraînement,{"\n"}construit autour de toi.</Text>
      </View> : <View style={styles.header}>
        {p.onBack ? <AccountLink label="Retour" onPress={p.onBack} disabled={p.backDisabled} testID="account-back" /> : <View style={{ width: 64 }} />}
        <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}><AurenMark size={20} color={color.ink} /><Text style={type.eyebrow}>AUREN</Text></View>
        <Text style={[type.small, { minWidth: 64, textAlign: 'right' }]}>{p.step ?? ''}</Text>
      </View>}
      {p.title ? <Text accessibilityRole="header" style={[type.title, { fontSize: 30, lineHeight: 35, marginTop: p.entry ? 32 : 28 }]}>{p.title}</Text> : null}
      {p.lead ? <Text style={[type.body, { marginTop: 12 }]}>{p.lead}</Text> : null}
      {p.children ? <View style={{ marginTop: p.entry && !p.title ? 48 : 24, gap: 16 }}>{p.children}</View> : null}
      {p.footer ? <View style={{ flexGrow: 1, justifyContent: 'flex-end', paddingTop: 24, gap: 8 }}>{p.footer}</View> : null}
    </ScrollView>
  </KeyboardAvoidingView>;
}
export function AccountField(p: TextInputProps & { label: string; helper?: string; centered?: boolean; inputRef?: React.Ref<React.ComponentRef<typeof TextInput>> }) {
  const { label, helper, centered, inputRef, ...input } = p;
  return <View style={{ gap: 6 }}>
    <Text style={[type.eyebrow, centered && { textAlign: 'center' }]}>{label}</Text>
    <TextInput ref={inputRef} autoCorrect={false} spellCheck={false} autoCapitalize="none" placeholderTextColor={color.ink3}
      selectionColor={color.signal} {...input} accessibilityLabel={label} style={[styles.input, centered && { textAlign: 'center' }, input.style]} />
    {helper ? <Text style={[type.small, centered && { textAlign: 'center' }]}>{helper}</Text> : null}
  </View>;
}
export function AccountLink(p: { label: string; onPress: () => void; testID?: string; disabled?: boolean; centered?: boolean }) {
  return <Pressable testID={p.testID} disabled={p.disabled} accessibilityState={{ disabled: p.disabled ?? false }} accessibilityRole="button" onPress={p.onPress} style={({ pressed }) => ({ minHeight: 44, justifyContent: 'center', opacity: p.disabled ? 0.5 : pressed ? 0.6 : 1 })}>
    <Text style={[type.bodyStrong, { fontSize: 15, textAlign: p.centered ? 'center' : 'left' }]}>{p.label}</Text>
  </Pressable>;
}
export function AccountMessage(p: { text: string; alert?: boolean }) {
  return <Text selectable accessibilityLiveRegion="polite" style={[type.body, { color: p.alert ? color.alert : color.ink2 }]}>{p.text}</Text>;
}
const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: color.field },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', minHeight: 44 },
  input: { color: color.ink, fontSize: 20, fontWeight: '600', minHeight: 54, paddingVertical: 14, paddingHorizontal: 16,
    borderRadius: 16, borderWidth: 1, borderColor: color.line, backgroundColor: color.plate },
});
