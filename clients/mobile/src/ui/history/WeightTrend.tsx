import React, { useState } from 'react';
import { Pressable, StyleSheet, Text, View, useWindowDimensions } from 'react-native';
import Svg, { Circle, Line } from 'react-native-svg';
import type { WeightWindowState, WeightPoint } from '../../api/trainingHistoryResource';
import { CalibrationLink } from '../plan/calibrationControls';
import { color, type, space } from '../theme';
import { numeric, weightGeometry, weightExtent, weightDateLabel } from './historyView';

type WeightTrendProps = { state: WeightWindowState<WeightPoint>; onMore: () => void };

function comparable(point: WeightPoint): point is WeightPoint & { value: number } {
  return point.quality === 'KNOWN' && point.value !== null && Number.isFinite(point.value) && Number.isFinite(Date.parse(point.measured_at));
}

function weightLabel(point: WeightPoint) {
  if (comparable(point)) return `${numeric(point.value)} kg`;
  return point.quality === 'LEGACY_OUTSIDE_CURRENT_BOUNDS' ? 'Valeur hors limites actuelles' : 'Valeur invalide';
}

function WeightPlot(p: { entries: WeightPoint[]; timeZone?: string; selectedId?: number; onSelect: (id: number) => void }) {
  const { width, fontScale } = useWindowDimensions();
  const [measuredWidth, setMeasuredWidth] = useState(0);
  const plotWidth = measuredWidth || Math.max(32, width - 2 * space.gutter - 72);
  const height = Math.ceil(132 * Math.min(1.3, Math.max(1, fontScale)));
  const tickInset = Math.max(0, (19 * fontScale) / 2 - 10);
  const extent = weightExtent(p.entries);
  if (!extent) return null;
  const points = weightGeometry(p.entries, plotWidth, height);
  const selectedPoint = points.find(point => point.id === p.selectedId);
  const from = p.entries.find(e => e.measured_at === extent.from);
  const until = p.entries.find(e => e.measured_at === extent.until);
  const singleValue = extent.high === extent.low;
  const singleInstant = Date.parse(extent.from) === Date.parse(extent.until);
  const instantDates = singleInstant ? [...new Set(p.entries.map(e => weightDateLabel(e, p.timeZone)))].sort() : [];

  return <View testID="progress-weight-chart" style={styles.plot} importantForAccessibility="no-hide-descendants" accessibilityElementsHidden>
    <Text style={type.small}>kg</Text>
    <View style={styles.axes}>
      <View testID="progress-weight-scale" style={[styles.yTicks, singleValue ? styles.oneTick : null, { height: height + 2 * tickInset }]}>
        <Text testID="progress-weight-y-high" style={styles.tick}>{numeric(extent.high)}</Text>
        {!singleValue ? <Text testID="progress-weight-y-low" style={styles.tick}>{numeric(extent.low)}</Text> : null}
      </View>
      <View style={styles.xAxis}>
        <Pressable testID="progress-weight-chart-touch" accessible={false} focusable={false} style={{ marginVertical: tickInset }}
          onLayout={event => setMeasuredWidth(event.nativeEvent.layout.width)}
          onPress={event => {
            const { locationX, locationY } = event.nativeEvent;
            const distance = (point: (typeof points)[number]) => (locationX - point.x) ** 2 + (locationY - point.y) ** 2;
            const nearest = points.reduce((best, point) => distance(point) < distance(best) ? point : best);
            p.onSelect(nearest.id);
          }}>
          <View pointerEvents="none" importantForAccessibility="no-hide-descendants" style={{ height }}>
            <Svg width={plotWidth} height={height} viewBox={`0 0 ${plotWidth} ${height}`} accessible={false}>
              <Line x1={10} y1={10} x2={10} y2={height - 10} stroke={color.ink3} />
              <Line x1={10} y1={height - 10} x2={plotWidth - 10} y2={height - 10} stroke={color.ink3} />
              <Line x1={10} y1={singleValue ? height / 2 : 10} x2={15} y2={singleValue ? height / 2 : 10} stroke={color.ink3} />
              {singleInstant ? <Line x1={plotWidth / 2} y1={height - 10} x2={plotWidth / 2} y2={height - 5} stroke={color.ink3} /> : null}
              {!singleValue ? <>
                <Line x1={10} y1={10} x2={plotWidth - 10} y2={10} stroke={color.line} />
                <Line x1={10} y1={height / 2} x2={plotWidth - 10} y2={height / 2} stroke={color.line} strokeDasharray="2 6" />
              </> : null}
              {selectedPoint ? <Line x1={selectedPoint.x} y1={selectedPoint.y} x2={selectedPoint.x} y2={height - 10} stroke={color.ink3} strokeDasharray="2 4" /> : null}
              {points.map(q => <Circle key={q.id} cx={q.x} cy={q.y} r={q.id === p.selectedId ? 6 : 3.5}
                stroke={q.id === p.selectedId ? color.ink : color.ink2} strokeWidth={q.id === p.selectedId ? 2 : 0}
                fill={q.id === p.selectedId ? color.field : color.ink2} />)}
            </Svg>
          </View>
        </Pressable>
        <View testID="progress-weight-dates" style={[styles.dates, singleInstant ? styles.singleDate : null]}>
          {from ? <Text testID="progress-weight-date-from" style={styles.dateTick}>{instantDates.length > 1 ? `${instantDates.join(' / ')} · précisions de date distinctes` : weightDateLabel(from, p.timeZone)}</Text> : null}
          {until && !singleInstant ?
            <Text testID="progress-weight-date-until" style={[styles.dateTick, styles.dateEnd]}>{weightDateLabel(until, p.timeZone)}</Text> : null}
        </View>
      </View>
    </View>
  </View>;
}

