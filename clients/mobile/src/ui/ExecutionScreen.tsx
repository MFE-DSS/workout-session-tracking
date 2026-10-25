import React, { useEffect, useRef, useState } from 'react';
import { Animated, Easing, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { frenchSummary, kg, scheme } from '../domain/format';
import { formatClock, remainingFraction, remainingMs } from '../domain/timer';
import type { PlanExercise, SubstituteLevel } from '../domain/types';
import {
  canValidate,
  currentExercise,
  DoneSet,
  Draft,
  draftFor,
  exerciseById,
  progress,
  restSecondsFor,
  setById,
  setsOf,
  WorkoutState,
} from '../domain/workout';
import {
  ExerciseRail,
  IconButton,
  PrimaryAction,
  RestRing,
  SecondaryButton,
  Sheet,
  SheetRow,
  ValueDial,
} from './components';
import { color, NUMERAL_FONT_SCALE_CAP, space, type } from './theme';

export type ExecutionHandlers = {
  onAdjust: (setId: number, field: keyof Draft, delta: number) => void;
  onSetValue: (setId: number, field: keyof Draft, value: number | null) => void;
  onValidatePressIn: () => void;
  onValidate: (setId: number) => void;
  onShift: (deltaMs: number) => void;
  onSkip: () => void;
  onRequestSubstitute: (seId: number, name: string) => void;
  onOpenLab: () => void;
  onRestPainted: () => void;
  /** Lab evidence: a secondary sheet is a navigation decision (target: none on the nominal path). */
  onSecondaryOpened: () => void;
  /** R16 — the ONE workout-level secondary action: leave the session (D9 connected app). */
  onExitRequested?: () => void;
  /** D9 — a quiet secondary state (offline, to check). `null` on the nominal path. */
  statusNote?: { text: string; alert: boolean } | null;
  /**
   * D9 §8.7 — what the SERVER says of a set: acknowledged, refused, or nothing yet
   * (still « enregistrée sur l'appareil »). Absent in the lab, which has no server.
   */
  serverStateOf?: (setId: number) => 'synced' | 'refused' | null;
  /** R10 — leave the current set undone (nothing is written). */
  onSkipSet?: (setId: number) => void;
  /** R12 — leave the rest of the current exercise undone. */
  onSkipExercise?: () => void;
  /** R10 / R12 — a few seconds to take a skip back. `null` otherwise. */
  undo?: { text: string; onUndo: () => void } | null;
};

/**
 * EXECUTION — one training instrument, its composition changing with state:
 * CURRENT_SET → REST → CURRENT_SET → REST (next exercise) → … No tab bar, no
 * dashboard, no navigation decision on the nominal path.
 */
export function ExecutionScreen(props: { state: WorkoutState; nowMs: number; reducedMotion: boolean } & ExecutionHandlers) {
  const insets = useSafeAreaInsets();
  const { state } = props;
  const plan = state.plan!;
  const resting = state.phase === 'REST' && state.rest !== null;
  const { exerciseIndex, exerciseCount } = progress(state);
  const [menu, setMenu] = useState(false);
  const [swapFor, setSwapFor] = useState<number | null>(null);
  const [edit, setEdit] = useState<{ setId: number; field: keyof Draft } | null>(null);

  // the composition fades in on every state change — cut entirely under Reduce motion
  const appear = useRef(new Animated.Value(1)).current;
  const key = `${state.phase}-${state.cursorSetId}`;
  useEffect(() => {
    if (props.reducedMotion) {
      appear.setValue(1);
      return;
    }
    appear.setValue(0);
    Animated.timing(appear, { toValue: 1, duration: 240, easing: Easing.out(Easing.cubic), useNativeDriver: true }).start();
  }, [key, props.reducedMotion, appear]);
  const shiftY = appear.interpolate({ inputRange: [0, 1], outputRange: [10, 0] });

  const restingFrom = resting ? setById(plan, state.rest!.fromSetId) : undefined;
  const exercise = resting ? exerciseById(plan, restingFrom!.se_id)! : currentExercise(state)!;

  return (
    <View style={[styles.root, resting && styles.rootRest, { paddingTop: insets.top + 10, paddingBottom: insets.bottom + 12 }]}>
      <ExerciseRail count={exerciseCount} index={exerciseIndex} resting={resting} />
      <View style={styles.head}>
        {props.onExitRequested ? (
          <IconButton
            glyph="✕"
            label="Quitter la séance"
            onPress={() => {
              props.onExitRequested?.();
              props.onSecondaryOpened();
            }}
          />
        ) : null}
        <Text style={[type.eyebrow, props.onExitRequested && styles.headCentered]} numberOfLines={1}>
          {`Exercice ${exerciseIndex + 1} / ${exerciseCount}${resting ? ' · repos' : ''}`}
        </Text>
        <IconButton
          glyph="⋯"
          label="Options de l’exercice"
          onPress={() => {
            setMenu(true);
            props.onSecondaryOpened();
          }}
        />
      </View>
      {props.statusNote ? (
        <Text
          style={[styles.status, props.statusNote.alert && { color: color.alert }]}
          accessibilityLiveRegion="polite"
          numberOfLines={1}
        >
          {props.statusNote.text}
        </Text>
      ) : null}
      {props.undo ? (
        <View style={styles.undo} accessibilityLiveRegion="polite">
          <Text style={[type.small, { flex: 1, color: color.ink2 }]}>{props.undo.text}</Text>
          <SecondaryButton label="Annuler" onPress={props.undo.onUndo} style={styles.undoButton} />
        </View>
      ) : null}

      <Animated.View style={[styles.body, { opacity: appear, transform: [{ translateY: shiftY }] }]}>
        {resting ? (
          <RestBody
            {...props}
            exercise={exercise}
            onSwap={(seId) => {
              setSwapFor(seId);
              props.onSecondaryOpened();
            }}
          />
        ) : (
          <SetBody
            {...props}
            exercise={exercise}
            onEdit={(setId, field) => setEdit({ setId, field })}
            onSwap={(seId) => {
              setSwapFor(seId);
              props.onSecondaryOpened();
            }}
          />
        )}
      </Animated.View>

      {/* R8 — the ⋯ holds the EXERCISE gestures; replacing has its own icon (⇄) next to the name */}
      <Sheet visible={menu} title={exercise.executed_name} onClose={() => setMenu(false)}>
        {props.onSkipExercise && !resting ? (
          <SheetRow
            title="Passer cet exercice"
            detail="Ses séries restantes ne seront pas comptées. Tu pourras annuler quelques secondes."
            onPress={() => {
              setMenu(false);
              props.onSkipExercise?.();
            }}
          />
        ) : null}
        {/* R9 — the journal is instrumentation: development builds only, in the connected app */}
        {!props.onExitRequested || __DEV__ ? (
          <SheetRow
            title={props.onExitRequested ? 'Journal de l’appareil' : 'Journal local du labo'}
            detail={props.onExitRequested
              ? 'Diagnostic : ce qui est enregistré ici, ce qui est déjà sur AUREN, ce qui attend la connexion.'
              : 'Séries enregistrées sur l’appareil, commandes en attente, mesures.'}
            onPress={() => {
              setMenu(false);
              props.onOpenLab();
            }}
          />
        ) : null}
      </Sheet>

      <SwapSheet
        locked={swapFor !== null && setsOf(plan, swapFor).some((s) => state.done[s.set_id])}
        exercise={swapFor === null ? null : exerciseById(plan, swapFor) ?? null}
        onClose={() => setSwapFor(null)}
        onPick={(name) => {
          if (swapFor !== null) props.onRequestSubstitute(swapFor, name);
          setSwapFor(null);
        }}
      />
      <EntrySheet state={state} edit={edit} onClose={() => setEdit(null)} onSetValue={props.onSetValue} />
    </View>
  );
}

// ── CURRENT_SET ──────────────────────────────────────────────────────────────

function chipLabel(done: DoneSet | undefined, skipped: boolean, current: boolean): string {
  if (done) return `✓ ${kg(done.weight)}×${done.reps}`;
  if (skipped) return '— passée';
  return current ? '● en cours' : '○';
}

function chipA11y(index: number, done: DoneSet | undefined, skipped: boolean, current: boolean): string {
  if (done) return `série ${index} faite, ${kg(done.weight)} kilos, ${done.reps} reps`;
  if (skipped) return `série ${index} passée`;
  return current ? `série ${index} en cours` : `série ${index} à venir`;
}

function SetBody(props: {
  state: WorkoutState;
  exercise: PlanExercise;
  onEdit: (setId: number, field: keyof Draft) => void;
  onSwap: (seId: number) => void;
} & ExecutionHandlers) {
  const { state, exercise } = props;
  const setId = state.cursorSetId!;
  const set = setById(state.plan!, setId)!;
  const sets = setsOf(state.plan!, exercise.se_id);
  const draft = draftFor(state, setId);
  const valid = canValidate(draft);
  const pending = state.requiresSync[exercise.se_id];
  const skipped = state.skipped ?? {};

  return (
    <View style={{ flex: 1 }}>
      <View style={styles.nameRow}>
        <Text style={[type.exercise, { flex: 1 }]} accessibilityRole="header" maxFontSizeMultiplier={1.3}>
          {exercise.executed_name}
        </Text>
        {/* R8 — replacing is one tap away at every set, never hidden in the ⋯ */}
        <IconButton glyph="⇄" label="Remplacer cet exercice" onPress={() => props.onSwap(exercise.se_id)} />
      </View>
      <Text style={[type.body, styles.setLine]}>
        <Text style={type.bodyStrong}>{`Série ${set.index} sur ${sets.length}`}</Text>
        {exercise.rep_range ? `  ·  objectif ${exercise.rep_range.min}–${exercise.rep_range.max} reps` : ''}
      </Text>

      <View
        style={styles.chips}
        accessible
        accessibilityLabel={sets.map((s) => chipA11y(s.index, state.done[s.set_id], Boolean(skipped[s.set_id]), s.set_id === setId)).join(', ')}
      >
        {sets.map((s) => {
          const now = s.set_id === setId;
          return (
            <View key={s.set_id} style={[styles.chip, now && styles.chipNow]}>
              <Text style={styles.chipIndex}>{`S${s.index}`}</Text>
              <Text style={[styles.chipValue, now && { color: color.ink }]} numberOfLines={1}>
                {chipLabel(state.done[s.set_id], Boolean(skipped[s.set_id]), now)}
              </Text>
            </View>
          );
        })}
      </View>

      <Guidance exercise={exercise} />
      {pending ? (
        <Text style={styles.requiresSync}>{`Remplacement demandé : ${pending.substitute} — en attente de validation par AUREN`}</Text>
      ) : null}

      <View style={{ flex: 1, minHeight: 8 }} />
      <View style={styles.dials}>
        <ValueDial
          testID="dial-weight"
          label="Charge"
          value={kg(draft.weight)}
          unit="kg"
          stepLabel="2,5 kilos"
          onMinus={() => props.onAdjust(setId, 'weight', -1)}
          onPlus={() => props.onAdjust(setId, 'weight', 1)}
          onEdit={() => props.onEdit(setId, 'weight')}
        />
        <ValueDial
          testID="dial-reps"
          label="Reps"
          value={draft.reps === null ? '—' : String(draft.reps)}
          stepLabel="une rep"
          onMinus={() => props.onAdjust(setId, 'reps', -1)}
          onPlus={() => props.onAdjust(setId, 'reps', 1)}
          onEdit={() => props.onEdit(setId, 'reps')}
        />
      </View>
      <View style={{ height: 14 }} />
      {valid ? (
        <PrimaryAction
          testID="validate"
          label="Valider la série"
          sublabel={`${kg(draft.weight)} kg × ${draft.reps}`}
          onPressIn={props.onValidatePressIn}
          onPress={() => props.onValidate(setId)}
        />
      ) : (
        <PrimaryAction
          testID="validate"
          tone="quiet"
          label={draft.weight === null ? 'Indique la charge' : 'Indique les reps'}
          hint="Touche la valeur pour la saisir"
          onPress={() => {
            props.onValidate(setId);
            props.onEdit(setId, draft.weight === null ? 'weight' : 'reps');
          }}
        />
      )}
      {props.onSkipSet ? (
        // R10 — secondary, grey, set apart from « Valider » so the thumb does not hit it by accident
        <Pressable
          accessibilityRole="button"
          accessibilityLabel={`Passer la série ${set.index}`}
          accessibilityHint="La série ne sera pas comptée. Tu pourras annuler quelques secondes."
          hitSlop={8}
          onPress={() => props.onSkipSet?.(setId)}
          style={({ pressed }) => [styles.skip, pressed && { opacity: 0.6 }]}
        >
          <Text style={styles.skipText}>Passer cette série</Text>
        </Pressable>
      ) : null}
    </View>
  );
}

function Guidance(props: { exercise: PlanExercise }) {
  const g = props.exercise.guidance;
  const prev = props.exercise.previous;
  return (
    <View style={styles.guidance}>
      {g && !g.is_silent ? (
        <>
          <Text style={styles.guideLead}>{g.intent_label}</Text>
          {g.target_summary ? <Text style={styles.guideTarget}>{frenchSummary(g.target_summary)}</Text> : null}
          {g.reasons[1] ? <Text style={[type.small, { marginTop: 3 }]}>{g.reasons[1]}</Text> : null}
        </>
      ) : (
        <Text style={[type.body, { color: color.ink2 }]}>{g?.intent_label ?? 'Pas encore de référence'}</Text>
      )}
      {/* R6 — a first time is not a gap: it is where the reference is set */}
      {!prev && (!g || g.is_silent) ? (
        <Text style={[type.small, { marginTop: 4 }]}>Première fois : la charge que tu valides devient ta référence.</Text>
      ) : null}
      {prev ? <Text style={[type.small, { marginTop: 8 }]}>{`La dernière fois · ${prev.relative} · ${previousLine(prev)}`}</Text> : null}
    </View>
  );
}

function previousLine(prev: { weights: string; reps: string }): string {
  const weights = prev.weights.split(' / ');
  const reps = prev.reps.split(' / ').join(' · ');
  const same = weights.every((w) => w === weights[0]);
  const w = same ? `${frenchSummary(weights[0])} kg` : weights.map(frenchSummary).join(' / ');
  return `${w} × ${reps}`;
}

// ── REST (same instrument, other state) ──────────────────────────────────────

function RestBody(props: { state: WorkoutState; nowMs: number; exercise: PlanExercise; onSwap: (seId: number) => void } & ExecutionHandlers) {
  const { state, nowMs } = props;
  const rest = state.rest!;
  const plan = state.plan!;
  const from = setById(plan, rest.fromSetId)!;
  const done = state.done[rest.fromSetId];
  const toNewExercise = rest.after.kind === 'REST_THEN_EXERCISE';
  const nextSetId = rest.after.kind === 'BILAN' ? null : rest.after.set_id;
  const nextSet = nextSetId !== null ? setById(plan, nextSetId) : undefined;
  const nextEx = nextSet ? exerciseById(plan, nextSet.se_id) : undefined;
  const nextDraft = nextSetId !== null ? draftFor(state, nextSetId) : null;
  const left = remainingMs(rest, nowMs);
  const planned = restSecondsFor(plan, from.se_id);
  const shifted = rest.deadlineMs - rest.startedMs !== planned * 1000;

  const server = props.serverStateOf?.(rest.fromSetId) ?? null;
  const alert = done?.local === 'not_saved' || server === 'refused';
  let saved = 'enregistrement…';
  if (done?.local === 'not_saved') saved = 'NON enregistrée — réessaie depuis le journal';
  else if (server === 'refused') saved = 'refusée par AUREN — gardée sur l’appareil';
  else if (server === 'synced') saved = 'enregistrée sur AUREN';
  else if (done?.local === 'saved_local') saved = 'enregistrée sur l’appareil';

  return (
    <View style={{ flex: 1 }} onLayout={props.onRestPainted}>
      <View style={styles.savedRow} accessible accessibilityLabel={`Série ${from.index} ${saved}`}>
        <View style={[styles.tick, alert && { borderColor: color.alert }]}>
          <Text style={[styles.tickGlyph, alert && { color: color.alert }]}>{alert ? '!' : '✓'}</Text>
        </View>
        <Text style={[type.small, { flex: 1, color: alert ? color.alert : color.ink2 }]}>
          <Text style={{ color: color.ink, fontWeight: '700' }}>{`Série ${from.index}${done ? ` · ${kg(done.weight)} kg × ${done.reps}` : ''}`}</Text>
          {`  ${saved}`}
        </Text>
      </View>

      <View style={styles.ringWrap}>
        <RestRing size={toNewExercise ? 212 : 272} fraction={remainingFraction(rest, nowMs)}>
          <Text style={[type.eyebrow, { color: color.system, letterSpacing: 3 }]}>Repos</Text>
          <Text
            style={[type.clock, toNewExercise && { fontSize: 76 }]}
            maxFontSizeMultiplier={NUMERAL_FONT_SCALE_CAP}
            accessibilityLiveRegion="polite"
            accessibilityLabel={`${Math.ceil(left / 1000)} secondes de repos`}
          >
            {formatClock(left)}
          </Text>
          <Text style={[type.small, { marginTop: 2 }]}>{shifted ? 'ajusté' : `${planned} s prévues`}</Text>
        </RestRing>
      </View>

      {nextEx && nextSet ? (
        toNewExercise ? (
          <View style={styles.next}>
            <Text style={type.eyebrow}>{`Exercice suivant · ${plan.exercises.findIndex((e) => e.se_id === nextEx.se_id) + 1} / ${plan.exercises.length}`}</Text>
            <Text style={[type.exercise, { fontSize: 25, lineHeight: 29, marginTop: 4 }]} maxFontSizeMultiplier={1.3}>
              {nextEx.executed_name}
            </Text>
            <Text style={[type.small, { marginTop: 4 }]}>{scheme(nextEx.set_scheme)}</Text>
            <Guidance exercise={nextEx} />
            <SecondaryButton label="Machine prise ?  Remplacer ›" onPress={() => props.onSwap(nextEx.se_id)} style={styles.swap} />
          </View>
        ) : (
          <View style={styles.next}>
            <Text style={type.eyebrow}>Ensuite, automatiquement</Text>
            <Text style={[type.bodyStrong, { fontSize: 21, marginTop: 4 }]}>
              {`Série ${nextSet.index} sur ${setsOf(plan, nextSet.se_id).length}`}
              <Text style={[type.body, type.tabular]}>{nextDraft ? `  ·  ${kg(nextDraft.weight)} kg × ${nextDraft.reps ?? '—'}` : ''}</Text>
            </Text>
          </View>
        )
      ) : null}

      <View style={{ flex: 1, minHeight: 8 }} />
      <View style={styles.restControls}>
        <SecondaryButton label="−15 s" a11y="Raccourcir le repos de 15 secondes" onPress={() => props.onShift(-15_000)} style={styles.restBtn} />
        <SecondaryButton label="+15 s" a11y="Allonger le repos de 15 secondes" onPress={() => props.onShift(15_000)} style={styles.restBtn} />
      </View>
      <View style={{ height: 10 }} />
      <PrimaryAction
        testID="skip"
        tone="trace"
        label={toNewExercise ? 'Commencer maintenant' : 'Passer le repos'}
        sublabel={toNewExercise ? nextEx?.executed_name : nextSet ? `Série ${nextSet.index} maintenant` : undefined}
        onPress={props.onSkip}
      />
    </View>
  );
}

// ── secondary sheets ─────────────────────────────────────────────────────────

const LEVEL_TONE: Record<SubstituteLevel, string> = { N1: color.subN1, N2: color.subN2, N3: color.subN3 };

/** The engine's ranked list when the server sends it; the lab's flat list otherwise. */
function optionsOf(ex: PlanExercise): { name: string; level: SubstituteLevel | null; badge: string | null; rationale: string | null }[] {
  if (ex.substitute_options?.length) return ex.substitute_options;
  return ex.substitutes.map((name) => ({ name, level: null, badge: null, rationale: null }));
}

function SwapSheet(props: { exercise: PlanExercise | null; locked: boolean; onClose: () => void; onPick: (name: string) => void }) {
  const ex = props.exercise;
  const options = ex ? optionsOf(ex) : [];
  let body: React.ReactNode;
  if (props.locked) {
    // the server's rule (`can_substitute`): a session holds ONE executed name per
    // exercise — once a set is done, a swap would rename sets already performed
    body = <SheetRow title="Plus possible pour cet exercice" detail="Une série est déjà enregistrée sous ce nom : la remplacer changerait le nom des séries déjà faites." />;
  } else if (options.length === 0) {
    body = <SheetRow title="Aucun remplaçant proposé pour cet exercice" />;
  } else {
    body = options.map((o) => (
      <Pressable
        key={o.name}
        accessibilityRole="button"
        accessibilityLabel={o.badge ? `${o.name}, ${o.badge}` : o.name}
        onPress={() => props.onPick(o.name)}
        style={({ pressed }) => [styles.option, o.level && { borderLeftColor: LEVEL_TONE[o.level] }, pressed && { opacity: 0.72 }]}
      >
        <View style={{ flex: 1 }}>
          <Text style={type.bodyStrong}>{o.name}</Text>
          {o.rationale ? <Text style={[type.small, { marginTop: 2 }]}>{o.rationale}</Text> : null}
        </View>
        {o.badge && o.level ? (
          <Text style={[styles.badge, { color: LEVEL_TONE[o.level], borderColor: LEVEL_TONE[o.level] }]}>{o.badge}</Text>
        ) : null}
      </Pressable>
    ));
  }
  return (
    <Sheet visible={ex !== null} title="Remplacer l’exercice" onClose={props.onClose}>
      {props.locked ? null : (
        <Text style={[type.small, { marginBottom: 6 }]}>
          Du plus proche au plus éloigné, selon AUREN. Le changement est confirmé par le serveur : d’ici là, l’exercice est marqué « en attente ».
        </Text>
      )}
      {body}
    </Sheet>
  );
}

function EntrySheet(props: {
  state: WorkoutState;
  edit: { setId: number; field: keyof Draft } | null;
  onClose: () => void;
  onSetValue: (setId: number, field: keyof Draft, value: number | null) => void;
}) {
  const [text, setText] = useState('');
  const e = props.edit;
  useEffect(() => {
    if (!e) return;
    const v = draftFor(props.state, e.setId)[e.field];
    setText(v === null ? '' : String(v).replace('.', ','));
  }, [e, props.state]);
  const commit = () => {
    if (!e) return;
    const n = Number(text.replace(',', '.'));
    props.onSetValue(e.setId, e.field, text.trim() === '' || Number.isNaN(n) ? null : n);
    props.onClose();
  };
  return (
    <Sheet visible={e !== null} title={e?.field === 'weight' ? 'Charge (kg)' : 'Répétitions'} onClose={props.onClose}>
      <TextInput
        value={text}
        onChangeText={setText}
        onSubmitEditing={commit}
        autoFocus
        keyboardType={e?.field === 'weight' ? 'decimal-pad' : 'number-pad'}
        returnKeyType="done"
        accessibilityLabel={e?.field === 'weight' ? 'Charge en kilos' : 'Nombre de répétitions'}
        style={styles.entry}
        maxFontSizeMultiplier={NUMERAL_FONT_SCALE_CAP}
        selectionColor={color.signal}
      />
      <PrimaryAction label="OK" onPress={commit} />
    </Sheet>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: color.field, paddingHorizontal: space.gutter },
  rootRest: { backgroundColor: color.fieldRest },
  head: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginTop: 10, marginBottom: 6 },
  headCentered: { flex: 1, textAlign: 'center' },
  nameRow: { flexDirection: 'row', alignItems: 'flex-start', gap: 10 },
  skip: { alignSelf: 'center', marginTop: 14, minHeight: 44, justifyContent: 'center', paddingHorizontal: 16 },
  skipText: { color: color.ink3, fontSize: 15, fontWeight: '600' },
  undo: { flexDirection: 'row', alignItems: 'center', gap: 10, backgroundColor: color.plate, borderRadius: 14, borderWidth: 1, borderColor: color.line, paddingLeft: 14, marginBottom: 6 },
  undoButton: { minHeight: 44, borderWidth: 0 },
  option: { flexDirection: 'row', alignItems: 'center', gap: 12, paddingVertical: 12, paddingLeft: 12, borderLeftWidth: 4, borderLeftColor: color.line, borderBottomWidth: StyleSheet.hairlineWidth, borderBottomColor: color.line },
  badge: { fontSize: 12, fontWeight: '800', letterSpacing: 0.4, borderWidth: 1, borderRadius: 10, paddingHorizontal: 8, paddingVertical: 3, overflow: 'hidden' },
  status: { ...type.small, color: color.ink3, textAlign: 'center', marginTop: -2, marginBottom: 4 },
  body: { flex: 1 },
  setLine: { marginTop: 8, fontVariant: ['tabular-nums'] },
  chips: { flexDirection: 'row', gap: 8, marginTop: 16 },
  chip: { flex: 1, borderRadius: 14, borderWidth: 1, borderColor: color.line, paddingVertical: 8, paddingHorizontal: 10, minHeight: 54 },
  chipNow: { borderWidth: 2, borderColor: color.signal, backgroundColor: color.plate },
  chipIndex: { ...type.eyebrow, fontSize: 11 },
  chipValue: { color: color.ink2, fontSize: 15, fontWeight: '700', marginTop: 3, fontVariant: ['tabular-nums'] },
  guidance: { marginTop: 18, paddingLeft: 12, borderLeftWidth: 3, borderLeftColor: color.system },
  guideLead: { color: color.system, fontSize: 16, fontWeight: '700', lineHeight: 21 },
  guideTarget: { color: color.system, fontSize: 16, fontWeight: '600', marginTop: 2, fontVariant: ['tabular-nums'] },
  requiresSync: { marginTop: 12, color: color.alert, fontSize: 14, fontWeight: '600' },
  dials: { flexDirection: 'row', gap: 10 },
  savedRow: { flexDirection: 'row', alignItems: 'center', gap: 10, marginTop: 4 },
  tick: { width: 24, height: 24, borderRadius: 12, borderWidth: 2, borderColor: color.ink2, alignItems: 'center', justifyContent: 'center' },
  tickGlyph: { color: color.ink, fontSize: 12, fontWeight: '800' },
  ringWrap: { alignItems: 'center', marginTop: 18 },
  next: { marginTop: 18, backgroundColor: color.plateRest, borderRadius: 20, borderWidth: 1, borderColor: color.lineRest, padding: 16 },
  swap: { marginTop: 12, borderColor: color.lineRest, minHeight: 48 },
  restControls: { flexDirection: 'row', gap: 10 },
  restBtn: { flex: 1, borderColor: color.lineRest, minHeight: 56 },
  entry: {
    color: color.ink,
    fontSize: 64,
    fontWeight: '800',
    fontVariant: ['tabular-nums'],
    textAlign: 'center',
    paddingVertical: 18,
    marginVertical: 12,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: color.line,
    backgroundColor: color.field,
  },
});
