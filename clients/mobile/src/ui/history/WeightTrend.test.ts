import React, { act } from 'react';
import { StyleSheet } from 'react-native';
import { createRoot, type Root } from 'test-renderer';
import type { WeightPoint, WeightWindowState } from '../../api/trainingHistoryResource';
import { weightPage } from '../../../test/accountDataHarness';
import { window4 } from '../../../test/trainingHistoryHarness';
import { WeightTrend } from './WeightTrend';

let root: Root;
beforeEach(() => { root = createRoot(); });
afterEach(async () => { await act(async () => root.unmount()); });

const node = (id: string) => root.container.queryAll((n: any) => n.props.testID === id)[0]?.props;
const screenText = () => root.container.queryAll(() => true).flatMap((n: any) =>
  [n.props.children].flat().filter((child: unknown) => typeof child === 'string' || typeof child === 'number')
).join(' ');
async function press(id: string, nativeEvent: object = {}) {
  await act(async () => node(id).onClick({ nativeEvent, stopPropagation: () => {}, currentTarget: 1, target: 1 }));
}
async function render(state: WeightWindowState<WeightPoint>) {
  await act(async () => root.render(React.createElement(WeightTrend, { state, onMore: () => {} })));
}
function state(): WeightWindowState<WeightPoint> {
  const first = {
    ...weightPage(22).entries[0], measured_at: '2026-11-03T00:00:00Z', value: 68.2,
    provenance: { origin: 'USER_DECLARED', acquisition: 'MANUAL_ENTRY', source_ref: 'body_measurements/22/weight_kg' },
  } satisfies WeightPoint;
  const corrected = {
    ...first, measurement_id: 29, measured_at: '2026-11-06T00:00:00Z', recorded_at: '2026-11-07T09:30:00Z', value: 74.25,
    provenance: { origin: 'USER_DECLARED', acquisition: 'MANUAL_CORRECTION', source_ref: 'body_measurements/29/weight_kg' },
  } satisfies WeightPoint;
  return {
    status: 'confirmed', previous: false, coverage: 'COMPLETE', canContinue: false,
    window: { ...window4, time_zone: 'America/Los_Angeles' },
    entries: [
      { ...corrected, bodySource: { ...corrected.provenance, root_ref: 24, revision: 2, date_precision: 'DAY_UTC_CONVENTION' } },
      { ...first, bodySource: { ...first.provenance, root_ref: 22, revision: 1, date_precision: 'DAY_UTC_CONVENTION' } },
    ],
  };
}

test('the exact dates and kg endpoints come from received plottable values', async () => {
  await render(state());
  expect(node('progress-weight-y-high').children).toBe('74,25');
  expect(node('progress-weight-y-low').children).toBe('68,2');
  expect(node('progress-weight-date-from').children).toBe('3 nov. 2026');
  expect(node('progress-weight-date-until').children).toBe('6 nov. 2026');
  expect(node('progress-weight-selected-value').children).toBe('74,25 kg');
  await press('progress-weight-chart-touch', { locationX: 10, locationY: 95 });
  expect(node('progress-weight-selected-value').children).toBe('68,2 kg');
});

test.each([
  ['one point', null],
  ['two points at the same timestamp', '2026-11-06T00:00:00Z'],
  ['two timestamp formats for the same instant', '2026-11-06T00:00:00+00:00'],
])('a single date is centered under its plotted coordinates for %s', async (_case, sameInstant) => {
  const s = state();
  if (sameInstant === null) s.entries = [s.entries[0]];
  else s.entries[1] = { ...s.entries[1], measured_at: sameInstant };
  await render(s);

  expect(node('progress-weight-date-from').children).toBe('6 nov. 2026');
  expect(node('progress-weight-date-until')).toBeUndefined();
  expect(StyleSheet.flatten(node('progress-weight-dates').style).justifyContent).toBe('center');
  const circles = root.container.queryAll((n: any) => typeof n.props.cx === 'number' && typeof n.props.cy === 'number');
  expect(circles).toHaveLength(s.entries.length);
  const x = circles[0].props.cx;
  expect(circles.every(n => n.props.cx === x)).toBe(true);
  const lines = root.container.queryAll((n: any) => typeof n.props.x1 === 'number' && typeof n.props.x2 === 'number');
  const floor = lines.find(n => n.props.y1 === n.props.y2 && n.props.x2 - n.props.x1 > 20);
  expect(floor).toBeDefined();
  expect(lines.some(n => n.props.x1 === x && n.props.x2 === x &&
    n.props.y1 <= floor!.props.y1 && n.props.y2 > floor!.props.y1)).toBe(true);
});

