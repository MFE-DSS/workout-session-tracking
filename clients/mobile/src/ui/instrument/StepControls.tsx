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
 * Neutral by design: the grey of `line` says « press me », the Frame C stroke (`ink3`)
 * ties them to the instrument; `signal` stays the cursor's alone.
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
      <StepButton dir={-1} box={l.decrement} stroke={l.stroke} {...p} />
      <StepButton dir={1} box={l.increment} stroke={l.stroke} {...p} />
    </View>
  );
}

function StepButton(p: StepControlsProps & { dir: Direction; box: ControlBox; stroke: number }) {
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
        backgroundColor: pressed ? color.plate : color.line,
        borderColor: pressed ? color.ink : color.ink3,
        borderWidth: p.stroke,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 10,
      })}
    >
      <Text style={[styles.glyph, { color: enabled ? color.ink : color.ink3 }]}>{p.dir < 0 ? '−' : '+'}</Text>
      {value ? <Text style={[styles.value, { color: enabled ? color.ink2 : color.ink3 }]}>{value}</Text> : null}
    </Pressable>
  );
}

const styles = {
  glyph: { fontFamily: type.figure.fontFamily, fontSize: 36, fontWeight: '800' as const, lineHeight: 40 },
  value: { ...type.action, ...type.tabular },
};
