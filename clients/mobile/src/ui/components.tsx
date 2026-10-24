import React from 'react';
import {
  GestureResponderEvent,
  Modal,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
  ViewStyle,
} from 'react-native';
import Svg, { Circle } from 'react-native-svg';

import { nativeSheet } from '../native/platformUi';
import { ACTION_HEIGHT, color, NUMERAL_FONT_SCALE_CAP, space, type } from './theme';

// ── the one sovereign action ─────────────────────────────────────────────────

type ActionTone = 'signal' | 'trace' | 'quiet';

export function PrimaryAction(props: {
  label: string;
  sublabel?: string;
  tone?: ActionTone;
  onPress: () => void;
  onPressIn?: (e: GestureResponderEvent) => void;
  hint?: string;
  testID?: string;
}) {
  const tone = props.tone ?? 'signal';
  const fg = tone === 'signal' ? color.onSignal : tone === 'trace' ? color.system : color.ink;
  return (
    <Pressable
      testID={props.testID}
      accessibilityRole="button"
      accessibilityLabel={props.sublabel ? `${props.label}, ${props.sublabel}` : props.label}
      accessibilityHint={props.hint}
      onPress={props.onPress}
      onPressIn={props.onPressIn}
      style={({ pressed }) => [
        styles.action,
        tone === 'signal' && styles.actionSignal,
        tone === 'trace' && styles.actionTrace,
        tone === 'quiet' && styles.actionQuiet,
        pressed && styles.pressed,
      ]}
    >
      <Text style={[type.action, { color: fg }]} maxFontSizeMultiplier={1.4}>
        {props.label}
      </Text>
      {props.sublabel ? (
        <Text style={[styles.actionSub, { color: fg }]} maxFontSizeMultiplier={1.3}>
          {props.sublabel}
        </Text>
      ) : null}
    </Pressable>
  );
}

export function SecondaryButton(props: { label: string; onPress: () => void; style?: ViewStyle; a11y?: string }) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={props.a11y ?? props.label}
      onPress={props.onPress}
      style={({ pressed }) => [styles.secondary, props.style, pressed && styles.pressed]}
    >
      <Text style={[type.bodyStrong, styles.tabular]} maxFontSizeMultiplier={1.4}>
        {props.label}
      </Text>
    </Pressable>
  );
}

export function IconButton(props: { glyph: string; label: string; onPress: () => void }) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={props.label}
      hitSlop={8}
      onPress={props.onPress}
      style={({ pressed }) => [styles.icon, pressed && styles.pressed]}
    >
      <Text style={styles.iconGlyph} maxFontSizeMultiplier={1.2}>
        {props.glyph}
      </Text>
    </Pressable>
  );
}

// ── position rail: one segment per exercise — shape AND colour ───────────────

export function ExerciseRail(props: { count: number; index: number; resting: boolean }) {
  const segments = Array.from({ length: props.count }, (_, i) => i);
  return (
    <View
      style={styles.rail}
      accessible
      accessibilityLabel={`Exercice ${props.index + 1} sur ${props.count}`}
    >
      {segments.map((i) => (
        <View
          key={i}
          style={[
            styles.railSeg,
            i < props.index && styles.railDone,
            i === props.index && [styles.railNow, { backgroundColor: props.resting ? color.system : color.signal }],
          ]}
        />
      ))}
    </View>
  );
}

// ── a physical value: big readout + two thumb pads ───────────────────────────

