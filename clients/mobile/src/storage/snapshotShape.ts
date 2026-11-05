/** Structural boundary only: no repair, defaults, prescriptions or interpretation of persisted facts. */
import type { WorkoutState } from '../domain/workout';
const record = (v: unknown): v is Record<string, unknown> => v !== null && typeof v === 'object' && !Array.isArray(v);
const number = (v: unknown): v is number => typeof v === 'number' && Number.isFinite(v);
const nullableNumber = (v: unknown) => v === null || number(v);
const id = (v: unknown): v is number => Number.isSafeInteger(v) && (v as number) > 0;
const strings = (v: unknown) => Array.isArray(v) && v.every((item) => typeof item === 'string');
function transition(v: unknown): boolean {
  return record(v) && (v.kind === 'BILAN' || (v.kind === 'REST_THEN_SET' && id(v.set_id))
    || (v.kind === 'REST_THEN_EXERCISE' && id(v.set_id) && id(v.se_id)));
}
export function isRestorableSnapshot(v: unknown): v is WorkoutState {
  if (!record(v) || !['MISSION', 'SET', 'REST', 'COMPLETE'].includes(String(v.phase))) return false;
  if (!record(v.drafts) || !record(v.done) || !record(v.requiresSync)) return false;
  if (!nullableNumber(v.startedMs) || !nullableNumber(v.completedMs) || !nullableNumber(v.cursorSetId)) return false;
  if (v.skipped !== undefined && (!record(v.skipped) || Object.values(v.skipped).some((x) => x !== true))) return false;
  if (!Object.values(v.drafts).every((d) => record(d) && nullableNumber(d.weight) && nullableNumber(d.reps))) return false;
  if (!Object.values(v.done).every((d) => record(d) && number(d.weight) && number(d.reps)
    && record(d.performedAt) && number(d.performedAt.epochMs) && typeof d.performedAt.estimated === 'boolean'
    && ['pending_local', 'saved_local', 'not_saved'].includes(String(d.local)))) return false;
  if (!Object.values(v.requiresSync).every((x) => record(x) && typeof x.substitute === 'string')) return false;
  if (v.plan === null) return v.phase === 'MISSION' && v.rest === null;
  const p = v.plan;
  if (!record(p) || !id(p.session_id) || typeof p.template_name !== 'string' || typeof p.template_slug !== 'string'
    || typeof p.server_now !== 'string' || !number(p.rest_default_seconds) || !Array.isArray(p.exercises)
    || !Array.isArray(p.sets) || !record(p.on_complete)) return false;
  if (!p.exercises.every((e) => record(e) && id(e.se_id) && typeof e.code === 'string'
    && typeof e.prescribed_name === 'string' && typeof e.executed_name === 'string'
    && record(e.prefill) && nullableNumber(e.prefill.weight_kg) && nullableNumber(e.prefill.reps)
    && strings(e.substitutes))) return false;
  if (!p.sets.every((s) => record(s) && id(s.set_id) && id(s.se_id) && number(s.index)
    && p.exercises instanceof Array && p.exercises.some((e) => record(e) && e.se_id === s.se_id))) return false;
  if (!Object.values(p.on_complete).every(transition)) return false;
  if ((v.phase === 'SET' || v.phase === 'REST') && !p.sets.some((s) => record(s) && s.set_id === v.cursorSetId)) return false;
  if (v.rest !== null && (!record(v.rest) || !number(v.rest.deadlineMs) || !transition(v.rest.after) || !id(v.rest.fromSetId))) return false;
  if (v.phase === 'REST' && v.rest === null) return false;
  return true;
}
