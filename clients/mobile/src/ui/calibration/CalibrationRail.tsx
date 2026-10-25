import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Animated, Easing, LayoutChangeEvent, PanResponder, StyleSheet, Text, View } from 'react-native';
import Svg, { Circle, Defs, Line, Pattern, Rect, Text as SvgText } from 'react-native-svg';

import { useReducedMotion } from '../../native/motion';
import { color, type } from '../theme';
import { ActiveCursor } from './ActiveCursor';
import { ACTIVE_CURSOR, REFERENCE_MARKER } from './geometry';
import {
  type Boundaries,
  type Density,
  describeRail,
  formatDelta,
  formatValue,
  railLayout,
  type RailLayout,
  type Zone,
  ZONE_LABEL,
} from './layout';
import { ReferenceMarker } from './ReferenceMarker';

export type CalibrationRailProps = Boundaries & {
  /** normalized 0..1, clamped — where the engine's prescription sits */
  referencePosition: number;
  /** normalized 0..1, clamped — where the user's current decision sits */
  selectedPosition: number;
  /** the selectable values, normalized 0..1 — one rail index each; the cursor lands on one */
  steps?: readonly number[];
  /** the value each step stands for, same order as `steps` — printed under the major indexes (expanded) */
  stepValues?: readonly number[];
  selectedValue?: number;
  /** the prescription's value, for the readout and the spoken description */
  referenceValue?: number;
  unit?: string;
  /** forced density; otherwise derived from the laid-out width */
  density?: Density;
  /** fixed width (tests, gallery); otherwise the rail measures itself */
  width?: number;
  /** a finger on the rail: the (snapped) position it points at — the caller decides what it means */
  onSelectPosition?: (position: number) => void;
  /** assistive technologies: one step up / down */
  onIncrement?: () => void;
  onDecrement?: () => void;
  testID?: string;
};

/** AUREN_CALIBRATION_SYSTEM §3 — the range colours; the cursor stays `signal` in every zone. */
const ZONE_COLOR: Record<Zone, string> = {
  EASY: color.perfBelow,
  TARGET: color.ink,
  PUSH: color.perfAbove,
  HIGH_COST: color.alert,
};
const PATTERN_ID: Record<Zone, string> = {
  EASY: 'cal-easy',
  TARGET: 'cal-target',
  PUSH: 'cal-push',
  HIGH_COST: 'cal-high',
};

/**
 * The band's four signatures (AUREN_CALIBRATION_SYSTEM §2, §9): EASY points ·
 * TARGET a plain strip · PUSH affirmed dashes · HIGH COST a diagonal hatch. Flat
 * fills only: no gradient, no relief.
 */
function ZonePatterns({ u }: { u: number }) {
  const p = 2 * u; // pattern period
  return (
    <Defs>
      <Pattern id={PATTERN_ID.EASY} width={p} height={p} patternUnits="userSpaceOnUse">
        <Circle cx={p / 2} cy={p / 2} r={u * 0.32} fill={ZONE_COLOR.EASY} />
      </Pattern>
      <Pattern id={PATTERN_ID.TARGET} width={p} height={p} patternUnits="userSpaceOnUse">
        <Rect width={p} height={p} fill={ZONE_COLOR.TARGET} fillOpacity={0.28} />
      </Pattern>
      <Pattern id={PATTERN_ID.PUSH} width={p} height={p} patternUnits="userSpaceOnUse">
        <Rect x={0} y={0} width={u * 0.7} height={p} fill={ZONE_COLOR.PUSH} fillOpacity={0.75} />
      </Pattern>
      <Pattern
        id={PATTERN_ID.HIGH_COST}
        width={p}
        height={p}
        patternUnits="userSpaceOnUse"
        patternTransform="rotate(45)"
      >
        <Rect x={0} y={0} width={u * 0.6} height={p} fill={ZONE_COLOR.HIGH_COST} />
      </Pattern>
    </Defs>
  );
}

const MOTION_MS = 240;
const ZONE_LABEL_MIN_WIDTH = 56;

/**
 * DA-02.2 — the Calibration Rail (LOCKED v1). Shows the RELATIVE COST of a
 * deviation from the prescription; computes none of it: every position, step and
 * boundary is supplied (`VNEXT §8.11`). Shows a price, blocks nothing.
 */
export function CalibrationRail(props: CalibrationRailProps) {
  const [measured, setMeasured] = useState(0);
  const width = props.width ?? measured;
  const onLayout = (e: LayoutChangeEvent) => setMeasured(Math.round(e.nativeEvent.layout.width));
  const adjustable = Boolean(props.onIncrement || props.onDecrement);

  return (
    <View
      testID={props.testID}
      onLayout={props.width ? undefined : onLayout}
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
        zone: width ? railLayout({ ...props, width }).selectedZone : null,
      })}
    >
      {width > 0 ? <Rail {...props} width={width} /> : null}
    </View>
  );
}