export function ValueDial(props: {
  label: string;
  value: string;
  unit?: string;
  onMinus: () => void;
  onPlus: () => void;
  onEdit: () => void;
  stepLabel: string;
  testID?: string;
}) {
  return (
    <View style={styles.dial} testID={props.testID}>
      <Text style={type.eyebrow}>{props.label}</Text>
      <Pressable
        accessibilityRole="adjustable"
        accessibilityLabel={`${props.label} ${props.value}${props.unit ? ' ' + props.unit : ''}`}
        accessibilityHint="Toucher pour saisir une valeur"
        accessibilityActions={[{ name: 'increment' }, { name: 'decrement' }]}
        onAccessibilityAction={(e) => (e.nativeEvent.actionName === 'increment' ? props.onPlus() : props.onMinus())}
        onPress={props.onEdit}
        style={styles.dialValueRow}
      >
        <Text
          style={[type.readout, { fontSize: readoutSize(props.value, Boolean(props.unit)) }]}
          maxFontSizeMultiplier={NUMERAL_FONT_SCALE_CAP}
          numberOfLines={1}
          adjustsFontSizeToFit
        >
          {props.value}
        </Text>
        {props.unit ? <Text style={styles.unit}>{props.unit}</Text> : null}
      </Pressable>
      <View style={styles.pads}>
        <Pad glyph="−" label={`Moins ${props.stepLabel}`} onPress={props.onMinus} />
        <Pad glyph="+" label={`Plus ${props.stepLabel}`} onPress={props.onPlus} />
      </View>
    </View>
  );
}

/**
 * The readout shrinks with its own length so `107,5 kg` fits a half-width dial
 * at every load — `adjustsFontSizeToFit` alone does not exist on every platform.
 */
function readoutSize(value: string, withUnit: boolean): number {
  const chars = value.length + (withUnit ? 1.5 : 0);
  if (chars <= 3) return 68;
  if (chars <= 4.5) return 60;
  if (chars <= 5.5) return 50;
  return 42;
}

function Pad(props: { glyph: string; label: string; onPress: () => void }) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={props.label}
      onPress={props.onPress}
      style={({ pressed }) => [styles.pad, pressed && styles.padPressed]}
    >
      <Text style={styles.padGlyph} maxFontSizeMultiplier={1.2}>
        {props.glyph}
      </Text>
    </Pressable>
  );
}

// ── rest ring: drains with time; the DEADLINE is the truth, this only draws it ─

export function RestRing(props: { size: number; fraction: number; children: React.ReactNode }) {
  const stroke = props.size > 200 ? 10 : 7;
  const r = (props.size - stroke) / 2;
  const circumference = 2 * Math.PI * r;
  return (
    <View style={{ width: props.size, height: props.size, alignItems: 'center', justifyContent: 'center' }}>
      <Svg width={props.size} height={props.size} style={StyleSheet.absoluteFill}>
        <Circle cx={props.size / 2} cy={props.size / 2} r={r} stroke={color.lineRest} strokeWidth={stroke} fill="none" />
        <Circle
          cx={props.size / 2}
          cy={props.size / 2}
          r={r}
          stroke={color.system}
          strokeWidth={stroke}
          fill="none"
          strokeLinecap="round"
          strokeDasharray={`${circumference} ${circumference}`}
          strokeDashoffset={circumference * (1 - props.fraction)}
          transform={`rotate(-90 ${props.size / 2} ${props.size / 2})`}
        />
      </Svg>
      {props.children}
    </View>
  );
}

// ── native sheet: every secondary lives here, never on the instrument ─────────

export function Sheet(props: { visible: boolean; title: string; onClose: () => void; children: React.ReactNode }) {
  const own = nativeSheet.drawsOwnBackdrop;
  return (
    <Modal
      visible={props.visible}
      animationType="slide"
      presentationStyle={nativeSheet.presentationStyle}
      transparent={own}
      onRequestClose={props.onClose}
    >
      <View style={own ? styles.sheetBackdrop : styles.sheetIos}>
        <View style={own ? styles.sheetBody : styles.sheetBodyIos}>
          <View style={styles.sheetHead}>
            <Text style={[type.bodyStrong, { fontSize: 19 }]} accessibilityRole="header">
              {props.title}
            </Text>
            <SecondaryButton label="Fermer" onPress={props.onClose} style={styles.sheetClose} />
          </View>
          <ScrollView contentContainerStyle={{ paddingBottom: space.xl }}>{props.children}</ScrollView>
        </View>
      </View>
    </Modal>
  );
}