function acquisitionLabel(point: WeightPoint) {
  const acquisition = (point.bodySource ?? point.provenance).acquisition;
  return acquisition === 'MANUAL_CORRECTION' ? 'Correction personnelle' :
    acquisition === 'MANUAL_ENTRY' ? 'Saisie personnelle' : 'Acquisition inconnue';
}

function WeightSource({ point }: { point: WeightPoint }) {
  const source = point.bodySource ?? point.provenance;
  const precision = point.bodySource?.date_precision === 'DAY_UTC_CONVENTION' ? 'jour déclaré' :
    point.bodySource?.date_precision === 'SERVER_CAPTURE_TIME' ? 'heure enregistrée par le serveur' : 'précision de date inconnue';
  return <View style={styles.disclosure}>
    <Text selectable style={type.small}>{source.origin === 'USER_DECLARED' ? 'Origine déclarée' : 'Origine inconnue'} · {precision}</Text>
    <Text selectable style={type.small}>{point.bodySource?.date_precision === 'DAY_UTC_CONVENTION' ? `Jour déclaré · ${weightDateLabel(point, 'UTC')}` : `Date source · ${point.measured_at}`}</Text>
    <Text selectable style={type.small}>{point.recorded_at ? `Journal · ${point.recorded_at}` : 'Saisie non datée'}</Text>
    <Text selectable style={type.small}>Source {source.source_ref}</Text>
    {!comparable(point) ? <Text selectable style={type.small}>Valeur source · {point.raw_value_repr ?? point.value ?? 'inconnue'}</Text> : null}
  </View>;
}

function observationLabel(point: WeightPoint, timeZone?: string) {
  const source = point.bodySource ?? point.provenance;
  const origin = source.origin === 'USER_DECLARED' ? 'Origine déclarée' : 'Origine inconnue';
  const precision = point.bodySource?.date_precision === 'DAY_UTC_CONVENTION' ? 'jour déclaré' :
    point.bodySource?.date_precision === 'SERVER_CAPTURE_TIME' ? 'heure enregistrée par le serveur' : 'précision de date inconnue';
  return `${weightDateLabel(point, timeZone)} · ${weightLabel(point)} · ${acquisitionLabel(point)} · ${origin} · ${precision} · ${point.bodySource ? `Version ${point.bodySource.revision}` : 'Version non capturée'} · mesure ${point.measurement_id}`;
}

