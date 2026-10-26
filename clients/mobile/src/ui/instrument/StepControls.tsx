import React from 'react';
import { Pressable, Text, View } from 'react-native';

import { color, type } from '../theme';
import { type ControlBox, type Direction, neighborStep, stepControlsLayout, stepLabel, stepText } from './stepModel';

/**
 * DA-02.4B.3 — EXPLORATION. The − / + controls, under the instrument's frame. Each
 * press selects the previous / next supplied step and reports it through the SAME
 * callback as a finger on the rail (`onSelectPosition`): one path, so the caller's
 * disclosure wakes and its 1,5 s delay restarts exactly as for a drag.
 *
 * DA-02.7 R5 (operator: « rail », « tout sauf le basique ») — each key is a small Frame C:
 * the `plate` face, the secondary stroke (`ink3`) on three sides, a 1u mounting rail along
 * the bottom and two 1u registration marks standing on it. Pressed, the face sinks to
 * `field` and the rail and marks light up in `ink`. `signal` stays the cursor's alone.
 */
export type StepControlsProps = {
  width: number;
  steps?: readonly number[];
  stepValues?: readonly number[];
  selectedPosition: number;
  unit?: string;
  onSelectPosition?: (position: number) => void;
};

export function StepControls(p: StepControlsProps) {
  const l = stepControlsLayout(p.width);
  return (
    <View style={{ width: p.width, height: l.height }}>
      <StepButton dir={-1} box={l.decrement} stroke={l.stroke} u={l.u} {...p} />
      <StepButton dir={1} box={l.increment} stroke={l.stroke} u={l.u} {...p} />
    </View>
  );
}

/** Frame C's mounting rail and its two registration marks, in u — structure, not decoration. */
function KeyRail({ u, pressed }: { u: number; pressed: boolean }) {
  const tone = pressed ? color.ink : color.ink3;
  return (
    <>
      <View pointerEvents="none" style={{ position: 'absolute', left: 0, right: 0, bottom: 0, height: u, backgroundColor: tone }} />
      <View pointerEvents="none" style={{ position: 'absolute', left: 2 * u, bottom: u, width: u, height: 1.6 * u, backgroundColor: tone }} />
      <View pointerEvents="none" style={{ position: 'absolute', right: 2 * u, bottom: u, width: u, height: 1.6 * u, backgroundColor: tone }} />
    </>
  );
}

function StepButton(p: StepControlsProps & { dir: Direction; box: ControlBox; stroke: number; u: number }) {
  const move = neighborStep(p.steps, p.stepValues, p.selectedPosition, p.dir);
  const enabled = Boolean(move && p.onSelectPosition);
  const value = stepText(move);
  return (
    <Pressable
      testID={p.dir < 0 ? 'step-decrement' : 'step-increment'}
      accessibilityRole="button"
      accessibilityLabel={stepLabel(p.dir, move, p.unit)}
      accessibilityState={{ disabled: !enabled }}
      disabled={!enabled}
      onPress={() => move && p.onSelectPosition?.(move.position)}
      style={({ pressed }) => ({
        position: 'absolute',
        left: p.box.x,
        top: p.box.y,
        width: p.box.w,
        height: p.box.h,
        backgroundColor: pressed ? color.field : color.plate,
        borderColor: pressed ? color.ink : color.ink3,
        borderTopWidth: p.stroke,
        borderLeftWidth: p.stroke,
        borderRightWidth: p.stroke,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 10,
      })}
    >
      {({ pressed }) => (
        <>
          <KeyRail u={p.u} pressed={pressed} />
          <Text style={[styles.glyph, { color: enabled ? color.ink : color.ink3 }]}>{p.dir < 0 ? '−' : '+'}</Text>
          {value ? <Text style={[styles.value, { color: enabled ? color.ink2 : color.ink3 }]}>{value}</Text> : null}
        </>
      )}
    </Pressable>
  );
}

const styles = {
  glyph: { fontFamily: type.figure.fontFamily, fontSize: 36, fontWeight: '800' as const, lineHeight: 40 },
  value: { ...type.action, ...type.tabular },
};