function Rail(props: CalibrationRailProps & { width: number }) {
  const l = railLayout(props);
  const reduced = useReducedMotion();
  const x = useRef(new Animated.Value(l.selectedX)).current;
  const laidOutWidth = useRef(l.width);
  const dragging = useRef(false);

  useEffect(() => {
    // a new width is a new drawing, and a finger is already the motion: place, don't animate
    if (reduced || dragging.current || laidOutWidth.current !== l.width) {
      laidOutWidth.current = l.width;
      x.setValue(l.selectedX);
      return;
    }
    Animated.timing(x, {
      toValue: l.selectedX,
      duration: MOTION_MS,
      easing: Easing.out(Easing.cubic),
      useNativeDriver: false, // the deviation segment animates a layout width
    }).start();
  }, [l.selectedX, l.width, reduced, x]);

  // a finger on the rail: the rail reports the snapped position, the caller decides
  const host = useRef<React.ComponentRef<typeof View>>(null);
  const originX = useRef(0);
  const latest = useRef({ layout: l, onSelect: props.onSelectPosition });
  latest.current = { layout: l, onSelect: props.onSelectPosition };
  const pan = useMemo(
    () =>
      PanResponder.create({
        onStartShouldSetPanResponder: () => Boolean(latest.current.onSelect),
        onMoveShouldSetPanResponder: () => Boolean(latest.current.onSelect),
        onPanResponderTerminationRequest: () => false,
        onPanResponderGrant: (e) => {
          dragging.current = true;
          const pageX = e.nativeEvent.pageX;
          host.current?.measureInWindow((wx) => {
            originX.current = wx;
            latest.current.onSelect?.(latest.current.layout.positionAt(pageX - wx));
          });
        },
        onPanResponderMove: (_, g) => {
          latest.current.onSelect?.(latest.current.layout.positionAt(g.moveX - originX.current));
        },
        onPanResponderRelease: () => {
          dragging.current = false;
        },
        onPanResponderTerminate: () => {
          dragging.current = false;
        },
      }),
    [],
  );

  const u = l.u;
  const band = l.band;
  const active = l.selectedZone;
  const dim = (z: Zone | null) => (z && z === active ? 1 : 0.45);
  const segH = 0.8 * u;
  // the deviation, reference → cursor, on either side (AUREN_CALIBRATION_SYSTEM §6)
  const r = l.referenceX;
  const right = x.interpolate({
    inputRange: [r, Math.max(r + 0.001, l.trackEnd)],
    outputRange: [0, Math.max(0.001, l.trackEnd - r)],
    extrapolate: 'clamp',
  });
  const leftEdge = x.interpolate({
    inputRange: [Math.min(l.trackStart, r - 0.001), r],
    outputRange: [Math.min(l.trackStart, r - 0.001), r],
    extrapolate: 'clamp',
  });
  const leftWidth = x.interpolate({
    inputRange: [Math.min(l.trackStart, r - 0.001), r],
    outputRange: [Math.max(0.001, r - l.trackStart), 0],
    extrapolate: 'clamp',
  });

  return (
    <View>
      <View ref={host} style={{ width: l.width, height: l.height }} {...pan.panHandlers}>
        <Svg width={l.width} height={l.height} accessible={false} importantForAccessibility="no-hide-descendants">
          <ZonePatterns u={u} />
          {/* the zone band: each range a flat strip with its own pattern — never colour alone */}
          {band
            ? l.segments.map((s) => (
                <Rect
                  key={`band-${s.zone}`}
                  x={s.x1}
                  y={band.y}
                  width={s.x2 - s.x1}
                  height={band.height}
                  fill={`url(#${PATTERN_ID[s.zone]})`}
                  opacity={s.zone === active ? 1 : 0.5}
                />
              ))
            : null}
          {/* calibration brackets: where one range ends and the next begins */}
          {band
            ? l.brackets.map((bx) => (
                <Line
                  key={`br-${bx.toFixed(2)}`}
                  x1={bx}
                  y1={l.baselineY - 0.8 * u}
                  x2={bx}
                  y2={band.y + band.height + 0.6 * u}
                  stroke={color.ink2}
                  strokeWidth={1}
                />
              ))
            : null}
          {/* baseline: the structure, affirmed, then the ranges over it */}
          <Line x1={l.trackStart} y1={l.baselineY} x2={l.trackEnd} y2={l.baselineY} stroke={color.ink2} strokeWidth={3} />
          {l.segments.map((s) => (
            <Line
              key={s.zone}
              x1={s.x1}
              y1={l.baselineY}
              x2={s.x2}
              y2={l.baselineY}
              stroke={ZONE_COLOR[s.zone]}
              strokeOpacity={dim(s.zone)}
              strokeWidth={2}
            />
          ))}
          {l.scale.map((sc) => (
            <SvgText
              key={`sc-${sc.x.toFixed(2)}`}
              x={sc.x}
              y={(band ? band.y + band.height : l.baselineY) + 11}
              fontSize={11}
              fontWeight="600"
              fontFamily={type.small.fontFamily ?? 'Helvetica Neue, Helvetica, Arial, sans-serif'}
              fill={color.ink3}
              textAnchor="middle"
            >
              {sc.text}
            </SvgText>
          ))}
          {/* every index is exactly one slot wide; the hatch strokes are thinner */}
          {l.ticks.map((t) => (
            <Line
              key={`${t.x.toFixed(2)}-${t.hatch ? 'h' : 'i'}`}
              x1={t.x}
              y1={l.baselineY}
              x2={t.x + t.lean}
              y2={t.y1}
              stroke={t.zone ? ZONE_COLOR[t.zone] : color.ink3}
              strokeOpacity={t.zone ? dim(t.zone) : 1}
              strokeWidth={t.hatch ? u * 0.5 : u}
              strokeLinecap="butt"
            />
          ))}
          {/* the reference index: from the baseline into the marker's slot */}
          <Line
            x1={l.referenceTick.x}
            y1={l.referenceTick.y1}
            x2={l.referenceTick.x}
            y2={l.referenceTick.y2}
            stroke={color.system}
            strokeWidth={u}
            strokeLinecap="butt"
          />
        </Svg>

        <Animated.View
          pointerEvents="none"
          style={[styles.segment, { top: l.baselineY - segH / 2, height: segH, left: r, width: right }]}
        />
        <Animated.View
          pointerEvents="none"
          style={[styles.segment, { top: l.baselineY - segH / 2, height: segH, left: leftEdge, width: leftWidth }]}
        />

        <View
          pointerEvents="none"
          style={{ position: 'absolute', top: l.referenceTop, left: l.referenceX - (REFERENCE_MARKER.width / 2) * u }}
        >
          <ReferenceMarker size={u} />
        </View>

        {/* the cursor and the index it frames move together; the index fills its slot */}
        <Animated.View
          pointerEvents="none"
          style={{
            position: 'absolute',
            top: l.cursorTop,
            left: -(ACTIVE_CURSOR.width / 2) * u,
            transform: [{ translateX: x }],
          }}
        >
          <ActiveCursor size={u} />
          <View
            style={[
              styles.index,
              {
                width: u,
                left: (ACTIVE_CURSOR.width / 2) * u - u / 2,
                top: l.selectedTick.y1 - l.cursorTop,
                height: l.selectedTick.y2 - l.selectedTick.y1,
              },
            ]}
          />
        </Animated.View>
      </View>

      {l.density === 'expanded' ? <ZoneLabels l={l} /> : null}
      {l.density !== 'compact' ? <Readout {...props} zone={l.selectedZone} /> : null}
    </View>
  );
}

