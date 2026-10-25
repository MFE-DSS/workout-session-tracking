import React, { useEffect, useMemo, useRef } from 'react';
import { ScrollView, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { DoneSession, sessionsThisWeek, weeksHeld } from '../domain/adherence';
import { elapsedLabel, kg } from '../domain/format';
import { ExerciseResult, headline, LineReading, lineReading, SessionPerformance, Trend } from '../domain/performance';
import type { Mission } from '../domain/types';
import type { WorkoutState } from '../domain/workout';
import { DEFAULT_SESSIONS_PER_WEEK } from '../lab/profile';
import { feedback } from '../native/feedback';
import { IconButton, PrimaryAction } from './components';
import { color, space, type } from './theme';

const TIME = new Intl.DateTimeFormat('fr-FR', { hour: '2-digit', minute: '2-digit' });

/** Sets per zone, from the sets DONE on this device, by the server recap's own rule. */
export function zonesDone(state: WorkoutState): { label: string; sets: number }[] {
  const plan = state.plan!;
  const counts = new Map<string, number>();
  for (const s of plan.sets) {
    if (!state.done[s.set_id]) continue;
    const zone = plan.exercises.find((e) => e.se_id === s.se_id)?.zone;
    if (zone) counts.set(zone.label, (counts.get(zone.label) ?? 0) + 1);
  }
  return [...counts.entries()].map(([label, sets]) => ({ label, sets })).sort((a, b) => b.sets - a.sets || a.label.localeCompare(b.label));
}

const TREND: Record<Trend, { glyph: string; word: string; tone: string }> = {
  up: { glyph: '↑', word: 'en progrès', tone: color.signal },
  held: { glyph: '=', word: 'tenu', tone: color.ink2 },
  down: { glyph: '↓', word: 'en retrait', tone: color.ink3 },
  first: { glyph: '•', word: 'premier repère', tone: color.system },
};

/**
 * SESSION COMPLETE — engine V2, ruling 11: no single score. What the session
 * showed (performance, each exercise against comparable personal history),
 * then adherence to the agreed programme, where planned rest counts.
 */
export function CompleteScreen(props: {
  state: WorkoutState;
  performance: SessionPerformance;
  /**
   * sessions done BEFORE this one (this one is added here). `null` = not known
   * on this device (D9: the history lives on the server and no read model
   * carries it yet) — the programme card is then omitted, never shown as 1/N.
   */
  history: DoneSession[] | null;
  sessionsPerWeek: number | null;
  next: Mission | null;
  reducedMotion: boolean;
  onClose: () => void;
  onOpenLab: () => void;
}) {
  const insets = useSafeAreaInsets();
  const { state, performance: perf } = props;
  const plan = state.plan!;
  const started = state.startedMs ?? 0;
  const ended = state.completedMs ?? started;
  const pending = Object.values(state.done).filter((d) => d.local !== 'saved_local').length;

  const after = useMemo(() => [...(props.history ?? []), { atMs: ended, slug: plan.template_slug }], [props.history, ended, plan.template_slug]);
  const target = props.sessionsPerWeek ?? DEFAULT_SESSIONS_PER_WEEK;
  const week = sessionsThisWeek(after, ended);
  const held = weeksHeld(after, ended, target);
  const zones = zonesDone(state);
  const worked = perf.exercises.filter((e) => e.top);

  const rewarded = useRef(false);
  useEffect(() => {
    if (rewarded.current) return;
    rewarded.current = true;
    const t = setTimeout(() => (perf.records.length ? feedback.reward() : feedback.setSaved()), props.reducedMotion ? 0 : 500);
    return () => clearTimeout(t);
  }, [perf.records.length, props.reducedMotion]);

  return (
    <View style={[styles.root, { paddingTop: insets.top + 8 }]}>
      <View style={styles.top}>
        <Text style={type.eyebrow}>Séance terminée</Text>
        <IconButton glyph="⋯" label="Journal du labo" onPress={props.onOpenLab} />
      </View>
      <ScrollView contentContainerStyle={{ paddingBottom: insets.bottom + 24 }} showsVerticalScrollIndicator={false}>
        <View style={styles.mark} accessibilityElementsHidden>
          <Text style={styles.markGlyph}>✓</Text>
        </View>
        <Text style={styles.name} accessibilityRole="header">{plan.template_name.split(' — ')[0]}</Text>
        <Text style={[type.small, type.tabular, styles.centered]}>
          {`${TIME.format(new Date(started))} → ${TIME.format(new Date(ended))} · ${elapsedLabel(started, ended)}`}
        </Text>
        <Text style={styles.headline} accessibilityLiveRegion="polite">{headline(perf)}</Text>

        {perf.records.length ? (
          <View style={styles.card}>
            <Text style={[type.eyebrow, { color: color.signal }]}>Records</Text>
            {perf.records.map((e) => (
              <RecordRow key={e.se_id} e={e} />
            ))}
          </View>
        ) : null}

        <View style={styles.card}>
          <Text style={type.eyebrow}>Ce que tu as fait — comparé à toi-même</Text>
          {worked.map((e) => (
            <ExerciseRow key={e.se_id} e={e} />
          ))}
          <Text style={[type.small, { marginTop: 8 }]}>{`${perf.setsDone} séries sur ${perf.setsPlanned} prévues`}</Text>
        </View>

        {props.history === null ? null : (
        <View style={styles.card} accessible accessibilityLabel={`Programme de la semaine : ${week} séances sur ${target}. ${held} semaines tenues.`}>
          <Text style={type.eyebrow}>Ton programme</Text>
          <View style={styles.pair}>
            <View style={{ flex: 1 }}>
              <Text style={styles.big}>
                {Math.min(week, target)}
                <Text style={[type.body, { fontSize: 20 }]}>{` / ${target}`}</Text>
              </Text>
              <Text style={type.small}>{`séances prévues cette semaine${props.sessionsPerWeek === null ? ' (par défaut)' : ''}`}</Text>
            </View>
            <View style={{ flex: 1 }}>
              <Text style={styles.big}>{held}</Text>
              <Text style={type.small}>{held > 1 ? 'semaines tenues' : 'semaine tenue'}</Text>
            </View>
          </View>
          <Text style={[type.small, { marginTop: 8 }]}>Le repos prévu fait partie du programme : il ne casse rien.</Text>
        </View>
        )}

        {zones.length ? (
          <View style={styles.card}>
            <Text style={type.eyebrow}>Séries par zone</Text>
            <View style={styles.zones}>
              {zones.map((z) => (
                <View key={z.label} style={styles.zone}>
                  <Text style={styles.zoneText}>{z.label}</Text>
                  <Text style={[styles.zoneText, type.tabular, { color: color.ink }]}>{z.sets}</Text>
                </View>
              ))}
            </View>
          </View>
        ) : null}

        <View style={styles.ledger}>
          <Ledger label="Sur l’appareil" value={pending ? `${perf.setsDone - pending} / ${perf.setsDone}` : 'toutes'} alert={pending > 0} />
          <Ledger label="Remplacements" value={String(Object.keys(state.requiresSync).length)} />
        </View>

        {props.next ? (
          <View style={[styles.card, styles.next]}>
            <Text style={[type.eyebrow, { color: color.system }]}>L’IA AUREN a préparé ta prochaine séance</Text>
            <Text style={[type.bodyStrong, { fontSize: 22, marginTop: 6 }]}>{props.next.template.name}</Text>
            <Text style={[type.small, { marginTop: 4 }]}>{props.next.reason.phrase}</Text>
          </View>
        ) : null}

        <View style={{ height: space.l }} />
        <PrimaryAction label={props.next ? 'Voir ma prochaine séance' : 'Fermer'} onPress={props.onClose} />
      </ScrollView>
    </View>
  );
}

// R13 — the line's reading against the prescription: a mark AND a word, never colour alone
const READING: Record<LineReading, { mark: string; word: string; tone: string } | null> = {
  above: { mark: '▲', word: 'au-dessus de la cible', tone: color.perfAbove },
  on: { mark: '●', word: 'conforme', tone: color.ink2 },
  below: { mark: '▼', word: 'en dessous de la cible', tone: color.perfBelow },
  first: { mark: '◆', word: 'repère posé', tone: color.ink3 },
  free: null,
};

function ExerciseRow(props: { e: ExerciseResult }) {
  const { e } = props;
  const top = e.top!;
  const t = TREND[e.trend ?? 'first'];
  const before = e.previousTop ? `avant ${kg(e.previousTop.weight)} × ${e.previousTop.reps}` : t.word;
  const reading = READING[lineReading(e)];
  return (
    <View
      style={[styles.row, reading && { borderLeftWidth: 3, borderLeftColor: reading.tone, paddingLeft: 10 }]}
      accessible
      accessibilityLabel={`${e.name} : ${kg(top.weight)} kilos, ${top.reps} reps, ${t.word}${reading ? `, ${reading.word}` : ''}`}
    >
      <Text style={[styles.trend, { color: t.tone }]}>{t.glyph}</Text>
      <View style={{ flex: 1 }}>
        <Text style={type.bodyStrong} numberOfLines={2}>{e.name}</Text>
        {reading ? (
          <Text style={[type.small, { color: reading.tone, marginTop: 2 }]}>{`${reading.mark} ${reading.word}`}</Text>
        ) : null}
      </View>
      <View style={{ alignItems: 'flex-end' }}>
        <Text style={[type.bodyStrong, type.tabular]}>{`${kg(top.weight)} kg × ${top.reps}`}</Text>
        <Text style={type.small}>{e.replaced ? 'sur remplaçant' : before}</Text>
      </View>
    </View>
  );
}

function RecordRow(props: { e: ExerciseResult }) {
  const { e } = props;
  const top = e.top!;
  const was = e.previousBest ? `avant ${kg(e.previousBest.weight)} × ${e.previousBest.reps}` : '';
  return (
    <View style={styles.row} accessible accessibilityLabel={`Record : ${e.name}, ${kg(top.weight)} kilos, ${top.reps} reps, ${was}`}>
      <Text style={[type.bodyStrong, { flex: 1 }]} numberOfLines={2}>{e.name}</Text>
      <View style={{ alignItems: 'flex-end' }}>
        <Text style={[type.bodyStrong, type.tabular, { color: color.signal }]}>{`${kg(top.weight)} kg × ${top.reps}`}</Text>
        <Text style={type.small}>{was}</Text>
      </View>
    </View>
  );
}

function Ledger(props: { label: string; value: string; alert?: boolean }) {
  return (
    <View style={{ alignItems: 'center', flex: 1 }} accessible accessibilityLabel={`${props.label} : ${props.value}`}>
      <Text style={[type.bodyStrong, type.tabular, { fontSize: 20 }, props.alert && { color: color.alert }]}>{props.value}</Text>
      <Text style={[type.eyebrow, { fontSize: 10, marginTop: 2 }]}>{props.label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: color.field, paddingHorizontal: space.gutter },
  top: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  mark: { alignSelf: 'center', marginTop: 12, width: 64, height: 64, borderRadius: 32, borderWidth: 3, borderColor: color.ink, alignItems: 'center', justifyContent: 'center' },
  markGlyph: { color: color.ink, fontSize: 30, fontWeight: '800' },
  centered: { textAlign: 'center', marginTop: 4 },
  name: { ...type.title, textAlign: 'center', marginTop: 12 },
  headline: { ...type.bodyStrong, fontSize: 21, lineHeight: 27, textAlign: 'center', marginTop: 14 },
  card: { backgroundColor: color.plate, borderRadius: 20, borderWidth: 1, borderColor: color.line, padding: 16, marginTop: 14 },
  row: { flexDirection: 'row', alignItems: 'center', gap: 10, paddingVertical: 10, borderBottomWidth: StyleSheet.hairlineWidth, borderBottomColor: color.line },
  trend: { width: 18, fontSize: 18, fontWeight: '800', textAlign: 'center' },
  pair: { flexDirection: 'row', gap: 12, marginTop: 6 },
  big: { fontSize: 36, fontWeight: '800', color: color.ink, fontVariant: ['tabular-nums'] },
  zones: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginTop: 10 },
  zone: { flexDirection: 'row', gap: 8, borderRadius: 14, borderWidth: 1, borderColor: color.lineRest, backgroundColor: color.plateRest, paddingHorizontal: 12, paddingVertical: 6 },
  zoneText: { color: color.system, fontSize: 14, fontWeight: '700' },
  ledger: { flexDirection: 'row', marginTop: 18, paddingVertical: 12, borderTopWidth: StyleSheet.hairlineWidth, borderBottomWidth: StyleSheet.hairlineWidth, borderColor: color.line },
  next: { borderColor: color.lineRest, backgroundColor: color.plateRest },
});
