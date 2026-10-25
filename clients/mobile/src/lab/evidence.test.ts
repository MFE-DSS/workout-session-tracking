import { buildEvidence, EVIDENCE_SCHEMA, stats, THRESHOLDS } from './evidence';

const m = (name: string, value: number) => ({ name, value, at_ms: 0 });
const base = {
  build: { expo_sdk: '58.0.0', react_native: '0.88.0', app_version: '0.0.1', build_id: 'abc' },
  journal: [],
  outbox: [],
  plannedSets: 21,
  reduceMotionEnabled: false,
  capturedAtMs: Date.UTC(2026, 9, 23),
};

describe('one evidence schema for every platform', () => {
  test('an iOS and an Android run produce the same shape, with the same thresholds', () => {
    const metrics = [m('G-VAL', 40), m('G-VAL', 60), m('G-LOCAL', 4)];
    const ios = buildEvidence({ ...base, metrics, device: { platform: 'ios', model: 'iPhone', model_id: 'iPhone15,5', os_version: '27.0.1', physical: true } });
    const android = buildEvidence({ ...base, metrics, device: { platform: 'android', model: 'Pixel', model_id: null, os_version: '16', physical: true } });
    const keys = (o: object): string[] => Object.entries(o).flatMap(([k, v]) => (v && typeof v === 'object' && !Array.isArray(v) ? [k, ...keys(v).map((s) => `${k}.${s}`)] : [k]));
    expect(keys(android).sort()).toEqual(keys(ios).sort());
    expect(ios.schema).toBe(EVIDENCE_SCHEMA);
    expect(ios.ux.g_val_within_threshold).toBe(android.ux.g_val_within_threshold);
  });

  test('a simulator / emulator record never counts as physical evidence', () => {
    const e = buildEvidence({ ...base, metrics: [], device: { platform: 'android', model: 'sdk_gphone', model_id: null, os_version: '16', physical: false } });
    expect(e.gate.counts_as_physical_evidence).toBe(false);
  });

  test('a record never claims cross-platform validation by itself', () => {
    const e = buildEvidence({ ...base, metrics: [], device: { platform: 'ios', model: null, model_id: null, os_version: null, physical: true } });
    expect(e.gate.cross_platform).toBe(false);
  });

  test('operator observations stay null until the operator writes them; nothing is guessed', () => {
    const e = buildEvidence({ ...base, metrics: [], device: { platform: 'ios', model: null, model_id: null, os_version: null, physical: true } });
    expect([e.ux.thumb_reach, e.ux.keyboard, e.persistence.force_kill_observation, e.native_feedback.haptics_observation, e.gate.operator_verdict]).toEqual([null, null, null, null, null]);
    expect(e.ux.g_val_within_threshold).toBeNull();
  });

  test('thresholds are judged from measurements', () => {
    const slow = buildEvidence({ ...base, metrics: [m('G-VAL', THRESHOLDS.g_val_p95_ms + 50)], device: { platform: 'ios', model: null, model_id: null, os_version: null, physical: true } });
    expect(slow.ux.g_val_within_threshold).toBe(false);
  });

  test('stats are median / p95 / worst over the samples', () => {
    expect(stats([5, 1, 3])).toEqual({ n: 3, median: 3, p95: 5, worst: 5 });
    expect(stats([])).toEqual({ n: 0, median: null, p95: null, worst: null });
  });
});
