import React, { useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaFrame, useSafeAreaInsets } from 'react-native-safe-area-context';

import { scheme } from '../domain/format';
import type { Mission } from '../domain/types';
import { BodyMapTriptych } from './bodymap/BodyMapTriptych';
import { zoneGridHeight } from './bodymap/triptychLayout';
import { type BodyMapViewPreset, presetForZone } from './bodymap/viewPresets';
import { IconButton, PrimaryAction, Sheet, SheetRow } from './components';
import { color, space, type } from './theme';

const DAY = new Intl.DateTimeFormat('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' });

/**
 * MISSION / READY — « Qu'est-ce que je fais maintenant, et pourquoi ? »
 * One question, one action. The reason is the engine's own words; no duration
 * is shown because none is estimated (AUREN_INSTRUMENTS §6.2bis-3).
 */
export function MissionScreen(props: {
  mission: Mission;
  onStart: (slug: string) => void;
  onOpenLab: () => void;
  onSecondaryOpened: () => void;
  /** today — a fixed day only in a review frame, so its capture does not change every day */
  today?: Date;
}) {
  const insets = useSafeAreaInsets();
  const [why, setWhy] = useState(false);
  const m = props.mission;
  const secondary = m.reason.reasons.filter((r) => r !== m.reason.phrase);
  // the session's BodyMap says WHERE the session works: the subtitle (« Pecs + Delts + Triceps ») and the
  // « On commence par » box step aside for it — one fact, once; the first exercise opens right after « Démarrer »
  const presets = zonePresets(m.zones);
  const withZones = presets.length > 0;

  return (
    <View style={[styles.root, { paddingTop: insets.top + 8, paddingBottom: insets.bottom + 12 }]}>
      <View style={styles.top}>
        <View style={{ width: 44 }} />
        <Text style={type.eyebrow}>AUREN · Aujourd’hui</Text>
        <IconButton icon="more" label="Journal du labo" onPress={props.onOpenLab} />
      </View>
      <Text style={[type.small, styles.date]}>{DAY.format(props.today ?? new Date())}</Text>

      <Text style={styles.name} accessibilityRole="header" maxFontSizeMultiplier={1.3}>
        {m.template.name}
      </Text>
      {m.template.subtitle && !withZones ? <Text style={[type.body, styles.subtitle]}>{m.template.subtitle}</Text> : null}

      <Pressable
        accessibilityRole="button"
        accessibilityLabel={`Pourquoi : ${m.reason.reasons.join(' ')}`}
        accessibilityHint="Ouvre le détail et les autres séances"
        onPress={() => {
          setWhy(true);
          props.onSecondaryOpened();
        }}
        style={styles.reason}
      >
        <Text style={styles.reasonLead}>{m.reason.phrase}</Text>
        {secondary.map((r) => (
          <Text key={r} style={[type.body, styles.reasonMore]}>
            {r}
          </Text>
        ))}
        <Text style={styles.provenance}>
          {m.reason.provenance === 'mesurée' ? 'Mesuré' : 'Lecture partielle'} · {m.reason.horizon}
        </Text>
      </Pressable>

      {withZones ? <MissionZones presets={presets} /> : null}

      <View style={styles.scope}>
        <Figure value={m.scope.exercise_count} label={m.scope.exercise_count > 1 ? 'exercices' : 'exercice'} />
        <Figure value={m.scope.work_set_count} label="séries de travail" />
      </View>

      {withZones ? null : (
        <View style={styles.first}>
          <Text style={type.eyebrow}>On commence par</Text>
          <Text style={[type.bodyStrong, { marginTop: 4, textAlign: 'center' }]}>{m.scope.first_exercise.name}</Text>
          <Text style={[type.small, { marginTop: 2 }]}>{scheme(m.scope.first_exercise.set_scheme)}</Text>
        </View>
      )}

      <View style={{ flex: withZones ? 0 : 1, minHeight: 16 }} />
      <PrimaryAction
        testID="start"
        label="Démarrer"
        hint="Démarre la séance recommandée"
        onPress={() => props.onStart(m.template.slug)}
      />

      <Sheet visible={why} title="Pourquoi cette séance" onClose={() => setWhy(false)}>
        {m.reason.reasons.map((r) => (
          <SheetRow key={r} title={r} />
        ))}
        {m.reason.limiting.length ? (
          <SheetRow title="Ce qui limite" detail={m.reason.limiting.join(' · ')} />
        ) : null}
        <Text style={[type.eyebrow, { marginTop: space.l, marginBottom: 4 }]}>Autres séances possibles</Text>
        {m.alternatives.map((a) => (
          <SheetRow
            key={a.slug}
            title={a.name}
            detail={a.phrase}
            a11y={`Démarrer plutôt ${a.name}`}
            onPress={() => {
              setWhy(false);
              props.onStart(a.slug);
            }}
          />
        ))}
      </Sheet>
    </View>
  );
}

