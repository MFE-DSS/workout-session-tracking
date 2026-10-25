import React, { useMemo, useRef } from 'react';
import { PanResponder, StyleSheet, Text, View } from 'react-native';
import Svg, { Line } from 'react-native-svg';

import { color, type } from '../theme';
import { ActiveCursor } from './ActiveCursor';
import { type FieldBar, fieldLayout } from './fieldLayout';
import { ACTIVE_CURSOR, REFERENCE_MARKER } from './geometry';
import { type Boundaries, describeRail, formatDelta, formatValue, type Zone, ZONE_LABEL } from './layout';
import { ReferenceMarker } from './ReferenceMarker';

export type CalibrationFieldProps = Boundaries & {
  width: number;
  /** the whole height the field may take, readout included */
  height: number;
  referencePosition: number;
  selectedPosition: number;
  steps: readonly number[];
  selectedValue?: number;
  referenceValue?: number;
  unit?: string;
  u?: number;
  /** a finger on the field: the step it points at — the caller decides what it means */
  onSelectPosition?: (position: number) => void;
  onIncrement?: () => void;
  onDecrement?: () => void;
  testID?: string;
};

/** The locked range colours (AUREN_CALIBRATION_SYSTEM §3). */
const ZONE_COLOR: Record<Zone, string> = {
  EASY: color.perfBelow,
  TARGET: color.ink,
  PUSH: color.perfAbove,
  HIGH_COST: color.alert,
};
/** The prescription's bar speaks with the engine's voice; every other bar with its range's. */
function barColor(b: FieldBar): string {
  if (b.reference) return color.system;
  return b.zone ? ZONE_COLOR[b.zone] : color.ink3;
}

/** Approximate advance of one capital at the zone-name size (13 pt, tracking 1.6). */
const LABEL_CHAR_W = 10;

/**
 * Zone names centred under their ranges, wide enough to be read whole, and
 * NEVER overlapping: a narrow range (TARGET) borrows room from its neighbours,
 * boxes are swept left to right, then pulled back inside the field.
 */
export function packLabels(
  segments: { zone: Zone; x1: number; x2: number }[],
  width: number,
): { zone: Zone; left: number; width: number }[] {
  const boxes = segments.map((s) => {
    const w = Math.max(s.x2 - s.x1, ZONE_LABEL[s.zone].length * LABEL_CHAR_W + 6);
    return { zone: s.zone, left: (s.x1 + s.x2) / 2 - w / 2, width: w };
  });
  for (let k = 0; k < boxes.length; k++) {
    const prevEnd = k ? boxes[k - 1].left + boxes[k - 1].width : 0;
    boxes[k].left = Math.max(boxes[k].left, prevEnd);
  }
  for (let k = boxes.length - 1; k >= 0; k--) {
    const nextStart = k < boxes.length - 1 ? boxes[k + 1].left : width;
    boxes[k].left = Math.min(boxes[k].left, nextStart - boxes[k].width);
  }
  return boxes;
}

const READOUT_H = 34;
const LABELS_H = 24;
/** below this height the zone names would starve the bars: the bars keep the room */
const LABELS_MIN_HEIGHT = 180;

/**
 * The Calibration FIELD: the rail as the frame's background. Bars hang from the
 * top, one per step; the ones between the prescription and the decision are lit.
 * The cursor moves by STEPS, like a digital metronome: no glide, a click per step.
 */