test('the accessible measure list selects the effective correction and discloses exact provenance', async () => {
  const s = state();
  // Measurements on the same date can only be distinguished reliably through the list.
  s.entries[1] = { ...s.entries[1], measured_at: s.entries[0].measured_at, value: 74.25 };
  await render(s);
  expect(screenText()).not.toContain('body_measurements/29/weight_kg');
  await press('progress-weight-show-list');
  expect(node('progress-weight-entry-29').accessibilityState.selected).toBe(true);
  expect(node('progress-weight-entry-29').accessibilityLabel).toContain('mesure 29');
  expect(node('progress-weight-entry-22').accessibilityLabel).toContain('mesure 22');
  expect(screenText()).toContain('body_measurements/29/weight_kg');
  expect(screenText()).toContain('Version 2');
  expect(screenText()).toContain('2026-11-07T09:30:00Z');
  await press('progress-weight-entry-22');
  expect(node('progress-weight-entry-22').accessibilityState.selected).toBe(true);
  expect(node('progress-weight-entry-29').accessibilityState.selected).toBe(false);
  expect(screenText()).toContain('body_measurements/22/weight_kg');
  expect(screenText()).not.toContain('body_measurements/29/weight_kg');
  await render({ ...s, entries: [s.entries[0]] });
  expect(node('progress-weight-entry-22')).toBeUndefined();
  expect(node('progress-weight-entry-29').accessibilityState.selected).toBe(true);
});

test('withdrawal hides a previously selected effective point and its source despite retained rows', async () => {
  const s = state();
  await render(s);
  await press('progress-weight-show-list');
  await press('progress-weight-entry-22');
  await render({ ...s, status: 'consent_required' });
  expect(node('progress-weight-consent')).toBeDefined();
  expect(node('progress-weight-chart')).toBeUndefined();
  expect(node('progress-weight-entry-22')).toBeUndefined();
  expect(screenText()).not.toMatch(/68,2|74,25|body_measurements/);
  await render(s);
  expect(node('progress-weight-entry-22')).toBeUndefined();
  expect(node('progress-weight-selected-value').children).toBe('74,25 kg');
});

test('invalid points stay discoverable without plotting and partial readings stay distinct from an empty period', async () => {
  const s = state();
  await render({ ...s, coverage: 'PARTIAL', entries: [] });
  expect(node('progress-weight-partial')).toBeDefined();
  expect(node('progress-weight-empty')).toBeUndefined();
  await render({ ...s, entries: [] });
  expect(node('progress-weight-empty')).toBeDefined();
  const invalid = { ...s.entries[0], value: null, raw_value_repr: 'Infinity', quality: 'INVALID_NONFINITE' as const };
  await render({ ...s, entries: [invalid] });
  expect(node('progress-weight-chart')).toBeUndefined();
  expect(node('progress-weight-empty')).toBeUndefined();
  expect(screenText()).toContain('Valeur invalide');
  await press('progress-weight-show-list');
  expect(screenText()).toContain('Infinity');
});

test('memory navigation selects the actual adjacent observation without changing recorded values', async () => {
  const s = state();
  await render(s);
  expect(node('progress-weight-selected-value').children).toBe('74,25 kg');
  expect(node('progress-weight-next').accessibilityState.disabled).toBe(true);
  await press('progress-weight-previous');
  expect(node('progress-weight-selected-value').children).toBe('68,2 kg');
  expect(node('progress-weight-previous').accessibilityState.disabled).toBe(true);
  await press('progress-weight-next');
  expect(node('progress-weight-selected-value').children).toBe('74,25 kg');
  expect(s.entries.map(p => p.value)).toEqual([74.25, 68.2]);
  expect(screenText()).not.toMatch(/recommand|récupér|amélior/);
});


test('review BC-M1: identical instants with different date precision expose both civil dates on the axis',async()=>{
 const s=state(),base=s.entries[0];s.entries=[
  {...base,measurement_id:1,measured_at:'2026-11-06T00:00:00Z',bodySource:{...base.bodySource!,date_precision:'DAY_UTC_CONVENTION'}},
  {...base,measurement_id:2,measured_at:'2026-11-06T00:00:00Z',bodySource:{...base.bodySource!,date_precision:'SERVER_CAPTURE_TIME'}},
 ];
 await render(s);
 const dates=root.container.queryAll(n=>n.props.testID==='progress-weight-dates')[0];
 const read=(v:any):string=>Array.isArray(v)?v.map(read).join(' '):typeof v==='string'||typeof v==='number'?String(v):v?.props?read(v.props.children):'';
 const visible=read(dates.props.children);expect(visible).toContain('5 nov. 2026');expect(visible).toContain('6 nov. 2026');
});