/** The cameras of the zones the session trains (`mission.zones`, derived by the server); unknown zones draw nothing. */
function zonePresets(zones: Mission['zones']): BodyMapViewPreset[] {
  return (zones ?? []).map((z) => presetForZone(z.zone)).filter((p): p is BodyMapViewPreset => p !== undefined);
}

/** Under this, a row of zone windows is no longer read: the panel is not drawn rather than crushed. */
const MIN_ROW = 96;
const ZONES_GAP = 22;

/**
 * The session's BodyMap (`BODYMAP-ZONES-V1`): one camera per zone the session trains, DERIVED from its exercises
 * by the server — never composed here. Equal windows, three per row at most; the panel takes the room the screen
 * leaves (the R1 rule: no unintended void), up to its governed height. Full-bleed, like every window module.
 */
function MissionZones(props: { presets: readonly BodyMapViewPreset[] }) {
  const { width } = useSafeAreaFrame();
  const [room, setRoom] = useState(0);
  const full = zoneGridHeight(props.presets.length);
  const rows = Math.ceil(props.presets.length / 3);
  const height = Math.min(full, Math.floor(room) - ZONES_GAP);
  return (
    <View style={[styles.zonesRoom, { maxHeight: full + ZONES_GAP }]} onLayout={(e) => setRoom(e.nativeEvent.layout.height)}>
      {height >= rows * MIN_ROW ? (
        <View testID="mission-zones" style={styles.zones}>
          <BodyMapTriptych width={width} height={height} presets={props.presets} />
        </View>
      ) : null}
    </View>
  );
}

function Figure(props: { value: number; label: string }) {
  return (
    <View style={{ alignItems: 'center' }} accessible accessibilityLabel={`${props.value} ${props.label}`}>
      <Text style={type.figure} maxFontSizeMultiplier={1.3}>
        {props.value}
      </Text>
      <Text style={[type.eyebrow, { marginTop: 2 }]}>{props.label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: color.field, paddingHorizontal: space.gutter },
  top: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  date: { marginTop: 10, textTransform: 'capitalize', textAlign: 'center' },
  name: { ...type.title, fontSize: 46, lineHeight: 50, marginTop: 22, textAlign: 'center' },
  subtitle: { textAlign: 'center', marginTop: 4 },
  reason: { marginTop: 26, paddingLeft: 14, borderLeftWidth: 3, borderLeftColor: color.system, paddingVertical: 2 },
  reasonLead: { ...type.bodyStrong, fontSize: 21, lineHeight: 27 },
  reasonMore: { marginTop: 6, fontSize: 16, lineHeight: 21 },
  provenance: { ...type.eyebrow, color: color.system, marginTop: 10, letterSpacing: 1 },
  zonesRoom: { flexGrow: 1, flexShrink: 1, flexBasis: 0 },
  zones: { marginHorizontal: -space.gutter, marginTop: 22 },
  scope: { flexDirection: 'row', justifyContent: 'center', gap: 48, marginTop: 24 },
  first: {
    alignItems: 'center',
    marginTop: 26,
    backgroundColor: color.plate,
    borderRadius: 18,
    borderWidth: 1,
    borderColor: color.line,
    padding: 16,
  },
});
