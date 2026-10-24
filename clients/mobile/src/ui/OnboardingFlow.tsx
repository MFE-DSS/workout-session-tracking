import React, { useMemo, useState } from 'react';
import { KeyboardAvoidingView, Platform, Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import Svg, { Circle } from 'react-native-svg';

import { scheme } from '../domain/format';
import type { FamilyKey, OnboardingFamily, OnboardingSession, SessionPlan } from '../domain/types';
import {
  ACTIVITIES,
  Choice,
  emptyProfile,
  EXPERIENCES,
  OBJECTIVES,
  plausible,
  Profile,
  SESSIONS_PER_WEEK,
  SEXES,
  WHY,
} from '../lab/profile';
import { feedback } from '../native/feedback';
import { PrimaryAction, SecondaryButton } from './components';
import { color, space, type } from './theme';

type Step = 'welcome' | 'objective' | 'family' | 'session' | 'profile' | 'proposal';
const ORDER: Step[] = ['welcome', 'objective', 'family', 'session', 'profile', 'proposal'];
const FAMILY_ORDER: FamilyKey[] = ['upper', 'lower', 'full'];

/** The zones a session works (the recap's own rule), the one with the most sets first. */
export function zonesOf(plan: SessionPlan): string[] {
  const sets = new Map<string, number>();
  for (const s of plan.sets) {
    const zone = plan.exercises.find((e) => e.se_id === s.se_id)?.zone;
    if (zone) sets.set(zone.label, (sets.get(zone.label) ?? 0) + 1);
  }
  return [...sets.entries()].sort((a, b) => b[1] - a[1]).map(([label]) => label);
}

function familyZones(f: OnboardingFamily): string[] {
  const seen: string[] = [];
  for (const s of f.sessions) for (const z of zonesOf(s.plan)) if (!seen.includes(z)) seen.push(z);
  return seen;
}

/**
 * D13 — FIRST LAUNCH. One thing to do: choose the first session and do it.
 * objective → family → a real catalogue session, shown by the muscles it works
 * (its name stays small) → profile (all skippable) → the proposed session.
 * The tutorial runs on the first set itself.
 */
export function OnboardingFlow(props: {
  families: Record<FamilyKey, OnboardingFamily>;
  onDone: (profile: Profile) => void;
}) {
  const insets = useSafeAreaInsets();
  const [step, setStep] = useState<Step>('welcome');
  const [profile, setProfile] = useState<Profile>(() => emptyProfile('upper', Date.now()));
  const [familyChosen, setFamilyChosen] = useState(false);
  const go = (s: Step) => {
    feedback.step();
    setStep(s);
  };
  const back = () => setStep(ORDER[Math.max(0, ORDER.indexOf(step) - 1)]);
  const patch = (p: Partial<Profile>) => setProfile((x) => ({ ...x, ...p }));
  const family = props.families[profile.family];
  const chosen = family.sessions.find((s) => s.slug === profile.slug);

  return (
    <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={styles.root}>
      <View style={[styles.frame, { paddingTop: insets.top + 8, paddingBottom: insets.bottom + 12 }]}>
        {step !== 'welcome' ? (
          <View style={styles.top}>
            <Pressable accessibilityRole="button" accessibilityLabel="Retour" hitSlop={10} onPress={back} style={styles.backBtn}>
              <Text style={styles.backGlyph}>‹</Text>
            </Pressable>
            <Dots index={ORDER.indexOf(step) - 1} count={ORDER.length - 1} />
            <View style={{ width: 44 }} />
          </View>
        ) : null}

        {step === 'welcome' && <Welcome onNext={() => go('objective')} />}

        {step === 'objective' && (
          <Page title="Ton objectif" lead="Ce que tu viens chercher en salle.">
            {OBJECTIVES.map((o) => (
              <ChoiceCard key={o.value} choice={o} selected={profile.objective === o.value} onPress={() => {
                patch({ objective: o.value });
                feedback.step();
              }} />
            ))}
            <View style={{ height: space.l }} />
            <PrimaryAction label="Continuer" tone={profile.objective ? 'signal' : 'quiet'} onPress={() => (profile.objective ? go('family') : feedback.refused())} />
          </Page>
        )}

        {step === 'family' && (
          <Page title="Ta première séance" lead="Que veux-tu travailler aujourd’hui ?">
            {FAMILY_ORDER.map((k) => {
              const f = props.families[k];
              const n = f.sessions.length;
              return (
                <ChoiceCard
                  key={k}
                  choice={{ value: k, label: f.label, detail: familyZones(f).slice(0, 5).join(' · ') }}
                  meta={`${n} séance${n > 1 ? 's' : ''} au choix`}
                  selected={familyChosen && profile.family === k}
                  onPress={() => {
                    // a session of another family no longer applies
                    patch({ family: k, slug: k === profile.family ? profile.slug : null });
                    setFamilyChosen(true);
                    feedback.step();
                  }}
                />
              );
            })}
            <View style={{ height: space.l }} />
            <PrimaryAction label="Continuer" tone={familyChosen ? 'signal' : 'quiet'} onPress={() => (familyChosen ? go('session') : feedback.refused())} />
          </Page>
        )}

        {step === 'session' && (
          <Page title={family.label} lead="Choisis ta séance. Ce qu’elle travaille d’abord, son nom ensuite." scroll>
            {family.sessions.map((s) => (
              <ChoiceCard
                key={s.slug}
                choice={{ value: s.slug, label: zonesOf(s.plan).slice(0, 3).join(' · '), detail: s.subtitle ?? undefined }}
                meta={`${s.name} · ${s.plan.exercises.length} exercices · ${s.plan.sets.length} séries`}
                selected={profile.slug === s.slug}
                onPress={() => {
                  patch({ slug: s.slug });
                  feedback.step();
                }}
              />
            ))}
            <View style={{ height: space.l }} />
            <PrimaryAction label="Continuer" tone={chosen ? 'signal' : 'quiet'} onPress={() => (chosen ? go('profile') : feedback.refused())} />
          </Page>
        )}

        {step === 'profile' && <ProfileStep profile={profile} patch={patch} onNext={() => go('proposal')} />}

        {step === 'proposal' && chosen && (
          <Proposal family={family.label} session={chosen} onStart={() => props.onDone({ ...profile, createdAtMs: Date.now() })} />
        )}
      </View>
    </KeyboardAvoidingView>
  );
}

// ── welcome: the promise, in three lines ─────────────────────────────────────

function Welcome(props: { onNext: () => void }) {
  return (
    <View style={styles.center}>
      <View style={{ flex: 1 }} />
      <Mark />
      <Text style={[type.eyebrow, { marginTop: 28, letterSpacing: 4 }]}>AUREN</Text>
      <Text style={[styles.hero, { textAlign: 'center' }]} accessibilityRole="header">Ton cockpit d’entraînement</Text>
      <Text style={[type.body, styles.centerText, { marginTop: 14 }]}>
        Une seule chose à faire : choisir ta première séance, et la faire normalement.
      </Text>
      <View style={styles.promise}>
        <PromiseLine n="1" text="L’IA AUREN lit chacune de tes séries." />
        <PromiseLine n="2" text="Elle prépare ta séance suivante." />
        <PromiseLine n="3" text="Séance après séance, jusqu’à ton plein potentiel." />
      </View>
      <View style={{ flex: 1.2 }} />
      <PrimaryAction label="Choisir ma première séance" onPress={props.onNext} />
    </View>
  );
}

function PromiseLine(props: { n: string; text: string }) {
  return (
    <View style={styles.promiseRow}>
      <View style={styles.promiseDot}>
        <Text style={styles.promiseN}>{props.n}</Text>
      </View>
      <Text style={[type.bodyStrong, { flex: 1 }]}>{props.text}</Text>
    </View>
  );
}

function Mark() {
  return (
    <Svg width={96} height={96} accessibilityElementsHidden importantForAccessibility="no-hide-descendants">
      <Circle cx={48} cy={48} r={44} stroke={color.line} strokeWidth={4} fill="none" />
      <Circle cx={48} cy={48} r={44} stroke={color.signal} strokeWidth={4} fill="none" strokeLinecap="round"
        strokeDasharray={`${2 * Math.PI * 44 * 0.72} 999`} transform="rotate(-90 48 48)" />
      <Circle cx={48} cy={48} r={30} stroke={color.system} strokeWidth={3} fill="none" strokeLinecap="round"
        strokeDasharray={`${2 * Math.PI * 30 * 0.45} 999`} transform="rotate(30 48 48)" />
    </Svg>
  );
}

// ── profile: everything skippable, every field says why ──────────────────────

function ProfileStep(props: { profile: Profile; patch: (p: Partial<Profile>) => void; onNext: () => void }) {
  const p = props.profile;
  const nowYear = new Date().getFullYear();
  return (
    <Page title="Ton profil" lead="Pour que l’IA AUREN parte de toi. Tout est facultatif." scroll>
      <View style={styles.row2}>
        <NumberField label="Taille" unit="cm" why={WHY.height} value={p.heightCm}
          onValue={(v) => props.patch({ heightCm: plausible('heightCm', v, nowYear) })} />
        <NumberField label="Poids" unit="kg" decimal why={WHY.weight} value={p.weightKg}
          onValue={(v) => props.patch({ weightKg: plausible('weightKg', v, nowYear) })} />
      </View>
      <NumberField label="Année de naissance" why={WHY.birthYear} value={p.birthYear}
        onValue={(v) => props.patch({ birthYear: plausible('birthYear', v, nowYear) })} />
      <Chips label="Sexe" why={WHY.sex} choices={SEXES} value={p.sex} onPick={(v) => props.patch({ sex: v })} />
      <Chips label="Tu t’entraînes depuis" why={WHY.experience} choices={EXPERIENCES} value={p.experience} onPick={(v) => props.patch({ experience: v })} />
      <Chips label="Au quotidien" why={WHY.dailyActivity} choices={ACTIVITIES} value={p.dailyActivity} onPick={(v) => props.patch({ dailyActivity: v })} />
      <Chips label="Séances par semaine" why={WHY.sessionsPerWeek}
        choices={SESSIONS_PER_WEEK.map((n) => ({ value: String(n), label: String(n) }))}
        value={p.sessionsPerWeek === null ? null : String(p.sessionsPerWeek)}
        onPick={(v) => props.patch({ sessionsPerWeek: Number(v) })} />
      <Text style={[type.small, { marginTop: space.l, textAlign: 'center' }]}>Dans ce labo, ces données restent sur ce téléphone.</Text>
      <View style={{ height: space.m }} />
      <PrimaryAction label="Continuer" onPress={props.onNext} />
      <SecondaryButton label="Passer pour l’instant" onPress={props.onNext} style={{ marginTop: 10, borderWidth: 0 }} />
    </Page>
  );
}

function NumberField(props: { label: string; unit?: string; why: string; value: number | null; decimal?: boolean; onValue: (v: number | null) => void }) {
  const [text, setText] = useState(props.value === null ? '' : String(props.value).replace('.', ','));
  const commit = () => {
    const n = Number(text.replace(',', '.'));
    props.onValue(text.trim() === '' || Number.isNaN(n) ? null : n);
  };
  const rejected = text.trim() !== '' && props.value === null;
  return (
    <View style={[styles.field, { flex: 1 }]}>
      <Text style={type.eyebrow}>{props.label}</Text>
      <View style={styles.inputRow}>
        <TextInput
          value={text}
          onChangeText={setText}
          onBlur={commit}
          onSubmitEditing={commit}
          keyboardType={props.decimal ? 'decimal-pad' : 'number-pad'}
          returnKeyType="done"
          placeholder="—"
          placeholderTextColor={color.ink3}
          accessibilityLabel={[props.label, props.unit && `en ${props.unit}`].filter(Boolean).join(' ') + `. ${props.why}`}
          style={styles.input}
          selectionColor={color.signal}
        />
        {props.unit ? <Text style={styles.inputUnit}>{props.unit}</Text> : null}
      </View>
      <Text style={[type.small, { marginTop: 4, color: rejected ? color.alert : color.ink3 }]}>{rejected ? 'Valeur non retenue — vérifie-la.' : props.why}</Text>
    </View>
  );
}

function Chips<T extends string>(props: { label: string; why: string; choices: Choice<T>[]; value: T | null; onPick: (v: T) => void }) {
  return (
    <View style={styles.field}>
      <Text style={type.eyebrow}>{props.label}</Text>
      <View style={styles.chips}>
        {props.choices.map((c) => {
          const on = props.value === c.value;
          return (
            <Pressable key={c.value} accessibilityRole="radio" accessibilityState={{ selected: on }} accessibilityLabel={c.label}
              onPress={() => {
                props.onPick(c.value);
                feedback.step();
              }}
              style={({ pressed }) => [styles.chip, on && styles.chipOn, pressed && { opacity: 0.75 }]}>
              <Text style={[styles.chipText, on && { color: color.onSignal }]}>{c.label}</Text>
            </Pressable>
          );
        })}
      </View>
      <Text style={[type.small, { marginTop: 4 }]}>{props.why}</Text>
    </View>
  );
}

// ── the proposed session ─────────────────────────────────────────────────────

function Proposal(props: { family: string; session: OnboardingSession; onStart: () => void }) {
  const f = props.session;
  const first = f.plan.exercises[0];
  const zones = useMemo(() => zonesOf(f.plan), [f]);
  return (
    <View style={styles.center}>
      <View style={{ flex: 0.6 }} />
      <Text style={type.eyebrow}>{`Ta première séance · ${props.family}`}</Text>
      <Text style={[styles.hero, { fontSize: 48, lineHeight: 52, textAlign: 'center' }]} accessibilityRole="header">{f.name}</Text>
      {f.subtitle ? <Text style={[type.body, styles.centerText]}>{f.subtitle}</Text> : null}
      <View style={styles.figures}>
        <Figure value={f.plan.exercises.length} label="exercices" />
        <View style={styles.figureSep} />
        <Figure value={f.plan.sets.length} label="séries" />
      </View>
      <View style={styles.zoneWrap}>
        {zones.map((z) => (
          <View key={z} style={styles.zone}>
            <Text style={styles.zoneText}>{z}</Text>
          </View>
        ))}
      </View>
      <View style={styles.firstCard}>
        <Text style={type.eyebrow}>On commence par</Text>
        <Text style={[type.bodyStrong, { marginTop: 4, textAlign: 'center' }]}>{first.executed_name}</Text>
        <Text style={[type.small, { marginTop: 2 }]}>{scheme(first.set_scheme)}</Text>
      </View>
      <View style={{ flex: 1 }} />
      <PrimaryAction label="C’est parti" sublabel="Un court guide s’affiche sur la première série" onPress={props.onStart} />
    </View>
  );
}

function Figure(props: { value: number; label: string }) {
  return (
    <View style={{ alignItems: 'center' }} accessible accessibilityLabel={`${props.value} ${props.label}`}>
      <Text style={type.figure}>{props.value}</Text>
      <Text style={type.eyebrow}>{props.label}</Text>
    </View>
  );
}

// ── building blocks ──────────────────────────────────────────────────────────

function Page(props: { title: string; lead: string; children: React.ReactNode; scroll?: boolean }) {
  const body = (
    <>
      <Text style={[styles.hero, { fontSize: 34, lineHeight: 38, textAlign: 'center', marginTop: space.m }]} accessibilityRole="header">{props.title}</Text>
      <Text style={[type.body, styles.centerText, { marginBottom: space.l }]}>{props.lead}</Text>
      {props.children}
    </>
  );
  return props.scroll ? (
    <ScrollView keyboardShouldPersistTaps="handled" contentContainerStyle={{ paddingBottom: space.l }} showsVerticalScrollIndicator={false}>{body}</ScrollView>
  ) : (
    <View style={{ flex: 1 }}>{body}</View>
  );
}

function ChoiceCard<T extends string>(props: { choice: Choice<T>; selected: boolean; onPress: () => void; meta?: string }) {
  return (
    <Pressable
      accessibilityRole="radio"
      accessibilityState={{ selected: props.selected }}
      accessibilityLabel={[props.choice.label, props.choice.detail, props.meta].filter(Boolean).join('. ')}
      onPress={props.onPress}
      style={({ pressed }) => [styles.card, props.selected && styles.cardOn, pressed && { opacity: 0.8 }]}
    >
      <View style={{ flex: 1 }}>
        <Text style={[type.bodyStrong, { fontSize: 19 }]}>{props.choice.label}</Text>
        {props.choice.detail ? <Text style={[type.small, { marginTop: 3, color: color.ink2 }]}>{props.choice.detail}</Text> : null}
        {props.meta ? <Text style={[type.eyebrow, { marginTop: 6, color: color.system }]}>{props.meta}</Text> : null}
      </View>
      <View style={[styles.radio, props.selected && styles.radioOn]}>{props.selected ? <View style={styles.radioDot} /> : null}</View>
    </Pressable>
  );
}

function Dots(props: { index: number; count: number }) {
  return (
    <View style={styles.dots} accessible accessibilityLabel={`Étape ${props.index + 1} sur ${props.count}`}>
      {Array.from({ length: props.count }, (_, i) => (
        <View key={i} style={[styles.dot, i <= props.index && styles.dotOn]} />
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: color.field },
  frame: { flex: 1, paddingHorizontal: space.gutter },
  top: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  backBtn: { width: 44, height: 44, alignItems: 'center', justifyContent: 'center' },
  backGlyph: { color: color.ink2, fontSize: 34, fontWeight: '600', marginTop: -4 },
  dots: { flexDirection: 'row', gap: 6 },
  dot: { width: 22, height: 4, borderRadius: 2, backgroundColor: color.line },
  dotOn: { backgroundColor: color.signal },
  center: { flex: 1, alignItems: 'center' },
  centerText: { textAlign: 'center', marginTop: 6 },
  hero: { ...type.title, fontSize: 38, lineHeight: 42, marginTop: 8 },
  promise: { alignSelf: 'stretch', marginTop: 30, gap: 14 },
  promiseRow: { flexDirection: 'row', alignItems: 'center', gap: 14, backgroundColor: color.plate, borderRadius: 18, borderWidth: 1, borderColor: color.line, padding: 14 },
  promiseDot: { width: 30, height: 30, borderRadius: 15, borderWidth: 2, borderColor: color.system, alignItems: 'center', justifyContent: 'center' },
  promiseN: { color: color.system, fontWeight: '800', fontSize: 14 },
  card: { flexDirection: 'row', alignItems: 'center', gap: 12, backgroundColor: color.plate, borderRadius: 20, borderWidth: 1, borderColor: color.line, padding: 16, marginBottom: 10, minHeight: 72 },
  cardOn: { borderColor: color.signal, borderWidth: 2 },
  radio: { width: 26, height: 26, borderRadius: 13, borderWidth: 2, borderColor: color.ink3, alignItems: 'center', justifyContent: 'center' },
  radioOn: { borderColor: color.signal },
  radioDot: { width: 12, height: 12, borderRadius: 6, backgroundColor: color.signal },
  row2: { flexDirection: 'row', gap: 12 },
  field: { marginTop: space.m },
  inputRow: { flexDirection: 'row', alignItems: 'center', marginTop: 6, backgroundColor: color.plate, borderRadius: 16, borderWidth: 1, borderColor: color.line, paddingHorizontal: 14, minHeight: 56 },
  input: { flex: 1, minWidth: 0, width: '100%', color: color.ink, fontSize: 24, fontWeight: '800', fontVariant: ['tabular-nums'], paddingVertical: 10 },
  inputUnit: { color: color.ink2, fontSize: 16, fontWeight: '700', marginLeft: 6, flexShrink: 0 },
  chips: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginTop: 6 },
  chip: { minHeight: 44, minWidth: 56, alignItems: 'center', borderRadius: 22, borderWidth: 1, borderColor: color.line, backgroundColor: color.plate, paddingHorizontal: 16, justifyContent: 'center' },
  chipOn: { backgroundColor: color.signal, borderColor: color.signal },
  chipText: { color: color.ink, fontSize: 15, fontWeight: '700' },
  figures: { flexDirection: 'row', alignItems: 'center', gap: 28, marginTop: 26 },
  figureSep: { width: 1, height: 40, backgroundColor: color.line },
  zoneWrap: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'center', gap: 8, marginTop: 22 },
  zone: { borderRadius: 14, borderWidth: 1, borderColor: color.lineRest, backgroundColor: color.plateRest, paddingHorizontal: 12, paddingVertical: 6 },
  zoneText: { color: color.system, fontSize: 14, fontWeight: '700' },
  firstCard: { alignSelf: 'stretch', alignItems: 'center', marginTop: 24, backgroundColor: color.plate, borderRadius: 18, borderWidth: 1, borderColor: color.line, padding: 16 },
});