// Operator C-final: a screen-reader selection must identify the exact observation,
// including equal-day/equal-value observations and its actual provenance.
test('C-final: equal-day observations remain distinct spoken selections in chronological navigation', async () => {
  const s = state();
  s.entries[1] = { ...s.entries[1], measured_at: s.entries[0].measured_at, value: 74.25 };
  await render(s);
  const firstLabel = node('progress-weight-selected').accessibilityLabel;
  expect(firstLabel).toContain('74,25 kg');
  expect(firstLabel).toContain('6 nov. 2026');
  expect(firstLabel).toContain('Correction personnelle');
  expect(firstLabel).toContain('Version 2');
  expect(firstLabel).toContain('mesure 29');
  expect(node('progress-weight-selected-provenance').children).toContain('Mesure 29');
  await press('progress-weight-previous');
  const secondLabel = node('progress-weight-selected').accessibilityLabel;
  expect(secondLabel).toContain('Saisie personnelle');
  expect(secondLabel).toContain('mesure 22');
  expect(node('progress-weight-selected-provenance').children).toContain('Mesure 22');
  expect(secondLabel).not.toBe(firstLabel);
  expect(node('progress-weight-selected-value').children).toBe('74,25 kg');
  await press('progress-weight-next');
  expect(node('progress-weight-selected').accessibilityLabel).toBe(firstLabel);
  expect(s.entries.map(p => p.measurement_id)).toEqual([29, 22]);
});

test('C-final: sequential reading includes an unplottable observation without replacing it by zero', async () => {
  const s = state();
  s.entries[1] = { ...s.entries[1], value: null, raw_value_repr: 'Infinity', quality: 'INVALID_NONFINITE' };
  await render(s);
  expect(node('progress-weight-previous').accessibilityState.disabled).toBe(false);
  await press('progress-weight-previous');
  expect(node('progress-weight-selected-value').children).toBe('Valeur invalide');
  expect(node('progress-weight-selected').accessibilityLabel).toContain('mesure 22');
  expect(node('progress-weight-selected').accessibilityLabel).not.toContain('0 kg');
  await press('progress-weight-next');
  expect(node('progress-weight-selected-value').children).toBe('74,25 kg');
});

test('C-final: spoken selection retains previous and partial reading qualification', async () => {
  await render({ ...state(), previous: true, status: 'unknown', coverage: 'PARTIAL' });
  expect(node('progress-weight-selected').accessibilityLabel).toContain('Lecture précédente');
  expect(node('progress-weight-selected').accessibilityLabel).not.toContain('Lecture confirmée');
  await render({ ...state(), coverage: 'PARTIAL' });
  expect(node('progress-weight-selected').accessibilityLabel).toContain('Lecture partielle');
  await render(state());
  expect(node('progress-weight-selected').accessibilityLabel).toContain('Lecture confirmée');
});


test('C-review I1: a declared day discloses its day without attributing the conventional midnight to the measurement', async () => {
  await render(state());
  await press('progress-weight-show-list');
  expect(screenText()).toContain('Jour déclaré · 6 nov. 2026');
  expect(screenText()).not.toContain('Mesure datée du 2026-11-06T00:00:00Z');
  expect(screenText()).toContain('Journal · 2026-11-07T09:30:00Z');
});

test('C-review I1: a server capture keeps its original instant explicitly labelled as source time', async () => {
  const s = state(); s.entries = [{ ...s.entries[0], bodySource: { ...s.entries[0].bodySource!, date_precision: 'SERVER_CAPTURE_TIME' } }];
  await render(s); await press('progress-weight-show-list');
  expect(screenText()).toContain('Date source · 2026-11-06T00:00:00Z');
  expect(screenText()).toContain('heure enregistrée par le serveur');
  expect(screenText()).not.toContain('Jour déclaré ·');
});


test('native C-focus witness: the numeric child cannot steal focus from its atomic dated and sourced observation', async () => {
  await render(state());
  // Android TalkBack actually focused the selectable Text and spoke only "71,4 kg".
  // Keep copying in the source disclosure; primary reading is one semantic object.
  expect(node('progress-weight-selected-value').selectable).not.toBe(true);
  expect(node('progress-weight-selected').focusable).toBe(true);
  expect(node('progress-weight-selected-content').importantForAccessibility).toBe('no-hide-descendants');
  expect(node('progress-weight-selected').accessibilityLabel).toContain('6 nov. 2026');
  expect(node('progress-weight-selected').accessibilityLabel).toContain('74,25 kg');
  expect(node('progress-weight-selected').accessibilityLabel).toContain('Correction personnelle');
  expect(node('progress-weight-selected').accessibilityLabel).toContain('mesure 29');
});
