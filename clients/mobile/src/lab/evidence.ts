/**
 * PHYSICAL_DEVICE_GATE evidence — ONE schema for every platform.
 *
 * Measured fields are filled from the lab's own instrumentation; operator
 * observations stay `null` until the operator writes them. Success is never
 * defined per platform: the same thresholds apply to iOS and Android, and a
 * record from a simulator/emulator is marked `physical: false` and cannot
 * close the gate.
 */
import type { Metric } from '../storage/journalTypes';
import type { JournalRow, OutboxRow } from '../storage/outbox';

export const EVIDENCE_SCHEMA = 'auren.n0.physical-device-evidence/1';

/** Same thresholds on every platform (spec §10.2, amended 2026-10-23). */
export const THRESHOLDS = {
  g_val_p95_ms: 100,
  g_local_p95_ms: 20,
  timer_drift_ms: 1000,
} as const;

export type Stats = { n: number; median: number | null; p95: number | null; worst: number | null };

export function stats(values: number[]): Stats {
  if (!values.length) return { n: 0, median: null, p95: null, worst: null };
  const s = [...values].sort((a, b) => a - b);
  const at = (p: number) => s[Math.min(s.length - 1, Math.round(p * (s.length - 1)))];
  return { n: s.length, median: Math.round(at(0.5)), p95: Math.round(at(0.95)), worst: Math.round(s[s.length - 1]) };
}

const of = (metrics: Metric[], name: string) => metrics.filter((m) => m.name === name).map((m) => m.value);
const count = (metrics: Metric[], name: string) => of(metrics, name).length;

export type EvidenceInput = {
  device: { platform: string; model: string | null; model_id: string | null; os_version: string | null; physical: boolean };
  build: { expo_sdk: string | null; react_native: string | null; app_version: string | null; build_id: string | null };
  metrics: Metric[];
  journal: JournalRow[];
  outbox: OutboxRow[];
  plannedSets: number | null;
  reduceMotionEnabled: boolean;
  capturedAtMs: number;
};

export function buildEvidence(i: EvidenceInput) {
  const gVal = stats(of(i.metrics, 'G-VAL'));
  const gLocal = stats(of(i.metrics, 'G-LOCAL'));
  const fg = stats(of(i.metrics, 'REST-END-LATENESS-FOREGROUND'));
  const validated = count(i.metrics, 'SET-VALIDATED');
  return {
    schema: EVIDENCE_SCHEMA,
    captured_at: new Date(i.capturedAtMs).toISOString(),
    device: i.device,
    build: i.build,
    ux: {
      g_val_ms: gVal,
      g_val_within_threshold: gVal.p95 === null ? null : gVal.p95 <= THRESHOLDS.g_val_p95_ms,
      g_local_ms: gLocal,
      g_local_within_threshold: gLocal.p95 === null ? null : gLocal.p95 <= THRESHOLDS.g_local_p95_ms,
      thumb_reach: null,
      safe_area: null,
      keyboard: null,
      dynamic_text: null,
      reduced_motion: { system_setting_enabled: i.reduceMotionEnabled, observation: null },
    },
    state: {
      sets_planned: i.plannedSets,
      sets_validated: validated,
      nominal_path_completed: count(i.metrics, 'SESSION-COMPLETED') > 0,
      navigation_decisions: count(i.metrics, 'SECONDARY-OPENED'),
      automatic_set_transitions: count(i.metrics, 'AUTO-NEXT-SET'),
      automatic_exercise_transitions: count(i.metrics, 'AUTO-NEXT-EXERCISE'),
      rest_skips: count(i.metrics, 'REST-SKIP'),
    },
    persistence: {
      journal_sets: i.journal.length,
      outbox_pending: i.outbox.filter((o) => o.state === 'pending').length,
      relaunch_restores: count(i.metrics, 'RELAUNCH-RESTORED-SETS'),
      sets_restored_after_relaunch: of(i.metrics, 'RELAUNCH-RESTORED-SETS').at(-1) ?? null,
      // the first physical run showed « non enregistrée » once: every failure is counted
      commit_failures: count(i.metrics, 'COMMIT-FAILED'),
      force_kill_observation: null,
    },
    // D9 — the connected app: decided on the device → acknowledged by the server
    sync: {
      g_sync_ms: stats(of(i.metrics, 'G-SYNC')),
      acknowledged: count(i.metrics, 'SYNC-ACK'),
      already_present_on_server: count(i.metrics, 'SYNC-ACK-DUPLICATE'),
      requires_attention: i.outbox.filter((o) => o.state === 'failed').length,
    },
    timer: {
      foreground_end_lateness_ms: fg,
      foreground_within_threshold: fg.worst === null ? null : fg.worst <= THRESHOLDS.timer_drift_ms,
      resume_end_lateness_ms: stats(of(i.metrics, 'REST-END-LATENESS-RESUME')),
      background_locked_observation: null,
    },
    native_feedback: {
      haptics_observation: null,
      rest_notifications_requested: count(i.metrics, 'NOTIF-REQUESTED'),
      rest_notification_delay_ms: stats(of(i.metrics, 'NOTIF-LATENESS')),
    },
    gate: {
      counts_as_physical_evidence: i.device.physical,
      cross_platform: false,
      operator_verdict: null,
    },
  };
}

export type Evidence = ReturnType<typeof buildEvidence>;