/**
 * Expanded only: each zone name centred under its range. A narrow range (TARGET
 * is often one) still gets its name, in a box wider than the range itself.
 */
function ZoneLabels({ l }: { l: RailLayout }) {
  return (
    <View style={{ height: 16, width: l.width }}>
      {l.segments.map((s) => {
        const box = Math.max(s.x2 - s.x1, ZONE_LABEL_MIN_WIDTH);
        const left = Math.min(Math.max(0, (s.x1 + s.x2) / 2 - box / 2), l.width - box);
        return (
          <Text
            key={s.zone}
            numberOfLines={1}
            style={[styles.zoneLabel, { left, width: box, color: s.zone === l.selectedZone ? color.ink2 : color.ink3 }]}
          >
            {ZONE_LABEL[s.zone]}
          </Text>
        );
      })}
    </View>
  );
}

/** Regular and expanded: the prescription, the choice, the delta — and the zone in words. */
function Readout(props: CalibrationRailProps & { zone: Zone | null }) {
  const unit = props.unit ? ` ${props.unit}` : '';
  const hasBoth = props.selectedValue !== undefined && props.referenceValue !== undefined;
  return (
    <View style={styles.readout}>
      <View>
        <Text style={styles.readLabel}>Prescrit</Text>
        <Text style={[styles.readRef, { color: color.system }]}>
          {props.referenceValue !== undefined ? `${formatValue(props.referenceValue)}${unit}` : '—'}
        </Text>
      </View>
      <View style={{ alignItems: 'flex-end' }}>
        <Text style={styles.readLabel}>
          {[hasBoth ? formatDelta(props.selectedValue as number, props.referenceValue as number) : null,
            props.zone ? ZONE_LABEL[props.zone] : null].filter(Boolean).join('  ·  ')}
        </Text>
        {props.selectedValue !== undefined ? (
          <Text style={styles.readValue} maxFontSizeMultiplier={1.25}>
            {formatValue(props.selectedValue)}
            <Text style={styles.readUnit}>{unit}</Text>
          </Text>
        ) : null}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  segment: { position: 'absolute', backgroundColor: color.signal, opacity: 0.55 },
  index: { position: 'absolute', backgroundColor: color.ink },
  zoneLabel: { ...type.eyebrow, position: 'absolute', fontSize: 10, letterSpacing: 1, textAlign: 'center' },
  readout: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-end', marginTop: 8 },
  readLabel: { ...type.eyebrow, fontSize: 11, letterSpacing: 1.2, ...type.tabular },
  readRef: { ...type.bodyStrong, fontSize: 18, marginTop: 2, ...type.tabular },
  readValue: { ...type.readout, fontSize: 34, letterSpacing: -0.8, lineHeight: 38, marginTop: 2 },
  readUnit: { fontSize: 16, fontWeight: '700', color: color.ink2 },
});