export function CalibrationField(props: CalibrationFieldProps) {
  const labels = props.height >= LABELS_MIN_HEIGHT;
  const fieldH = props.height - READOUT_H - (labels ? LABELS_H : 0);
  const l = fieldLayout({ ...props, height: fieldH });
  const u = l.u;

  const host = useRef<React.ComponentRef<typeof View>>(null);
  const originX = useRef(0);
  const latest = useRef({ l, onSelect: props.onSelectPosition });
  latest.current = { l, onSelect: props.onSelectPosition };
  const pan = useMemo(
    () =>
      PanResponder.create({
        onStartShouldSetPanResponder: () => Boolean(latest.current.onSelect),
        onMoveShouldSetPanResponder: () => Boolean(latest.current.onSelect),
        onPanResponderTerminationRequest: () => false,
        onPanResponderGrant: (e) => {
          const pageX = e.nativeEvent.pageX;
          host.current?.measureInWindow((wx) => {
            originX.current = wx;
            latest.current.onSelect?.(latest.current.l.positionAt(pageX - wx));
          });
        },
        onPanResponderMove: (_, g) => latest.current.onSelect?.(latest.current.l.positionAt(g.moveX - originX.current)),
      }),
    [],
  );
  const adjustable = Boolean(props.onIncrement || props.onDecrement);

  return (
    <View
      testID={props.testID}
      style={{ width: props.width, height: props.height }}
      accessible
      accessibilityRole={adjustable ? 'adjustable' : undefined}
      accessibilityActions={adjustable ? [{ name: 'increment' }, { name: 'decrement' }] : undefined}
      onAccessibilityAction={(e) => {
        if (e.nativeEvent.actionName === 'increment') props.onIncrement?.();
        if (e.nativeEvent.actionName === 'decrement') props.onDecrement?.();
      }}
      accessibilityLabel={describeRail({
        referenceValue: props.referenceValue,
        selectedValue: props.selectedValue,
        unit: props.unit,
        zone: l.selectedZone,
      })}
    >
      <View ref={host} style={{ width: props.width, height: fieldH }} {...pan.panHandlers}>
        <Svg width={props.width} height={fieldH} accessible={false} importantForAccessibility="no-hide-descendants">
          {l.brackets.map((bx) => (
            <Line key={`br-${bx.toFixed(2)}`} x1={bx} y1={0} x2={bx} y2={fieldH} stroke={color.line} strokeWidth={1} />
          ))}
          {l.bars.map((b) => (
            <Line
              key={`bar-${b.x.toFixed(2)}`}
              x1={b.x}
              y1={b.y1}
              x2={b.x + b.lean}
              y2={b.y2}
              stroke={barColor(b)}
              strokeOpacity={b.lit || b.reference ? 1 : 0.28}
              strokeWidth={u}
              strokeLinecap="butt"
            />
          ))}
        </Svg>
        <View
          pointerEvents="none"
          style={{ position: 'absolute', top: l.referenceTop, left: l.referenceX - (REFERENCE_MARKER.width / 2) * u }}
        >
          <ReferenceMarker size={u} />
        </View>
        <View
          pointerEvents="none"
          style={{ position: 'absolute', top: l.cursorTop, left: l.selectedX - (ACTIVE_CURSOR.width / 2) * u }}
        >
          <ActiveCursor size={u} />
        </View>
      </View>
      {labels ? (
        <View style={{ height: LABELS_H, width: props.width }}>
          {packLabels(l.segments, props.width).map(({ zone, left, width }) => (
            <Text
              key={zone}
              numberOfLines={1}
              style={[styles.zone, { left, width, color: zone === l.selectedZone ? ZONE_COLOR[zone] : color.ink3 }]}
            >
              {ZONE_LABEL[zone]}
            </Text>
          ))}
        </View>
      ) : null}
      <View style={styles.readout}>
        <Text style={[styles.read, { color: color.system }]}>
          {props.referenceValue !== undefined ? `PRESCRIT ${formatValue(props.referenceValue)} ${props.unit ?? ''}` : ''}
        </Text>
        <Text style={styles.read}>
          {props.selectedValue !== undefined ? (
            <Text style={styles.value}>{`${formatValue(props.selectedValue)} ${props.unit ?? ''}`}</Text>
          ) : null}
          {props.selectedValue !== undefined && props.referenceValue !== undefined
            ? `  ${formatDelta(props.selectedValue, props.referenceValue)}`
            : ''}
          {l.selectedZone ? `  ·  ${ZONE_LABEL[l.selectedZone]}` : ''}
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  readout: { height: READOUT_H, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-end' },
  read: { ...type.eyebrow, fontSize: 13, letterSpacing: 1.2, ...type.tabular },
  value: { color: color.ink, fontSize: 24, fontWeight: '800', letterSpacing: -0.4 },
  zone: { ...type.eyebrow, position: 'absolute', top: 4, fontSize: 13, letterSpacing: 1.6, textAlign: 'center' },
});