function WeightReading({ state: s, onMore }: WeightTrendProps) {
  const [listOpen, setListOpen] = useState(false);
  const [selectedId, setSelectedId] = useState<number>();
  const points = s.entries.filter(comparable);
  const ordered = [...s.entries].sort((a, b) => Date.parse(a.measured_at) - Date.parse(b.measured_at) || a.measurement_id - b.measurement_id);
  const latest = [...ordered].reverse().find(comparable);
  const selected = s.entries.find(e => e.measurement_id === selectedId) ?? latest ?? ordered[ordered.length - 1];
  const timeZone = s.window?.time_zone;
  const selectedIndex = ordered.findIndex(point => point.measurement_id === selected?.measurement_id);
  const rows = listOpen ? ordered.map(point => ({ point, label: `${weightDateLabel(point, timeZone)} · ${weightLabel(point)}` })) : [];
  const labelCounts = new Map<string, number>();
  for (const { label } of rows) labelCounts.set(label, (labelCounts.get(label) ?? 0) + 1);
  return <View style={styles.reading}>
    {s.previous || s.status === 'pending' || s.status === 'unknown' || s.coverage === 'PARTIAL' ?
      <Text testID="progress-weight-partial" style={type.small} accessibilityLiveRegion="polite">
        {s.previous ? `Lecture précédente · ${s.status === 'pending' ? 'actualisation…' : 'lecture incomplète'}` :
          s.status === 'pending' ? 'Lecture des mesures…' : 'Lecture des mesures incomplète'}
      </Text> : null}
    {selected ? <View testID="progress-weight-selected" accessible focusable accessibilityRole="text" accessibilityLiveRegion="polite"
      accessibilityLabel={`${s.previous ? 'Lecture précédente' : s.status === 'confirmed' ? s.coverage === 'COMPLETE' ? 'Lecture confirmée' : 'Lecture partielle' : s.status === 'pending' ? 'Actualisation' : 'Lecture non confirmée'} · Observation ${selectedIndex + 1} sur ${ordered.length} · ${observationLabel(selected, timeZone)}`}>
      <View testID="progress-weight-selected-content" importantForAccessibility="no-hide-descendants" accessibilityElementsHidden>
      <View style={styles.selection}>
        <Text testID="progress-weight-selected-value" style={styles.value}>{weightLabel(selected)}</Text>
        <Text style={type.small}>{weightDateLabel(selected, timeZone)}</Text>
      </View>
      <Text testID="progress-weight-selected-provenance" style={type.small}>{`${acquisitionLabel(selected)} · ${selected.bodySource ? `Version ${selected.bodySource.revision}` : 'Version non capturée'}${s.entries.filter(e => weightDateLabel(e, timeZone) === weightDateLabel(selected, timeZone)).length > 1 ? ` · Mesure ${selected.measurement_id}` : ''}`}</Text>
      </View>
    </View> : null}
    {points.length ? <WeightPlot entries={points} timeZone={timeZone} selectedId={selected?.measurement_id} onSelect={setSelectedId} /> : null}
    {!s.entries.length && s.status === 'confirmed' && s.coverage === 'COMPLETE' ?
      <Text testID="progress-weight-empty" style={type.small}>Aucune mesure dans cette période.</Text> : null}
    {selectedIndex >= 0 ? <View style={styles.navigation}>
      <CalibrationLink testID="progress-weight-previous" label="Relevé précédent" disabled={selectedIndex <= 0}
        onPress={() => { if (selectedIndex > 0) setSelectedId(ordered[selectedIndex - 1].measurement_id); }} />
      <CalibrationLink testID="progress-weight-next" label="Relevé suivant" disabled={selectedIndex >= ordered.length - 1}
        onPress={() => { if (selectedIndex < ordered.length - 1) setSelectedId(ordered[selectedIndex + 1].measurement_id); }} />
    </View> : null}
    {s.entries.length ? <CalibrationLink testID="progress-weight-show-list"
      label={listOpen ? 'Masquer les mesures et leurs sources' : 'Voir les mesures et leurs sources'}
      expanded={listOpen} onPress={() => setListOpen(open => !open)} /> : null}
    {listOpen ? <View style={styles.disclosure}>
      {rows.map(({ point, label }) => <View key={point.measurement_id} style={styles.record}>
        <CalibrationLink testID={`progress-weight-entry-${point.measurement_id}`}
          label={`${(labelCounts.get(label) ?? 0) > 1 ? `${label} · mesure ${point.measurement_id}` : label} · ${acquisitionLabel(point)}${point.bodySource ? ` · Version ${point.bodySource.revision}` : ' · Version non capturée'}`}
          selected={selected?.measurement_id === point.measurement_id} onPress={() => setSelectedId(point.measurement_id)} />
        {point.measurement_id === selected?.measurement_id ? <WeightSource point={point} /> : null}
      </View>)}
    </View> : null}
    {s.canContinue ? <CalibrationLink label="Continuer la lecture" onPress={onMore} /> : null}
  </View>;
}

export function WeightTrend(p: WeightTrendProps) {
  if (p.state.status === 'consent_required') return <Text testID="progress-weight-consent" style={type.small}>
    Un accord est nécessaire pour consulter les mesures. Gère cet accord depuis Profil.
  </Text>;
  if (p.state.status === 'idle' || p.state.status === 'unavailable' || p.state.status === 'rejected') {
    return <Text style={type.small}>Mesures indisponibles.</Text>;
  }
  return <WeightReading {...p} />;
}

const styles = StyleSheet.create({
  reading: { gap: 8 },
  plot: { paddingVertical: 8 },
  navigation: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between', gap: 8 },
  selection: { borderLeftWidth: 2, borderLeftColor: color.ink3, paddingLeft: 10, flexDirection: 'row', alignItems: 'baseline', flexWrap: 'wrap', columnGap: 8, rowGap: 4 },
  value: { ...type.bodyStrong, ...type.tabular, fontSize: 22, lineHeight: 28, flexShrink: 1 },
  axes: { flexDirection: 'row', alignItems: 'flex-start', gap: 4 },
  yTicks: { justifyContent: 'space-between', alignItems: 'flex-end' },
  oneTick: { justifyContent: 'center' },
  tick: { ...type.small, ...type.tabular },
  xAxis: { flex: 1, minWidth: 0 },
  dates: { flexDirection: 'row', justifyContent: 'space-between', flexWrap: 'wrap', gap: 8, paddingHorizontal: 10 },
  singleDate: { justifyContent: 'center' },
  dateTick: { ...type.small, flexShrink: 1 },
  dateEnd: { textAlign: 'right', marginLeft: 'auto' },
  disclosure: { gap: 4 },
  record: { borderTopWidth: StyleSheet.hairlineWidth, borderTopColor: color.line },
});