export function SheetRow(props: { title: string; detail?: string; onPress?: () => void; a11y?: string }) {
  const content = (
    <View style={styles.sheetRow}>
      <Text style={type.bodyStrong}>{props.title}</Text>
      {props.detail ? <Text style={[type.small, { marginTop: 2 }]}>{props.detail}</Text> : null}
    </View>
  );
  if (!props.onPress) return content;
  return (
    <Pressable accessibilityRole="button" accessibilityLabel={props.a11y ?? props.title} onPress={props.onPress}
      style={({ pressed }) => pressed && styles.pressed}>
      {content}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  tabular: { fontVariant: ['tabular-nums'] },
  pressed: { opacity: 0.72, transform: [{ scale: 0.985 }] },
  action: {
    minHeight: ACTION_HEIGHT,
    borderRadius: 22,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: space.l,
    paddingVertical: 10,
  },
  actionSignal: { backgroundColor: color.signal },
  actionTrace: { borderWidth: 2, borderColor: color.system },
  actionQuiet: { borderWidth: 1, borderColor: color.line },
  actionSub: { fontSize: 14, fontWeight: '600', marginTop: 2, opacity: 0.85, fontVariant: ['tabular-nums'] },
  secondary: {
    minHeight: 52,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: color.line,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: space.m,
  },
  icon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    borderWidth: 1,
    borderColor: color.line,
    alignItems: 'center',
    justifyContent: 'center',
  },
  iconGlyph: { color: color.ink2, fontSize: 22, fontWeight: '700', marginTop: -2 },
  rail: { flexDirection: 'row', gap: 4, height: 6, alignItems: 'center' },
  railSeg: { flex: 1, height: 4, borderRadius: 2, backgroundColor: color.line },
  railDone: { backgroundColor: color.ink3 },
  railNow: { height: 6, borderRadius: 3 },
  dial: {
    flex: 1,
    backgroundColor: color.plate,
    borderRadius: 24,
    borderWidth: 1,
    borderColor: color.line,
    paddingTop: 14,
    paddingHorizontal: 12,
    paddingBottom: 12,
    alignItems: 'center',
  },
  dialValueRow: { flexDirection: 'row', alignItems: 'flex-end', minHeight: 84, paddingHorizontal: 4 },
  unit: { color: color.ink2, fontSize: 20, fontWeight: '700', marginBottom: 14, marginLeft: 4 },
  pads: { flexDirection: 'row', gap: 8, alignSelf: 'stretch', marginTop: 6 },
  pad: {
    flex: 1,
    height: 60,
    borderRadius: 18,
    backgroundColor: color.field,
    borderWidth: 1,
    borderColor: color.line,
    alignItems: 'center',
    justifyContent: 'center',
  },
  padPressed: { backgroundColor: color.line },
  padGlyph: { color: color.ink, fontSize: 30, fontWeight: '700', marginTop: -3 },
  sheetIos: { flex: 1, backgroundColor: color.plate },
  sheetBodyIos: { flex: 1, paddingHorizontal: space.gutter, paddingTop: space.m },
  sheetBackdrop: { flex: 1, justifyContent: 'flex-end', backgroundColor: 'rgba(0,0,0,0.55)' },
  sheetBody: {
    maxHeight: '82%',
    backgroundColor: color.plate,
    borderTopLeftRadius: 28,
    borderTopRightRadius: 28,
    paddingHorizontal: space.gutter,
    paddingTop: space.m,
  },
  sheetHead: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: space.s },
  sheetClose: { minHeight: 44, paddingHorizontal: 14 },
  sheetRow: { paddingVertical: 14, borderBottomWidth: StyleSheet.hairlineWidth, borderBottomColor: color.line },
});
